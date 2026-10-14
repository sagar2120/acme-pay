# ACME Pay

Salary management for ACME's HR manager: keep pay for 10,000 people across six cities correct, and answer "what do we pay?" in seconds, in one currency.

**Live:** https://acme-pay.onrender.com (free plan: the first visit after a quiet period can take up to a minute to wake up)
**Demo video (5 min):** _link added after recording_

## What it does

- **Pay answers** (home page): headcount, annual payroll and the lowest / 25th percentile / median / 75th percentile / highest pay in USD, grouped by location, department or level, with filters. A range strip per group shows the spread, with the middle half as a band and the median as a dot. Click a group to see those people.
- **Ask in plain English**: "what do we pay senior engineers in Pune?" The language model (Gemini) only translates the question into the page's own filters; it never sees or produces a number. The database answers, and the page says which filters were applied. Questions it cannot map, or places ACME does not have, are refused rather than guessed.
- **People**: search by name or email, filter, sort by name or pay, 50 per page.
- **Record a pay change**: a new dated record with a note; old records are never overwritten. Changes that break a rule (zero pay, a date before the hire date, two changes on one day) are refused with the reason.
- **Import pay changes from CSV**: every row is checked with the same rules; if any row fails, nothing is saved and every problem line is listed with its reason, so the file is fixed once and uploaded again.
- **Pay in local currency** (₹, $, €, £, S$), converted to USD with a fixed rate table, so cities can be compared.
- **Seed**: the same 10,000 realistic employees on every run.

What I chose to leave out, and why, is in [docs/requirements.md](docs/requirements.md): login, pay bands, live exchange rates. Import and the question box were optional in the brief; I added them because the import is the real replacement for the spreadsheet, and the question box could be built in a form that cannot invent a number.

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
uv run pytest            # 64 tests, under 1 second
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

Claude was my engineering partner; I set the direction, made the calls and checked the result.

- **Before any code**, I asked Incubyte six scoping questions (currency, salary history, login, analytics, import, timeline) and used their answers to fix the scope. Then the requirements, the glossary of words the project may use and the ten design decisions were written and committed first, so the code had something to be checked against.
- **Working rules** live in [CLAUDE.md](CLAUDE.md): one behaviour at a time, the failing test first, only glossary words, no new libraries without asking, rules in one module with no database import, aggregates in SQL.
- **Every feature went test first.** The commit history reads `test: … (red)` then `feat: …` for each one. The tests are the pay rules written down, not plumbing.
- **I made the product calls**: pay kept as dated records instead of a column; median as the headline figure; the pay ladder and city split for the seed data; adding percentiles, CSV import and the question box after Incubyte said they were optional, and the condition for the question box — the model may choose filters but may never produce a number.
- **What review caught** is recorded in [docs/prompts/](docs/prompts/) and [docs/NOTES.md](docs/NOTES.md): amounts not actually rounded to the nearest 1,000 although tests passed; test data saved before the employee it belonged to; an index that made no measurable difference, written down as such instead of claimed as a speed-up; a drop zone that pushed the import report off screen.
- **Deployment** was done with Claude Code on my Mac: the Render service was created from `render.yaml`, the health check verified, and the Gemini key set as a host secret, never in the repository.

## Known limits

- On Render's free plan the disk is reset on every deploy, so the live site re-seeds and pay changes made there do not survive a redeploy. Real use would point `DATABASE_URL` at a managed Postgres.
- No login: one trusted user, as agreed for this exercise.

## What I would do next

1. Login and roles before anyone other than the HR manager uses it.
2. A managed Postgres so pay changes on the live site survive a redeploy.
3. At ~100,000 people: keep current pay in its own table, updated with each pay change, and keyset paging on the People list.
