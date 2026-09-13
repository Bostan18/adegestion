"""Tests du module Baux : CRUD, permissions, chevauchements et statut du bien."""

import uuid
from datetime import date

import pytest

from app.models.enums import UserRole
from app.models.lease import Lease
from app.models.property import Property


@pytest.fixture
def agent(make_user):
    return make_user(UserRole.AGENT)


@pytest.fixture
def admin(make_user):
    return make_user(UserRole.ADMIN)


def bail(property_id, **overrides) -> dict:
    payload = {
        "property_id": str(property_id),
        "tenant_name": "Koffi N'Guessan",
        "tenant_contact": "+225 07 77 88 99 00",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "rent_amount": "450000",
        "deposit_amount": "900000",
        "status": "actif",
    }
    payload.update(overrides)
    return payload


# --- CRUD -----------------------------------------------------------------


def test_creation_puis_lecture(client, agent, auth_headers, sample_property):
    created = client.post(
        "/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent)
    )
    assert created.status_code == 201
    body = created.json()
    assert body["tenant_name"] == "Koffi N'Guessan"
    assert body["rent_amount"] == "450000"
    # Le bien est resume dans la reponse, pour eviter un second appel.
    assert body["property"]["title"] == "Villa Cocody Angre"

    fetched = client.get(f"/api/v1/leases/{body['id']}", headers=auth_headers(agent))
    assert fetched.status_code == 200
    assert fetched.json()["deposit_amount"] == "900000"


def test_statut_par_defaut_actif(client, agent, auth_headers, sample_property):
    payload = bail(sample_property.id)
    del payload["status"]
    response = client.post("/api/v1/leases", json=payload, headers=auth_headers(agent))
    assert response.status_code == 201
    assert response.json()["status"] == "actif"


def test_bail_sans_terme(client, agent, auth_headers, sample_property):
    response = client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, end_date=None),
        headers=auth_headers(agent),
    )
    assert response.status_code == 201
    assert response.json()["end_date"] is None


def test_bien_inconnu_renvoie_404(client, agent, auth_headers):
    response = client.post(
        "/api/v1/leases", json=bail(uuid.uuid4()), headers=auth_headers(agent)
    )
    assert response.status_code == 404


def test_date_de_fin_avant_le_debut_renvoie_422(client, agent, auth_headers, sample_property):
    response = client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, start_date="2026-06-01", end_date="2026-01-01"),
        headers=auth_headers(agent),
    )
    assert response.status_code == 422


def test_mise_a_jour_partielle(client, agent, auth_headers, sample_property):
    created = client.post(
        "/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent)
    ).json()

    response = client.patch(
        f"/api/v1/leases/{created['id']}",
        json={"rent_amount": "500000", "tenant_contact": "+225 01 02 03 04 05"},
        headers=auth_headers(agent),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["rent_amount"] == "500000"
    assert body["tenant_name"] == "Koffi N'Guessan"


def test_mise_a_jour_avec_fin_anterieure_au_debut_refusee(
    client, agent, auth_headers, sample_property
):
    created = client.post(
        "/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent)
    ).json()

    response = client.patch(
        f"/api/v1/leases/{created['id']}",
        json={"end_date": "2025-06-01"},
        headers=auth_headers(agent),
    )
    assert response.status_code == 422


def test_filtres_et_pagination(client, agent, auth_headers, sample_property, db):
    autre = Property(
        title="Studio Marcory",
        type="appartement",
        address="Rue du Canal",
        city="Abidjan",
        rent_amount=200000,
        status="disponible",
    )
    db.add(autre)
    db.commit()
    db.refresh(autre)

    client.post("/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent))
    client.post(
        "/api/v1/leases",
        json=bail(autre.id, tenant_name="Awa Bamba", start_date="2025-01-01",
                  end_date="2025-12-31", status="termine"),
        headers=auth_headers(agent),
    )

    tous = client.get("/api/v1/leases", headers=auth_headers(agent)).json()
    assert tous["total"] == 2

    actifs = client.get("/api/v1/leases?status=actif", headers=auth_headers(agent)).json()
    assert actifs["total"] == 1

    par_bien = client.get(
        f"/api/v1/leases?property_id={autre.id}", headers=auth_headers(agent)
    ).json()
    assert par_bien["total"] == 1
    assert par_bien["items"][0]["tenant_name"] == "Awa Bamba"

    recherche = client.get("/api/v1/leases?q=bamba", headers=auth_headers(agent)).json()
    assert recherche["total"] == 1


# --- Regle 1 : pas de chevauchement de baux actifs -------------------------


def test_chevauchement_refuse(client, agent, auth_headers, sample_property):
    premier = client.post(
        "/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent)
    )
    assert premier.status_code == 201

    second = client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, tenant_name="Autre Locataire",
                  start_date="2026-06-01", end_date="2027-05-31"),
        headers=auth_headers(agent),
    )

    assert second.status_code == 409
    assert "Koffi N'Guessan" in second.json()["detail"]


