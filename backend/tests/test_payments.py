"""Tests du module Paiements : CRUD, RBAC strict, coherence, quittance, export."""

import uuid
from datetime import date, timedelta

import pytest

from app.models.enums import UserRole


@pytest.fixture
def comptable(make_user):
    return make_user(UserRole.COMPTABLE)


@pytest.fixture
def admin(make_user):
    return make_user(UserRole.ADMIN)


def paiement(lease_id, **overrides) -> dict:
    payload = {
        "lease_id": str(lease_id),
        "amount": "450000",
        "payment_method": "wave",
        "period_start": "2026-01-01",
        "period_end": "2026-01-31",
        "due_date": "2026-01-05",
        "paid_at": "2026-01-04",
        "status": "paye",
    }
    payload.update(overrides)
    return payload


# --- CRUD -----------------------------------------------------------------


def test_creation_puis_lecture(client, comptable, auth_headers, sample_lease):
    created = client.post(
        "/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable)
    )
    assert created.status_code == 201
    body = created.json()
    assert body["amount"] == "450000"
    assert body["payment_method"] == "wave"
    # Le bail et son bien sont resumes dans la reponse.
    assert body["lease"]["tenant_name"] == "Koffi N'Guessan"
    assert body["lease"]["property"]["title"] == "Villa Cocody Angre"
    assert body["is_overdue"] is False

    fetched = client.get(f"/api/v1/payments/{body['id']}", headers=auth_headers(comptable))
    assert fetched.status_code == 200


def test_bail_inconnu_renvoie_404(client, comptable, auth_headers):
    response = client.post(
        "/api/v1/payments", json=paiement(uuid.uuid4()), headers=auth_headers(comptable)
    )
    assert response.status_code == 404


def test_mise_a_jour_partielle(client, comptable, auth_headers, sample_lease):
    created = client.post(
        "/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable)
    ).json()

    response = client.patch(
        f"/api/v1/payments/{created['id']}",
        json={"amount": "460000", "reference_number": "TX-9981"},
        headers=auth_headers(comptable),
    )

    assert response.status_code == 200
    assert response.json()["amount"] == "460000"
    assert response.json()["reference_number"] == "TX-9981"


def test_suppression_reservee_a_admin(client, comptable, admin, auth_headers, sample_lease):
    created = client.post(
        "/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable)
    ).json()

    assert (
        client.delete(f"/api/v1/payments/{created['id']}", headers=auth_headers(comptable))
    ).status_code == 403
    assert (
        client.delete(f"/api/v1/payments/{created['id']}", headers=auth_headers(admin))
    ).status_code == 204


def test_paiement_inconnu_renvoie_404(client, comptable, auth_headers):
    response = client.get(f"/api/v1/payments/{uuid.uuid4()}", headers=auth_headers(comptable))
    assert response.status_code == 404


# --- Coherence des donnees ------------------------------------------------


def test_paye_sans_date_d_encaissement_refuse(client, comptable, auth_headers, sample_lease):
    response = client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, status="paye", paid_at=None),
        headers=auth_headers(comptable),
    )
    assert response.status_code == 422
    assert "date d'encaissement" in response.json()["detail"]


def test_en_attente_avec_date_d_encaissement_refuse(client, comptable, auth_headers, sample_lease):
    response = client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, status="en_attente", paid_at="2026-01-04"),
        headers=auth_headers(comptable),
    )
    assert response.status_code == 422


def test_en_attente_sans_date_accepte(client, comptable, auth_headers, sample_lease):
    """Cas normal d'un loyer attendu : echeance connue, encaissement pas encore fait."""
    response = client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, status="en_attente", paid_at=None),
        headers=auth_headers(comptable),
    )
    assert response.status_code == 201
    assert response.json()["paid_at"] is None


def test_periode_inversee_refusee(client, comptable, auth_headers, sample_lease):
    response = client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, period_start="2026-01-31", period_end="2026-01-01"),
        headers=auth_headers(comptable),
    )
    assert response.status_code == 422


def test_encaissement_avant_la_periode_refuse(client, comptable, auth_headers, sample_lease):
    response = client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, paid_at="2025-12-01"),
        headers=auth_headers(comptable),
    )
    assert response.status_code == 422


def test_cheque_sans_reference_refuse(client, comptable, auth_headers, sample_lease):
    """Sans numero de cheque, un rejet pour provision insuffisante serait
    impossible a rapprocher."""
    response = client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, payment_method="cheque", reference_number=None),
        headers=auth_headers(comptable),
    )
    assert response.status_code == 422
    assert "cheque" in response.json()["detail"].lower()


def test_cheque_avec_reference_accepte(client, comptable, auth_headers, sample_lease):
    response = client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, payment_method="cheque", reference_number="CH-4412"),
        headers=auth_headers(comptable),
    )
    assert response.status_code == 201


