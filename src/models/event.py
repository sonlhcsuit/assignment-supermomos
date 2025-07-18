import datetime
import uuid

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.models.base import BaseModelWithAuditAndId


class EventType(BaseModelWithAuditAndId):
    """
    SQLAlchemy model for the 'event_types' table.
    Defines the categories or templates for different types of CRM events.
    """

    __tablename__ = 'event_types'
    __table_args__ = {'extend_existing': True}  # noqa: RUF012

    type_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Define relationships
    # One EventType can have many Events
    events = relationship('Event', back_populates='event_type', lazy=True)
    extend_existing = True

    def __repr__(self):
        return f"<EventType(id='{self.event_type_id}', name='{self.type_name}', category='{self.category}')>"


class Event(BaseModelWithAuditAndId):
    """
    SQLAlchemy model for the 'events' table.
    Records each specific instance of an event that a user is associated with.
    """

    __tablename__ = 'events'
    __table_args__ = {'extend_existing': True}  # noqa: RUF012

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    event_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('event_types.id'), nullable=False
    )
    event_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_status: Mapped[str] = mapped_column(String(50), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    event_details: Mapped[dict] = mapped_column(JSON, nullable=True)  # JSONB for PostgreSQL, JSON for others
    recorded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=True
    )

    owner = relationship('User', foreign_keys=[owner_id], back_populates='events', lazy=True)
    event_type = relationship('EventType', back_populates='events', lazy=True)
    recorded_by_user = relationship(
        'User', foreign_keys=[recorded_by_user_id], back_populates='recorded_events', lazy=True
    )
    registrations = relationship('Registration', back_populates='event', lazy=True)

    def __repr__(self):
        return f"<Event(id='{self.event_id}', user_id='{self.owner_id}', type='{self.event_type.type_name if self.event_type else 'N/A'}', timestamp='{self.event_timestamp}')>"
