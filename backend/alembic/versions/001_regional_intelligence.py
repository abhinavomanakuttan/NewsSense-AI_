"""Add region/state/district/city/locality to Article; region to Source.

Revision ID: 001_regional_intelligence
Revises: (initial migration)
Create Date: 2026-09-08
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "001_regional_intelligence"
down_revision = None  # Replace with actual parent revision ID if applicable
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add regional intelligence columns to articles and sources tables."""

    # ------------------------------------------------------------------ #
    #  articles table                                                      #
    # ------------------------------------------------------------------ #
    # Add region, state, district, city, locality columns
    with op.batch_alter_table("articles") as batch_op:
        batch_op.add_column(
            sa.Column("region", sa.String(20), nullable=True)
        )
        batch_op.add_column(
            sa.Column("state", sa.String(100), nullable=True)
        )
        batch_op.add_column(
            sa.Column("district", sa.String(100), nullable=True)
        )
        batch_op.add_column(
            sa.Column("city", sa.String(100), nullable=True)
        )
        batch_op.add_column(
            sa.Column("locality", sa.String(100), nullable=True)
        )
        # Create indexes for region filtering (the most-queried new columns)
        batch_op.create_index("ix_articles_region", ["region"])
        batch_op.create_index("ix_articles_state", ["state"])
        batch_op.create_index("ix_articles_district", ["district"])

    # ------------------------------------------------------------------ #
    #  sources table                                                       #
    # ------------------------------------------------------------------ #
    with op.batch_alter_table("sources") as batch_op:
        batch_op.add_column(
            sa.Column("region", sa.String(20), nullable=True)
        )
        batch_op.create_index("ix_sources_region", ["region"])


def downgrade() -> None:
    """Remove regional intelligence columns."""

    with op.batch_alter_table("sources") as batch_op:
        batch_op.drop_index("ix_sources_region")
        batch_op.drop_column("region")

    with op.batch_alter_table("articles") as batch_op:
        batch_op.drop_index("ix_articles_district")
        batch_op.drop_index("ix_articles_state")
        batch_op.drop_index("ix_articles_region")
        batch_op.drop_column("locality")
        batch_op.drop_column("city")
        batch_op.drop_column("district")
        batch_op.drop_column("state")
        batch_op.drop_column("region")
