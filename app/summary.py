"""Pay answers: headcount, payroll and the pay spread per group, all computed in SQL."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from sqlalchemy import case, func, literal, select
from sqlalchemy.orm import Session

from app.answers_cache import remember, remembered
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
    key = (group_by, filters)
    answer = remembered(key)
    if answer is None:
        groups = _summarise(session, GROUP_COLUMN[group_by], filters)
        overall = _summarise(session, literal("All"), filters)
        answer = remember(
            key,
            {
                "group_by": group_by,
                "overall": overall[0] if overall else _empty(),
                "groups": sorted(groups, key=lambda g: g["median_usd"], reverse=True),
            },
        )
    return answer


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

    # One pass: rank each group's pay once, then read every figure off that
    # ranking in a single GROUP BY. The median is the middle row (or the two
    # middle rows averaged); the quartiles are nearest-rank, ceil(p x n).
    ranked = select(
        people.c.name,
        people.c.usd,
        func.row_number().over(partition_by=people.c.name, order_by=people.c.usd).label("rank"),
        func.count().over(partition_by=people.c.name).label("size"),
    ).subquery()
    r = ranked.c
    middle = r.rank.between((r.size + 1) // 2, (r.size + 2) // 2)
    rows = session.execute(
        select(
            r.name,
            func.count().label("headcount"),
            func.sum(r.usd).label("payroll_usd"),
            func.min(r.usd).label("min_usd"),
            func.max(case((r.rank == (r.size + 3) // 4, r.usd))).label("p25_usd"),
            func.avg(case((middle, r.usd))).label("median_usd"),
            func.max(case((r.rank == (3 * r.size + 3) // 4, r.usd))).label("p75_usd"),
            func.max(r.usd).label("max_usd"),
        ).group_by(r.name)
    ).all()

    return [
        {
            "name": row.name,
            "headcount": row.headcount,
            "payroll_usd": _money(row.payroll_usd),
            "min_usd": _money(row.min_usd),
            "p25_usd": _money(row.p25_usd),
            "median_usd": _money(row.median_usd),
            "p75_usd": _money(row.p75_usd),
            "max_usd": _money(row.max_usd),
        }
        for row in rows
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
        "p25_usd": zero,
        "median_usd": zero,
        "p75_usd": zero,
        "max_usd": zero,
    }
