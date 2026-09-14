"""Module Maintenance : tickets d'intervention, couts et photos.

RBAC particulier, aligne sur les policies RLS deja deployees : les trois roles
consultent et **declarent** un ticket, car le locataire peut tomber sur
n'importe qui en appelant l'agence. En revanche seuls l'admin et l'agent le
traitent, et seul l'admin le supprime.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, PropertyManagerUser, require_admin
from app.models.enums import TicketPriority, TicketStatus
from app.models.maintenance_ticket import MaintenancePhoto, MaintenanceTicket
from app.schemas.common import Page
from app.schemas.maintenance import (
    MaintenancePhotoCreate,
    MaintenancePhotoRead,
    MaintenancePhotoUploadRequest,
    TicketCreate,
    TicketListItem,
    TicketRead,
    TicketUpdate,
)
from app.schemas.property import PhotoUploadTicket
from app.services.maintenance import (
    CLOSED_STATUSES,
    ensure_contractor_exists,
    get_property_or_404,
    sync_resolved_at,
    validate_costs,
)
from app.services.storage import (
    StorageService,
    build_storage_path,
    get_maintenance_storage_service,
)

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

DbSession = Annotated[Session, Depends(get_db)]
Storage = Annotated[StorageService, Depends(get_maintenance_storage_service)]


def _with_relations(statement):
    return statement.options(
        selectinload(MaintenanceTicket.property),
        selectinload(MaintenanceTicket.reporter),
        selectinload(MaintenanceTicket.contractor),
        selectinload(MaintenanceTicket.photos),
    )


def _get_ticket_or_404(db: Session, ticket_id: uuid.UUID) -> MaintenanceTicket:
    ticket = db.scalar(
        _with_relations(select(MaintenanceTicket).where(MaintenanceTicket.id == ticket_id))
    )
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable.")
    return ticket


def _serialize(ticket: MaintenanceTicket, storage: StorageService) -> TicketRead:
    data = TicketRead.model_validate(ticket)
    return data.model_copy(
        update={
            "photos": [
                MaintenancePhotoRead.model_validate(photo).model_copy(
                    update={"url": storage.create_signed_url(photo.storage_path)}
                )
                for photo in ticket.photos
            ]
        }
    )


@router.get("", response_model=Page[TicketListItem], summary="Lister les tickets")
def list_tickets(
    db: DbSession,
    _: CurrentUser,
    property_id: uuid.UUID | None = None,
    contractor_id: uuid.UUID | None = None,
    status_filter: Annotated[TicketStatus | None, Query(alias="status")] = None,
    priority: TicketPriority | None = None,
    open_only: Annotated[bool, Query(description="Seulement les tickets a traiter")] = False,
    q: Annotated[str | None, Query(description="Recherche sur l'intitule")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[TicketListItem]:
    filters = []
    if property_id is not None:
        filters.append(MaintenanceTicket.property_id == property_id)
    if contractor_id is not None:
        filters.append(MaintenanceTicket.contractor_id == contractor_id)
    if status_filter is not None:
        filters.append(MaintenanceTicket.status == str(status_filter))
    if priority is not None:
        filters.append(MaintenanceTicket.priority == str(priority))
    if open_only:
        filters.append(
            MaintenanceTicket.status.in_([str(TicketStatus.OUVERT), str(TicketStatus.EN_COURS)])
        )
    if q:
        pattern = f"%{q.strip()}%"
        filters.append(
            or_(
                MaintenanceTicket.title.ilike(pattern),
                MaintenanceTicket.description.ilike(pattern),
            )
        )

    total = db.scalar(select(func.count()).select_from(MaintenanceTicket).where(*filters)) or 0
    rows = db.scalars(
        _with_relations(select(MaintenanceTicket).where(*filters))
        # Les urgences d'abord, puis le plus recent.
        .order_by(
            MaintenanceTicket.status.in_(list(CLOSED_STATUSES)),
            MaintenanceTicket.created_at.desc(),
        )
        .limit(limit)
        .offset(offset)
    ).all()

    return Page[TicketListItem](
        items=[TicketListItem.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
    summary="Declarer un ticket",
)
def create_ticket(
    payload: TicketCreate,
    db: DbSession,
    storage: Storage,
    current_user: CurrentUser,
) -> TicketRead:
    """Ouvert aux trois roles : le comptable prend parfois l'appel du locataire."""
    get_property_or_404(db, payload.property_id)
    ensure_contractor_exists(db, payload.contractor_id)
    validate_costs(str(payload.status), payload.actual_cost)

    ticket = MaintenanceTicket(**payload.model_dump())
    ticket.priority = str(payload.priority)
    ticket.status = str(payload.status)
    # Tracabilite non falsifiable : le declarant vient du jeton, pas du client.
    ticket.reported_by = current_user.id
    sync_resolved_at(ticket, str(payload.status))

    db.add(ticket)
    db.commit()
    return _serialize(_get_ticket_or_404(db, ticket.id), storage)


