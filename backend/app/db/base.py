"""Classe de base des modeles et import centralise pour Alembic."""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative commune a tous les modeles."""


class TimestampMixin:
    """Colonne created_at partagee par toutes les tables du schema."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
