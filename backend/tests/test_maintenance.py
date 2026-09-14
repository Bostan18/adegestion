"""Tests du module Maintenance : tickets, prestataires, couts et photos."""

import uuid

import pytest

from app.models.contractor import Contractor
from app.models.enums import UserRole
from app.models.maintenance_ticket import MaintenancePhoto, MaintenanceTicket


@pytest.fixture
def agent(make_user):
    return make_user(UserRole.AGENT)


@pytest.fixture
def admin(make_user):
    return make_user(UserRole.ADMIN)


@pytest.fixture
def comptable(make_user):
    return make_user(UserRole.COMPTABLE)


def ticket(property_id, **overrides) -> dict:
    payload = {
        "property_id": str(property_id),
        "title": "Fuite sous l'evier de la cuisine",
        "description": "Le locataire signale une fuite continue.",
        "priority": "haute",
        "status": "ouvert",
    }
    payload.update(overrides)
    return payload


# --- Prestataires ----------------------------------------------------------


def test_creation_de_prestataire(client, agent, auth_headers):
    response = client.post(
        "/api/v1/contractors",
        json={"name": "Elec Abidjan", "trade": "Electricien", "contact": "+225 01 02 03 04 05"},
        headers=auth_headers(agent),
    )
    assert response.status_code == 201
    assert response.json()["is_active"] is True


def test_recherche_de_prestataire(client, agent, auth_headers, sample_contractor):
    client.post(
        "/api/v1/contractors",
        json={"name": "Elec Abidjan", "trade": "Electricien"},
        headers=auth_headers(agent),
    )

    par_metier = client.get(
        "/api/v1/contractors?q=plomb", headers=auth_headers(agent)
    ).json()
    assert par_metier["total"] == 1
    assert par_metier["items"][0]["name"] == "Plomberie Lagune"


def test_filtre_prestataires_actifs(client, agent, auth_headers, sample_contractor):
    client.patch(
        f"/api/v1/contractors/{sample_contractor.id}",
        json={"is_active": False},
        headers=auth_headers(agent),
    )
    actifs = client.get("/api/v1/contractors?is_active=true", headers=auth_headers(agent)).json()
    assert actifs["total"] == 0


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 201), (UserRole.AGENT, 201), (UserRole.COMPTABLE, 403)],
)
def test_creation_de_prestataire_par_role(client, make_user, auth_headers, role, expected_status):
    user = make_user(role)
    response = client.post(
        "/api/v1/contractors", json={"name": "Test SARL"}, headers=auth_headers(user)
    )
    assert response.status_code == expected_status


def test_suppression_de_prestataire_rattache_refusee(
    client, admin, auth_headers, sample_property, sample_contractor
):
    """L'historique d'intervention a de la valeur, on desactive plutot."""
    client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, contractor_id=str(sample_contractor.id)),
        headers=auth_headers(admin),
    )

    response = client.delete(
        f"/api/v1/contractors/{sample_contractor.id}", headers=auth_headers(admin)
    )

    assert response.status_code == 409
    assert "Desactivez-le" in response.json()["detail"]


def test_suppression_de_prestataire_libre_acceptee(
    client, admin, auth_headers, sample_contractor, db
):
    contractor_id = sample_contractor.id

    response = client.delete(
        f"/api/v1/contractors/{contractor_id}", headers=auth_headers(admin)
    )

    assert response.status_code == 204
    db.expire_all()
    assert db.get(Contractor, contractor_id) is None


def test_suppression_de_prestataire_reservee_a_admin(
    client, agent, auth_headers, sample_contractor
):
    response = client.delete(
        f"/api/v1/contractors/{sample_contractor.id}", headers=auth_headers(agent)
    )
    assert response.status_code == 403


# --- Tickets ---------------------------------------------------------------


def test_creation_puis_lecture(client, agent, auth_headers, sample_property):
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    )
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "Fuite sous l'evier de la cuisine"
    assert body["property"]["title"] == "Villa Cocody Angre"
    assert body["is_open"] is True
    assert body["resolved_at"] is None
    # Le declarant vient du jeton, pas du client.
    assert body["reporter"]["full_name"] == agent.full_name
    assert body["reported_by"] == str(agent.id)

    fetched = client.get(f"/api/v1/maintenance/{body['id']}", headers=auth_headers(agent))
    assert fetched.status_code == 200


