"""Prestataires d'intervention (plombiers, electriciens, macons...).

Table dediee plutot que des champs libres sur le ticket : l'agence retravaille
avec les memes artisans, et une table evite les doublons de saisie tout en
permettant de retrouver l'historique d'un prestataire.
"""

import uuid

from sqlalchemy import Boolean, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Contractor(Base, TimestampMixin):
    __tablename__ = "contractors"
    __table_args__ = (Index("idx_contractors_name", "name"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    # Metier, en texte libre : la liste varie trop pour etre figee.
    trade: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Un prestataire avec qui on ne travaille plus est desactive, pas supprime,
    # pour ne pas perdre l'historique des tickets.
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
