"""Rules every pay change must pass. Pure functions: no database, no web framework."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
# Above this the number is a typo, whatever the currency (one billion a year).
MAX_ANNUAL_PAY = Decimal("1000000000")


class PayRuleError(ValueError):
    pass


class PayNotPositive(PayRuleError):
    pass


class CurrencyMismatch(PayRuleError):
    pass


class PayChangeBeforeHire(PayRuleError):
    pass


def check_pay_change(
    *,
    amount: Decimal,
    currency: str,
    location_currency: str,
    effective_from: date,
    hire_date: date,
) -> None:
    if amount <= 0:
        raise PayNotPositive(f"Annual amount must be greater than zero, got {amount}")
    if amount > MAX_ANNUAL_PAY:
        raise PayNotPositive(f"Annual amount {amount} is above the limit of {MAX_ANNUAL_PAY:,}")
    if currency != location_currency:
        raise CurrencyMismatch(
            f"Pay must be in {location_currency}, the currency of the employee's location; "
            f"got {currency}"
        )
    if effective_from < hire_date:
        raise PayChangeBeforeHire(f"Pay change on {effective_from} is before hire date {hire_date}")


def to_usd(amount: Decimal, usd_per_unit: Decimal) -> Decimal:
    return (amount * usd_per_unit).quantize(CENT, rounding=ROUND_HALF_UP)
