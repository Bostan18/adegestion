"""Schema initial AdeImmo (docs/schema.sql).

Revision ID: 0001
Revises:
Create Date: 2026-09-11

La table `users` reprend l'identifiant de Supabase Auth. Quand le schema `auth`
existe (projet Supabase), on ajoute la cle etrangere vers auth.users ; sur un
Postgres local de developpement, la colonne reste un simple UUID.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")
NEW_UUID = sa.text("gen_random_uuid()")


def _supabase_auth_available() -> bool:
    """Vrai si la table auth.users de Supabase est presente."""
    if op.get_context().as_sql:
        # Rendu hors ligne (alembic upgrade --sql) : aucune introspection
        # possible, la cle etrangere vers auth.users est alors a ajouter a part.
        return False
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return False
    return bool(
        bind.scalar(
            sa.text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'auth' AND table_name = 'users'"
            )
        )
    )


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID, primary_key=True, server_default=NEW_UUID),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.CheckConstraint("role IN ('admin', 'agent', 'comptable')", name="users_role_check"),
    )

    if _supabase_auth_available():
        op.create_foreign_key(
            "users_id_fkey",
            "users",
            "users",
            ["id"],
            ["id"],
            source_schema="public",
            referent_schema="auth",
            ondelete="CASCADE",
        )

    op.create_table(
        "properties",
        sa.Column("id", UUID, primary_key=True, server_default=NEW_UUID),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("city", sa.Text(), nullable=False),
        sa.Column("surface_m2", sa.Numeric(), nullable=True),
        sa.Column("rent_amount", sa.Numeric(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("owner_name", sa.Text(), nullable=True),
        sa.Column("owner_contact", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.CheckConstraint(
            "type IN ('appartement', 'villa', 'terrain', 'bureau', 'commerce')",
            name="properties_type_check",
        ),
        sa.CheckConstraint(
            "status IN ('disponible', 'loue', 'en_travaux', 'indisponible')",
            name="properties_status_check",
        ),
    )
    op.create_index("idx_properties_status", "properties", ["status"])
    op.create_index("idx_properties_city", "properties", ["city"])

    op.create_table(
        "property_photos",
        sa.Column("id", UUID, primary_key=True, server_default=NEW_UUID),
        sa.Column("property_id", UUID, nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("is_cover", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            name="property_photos_property_id_fkey",
            ondelete="CASCADE",
        ),
    )
    op.create_index("idx_property_photos_property_id", "property_photos", ["property_id"])

    op.create_table(
        "leases",
        sa.Column("id", UUID, primary_key=True, server_default=NEW_UUID),
        sa.Column("property_id", UUID, nullable=False),
        sa.Column("tenant_name", sa.Text(), nullable=False),
        sa.Column("tenant_contact", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("rent_amount", sa.Numeric(), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["property_id"], ["properties.id"], name="leases_property_id_fkey"
        ),
        sa.CheckConstraint(
            "status IN ('actif', 'termine', 'resilie')", name="leases_status_check"
        ),
    )
    op.create_index("idx_leases_property_id", "leases", ["property_id"])

    op.create_table(
        "payments",
        sa.Column("id", UUID, primary_key=True, server_default=NEW_UUID),
        sa.Column("lease_id", UUID, nullable=False),
        sa.Column("amount", sa.Numeric(), nullable=False),
        sa.Column("payment_method", sa.Text(), nullable=False),
        sa.Column("reference_number", sa.Text(), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("paid_at", sa.Date(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "receipt_generated", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(["lease_id"], ["leases.id"], name="payments_lease_id_fkey"),
        sa.CheckConstraint(
            "payment_method IN ('especes', 'virement_bancaire', 'cheque', "
            "'mobile_money_orange', 'mobile_money_mtn', 'mobile_money_moov', 'wave')",
            name="payments_payment_method_check",
        ),
        sa.CheckConstraint(
            "status IN ('paye', 'en_attente', 'en_retard', 'rejete')",
            name="payments_status_check",
        ),
    )
    op.create_index("idx_payments_lease_id", "payments", ["lease_id"])
    op.create_index("idx_payments_status", "payments", ["status"])

    op.create_table(
        "maintenance_tickets",
        sa.Column("id", UUID, primary_key=True, server_default=NEW_UUID),
        sa.Column("property_id", UUID, nullable=False),
        sa.Column("reported_by", UUID, nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["property_id"], ["properties.id"], name="maintenance_tickets_property_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["reported_by"], ["users.id"], name="maintenance_tickets_reported_by_fkey"
        ),
        sa.CheckConstraint(
            "priority IN ('basse', 'moyenne', 'haute', 'urgente')",
            name="maintenance_tickets_priority_check",
        ),
        sa.CheckConstraint(
            "status IN ('ouvert', 'en_cours', 'resolu', 'ferme')",
            name="maintenance_tickets_status_check",
        ),
    )
    op.create_index("idx_maintenance_property_id", "maintenance_tickets", ["property_id"])


def downgrade() -> None:
    op.drop_table("maintenance_tickets")
    op.drop_table("payments")
    op.drop_table("leases")
    op.drop_table("property_photos")
    op.drop_table("properties")
    op.drop_table("users")