def test_periodes_qui_ne_se_croisent_pas_acceptees(
    client, agent, auth_headers, sample_property
):
    client.post("/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent))

    suivant = client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, tenant_name="Locataire Suivant",
                  start_date="2027-01-01", end_date="2027-12-31"),
        headers=auth_headers(agent),
    )
    assert suivant.status_code == 201


def test_bail_sans_terme_bloque_toute_periode_posterieure(
    client, agent, auth_headers, sample_property
):
    client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, end_date=None),
        headers=auth_headers(agent),
    )

    response = client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, tenant_name="Autre", start_date="2030-01-01",
                  end_date="2030-12-31"),
        headers=auth_headers(agent),
    )
    assert response.status_code == 409


def test_un_bail_termine_ne_bloque_pas(client, agent, auth_headers, sample_property):
    client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, status="termine"),
        headers=auth_headers(agent),
    )

    response = client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, tenant_name="Nouveau"),
        headers=auth_headers(agent),
    )
    assert response.status_code == 201


def test_chevauchement_sur_un_autre_bien_autorise(client, agent, auth_headers, sample_property, db):
    autre = Property(
        title="Bureau Zone 4",
        type="bureau",
        address="Rue Curie",
        city="Abidjan",
        rent_amount=300000,
        status="disponible",
    )
    db.add(autre)
    db.commit()
    db.refresh(autre)

    client.post("/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent))
    response = client.post("/api/v1/leases", json=bail(autre.id), headers=auth_headers(agent))
    assert response.status_code == 201


def test_mise_a_jour_ne_se_bloque_pas_elle_meme(client, agent, auth_headers, sample_property):
    """Le bail modifie doit etre exclu de son propre controle de chevauchement."""
    created = client.post(
        "/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent)
    ).json()

    response = client.patch(
        f"/api/v1/leases/{created['id']}",
        json={"end_date": "2027-06-30"},
        headers=auth_headers(agent),
    )
    assert response.status_code == 200
    assert response.json()["end_date"] == "2027-06-30"


def test_reactivation_en_chevauchement_refusee(client, agent, auth_headers, sample_property):
    termine = client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, status="termine"),
        headers=auth_headers(agent),
    ).json()
    client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, tenant_name="Occupant actuel"),
        headers=auth_headers(agent),
    )

    response = client.patch(
        f"/api/v1/leases/{termine['id']}",
        json={"status": "actif"},
        headers=auth_headers(agent),
    )
    assert response.status_code == 409


# --- Regle 2 : le statut du bien suit celui du bail ------------------------


def test_bail_actif_passe_le_bien_en_loue(client, agent, auth_headers, sample_property, db):
    assert sample_property.status == "disponible"

    client.post("/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent))

    db.expire_all()
    assert db.get(Property, sample_property.id).status == "loue"


def test_bail_non_actif_ne_change_pas_le_statut(
    client, agent, auth_headers, sample_property, db
):
    client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, status="termine"),
        headers=auth_headers(agent),
    )

    db.expire_all()
    assert db.get(Property, sample_property.id).status == "disponible"


@pytest.mark.parametrize("statut_final", ["termine", "resilie"])
def test_cloture_du_bail_libere_le_bien(
    client, agent, auth_headers, sample_property, db, statut_final
):
    created = client.post(
        "/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent)
    ).json()

    client.patch(
        f"/api/v1/leases/{created['id']}",
        json={"status": statut_final},
        headers=auth_headers(agent),
    )

    db.expire_all()
    assert db.get(Property, sample_property.id).status == "disponible"


