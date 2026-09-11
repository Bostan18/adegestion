"""Baux. Le module Baux n'est pas encore expose par l'API, le modele existe
pour que la migration initiale couvre l'integralite de docs/schema.sql."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import LeaseStatus, check_expression


class Lease(Base, TimestampMixin):
    __tablename__ = "leases"
    __table_args__ = (
        CheckConstraint(check_expression("status", LeaseStatus), name="leases_status_check"),
        Index("idx_leases_property_id", "property_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id"), nullable=False)
    tenant_name: Mapped[str] = mapped_column(Text, nullable=False)
    tenant_contact: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    rent_amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    deposit_amount: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)

    property = relationship("Property")
