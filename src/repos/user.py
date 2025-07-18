from typing import Optional
from sqlalchemy import and_, select, text, true
from sqlalchemy.orm import Query

from src.core.db import Database
from src.models import User
from src.schemas.dto.user import UserFilterCriteria


class UserRepo:
    def __init__(self, db: Database):
        self.db = db

    def retrieve_user_using_criteria(self, criteria: UserFilterCriteria) -> Query:
        stm = select(User)
        # --- Apply Text Filters (case-insensitive, partial match) ---
        # We can go with == operator with exact match, or migrate to ES for better perf for i-like search
        if criteria.company_name:
            stm = stm.filter(User.company_name.ilike(f'%{criteria.company_name}%'))
        if criteria.job_title:
            stm = stm.filter(User.job_title.ilike(f'%{criteria.job_title}%'))
        if criteria.city:
            stm = stm.filter(User.city.ilike(f'%{criteria.city}%'))
        if criteria.state:
            stm = stm.filter(User.state.ilike(criteria))
        # In order to maintain consistency for min_number, max_number. An update on user's analytics data when they
        # register for an event is need. Since the cost of group by and count when querying maybe a huge problem
        if criteria.event_hosted:
            min_cond, max_cond = None, None
            if criteria.event_hosted.min_number:
                min_cond = User.number_events_hosted > criteria.event_hosted.min_number
            if criteria.event_hosted.max_number:
                max_cond = User.number_events_hosted < criteria.event_hosted.max_number
            conds = list(filter(lambda x: x is not None, [min_cond, max_cond]))
            stm = stm.filter(true(), and_(**conds))

        if criteria.event_attended:
            min_cond, max_cond = None, None
            if criteria.event_attended.min_number:
                min_cond = User.number_events_hosted > criteria.event_attended.min_number
            if criteria.event_attended.max_number:
                max_cond = User.number_events_hosted < criteria.event_attended.max_number
            conds = list(filter(lambda x: x is not None, [min_cond, max_cond]))
            stm = stm.filter(true(), and_(**conds))
        return stm

    def data_range(self, stm: Query, limit: int, offset: int, sort_by: str, sort_order: str) -> Query:  # noqa: F821
        # Since it was just an simple assignment. I dont want to spend too much time on this once so I go with the naive
        # approach using offset & limit. We can enhance it using keyset pagination
        stm = stm.order_by(text(f'{sort_by} {sort_order}'))
        stm = stm.limit(limit).offset(offset)
        return stm
