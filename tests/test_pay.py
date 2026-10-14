from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models import PayRecord
from app.pay import EmployeeNotFound, SamePayChangeDate, current_pay, record_pay_change


def current_amount(session, employee_id):
    cp = current_pay()
    return session.scalar(select(cp.c.amount).where(cp.c.employee_id == employee_id))


def test_the_newest_pay_record_is_the_current_pay(session, asha):
    record_pay_change(session, asha.id, Decimal("1500000"), date(2021, 3, 1))
    record_pay_change(session, asha.id, Decimal("1800000"), date(2022, 4, 1))

    assert current_amount(session, asha.id) == Decimal("1800000")


def test_a_backdated_change_does_not_replace_a_newer_one(session, asha):
    record_pay_change(session, asha.id, Decimal("1800000"), date(2022, 4, 1))
    record_pay_change(session, asha.id, Decimal("1500000"), date(2021, 3, 1))

    assert current_amount(session, asha.id) == Decimal("1800000")


def test_a_pay_change_adds_a_record_and_leaves_older_ones_untouched(session, asha):
    first = record_pay_change(session, asha.id, Decimal("1500000"), date(2021, 3, 1))
    record_pay_change(session, asha.id, Decimal("1800000"), date(2022, 4, 1))

    amounts = session.scalars(select(PayRecord.amount).order_by(PayRecord.effective_from)).all()
    assert amounts == [Decimal("1500000"), Decimal("1800000")]
    assert session.get(PayRecord, first.id).amount == Decimal("1500000")


def test_pay_is_stored_in_the_location_currency_with_its_usd_value(session, asha):
    record = record_pay_change(
        session, asha.id, Decimal("1800000"), date(2022, 4, 1), note="Promotion"
    )

    assert (record.currency, record.amount_usd, record.note) == (
        "INR",
        Decimal("21600.00"),
        "Promotion",
    )


def test_pay_change_for_an_unknown_employee_is_refused(session):
    with pytest.raises(EmployeeNotFound):
        record_pay_change(session, "ACME-2021-99999", Decimal("1800000"), date(2022, 4, 1))


def test_a_second_pay_change_on_the_same_day_is_refused(session, asha):
    record_pay_change(session, asha.id, Decimal("1800000"), date(2022, 4, 1))

    with pytest.raises(SamePayChangeDate, match="2022-04-01"):
        record_pay_change(session, asha.id, Decimal("1900000"), date(2022, 4, 1))
