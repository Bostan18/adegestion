"""Module Paiements : encaissements des loyers, quittances et export.

RBAC volontairement plus strict que les autres modules, conformement a
docs/ARCHITECTURE.md : seuls l'admin et le comptable accedent aux paiements,
l'agent n'y a acces ni en ecriture ni en lecture. La suppression reste reservee
a l'admin.
"""

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies.auth import AccountantUser, require_admin
from app.models.enums import PaymentMethod, PaymentStatus
from app.models.lease import Lease
from app.models.payment import Payment
from app.schemas.payment import (
    PaymentCreate,
    PaymentPage,
    PaymentRead,
    PaymentTotals,
    PaymentUpdate,
)
from app.services.payments import build_receipt_filename, validate_payment
from app.services.receipts import build_payments_csv, build_receipt_pdf

router = APIRouter(prefix="/payments", tags=["paiements"])

DbSession = Annotated[Session, Depends(get_db)]


def _with_lease(statement):
    """Charge le bail et son bien, affiches partout avec le paiement."""
    return statement.options(selectinload(Payment.lease).selectinload(Lease.property))


def _get_payment_or_404(db: Session, payment_id: uuid.UUID) -> Payment:
    payment = db.scalar(_with_lease(select(Payment).where(Payment.id == payment_id)))
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paiement introuvable."
        )
    return payment


def _build_filters(
    lease_id: uuid.UUID | None,
    payment_status: PaymentStatus | None,
    payment_method: PaymentMethod | None,
    due_from: date | None,
    due_to: date | None,
) -> list:
    filters = []
    if lease_id is not None:
        filters.append(Payment.lease_id == lease_id)
    if payment_status is not None:
        filters.append(Payment.status == str(payment_status))
    if payment_method is not None:
        filters.append(Payment.payment_method == str(payment_method))
    if due_from is not None:
        filters.append(Payment.due_date >= due_from)
    if due_to is not None:
        filters.append(Payment.due_date <= due_to)
    return filters


# L'export doit etre declare avant /{payment_id}, sinon "export" serait lu
# comme un identifiant et rejete en 422.
@router.get(
    "/export",
    summary="Exporter les paiements en CSV",
    response_class=Response,
    responses={200: {"content": {"text/csv": {}}}},
)
def export_payments(
    db: DbSession,
    _: AccountantUser,
    lease_id: uuid.UUID | None = None,
    payment_status: Annotated[PaymentStatus | None, Query(alias="status")] = None,
    payment_method: Annotated[PaymentMethod | None, Query(alias="method")] = None,
    due_from: date | None = None,
    due_to: date | None = None,
) -> Response:
    """Export par periode, pour le rapprochement bancaire."""
    filters = _build_filters(lease_id, payment_status, payment_method, due_from, due_to)
    payments = db.scalars(
        _with_lease(select(Payment).where(*filters)).order_by(Payment.due_date)
    ).all()

    periode = f"{due_from or 'debut'}_{due_to or 'fin'}"
    return Response(
        content=build_payments_csv(payments),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="paiements-{periode}.csv"'
        },
    )


