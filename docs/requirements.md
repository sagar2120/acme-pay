# ACME Pay — what we are building and what we are not

ACME's HR manager keeps pay for about 10,000 people in spreadsheets, one per
country, in local currencies. Two things go wrong: edits overwrite history with
no trace, and any question from leadership ("what do we pay senior engineers in
Pune?") means an afternoon of pivot tables and manual currency maths.

**Goal:** one web app, one trusted user (the HR manager), where a pay change is
recorded safely and pay questions are answered in seconds, across countries, in
one currency.

## In scope

- **Pay answers (home page).** Pick a grouping (location, department, level) and
  filters; see headcount, annual payroll in USD, lowest, median and highest pay
  per group. Median, not average: pay is lopsided and the average is pulled up by
  a few senior people.
- **People.** Find anyone by name or email, filter by location / department /
  level, sort, open a person and record a pay change with an effective date and
  a note.
- **Pay in local currency**, converted to USD with a static exchange-rate table
  that HR controls. Annual gross base pay only.
- **Seed:** 10,000 realistic people across 6 locations and 8 departments, the
  same data every run.

## Out of scope, on purpose

- **Login and roles.** One persona, confirmed with Incubyte. First thing to add
  before anyone other than the HR manager uses it.
- **CSV / Excel import.** The seed stands in for migration here. A correct
  import needs per-row validation, an error report and all-or-nothing saving;
  that is a feature of its own, and I would rather ship a smaller app that is
  right. First item after v1.
- **Chat / LLM question box.** Pay numbers must be exact and repeatable. The
  filters already answer the questions. An LLM adds cost, latency and a
  prompt-injection surface and solves no pain the HR manager stated.
- **Pay bands and band charts.** ACME has no band structure; inventing one
  would produce confident but arbitrary numbers.
- **Live exchange rates, payroll runs, payslips, tax, bonus, equity.** Other
  systems' jobs; this app is the record of base pay they would read from.

## Assumptions

- Everyone has one location and is paid in that location's currency.
- Amounts are annual, whatever the local pay frequency.
- A rate change does not rewrite old USD figures (reports stay reproducible);
  a recompute command exists for when HR wants that.
- Employee IDs are stable text (`ACME-<hire year>-<5 digits>`) and never reused.

## Non-functional

- People list and pay answers respond in under 300 ms on 10,000 people.
- Tests run in under 5 seconds, no network, no randomness.
- Deployed as one service; the first request after idle on a free tier can take
  ~30 seconds.
