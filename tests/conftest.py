from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.db import make_engine, make_session_factory
from app.main import create_app
from app.models import Base, Department, Employee, FxRate, Location


@pytest.fixture
def session_factory():
    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield make_session_factory(engine)
    engine.dispose()


@pytest.fixture
def session(session_factory):
    with session_factory() as session:
        yield session


@pytest.fixture
def client(session_factory):
    return TestClient(create_app(session_factory))


@pytest.fixture
def asha(session):
    """One Pune engineer, hired 1 March 2021, with the INR rate in place."""
    session.add(FxRate(currency="INR", usd_per_unit=Decimal("0.0120"), as_of=date(2026, 10, 1)))
    person = Employee(
        id="ACME-2021-00001",
        full_name="Asha Patel",
        email="asha.patel@acme.example",
        job_title="Senior Software Engineer",
        level="L3",
        location=Location(city="Pune", country="India", currency="INR"),
        department=Department(name="Engineering"),
        hire_date=date(2021, 3, 1),
    )
    session.add(person)
    session.commit()
    return person
