# Glossary — the only words this project uses

Code, screens, commits and docs all use these words. Nothing else.

| Thing | Call it | Never | Why |
| --- | --- | --- | --- |
| A person on payroll | `employee` (code), "person" (screens) | user, staff, worker | HR says employee; the "user" is the HR manager |
| Where someone works | `location` (city, country, currency) | country, office, region | Pay differs by city; the currency belongs to the location |
| What someone is paid | `pay_record` (amount, currency, amount_usd, effective_from, note) | salary, compensation | Shorter, and "record" says there is history |
| Pay right now | `current_pay` (always a query, never a column) | salary column | Derived from the newest record, so it cannot go stale |
| Seniority | `level` L1–L6 | grade, band | ACME has no bands; a level is a plain label |
| Job | `job_title` | position, role, designation | "role" collides with login roles |
| Team | `department` | team, org unit | The brief says department |
| Rate table | `fx_rate` (currency, usd_per_unit, as_of) | exchange_rates | Standard finance abbreviation |
| Employee ID | `ACME-YYYY-NNNNN` text key | auto-number | Stable, carries hire year, hides row counts |

Banned words anywhere in code: user, staff, salary, compensation, grade, band,
role, utils, helpers, base, manager, handler.

## Screen text

| Element | Text |
| --- | --- |
| App name | ACME Pay |
| Menu | Pay answers · People |
| Home heading | What does ACME pay? |
| Group selector | Group by: Location / Department / Level |
| Big numbers | Headcount · Annual payroll (USD) · Median pay (USD) |
| Row action | Record a pay change |
| Side panel title | Record a pay change for {name} |
| Side panel fields | Annual amount · Currency (fixed by location) · Effective from · Note |
| Main button | Save pay change |
| Empty state | No people match these filters. |

## Endpoints

```
GET  /api/employees            list: q, location, department, level, sort, page, page_size
GET  /api/employees/{id}       one person, current pay, pay history
POST /api/employees/{id}/pay   record a pay change
GET  /api/pay/summary          group_by + same filters → headcount, payroll_usd, min, median, max
```
