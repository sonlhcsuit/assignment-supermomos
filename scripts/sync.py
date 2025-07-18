from sqlalchemy import func, select
from sqlalchemy.orm.session import Session

from src.models import Event, Registration
from src.models.user import User

NUM_USERS = 100
NUM_EVENTS = 20
NUM_MIN_REGISTRATION = 20
NUM_MAX_REGISTRATION = 60


def sync_user_relation_count(session:Session):
    with session.begin():
        stm = select(
            Registration.user_id,
            func.count()
        ).group_by(Registration.user_id)
        records = session.execute(stm)
        users = []
        for record in records:
            id_ = record[0]
            no_attended = record[1]
            user = session.execute(select(User).filter(User.id == id_).with_for_update()).scalar_one_or_none()
            if user:
                user.number_events_attended = no_attended
                users.append(user)
        session.bulk_save_objects(users)

        stm = select(
            Event.owner_id,
            func.count()
        ).group_by(Event.owner_id)
        records = session.execute(stm)
        users = []
        for record in records:
            id_ = record[0]
            no_attended = record[1]
            user = session.execute(select(User).filter(User.id == id_).with_for_update()).scalar_one_or_none()
            if user:
                user.number_events_hosted = no_attended
                users.append(user)
        session.bulk_save_objects(users)
