"""Tests du RBAC : ce que chaque role peut faire, et surtout ne peut pas faire."""

import uuid

import pytest

from app.models.enums import UserRole

NOUVEAU_BIEN = {
    "title": "Appartement Plateau",
    "type": "appartement",
    "address": "Avenue Franchet d'Esperey",
    "city": "Abidjan",
    "rent_amount": 300000,
    "status": "disponible",
}


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 201), (UserRole.AGENT, 201), (UserRole.COMPTABLE, 403)],
)
def test_creation_de_bien_par_role(client, make_user, auth_headers, role, expected_status):
    user = make_user(role)
    response = client.post("/api/v1/properties", json=NOUVEAU_BIEN, headers=auth_headers(user))
    assert response.status_code == expected_status


@pytest.mark.parametrize("role", [UserRole.ADMIN, UserRole.AGENT, UserRole.COMPTABLE])
def test_tous_les_roles_peuvent_consulter_les_biens(
    client, make_user, auth_headers, sample_property, role
):
    user = make_user(role)
    response = client.get("/api/v1/properties", headers=auth_headers(user))
    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 200), (UserRole.AGENT, 200), (UserRole.COMPTABLE, 403)],
)
def test_modification_de_bien_par_role(
    client, make_user, auth_headers, sample_property, role, expected_status
):
    """Le risque identifie dans l'architecture : un comptable qui modifie un bien."""
    user = make_user(role)
    response = client.patch(
        f"/api/v1/properties/{sample_property.id}",
        json={"status": "loue"},
        headers=auth_headers(user),
    )
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 204), (UserRole.AGENT, 403), (UserRole.COMPTABLE, 403)],
)
def test_suppression_de_bien_reservee_a_admin(
    client, make_user, auth_headers, sample_property, role, expected_status
):
    user = make_user(role)
    response = client.delete(
        f"/api/v1/properties/{sample_property.id}", headers=auth_headers(user)
    )
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 200), (UserRole.AGENT, 403), (UserRole.COMPTABLE, 403)],
)
def test_gestion_des_utilisateurs_reservee_a_admin(
    client, make_user, auth_headers, role, expected_status
):
    user = make_user(role)
    response = client.get("/api/v1/users", headers=auth_headers(user))
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 200), (UserRole.AGENT, 200), (UserRole.COMPTABLE, 403)],
)
def test_upload_de_photo_par_role(
    client, make_user, auth_headers, sample_property, role, expected_status
):
    user = make_user(role)
    response = client.post(
        f"/api/v1/properties/{sample_property.id}/photos/upload-url",
        json={"filename": "facade.webp", "content_type": "image/webp"},
        headers=auth_headers(user),
    )
    assert response.status_code == expected_status


def test_admin_cree_un_profil_utilisateur(client, make_user, auth_headers):
    admin = make_user(UserRole.ADMIN)
    nouvel_id = str(uuid.uuid4())

    response = client.post(
        "/api/v1/users",
        json={
            "id": nouvel_id,
            "email": "agent2@adeimmo.ci",
            "full_name": "Yao Kone",
            "role": "agent",
        },
        headers=auth_headers(admin),
    )

    assert response.status_code == 201
    assert response.json()["role"] == "agent"


def test_creation_de_profil_en_double_renvoie_409(client, make_user, auth_headers):
    admin = make_user(UserRole.ADMIN)
    payload = {
        "id": str(uuid.uuid4()),
        "email": "doublon@adeimmo.ci",
        "full_name": "Doublon",
        "role": "agent",
    }
    premiere = client.post("/api/v1/users", json=payload, headers=auth_headers(admin))
    seconde = client.post("/api/v1/users", json=payload, headers=auth_headers(admin))

    assert premiere.status_code == 201
    assert seconde.status_code == 409


def test_admin_ne_peut_pas_changer_son_propre_role(client, make_user, auth_headers):
    admin = make_user(UserRole.ADMIN)
    response = client.patch(
        f"/api/v1/users/{admin.id}",
        json={"role": "agent"},
        headers=auth_headers(admin),
    )
    assert response.status_code == 400


def test_admin_peut_changer_le_role_d_un_autre(client, make_user, auth_headers):
    admin = make_user(UserRole.ADMIN)
    agent = make_user(UserRole.AGENT)

    response = client.patch(
        f"/api/v1/users/{agent.id}",
        json={"role": "comptable"},
        headers=auth_headers(admin),
    )

    assert response.status_code == 200
    assert response.json()["role"] == "comptable"