def test_declarant_non_falsifiable(client, agent, admin, auth_headers, sample_property):
    """Un reported_by transmis par le client est ignore."""
    payload = ticket(sample_property.id, reported_by=str(admin.id))
    body = client.post(
        "/api/v1/maintenance", json=payload, headers=auth_headers(agent)
    ).json()
    assert body["reported_by"] == str(agent.id)


def test_bien_inconnu_renvoie_404(client, agent, auth_headers):
    response = client.post(
        "/api/v1/maintenance", json=ticket(uuid.uuid4()), headers=auth_headers(agent)
    )
    assert response.status_code == 404


def test_prestataire_inconnu_renvoie_404(client, agent, auth_headers, sample_property):
    response = client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, contractor_id=str(uuid.uuid4())),
        headers=auth_headers(agent),
    )
    assert response.status_code == 404


def test_priorite_invalide_renvoie_422(client, agent, auth_headers, sample_property):
    response = client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, priority="critique"),
        headers=auth_headers(agent),
    )
    assert response.status_code == 422


def test_mise_a_jour_partielle(client, agent, auth_headers, sample_property):
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    ).json()

    response = client.patch(
        f"/api/v1/maintenance/{created['id']}",
        json={"status": "en_cours", "priority": "urgente"},
        headers=auth_headers(agent),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "en_cours"
    assert body["priority"] == "urgente"
    assert body["title"] == "Fuite sous l'evier de la cuisine"


def test_filtres_et_recherche(client, agent, auth_headers, sample_property, sample_contractor):
    client.post("/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent))
    client.post(
        "/api/v1/maintenance",
        json=ticket(
            sample_property.id, title="Volet roulant bloque", priority="basse",
            status="resolu", contractor_id=str(sample_contractor.id),
        ),
        headers=auth_headers(agent),
    )

    tous = client.get("/api/v1/maintenance", headers=auth_headers(agent)).json()
    assert tous["total"] == 2

    ouverts = client.get("/api/v1/maintenance?open_only=true", headers=auth_headers(agent)).json()
    assert ouverts["total"] == 1
    assert ouverts["items"][0]["title"] == "Fuite sous l'evier de la cuisine"

    par_priorite = client.get(
        "/api/v1/maintenance?priority=basse", headers=auth_headers(agent)
    ).json()
    assert par_priorite["total"] == 1

    par_prestataire = client.get(
        f"/api/v1/maintenance?contractor_id={sample_contractor.id}", headers=auth_headers(agent)
    ).json()
    assert par_prestataire["total"] == 1

    recherche = client.get(
        "/api/v1/maintenance?q=volet", headers=auth_headers(agent)
    ).json()
    assert recherche["total"] == 1


def test_les_tickets_a_traiter_remontent_en_premier(
    client, agent, auth_headers, sample_property
):
    client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, title="Deja resolu", status="resolu"),
        headers=auth_headers(agent),
    )
    client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, title="Encore ouvert"),
        headers=auth_headers(agent),
    )

    items = client.get("/api/v1/maintenance", headers=auth_headers(agent)).json()["items"]
    assert items[0]["title"] == "Encore ouvert"


def test_la_liste_n_embarque_pas_les_photos(client, agent, auth_headers, sample_property):
    client.post("/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent))
    item = client.get("/api/v1/maintenance", headers=auth_headers(agent)).json()["items"][0]
    assert "photos" not in item


# --- Date de resolution ----------------------------------------------------


@pytest.mark.parametrize("statut", ["resolu", "ferme"])
def test_la_resolution_horodate_le_ticket(client, agent, auth_headers, sample_property, statut):
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    ).json()
    assert created["resolved_at"] is None

    response = client.patch(
        f"/api/v1/maintenance/{created['id']}",
        json={"status": statut},
        headers=auth_headers(agent),
    )

    assert response.json()["resolved_at"] is not None
    assert response.json()["is_open"] is False


def test_la_reouverture_efface_la_date_de_resolution(
    client, agent, auth_headers, sample_property
):
    """Sans cela, un ticket rouvert garderait une date de resolution mensongere."""
    created = client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, status="resolu"),
        headers=auth_headers(agent),
    ).json()
    assert created["resolved_at"] is not None

    response = client.patch(
        f"/api/v1/maintenance/{created['id']}",
        json={"status": "en_cours"},
        headers=auth_headers(agent),
    )

    assert response.json()["resolved_at"] is None
    assert response.json()["is_open"] is True


# --- Couts -----------------------------------------------------------------


