"""Generation des quittances de loyer en PDF et de l'export CSV.

Le PDF est produit a la volee et renvoye au navigateur, sans stockage : une
quittance se regenere a l'identique depuis les donnees du paiement, l'archiver
n'apporterait rien pour l'instant.
"""

import csv
import io
from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from fpdf import FPDF

from app.models.enums import PaymentMethod, PaymentStatus
from app.models.payment import Payment
from app.schemas.common import normalize_amount

AGENCY_NAME = "AdeImmo"

PAYMENT_METHOD_LABELS: dict[str, str] = {
    PaymentMethod.ESPECES: "Espèces",
    PaymentMethod.VIREMENT_BANCAIRE: "Virement bancaire",
    PaymentMethod.CHEQUE: "Chèque",
    PaymentMethod.MOBILE_MONEY_ORANGE: "Orange Money",
    PaymentMethod.MOBILE_MONEY_MTN: "MTN Mobile Money",
    PaymentMethod.MOBILE_MONEY_MOOV: "Moov Money",
    PaymentMethod.WAVE: "Wave",
}

PAYMENT_STATUS_LABELS: dict[str, str] = {
    PaymentStatus.PAYE: "Payé",
    PaymentStatus.EN_ATTENTE: "En attente",
    PaymentStatus.EN_RETARD: "En retard",
    PaymentStatus.REJETE: "Rejeté",
}


def format_amount(value: Decimal | None) -> str:
    """Montant en francs CFA, avec une espace comme separateur de milliers."""
    if value is None:
        return "-"
    entier = int(Decimal(value))
    return f"{entier:,}".replace(",", " ") + " FCFA"


def format_day(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else "-"


def build_receipt_pdf(payment: Payment) -> bytes:
    """Quittance d'une page, imprimable telle quelle."""
    lease = payment.lease
    tenant = lease.tenant_name if lease else "-"
    property_title = lease.property.title if lease and lease.property else "-"
    property_address = (
        f"{lease.property.address}, {lease.property.city}"
        if lease and lease.property
        else "-"
    )

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, AGENCY_NAME, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 12, "Quittance de loyer", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(110, 110, 110)
    pdf.cell(
        0,
        6,
        f"Émise le {format_day(date.today())} · référence {str(payment.id)[:8]}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    rows = [
        ("Locataire", tenant),
        ("Bien", property_title),
        ("Adresse", property_address),
        (
            "Période réglée",
            f"{format_day(payment.period_start)} au {format_day(payment.period_end)}",
        ),
        ("Échéance", format_day(payment.due_date)),
        ("Date d'encaissement", format_day(payment.paid_at)),
        (
            "Mode de paiement",
            PAYMENT_METHOD_LABELS.get(payment.payment_method, payment.payment_method),
        ),
        ("Référence", payment.reference_number or "-"),
        ("Statut", PAYMENT_STATUS_LABELS.get(payment.status, payment.status)),
    ]

    for label, value in rows:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(110, 110, 110)
        pdf.cell(55, 9, label)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 9, str(value), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(8)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(55, 12, "Montant")
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, format_amount(payment.amount), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(110, 110, 110)
    pdf.multi_cell(
        0,
        5,
        "Cette quittance atteste du règlement du loyer pour la période indiquée. "
        "Elle ne vaut pas quittance des périodes antérieures.",
    )

    return bytes(pdf.output())


CSV_HEADERS = [
    "date_encaissement",
    "echeance",
    "periode_debut",
    "periode_fin",
    "locataire",
    "bien",
    "montant",
    "mode_paiement",
    "reference",
    "statut",
    "quittance_generee",
]


def build_payments_csv(payments: Iterable[Payment]) -> str:
    """Export destine au rapprochement bancaire, ouvrable dans un tableur.

    Separateur point-virgule et BOM UTF-8, sans quoi Excel en configuration
    francaise colle toute la ligne dans une seule colonne et casse les accents.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", lineterminator="\r\n")
    writer.writerow(CSV_HEADERS)

    for payment in payments:
        lease = payment.lease
        writer.writerow([
            payment.paid_at.isoformat() if payment.paid_at else "",
            payment.due_date.isoformat(),
            payment.period_start.isoformat(),
            payment.period_end.isoformat(),
            lease.tenant_name if lease else "",
            lease.property.title if lease and lease.property else "",
            # Forme courte, sans les zeros de fin ajoutes par le driver.
            f"{normalize_amount(Decimal(payment.amount)):f}",
            PAYMENT_METHOD_LABELS.get(payment.payment_method, payment.payment_method),
            payment.reference_number or "",
            PAYMENT_STATUS_LABELS.get(payment.status, payment.status),
            "oui" if payment.receipt_generated else "non",
        ])

    return "﻿" + buffer.getvalue()
