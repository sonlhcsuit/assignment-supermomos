"""Common API endpoints."""

from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from services.user import UserService
from src.container import Container
from src.core.logger import get_logger
from src.schemas.dto.user import (
    NumRange,
    PaginatedUsersResponse,
    UserFilterCriteria,
)

common_router = APIRouter(prefix='/api', tags=['Common'])
logger = get_logger(__name__)


@common_router.get('/health')
async def health_check():
    """Health check endpoint."""
    return {'status': 'healthy'}


@common_router.get('/ping')
async def ping():
    """Ping endpoint."""
    return {'message': 'pong'}


# --- Endpoint ---
@common_router.get('/users', response_model=PaginatedUsersResponse)
@inject
async def retrieve_user(  # noqa: PLR0913
    # Since this one is too many argument, we can UserFilterCriteria as an input validator - request body
    # and change from get to post in order to support RequestModel from fastapi
    user_service: UserService = Depends(Provide[Container.user_service]),
    company_name: Optional[str] = Query(
        None, description='Filter by company name (case-insensitive, partial match)'
    ),
    job_title: Optional[str] = Query(
        None, description='Filter by job title (case-insensitive, partial match)'
    ),
    city: Optional[str] = Query(None, description='Filter by city (case-insensitive, partial match)'),
    state: Optional[str] = Query(None, description='Filter by state (case-insensitive, exact match)'),
    min_events_hosted: Optional[int] = Query(
        None, ge=0, description='Minimum number of events hosted by the user'
    ),
    max_events_hosted: Optional[int] = Query(
        None, ge=0, description='Maximum number of events hosted by the user'
    ),
    min_events_attended: Optional[int] = Query(
        None, ge=0, description='Minimum number of events attended by the user'
    ),
    max_events_attended: Optional[int] = Query(
        None, ge=0, description='Maximum number of events attended by the user'
    ),
    page: int = Query(1, ge=1, description='Page number for pagination'),
    page_size: int = Query(10, ge=1, le=100, description='Number of users per page'),
    page_last_id: int = Query(None, description='Last id of the page to improve pagination.'),
    sort_by: Optional[str] = Query(
        'email',
        description="Field to sort by (e.g., 'first_name', 'last_name', 'email', 'company_name', 'job_title', 'city', 'state', 'created_at', 'events_hosted_count', 'events_attended_count')",
        regex='^(first_name|last_name|email|company_name|job_title|city|state|created_at|events_hosted_count|events_attended_count)$',
    ),
    sort_order: Optional[str] = Query(
        'asc', description="Sort order ('asc' for ascending, 'desc' for descending)", regex='^(asc|desc)$'
    ),
):
    """
    Filters CRM users based on various criteria, supporting pagination and sorting.

    **Filtering Criteria:**
    - `company_name`: Filter by company name (case-insensitive, partial match).
    - `job_title`: Filter by job title (case-insensitive, partial match).
    - `city`: Filter by city (case-insensitive, partial match).
    - `state`: Filter by state (case-insensitive, exact match).
    - `min_events_hosted`: Filter by minimum number of events recorded/hosted by the user.
    - `max_events_hosted`: Filter by maximum number of events recorded/hosted by the user.
    - `min_events_attended`: Filter by minimum number of events attended/registered for by the user.
    - `max_events_attended`: Filter by maximum number of events attended/registered for by the user.

    **Pagination:**
    - `page`: Current page number (starts from 1).
    - `page_size`: Number of results per page (max 100).

    **Sorting:**
    - `sort_by`: Field to sort the results by.
    - `sort_order`: 'asc' for ascending (default), 'desc' for descending.
    """

    criteria = UserFilterCriteria(
        company_name=company_name,
        job_title=job_title,
        city=city,
        state=state,
        event_hosted=NumRange(min_events_hosted, max_events_hosted)
        if min_events_hosted or max_events_hosted
        else None,
        event_attended=NumRange(min_events_attended, max_events_attended)
        if min_events_attended or max_events_attended
        else None,
        page=page,
        page_size=page_size,
        page_last_id=page_last_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    total_count, user = user_service.filter_user(criteria=criteria)

    return PaginatedUsersResponse(total_count=0, page=0, page_size=0, users=[])
    return PaginatedUsersResponse(total_count=total_count, page=page, page_size=page_size, users=user)
