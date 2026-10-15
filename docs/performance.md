# Performance notes

Measured 14 Oct 2026 with `scripts/bench.py`: 10,000 seeded employees,
11,407 pay records, SQLite file database, FastAPI TestClient, median of 20
runs after one warm-up. Target from requirements.md: under 300 ms.

| Request | Time | With the pay_record (employee_id, effective_from) index | Without it |
| --- | --- | --- | --- |
| People, sorted by USD pay, highest first | page of 50 | 41 ms | 42 ms |
| People, search "patel" in Pune | page of 50 | 37 ms | 37 ms |
| Pay answers grouped by location | 6 groups | 86 ms | 86 ms |
| Pay answers grouped by level, one department | 6 groups | 77 ms | 77 ms |
| Pay answers by location, after percentiles were added and the query rewritten as one pass (14 Oct, later) | 6 groups | **57 ms** | |
| Pay answers by level, one department, same rewrite | 6 groups | **46 ms** | |
| Seed 10,000 employees | once | 0.2 s | |

## What this says

- Everything is 3-7x under the target, so nothing needs caching today.
- The index I planned made **no difference**. "Current pay" ranks every pay
  record with a window function, which reads the whole pay_record table
  whatever the index. At 11k rows that full read takes a few milliseconds.
- The first version of the answers ranked pay twice (totals, then median),
  and adding percentiles made that four passes. Rewritten as one ranked
  pass read with CASE expressions in a single GROUP BY: 86 ms became 57 ms
  with more figures, not fewer.

## On the free host (measured from a Mac in India, 14 Oct evening)

| Request | Seconds |
| --- | --- |
| /api/health (does no work) | 0.85 |
| /api/employees?page_size=50 | 1.55 |
| /api/pay/summary?group_by=location | 1.91 |

0.85 s for a request that does nothing is the host: a sleeping free
instance in Oregon with a fraction of a CPU, reached from India. The
remaining ~1 s on the summary is our query running on that slow CPU
(57 ms on a laptop). Answers change only when pay changes, so the summary
is now kept in memory per (grouping, filters) and cleared on every pay
write or import. Repeat views cost the host overhead only.

## What I would change, and when

| When | Change | Why |
| --- | --- | --- |
| ~100k employees | Keep a `current_pay` table (or an `is_current` flag) updated in the same transaction as each pay change | Removes the full window scan from every request; the index then helps |
| ~100k employees | Keyset paging on the People list (`WHERE (full_name, id) > (:last_name, :last_id)`) | OFFSET slows down on deep pages |
| Several HR users writing | Postgres instead of SQLite (connection setting, driver, migrations, a test run on Postgres) | SQLite allows one writer at a time |
| A second server process | Shared cache (Redis) instead of the in-process dict | The dict is per process; two processes would each recompute and could serve stale answers after the other's write |
