import datetime
import random
import uuid
from uuid import uuid4

from faker import Faker  # For generating realistic-looking data
from sqlalchemy import select
from sqlalchemy.orm.session import Session

from src.models import Event, EventType, Registration
from src.models.user import User

NUM_USERS = 100
NUM_EVENTS = 20
NUM_MIN_REGISTRATION = 20
NUM_MAX_REGISTRATION = 60

SEED = 1739
Faker.seed(SEED)
fake = Faker()
rd = random.Random()  # noqa: F821
rd.seed(SEED)



def gen_consistent_uuid() -> uuid.UUID:
    return uuid.UUID(int=rd.getrandbits(128))


def generate_users(num_users):
    """Generates a list of dummy User objects."""
    users = []
    crm_statuses = ['Lead', 'Prospect', 'Customer', 'Churned']
    lead_sources = ['Website', 'Referral', 'Campaign', 'Direct Mail', 'Social Media']
    for _ in range(num_users):
        first_name = fake.first_name()
        last_name = fake.last_name()
        user = User(
            id=gen_consistent_uuid(),
            first_name=first_name,
            last_name=last_name,
            email=fake.unique.email(),
            phone_number=fake.phone_number(),
            company_name=fake.company(),
            job_title=fake.job(),
            crm_status=random.choice(crm_statuses),
            lead_source=random.choice(lead_sources),
            last_activity_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=datetime.UTC),
        )
        users.append(user)
    return users


def generate_event_types():
    """Generates a list of common EventType objects."""
    event_types_data = [
        {'name': 'Product Demo', 'desc': 'Live demonstration of a product', 'cat': 'Sales'},
        {'name': 'Support Call', 'desc': 'Customer support interaction', 'cat': 'Support'},
        {'name': 'Webinar', 'desc': 'Online seminar about a topic', 'cat': 'Marketing'},
        {'name': 'Email Opened', 'desc': 'User opened a marketing email', 'cat': 'Engagement'},
        {'name': 'Meeting Scheduled', 'desc': 'A meeting with a prospect/customer', 'cat': 'Sales'},
        {'name': 'Website Visit', 'desc': 'User visited a specific page on website', 'cat': 'Engagement'},
        {'name': 'Contract Signed', 'desc': 'Customer signed a contract', 'cat': 'Sales'},
        {'name': 'Feedback Received', 'desc': 'User provided feedback', 'cat': 'Support'},
    ]
    event_types = []
    for et_data in event_types_data:
        event_types.append(
            EventType(id=gen_consistent_uuid(),type_name=et_data['name'], description=et_data['desc'], category=et_data['cat'])
        )
    return event_types


def generate_events(num_events, users, event_types):
    """Generates a list of dummy Event objects."""
    events = []
    event_statuses = ['Completed', 'Scheduled', 'Cancelled', 'Failed']

    # Ensure there are enough users and event types to pick from
    if not users or not event_types:
        print('Error: Cannot generate events without users or event types.')
        return []

    for _ in range(num_events):
        random_user = random.choice(users)
        random_event_type = random.choice(event_types)

        # Randomly select a CRM user to record the event (can be None)
        recorded_by = random.choice([*users, None])

        event = Event(
            id=gen_consistent_uuid(),
            owner_id=random_user.id,
            event_type=random_event_type,
            event_timestamp=fake.date_time_between(
                start_date='-6m', end_date='now', tzinfo=datetime.timezone.utc
            ),
            event_status=random.choice(event_statuses),
            duration_minutes=random.randint(10, 120)
            if random_event_type.category in ['Sales', 'Support']
            else None,
            notes=fake.sentence() if random.random() > 0.3 else None,  # Add notes sometimes
            event_details={
                'detail_key': fake.word(),
                'value': fake.random_int(min=1, max=100),
            },  # Simple JSON details
        )
        # Assign recorded_by_user if a user was chosen
        if recorded_by:
            event.recorded_by_user = recorded_by

        events.append(event)
    return events


def generate_registration(users: list[User], events: list[Event]):
    regs = []
    for event in events:
        number_of_participant = random.randrange(NUM_MIN_REGISTRATION, NUM_MAX_REGISTRATION)
        participants: list[User] = random.choices(users, k=number_of_participant)

        for participant in participants:
            if participant.id == event.owner_id:
                continue
            reg = Registration(
                id=gen_consistent_uuid(),
                user_id=participant.id,
                event_id=event.id,
                registration_timestamp=fake.date_time_between(start_date='-1y', end_date='now'),
                status=random.choice(['Registered', 'Attended', 'Cancelled']),
            )
            regs.append(reg)
    return regs


def seeding_data(session: Session):
    with session.begin():
        rec = []
        stm = select(User.id).limit(1)
        user_cnt = session.execute(stm).scalar_one_or_none()
        if user_cnt is None:
            users = generate_users(NUM_USERS)
            rec = rec + users
            # session.add_all(users)
            # session.commit()

        stm = select(EventType.id).limit(1)
        event_type = session.execute(stm).scalar_one_or_none()
        if event_type is None:
            event_types = generate_event_types()
            rec = rec + event_types
            # session.add_all(event_types)
            # session.commit()

        stm = select(Event.id).limit(1)
        event = session.execute(stm).scalar_one_or_none()
        if event is None:
            events = generate_events(
                NUM_EVENTS,
                users if len(users) > 0 else [],
                event_types=event_types if len(event_types) > 0 else [],
            )
            rec = rec + events
            # session.add_all(events)
            # session.commit()

        stm = select(Registration.id).limit(1)
        reg = session.execute(stm).scalar_one_or_none()
        if reg is None:
            regs = generate_registration(
                users if len(users) > 0 else [],
                events=events if len(events) > 0 else [],
            )
            rec = rec + regs
            # session.add_all(regs)
        session.add_all(rec)
        session.commit()