def test_un_bien_en_travaux_garde_son_statut(client, agent, auth_headers, db):
    """Le statut pose a la main par l'agent prime sur la fin du bail."""
    prop = Property(
        title="Local en renovation",
        type="commerce",
        address="Boulevard principal",
        city="Abidjan",
        rent_amount=250000,
        status="disponible",
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)

    created = client.post(
        "/api/v1/leases", json=bail(prop.id), headers=auth_headers(agent)
    ).json()

    # L'agent met le bien en travaux pendant le bail.
    client.patch(
        f"/api/v1/properties/{prop.id}",
        json={"status": "en_travaux"},
        headers=auth_headers(agent),
    )
    client.patch(
        f"/api/v1/leases/{created['id']}",
        json={"status": "termine"},
        headers=auth_headers(agent),
    )

    db.expire_all()
    assert db.get(Property, prop.id).status == "en_travaux"


def test_le_bien_reste_loue_s_il_a_un_autre_bail_actif(
    client, agent, auth_headers, sample_property, db
):
    premier = client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, start_date="2026-01-01", end_date="2026-06-30"),
        headers=auth_headers(agent),
    ).json()
    client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, tenant_name="Suivant", start_date="2026-07-01",
                  end_date="2027-06-30"),
        headers=auth_headers(agent),
    )

    client.patch(
        f"/api/v1/leases/{premier['id']}",
        json={"status": "termine"},
        headers=auth_headers(agent),
    )

    db.expire_all()
    assert db.get(Property, sample_property.id).status == "loue"


def test_suppression_d_un_bail_actif_libere_le_bien(
    client, admin, auth_headers, sample_property, db
):
    created = client.post(
        "/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(admin)
    ).json()
    lease_id = uuid.UUID(created["id"])

    response = client.delete(f"/api/v1/leases/{lease_id}", headers=auth_headers(admin))

    assert response.status_code == 204
    db.expire_all()
    assert db.get(Lease, lease_id) is None
    assert db.get(Property, sample_property.id).status == "disponible"


# --- RBAC -----------------------------------------------------------------


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 201), (UserRole.AGENT, 201), (UserRole.COMPTABLE, 403)],
)
def test_creation_par_role(client, make_user, auth_headers, sample_property, role, expected_status):
    user = make_user(role)
    response = client.post(
        "/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(user)
    )
    assert response.status_code == expected_status


@pytest.mark.parametrize("role", [UserRole.ADMIN, UserRole.AGENT, UserRole.COMPTABLE])
def test_tous_les_roles_consultent(client, make_user, auth_headers, sample_property, role):
    user = make_user(role)
    assert client.get("/api/v1/leases", headers=auth_headers(user)).status_code == 200


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 200), (UserRole.AGENT, 200), (UserRole.COMPTABLE, 403)],
)
def test_modification_par_role(
    client, make_user, auth_headers, sample_property, agent, role, expected_status
):
    created = client.post(
        "/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent)
    ).json()

    user = make_user(role)
    response = client.patch(
        f"/api/v1/leases/{created['id']}",
        json={"tenant_contact": "+225 00 00 00 00 00"},
        headers=auth_headers(user),
    )
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 204), (UserRole.AGENT, 403), (UserRole.COMPTABLE, 403)],
)
def test_suppression_reservee_a_admin(
    client, make_user, auth_headers, sample_property, agent, role, expected_status
):
    created = client.post(
        "/api/v1/leases", json=bail(sample_property.id), headers=auth_headers(agent)
    ).json()

    user = make_user(role)
    response = client.delete(f"/api/v1/leases/{created['id']}", headers=auth_headers(user))
    assert response.status_code == expected_status


def test_bail_inconnu_renvoie_404(client, agent, auth_headers):
    response = client.get(f"/api/v1/leases/{uuid.uuid4()}", headers=auth_headers(agent))
    assert response.status_code == 404


def test_sans_jeton_renvoie_401(client, sample_property):
    assert client.get("/api/v1/leases").status_code == 401
    assert client.post("/api/v1/leases", json=bail(sample_property.id)).status_code == 401


def test_date_du_jour_non_requise(client, agent, auth_headers, sample_property):
    """Un bail peut demarrer dans le futur, l'agence signe souvent en avance."""
    futur = date.today().replace(year=date.today().year + 1).isoformat()
    response = client.post(
        "/api/v1/leases",
        json=bail(sample_property.id, start_date=futur, end_date=None),
        headers=auth_headers(agent),
    )
    assert response.status_code == 201
