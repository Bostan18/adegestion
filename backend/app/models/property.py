"""Biens immobiliers et leurs photos."""

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import PropertyStatus, PropertyType, check_expression


class Property(Base, TimestampMixin):
    __tablename__ = "properties"
    __table_args__ = (
        CheckConstraint(check_expression("type", PropertyType), name="properties_type_check"),
        CheckConstraint(
            check_expression("status", PropertyStatus), name="properties_status_check"
        ),
        Index("idx_properties_status", "status"),
        Index("idx_properties_city", "city"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    surface_m2: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    rent_amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    owner_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_contact: Mapped[str | None] = mapped_column(Text, nullable=True)

    photos: Mapped[list["PropertyPhoto"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="PropertyPhoto.created_at",
    )


class PropertyPhoto(Base, TimestampMixin):
    __tablename__ = "property_photos"
    __table_args__ = (Index("idx_property_photos_property_id", "property_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    is_cover: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    property: Mapped[Property] = relationship(back_populates="photos")
