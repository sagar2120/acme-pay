# ACME Pay

Salary management for ACME's HR manager: keep pay for 10,000 people across six cities correct, and answer "what do we pay?" in seconds, in one currency.

**Live:** https://acme-pay.onrender.com (free plan: the first visit after a quiet period can take up to a minute to wake up)
**Demo video (5 min):** _link added after recording_

## What it does

- **Pay answers** (home page): headcount, annual payroll and the lowest / median / highest pay in USD, grouped by location, department or level, with filters. A thin line per group shows the spread of pay, not just one number. Click a group to see those people.
- **People**: search by name or email, filter, sort by name or pay, 50 per page.
- **Record a pay change**: a new dated record with a note; old records are never overwritten. Changes that break a rule (zero pay, a date before the hire date, two changes on one day) are refused with the reason.
- **Pay in local currency** (₹, $, €, £, S$), converted to USD with a fixed rate table, so cities can be compared.
- **Seed**: the same 10,000 realistic employees on every run.

What I chose to leave out, and why, is in [docs/requirements.md](docs/requirements.md): login, CSV import, an LLM question box, pay bands, live exchange rates.

## Run it locally

Needs Python 3.10+ with [uv](https://docs.astral.sh/uv/), and Node 20+.

```bash
# backend (creates and seeds acme.db on first start)
uv sync
uv run uvicorn app.main:app --reload          # http://localhost:8000/api/health

# screens, in a second terminal
cd ui && npm ci && npm run dev                # http://localhost:5173
```

Or the whole thing as it runs online: `docker build -t acme-pay . && docker run -p 8000:8000 acme-pay`, then open http://localhost:8000.

## Tests

```bash
uv run pytest            # 48 tests, under 1 second
cd ui && npm test        # 10 tests
```

Tests are named as the rules they check, for example `test_pay_change_before_hire_date_is_rejected` and `test_median_of_an_even_sized_group_is_the_mean_of_the_middle_two`. The median tests use small groups whose answers are worked out by hand at the top of `tests/test_summary.py`.

## How it is built

One FastAPI service serves both the API and the built React screens, backed by one SQLite file. Diagrams: [docs/architecture.md](docs/architecture.md).

The three decisions that shaped it (all ten are in [docs/decisions.md](docs/decisions.md)):

1. **Pay is a dated record, not a salary column.** Overwriting pay is the spreadsheet problem this replaces. Current pay is the newest record, found with one window-function query.
2. **USD is fixed when a pay record is saved**, from a static rate table. Reports give the same answer tomorrow as today, and totals over 10,000 people do not re-convert every row.
3. **Answers are computed in SQL**, median included, so Python never loops over employees. Median, not average, because pay is lopsided.

Measured speed on 10,000 people: 37–86 ms per request, against a 300 ms target. Details, and what would change at 100,000 people: [docs/performance.md](docs/performance.md).

## How I used Claude Code

- I wrote the requirements, the glossary of words to use and the decisions before any code, and gave Claude Code standing rules in [CLAUDE.md](CLAUDE.md): it types, I decide; test first; only glossary words.
- Every feature went test first, then code: the commit history shows a `test: … (red)` commit before each `feat:`.
- The prompts for each step, what Claude proposed and what was changed are in [docs/prompts/](docs/prompts/). Examples of what review caught: pay was not actually rounded to the nearest 1,000 even though tests passed; test data saved pay before the employee existed; a planned index made no measurable difference, so the performance notes say so.

## Known limits

- On Render's free plan the disk is reset on every deploy, so the live site re-seeds and pay changes made there do not survive a redeploy. Real use would point `DATABASE_URL` at a managed Postgres.
- No login: one trusted user, as agreed for this exercise.

## What I would do next

1. CSV import with per-row validation and an error report.
2. Login and roles before anyone other than the HR manager uses it.
3. At ~100,000 people: keep current pay in its own table, updated with each pay change, and keyset paging on the People list.
