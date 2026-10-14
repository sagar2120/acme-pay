"""Pay answers: headcount, payroll and the pay spread per group, all computed in SQL."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from sqlalchemy import func, literal, select
from sqlalchemy.orm import Session

from app.employees import Filters, active_matching
from app.models import Department, Employee, Location
from app.pay import current_pay

GroupBy = Literal["location", "department", "level"]

GROUP_COLUMN = {
    "location": Location.city,
    "department": Department.name,
    "level": Employee.level,
}
CENT = Decimal("0.01")


def pay_summary(session: Session, group_by: GroupBy, filters: Filters) -> dict:
    groups = _summarise(session, GROUP_COLUMN[group_by], filters)
    overall = _summarise(session, literal("All"), filters)
    return {
        "group_by": group_by,
        "overall": overall[0] if overall else _empty(),
        "groups": sorted(groups, key=lambda g: g["median_usd"], reverse=True),
    }


def _summarise(session: Session, group_column, filters: Filters) -> list[dict]:
    pay = current_pay()
    people = active_matching(
        select(group_column.label("name"), pay.c.amount_usd.label("usd"))
        .select_from(Employee)
        .join(Location, Employee.location_id == Location.id)
        .join(Department, Employee.department_id == Department.id)
        .join(pay, pay.c.employee_id == Employee.id),
        filters,
    ).subquery()

    totals = session.execute(
        select(
            people.c.name,
            func.count().label("headcount"),
            func.sum(people.c.usd).label("payroll_usd"),
            func.min(people.c.usd).label("min_usd"),
            func.max(people.c.usd).label("max_usd"),
        ).group_by(people.c.name)
    ).all()

    # Median: number each group's pay in order, keep the middle row (odd count)
    # or the middle two rows (even count), and average them. Works on SQLite and Postgres.
    ranked = select(
        people.c.name,
        people.c.usd,
        func.row_number().over(partition_by=people.c.name, order_by=people.c.usd).label("rank"),
        func.count().over(partition_by=people.c.name).label("size"),
    ).subquery()
    medians = dict(
        session.execute(
            select(ranked.c.name, func.avg(ranked.c.usd))
            .where(ranked.c.rank.between((ranked.c.size + 1) // 2, (ranked.c.size + 2) // 2))
            .group_by(ranked.c.name)
        ).all()
    )

    return [
        {
            "name": row.name,
            "headcount": row.headcount,
            "payroll_usd": _money(row.payroll_usd),
            "min_usd": _money(row.min_usd),
            "median_usd": _money(medians[row.name]),
            "max_usd": _money(row.max_usd),
        }
        for row in totals
    ]


def _money(value) -> Decimal:
    # SQLite returns aggregates of NUMERIC columns as floats; bring them back to cents.
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def _empty() -> dict:
    zero = Decimal("0.00")
    return {
        "name": "All",
        "headcount": 0,
        "payroll_usd": zero,
        "min_usd": zero,
        "median_usd": zero,
        "max_usd": zero,
    }
