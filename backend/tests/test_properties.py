"""Tests du module Biens : CRUD, filtres et photos."""

import uuid

import pytest

from app.models.enums import UserRole
from app.models.property import PropertyPhoto

BIEN_VALIDE = {
    "title": "Bureau Marcory Zone 4",
    "type": "bureau",
    "address": "Rue Pierre et Marie Curie",
    "city": "Abidjan",
    "surface_m2": "95.5",
    "rent_amount": "750000",
    "status": "disponible",
    "owner_name": "SCI Lagune",
    "owner_contact": "+225 27 21 00 00 00",
}


@pytest.fixture
def agent(make_user):
    return make_user(UserRole.AGENT)


@pytest.fixture
def admin(make_user):
    return make_user(UserRole.ADMIN)


def test_creation_puis_lecture_d_un_bien(client, agent, auth_headers):
    created = client.post("/api/v1/properties", json=BIEN_VALIDE, headers=auth_headers(agent))
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "Bureau Marcory Zone 4"
    assert body["photos"] == []

    fetched = client.get(f"/api/v1/properties/{body['id']}", headers=auth_headers(agent))
    assert fetched.status_code == 200
    assert fetched.json()["city"] == "Abidjan"


def test_statut_par_defaut_disponible(client, agent, auth_headers):
    payload = {key: value for key, value in BIEN_VALIDE.items() if key != "status"}
    response = client.post("/api/v1/properties", json=payload, headers=auth_headers(agent))
    assert response.status_code == 201
    assert response.json()["status"] == "disponible"


def test_type_invalide_renvoie_422(client, agent, auth_headers):
    payload = {**BIEN_VALIDE, "type": "chateau"}
    response = client.post("/api/v1/properties", json=payload, headers=auth_headers(agent))
    assert response.status_code == 422


def test_loyer_negatif_renvoie_422(client, agent, auth_headers):
    payload = {**BIEN_VALIDE, "rent_amount": "-1000"}
    response = client.post("/api/v1/properties", json=payload, headers=auth_headers(agent))
    assert response.status_code == 422


def test_bien_inconnu_renvoie_404(client, agent, auth_headers):
    response = client.get(f"/api/v1/properties/{uuid.uuid4()}", headers=auth_headers(agent))
    assert response.status_code == 404