def test_cheque_rejete(client, comptable, auth_headers, sample_lease):
    """Cheque sans provision : le statut passe a rejete, la reference reste."""
    created = client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, payment_method="cheque", reference_number="CH-4412"),
        headers=auth_headers(comptable),
    ).json()

    response = client.patch(
        f"/api/v1/payments/{created['id']}",
        json={"status": "rejete"},
        headers=auth_headers(comptable),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejete"
    assert body["reference_number"] == "CH-4412"
    assert body["is_overdue"] is False


def test_mise_a_jour_incoherente_refusee(client, comptable, auth_headers, sample_lease):
    """Vider la date d'encaissement d'un paiement paye doit echouer."""
    created = client.post(
        "/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable)
    ).json()

    response = client.patch(
        f"/api/v1/payments/{created['id']}",
        json={"paid_at": None},
        headers=auth_headers(comptable),
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "methode",
    ["especes", "virement_bancaire", "mobile_money_orange", "mobile_money_mtn",
     "mobile_money_moov", "wave"],
)
def test_tous_les_modes_de_paiement(client, comptable, auth_headers, sample_lease, methode):
    response = client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, payment_method=methode),
        headers=auth_headers(comptable),
    )
    assert response.status_code == 201


# --- Indicateur de retard --------------------------------------------------


def test_retard_calcule_sur_une_echeance_passee(client, comptable, auth_headers, sample_lease):
    hier = (date.today() - timedelta(days=1)).isoformat()
    response = client.post(
        "/api/v1/payments",
        json=paiement(
            sample_lease.id, status="en_attente", paid_at=None,
            period_start=hier, period_end=hier, due_date=hier,
        ),
        headers=auth_headers(comptable),
    )
    assert response.status_code == 201
    assert response.json()["is_overdue"] is True


def test_pas_de_retard_sur_une_echeance_future(client, comptable, auth_headers, sample_lease):
    demain = (date.today() + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/v1/payments",
        json=paiement(
            sample_lease.id, status="en_attente", paid_at=None,
            period_start=demain, period_end=demain, due_date=demain,
        ),
        headers=auth_headers(comptable),
    )
    assert response.json()["is_overdue"] is False


def test_un_paiement_encaisse_n_est_jamais_en_retard(
    client, comptable, auth_headers, sample_lease
):
    response = client.post(
        "/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable)
    )
    assert response.json()["is_overdue"] is False


# --- Filtres, totaux et pagination ----------------------------------------


def test_filtres_et_totaux(client, comptable, auth_headers, sample_lease):
    client.post("/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable))
    client.post(
        "/api/v1/payments",
        json=paiement(
            sample_lease.id, status="en_attente", paid_at=None, amount="450000",
            period_start="2026-02-01", period_end="2026-02-28", due_date="2026-02-05",
            payment_method="especes",
        ),
        headers=auth_headers(comptable),
    )

    tous = client.get("/api/v1/payments", headers=auth_headers(comptable)).json()
    assert tous["total"] == 2
    assert tous["totals"]["encaisse"] == "450000"
    assert tous["totals"]["attendu"] == "450000"

    payes = client.get("/api/v1/payments?status=paye", headers=auth_headers(comptable)).json()
    assert payes["total"] == 1

    par_methode = client.get(
        "/api/v1/payments?method=especes", headers=auth_headers(comptable)
    ).json()
    assert par_methode["total"] == 1

    par_periode = client.get(
        "/api/v1/payments?due_from=2026-02-01&due_to=2026-02-28",
        headers=auth_headers(comptable),
    ).json()
    assert par_periode["total"] == 1

    recherche = client.get(
        "/api/v1/payments?q=koffi", headers=auth_headers(comptable)
    ).json()
    assert recherche["total"] == 2

    vide = client.get("/api/v1/payments?q=inconnu", headers=auth_headers(comptable)).json()
    assert vide["total"] == 0
    assert vide["totals"]["encaisse"] == "0"


def test_filtre_par_bail(client, comptable, auth_headers, sample_lease):
    client.post("/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable))
    response = client.get(
        f"/api/v1/payments?lease_id={sample_lease.id}", headers=auth_headers(comptable)
    ).json()
    assert response["total"] == 1


# --- Quittance PDF ---------------------------------------------------------


def test_quittance_pdf(client, comptable, auth_headers, sample_lease):
    created = client.post(
        "/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable)
    ).json()
    assert created["receipt_generated"] is False

    response = client.post(
        f"/api/v1/payments/{created['id']}/receipt", headers=auth_headers(comptable)
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert "quittance-koffi-n-guessan" in response.headers["content-disposition"]

    relu = client.get(f"/api/v1/payments/{created['id']}", headers=auth_headers(comptable))
    assert relu.json()["receipt_generated"] is True


def test_nom_de_quittance_sans_accent(client, comptable, auth_headers, db, sample_property):
    """Regression : un en-tete Content-Disposition ne transporte pas d'accents."""
    from app.models.lease import Lease

    lease = Lease(
        property_id=sample_property.id,
        tenant_name="Societe Ivoire Conseil",
        start_date=date(2026, 1, 1),
        rent_amount=850000,
        status="actif",
    )
    lease.tenant_name = "Société Ivoire Conseil"
    db.add(lease)
    db.commit()
    db.refresh(lease)

    created = client.post(
        "/api/v1/payments", json=paiement(lease.id), headers=auth_headers(comptable)
    ).json()

    response = client.post(
        f"/api/v1/payments/{created['id']}/receipt", headers=auth_headers(comptable)
    )

    disposition = response.headers["content-disposition"]
    assert "societe-ivoire-conseil" in disposition
    assert disposition.isascii()


def test_pas_de_quittance_sur_un_paiement_non_encaisse(
    client, comptable, auth_headers, sample_lease
):
    created = client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, status="en_attente", paid_at=None),
        headers=auth_headers(comptable),
    ).json()

    response = client.post(
        f"/api/v1/payments/{created['id']}/receipt", headers=auth_headers(comptable)
    )
    assert response.status_code == 422


# --- Export CSV ------------------------------------------------------------


def test_export_csv(client, comptable, auth_headers, sample_lease):
    client.post(
        "/api/v1/payments",
        json=paiement(sample_lease.id, payment_method="cheque", reference_number="CH-4412"),
        headers=auth_headers(comptable),
    )

    response = client.get("/api/v1/payments/export", headers=auth_headers(comptable))

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]

    contenu = response.content.decode("utf-8-sig")
    lignes = contenu.strip().split("\r\n")
    assert lignes[0].startswith("date_encaissement;echeance")
    assert "Koffi N'Guessan" in lignes[1]
    assert "Villa Cocody Angre" in lignes[1]
    assert "CH-4412" in lignes[1]
    assert "Chèque" in lignes[1]


