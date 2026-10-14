import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, sessionmaker

from app.api import employees, options, pay, summary
from app.db import make_engine, make_session_factory
from app.models import Base
from app.pay import EmployeeNotFound, SamePayChangeDate
from app.rules import PayRuleError
from app.seed import seed

# Domain errors map to HTTP status codes here, and only here.
ERROR_STATUS = {
    EmployeeNotFound: 404,
    SamePayChangeDate: 409,
    PayRuleError: 422,
}
BUILT_SCREENS = Path(__file__).parent / "static"


def create_app(
    session_factory: sessionmaker[Session] | None = None,
    static_dir: Path | None = BUILT_SCREENS,
) -> FastAPI:
    """Tests pass their own in-memory database; the server opens DATABASE_URL on start."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if app.state.session_factory is None:
            app.state.session_factory = _open_database(
                os.environ.get("DATABASE_URL", "sqlite:///./acme.db")
            )
        yield

    app = FastAPI(title="ACME Pay", lifespan=lifespan)
    app.state.session_factory = session_factory

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(employees.router)
    app.include_router(pay.router)
    app.include_router(summary.router)
    app.include_router(options.router)

    for error, status in ERROR_STATUS.items():
        app.add_exception_handler(error, _responds_with(status))

    if static_dir is not None and static_dir.is_dir():
        _serve_screens(app, static_dir)

    return app


def _open_database(url: str) -> sessionmaker[Session]:
    engine = make_engine(url)
    Base.metadata.create_all(engine)
    factory = make_session_factory(engine)
    with factory() as session:
        seed(session)  # does nothing if people already exist
    return factory


def _serve_screens(app: FastAPI, static_dir: Path) -> None:
    """The built React screens. Any address outside /api gets index.html and React routes it."""
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def screens(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(status_code=404)
        return FileResponse(static_dir / "index.html")


def _responds_with(status: int):
    async def handler(_request: Request, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=status, content={"detail": str(error)})

    return handler


app = create_app()
