"""Deterministic demo data: the same 10,000 ACME employees on every run.

Pay follows a level ladder per location, so the answers page shows a real
shape instead of noise. Every pay record goes through the same rules as a
pay change made in the app.
"""

import random
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from app.models import Department, Employee, FxRate, Location, PayRecord
from app.rules import check_pay_change, to_usd

RATES_AS_OF = date(2026, 10, 1)
USD_PER_UNIT = {
    "INR": Decimal("0.0120"),
    "EUR": Decimal("1.08"),
    "GBP": Decimal("1.27"),
    "SGD": Decimal("0.74"),
    "USD": Decimal("1"),
}

LEVELS = ["L1", "L2", "L3", "L4", "L5", "L6"]
LEVEL_SHARE = [15, 25, 28, 18, 10, 4]

# Annual base pay in local currency, L1 to L6.
BASE_PAY = {
    "Pune": ("India", "INR", 35, [600_000, 1_000_000, 1_800_000, 2_800_000, 4_200_000, 6_500_000]),
    "Bengaluru": (
        "India",
        "INR",
        25,
        [660_000, 1_100_000, 2_000_000, 3_100_000, 4_600_000, 7_200_000],
    ),
    "Austin": ("United States", "USD", 12, [75_000, 95_000, 125_000, 155_000, 190_000, 240_000]),
    "Berlin": ("Germany", "EUR", 10, [48_000, 58_000, 72_000, 88_000, 105_000, 130_000]),
    "London": ("United Kingdom", "GBP", 10, [40_000, 52_000, 68_000, 85_000, 105_000, 135_000]),
    "Singapore": ("Singapore", "SGD", 8, [60_000, 80_000, 105_000, 135_000, 170_000, 220_000]),
}

DEPARTMENTS = {
    "Engineering": "Software Engineer",
    "Product": "Product Owner",
    "Design": "Product Designer",
    "Sales": "Account Executive",
    "Marketing": "Marketing Specialist",
    "Finance": "Financial Analyst",
    "People": "People Partner",
    "Operations": "Operations Specialist",
}
DEPARTMENT_SHARE = [38, 8, 5, 15, 9, 7, 6, 12]
TITLE_PREFIX = {"L1": "Associate ", "L2": "", "L3": "Senior ", "L4": "Lead ", "L5": "Principal "}

NAMES = {
    "India": (
        "Aarav Aditi Ananya Arjun Diya Ishaan Kavya Meera Nikhil Pooja Rahul Riya "
        "Rohan Saanvi Sneha Tanvi Varun Vihaan Yash Zara Asha Kiran Dev Neha".split(),
        "Patel Shah Mehta Iyer Nair Reddy Sharma Gupta Joshi Desai Kulkarni Rao "
        "Menon Pillai Bhat Chopra Kapoor Malhotra Verma Trivedi".split(),
    ),
    "United States": (
        "James Emily Michael Sarah David Jessica Daniel Ashley Ryan Megan Tyler "
        "Lauren Jacob Hannah Ethan Olivia Noah Ava Logan Chloe".split(),
        "Smith Johnson Williams Brown Garcia Miller Davis Martinez Wilson Anderson "
        "Taylor Moore Jackson Lee Harris Clark Lewis Walker".split(),
    ),
    "Germany": (
        "Lukas Anna Leon Laura Felix Lena Jonas Julia Paul Sophie Maximilian "
        "Hannah Tim Lea Niklas Marie".split(),
        "Müller Schmidt Schneider Fischer Weber Meyer Wagner Becker Schulz Hoffmann "
        "Koch Richter Klein Wolf".split(),
    ),
    "United Kingdom": (
        "Oliver Amelia Harry Isla George Emily Jack Ava Charlie Grace Thomas "
        "Freya Alfie Poppy William Evie".split(),
        "Smith Jones Taylor Brown Williams Wilson Evans Thomas Roberts Walker "
        "Wright Hughes Green Hall".split(),
    ),
    "Singapore": (
        "Wei Ling Jun Hui Ming Xin Rajesh Priya Ahmad Nur Daniel Rachel Ethan "
        "Chloe Marcus Shu".split(),
        "Tan Lim Lee Ng Ong Wong Goh Chua Koh Teo Chan Yeo Kumar Rahman".split(),
    ),
}

