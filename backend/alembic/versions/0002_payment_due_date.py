"""Distingue le loyer du au loyer encaisse.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-13

Le schema initial rendait `paid_at` obligatoire, ce qui contredisait les
statuts `en_attente` et `en_retard` : un loyer attendu n'a pas encore de date
d'encaissement. On ajoute donc `due_date`, la date d'echeance, obligatoire, et
`paid_at` ne porte plus que l'encaissement effectif.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PAID_REQUIRES_DATE = "payments_paid_at_required_check"


def upgrade() -> None:
    # Ajoutee nullable puis remplie, pour ne pas casser d'eventuelles lignes
    # existantes, avant d'etre passee en NOT NULL.
    op.add_column("payments", sa.Column("due_date", sa.Date(), nullable=True))
    op.execute("UPDATE payments SET due_date = period_start WHERE due_date IS NULL")
    op.alter_column("payments", "due_date", nullable=False)

    op.alter_column("payments", "paid_at", existing_type=sa.Date(), nullable=True)

    # Un paiement declare paye doit porter sa date d'encaissement.
    op.create_check_constraint(
        PAID_REQUIRES_DATE,
        "payments",
        "status <> 'paye' OR paid_at IS NOT NULL",
    )

    op.create_index("idx_payments_due_date", "payments", ["due_date"])


def downgrade() -> None:
    op.drop_index("idx_payments_due_date", table_name="payments")
    op.drop_constraint(PAID_REQUIRES_DATE, "payments", type_="check")

    # paid_at redevient obligatoire : on retombe sur l'echeance pour les
    # paiements qui n'ont pas encore ete encaisses.
    op.execute("UPDATE payments SET paid_at = due_date WHERE paid_at IS NULL")
    op.alter_column("payments", "paid_at", existing_type=sa.Date(), nullable=False)

    op.drop_column("payments", "due_date")
