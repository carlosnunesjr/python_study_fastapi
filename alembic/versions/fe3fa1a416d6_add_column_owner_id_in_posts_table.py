"""add column owner_id in posts table

Revision ID: fe3fa1a416d6
Revises: 71068db7bf0f
Create Date: 2023-07-20 15:22:51.231951

"""
from alembic import op
import sqlalchemy as sa

from typing import cast
import uuid

# revision identifiers, used by Alembic.
revision = "fe3fa1a416d6"
down_revision = "71068db7bf0f"
branch_labels = None
depends_on = None

PostgreSQLUUID = cast(
    "sa.types.TypeEngine[uuid.UUID]",
    sa.dialects.postgresql.UUID(as_uuid=True),
)


def upgrade() -> None:
    op.add_column(
        table_name="posts",
        column=sa.Column(
            "owner_id",
            PostgreSQLUUID,
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "post_users_fk",
        source_table="posts",
        referent_table="users",
        local_cols=["owner_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("post_users_fk", table_name="posts")
    op.drop_column("posts", "owner_id")
