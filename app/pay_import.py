"""Bulk pay changes from a CSV file.

Every row is checked first; nothing is saved unless all rows pass. The HR
manager gets one report with every problem row, fixes the file, and uploads
again. That is the same all-or-nothing rule a payroll run would need.
"""

import csv
import io
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.answers_cache import forget_answers
from app.models import Employee, FxRate, PayRecord
from app.rules import PayRuleError, check_pay_change, to_usd

COLUMNS = ["employee_id", "amount", "effective_from", "note"]
MAX_ROWS = 20_000


class ImportFileError(ValueError):
    """The file as a whole cannot be read; no rows were checked."""


@dataclass(frozen=True)
class RowError:
    line: int
    employee_id: str
    error: str


@dataclass(frozen=True)
class ImportResult:
    saved: int
    errors: list[RowError]


def import_pay_changes(session: Session, content: bytes) -> ImportResult:
    rows = _read(content)
    employees = _employees_for(session, {row["employee_id"] for row in rows})
    rates = {rate.currency: rate.usd_per_unit for rate in session.scalars(select(FxRate))}
    taken = _dates_already_taken(session, employees)

    records, errors, seen = [], [], set()
    for line, row in enumerate(rows, start=2):  # line 1 is the header
        try:
            records.append(_record_from(row, employees, rates, taken, seen))
        except (PayRuleError, ValueError) as problem:
            errors.append(RowError(line, row["employee_id"], str(problem)))

    if errors:
        return ImportResult(saved=0, errors=errors)
    session.add_all(records)
    session.commit()
    forget_answers()
    return ImportResult(saved=len(records), errors=[])


def _read(content: bytes) -> list[dict]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as problem:
        raise ImportFileError(
            "The file is not readable as UTF-8 text. Save it as CSV (UTF-8)."
        ) from problem
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or [c.strip() for c in reader.fieldnames][:3] != COLUMNS[:3]:
        raise ImportFileError(
            "The first line must be the header: employee_id, amount, effective_from, note"
        )
    rows = [{k.strip(): (v or "").strip() for k, v in row.items() if k} for row in reader]
    if len(rows) > MAX_ROWS:
        raise ImportFileError(f"At most {MAX_ROWS:,} rows per file; this one has {len(rows):,}.")
    return rows


def _employees_for(session: Session, ids: set[str]) -> dict[str, Employee]:
    found = session.scalars(select(Employee).where(Employee.id.in_(ids))).all()
    return {employee.id: employee for employee in found}


def _dates_already_taken(session: Session, employees: dict[str, Employee]) -> set[tuple[str, date]]:
    existing = session.execute(
        select(PayRecord.employee_id, PayRecord.effective_from).where(
            PayRecord.employee_id.in_(employees)
        )
    ).all()
    return {(employee_id, effective_from) for employee_id, effective_from in existing}


def _record_from(row: dict, employees: dict, rates: dict, taken: set, seen: set) -> PayRecord:
    employee = employees.get(row["employee_id"])
    if employee is None:
        raise ValueError(f"No employee with id {row['employee_id'] or '(blank)'}")
    try:
        amount = Decimal(row["amount"])
    except InvalidOperation as problem:
        raise ValueError(f"amount must be a number, got {row['amount']!r}") from problem
    try:
        effective_from = date.fromisoformat(row["effective_from"])
    except ValueError as problem:
        raise ValueError(
            f"effective_from must be a date like 2026-04-01, got {row['effective_from']!r}"
        ) from problem

    currency = employee.location.currency
    check_pay_change(
        amount=amount,
        currency=currency,
        location_currency=currency,
        effective_from=effective_from,
        hire_date=employee.hire_date,
    )
    key = (employee.id, effective_from)
    if key in taken:
        raise ValueError(f"{employee.full_name} already has a pay change on {effective_from}")
    if key in seen:
        raise ValueError(f"Another row in this file has the same effective_from for {employee.id}")
    seen.add(key)

    return PayRecord(
        employee_id=employee.id,
        amount=amount,
        currency=currency,
        amount_usd=to_usd(amount, rates[currency]),
        effective_from=effective_from,
        note=row.get("note") or None,
    )
