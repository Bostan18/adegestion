"""Schemas des biens immobiliers et de leurs photos."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import PropertyStatus, PropertyType
from app.schemas.common import Amount


class PropertyBase(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    type: PropertyType
    address: str = Field(min_length=2, max_length=500)
    city: str = Field(min_length=2, max_length=120)
    surface_m2: Amount | None = None
    rent_amount: Amount
    status: PropertyStatus
    owner_name: str | None = Field(default=None, max_length=200)
    owner_contact: str | None = Field(default=None, max_length=200)

    @field_validator("title", "address", "city")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class PropertyCreate(PropertyBase):
    status: PropertyStatus = PropertyStatus.DISPONIBLE


class PropertyUpdate(BaseModel):
    """Mise a jour partielle, tous les champs sont optionnels."""

    title: str | None = Field(default=None, min_length=2, max_length=200)
    type: PropertyType | None = None
    address: str | None = Field(default=None, min_length=2, max_length=500)
    city: str | None = Field(default=None, min_length=2, max_length=120)
    surface_m2: Amount | None = None
    rent_amount: Amount | None = None
    status: PropertyStatus | None = None
    owner_name: str | None = Field(default=None, max_length=200)
    owner_contact: str | None = Field(default=None, max_length=200)


class PhotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    property_id: uuid.UUID
    storage_path: str
    is_cover: bool
    created_at: datetime
    # URL signee, calculee a la lecture. Le bucket reste prive.
    url: str | None = None


class PhotoCreate(BaseModel):
    """Enregistre en base une photo deja televersee dans le Storage."""

    storage_path: str = Field(min_length=1, max_length=500)
    is_cover: bool = False


class PhotoUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(default="image/webp", max_length=100)


class PhotoUploadTicket(BaseModel):
    """Jeton d'upload direct navigateur vers Supabase Storage."""

    bucket: str
    storage_path: str
    token: str
    signed_url: str


class PropertyRead(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    photos: list[PhotoRead] = Field(default_factory=list)


class PropertyListItem(PropertyBase):
    """Version allegee pour la liste, avec seulement la photo de couverture."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    cover_url: str | None = None
