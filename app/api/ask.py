from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.api.summary import PaySummary
from app.ask import MAX_QUESTION_CHARS, filters_from
from app.employees import Filters
from app.models import LEVELS, Department, Location
from app.summary import pay_summary

router = APIRouter(prefix="/api")


class QuestionIn(BaseModel):
    question: str = Field(min_length=3, max_length=MAX_QUESTION_CHARS)


class AnswerOut(BaseModel):
    filters: dict
    summary: PaySummary


@router.post("/pay/ask", response_model=AnswerOut)
def post_question(
    body: QuestionIn, request: Request, session: Annotated[Session, Depends(get_session)]
):
    locations = dict(session.execute(select(Location.city, Location.id)).all())
    departments = dict(session.execute(select(Department.name, Department.id)).all())
    options = {"locations": locations, "departments": departments, "levels": LEVELS}

    picked = request.app.state.interpreter(
        body.question,
        {"locations": list(locations), "departments": list(departments), "levels": LEVELS},
    )
    filters = filters_from(picked, options)
    summary = pay_summary(
        session,
        filters["group_by"],
        Filters(
            location_id=filters["location_id"],
            department_id=filters["department_id"],
            level=filters["level"],
        ),
    )
    names = {
        "location_name": next(
            (n for n, i in locations.items() if i == filters["location_id"]), None
        ),
        "department_name": next(
            (n for n, i in departments.items() if i == filters["department_id"]), None
        ),
    }
    return {"filters": {**filters, **names}, "summary": summary}
