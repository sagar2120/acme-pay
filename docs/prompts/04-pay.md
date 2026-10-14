# 04 — Current pay and recording a pay change

Commits: 9c52261 (red), then the feat commit after it

## Prompts

> Decision: app/pay.py has:
> - current_pay_query(): the newest pay_record per employee, ordered by effective_from DESC then id DESC, using ROW_NUMBER() in SQL so it runs on SQLite and Postgres.
> - record_pay_change(session, employee_id, amount, effective_from, note): loads the employee, applies the rules from rules.py, converts with the fx_rate of the location's currency, and saves a NEW pay_record. It never edits an old record.
> create_app(session_factory) receives the database from outside so tests can pass an in-memory one.
> API: POST /api/employees/{id}/pay with body {amount, effective_from, note}. The currency comes from the employee's location, not from the request. Unknown employee 404; rule errors 422 with the rule's message; same-day duplicate 409.
> Tests first: tests/test_pay.py (newest record wins; same-day tie goes to the higher id; a new change leaves older records untouched) and in tests/test_api.py (201 on success, 404, 422, 409).

## What Claude proposed

Shared test fixtures in conftest (session factory, TestClient, one Pune
employee). Domain errors mapped to HTTP codes in one dictionary in main.py
instead of try/except in each endpoint.

## Changed from the plan

Dropped the "same-day tie goes to the higher id" test and the id tie-break:
the unique (employee_id, effective_from) constraint from step 1 makes a
same-day tie impossible, so the test could never fail. Added a test that a
back-dated change does not replace a newer one, which is the real risk.

## What I changed and why

Reviewed the decision and the diff; approved as proposed.
