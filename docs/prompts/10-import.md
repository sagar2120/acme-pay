# 10 — CSV import of pay changes

Commits: b1fad25 (red), 2b988fe (green), e337429 (screen)

## Prompt

> Incubyte said import is a stretch goal. Decision: build it properly or not at all. Rules: every row is checked with the same rules as a single pay change; if any row fails, nothing is saved and every bad line is reported with its number and reason; a date already in the database or repeated inside the file is an error; file limit 2 MB / 20,000 rows; wrong header refused before any row is read. Tests first for each of those.

## What Claude proposed

Loading employees, rates and existing dates in three queries up front
instead of one query per row; a downloadable template so the columns are
never guessed.

## Caught in review

The first version reported a repeated date inside the file with the same
wording as a date already in the database. Separated them so HR knows
whether to fix the file or the database.

## What I changed and why

Incubyte called import a stretch goal and the first plan left it out; I
decided to add it because it is the actual replacement for the spreadsheet.
Approved the all-or-nothing rule for payroll data. After using the live page I
said the import button was hard to find among the filters; it moved beside the
People heading.
