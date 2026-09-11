"""Paiements de loyers. Module non encore expose par l'API."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import PaymentMethod, PaymentStatus, check_expression


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint(
            check_expression("payment_method", PaymentMethod),
            name="payments_payment_method_check",
        ),
        CheckConstraint(check_expression("status", PaymentStatus), name="payments_status_check"),
        Index("idx_payments_lease_id", "lease_id"),
        Index("idx_payments_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    lease_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("leases.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    payment_method: Mapped[str] = mapped_column(Text, nullable=False)
    # Indispensable pour tracer un cheque et pouvoir le passer en "rejete".
    reference_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    paid_at: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    receipt_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    lease = relationship("Lease")