def test_cout_reel_refuse_sur_un_ticket_ouvert(client, agent, auth_headers, sample_property):
    response = client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, status="ouvert", actual_cost="75000"),
        headers=auth_headers(agent),
    )
    assert response.status_code == 422
    assert "cout reel" in response.json()["detail"]


def test_cout_estime_accepte_sur_un_ticket_ouvert(client, agent, auth_headers, sample_property):
    response = client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, estimated_cost="60000"),
        headers=auth_headers(agent),
    )
    assert response.status_code == 201
    assert response.json()["estimated_cost"] == "60000"
    assert response.json()["cost_overrun"] is None


def test_ecart_entre_devis_et_facture(client, agent, auth_headers, sample_property):
    created = client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, estimated_cost="60000"),
        headers=auth_headers(agent),
    ).json()

    response = client.patch(
        f"/api/v1/maintenance/{created['id']}",
        json={"status": "resolu", "actual_cost": "75000", "billed_to_owner": True},
        headers=auth_headers(agent),
    )

    body = response.json()
    assert body["actual_cost"] == "75000"
    assert body["cost_overrun"] == "15000"
    assert body["billed_to_owner"] is True


def test_facture_moins_chere_que_le_devis(client, agent, auth_headers, sample_property):
    created = client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, estimated_cost="60000"),
        headers=auth_headers(agent),
    ).json()

    body = client.patch(
        f"/api/v1/maintenance/{created['id']}",
        json={"status": "resolu", "actual_cost": "50000"},
        headers=auth_headers(agent),
    ).json()

    assert body["cost_overrun"] == "-10000"


def test_reouverture_d_un_ticket_avec_cout_reel(client, agent, auth_headers, sample_property):
    """Regression : la regle de saisie bloquait toute reouverture d'un ticket
    deja facture, avec un message qui ne decrivait pas l'action de l'agent."""
    created = client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, status="resolu", actual_cost="75000"),
        headers=auth_headers(agent),
    ).json()
    assert created["resolved_at"] is not None

    response = client.patch(
        f"/api/v1/maintenance/{created['id']}",
        json={"status": "en_cours"},
        headers=auth_headers(agent),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "en_cours"
    assert body["resolved_at"] is None
    # Le cout deja engage reste, l'argent a bien ete depense.
    assert body["actual_cost"] == "75000"


def test_saisie_d_un_cout_reel_sur_ticket_rouvert_refusee(
    client, agent, auth_headers, sample_property
):
    """La regle tient toujours quand on tente d'ajouter un montant."""
    created = client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, status="en_cours"),
        headers=auth_headers(agent),
    ).json()

    response = client.patch(
        f"/api/v1/maintenance/{created['id']}",
        json={"actual_cost": "50000"},
        headers=auth_headers(agent),
    )
    assert response.status_code == 422


def test_cout_negatif_refuse(client, agent, auth_headers, sample_property):
    response = client.post(
        "/api/v1/maintenance",
        json=ticket(sample_property.id, estimated_cost="-1000"),
        headers=auth_headers(agent),
    )
    assert response.status_code == 422


# --- Photos ----------------------------------------------------------------


@pytest.mark.parametrize("kind", ["avant", "apres"])
def test_ticket_d_upload_puis_enregistrement(
    client, agent, auth_headers, sample_property, kind
):
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    ).json()

    ticket_upload = client.post(
        f"/api/v1/maintenance/{created['id']}/photos/upload-url?kind={kind}",
        json={"filename": "fuite.jpg", "content_type": "image/jpeg"},
        headers=auth_headers(agent),
    )
    assert ticket_upload.status_code == 200
    data = ticket_upload.json()
    assert data["storage_path"].startswith(f"tickets/{created['id']}/{kind}/")

    registered = client.post(
        f"/api/v1/maintenance/{created['id']}/photos",
        json={"storage_path": data["storage_path"], "kind": kind},
        headers=auth_headers(agent),
    )
    assert registered.status_code == 201
    assert registered.json()["kind"] == kind
    assert registered.json()["url"].startswith("https://")


def test_photos_avant_et_apres_sur_un_meme_ticket(
    client, agent, auth_headers, sample_property
):
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    ).json()

    for kind in ("avant", "apres"):
        client.post(
            f"/api/v1/maintenance/{created['id']}/photos",
            json={"storage_path": f"tickets/{created['id']}/{kind}/photo.webp", "kind": kind},
            headers=auth_headers(agent),
        )

    photos = client.get(
        f"/api/v1/maintenance/{created['id']}", headers=auth_headers(agent)
    ).json()["photos"]
    assert sorted(photo["kind"] for photo in photos) == ["apres", "avant"]


