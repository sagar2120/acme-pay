# Architecture

One service. The browser loads the React screens from FastAPI and calls `/api` on the same address. FastAPI reads and writes one SQLite file. Business rules sit in a module that knows nothing about the web or the database.

```mermaid
flowchart LR
    hr([HR manager<br/>browser]) -->|/ and /people| screens[React screens<br/>ui/ → app/static]
    hr -->|/api/...| api[FastAPI routers<br/>app/api/]
    api --> services[employees.py · pay.py · summary.py]
    services --> rules[rules.py<br/>pure pay rules]
    services --> db[(SQLite<br/>acme.db)]
    seed[seed.py<br/>10,000 people] -->|on first start| db
```

## Data model

Pay is a dated record, never a column on the employee. Current pay is the newest record for each person.

```mermaid
erDiagram
    location ||--o{ employee : "works at"
    department ||--o{ employee : "belongs to"
    employee ||--o{ pay_record : "is paid"
    fx_rate ||--o{ pay_record : "converts (by currency)"

    location { int id PK  string city  string country  string currency }
    department { int id PK  string name UK }
    employee { string id PK "ACME-2019-00412"  string full_name  string email UK  string job_title  string level "L1-L6"  int location_id FK  int department_id FK  date hire_date  bool is_active }
    pay_record { int id PK  string employee_id FK  decimal amount "local currency"  string currency  decimal amount_usd "fixed when saved"  date effective_from  string note }
    fx_rate { string currency PK  decimal usd_per_unit  date as_of }
```

Rules the database enforces itself: a pay record must belong to an existing employee (foreign key), and one employee cannot have two pay records on the same day (unique `employee_id, effective_from`).

## Where things live

| Path | Job |
| --- | --- |
| `app/rules.py` | Pay rules as pure functions: positive amount, location currency, not before hire, USD rounding |
| `app/pay.py` | Current pay (window function) and recording a pay change |
| `app/employees.py` | People list and detail; shared filters |
| `app/summary.py` | Pay answers: headcount, payroll, lowest, median, highest per group, in SQL |
| `app/seed.py` | The same 10,000 people every run |
| `app/api/` | HTTP layer only: request/response shapes; errors mapped to status codes once in `main.py` |
| `ui/src/pages/` | Pay answers and People screens |
| `tests/` | One file per module, named as the rules they check |
