from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.api.employees import filters
from app.employees import Filters
from app.summary import GroupBy, pay_summary

router = APIRouter(prefix="/api")


class PayGroup(BaseModel):
    name: str
    headcount: int
    payroll_usd: Decimal
    min_usd: Decimal
    p25_usd: Decimal
    median_usd: Decimal
    p75_usd: Decimal
    max_usd: Decimal


class PaySummary(BaseModel):
    group_by: GroupBy
    overall: PayGroup
    groups: list[PayGroup]


@router.get("/pay/summary", response_model=PaySummary)
def get_pay_summary(
    group_by: GroupBy,
    session: Annotated[Session, Depends(get_session)],
    matching: Annotated[Filters, Depends(filters)],
):
    return pay_summary(session, group_by, matching)
