from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.models import LEVELS, Department, Location

router = APIRouter(prefix="/api")


@router.get("/options")
def get_options(session: Annotated[Session, Depends(get_session)]) -> dict:
    """Values for the filter dropdowns on both screens."""
    locations = session.execute(select(Location.id, Location.city).order_by(Location.city))
    departments = session.execute(select(Department.id, Department.name).order_by(Department.name))
    return {
        "locations": [{"id": id_, "name": city} for id_, city in locations],
        "departments": [{"id": id_, "name": name} for id_, name in departments],
        "levels": LEVELS,
    }