def test_chemin_etranger_refuse(client, agent, auth_headers, sample_property):
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    ).json()

    response = client.post(
        f"/api/v1/maintenance/{created['id']}/photos",
        json={"storage_path": f"tickets/{uuid.uuid4()}/avant/vole.webp"},
        headers=auth_headers(agent),
    )
    assert response.status_code == 400


def test_type_de_photo_invalide_refuse(client, agent, auth_headers, sample_property):
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    ).json()

    response = client.post(
        f"/api/v1/maintenance/{created['id']}/photos",
        json={"storage_path": f"tickets/{created['id']}/avant/p.webp", "kind": "pendant"},
        headers=auth_headers(agent),
    )
    assert response.status_code == 422


def test_suppression_de_photo(client, agent, auth_headers, sample_property, storage, db):
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    ).json()
    photo = client.post(
        f"/api/v1/maintenance/{created['id']}/photos",
        json={"storage_path": f"tickets/{created['id']}/avant/p.webp"},
        headers=auth_headers(agent),
    ).json()

    response = client.delete(
        f"/api/v1/maintenance/{created['id']}/photos/{photo['id']}",
        headers=auth_headers(agent),
    )

    assert response.status_code == 204
    db.expire_all()
    assert db.get(MaintenancePhoto, uuid.UUID(photo["id"])) is None
    assert photo["storage_path"] in storage.deleted


def test_suppression_du_ticket_emporte_les_photos(
    client, admin, auth_headers, sample_property, storage, db
):
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(admin)
    ).json()
    photo = client.post(
        f"/api/v1/maintenance/{created['id']}/photos",
        json={"storage_path": f"tickets/{created['id']}/avant/p.webp"},
        headers=auth_headers(admin),
    ).json()

    response = client.delete(f"/api/v1/maintenance/{created['id']}", headers=auth_headers(admin))

    assert response.status_code == 204
    db.expire_all()
    assert db.get(MaintenanceTicket, uuid.UUID(created["id"])) is None
    assert db.get(MaintenancePhoto, uuid.UUID(photo["id"])) is None
    assert photo["storage_path"] in storage.deleted


# --- RBAC ------------------------------------------------------------------


@pytest.mark.parametrize("role", [UserRole.ADMIN, UserRole.AGENT, UserRole.COMPTABLE])
def test_les_trois_roles_declarent_un_ticket(
    client, make_user, auth_headers, sample_property, role
):
    """Un locataire qui appelle peut tomber sur n'importe qui dans l'agence."""
    user = make_user(role)
    response = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(user)
    )
    assert response.status_code == 201


@pytest.mark.parametrize("role", [UserRole.ADMIN, UserRole.AGENT, UserRole.COMPTABLE])
def test_les_trois_roles_consultent(client, make_user, auth_headers, role):
    user = make_user(role)
    assert client.get("/api/v1/maintenance", headers=auth_headers(user)).status_code == 200
    assert client.get("/api/v1/contractors", headers=auth_headers(user)).status_code == 200


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 200), (UserRole.AGENT, 200), (UserRole.COMPTABLE, 403)],
)
def test_traitement_refuse_au_comptable(
    client, make_user, auth_headers, sample_property, agent, role, expected_status
):
    """Declarer n'est pas traiter."""
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    ).json()

    user = make_user(role)
    response = client.patch(
        f"/api/v1/maintenance/{created['id']}",
        json={"status": "en_cours"},
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
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    ).json()

    user = make_user(role)
    response = client.delete(
        f"/api/v1/maintenance/{created['id']}", headers=auth_headers(user)
    )
    assert response.status_code == expected_status


def test_upload_de_photo_refuse_au_comptable(
    client, agent, comptable, auth_headers, sample_property
):
    created = client.post(
        "/api/v1/maintenance", json=ticket(sample_property.id), headers=auth_headers(agent)
    ).json()

    response = client.post(
        f"/api/v1/maintenance/{created['id']}/photos/upload-url",
        json={"filename": "p.webp"},
        headers=auth_headers(comptable),
    )
    assert response.status_code == 403


def test_ticket_inconnu_renvoie_404(client, agent, auth_headers):
    response = client.get(f"/api/v1/maintenance/{uuid.uuid4()}", headers=auth_headers(agent))
    assert response.status_code == 404


def test_sans_jeton_renvoie_401(client):
    assert client.get("/api/v1/maintenance").status_code == 401
    assert client.get("/api/v1/contractors").status_code == 401
