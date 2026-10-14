from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker

from app.api import employees, pay, summary
from app.pay import EmployeeNotFound, SamePayChangeDate
from app.rules import PayRuleError

# Domain errors map to HTTP status codes here, and only here.
ERROR_STATUS = {
    EmployeeNotFound: 404,
    SamePayChangeDate: 409,
    PayRuleError: 422,
}


def create_app(session_factory: sessionmaker[Session] | None = None) -> FastAPI:
    app = FastAPI(title="ACME Pay")
    app.state.session_factory = session_factory

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(employees.router)
    app.include_router(pay.router)
    app.include_router(summary.router)

    for error, status in ERROR_STATUS.items():
        app.add_exception_handler(error, _responds_with(status))

    return app


def _responds_with(status: int):
    async def handler(_request: Request, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=status, content={"detail": str(error)})

    return handler


app = create_app()
