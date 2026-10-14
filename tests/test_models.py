from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import PayRecord


def pay(employee_id, effective_from):
    return PayRecord(
        employee_id=employee_id,
        amount=Decimal("1800000.00"),
        currency="INR",
        amount_usd=Decimal("21600.00"),
        effective_from=effective_from,
    )


def test_pay_record_for_unknown_employee_is_rejected(session):
    session.add(pay("ACME-2021-99999", date(2022, 4, 1)))

    with pytest.raises(IntegrityError):
        session.flush()


def test_two_pay_records_for_one_employee_on_the_same_day_are_rejected(session, asha):
    session.add(pay(asha.id, date(2022, 4, 1)))
    session.flush()
    session.add(pay(asha.id, date(2022, 4, 1)))

    with pytest.raises(IntegrityError):
        session.flush()