def test_export_csv_montant_sans_zeros_de_fin(client, comptable, auth_headers, sample_lease):
    """Regression : le driver renvoyait 450000.0000000000 dans l'export."""
    client.post("/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable))

    lignes = (
        client.get("/api/v1/payments/export", headers=auth_headers(comptable))
        .content.decode("utf-8-sig")
        .strip()
        .split("\r\n")
    )
    montant = lignes[1].split(";")[6]
    assert montant == "450000"


def test_export_csv_filtre_par_periode(client, comptable, auth_headers, sample_lease):
    client.post("/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable))
    client.post(
        "/api/v1/payments",
        json=paiement(
            sample_lease.id, period_start="2026-03-01", period_end="2026-03-31",
            due_date="2026-03-05", paid_at="2026-03-03",
        ),
        headers=auth_headers(comptable),
    )

    response = client.get(
        "/api/v1/payments/export?due_from=2026-03-01&due_to=2026-03-31",
        headers=auth_headers(comptable),
    )

    lignes = response.content.decode("utf-8-sig").strip().split("\r\n")
    assert len(lignes) == 2  # en-tete plus une ligne
    assert "2026-03-03" in lignes[1]


def test_export_vide_garde_l_en_tete(client, comptable, auth_headers):
    response = client.get("/api/v1/payments/export", headers=auth_headers(comptable))
    assert response.status_code == 200
    assert response.content.decode("utf-8-sig").strip().startswith("date_encaissement")


# --- RBAC ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 200), (UserRole.COMPTABLE, 200), (UserRole.AGENT, 403)],
)
def test_lecture_par_role(client, make_user, auth_headers, role, expected_status):
    """L'agent n'a aucun acces aux paiements, pas meme en lecture."""
    user = make_user(role)
    assert client.get("/api/v1/payments", headers=auth_headers(user)).status_code == expected_status


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.ADMIN, 201), (UserRole.COMPTABLE, 201), (UserRole.AGENT, 403)],
)
def test_creation_par_role(client, make_user, auth_headers, sample_lease, role, expected_status):
    user = make_user(role)
    response = client.post(
        "/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(user)
    )
    assert response.status_code == expected_status


def test_agent_bloque_sur_toutes_les_routes(
    client, make_user, comptable, auth_headers, sample_lease
):
    created = client.post(
        "/api/v1/payments", json=paiement(sample_lease.id), headers=auth_headers(comptable)
    ).json()
    agent = make_user(UserRole.AGENT)
    entetes = auth_headers(agent)

    assert client.get(f"/api/v1/payments/{created['id']}", headers=entetes).status_code == 403
    assert client.get("/api/v1/payments/export", headers=entetes).status_code == 403
    assert client.patch(
        f"/api/v1/payments/{created['id']}", json={"amount": "1"}, headers=entetes
    ).status_code == 403
    assert client.post(
        f"/api/v1/payments/{created['id']}/receipt", headers=entetes
    ).status_code == 403
    assert client.delete(f"/api/v1/payments/{created['id']}", headers=entetes).status_code == 403


def test_sans_jeton_renvoie_401(client):
    assert client.get("/api/v1/payments").status_code == 401
    assert client.get("/api/v1/payments/export").status_code == 401
