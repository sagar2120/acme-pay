"""Time the main API requests on 10,000 seeded employees, with and without the pay_record index.

Run: uv run python scripts/bench.py
"""

import os
import statistics
import time

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db import make_engine, make_session_factory
from app.main import create_app
from app.models import Base
from app.seed import seed

path = os.path.join(os.path.dirname(__file__), "bench.db")
if os.path.exists(path):
    os.remove(path)
engine = make_engine(f"sqlite:///{path}")
Base.metadata.create_all(engine)
factory = make_session_factory(engine)
with factory() as s:
    seed(s)
client = TestClient(create_app(factory))


def ms(url, n=20):
    client.get(url)
    t = []
    for _ in range(n):
        a = time.perf_counter()
        r = client.get(url)
        t.append((time.perf_counter() - a) * 1000)
        assert r.status_code == 200, r.text
    return statistics.median(t)


urls = [
    "/api/employees?sort=-pay_usd",
    "/api/employees?q=patel&location_id=1",
    "/api/pay/summary?group_by=location",
    "/api/pay/summary?group_by=level&department_id=1",
]
print("WITH index:", {u: round(ms(u), 1) for u in urls})
with engine.begin() as c:
    c.execute(text("DROP INDEX pay_record_newest_first"))
print("WITHOUT index:", {u: round(ms(u), 1) for u in urls})
print(client.get("/api/pay/summary?group_by=location").json()["groups"][:2])
