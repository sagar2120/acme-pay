# 01 — Tables

Commits: 7132cfa (red), 662f00a (green)

## Prompts

> Decision: the database has five tables in app/models.py, SQLAlchemy 2.0 style (Mapped / mapped_column):
> - location: id int PK, city, country, currency (3 letters)
> - department: id int PK, name unique
> - employee: id text PK like ACME-2019-00412, full_name, email unique, job_title, level (L1-L6), location_id FK, department_id FK, hire_date, is_active default true. Indexes on location_id, department_id, level, full_name.
> - pay_record: id int PK, employee_id FK, amount Numeric(14,2), currency, amount_usd Numeric(14,2), effective_from date, note nullable. Unique (employee_id, effective_from).
> - fx_rate: currency PK, usd_per_unit Numeric(18,8), as_of date.
> There is no salary column anywhere.
> app/db.py: make_engine(url) that turns on SQLite foreign keys, plus a session factory.
> tests/conftest.py: an in-memory SQLite session fixture.
> Test first, in tests/test_models.py:
> 1. a pay_record pointing at an employee that does not exist is rejected by the database
> 2. two pay_records for the same employee on the same date are rejected
> Write only the tests, run them, show me the failure, stop.

> Commit as "test: database rejects orphan and same-day pay records (red)". Then implement models.py and db.py with the smallest code that passes, run all tests, show me the diff.

> Commit as "feat: five tables; pay is a dated record, not a column"

## What Claude proposed

Two tests that expect IntegrityError, then the five tables as specified.
Two details it added that the prompt did not name: StaticPool for in-memory
SQLite (otherwise each session gets its own empty database), and naming the
unique constraint `one_pay_change_per_day` so the error says what rule broke.

## What I changed and why

Reviewed the decision and the diff; approved as proposed.
