# ACME Pay — rules for Claude Code

You are the typist. I make every design decision. If a decision is missing,
ask me one question and stop; never pick a default silently.

## Words
Use only the words in docs/glossary.md. Never introduce: user, staff, salary,
compensation, grade, band, role, utils, helpers, base, manager, handler.

## Process
- One behaviour at a time. Write the failing test first, run it, show me the
  failure, stop. Then write the smallest code that passes, run the full suite,
  show the diff.
- Never edit a file I did not name in the prompt.
- No try/except around whole functions. Raise the named errors from
  app/rules.py; the API layer maps them to HTTP responses in one place.
- No docstrings unless the reason is non-obvious. No comments that repeat code.
- No new libraries without asking. Stable versions only.
- Business rules live in app/rules.py and must not import SQLAlchemy.
- Aggregations run in SQL (GROUP BY, window functions), never in Python loops.

## Commands
- uv run pytest -q          (must stay under 5 seconds)
- uv run ruff check . && uv run ruff format .
- cd ui && pnpm test

## Layout
app/ (main.py, db.py, models.py, rules.py, employees.py, pay.py, summary.py,
seed.py, api/) · tests/ · ui/ · docs/
