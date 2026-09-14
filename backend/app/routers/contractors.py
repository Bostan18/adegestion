"""Prestataires d'intervention.

RBAC aligne sur les tickets : les trois roles consultent la liste, l'admin et
l'agent la tiennent a jour, seul l'admin supprime.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, PropertyManagerUser, require_admin
from app.models.contractor import Contractor
from app.schemas.common import Page
from app.schemas.contractor import ContractorCreate, ContractorRead, ContractorUpdate
from app.services.maintenance import ensure_contractor_detachable

router = APIRouter(prefix="/contractors", tags=["prestataires"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_contractor_or_404(db: Session, contractor_id: uuid.UUID) -> Contractor:
    contractor = db.get(Contractor, contractor_id)
    if contractor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prestataire introuvable."
        )
    return contractor


@router.get("", response_model=Page[ContractorRead], summary="Lister les prestataires")
def list_contractors(
    db: DbSession,
    _: CurrentUser,
    q: Annotated[str | None, Query(description="Recherche sur le nom ou le metier")] = None,
    is_active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[ContractorRead]:
    filters = []
    if q:
        pattern = f"%{q.strip()}%"
        filters.append(or_(Contractor.name.ilike(pattern), Contractor.trade.ilike(pattern)))
    if is_active is not None:
        filters.append(Contractor.is_active.is_(is_active))

    total = db.scalar(select(func.count()).select_from(Contractor).where(*filters)) or 0
    rows = db.scalars(
        select(Contractor).where(*filters).order_by(Contractor.name).limit(limit).offset(offset)
    ).all()

    return Page[ContractorRead](
        items=[ContractorRead.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=ContractorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un prestataire",
)
def create_contractor(
    payload: ContractorCreate, db: DbSession, _: PropertyManagerUser
) -> Contractor:
    contractor = Contractor(**payload.model_dump())
    db.add(contractor)
    db.commit()
    db.refresh(contractor)
    return contractor


@router.get(
    "/{contractor_id}", response_model=ContractorRead, summary="Detail d'un prestataire"
)
def get_contractor(contractor_id: uuid.UUID, db: DbSession, _: CurrentUser) -> Contractor:
    return _get_contractor_or_404(db, contractor_id)


@router.patch(
    "/{contractor_id}", response_model=ContractorRead, summary="Modifier un prestataire"
)
def update_contractor(
    contractor_id: uuid.UUID,
    payload: ContractorUpdate,
    db: DbSession,
    _: PropertyManagerUser,
) -> Contractor:
    contractor = _get_contractor_or_404(db, contractor_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contractor, field, value)
    db.commit()
    db.refresh(contractor)
    return contractor


@router.delete(
    "/{contractor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
    summary="Supprimer un prestataire",
)
def delete_contractor(contractor_id: uuid.UUID, db: DbSession) -> Response:
    contractor = _get_contractor_or_404(db, contractor_id)
    # Un prestataire deja intervenu se desactive, il ne se supprime pas.
    ensure_contractor_detachable(db, contractor_id)
    db.delete(contractor)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
