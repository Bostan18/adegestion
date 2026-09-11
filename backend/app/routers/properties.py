"""Module Biens : CRUD des proprietes et gestion des photos.

RBAC : tout utilisateur authentifie peut consulter les biens (le comptable en a
besoin pour rapprocher un paiement), mais seuls l'admin et l'agent peuvent
creer ou modifier. La suppression d'un bien est reservee a l'admin.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, PropertyManagerUser, require_admin
from app.models.enums import PropertyStatus, PropertyType
from app.models.property import Property, PropertyPhoto
from app.schemas.common import Page
from app.schemas.property import (
    PhotoCreate,
    PhotoRead,
    PhotoUploadRequest,
    PhotoUploadTicket,
    PropertyCreate,
    PropertyListItem,
    PropertyRead,
    PropertyUpdate,
)
from app.services.storage import StorageService, build_storage_path, get_storage_service

router = APIRouter(prefix="/properties", tags=["biens"])

DbSession = Annotated[Session, Depends(get_db)]
Storage = Annotated[StorageService, Depends(get_storage_service)]


def _get_property_or_404(db: Session, property_id: uuid.UUID) -> Property:
    prop = db.get(Property, property_id)
    if prop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bien introuvable.")
    return prop


def _serialize_photo(photo: PropertyPhoto, storage: StorageService) -> PhotoRead:
    data = PhotoRead.model_validate(photo)
    return data.model_copy(update={"url": storage.create_signed_url(photo.storage_path)})


def _serialize_property(prop: Property, storage: StorageService) -> PropertyRead:
    data = PropertyRead.model_validate(prop)
    return data.model_copy(
        update={"photos": [_serialize_photo(photo, storage) for photo in prop.photos]}
    )


def _cover_photo(prop: Property) -> PropertyPhoto | None:
    if not prop.photos:
        return None
    return next((photo for photo in prop.photos if photo.is_cover), prop.photos[0])


@router.get("", response_model=Page[PropertyListItem], summary="Lister les biens")
def list_properties(
    db: DbSession,
    storage: Storage,
    _: CurrentUser,
    q: Annotated[str | None, Query(description="Recherche sur le titre ou l'adresse")] = None,
    status_filter: Annotated[PropertyStatus | None, Query(alias="status")] = None,
    type_filter: Annotated[PropertyType | None, Query(alias="type")] = None,
    city: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[PropertyListItem]:
    filters = []
    if q:
        pattern = f"%{q.strip()}%"
        filters.append(or_(Property.title.ilike(pattern), Property.address.ilike(pattern)))
    if status_filter is not None:
        filters.append(Property.status == str(status_filter))
    if type_filter is not None:
        filters.append(Property.type == str(type_filter))
    if city:
        filters.append(Property.city.ilike(f"%{city.strip()}%"))

    total = db.scalar(select(func.count()).select_from(Property).where(*filters)) or 0
    rows = db.scalars(
        select(Property)
        .where(*filters)
        .options(selectinload(Property.photos))
        .order_by(Property.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    items = []
    for row in rows:
        item = PropertyListItem.model_validate(row)
        cover = _cover_photo(row)
        cover_url = storage.create_signed_url(cover.storage_path) if cover else None
        items.append(item.model_copy(update={"cover_url": cover_url}))

    return Page[PropertyListItem](items=items, total=total, limit=limit, offset=offset)


@router.post(
    "",
    response_model=PropertyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Creer un bien",
)
def create_property(
    payload: PropertyCreate,
    db: DbSession,
    storage: Storage,
    _: PropertyManagerUser,
) -> PropertyRead:
    prop = Property(**payload.model_dump())
    prop.type = str(payload.type)
    prop.status = str(payload.status)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return _serialize_property(prop, storage)


@router.get("/{property_id}", response_model=PropertyRead, summary="Detail d'un bien")
def get_property(
    property_id: uuid.UUID,
    db: DbSession,
    storage: Storage,
    _: CurrentUser,
) -> PropertyRead:
    prop = _get_property_or_404(db, property_id)
    return _serialize_property(prop, storage)


@router.patch("/{property_id}", response_model=PropertyRead, summary="Modifier un bien")
def update_property(
    property_id: uuid.UUID,
    payload: PropertyUpdate,
    db: DbSession,
    storage: Storage,
    _: PropertyManagerUser,
) -> PropertyRead:
    prop = _get_property_or_404(db, property_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prop, field, str(value) if field in {"type", "status"} else value)
    db.commit()
    db.refresh(prop)
    return _serialize_property(prop, storage)


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
    summary="Supprimer un bien",
)
def delete_property(property_id: uuid.UUID, db: DbSession, storage: Storage) -> Response:
    prop = _get_property_or_404(db, property_id)
    paths = [photo.storage_path for photo in prop.photos]
    db.delete(prop)
    db.commit()
    for path in paths:
        storage.delete_object(path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Photos ---------------------------------------------------------------


@router.post(
    "/{property_id}/photos/upload-url",
    response_model=PhotoUploadTicket,
    summary="Obtenir une URL d'upload signee",
)
def create_photo_upload_url(
    property_id: uuid.UUID,
    payload: PhotoUploadRequest,
    db: DbSession,
    storage: Storage,
    _: PropertyManagerUser,
) -> PhotoUploadTicket:
    """Le navigateur compresse l'image puis la televerse directement avec ce jeton."""
    _get_property_or_404(db, property_id)
    storage_path = build_storage_path(property_id, payload.filename)
    signed_url, token = storage.create_signed_upload_url(storage_path)
    return PhotoUploadTicket(
        bucket=storage.bucket,
        storage_path=storage_path,
        token=token,
        signed_url=signed_url,
    )


