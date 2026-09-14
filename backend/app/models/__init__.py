"""Tous les modeles, importes ici pour qu'Alembic voie la metadata complete."""

from app.db.base import Base
from app.models.contractor import Contractor
from app.models.lease import Lease
from app.models.maintenance_ticket import MaintenancePhoto, MaintenanceTicket
from app.models.payment import Payment
from app.models.property import Property, PropertyPhoto
from app.models.user import User

__all__ = [
    "Base",
    "Contractor",
    "Lease",
    "MaintenancePhoto",
    "MaintenanceTicket",
    "Payment",
    "Property",
    "PropertyPhoto",
    "User",
]
