"""create post table

Revision ID: 1aa6dba81087
Revises: 
Create Date: 2023-07-19 17:33:57.177041

"""
from alembic import op
import sqlalchemy as sa
from typing import cast
import uuid

# revision identifiers, used by Alembic.
revision = "1aa6dba81087"
down_revision = None
branch_labels = None
depends_on = None


PostgreSQLUUID = cast(
    "sa.types.TypeEngine[uuid.UUID]",
    sa.dialects.postgresql.UUID(as_uuid=True),
)


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column(
            "id", PostgreSQLUUID, default=uuid.uuid4, nullable=False, primary_key=True
        ),
        sa.Column("title", sa.String(60), nullable=False),
        sa.Column("content", sa.String(255), nullable=False),
        sa.Column("published", sa.Boolean, nullable=False, server_default="FALSE"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("posts")
