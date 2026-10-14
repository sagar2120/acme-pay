from dataclasses import dataclass
from typing import Literal

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models import Department, Employee, Location, PayRecord
from app.pay import EmployeeNotFound, current_pay

Sort = Literal["name", "-name", "pay_usd", "-pay_usd"]


@dataclass(frozen=True)
class Filters:
    q: str | None = None
    location_id: int | None = None
    department_id: int | None = None
    level: str | None = None


def list_employees(
    session: Session, filters: Filters, sort: Sort, page: int, page_size: int
) -> tuple[list, int]:
    pay = current_pay()
    query = (
        select(
            Employee.id,
            Employee.full_name,
            Employee.job_title,
            Employee.level,
            Location.city.label("location"),
            Department.name.label("department"),
            pay.c.amount.label("pay_amount"),
            pay.c.currency.label("pay_currency"),
            pay.c.amount_usd.label("pay_usd"),
        )
        .join(Location, Employee.location_id == Location.id)
        .join(Department, Employee.department_id == Department.id)
        .outerjoin(pay, pay.c.employee_id == Employee.id)
    )
    query = active_matching(query, filters)

    total = session.scalar(select(func.count()).select_from(query.subquery()))
    order = {
        "name": Employee.full_name.asc(),
        "-name": Employee.full_name.desc(),
        "pay_usd": pay.c.amount_usd.asc(),
        "-pay_usd": pay.c.amount_usd.desc(),
    }[sort]
    rows = session.execute(
        query.order_by(order, Employee.id).limit(page_size).offset((page - 1) * page_size)
    ).all()
    return rows, total


def active_matching(query: Select, filters: Filters) -> Select:
    """Active employees matching the filters. Shared by the list and the pay summary."""
    query = query.where(Employee.is_active)
    if filters.q:
        pattern = f"%{filters.q}%"
        query = query.where(or_(Employee.full_name.ilike(pattern), Employee.email.ilike(pattern)))
    if filters.location_id is not None:
        query = query.where(Employee.location_id == filters.location_id)
    if filters.department_id is not None:
        query = query.where(Employee.department_id == filters.department_id)
    if filters.level:
        query = query.where(Employee.level == filters.level)
    return query


def get_employee(session: Session, employee_id: str) -> tuple[Employee, list[PayRecord]]:
    employee = session.get(Employee, employee_id)
    if employee is None:
        raise EmployeeNotFound(f"No employee with id {employee_id}")
    history = session.scalars(
        select(PayRecord)
        .where(PayRecord.employee_id == employee_id)
        .order_by(PayRecord.effective_from.desc())
    ).all()
    return employee, list(history)
