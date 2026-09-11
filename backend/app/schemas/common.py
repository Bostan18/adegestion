"""Schemas partages."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Reponse paginee standard de l'API."""

    items: list[T]
    total: int
    limit: int
    offset: int


class Message(BaseModel):
    detail: str
