"""Fixtures de test.

Les tests tournent sur une base SQLite temporaire : ils ne touchent jamais au
projet Supabase. Les jetons sont forges avec le meme secret HS256 que celui lu
par l'application, ce qui permet de tester l'auth et le RBAC de bout en bout.
"""

import os
import tempfile
import uuid
from collections.abc import Callable, Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

# Les variables doivent etre posees avant le premier import de app.*, car la
# configuration est chargee une seule fois a l'import.
_TMP_DB = Path(tempfile.mkdtemp(prefix="adeimmo-tests-")) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{_TMP_DB}"
os.environ["SUPABASE_JWT_SECRET"] = "secret-de-test-uniquement"
os.environ["SUPABASE_JWT_AUDIENCE"] = "authenticated"
os.environ["SUPABASE_URL"] = "https://projet-de-test.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "cle-de-service-de-test"
os.environ["ENVIRONMENT"] = "test"

import jwt  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import event  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Lease, Property, PropertyPhoto, User  # noqa: E402
from app.models.enums import UserRole  # noqa: E402
from app.services.storage import StorageService, get_storage_service  # noqa: E402


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    """SQLite n'applique les cles etrangeres que si on le demande."""
    if engine.dialect.name != "sqlite":
        return
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class FakeStorageService(StorageService):
    """Storage simule : aucun appel reseau, comportement deterministe."""

    def __init__(self) -> None:
        super().__init__(
            base_url="https://projet-de-test.supabase.co",
            service_key="cle-de-service-de-test",
            bucket="property-photos",
        )
        self.deleted: list[str] = []

    def create_signed_upload_url(self, storage_path: str) -> tuple[str, str]:
        return (
            f"{self.base_url}/storage/v1/object/upload/sign/{self.bucket}/{storage_path}",
            "jeton-upload-de-test",
        )

    def create_signed_url(self, storage_path: str, expires_in: int | None = None) -> str:
        return f"{self.base_url}/storage/v1/object/sign/{self.bucket}/{storage_path}"

    def delete_object(self, storage_path: str) -> None:
        self.deleted.append(storage_path)


@pytest.fixture(scope="session", autouse=True)
def _create_schema() -> Iterator[None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _clean_tables() -> Iterator[None]:
    """Repart d'une base vide a chaque test."""
    yield
    with SessionLocal() as session:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()


@pytest.fixture
def storage() -> FakeStorageService:
    return FakeStorageService()


@pytest.fixture
def client(storage: FakeStorageService) -> Iterator[TestClient]:
    app.dependency_overrides[get_storage_service] = lambda: storage
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


@pytest.fixture
def make_user(db: Session) -> Callable[..., User]:
    def _make_user(
        role: UserRole = UserRole.AGENT,
        email: str | None = None,
        full_name: str = "Utilisateur Test",
    ) -> User:
        user = User(
            id=uuid.uuid4(),
            email=email or f"{role}-{uuid.uuid4().hex[:8]}@adeimmo.ci",
            full_name=full_name,
            role=str(role),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return _make_user


def make_token(
    subject: str,
    *,
    secret: str | None = None,
    audience: str = "authenticated",
    expires_in: timedelta = timedelta(hours=1),
    role: str | None = None,
) -> str:
    """Forge un jeton equivalent a celui emis par Supabase Auth."""
    now = datetime.now(UTC)
    payload: dict = {
        "sub": subject,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_in).timestamp()),
        "email": "utilisateur@adeimmo.ci",
        "app_metadata": {"role": role} if role else {},
    }
    return jwt.encode(payload, secret or settings.supabase_jwt_secret, algorithm="HS256")


@pytest.fixture
def auth_headers() -> Callable[[User], dict[str, str]]:
    def _headers(user: User) -> dict[str, str]:
        return {"Authorization": f"Bearer {make_token(str(user.id), role=user.role)}"}

    return _headers


@pytest.fixture
def sample_property(db: Session) -> Property:
    prop = Property(
        title="Villa Cocody Angre",
        type="villa",
        address="Rue des Jardins, Angre 7e tranche",
        city="Abidjan",
        surface_m2=180,
        rent_amount=450000,
        status="disponible",
        owner_name="M. Kouassi",
        owner_contact="+225 07 00 00 00 00",
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@pytest.fixture
def sample_lease(db: Session, sample_property: Property) -> Lease:
    lease = Lease(
        property_id=sample_property.id,
        tenant_name="Koffi N'Guessan",
        tenant_contact="+225 07 77 88 99 00",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        rent_amount=450000,
        deposit_amount=900000,
        status="actif",
    )
    db.add(lease)
    db.commit()
    db.refresh(lease)
    return lease


@pytest.fixture
def sample_photo(db: Session, sample_property: Property) -> PropertyPhoto:
    photo = PropertyPhoto(
        property_id=sample_property.id,
        storage_path=f"properties/{sample_property.id}/photo-1.webp",
        is_cover=True,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo
