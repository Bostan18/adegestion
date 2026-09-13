"""Module Baux : CRUD des baux.

RBAC identique au module Biens : tout utilisateur authentifie consulte (le
comptable a besoin du bail pour rapprocher un loyer), l'admin et l'agent
creent et modifient, seul l'admin supprime.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, PropertyManagerUser, require_admin
from app.models.enums import LeaseStatus
from app.models.lease import Lease
from app.schemas.common import Page
from app.schemas.lease import LeaseCreate, LeaseRead, LeaseUpdate
from app.services.leases import (
    ensure_no_overlap,
    get_property_or_404,
    mark_property_rented,
    release_property,
)

router = APIRouter(prefix="/leases", tags=["baux"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_lease_or_404(db: Session, lease_id: uuid.UUID) -> Lease:
    lease = db.scalar(
        select(Lease).where(Lease.id == lease_id).options(selectinload(Lease.property))
    )
    if lease is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bail introuvable.")
    return lease


@router.get("", response_model=Page[LeaseRead], summary="Lister les baux")
def list_leases(
    db: DbSession,
    _: CurrentUser,
    property_id: uuid.UUID | None = None,
    status_filter: Annotated[LeaseStatus | None, Query(alias="status")] = None,
    q: Annotated[str | None, Query(description="Recherche sur le nom du locataire")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[LeaseRead]:
    filters = []
    if property_id is not None:
        filters.append(Lease.property_id == property_id)
    if status_filter is not None:
        filters.append(Lease.status == str(status_filter))
    if q:
        filters.append(Lease.tenant_name.ilike(f"%{q.strip()}%"))

    total = db.scalar(select(func.count()).select_from(Lease).where(*filters)) or 0
    rows = db.scalars(
        select(Lease)
        .where(*filters)
        .options(selectinload(Lease.property))
        .order_by(Lease.start_date.desc(), Lease.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    return Page[LeaseRead](
        items=[LeaseRead.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=LeaseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Creer un bail",
)
def create_lease(payload: LeaseCreate, db: DbSession, _: PropertyManagerUser) -> LeaseRead:
    get_property_or_404(db, payload.property_id)

    is_active = payload.status == LeaseStatus.ACTIF
    if is_active:
        ensure_no_overlap(db, payload.property_id, payload.start_date, payload.end_date)

    lease = Lease(**payload.model_dump())
    lease.status = str(payload.status)
    db.add(lease)

    if is_active:
        mark_property_rented(db, payload.property_id)

    db.commit()
    db.refresh(lease)
    return LeaseRead.model_validate(lease)


@router.get("/{lease_id}", response_model=LeaseRead, summary="Detail d'un bail")
def get_lease(lease_id: uuid.UUID, db: DbSession, _: CurrentUser) -> LeaseRead:
    return LeaseRead.model_validate(_get_lease_or_404(db, lease_id))


@router.patch("/{lease_id}", response_model=LeaseRead, summary="Modifier un bail")
def update_lease(
    lease_id: uuid.UUID,
    payload: LeaseUpdate,
    db: DbSession,
    _: PropertyManagerUser,
) -> LeaseRead:
    lease = _get_lease_or_404(db, lease_id)
    data = payload.model_dump(exclude_unset=True)

    was_active = lease.status == str(LeaseStatus.ACTIF)
    new_status = data.get("status", lease.status)
    will_be_active = str(new_status) == str(LeaseStatus.ACTIF)

    start_date = data.get("start_date", lease.start_date)
    end_date = data.get("end_date", lease.end_date)
    if end_date is not None and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La date de fin ne peut pas preceder la date de debut.",
        )

    if will_be_active:
        ensure_no_overlap(db, lease.property_id, start_date, end_date, exclude_lease_id=lease.id)

    for field, value in data.items():
        setattr(lease, field, str(value) if field == "status" else value)

    if will_be_active:
        mark_property_rented(db, lease.property_id)
    elif was_active:
        # Le bail vient de se terminer ou d'etre resilie.
        release_property(db, lease.property_id, exclude_lease_id=lease.id)

    db.commit()
    db.refresh(lease)
    return LeaseRead.model_validate(lease)


@router.delete(
    "/{lease_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
    summary="Supprimer un bail",
)
def delete_lease(lease_id: uuid.UUID, db: DbSession) -> Response:
    lease = _get_lease_or_404(db, lease_id)
    property_id = lease.property_id
    was_active = lease.status == str(LeaseStatus.ACTIF)

    db.delete(lease)
    db.flush()

    if was_active:
        release_property(db, property_id, exclude_lease_id=lease_id)

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