FIRST_HIRE = date(2015, 1, 1)
LAST_HIRE = date(2026, 6, 30)
OUTLIER_SHARE = 0.03
RAISE_SHARE = 0.15
LEAVER_SHARE = 0.03


def seed(session: Session, count: int = 10_000) -> int:
    """Fill an empty database. Returns the number of employees added (0 if not empty)."""
    if session.scalar(select(func.count()).select_from(Employee)):
        return 0

    rng = random.Random(42)
    session.add_all(
        FxRate(currency=c, usd_per_unit=r, as_of=RATES_AS_OF) for c, r in USD_PER_UNIT.items()
    )
    locations = [
        Location(city=city, country=country, currency=currency)
        for city, (country, currency, _, _) in BASE_PAY.items()
    ]
    departments = [Department(name=name) for name in DEPARTMENTS]
    session.add_all(locations + departments)
    session.flush()

    employees, pay_records = [], []
    used_emails: set[str] = set()
    hire_span = (LAST_HIRE - FIRST_HIRE).days

    for seq in range(1, count + 1):
        location = rng.choices(locations, weights=[v[2] for v in BASE_PAY.values()])[0]
        department = rng.choices(departments, weights=DEPARTMENT_SHARE)[0]
        level = rng.choices(LEVELS, weights=LEVEL_SHARE)[0]
        hire_date = FIRST_HIRE + timedelta(days=rng.randrange(hire_span))
        first, last = (rng.choice(pool) for pool in NAMES[location.country])
        employee_id = f"ACME-{hire_date.year}-{seq:05d}"

        employees.append(
            {
                "id": employee_id,
                "full_name": f"{first} {last}",
                "email": _unique_email(first, last, used_emails),
                "job_title": _job_title(level, department.name),
                "level": level,
                "location_id": location.id,
                "department_id": department.id,
                "hire_date": hire_date,
                "is_active": rng.random() >= LEAVER_SHARE,
            }
        )

        amount = _starting_pay(rng, location.city, level)
        pay_records.append(
            _pay_record(employee_id, amount, location.currency, hire_date, hire_date)
        )

        raise_date = hire_date + timedelta(days=365)
        if raise_date <= RATES_AS_OF and rng.random() < RAISE_SHARE:
            raised = _round_to_thousand(amount * Decimal(str(rng.uniform(1.05, 1.15))))
            pay_records.append(
                _pay_record(employee_id, raised, location.currency, raise_date, hire_date)
            )

    session.execute(insert(Employee), employees)
    session.execute(insert(PayRecord), pay_records)
    session.commit()
    return count


def _starting_pay(rng: random.Random, city: str, level: str) -> Decimal:
    base = BASE_PAY[city][3][LEVELS.index(level)]
    factor = max(0.6, rng.gauss(1.0, 0.12))
    if rng.random() < OUTLIER_SHARE:
        factor *= 1.6
    return _round_to_thousand(Decimal(base) * Decimal(str(factor)))


def _round_to_thousand(amount: Decimal) -> Decimal:
    return (amount / 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 1000


def _pay_record(employee_id, amount, currency, effective_from, hire_date) -> dict:
    check_pay_change(
        amount=amount,
        currency=currency,
        location_currency=currency,
        effective_from=effective_from,
        hire_date=hire_date,
    )
    return {
        "employee_id": employee_id,
        "amount": amount,
        "currency": currency,
        "amount_usd": to_usd(amount, USD_PER_UNIT[currency]),
        "effective_from": effective_from,
        "note": "Hired" if effective_from == hire_date else "Annual review",
    }


def _job_title(level: str, department: str) -> str:
    if level == "L6":
        return f"Head of {department}"
    return f"{TITLE_PREFIX[level]}{DEPARTMENTS[department]}"


def _unique_email(first: str, last: str, used: set[str]) -> str:
    stem = f"{first}.{last}".lower().replace("ü", "ue")
    email, n = f"{stem}@acme.example", 1
    while email in used:
        n += 1
        email = f"{stem}{n}@acme.example"
    used.add(email)
    return email