@router.get("", response_model=PaymentPage, summary="Lister les paiements")
def list_payments(
    db: DbSession,
    _: AccountantUser,
    lease_id: uuid.UUID | None = None,
    payment_status: Annotated[PaymentStatus | None, Query(alias="status")] = None,
    payment_method: Annotated[PaymentMethod | None, Query(alias="method")] = None,
    due_from: date | None = None,
    due_to: date | None = None,
    q: Annotated[str | None, Query(description="Recherche sur le nom du locataire")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaymentPage:
    filters = _build_filters(lease_id, payment_status, payment_method, due_from, due_to)

    base = select(Payment).where(*filters)
    count_base = select(func.count()).select_from(Payment).where(*filters)
    encaisse_base = select(func.coalesce(func.sum(Payment.amount), 0)).where(
        *filters, Payment.status == str(PaymentStatus.PAYE)
    )
    attendu_base = select(func.coalesce(func.sum(Payment.amount), 0)).where(
        *filters, Payment.status.in_([str(PaymentStatus.EN_ATTENTE), str(PaymentStatus.EN_RETARD)])
    )

    if q:
        pattern = f"%{q.strip()}%"
        base = base.join(Lease).where(Lease.tenant_name.ilike(pattern))
        count_base = count_base.join(Lease).where(Lease.tenant_name.ilike(pattern))
        encaisse_base = encaisse_base.join(Lease).where(Lease.tenant_name.ilike(pattern))
        attendu_base = attendu_base.join(Lease).where(Lease.tenant_name.ilike(pattern))

    total = db.scalar(count_base) or 0
    rows = db.scalars(
        _with_lease(base).order_by(Payment.due_date.desc(), Payment.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    return PaymentPage(
        items=[PaymentRead.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
        totals=PaymentTotals(
            encaisse=db.scalar(encaisse_base) or 0,
            attendu=db.scalar(attendu_base) or 0,
        ),
    )


@router.post(
    "",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Enregistrer un paiement",
)
def create_payment(payload: PaymentCreate, db: DbSession, _: AccountantUser) -> PaymentRead:
    lease = db.get(Lease, payload.lease_id)
    if lease is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bail introuvable.")

    validate_payment(
        period_start=payload.period_start,
        period_end=payload.period_end,
        due_date=payload.due_date,
        paid_at=payload.paid_at,
        payment_method=str(payload.payment_method),
        payment_status=str(payload.status),
        reference_number=payload.reference_number,
    )

    payment = Payment(**payload.model_dump())
    payment.payment_method = str(payload.payment_method)
    payment.status = str(payload.status)
    db.add(payment)
    db.commit()

    return PaymentRead.model_validate(_get_payment_or_404(db, payment.id))


@router.get("/{payment_id}", response_model=PaymentRead, summary="Detail d'un paiement")
def get_payment(payment_id: uuid.UUID, db: DbSession, _: AccountantUser) -> PaymentRead:
    return PaymentRead.model_validate(_get_payment_or_404(db, payment_id))


@router.patch("/{payment_id}", response_model=PaymentRead, summary="Modifier un paiement")
def update_payment(
    payment_id: uuid.UUID,
    payload: PaymentUpdate,
    db: DbSession,
    _: AccountantUser,
) -> PaymentRead:
    payment = _get_payment_or_404(db, payment_id)
    data = payload.model_dump(exclude_unset=True)

    merged = {
        "period_start": data.get("period_start", payment.period_start),
        "period_end": data.get("period_end", payment.period_end),
        "due_date": data.get("due_date", payment.due_date),
        "paid_at": data.get("paid_at", payment.paid_at),
        "payment_method": str(data.get("payment_method", payment.payment_method)),
        "payment_status": str(data.get("status", payment.status)),
        "reference_number": data.get("reference_number", payment.reference_number),
    }
    validate_payment(**merged)

    for field, value in data.items():
        setattr(payment, field, str(value) if field in {"status", "payment_method"} else value)

    db.commit()
    return PaymentRead.model_validate(_get_payment_or_404(db, payment_id))


@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
    summary="Supprimer un paiement",
)
def delete_payment(payment_id: uuid.UUID, db: DbSession) -> Response:
    payment = _get_payment_or_404(db, payment_id)
    db.delete(payment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{payment_id}/receipt",
    summary="Generer la quittance en PDF",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}},
)
def generate_receipt(payment_id: uuid.UUID, db: DbSession, _: AccountantUser) -> Response:
    """Renvoie la quittance et marque le paiement comme quittance.

    Verbe POST plutot que GET : l'appel a un effet de bord, il bascule
    `receipt_generated`. Le navigateur doit de toute facon passer par un appel
    authentifie pour joindre son jeton, un lien simple ne conviendrait pas.
    """
    payment = _get_payment_or_404(db, payment_id)

    if payment.status != str(PaymentStatus.PAYE):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Une quittance ne peut etre emise que pour un paiement encaisse.",
        )

    pdf = build_receipt_pdf(payment)
    payment.receipt_generated = True
    db.commit()

    tenant = payment.lease.tenant_name if payment.lease else "locataire"
    filename = build_receipt_filename(payment_id, tenant)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