def test_mise_a_jour_partielle(client, agent, auth_headers, sample_property):
    response = client.patch(
        f"/api/v1/properties/{sample_property.id}",
        json={"status": "loue", "rent_amount": "500000"},
        headers=auth_headers(agent),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "loue"
    assert body["rent_amount"] == "500000"
    # Les champs non transmis restent inchanges.
    assert body["title"] == "Villa Cocody Angre"


def test_suppression_par_admin_supprime_aussi_les_photos(
    client, admin, auth_headers, sample_property, sample_photo, storage, db
):
    photo_id, storage_path = sample_photo.id, sample_photo.storage_path

    response = client.delete(
        f"/api/v1/properties/{sample_property.id}", headers=auth_headers(admin)
    )

    assert response.status_code == 204
    db.expire_all()
    assert db.get(PropertyPhoto, photo_id) is None
    assert storage_path in storage.deleted


def test_filtres_et_pagination(client, agent, auth_headers):
    biens = [
        {**BIEN_VALIDE, "title": "Villa Bingerville", "type": "villa", "city": "Bingerville"},
        {**BIEN_VALIDE, "title": "Terrain Bassam", "type": "terrain", "city": "Grand-Bassam"},
        {**BIEN_VALIDE, "title": "Villa Riviera", "type": "villa", "status": "loue"},
    ]
    for bien in biens:
        client.post("/api/v1/properties", json=bien, headers=auth_headers(agent))

    par_type = client.get("/api/v1/properties?type=villa", headers=auth_headers(agent)).json()
    assert par_type["total"] == 2

    par_statut = client.get("/api/v1/properties?status=loue", headers=auth_headers(agent)).json()
    assert par_statut["total"] == 1
    assert par_statut["items"][0]["title"] == "Villa Riviera"

    par_ville = client.get(
        "/api/v1/properties?city=bassam", headers=auth_headers(agent)
    ).json()
    assert par_ville["total"] == 1

    recherche = client.get("/api/v1/properties?q=Riviera", headers=auth_headers(agent)).json()
    assert recherche["total"] == 1

    page = client.get("/api/v1/properties?limit=2&offset=0", headers=auth_headers(agent)).json()
    assert page["total"] == 3
    assert len(page["items"]) == 2
    assert page["limit"] == 2


def test_limite_de_pagination_hors_bornes_renvoie_422(client, agent, auth_headers):
    response = client.get("/api/v1/properties?limit=500", headers=auth_headers(agent))
    assert response.status_code == 422


# --- Photos ---------------------------------------------------------------


def test_ticket_d_upload_puis_enregistrement(client, agent, auth_headers, sample_property):
    ticket = client.post(
        f"/api/v1/properties/{sample_property.id}/photos/upload-url",
        json={"filename": "salon.jpg", "content_type": "image/jpeg"},
        headers=auth_headers(agent),
    )
    assert ticket.status_code == 200
    data = ticket.json()
    assert data["bucket"] == "property-photos"
    assert data["storage_path"].startswith(f"properties/{sample_property.id}/")
    assert data["token"]

    registered = client.post(
        f"/api/v1/properties/{sample_property.id}/photos",
        json={"storage_path": data["storage_path"], "is_cover": True},
        headers=auth_headers(agent),
    )
    assert registered.status_code == 201
    assert registered.json()["is_cover"] is True
    assert registered.json()["url"].startswith("https://")


def test_enregistrement_d_un_chemin_etranger_refuse(client, agent, auth_headers, sample_property):
    """Empeche d'attacher a un bien un fichier appartenant a un autre."""
    response = client.post(
        f"/api/v1/properties/{sample_property.id}/photos",
        json={"storage_path": f"properties/{uuid.uuid4()}/vole.webp"},
        headers=auth_headers(agent),
    )
    assert response.status_code == 400


def test_une_seule_photo_de_couverture(
    client, agent, auth_headers, sample_property, sample_photo, db
):
    seconde = client.post(
        f"/api/v1/properties/{sample_property.id}/photos",
        json={"storage_path": f"properties/{sample_property.id}/photo-2.webp", "is_cover": True},
        headers=auth_headers(agent),
    )
    assert seconde.status_code == 201

    db.expire_all()
    assert db.get(PropertyPhoto, sample_photo.id).is_cover is False
    assert db.get(PropertyPhoto, uuid.UUID(seconde.json()["id"])).is_cover is True


def test_changement_de_photo_de_couverture(
    client, agent, auth_headers, sample_property, sample_photo, db
):
    autre = PropertyPhoto(
        property_id=sample_property.id,
        storage_path=f"properties/{sample_property.id}/photo-3.webp",
        is_cover=False,
    )
    db.add(autre)
    db.commit()
    db.refresh(autre)

    response = client.patch(
        f"/api/v1/properties/{sample_property.id}/photos/{autre.id}/cover",
        headers=auth_headers(agent),
    )

    assert response.status_code == 200
    db.expire_all()
    assert db.get(PropertyPhoto, autre.id).is_cover is True
    assert db.get(PropertyPhoto, sample_photo.id).is_cover is False


def test_suppression_de_photo(
    client, agent, auth_headers, sample_property, sample_photo, storage, db
):
    photo_id, storage_path = sample_photo.id, sample_photo.storage_path

    response = client.delete(
        f"/api/v1/properties/{sample_property.id}/photos/{photo_id}",
        headers=auth_headers(agent),
    )

    assert response.status_code == 204
    db.expire_all()
    assert db.get(PropertyPhoto, photo_id) is None
    assert storage_path in storage.deleted


def test_photo_d_un_autre_bien_renvoie_404(
    client, agent, auth_headers, sample_property, sample_photo, db
):
    from app.models.property import Property

    autre_bien = Property(
        title="Commerce Yopougon",
        type="commerce",
        address="Boulevard principal",
        city="Abidjan",
        rent_amount=200000,
        status="disponible",
    )
    db.add(autre_bien)
    db.commit()
    db.refresh(autre_bien)

    response = client.delete(
        f"/api/v1/properties/{autre_bien.id}/photos/{sample_photo.id}",
        headers=auth_headers(agent),
    )
    assert response.status_code == 404


def test_la_liste_renvoie_l_url_de_couverture(
    client, agent, auth_headers, sample_property, sample_photo
):
    response = client.get("/api/v1/properties", headers=auth_headers(agent))
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["cover_url"] is not None
    assert sample_photo.storage_path in item["cover_url"]
