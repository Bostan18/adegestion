"""Utilisateurs de l'agence.

L'identifiant est celui de Supabase Auth (auth.users.id). La table sert de
profil applicatif et fait autorite sur le role : l'API lit le role ici, et un
trigger le recopie dans le JWT pour que les policies RLS puissent l'utiliser.
"""

import uuid

from sqlalchemy import CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.models.enums import UserRole, check_expression


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(check_expression("role", UserRole), name="users_role_check"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # La contrainte UNIQUE fournit deja un index, inutile d'en ajouter un second.
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)

    def has_role(self, *roles: str) -> bool:
        return self.role in roles

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
