# 07 — Screens (Pay answers and People)

## Prompts

> Decision: the screens live in ui/ with Vite + React + TypeScript + Ant Design. Two pages: Pay answers at / and People at /people, with a top menu "Pay answers · People" and the app name "ACME Pay". Theme: one primary colour #2F5D50 (muted green), compact size, no dark mode. Two helper functions, tested with Vitest: money.ts (Indian grouping for INR, normal grouping otherwise) and query.ts (build the query string, leaving out empty filters).

> People page: Ant Design Table with server-side paging, 50 per page; search that waits 300 ms after typing; Location, Department, Level filters; a drawer "Record a pay change for {name}" that shows the server's error message when a change is refused. Pay answers page: heading "What does ACME pay?", Group by selector, the same filters, one line with headcount, payroll and median, a table per group. Clicking a group opens People filtered to that group. No stat cards, no chart library.

## What Claude proposed

- Pinned stable versions (React 18, Ant Design 5, Vite 5) rather than the newest.
- A third tested helper, `filters.ts`, to read filters from the URL so a group
  on the answers page links to People, and a refresh keeps the view.
- A pay range line per group (lowest to highest, dot at the median, one shared
  USD scale) instead of the planned single median bar, because the spread is
  the point of a pay question.
- A small `/api/options` endpoint for the dropdowns (tested first).

## Caught along the way

- The level list was first placed in the web layer and imported by the seed:
  wrong direction. Moved to `models.py`.
- Checked every screen in a real browser with all 10,000 people. Links showed
  Ant Design's default blue instead of the app's green; fixed.

## What I changed and why

Asked directly whether the screens looked AI-generated before accepting them.
Approved the pay-range strip as the one distinctive element and the rule of
no stat-card row and no chart library. Checked the screenshots of both pages
before they were committed.
