"""Point d'entree de l'API AdeImmo."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import health, leases, properties, users

app = FastAPI(
    title="AdeImmo API",
    description="API de gestion immobiliere pour l'agence.",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(properties.router, prefix=settings.api_v1_prefix)
app.include_router(leases.router, prefix=settings.api_v1_prefix)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"service": "adeimmo-api", "version": app.version}
