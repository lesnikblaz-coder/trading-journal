"""opened_at and closed_at Trade columns from string to DATETIME

Revision ID: 30c419d5b509
Revises: b1f16d56d3aa
Create Date: 2026-09-09 15:17:08.586354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30c419d5b509'
down_revision: Union[str, Sequence[str], None] = 'b1f16d56d3aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "trades",
        "opened_at",
        existing_type=sa.VARCHAR(length=30),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="opened_at::timestamp with time zone",
    )

    op.alter_column(
        "trades",
        "closed_at",
        existing_type=sa.VARCHAR(length=30),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="closed_at::timestamp with time zone",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "trades",
        "closed_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(length=30),
        existing_nullable=True,
    )

    op.alter_column(
        "trades",
        "opened_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(length=30),
        existing_nullable=True,
    )