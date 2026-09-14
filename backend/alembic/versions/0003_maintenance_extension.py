"""Etend le module Maintenance : prestataires, couts et photos.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-14

Le schema initial ne portait que le signalement. Une agence a besoin de trois
choses de plus pour exploiter ses tickets : savoir qui est intervenu, combien
cela a coute et si la depense a ete refacturee au proprietaire, et disposer de
photos avant et apres pour justifier l'intervention.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")
NEW_UUID = sa.text("gen_random_uuid()")


def upgrade() -> None:
    # --- Prestataires -----------------------------------------------------
    op.create_table(
        "contractors",
        sa.Column("id", UUID, primary_key=True, server_default=NEW_UUID),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("trade", sa.Text(), nullable=True),
        sa.Column("contact", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("idx_contractors_name", "contractors", ["name"])

    # --- Tickets ----------------------------------------------------------
    op.add_column("maintenance_tickets", sa.Column("contractor_id", UUID, nullable=True))
    op.create_foreign_key(
        "maintenance_tickets_contractor_id_fkey",
        "maintenance_tickets",
        "contractors",
        ["contractor_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "idx_maintenance_contractor_id", "maintenance_tickets", ["contractor_id"]
    )

    op.add_column(
        "maintenance_tickets", sa.Column("estimated_cost", sa.Numeric(), nullable=True)
    )
    op.add_column("maintenance_tickets", sa.Column("actual_cost", sa.Numeric(), nullable=True))
    op.add_column(
        "maintenance_tickets",
        sa.Column(
            "billed_to_owner", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )
    op.create_index("idx_maintenance_status", "maintenance_tickets", ["status"])

    # --- Photos -----------------------------------------------------------
    op.create_table(
        "maintenance_photos",
        sa.Column("id", UUID, primary_key=True, server_default=NEW_UUID),
        sa.Column("ticket_id", UUID, nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        # "avant" documente le probleme, "apres" justifie l'intervention.
        sa.Column("kind", sa.Text(), nullable=False, server_default=sa.text("'avant'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["maintenance_tickets.id"],
            name="maintenance_photos_ticket_id_fkey",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "kind IN ('avant', 'apres')", name="maintenance_photos_kind_check"
        ),
    )
    op.create_index("idx_maintenance_photos_ticket_id", "maintenance_photos", ["ticket_id"])


def downgrade() -> None:
    op.drop_table("maintenance_photos")

    op.drop_index("idx_maintenance_status", table_name="maintenance_tickets")
    op.drop_column("maintenance_tickets", "billed_to_owner")
    op.drop_column("maintenance_tickets", "actual_cost")
    op.drop_column("maintenance_tickets", "estimated_cost")

    op.drop_index("idx_maintenance_contractor_id", table_name="maintenance_tickets")
    op.drop_constraint(
        "maintenance_tickets_contractor_id_fkey", "maintenance_tickets", type_="foreignkey"
    )
    op.drop_column("maintenance_tickets", "contractor_id")

    op.drop_index("idx_contractors_name", table_name="contractors")
    op.drop_table("contractors")
