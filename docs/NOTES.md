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

## Wed 14 Oct
Backend first, screens after, online by mid-afternoon. 28 commits by then,
every feature test first.

Things caught while checking, not by the tests:
- Seed amounts were not rounded to the nearest 1,000. quantize(Decimal("1000"))
  rounds to whole units, not thousands. Added a test, then fixed it.
- Summary test data saved pay before the employee existed; the foreign key
  refused it. The database rule was right, the test setup was wrong.
- The pay_record index I expected to help made no difference (41 vs 42 ms).
  The window function reads the whole table anyway. Wrote the real numbers.
- Links were Ant's default blue; the import drop zone filled the whole drawer.
  Both found by looking at the screens in a browser.

Incubyte's reply made percentiles, import and an LLM box optional. Decided to
add all three after the core was live, each on a condition: percentiles only
if read off the same ranking as the median; import only all-or-nothing with
every bad line reported; the question box only if the model can never
produce a number — it picks filters, SQL answers, unknown places are refused.

Deployed from Claude Code on the Mac. Gemini key is a Render secret only.
Measured again after the additions: still under 100 ms per request.
