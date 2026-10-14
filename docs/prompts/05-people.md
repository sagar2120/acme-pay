# 05 — People list

Commits: ea2622a (red), then the feat commit after it

## Prompts

> Decision: app/employees.py with GET /api/employees and GET /api/employees/{id}.
> List filters: q (name or email, case-insensitive), location_id, department_id, level. sort is one of name, -name, pay_usd, -pay_usd; anything else is refused with 422. page default 1, page_size default 50, max 200.
> Response {items, total, page, page_size}. Each item: id, full_name, job_title, level, location city, department name, current pay amount, currency and amount_usd. One query for the page, never one query per row.
> Detail: the employee plus pay history, newest first.
> Tests first in tests/test_employees.py: total counts all filtered rows, not just the page; page_size above 200 is refused; an unknown sort is refused; search matches email; items carry the current pay.

## What Claude proposed

Filters in one shared function (`active_matching`) so the pay summary in
step 6 filters exactly the same way. Fixed sort values as a `Literal` type so
FastAPI refuses anything else before it reaches the database.

## Decided during the step

Leavers (is_active = false) are hidden from the list, matching the pay
summary. Their detail page still works by ID, so history is not lost.
Added a test that sorting by USD compares across currencies (a Berlin
€88k person ranks above a Pune ₹20 L person).

## What I changed and why

Reviewed the decision and the diff; approved as proposed.
