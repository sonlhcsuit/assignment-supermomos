import uuid
from datetime import datetime

from sqlalchemy import UUID, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all models in the application.

    This class inherits from SQLAlchemy's DeclarativeBase and serves as the
    foundation for all ORM models. It provides a consistent base for defining
    database tables and their relationships.
    """

    __abstract__ = True


class UUIDMixin:
    """Mixin for UUID primary key.

    This mixin provides a consistent UUID primary key implementation
    across all models that need it, using PostgreSQL's gen_random_uuid() function.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=text('gen_random_uuid()'),
        nullable=False,
    )


class AuditMixin:
    """Mixin for audit columns (created_at, updated_at).

    This mixin provides consistent timestamp tracking for all models
    as specified in the README. Both fields are required and automatically
    managed by the database.
    """

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        comment='Timestamp of when the record was created',
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment='Timestamp of when the record was last updated',
    )


class BaseModelWithAuditAndId(Base, UUIDMixin, AuditMixin):
    """Base model class that combines UUID primary key and audit columns.

    This class should be used as the base for most models that need both
    UUID primary keys and audit timestamps, providing a consistent
    foundation following the README specifications.
    """

    __abstract__ = True
