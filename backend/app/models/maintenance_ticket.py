"""Tickets de maintenance."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import TicketPriority, TicketStatus, check_expression


class MaintenanceTicket(Base, TimestampMixin):
    __tablename__ = "maintenance_tickets"
    __table_args__ = (
        CheckConstraint(
            check_expression("priority", TicketPriority),
            name="maintenance_tickets_priority_check",
        ),
        CheckConstraint(
            check_expression("status", TicketStatus),
            name="maintenance_tickets_status_check",
        ),
        Index("idx_maintenance_property_id", "property_id"),
        Index("idx_maintenance_contractor_id", "contractor_id"),
        Index("idx_maintenance_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id"), nullable=False)
    reported_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    contractor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("contractors.id", ondelete="SET NULL"), nullable=True
    )
    # Devis annonce a l'ouverture, puis facture reelle a la resolution.
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    actual_cost: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    billed_to_owner: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    property = relationship("Property")
    reporter = relationship("User")
    contractor = relationship("Contractor")
    photos: Mapped[list["MaintenancePhoto"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="MaintenancePhoto.created_at",
    )


class MaintenancePhoto(Base, TimestampMixin):
    """Photo d'un ticket, prise avant ou apres l'intervention."""

    __tablename__ = "maintenance_photos"
    __table_args__ = (
        CheckConstraint("kind IN ('avant', 'apres')", name="maintenance_photos_kind_check"),
        Index("idx_maintenance_photos_ticket_id", "ticket_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("maintenance_tickets.id", ondelete="CASCADE"), nullable=False
    )
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False, default="avant")

    ticket: Mapped[MaintenanceTicket] = relationship(back_populates="photos")