@router.get("/{ticket_id}", response_model=TicketRead, summary="Detail d'un ticket")
def get_ticket(
    ticket_id: uuid.UUID, db: DbSession, storage: Storage, _: CurrentUser
) -> TicketRead:
    return _serialize(_get_ticket_or_404(db, ticket_id), storage)


@router.patch("/{ticket_id}", response_model=TicketRead, summary="Traiter un ticket")
def update_ticket(
    ticket_id: uuid.UUID,
    payload: TicketUpdate,
    db: DbSession,
    storage: Storage,
    _: PropertyManagerUser,
) -> TicketRead:
    """Reserve a l'admin et a l'agent : declarer n'est pas traiter."""
    ticket = _get_ticket_or_404(db, ticket_id)
    data = payload.model_dump(exclude_unset=True)

    if "contractor_id" in data:
        ensure_contractor_exists(db, data["contractor_id"])

    new_status = str(data.get("status", ticket.status))
    # Uniquement sur le cout transmis par cette requete : un montant deja
    # enregistre ne doit pas empecher de rouvrir le ticket.
    if "actual_cost" in data:
        validate_costs(new_status, data["actual_cost"])

    for field, value in data.items():
        setattr(ticket, field, str(value) if field in {"status", "priority"} else value)

    sync_resolved_at(ticket, new_status)
    db.commit()
    return _serialize(_get_ticket_or_404(db, ticket_id), storage)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
    summary="Supprimer un ticket",
)
def delete_ticket(ticket_id: uuid.UUID, db: DbSession, storage: Storage) -> Response:
    ticket = _get_ticket_or_404(db, ticket_id)
    paths = [photo.storage_path for photo in ticket.photos]
    db.delete(ticket)
    db.commit()
    for path in paths:
        storage.delete_object(path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Photos ---------------------------------------------------------------


@router.post(
    "/{ticket_id}/photos/upload-url",
    response_model=PhotoUploadTicket,
    summary="Obtenir une URL d'upload signee",
)
def create_photo_upload_url(
    ticket_id: uuid.UUID,
    payload: MaintenancePhotoUploadRequest,
    db: DbSession,
    storage: Storage,
    _: PropertyManagerUser,
    kind: Annotated[str, Query(pattern="^(avant|apres)$")] = "avant",
) -> PhotoUploadTicket:
    _get_ticket_or_404(db, ticket_id)
    storage_path = build_storage_path("tickets", ticket_id, kind, filename=payload.filename)
    signed_url, token = storage.create_signed_upload_url(storage_path)
    return PhotoUploadTicket(
        bucket=storage.bucket, storage_path=storage_path, token=token, signed_url=signed_url
    )


@router.post(
    "/{ticket_id}/photos",
    response_model=MaintenancePhotoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Enregistrer une photo televersee",
)
def register_photo(
    ticket_id: uuid.UUID,
    payload: MaintenancePhotoCreate,
    db: DbSession,
    storage: Storage,
    _: PropertyManagerUser,
) -> MaintenancePhotoRead:
    _get_ticket_or_404(db, ticket_id)
    expected_prefix = f"tickets/{ticket_id}/"
    if not payload.storage_path.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le chemin de stockage ne correspond pas a ce ticket.",
        )

    photo = MaintenancePhoto(
        ticket_id=ticket_id, storage_path=payload.storage_path, kind=payload.kind
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)

    data = MaintenancePhotoRead.model_validate(photo)
    return data.model_copy(update={"url": storage.create_signed_url(photo.storage_path)})


@router.delete(
    "/{ticket_id}/photos/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une photo",
)
def delete_photo(
    ticket_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: DbSession,
    storage: Storage,
    _: PropertyManagerUser,
) -> Response:
    photo = db.scalar(
        select(MaintenancePhoto).where(
            MaintenancePhoto.id == photo_id, MaintenancePhoto.ticket_id == ticket_id
        )
    )
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo introuvable.")

    storage_path = photo.storage_path
    db.delete(photo)
    db.commit()
    storage.delete_object(storage_path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
