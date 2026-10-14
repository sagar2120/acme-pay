from datetime import date
from decimal import Decimal

import pytest

from app.models import Department, Employee, FxRate, Location
from app.pay import record_pay_change


@pytest.fixture
def team(session):
    """Four people: three in Pune, one in Berlin; one Pune person has left."""
    session.add_all(
        [
            FxRate(currency="INR", usd_per_unit=Decimal("0.0120"), as_of=date(2026, 10, 1)),
            FxRate(currency="EUR", usd_per_unit=Decimal("1.08"), as_of=date(2026, 10, 1)),
        ]
    )
    pune = Location(city="Pune", country="India", currency="INR")
    berlin = Location(city="Berlin", country="Germany", currency="EUR")
    engineering, sales = Department(name="Engineering"), Department(name="Sales")
    people = [
        ("ACME-2021-00001", "Asha Patel", pune, engineering, "L3", True, "1800000"),
        ("ACME-2022-00002", "Rohan Mehta", pune, sales, "L2", True, "1000000"),
        ("ACME-2020-00003", "Lena Fischer", berlin, engineering, "L4", True, "88000"),
        ("ACME-2019-00004", "Kiran Rao", pune, engineering, "L5", False, "4200000"),
    ]
    for employee_id, name, location, department, level, active, _ in people:
        first, last = name.lower().split()
        session.add(
            Employee(
                id=employee_id,
                full_name=name,
                email=f"{first}.{last}@acme.example",
                job_title="Engineer",
                level=level,
                location=location,
                department=department,
                hire_date=date(2019, 1, 1),
                is_active=active,
            )
        )
    session.commit()
    for employee_id, *_, amount in people:
        record_pay_change(session, employee_id, Decimal(amount), date(2019, 1, 1))
    record_pay_change(session, "ACME-2021-00001", Decimal("2000000"), date(2025, 4, 1), "Promotion")
    return {"pune": pune.id, "berlin": berlin.id, "engineering": engineering.id}


def test_the_list_returns_one_page_and_the_total_of_all_active_matches(client, team):
    body = client.get("/api/employees", params={"page_size": 2}).json()

    assert len(body["items"]) == 2
    assert body["total"] == 3


def test_people_who_have_left_are_not_listed(client, team):
    ids = [p["id"] for p in client.get("/api/employees").json()["items"]]

    assert "ACME-2019-00004" not in ids


def test_filters_narrow_the_total_not_just_the_page(client, team):
    body = client.get(
        "/api/employees", params={"location_id": team["pune"], "department_id": team["engineering"]}
    ).json()

    assert [p["full_name"] for p in body["items"]] == ["Asha Patel"]
    assert body["total"] == 1


def test_search_matches_email_ignoring_case(client, team):
    body = client.get("/api/employees", params={"q": "LENA.FISCH"}).json()

    assert [p["full_name"] for p in body["items"]] == ["Lena Fischer"]


def test_each_person_shows_current_pay_in_local_currency_and_usd(client, team):
    asha = client.get("/api/employees", params={"q": "asha"}).json()["items"][0]

    assert (asha["pay_amount"], asha["pay_currency"], asha["pay_usd"]) == (
        "2000000.00",
        "INR",
        "24000.00",
    )


def test_sorting_by_usd_pay_compares_across_currencies(client, team):
    body = client.get("/api/employees", params={"sort": "-pay_usd"}).json()

    assert [p["full_name"] for p in body["items"]] == ["Lena Fischer", "Asha Patel", "Rohan Mehta"]


@pytest.mark.parametrize("params", [{"page_size": 201}, {"sort": "salary"}, {"page": 0}])
def test_out_of_range_paging_and_unknown_sorts_are_refused(client, team, params):
    assert client.get("/api/employees", params=params).status_code == 422


def test_one_person_comes_with_pay_history_newest_first(client, team):
    body = client.get("/api/employees/ACME-2021-00001").json()

    assert body["location"] == "Pune"
    assert [r["amount"] for r in body["pay_history"]] == ["2000000.00", "1800000.00"]


def test_an_unknown_person_is_404(client, team):
    assert client.get("/api/employees/ACME-2021-99999").status_code == 404
