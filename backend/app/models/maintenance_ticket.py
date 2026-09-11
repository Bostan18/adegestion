"""Tickets de maintenance. Module non encore expose par l'API."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text
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
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id"), nullable=False)
    reported_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    property = relationship("Property")
    reporter = relationship("User")
