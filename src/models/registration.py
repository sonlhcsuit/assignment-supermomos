import datetime
import uuid

from sqlalchemy import (
    UUID,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.models.base import BaseModelWithAuditAndId


class Registration(BaseModelWithAuditAndId):
    """
    SQLAlchemy model for the 'registrations' table.
    Links users to specific events they have signed up for.
    """

    __tablename__ = 'registrations'
    # __table_args__ = {'extend_existing': True}  # noqa: RUF012

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('events.id'), nullable=False)
    registration_timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default='Registered', nullable=False
    )  # e.g., 'Registered', 'Attended', 'Cancelled'
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Define relationships
    # Many Registrations belong to one User
    user = relationship('User', back_populates='registrations', lazy=True)
    # Many Registrations belong to one Event
    event = relationship('Event', back_populates='registrations', lazy=True)

    def __repr__(self):
        return f"<Registration(id='{self.registration_id}', user_id='{self.user_id}', event_id='{self.event_id}', status='{self.status}')>"
