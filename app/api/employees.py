from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.api.pay import PayRecordOut
from app.employees import Filters, Sort, get_employee, list_employees

router = APIRouter(prefix="/api")


class EmployeeRow(BaseModel):
    id: str
    full_name: str
    job_title: str
    level: str
    location: str
    department: str
    pay_amount: Decimal | None
    pay_currency: str | None
    pay_usd: Decimal | None


class EmployeePage(BaseModel):
    items: list[EmployeeRow]
    total: int
    page: int
    page_size: int


class EmployeeDetail(BaseModel):
    id: str
    full_name: str
    email: str
    job_title: str
    level: str
    location: str
    currency: str
    department: str
    hire_date: date
    is_active: bool
    pay_history: list[PayRecordOut]


def filters(
    q: str | None = None,
    location_id: int | None = None,
    department_id: int | None = None,
    level: str | None = None,
) -> Filters:
    return Filters(q=q, location_id=location_id, department_id=department_id, level=level)


@router.get("/employees", response_model=EmployeePage)
def get_employees(
    session: Annotated[Session, Depends(get_session)],
    matching: Annotated[Filters, Depends(filters)],
    sort: Sort = "name",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 50,
):
    rows, total = list_employees(session, matching, sort, page, page_size)
    return {"items": rows, "total": total, "page": page, "page_size": page_size}


@router.get("/employees/{employee_id}", response_model=EmployeeDetail)
def get_one_employee(employee_id: str, session: Annotated[Session, Depends(get_session)]):
    employee, history = get_employee(session, employee_id)
    return {
        **{c: getattr(employee, c) for c in ("id", "full_name", "email", "job_title", "level")},
        "location": employee.location.city,
        "currency": employee.location.currency,
        "department": employee.department.name,
        "hire_date": employee.hire_date,
        "is_active": employee.is_active,
        "pay_history": history,
    }
