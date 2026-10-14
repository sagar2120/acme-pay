"""Pay answers, checked against medians worked out by hand.

All three cities pay in USD (rate 1) so the expected numbers are easy to read.
Austin, 7 people:  10 20 30 40 50 60 1000  -> median 40   (odd count: middle value)
Denver, 4 people:  10 20 30 100            -> median 25   (even count: mean of middle two)
Boston, 1 person:  70                      -> median 70
Plus a leaver in Austin paid 5000, who must not count anywhere.
Whole company, 12 people: 10 10 20 20 30 30 | 40 50 60 70 100 1000 -> median 35
"""

from datetime import date
from decimal import Decimal

import pytest

from app.models import Department, Employee, FxRate, Location, PayRecord

PAY_IN_THOUSANDS = {
    "Austin": [10, 20, 30, 40, 50, 60, 1000],
    "Denver": [10, 20, 30, 100],
    "Boston": [70],
}


@pytest.fixture
def company(session):
    session.add(FxRate(currency="USD", usd_per_unit=Decimal("1"), as_of=date(2026, 10, 1)))
    engineering, sales = Department(name="Engineering"), Department(name="Sales")
    seq = 0

    def hire(location, thousands, active=True):
        nonlocal seq
        seq += 1
        employee_id = f"ACME-2020-{seq:05d}"
        session.add(
            Employee(
                id=employee_id,
                full_name=f"Person {seq}",
                email=f"person{seq}@acme.example",
                job_title="Engineer",
                level="L3" if thousands < 50 else "L5",
                location=location,
                department=engineering if seq % 2 else sales,
                hire_date=date(2020, 1, 1),
                is_active=active,
            )
        )
        session.flush()  # the employee must exist before its pay record
        amount = Decimal(thousands * 1000)
        session.add(
            PayRecord(
                employee_id=employee_id,
                amount=amount,
                currency="USD",
                amount_usd=amount,
                effective_from=date(2020, 1, 1),
            )
        )

    locations = {}
    for city, pay in PAY_IN_THOUSANDS.items():
        locations[city] = Location(city=city, country="United States", currency="USD")
        for thousands in pay:
            hire(locations[city], thousands)
    hire(locations["Austin"], 5000, active=False)
    session.commit()
    return {city: loc.id for city, loc in locations.items()}


def summary(client, **params):
    response = client.get("/api/pay/summary", params={"group_by": "location", **params})
    assert response.status_code == 200
    return response.json()


def by_name(body):
    return {g["name"]: g for g in body["groups"]}


def test_median_of_an_odd_sized_group_is_the_middle_value(client, company):
    assert by_name(summary(client))["Austin"]["median_usd"] == "40000.00"


def test_median_of_an_even_sized_group_is_the_mean_of_the_middle_two(client, company):
    assert by_name(summary(client))["Denver"]["median_usd"] == "25000.00"


def test_a_group_of_one_has_that_persons_pay_as_its_median(client, company):
    assert by_name(summary(client))["Boston"]["median_usd"] == "70000.00"


def test_each_group_reports_headcount_payroll_lowest_and_highest(client, company):
    austin = by_name(summary(client))["Austin"]

    assert (austin["headcount"], austin["payroll_usd"]) == (7, "1210000.00")
    assert (austin["min_usd"], austin["max_usd"]) == ("10000.00", "1000000.00")


def test_people_who_have_left_are_not_counted(client, company):
    overall = summary(client)["overall"]

    assert overall["headcount"] == 12
    assert overall["max_usd"] == "1000000.00"


def test_the_whole_company_median_is_taken_across_all_groups(client, company):
    assert summary(client)["overall"]["median_usd"] == "35000.00"


def test_groups_come_highest_median_first(client, company):
    assert [g["name"] for g in summary(client)["groups"]] == ["Boston", "Austin", "Denver"]


def test_filters_apply_before_grouping(client, company):
    body = summary(client, group_by="level", location_id=company["Denver"])

    assert {g["name"]: g["headcount"] for g in body["groups"]} == {"L5": 1, "L3": 3}


def test_an_unknown_grouping_is_refused(client, company):
    assert client.get("/api/pay/summary", params={"group_by": "salary"}).status_code == 422
