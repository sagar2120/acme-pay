# 06 — Pay answers (summary)

Commits: 2a1ee82 (red), 22b80fb (green), f08fbd6 (performance notes)

## Prompts

> Decision: app/summary.py with GET /api/pay/summary?group_by=location|department|level, plus the same filters as the list. For each group: name, headcount, payroll_usd (sum), min_usd, median_usd, max_usd; plus one overall row. Active employees and current pay only.
> The median is computed in SQL: ROW_NUMBER and COUNT per group, then the middle row, or the average of the two middle rows. No Python loop over employees.
> Tests first in tests/test_summary.py with small hand-made data: a group of 7 people whose median I can check by hand; a group of 4 (even count); a group of 1; an inactive employee who must not count.

> Seed 10,000 employees into a temporary SQLite file. Time GET /api/employees?sort=-pay_usd and GET /api/pay/summary?group_by=location, 20 runs each, and report the median in milliseconds. Then tell me which index would help most, add it, and measure again. Write both before/after numbers to docs/performance.md with one line on what changed.

## What Claude proposed

Expected medians written at the top of the test file so a reader can check
them by hand. Groups sorted highest median first.

## Caught along the way

- The first test run errored, not failed: the test data saved pay records
  before their employees, and the foreign key (from step 1) refused them.
  Fixed the test setup; the database rule was right.
- The planned index made no measurable difference (41 vs 42 ms). Wrote that
  down as measured instead of claiming a speed-up, with the reason (the
  window function reads every pay record anyway) and what would actually
  help at 100k employees.

## What I changed and why

Reviewed the decision and the diff; approved as proposed.
