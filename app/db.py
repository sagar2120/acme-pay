from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


def make_engine(url: str) -> Engine:
    if url in ("sqlite://", "sqlite:///:memory:"):
        # An in-memory SQLite database lives inside one connection;
        # StaticPool makes every session share that connection.
        engine = create_engine(url, poolclass=StaticPool, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(url)

    if engine.dialect.name == "sqlite":
        event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    # SQLite ignores foreign keys unless this is switched on per connection.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
