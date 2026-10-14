"""Bulk pay changes from a CSV file: every row is checked, and nothing is saved unless all pass."""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

from app.models import PayRecord

HEADER = "employee_id,amount,effective_from,note\n"


def upload(client, rows: str, filename="pay.csv"):
    return client.post(
        "/api/pay/import", files={"file": (filename, (HEADER + rows).encode(), "text/csv")}
    )


def saved_records(session):
    return session.scalar(select(func.count()).select_from(PayRecord))


def test_a_good_file_saves_every_row_and_reports_the_count(client, session, asha):
    response = upload(
        client,
        "ACME-2021-00001,1900000,2023-04-01,Annual review\nACME-2021-00001,2100000,2024-04-01,\n",
    )

    assert response.status_code == 201
    assert response.json() == {"saved": 2, "errors": []}
    assert saved_records(session) == 2


def test_one_bad_row_means_nothing_is_saved(client, session, asha):
    response = upload(
        client, "ACME-2021-00001,1900000,2023-04-01,ok\nACME-2021-00001,0,2024-04-01,zero pay\n"
    )

    assert response.status_code == 422
    assert saved_records(session) == 0


def test_every_problem_row_is_reported_with_its_line_number(client, asha):
    rows = (
        "ACME-2021-00001,1900000,2023-04-01,fine\n"
        "ACME-2021-99999,1900000,2023-04-01,unknown person\n"
        "ACME-2021-00001,1900000,2020-01-01,before hire\n"
        "ACME-2021-00001,abc,2023-05-01,not a number\n"
        "ACME-2021-00001,1900000,2023-04-01,same day as line 2\n"
    )
    body = upload(client, rows).json()

    assert [e["line"] for e in body["errors"]] == [3, 4, 5, 6]
    assert "No employee with id ACME-2021-99999" in body["errors"][0]["error"]
    assert "before hire date" in body["errors"][1]["error"]
    assert "amount" in body["errors"][2]["error"]
    assert "same effective_from" in body["errors"][3]["error"]


def test_a_date_already_in_the_database_is_a_problem_row(client, session, asha):
    session.add(
        PayRecord(
            employee_id=asha.id,
            amount=Decimal("1800000"),
            currency="INR",
            amount_usd=Decimal("21600"),
            effective_from=date(2023, 4, 1),
        )
    )
    session.commit()

    body = upload(client, "ACME-2021-00001,1900000,2023-04-01,duplicate\n").json()

    assert "already has a pay change on 2023-04-01" in body["errors"][0]["error"]


def test_a_file_with_the_wrong_columns_is_refused_before_any_row_is_read(client, asha):
    response = client.post(
        "/api/pay/import", files={"file": ("pay.csv", b"name,salary\nAsha,100\n", "text/csv")}
    )

    assert response.status_code == 422
    assert "employee_id, amount, effective_from" in response.json()["detail"]


def test_a_file_that_is_not_text_is_refused(client, asha):
    response = client.post(
        "/api/pay/import", files={"file": ("pay.csv", b"\xff\xfe\x00binary", "text/csv")}
    )

    assert response.status_code == 422
