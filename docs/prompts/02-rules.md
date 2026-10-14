# 02 — Pay rules

Commits: 5f8de13 (red), a6b758b (green)

## Prompts

> Decision: business rules live in app/rules.py as pure functions with no SQLAlchemy import. Named errors, all subclasses of PayRuleError:
> - PayNotPositive: amount must be greater than 0
> - CurrencyMismatch: the pay currency must equal the employee's location currency
> - PayChangeBeforeHire: effective_from cannot be before hire_date
> Also to_usd(amount, usd_per_unit) returning a Decimal rounded half-up to 2 places.
> Tests in tests/test_rules.py, one per rule, named as sentences, e.g. test_pay_change_before_hire_date_is_rejected, test_usd_conversion_rounds_half_up_to_cents. Plain dates and Decimals, no database.
> Write only the tests, run them, show me the failure, stop.

> Commit red, implement with the smallest code that passes, run all tests, show me the diff. Then commit as "feat: pay rules as pure functions with named errors".

## What Claude proposed

One `check_pay_change(...)` function that runs the three rules in order, plus
`to_usd`. Tests build one valid change and vary a single field each, plus a
boundary test (pay change on the hire date itself is allowed) and a rounding
case where half-up and banker's rounding give different answers (12.345).

## What I changed and why

Reviewed and approved. Later I questioned whether tests like "a pay change
before the hire date is rejected" were too obvious to be worth writing. Kept
them: the point is not to tell me the rule, it is that a future change to
record_pay_change cannot silently break it without a red test.
