"""Acces au Storage Supabase (photos des biens).

Le bucket est prive. Le navigateur ne recoit jamais la cle de service : il
demande a l'API un jeton d'upload signe, televerse directement le fichier vers
Supabase, puis l'API enregistre le chemin en base. A la lecture, l'API renvoie
des URLs signees a duree limitee.
"""

from __future__ import annotations

import uuid
from pathlib import PurePosixPath
from urllib.parse import parse_qs, urlparse

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
_DEFAULT_EXTENSION = ".webp"
_TIMEOUT = httpx.Timeout(15.0)


class StorageError(Exception):
    """Erreur renvoyee par l'API Storage de Supabase."""


def build_storage_path(*segments: object, filename: str) -> str:
    """Chemin stable et sans collision, range sous les segments donnes.

    Exemples : ("properties", bien_id) pour une photo de bien,
    ("tickets", ticket_id, "avant") pour une photo de maintenance.
    """
    extension = PurePosixPath(filename).suffix.lower()
    if extension not in _ALLOWED_EXTENSIONS:
        extension = _DEFAULT_EXTENSION
    prefix = "/".join(str(segment) for segment in segments)
    return f"{prefix}/{uuid.uuid4().hex}{extension}"


class StorageService:
    """Client minimal de l'API Storage, limite a ce dont le module Biens a besoin."""

    def __init__(
        self,
        base_url: str | None = None,
        service_key: str | None = None,
        bucket: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.supabase_url).rstrip("/")
        self.service_key = service_key or settings.supabase_service_role_key
        self.bucket = bucket or settings.supabase_storage_bucket

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.service_key)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.service_key}",
            "apikey": self.service_key,
        }

    def _require_configuration(self) -> None:
        if not self.is_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Le Storage Supabase n'est pas configure sur ce serveur.",
            )

    def _absolute(self, relative_url: str) -> str:
        return f"{self.base_url}/storage/v1{relative_url}"

    def create_signed_upload_url(self, storage_path: str) -> tuple[str, str]:
        """Retourne (url_signee_absolue, token) pour un upload direct navigateur."""
        self._require_configuration()
        endpoint = (
            f"{self.base_url}/storage/v1/object/upload/sign/{self.bucket}/{storage_path}"
        )
        try:
            response = httpx.post(endpoint, headers=self._headers(), timeout=_TIMEOUT)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Impossible de preparer l'upload vers le Storage.",
            ) from exc

        relative_url = response.json().get("url", "")
        token = parse_qs(urlparse(relative_url).query).get("token", [""])[0]
        if not token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Le Storage n'a pas renvoye de jeton d'upload.",
            )
        return self._absolute(relative_url), token

    def create_signed_url(self, storage_path: str, expires_in: int | None = None) -> str | None:
        """URL de lecture temporaire, ou None si le Storage n'est pas configure."""
        if not self.is_configured:
            return None
        endpoint = f"{self.base_url}/storage/v1/object/sign/{self.bucket}/{storage_path}"
        payload = {"expiresIn": expires_in or settings.signed_url_expires_in}
        try:
            response = httpx.post(
                endpoint, headers=self._headers(), json=payload, timeout=_TIMEOUT
            )
            response.raise_for_status()
        except httpx.HTTPError:
            # Une photo illisible ne doit pas faire echouer l'affichage du bien.
            return None

        relative_url = response.json().get("signedURL")
        return self._absolute(relative_url) if relative_url else None

    def delete_object(self, storage_path: str) -> None:
        """Supprime un fichier. L'echec est tolere, la ligne en base part quand meme."""
        if not self.is_configured:
            return
        endpoint = f"{self.base_url}/storage/v1/object/{self.bucket}/{storage_path}"
        try:
            httpx.delete(endpoint, headers=self._headers(), timeout=_TIMEOUT)
        except httpx.HTTPError:
            return


def get_storage_service() -> StorageService:
    """Storage des photos de biens. Dependance surchargeable dans les tests."""
    return StorageService()


def get_maintenance_storage_service() -> StorageService:
    """Storage des photos de maintenance, dans un bucket distinct.

    Bucket separe plutot qu'un prefixe dans celui des biens : les volumes et la
    duree de conservation n'ont rien a voir, et les policies pourront diverger.
    """
    return StorageService(bucket=settings.supabase_maintenance_bucket)
