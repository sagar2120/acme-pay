# Decisions

Each entry: what I decided, what else I considered, why, and when I would
change it. Dated as made.

## 1. SQLite for tests, local and live (2026-10-13)
Considered: Postgres on a free host, MySQL.
Why: one writer (the HR manager), 10k rows, nothing to host or keep alive, the
same engine in tests and production, and the brief itself suggests it.
Cost: SQLite has no exact decimal type. Whole amounts (all seeded pay) are
stored as integers, but an amount with paise or cents would be stored as a
float; the code reads values back as Decimal. No wrong figure at this size,
but sums are not guaranteed exact at the database level.
Change when: a second writer appears, or before real payroll money. The
connection is one setting; the switch also needs the Postgres driver, Alembic
migrations and a full test run on Postgres. The median query uses standard SQL
(ROW_NUMBER, CASE) but has not been run on Postgres yet.

## 2. FastAPI + SQLAlchemy 2.0 + Pydantic v2 (2026-10-13)
Considered: Django + DRF, Flask.
Why: the role is Python; FastAPI validates input and documents the API for
free, and TestClient makes API tests cheap. Django's main strengths (login,
admin, the plugin ecosystem) are out of scope here.
Cost: no built-in migrations; tables are created at start-up with create_all.
Fine while the live database is rebuilt on every deploy; Alembic is needed
before a real database.
Change when: login, roles and several HR users are needed. Django gives
those built in.

## 3. One deployable service (2026-10-13)
Considered: separate API on Render + UI on Vercel.
Why: one URL, no CORS, one deploy that can fail during a demo. FastAPI serves
the built React bundle from `/`.
Change when: real traffic; the bundle moves to a CDN.

## 4. Pay is a dated record, not a column (2026-10-13)
Considered: `salary` column on employee (Incubyte said current pay is enough).
Why: overwriting pay is the actual Excel pain. A `pay_record` table with
`effective_from` gives history and an audit trail for one table and one
window-function query. No history analytics or timeline UI in v1.
Change when: n/a.

## 5. Store local amount, compute USD at write time (2026-10-13)
Considered: convert at read time.
Why: aggregates over 10k rows must not multiply per row per query, and a report
run today must give the same number tomorrow. Trade-off: a rate change leaves
old USD figures as they were; a recompute command is the escape hatch.
Change when: finance asks for "today's rate" views → versioned `fx_rate`.

## 6. Answers = filters + SQL-side aggregates; median, not average (2026-10-13)
Considered: an LLM question box; averages.
Why: pay figures must be exact and reproducible; pay is right-skewed so the
average misleads. GROUP BY + window functions in SQL; Python never loops over
employees.
Change when: 100k+ rows → pre-computed `pay_summary` table.

## 7. No login, no import, no bands (2026-10-13)
See requirements.md. Each is a real feature; each would take time from the core
being right. Order after v1: import, then login.

## 8. React + Vite + TypeScript + Ant Design (2026-10-13)
Considered: shadcn/ui + Tailwind, MUI.
Why: dense internal tool; Ant's Table gives server-side paging, sorting and
filters out of the box; one theme token sets the colour. Two screens only.
Change when: a design system exists.

## 9. Tests: rules first, plumbing second (2026-10-13)
Pure rule tests (no DB) → service tests on in-memory SQLite → a few API tests →
two UI pure-function tests. 25–35 tests, under 5 s. No coverage theatre.

## 10. Flat modules, no services/repositories/utils tree (2026-10-13)
Why: six endpoints; a layered tree is ceremony. Each module is named for its
job. Split when a second writer or a second area (leave, benefits) arrives.
