"""Tests de la configuration lue depuis l'environnement."""

from app.core.config import Settings


def build_settings() -> Settings:
    """Instancie la configuration sans lire de fichier .env local."""
    return Settings(_env_file=None)


def test_cors_origins_accepte_une_liste_separee_par_des_virgules(monkeypatch):
    """Regression : pydantic-settings tentait un json.loads avant le validateur."""
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,https://adeimmo.onrender.com")

    assert build_settings().cors_origins == [
        "http://localhost:3000",
        "https://adeimmo.onrender.com",
    ]


def test_cors_origins_accepte_une_seule_origine(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://adeimmo.onrender.com")
    assert build_settings().cors_origins == ["https://adeimmo.onrender.com"]


def test_cors_origins_ignore_les_espaces_et_les_entrees_vides(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", " http://localhost:3000 , , http://127.0.0.1:3000 ")
    assert build_settings().cors_origins == ["http://localhost:3000", "http://127.0.0.1:3000"]


def test_cors_origins_par_defaut(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    assert build_settings().cors_origins == ["http://localhost:3000"]


def test_is_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    assert build_settings().is_production is True

    monkeypatch.setenv("ENVIRONMENT", "development")
    assert build_settings().is_production is False


def test_storage_configured(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://projet.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "")
    assert build_settings().storage_configured is False

    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "cle")
    assert build_settings().storage_configured is True
