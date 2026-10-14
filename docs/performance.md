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
| Seed 10,000 employees | once | 0.2 s | |

## What this says

- Everything is 3-7x under the target, so nothing needs caching today.
- The index I planned made **no difference**. "Current pay" ranks every pay
  record with a window function, which reads the whole pay_record table
  whatever the index. At 11k rows that full read takes a few milliseconds.
- The answers are slower than the list because they rank pay twice (once
  for the totals, once for the median). Fine at this size.

## What I would change, and when

| When | Change | Why |
| --- | --- | --- |
| ~100k employees | Keep a `current_pay` table (or an `is_current` flag) updated in the same transaction as each pay change | Removes the full window scan from every request; the index then helps |
| ~100k employees | Keyset paging on the People list (`WHERE (full_name, id) > (:last_name, :last_id)`) | OFFSET slows down on deep pages |
| Several HR users writing | Postgres instead of SQLite (one setting) | SQLite allows one writer at a time |
| Answers page slow or hit often | Pre-computed `pay_summary` per group, refreshed on pay change | Answers change only when pay changes |
