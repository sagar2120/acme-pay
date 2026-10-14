# 09 — 25th and 75th percentiles

Commits: 090af6e (red), 9fb5137 (green)

## Prompt

> Incubyte said percentiles are optional. Decision: add them, because they show the "typical range" (middle half) which HR quotes in offers. Nearest-rank method so a quartile is always a real person's pay. Same SQL ranking as the median; no second pass. On screen, a thicker band on the range strip and two columns. Tests first on the same 7 / 4 / 1 people, worked out by hand at the top of the test file.

## What Claude proposed

Reading both quartiles off the existing ROW_NUMBER ranking with two filtered
selects, so the median query did not change.

## What I changed and why

Incubyte said percentiles were optional; I decided to add them after the core
was live. Reviewed the hand-worked values in the test header. On the live
page I flagged the column title "Pay range, $0 to $386,000; band = middle
half" as clumsy; it became "Pay spread" with a one-line key under the heading.
