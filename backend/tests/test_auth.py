"""Tests d'authentification : validite du jeton et existence du profil."""

import uuid
from datetime import timedelta

from app.models.enums import UserRole
from tests.conftest import make_token


def test_health_est_public(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_me_sans_jeton_renvoie_401(client):
    response = client.get("/api/v1/me")
    assert response.status_code == 401


def test_me_avec_jeton_malforme_renvoie_401(client):
    response = client.get("/api/v1/me", headers={"Authorization": "Bearer pas-un-jwt"})
    assert response.status_code == 401


def test_me_avec_jeton_signe_par_un_autre_secret_renvoie_401(client, make_user):
    user = make_user(UserRole.ADMIN)
    token = make_token(str(user.id), secret="mauvais-secret")
    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_me_avec_jeton_expire_renvoie_401(client, make_user):
    user = make_user(UserRole.AGENT)
    token = make_token(str(user.id), expires_in=timedelta(minutes=-5))
    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_me_avec_mauvaise_audience_renvoie_401(client, make_user):
    user = make_user(UserRole.AGENT)
    token = make_token(str(user.id), audience="autre-audience")
    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_compte_sans_profil_renvoie_403(client):
    """Le jeton est valide mais aucun utilisateur de l'agence ne correspond."""
    token = make_token(str(uuid.uuid4()))
    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_me_renvoie_le_profil(client, make_user, auth_headers):
    user = make_user(UserRole.COMPTABLE, email="comptable@adeimmo.ci", full_name="Awa Traore")
    response = client.get("/api/v1/me", headers=auth_headers(user))

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "comptable@adeimmo.ci"
    assert body["full_name"] == "Awa Traore"
    assert body["role"] == "comptable"


def test_le_role_du_jeton_ne_prime_pas_sur_la_base(client, make_user):
    """Un jeton qui annonce "admin" ne donne pas les droits admin."""
    agent = make_user(UserRole.AGENT)
    token = make_token(str(agent.id), role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/v1/me", headers=headers).json()["role"] == "agent"
    assert client.get("/api/v1/users", headers=headers).status_code == 403
