# 03 — Seed data

Commits: ee1740b (red), 07ac012 (green)

## Prompts

> Decision: app/seed.py fills the database with the same 10,000 employees every run, using random.Random(42).
> - 6 locations: Pune INR, Bengaluru INR, Berlin EUR, London GBP, Austin USD, Singapore SGD, with fixed fx_rate rows as of 2026-10-01.
> - 8 departments: Engineering, Product, Design, Sales, Marketing, Finance, People, Operations.
> - Levels L1-L6. A base annual pay per level per location, in local currency, as a readable table constant at the top of seed.py. Each person gets base x a factor from a normal distribution (mean 1, sd 0.12), rounded to the nearest 1,000. 3% get x1.6 as deliberate outliers.
> - Each employee gets one pay_record on their hire_date; 15% also get a raise record one year later.
> - IDs ACME-<hire year>-<5-digit sequence>. Emails firstname.lastname@acme.example.
> - seed(session, count=10000) does nothing if employees already exist. Insert in bulk in one transaction.
> Before writing any code, show me the base-pay table you propose so I can approve or change it.

Proposed table (approved as-is): Pune L3 ≈ ₹18 lakh, Austin L3 ≈ $125k, full table in `BASE_PAY` in app/seed.py. Headcount Pune 35%, Bengaluru 25%, Austin 12%, Berlin 10%, London 10%, Singapore 8%. Same pay for the same level in every department (kept simple on purpose).

## What Claude proposed

Bulk insert of dicts in one transaction, location-appropriate name pools,
emails with a numeric suffix on clashes (asha.patel2@), 3% leavers so the
"active only" rule in the summary has something to exclude, and every seeded
record passing `check_pay_change` so seed data obeys the same rules as the app.

## Caught in review

Rounding to the nearest 1,000 did not work: `quantize(Decimal("1000"))` keeps
exponent 0, so it rounded to whole units. The four tests passed anyway.
Added `test_every_amount_is_a_round_thousand_like_a_real_offer` (failed),
then fixed the rounding. Checked medians on 10,000: Pune L3 ₹18.09 L,
Austin L3 $126k, London L3 £69k — matches the table.

## What I changed and why

Approved the proposed base-pay table (Pune L3 about ₹18 lakh, Austin L3 about
$125k), the city split, and the simpler option of the same pay per level in
every department, before any seed code was written.
