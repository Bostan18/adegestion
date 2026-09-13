"""Regles metier des baux.

Deux regles, decidees avec l'agence :

1. Deux baux actifs ne peuvent pas se chevaucher sur un meme bien. La creation
   ou la mise a jour qui provoquerait un chevauchement est refusee en 409, en
   nommant le bail en conflit.
2. Le statut du bien suit celui de son bail. Un bail qui devient actif passe le
   bien en "loue". Un bail qui se termine ou se resilie repasse le bien en
   "disponible", mais seulement s'il etait "loue" : un bien mis en travaux ou
   indisponible garde le statut saisi par l'agent.
"""

import uuid

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.enums import LeaseStatus, PropertyStatus
from app.models.lease import Lease
from app.models.property import Property


def get_property_or_404(db: Session, property_id: uuid.UUID) -> Property:
    prop = db.get(Property, property_id)
    if prop is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Bien introuvable."
        )
    return prop


def find_overlapping_lease(
    db: Session,
    property_id: uuid.UUID,
    start_date,
    end_date,
    exclude_lease_id: uuid.UUID | None = None,
) -> Lease | None:
    """Premier bail actif du bien dont la periode croise celle donnee.

    Une date de fin vide signifie "sans terme", donc la periode reste ouverte
    et chevauche tout ce qui commence apres son debut.
    """
    conditions = [
        Lease.property_id == property_id,
        Lease.status == str(LeaseStatus.ACTIF),
        # Le bail existant se termine apres le debut de la nouvelle periode,
        # ou n'a pas de terme.
        or_(Lease.end_date.is_(None), Lease.end_date >= start_date),
    ]
    if end_date is not None:
        # Symetrique : il commence avant la fin de la nouvelle periode.
        conditions.append(Lease.start_date <= end_date)
    if exclude_lease_id is not None:
        conditions.append(Lease.id != exclude_lease_id)

    return db.scalars(select(Lease).where(*conditions).order_by(Lease.start_date)).first()


def ensure_no_overlap(
    db: Session,
    property_id: uuid.UUID,
    start_date,
    end_date,
    exclude_lease_id: uuid.UUID | None = None,
) -> None:
    """Refuse la double location d'un meme bien sur une periode qui se croise."""
    conflict = find_overlapping_lease(
        db, property_id, start_date, end_date, exclude_lease_id=exclude_lease_id
    )
    if conflict is None:
        return

    fin = conflict.end_date.isoformat() if conflict.end_date else "sans terme"
    raise HTTPException(
        status_code=http_status.HTTP_409_CONFLICT,
        detail=(
            f"Un bail actif existe deja sur ce bien pour cette periode "
            f"({conflict.tenant_name}, du {conflict.start_date.isoformat()} au {fin})."
        ),
    )


def has_other_active_lease(
    db: Session, property_id: uuid.UUID, exclude_lease_id: uuid.UUID | None = None
) -> bool:
    conditions = [
        Lease.property_id == property_id,
        Lease.status == str(LeaseStatus.ACTIF),
    ]
    if exclude_lease_id is not None:
        conditions.append(Lease.id != exclude_lease_id)
    return db.scalar(select(Lease.id).where(*conditions).limit(1)) is not None


def mark_property_rented(db: Session, property_id: uuid.UUID) -> None:
    """Un bail actif est un fait : le bien passe en "loue"."""
    prop = db.get(Property, property_id)
    if prop is not None and prop.status != str(PropertyStatus.LOUE):
        prop.status = str(PropertyStatus.LOUE)


def release_property(
    db: Session, property_id: uuid.UUID, exclude_lease_id: uuid.UUID | None = None
) -> None:
    """Repasse le bien en "disponible" s'il ne lui reste aucun bail actif.

    On ne touche pas a un bien "en_travaux" ou "indisponible" : ce statut a ete
    pose a la main par l'agent et prime sur la fin du bail.
    """
    if has_other_active_lease(db, property_id, exclude_lease_id=exclude_lease_id):
        return

    prop = db.get(Property, property_id)
    if prop is not None and prop.status == str(PropertyStatus.LOUE):
        prop.status = str(PropertyStatus.DISPONIBLE)
