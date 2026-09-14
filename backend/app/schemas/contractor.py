"""Schemas des prestataires d'intervention."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContractorBase(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    trade: str | None = Field(default=None, max_length=120)
    contact: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)
    is_active: bool = True

    @field_validator("name", "trade")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ContractorCreate(ContractorBase):
    pass


class ContractorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    trade: str | None = Field(default=None, max_length=120)
    contact: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)
    is_active: bool | None = None


class ContractorRead(ContractorBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class ContractorSummary(BaseModel):
    """Version courte, imbriquee dans un ticket."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    trade: str | None = None
    contact: str | None = None
