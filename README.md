# ACME Pay

Salary management for ACME's HR manager: keep pay for 10,000 people correct,
and answer "what do we pay?" across six cities in one currency.

**Live:** https://acme-pay.onrender.com (free plan: the first load after a quiet
period can take up to a minute) · **Demo video:** _link_

The decision that shaped everything else: **pay is a dated record, not a
column.** The spreadsheets this replaces lose history every time someone types
over a salary. Here a pay change always adds a new record with an effective
date; current pay is simply the newest one. It cost one table and one query.

## What it does

- **Pay answers** (home page). Group by location, department or level, filter,
  and see headcount, annual payroll, and the lowest, median and highest pay per
  group in USD, with the spread drawn as a line so you see more than one number.
  Click a group to see those people.
- **People.** 10,000 employees, 50 per page, search by name or email, filter,
  sort by name or pay. Record a pay change from any row; the app refuses changes
  that break a rule (zero pay, wrong currency, a date before the person was
  hired, two changes on one day) and says why.
- Pay is stored in each location's currency and converted to USD with a fixed
  rate table, so every report gives the same answer tomorrow.

## Run it locally

Needs Python 3.10+ with [uv](https://docs.astral.sh/uv/), and Node 20+.

```bash
uv sync
uv run uvicorn app.main:app --reload     # API on :8000; creates and seeds acme.db on first start
cd ui && npm ci && npm run dev           # screens on http://localhost:5173
```

Or the same image that runs live: `docker build -t acme-pay . && docker run -p 8000:8000 acme-pay`
then open http://localhost:8000.

## Tests

```bash
uv run pytest          # 48 tests, under 1 second
cd ui && npm test      # 10 tests
```

Tests are named as rules (`test_pay_change_before_hire_date_is_rejected`) and
were written before the code they cover; the commit history shows each
`test: ... (red)` followed by its `feat:`. The median tests use small groups
whose answers are worked out by hand at the top of `tests/test_summary.py`.

## How it is built

FastAPI + SQLAlchemy + SQLite, React + TypeScript + Ant Design, deployed as one
Docker service on Render that serves both the API and the screens. Business
rules are pure functions in `app/rules.py`; aggregates (including the median)
run in SQL, never as Python loops over employees.

Read these first:

- [`docs/requirements.md`](docs/requirements.md): scope, and what I left out on purpose
- [`docs/decisions.md`](docs/decisions.md): the ten main decisions, with the alternatives
- [`docs/performance.md`](docs/performance.md): measured timings on 10,000 people, and what changes at 100,000
- [`docs/glossary.md`](docs/glossary.md): the words used everywhere, from tables to buttons

## How I used Claude

I wrote the requirements, glossary and decisions before any code. Claude
(Claude Code and a planning chat) typed the code, test first, one behaviour per
commit. `CLAUDE.md` holds the standing rules I gave it. `docs/prompts/` records,
for each step, the decision prompt, what Claude proposed, and what was caught
or changed, including a rounding bug the tests missed, a test that wrote data
in the wrong order, and a planned index that turned out to make no difference.

## Known limits

- **Live data resets on redeploy.** Render's free plan has no persistent disk,
  so the live site re-seeds on each deploy and pay changes made there are lost.
  Fine for a demo; production would set `DATABASE_URL` to Postgres.
- **No login.** One trusted HR manager, agreed with Incubyte. It is the first
  thing to add before anyone else uses it.
- **No import.** The seed stands in for migrating the spreadsheets; a real CSV
  import (row-by-row validation, all-or-nothing save) is the next feature.

## What I would do next

1. CSV import with a per-row error report.
2. Login, then a department-head view limited to their own team.
3. At ~100k employees: keep current pay in its own table, keyset paging on
   People, and Postgres. See `docs/performance.md`.
