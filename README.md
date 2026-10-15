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

I used Claude Code as the engineer who types. I decided what to build, what not to build, and checked what came out.

Before starting I sent Incubyte six questions about scope and waited for the answers. Then I wrote down the requirements, the list of words the project is allowed to use (glossary.md) and the ten design decisions, and committed those before any code existed.

CLAUDE.md is the rule sheet Claude reads every time. The main rules: do one small thing at a time, write the failing test first, use only the glossary words, do not add libraries without asking, keep the pay rules in one file with no database code in it, do the maths in SQL.

The commit history shows the order: a `test: ... (red)` commit, then the `feat:` commit that makes it pass. The tests are the pay rules written down.

The decisions were mine. Pay is stored as dated records, not as a salary column. The headline number is the median, not the average. I approved the salary table used to make the 10,000 fake people. When Incubyte said percentiles, CSV import and an AI question box were optional, I added all three, with one condition for the question box: the model may only choose filters, it may never produce a number.

I also set the rules for how the app must behave under load and bad input: every number on the answers page is computed in SQL in a single pass, never by looping over employees in Python; each page is one query, with the total count from the same filtered query; page size, search length, upload size and pay amount all have hard limits; sort and group-by only accept fixed values; money is Decimal, never float; the database enforces the integrity rules itself so two simultaneous requests cannot slip past a Python check; imports save all rows or none; every error has a name and a status code mapped in one place, with no catch-all try/except; the browser gets nosniff, no-framing and same-origin-referrer headers; the AI key lives only on the host. I did not add a cache at first: on a laptop every request was under 60 ms, so a cache would have been complexity for nothing. Then I measured on the free host and saw 1.9 s for the answers page, with 0.85 s of that being the host itself. So I cached the one thing that only changes when pay changes: the answers, cleared on every pay write or import. Measure first, then cache. The numbers and what I would change at 100,000 people are in docs/performance.md.

Things found by checking, not by the tests, are written in docs/NOTES.md and docs/prompts/: amounts were not really rounded to the nearest 1,000; test data was saved before the employee existed; an index I expected to help made no difference, so I wrote that down instead of claiming a speed-up; the first Gemini model name was closed to new keys; a question about Pune came back as Austin, so now a city typed in the question always wins.

I deployed it to Render on macOS, signed in with my own account, with Claude Code running the Render CLI under my instructions. I set the Gemini key as a secret on the host; it is not in the repository.

## Known limits

- On Render's free plan the disk is reset on every deploy, so the live site re-seeds and pay changes made there do not survive a redeploy. Real use would point `DATABASE_URL` at a managed Postgres.
- No login: one trusted user, as agreed for this exercise.

## What I would do next

1. Login and roles before anyone other than the HR manager uses it.
2. A managed Postgres so pay changes on the live site survive a redeploy.
3. At ~100,000 people: keep current pay in its own table, updated with each pay change, and keyset paging on the People list.
