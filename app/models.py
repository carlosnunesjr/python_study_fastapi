from sqlalchemy import Column, String, Boolean, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
import sqlalchemy.dialects.postgresql

from typing import cast
from .database import Base

import uuid

PostgreSQLUUID = cast(
    "sqlalchemy.types.TypeEngine[uuid.UUID]",
    sqlalchemy.dialects.postgresql.UUID(as_uuid=True),
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(PostgreSQLUUID, default=uuid.uuid4, primary_key=True, nullable=False)
    title = Column(String(60), nullable=False)
    content = Column(String(255), nullable=False)
    published = Column(Boolean, nullable=False, server_default="FALSE")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User")


class User(Base):
    __tablename__ = "users"

    id = Column(PostgreSQLUUID, default=uuid.uuid4, primary_key=True, nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Vote(Base):
    __tablename__ = "votes"
    user_id = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    post_id = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
