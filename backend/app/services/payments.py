"""Regles metier des paiements.

Les paiements sont saisis a la main par le comptable, il n'y a pas de
generation automatique d'echeances. Les regles ci-dessous garantissent que la
ligne enregistree reste coherente et exploitable pour le rapprochement
bancaire :

- la periode reglee doit etre valide ;
- un paiement declare paye porte forcement sa date d'encaissement, et un
  paiement non abouti n'en porte pas ;
- un cheque trace toujours son numero, sans quoi un rejet pour provision
  insuffisante serait impossible a rapprocher.
"""

import unicodedata
import uuid
from datetime import date

from fastapi import HTTPException
from fastapi import status as http_status

from app.models.enums import PaymentMethod, PaymentStatus

# Modes de paiement dont la reference est indispensable au rapprochement.
REFERENCE_REQUIRED_METHODS = {PaymentMethod.CHEQUE}


def validate_payment(
    *,
    period_start: date,
    period_end: date,
    due_date: date,
    paid_at: date | None,
    payment_method: str,
    payment_status: str,
    reference_number: str | None,
) -> None:
    """Controle la coherence d'un paiement, en 422 si quelque chose cloche."""
    if period_end < period_start:
        _reject("La fin de periode ne peut pas preceder son debut.")

    if not (period_start <= due_date <= _plus_one_year(period_end)):
        _reject("L'echeance doit se situer dans la periode reglee ou juste apres.")

    is_settled = payment_status == str(PaymentStatus.PAYE)
    if is_settled and paid_at is None:
        _reject("Un paiement marque paye doit porter sa date d'encaissement.")

    if payment_status == str(PaymentStatus.EN_ATTENTE) and paid_at is not None:
        _reject(
            "Un paiement en attente ne peut pas porter de date d'encaissement. "
            "Passez-le a paye, ou videz la date."
        )

    if paid_at is not None and paid_at < period_start:
        _reject("La date d'encaissement ne peut pas preceder la periode reglee.")

    if payment_method in {str(method) for method in REFERENCE_REQUIRED_METHODS} and (
        not reference_number
    ):
        _reject(
            "Un paiement par cheque doit porter son numero de cheque, "
            "sans quoi un rejet ne serait pas rapprochable."
        )


def _plus_one_year(value: date) -> date:
    """Marge haute laissee a l'echeance, pour les loyers payes d'avance."""
    try:
        return value.replace(year=value.year + 1)
    except ValueError:
        # 29 fevrier d'une annee bissextile.
        return value.replace(year=value.year + 1, day=28)


def _reject(message: str) -> None:
    raise HTTPException(
        status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message
    )


def build_receipt_filename(payment_id: uuid.UUID, tenant_name: str) -> str:
    """Nom de fichier lisible, et strictement ASCII.

    L'en-tete Content-Disposition simple ne transporte pas les accents : sans
    ce repliage, "Societe Ivoire Conseil" ressort mutile cote navigateur.
    """
    sans_accent = (
        unicodedata.normalize("NFKD", tenant_name)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    slug = "".join(char if char.isalnum() else "-" for char in sans_accent.lower())
    slug = "-".join(part for part in slug.split("-") if part)[:40].strip("-")
    return f"quittance-{slug or 'locataire'}-{str(payment_id)[:8]}.pdf"
