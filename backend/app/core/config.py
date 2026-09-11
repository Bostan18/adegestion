"""Configuration de l'application, lue depuis l'environnement."""

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    # NoDecode : sans cela, pydantic-settings tente un json.loads sur la
    # variable d'environnement avant le validateur, et "http://localhost:3000"
    # n'est pas du JSON valide.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # Base de donnees
    database_url: str = "postgresql+psycopg://adeimmo:adeimmo@localhost:5432/adeimmo"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""
    supabase_jwt_audience: str = "authenticated"

    # Storage
    supabase_storage_bucket: str = "property-photos"
    signed_url_expires_in: int = 3600

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: object) -> object:
        """Autorise la notation "a,b,c" dans la variable d'environnement."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    @property
    def storage_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
