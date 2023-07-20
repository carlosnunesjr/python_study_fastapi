"""create users table

Revision ID: 71068db7bf0f
Revises: f497b7de7ecc
Create Date: 2023-07-20 15:14:40.109023

"""
from alembic import op
import sqlalchemy as sa

from typing import cast
import uuid


# revision identifiers, used by Alembic.
revision = "71068db7bf0f"
down_revision = "1aa6dba81087"
branch_labels = None
depends_on = None


PostgreSQLUUID = cast(
    "sa.types.TypeEngine[uuid.UUID]",
    sa.dialects.postgresql.UUID(as_uuid=True),
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id", PostgreSQLUUID, default=uuid.uuid4, nullable=False, primary_key=True
        ),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password", sa.String, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("users")
