"""Schemas des baux."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import LeaseStatus, PropertyType
from app.schemas.common import Amount


class LeasePropertySummary(BaseModel):
    """Resume du bien loue, pour eviter un aller-retour depuis le frontend."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    type: PropertyType
    city: str


class LeaseDatesMixin(BaseModel):
    """Controle de coherence des dates, partage par la creation et la mise a jour."""

    @model_validator(mode="after")
    def check_period(self):
        start = getattr(self, "start_date", None)
        end = getattr(self, "end_date", None)
        if start and end and end < start:
            raise ValueError("La date de fin ne peut pas preceder la date de debut.")
        return self


class LeaseBase(LeaseDatesMixin):
    property_id: uuid.UUID
    tenant_name: str = Field(min_length=2, max_length=200)
    tenant_contact: str | None = Field(default=None, max_length=200)
    start_date: date
    # Une date de fin vide correspond a un bail sans terme fixe.
    end_date: date | None = None
    rent_amount: Amount
    deposit_amount: Amount | None = None
    status: LeaseStatus

    @field_validator("tenant_name")
    @classmethod
    def strip_tenant_name(cls, value: str) -> str:
        return value.strip()


class LeaseCreate(LeaseBase):
    status: LeaseStatus = LeaseStatus.ACTIF


class LeaseUpdate(LeaseDatesMixin):
    """Mise a jour partielle. Le bien rattache n'est pas modifiable."""

    tenant_name: str | None = Field(default=None, min_length=2, max_length=200)
    tenant_contact: str | None = Field(default=None, max_length=200)
    start_date: date | None = None
    end_date: date | None = None
    rent_amount: Amount | None = None
    deposit_amount: Amount | None = None
    status: LeaseStatus | None = None


class LeaseRead(LeaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    property: LeasePropertySummary | None = None
