"""Schemas des paiements de loyers."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.models.enums import PaymentMethod, PaymentStatus
from app.schemas.common import Amount


class PaymentPropertySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str


class PaymentLeaseSummary(BaseModel):
    """Resume du bail regle, pour identifier le paiement sans second appel."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_name: str
    property: PaymentPropertySummary | None = None


class PaymentBase(BaseModel):
    lease_id: uuid.UUID
    amount: Amount
    payment_method: PaymentMethod
    # Indispensable pour tracer un cheque et pouvoir le passer en "rejete".
    reference_number: str | None = Field(default=None, max_length=120)
    period_start: date
    period_end: date
    due_date: date
    # Vide tant que le paiement n'est pas abouti.
    paid_at: date | None = None
    status: PaymentStatus
    receipt_generated: bool = False

    @field_validator("reference_number")
    @classmethod
    def strip_reference(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class PaymentCreate(PaymentBase):
    status: PaymentStatus = PaymentStatus.PAYE
    receipt_generated: bool = False


class PaymentUpdate(BaseModel):
    """Mise a jour partielle. Le bail regle n'est pas modifiable."""

    amount: Amount | None = None
    payment_method: PaymentMethod | None = None
    reference_number: str | None = Field(default=None, max_length=120)
    period_start: date | None = None
    period_end: date | None = None
    due_date: date | None = None
    paid_at: date | None = None
    status: PaymentStatus | None = None


class PaymentRead(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    lease: PaymentLeaseSummary | None = None

    @computed_field
    @property
    def is_overdue(self) -> bool:
        """Loyer attendu dont l'echeance est passee.

        Calcule a la lecture plutot que stocke : sans cela il faudrait un
        traitement planifie pour basculer les statuts chaque nuit, ce qui est
        disproportionne ici. Le statut `en_retard` reste saisissable a la main
        par le comptable, cet indicateur ne fait que signaler le cas.
        """
        if self.status in {PaymentStatus.PAYE, PaymentStatus.REJETE}:
            return False
        return self.due_date < date.today()


class PaymentTotals(BaseModel):
    """Totaux d'une selection de paiements, affiches au-dessus de la liste."""

    encaisse: Amount
    attendu: Amount


class PaymentPage(BaseModel):
    """Page de paiements, avec les totaux calcules sur les memes filtres."""

    items: list[PaymentRead]
    total: int
    limit: int
    offset: int
    totals: PaymentTotals
