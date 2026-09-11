"""Schemas des utilisateurs."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    """Creation d'un profil pour un compte Supabase Auth existant."""

    id: uuid.UUID


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
