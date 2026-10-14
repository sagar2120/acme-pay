from datetime import date
from decimal import Decimal

import pytest

from app.rules import (
    CurrencyMismatch,
    PayChangeBeforeHire,
    PayNotPositive,
    check_pay_change,
    to_usd,
)

HIRED = date(2021, 3, 1)


def change(**overrides):
    valid = dict(
        amount=Decimal("1800000"),
        currency="INR",
        location_currency="INR",
        effective_from=date(2022, 4, 1),
        hire_date=HIRED,
    )
    return {**valid, **overrides}


def test_a_valid_pay_change_passes():
    check_pay_change(**change())


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-1")])
def test_pay_that_is_zero_or_negative_is_rejected(amount):
    with pytest.raises(PayNotPositive):
        check_pay_change(**change(amount=amount))


def test_pay_in_a_currency_other_than_the_locations_is_rejected():
    with pytest.raises(CurrencyMismatch, match="INR"):
        check_pay_change(**change(currency="EUR"))


def test_pay_change_before_hire_date_is_rejected():
    with pytest.raises(PayChangeBeforeHire, match="2021-02-28 is before hire date 2021-03-01"):
        check_pay_change(**change(effective_from=date(2021, 2, 28)))


def test_pay_change_on_the_hire_date_is_allowed():
    check_pay_change(**change(effective_from=HIRED))


def test_usd_conversion_rounds_half_up_to_cents():
    # 1000 x 0.012345 = 12.345 exactly; half-up gives 12.35 (banker's rounding would give 12.34)
    assert to_usd(Decimal("1000"), Decimal("0.012345")) == Decimal("12.35")
