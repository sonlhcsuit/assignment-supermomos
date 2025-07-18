import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    user_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    crm_status: str
    created_at: datetime.datetime
    last_activity_at: Optional[datetime.datetime] = None
    class Config:
        orm_mode = True # Enable ORM mode for Pydantic to read from SQLAlchemy models

class PaginatedUsersResponse(BaseModel):
    total_count: int
    page: int
    page_size: int
    users: List[UserBase]

class NumRange(BaseModel):
    min_number : int = 0
    max_number: int = 1000

class UserFilterCriteria(BaseModel):
    company_name: Optional[str]
    job_title: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    event_hosted: Optional[NumRange] = None
    event_attended: Optional[NumRange] = None
    page_last_id: Optional[int] = None
    page_size: Optional[int] = 10
    page: Optional[int] = 1
    sort_by: Optional[str] = 'email'
    sort_order: Optional[str] = 'asc'

