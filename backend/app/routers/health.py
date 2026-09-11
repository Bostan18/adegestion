"""Sonde de sante, utilisee par Render et docker compose."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Etat du service")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
