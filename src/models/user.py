import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModelWithAuditAndId


class User(BaseModelWithAuditAndId):
    """
    SQLAlchemy model for the 'users' table.
    Represents individual customers or contacts in the CRM system.
    """

    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # noqa: RUF012

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(String(100), nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=True)
    job_title: Mapped[str] = mapped_column(String(100), nullable=True)
    last_activity_at: Mapped[datetime.date] = mapped_column(DateTime(timezone=True), nullable=True)
    crm_status: Mapped[str] = mapped_column(String(100), default='Lead', nullable=False)
    lead_source: Mapped[str] = mapped_column(String(100), nullable=True)
    number_events_hosted: Mapped[int] = mapped_column(Integer(), nullable=False)
    number_events_attended: Mapped[int] = mapped_column(Integer(), nullable=False)

    # Define relationships
    # One User can have many Events
    events = relationship('Event', foreign_keys='Event.owner_id', back_populates='owner', lazy=True)
    # One User can record many Events (if they are a CRM user)
    recorded_events = relationship(
        'Event', foreign_keys='Event.recorded_by_user_id', back_populates='recorded_by_user', lazy=True
    )
    # One User can have many Registrations
    registrations = relationship('Registration', back_populates='user', lazy=True)

    def __repr__(self):
        return f"<User(id='{self.id}', name='{self.first_name} {self.last_name}', email='{self.email}')>"
