from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.pay_import import ImportFileError, import_pay_changes

router = APIRouter(prefix="/api")

MAX_FILE_BYTES = 2 * 1024 * 1024  # 20,000 rows is well under 2 MB


class RowErrorOut(BaseModel):
    model_config = {"from_attributes": True}

    line: int
    employee_id: str
    error: str


class ImportOut(BaseModel):
    saved: int
    errors: list[RowErrorOut] = []


@router.post("/pay/import", status_code=201, response_model=ImportOut)
async def post_pay_import(file: UploadFile, session: Annotated[Session, Depends(get_session)]):
    content = await file.read(MAX_FILE_BYTES + 1)
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="The file is larger than 2 MB.")
    try:
        result = import_pay_changes(session, content)
    except ImportFileError as problem:
        raise HTTPException(status_code=422, detail=str(problem)) from problem
    if result.errors:
        # Nothing was saved; the report says which lines to fix.
        return JSONResponse(
            status_code=422, content=ImportOut(saved=0, errors=result.errors).model_dump()
        )
    return result
