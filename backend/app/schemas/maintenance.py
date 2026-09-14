"""Schemas des tickets de maintenance et de leurs photos."""

import builtins
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.models.enums import TicketPriority, TicketStatus
from app.schemas.common import Amount
from app.schemas.contractor import ContractorSummary

PhotoKind = Literal["avant", "apres"]


class TicketPropertySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    city: str


class TicketReporterSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str


class MaintenancePhotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ticket_id: uuid.UUID
    storage_path: str
    kind: PhotoKind
    created_at: datetime
    # URL signee, calculee a la lecture. Le bucket reste prive.
    url: str | None = None


class MaintenancePhotoCreate(BaseModel):
    """Enregistre une photo deja televersee dans le Storage."""

    storage_path: str = Field(min_length=1, max_length=500)
    kind: PhotoKind = "avant"


class MaintenancePhotoUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(default="image/webp", max_length=100)


class TicketBase(BaseModel):
    property_id: uuid.UUID
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    priority: TicketPriority
    status: TicketStatus
    contractor_id: uuid.UUID | None = None
    estimated_cost: Amount | None = None
    actual_cost: Amount | None = None
    billed_to_owner: bool = False

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        return value.strip()


class TicketCreate(TicketBase):
    priority: TicketPriority = TicketPriority.MOYENNE
    status: TicketStatus = TicketStatus.OUVERT


class TicketUpdate(BaseModel):
    """Mise a jour partielle. Le bien concerne n'est pas modifiable."""

    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    priority: TicketPriority | None = None
    status: TicketStatus | None = None
    contractor_id: uuid.UUID | None = None
    estimated_cost: Amount | None = None
    actual_cost: Amount | None = None
    billed_to_owner: bool | None = None


class TicketRead(TicketBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reported_by: uuid.UUID | None = None
    created_at: datetime
    resolved_at: datetime | None = None

    property: TicketPropertySummary | None = None
    reporter: TicketReporterSummary | None = None
    contractor: ContractorSummary | None = None
    photos: list[MaintenancePhotoRead] = Field(default_factory=list)

    # builtins.property : dans le corps de cette classe, le nom `property` est
    # masque par le champ du meme nom declare plus haut.
    @computed_field
    @builtins.property
    def is_open(self) -> bool:
        """Un ticket encore a traiter, quel que soit son avancement."""
        return self.status in {TicketStatus.OUVERT, TicketStatus.EN_COURS}

    @computed_field
    @builtins.property
    def cost_overrun(self) -> str | None:
        """Ecart entre la facture et le devis, utile face a un proprietaire."""
        if self.estimated_cost is None or self.actual_cost is None:
            return None
        return str(self.actual_cost - self.estimated_cost)


class TicketListItem(TicketRead):
    """Meme forme que le detail, sans les photos, pour alleger la liste."""

    photos: list[MaintenancePhotoRead] = Field(default_factory=list, exclude=True)
