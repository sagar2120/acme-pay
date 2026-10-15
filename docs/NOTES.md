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

Deployed to Render myself, with Claude Code running the CLI under my instructions. Gemini key is a Render secret only.
Measured again after the additions: still under 100 ms per request.

## Wed 14 Oct, evening
Three things found on the live site, none by the tests:
- The Gemini key was in the request address, so it showed up in the host
  logs. Moved to a header. Rotated the key.
- Google answered 503 once and the screen said "Request failed (500)" as if
  our app broke. Now: retry once, then a plain "busy, try again" message.
- "what do we pay in Pune by level" came back as Austin once. The model
  mis-picked. Now a city, team or level written in the question always wins
  over the model's pick; the model only fills what the question leaves open.

Speed: locally everything was under 60 ms so I had left out caching on
purpose. On the free host /api/health alone takes 0.85 s and the answers
page 1.9 s. Added one cache for the answers, cleared on any pay write.
Rewrote the summary to rank once and read all seven figures off that
ranking: 86 ms -> 57 ms locally even with percentiles added.

## Thu 15 Oct
Re-read the docs as an interviewer would. Two claims were too strong:
- "Postgres is a one-line switch" (Tue night). The connection is one setting,
  but the switch also needs the Postgres driver, migrations and a test run on
  Postgres. I have not done that run. Corrected in decisions.md.
- "Money is Decimal, never float". True in the code. SQLite has no exact
  decimal type: checked the seeded file, all 11,407 pay records are stored as
  integers because they are whole amounts, but an amount with cents would be
  stored as a float. Wrote it in known limits.
Also wrote down the cost of choosing FastAPI over Django: no built-in
migrations. Tables come from create_all, fine while the live site re-seeds on
every deploy, not fine for a real database.
