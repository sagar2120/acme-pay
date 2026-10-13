# Build notes

## Tue 13 Oct, night
First hour on docs, not code. Decided SQLite for everything: one writer, 10k
rows, and I do not want a second service to babysit on a free host. Median query
will be written so Postgres is a one-line switch.

Biggest call: pay as dated records. Incubyte said current pay is enough. Kept
history because the real pain in Excel is overwriting; it is one table and one
query. Not building history charts.

Wrote the glossary before any code so Claude Code cannot drift into
user/salary/utils naming.
