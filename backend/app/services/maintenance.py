"""Regles metier des tickets de maintenance.

Trois regles :

1. `resolved_at` est gere par l'API, jamais saisi. Il se pose quand le ticket
   passe a `resolu` ou `ferme`, et se vide si le ticket est rouvert : sans
   cela, un ticket reouvert garderait une date de resolution mensongere.
2. Un cout reel ne se saisit pas sur un ticket encore ouvert : la facture
   n'arrive qu'apres l'intervention.
3. `reported_by` est renseigne avec l'utilisateur connecte, pas transmis par
   le client, pour que la tracabilite du signalement ne soit pas falsifiable.
"""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contractor import Contractor
from app.models.enums import TicketStatus
from app.models.maintenance_ticket import MaintenanceTicket
from app.models.property import Property

# Statuts pour lesquels l'intervention est consideree terminee.
CLOSED_STATUSES = {str(TicketStatus.RESOLU), str(TicketStatus.FERME)}


def get_property_or_404(db: Session, property_id: uuid.UUID) -> Property:
    prop = db.get(Property, property_id)
    if prop is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Bien introuvable."
        )
    return prop


def ensure_contractor_exists(db: Session, contractor_id: uuid.UUID | None) -> None:
    if contractor_id is None:
        return
    if db.get(Contractor, contractor_id) is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Prestataire introuvable."
        )


def validate_costs(status: str, actual_cost) -> None:
    """Refuse de *saisir* un cout reel sur une intervention non terminee.

    La regle ne porte que sur la saisie. Un cout deja enregistre survit a une
    reouverture : si une premiere intervention a echoue, l'argent a bien ete
    depense, et effacer le montant ou bloquer la reouverture serait faux dans
    les deux cas.
    """
    if actual_cost is not None and status not in CLOSED_STATUSES:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Un cout reel ne peut etre saisi que sur un ticket resolu ou ferme. "
                "Utilisez le cout estime tant que l'intervention est en cours."
            ),
        )


def sync_resolved_at(ticket: MaintenanceTicket, new_status: str) -> None:
    """Aligne la date de resolution sur le statut, dans les deux sens."""
    if new_status in CLOSED_STATUSES:
        if ticket.resolved_at is None:
            ticket.resolved_at = datetime.now(UTC)
    else:
        # Ticket rouvert : la date de resolution n'a plus lieu d'etre.
        ticket.resolved_at = None


def count_tickets_for_contractor(db: Session, contractor_id: uuid.UUID) -> int:
    return len(
        db.scalars(
            select(MaintenanceTicket.id).where(
                MaintenanceTicket.contractor_id == contractor_id
            )
        ).all()
    )


def ensure_contractor_detachable(db: Session, contractor_id: uuid.UUID) -> None:
    """Refuse la suppression d'un prestataire encore rattache a des tickets.

    L'historique d'intervention a de la valeur : on propose de desactiver le
    prestataire plutot que de le supprimer.
    """
    attached = count_tickets_for_contractor(db, contractor_id)
    if attached:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=(
                f"Ce prestataire est rattache a {attached} ticket"
                f"{'s' if attached > 1 else ''}. Desactivez-le plutot que de le supprimer, "
                "pour conserver l'historique."
            ),
        )
