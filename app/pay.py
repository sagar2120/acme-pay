from datetime import date
from decimal import Decimal

from sqlalchemy import Subquery, func, select
from sqlalchemy.orm import Session

from app.answers_cache import forget_answers
from app.models import Employee, FxRate, PayRecord
from app.rules import check_pay_change, to_usd


class EmployeeNotFound(LookupError):
    pass


class SamePayChangeDate(ValueError):
    pass


def current_pay() -> Subquery:
    """One row per employee: their newest pay record.

    The unique (employee_id, effective_from) constraint means there is never a tie.
    """
    ranked = select(
        PayRecord,
        func.row_number()
        .over(partition_by=PayRecord.employee_id, order_by=PayRecord.effective_from.desc())
        .label("newest_first"),
    ).subquery()
    return select(ranked).where(ranked.c.newest_first == 1).subquery("current_pay")


def record_pay_change(
    session: Session,
    employee_id: str,
    amount: Decimal,
    effective_from: date,
    note: str | None = None,
) -> PayRecord:
    employee = session.get(Employee, employee_id)
    if employee is None:
        raise EmployeeNotFound(f"No employee with id {employee_id}")

    currency = employee.location.currency
    check_pay_change(
        amount=amount,
        currency=currency,
        location_currency=currency,
        effective_from=effective_from,
        hire_date=employee.hire_date,
    )
    already = session.scalar(
        select(PayRecord.id).where(
            PayRecord.employee_id == employee_id, PayRecord.effective_from == effective_from
        )
    )
    if already:
        raise SamePayChangeDate(
            f"{employee.full_name} already has a pay change on {effective_from}"
        )

    rate = session.get(FxRate, currency)
    record = PayRecord(
        employee_id=employee_id,
        amount=amount,
        currency=currency,
        amount_usd=to_usd(amount, rate.usd_per_unit),
        effective_from=effective_from,
        note=note,
    )
    session.add(record)
    session.commit()
    forget_answers()
    return record
