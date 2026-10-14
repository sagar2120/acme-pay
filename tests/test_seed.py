from sqlalchemy import func, select

from app.db import make_engine, make_session_factory
from app.models import Base, Employee, Location, PayRecord
from app.seed import seed

SMALL = 200


def count(session, model):
    return session.scalar(select(func.count()).select_from(model))


def test_seed_creates_the_requested_number_of_employees(session):
    seed(session, count=SMALL)

    assert count(session, Employee) == SMALL


def test_seeding_a_second_time_adds_nothing(session):
    seed(session, count=SMALL)
    seed(session, count=SMALL)

    assert count(session, Employee) == SMALL


def test_every_run_produces_the_same_people_and_pay():
    def first_employee_and_pay():
        engine = make_engine("sqlite://")
        Base.metadata.create_all(engine)
        with make_session_factory(engine)() as s:
            seed(s, count=SMALL)
            person = s.scalars(select(Employee).order_by(Employee.id)).first()
            pay = s.scalars(select(PayRecord).where(PayRecord.employee_id == person.id)).first()
            return person.id, person.full_name, person.level, pay.amount

    assert first_employee_and_pay() == first_employee_and_pay()


def test_every_pay_record_is_in_the_currency_of_the_employees_location(session):
    seed(session, count=SMALL)

    mismatched = session.scalar(
        select(func.count())
        .select_from(PayRecord)
        .join(Employee, PayRecord.employee_id == Employee.id)
        .join(Location, Employee.location_id == Location.id)
        .where(PayRecord.currency != Location.currency)
    )
    assert mismatched == 0
