from typing import Tuple

from src.models.user import User
from src.repos.user import UserRepo
from src.schemas.dto.user import UserBase, UserFilterCriteria


class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def construct_criteria() -> UserFilterCriteria:
        return None

    def filter_user(
        self,
        criteria: UserFilterCriteria,
    ) -> Tuple[int, list[UserBase]]:

        with self.user_repo.db.sync_session() as session:
            query = self.user_repo.retrieve_user_using_criteria(criteria=criteria)
            print(query)
            cnt = session.query(query.subquery()).count()
            offset = (criteria.page - 1) * criteria.page_size
            query = self.user_repo.data_range(
                query,
                limit=criteria.page_size,
                offset=offset,
                sort_by=criteria.sort_by,
                sort_order=criteria.sort_order,
            )

            records = session.execute(query).scalars()
            users = list(map(UserService.mapperUserModelToUserResponse, records))
        return cnt, users

    @staticmethod
    def mapperUserModelToUserResponse(user: User) -> UserBase:
        return UserBase(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            company_name=user.company_name,
            job_title=user.job_title,
            city='newyork',
            state='carolina',
            crm_status=user.crm_status,
            created_at=user.created_at,
            last_activity_at=user.last_activity_at,
        )