@router.post(
    "/{property_id}/photos",
    response_model=PhotoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Enregistrer une photo televersee",
)
def register_photo(
    property_id: uuid.UUID,
    payload: PhotoCreate,
    db: DbSession,
    storage: Storage,
    _: PropertyManagerUser,
) -> PhotoRead:
    _get_property_or_404(db, property_id)
    expected_prefix = f"properties/{property_id}/"
    if not payload.storage_path.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le chemin de stockage ne correspond pas a ce bien.",
        )

    photo = PropertyPhoto(
        property_id=property_id,
        storage_path=payload.storage_path,
        is_cover=payload.is_cover,
    )
    if payload.is_cover:
        _clear_covers(db, property_id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return _serialize_photo(photo, storage)


@router.patch(
    "/{property_id}/photos/{photo_id}/cover",
    response_model=PhotoRead,
    summary="Definir la photo de couverture",
)
def set_cover_photo(
    property_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: DbSession,
    storage: Storage,
    _: PropertyManagerUser,
) -> PhotoRead:
    photo = _get_photo_or_404(db, property_id, photo_id)
    _clear_covers(db, property_id)
    photo.is_cover = True
    db.commit()
    db.refresh(photo)
    return _serialize_photo(photo, storage)


@router.delete(
    "/{property_id}/photos/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une photo",
)
def delete_photo(
    property_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: DbSession,
    storage: Storage,
    _: PropertyManagerUser,
) -> Response:
    photo = _get_photo_or_404(db, property_id, photo_id)
    storage_path = photo.storage_path
    db.delete(photo)
    db.commit()
    storage.delete_object(storage_path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _get_photo_or_404(db: Session, property_id: uuid.UUID, photo_id: uuid.UUID) -> PropertyPhoto:
    photo = db.scalar(
        select(PropertyPhoto).where(
            PropertyPhoto.id == photo_id,
            PropertyPhoto.property_id == property_id,
        )
    )
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo introuvable.")
    return photo


def _clear_covers(db: Session, property_id: uuid.UUID) -> None:
    """Une seule photo de couverture par bien."""
    for existing in db.scalars(
        select(PropertyPhoto).where(
            PropertyPhoto.property_id == property_id,
            PropertyPhoto.is_cover.is_(True),
        )
    ).all():
        existing.is_cover = False
