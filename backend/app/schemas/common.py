"""Schemas partages."""

from decimal import Decimal
from typing import Annotated, Generic, TypeVar

from pydantic import AfterValidator, BaseModel, Field

T = TypeVar("T")


def normalize_amount(value: Decimal | None) -> Decimal | None:
    """Supprime les zeros de fin ajoutes par le driver de base de donnees.

    Un NUMERIC sans precision peut revenir en "500000.0000000000" selon le
    dialecte. On renvoie toujours la forme la plus courte, sans notation
    exponentielle, pour que le frontend affiche un montant lisible.
    """
    if value is None:
        return None
    normalized = value.normalize()
    if normalized == normalized.to_integral_value():
        normalized = normalized.quantize(Decimal(1))
    return normalized


# Montants en francs CFA, surfaces en m2.
Amount = Annotated[Decimal, Field(ge=0), AfterValidator(normalize_amount)]


class Page(BaseModel, Generic[T]):
    """Reponse paginee standard de l'API."""

    items: list[T]
    total: int
    limit: int
    offset: int


class Message(BaseModel):
    detail: str
