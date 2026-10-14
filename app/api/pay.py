from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.pay import record_pay_change

router = APIRouter(prefix="/api")


class PayChangeIn(BaseModel):
    amount: Decimal = Field(description="Annual gross base pay, in the location's currency")
    effective_from: date
    note: str | None = Field(default=None, max_length=500)


class PayRecordOut(BaseModel):
    id: int
    amount: Decimal
    currency: str
    amount_usd: Decimal
    effective_from: date
    note: str | None


@router.post("/employees/{employee_id}/pay", status_code=201, response_model=PayRecordOut)
def post_pay_change(
    employee_id: str,
    change: PayChangeIn,
    session: Annotated[Session, Depends(get_session)],
):
    return record_pay_change(
        session, employee_id, change.amount, change.effective_from, change.note
    )
