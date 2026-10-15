# 11 — Plain-English questions (Gemini)

Commits: 0e6eb58 (red), b4af2fb (green), b539cdb (screen)

## Prompt

> Incubyte said an LLM interface is optional "if you can justify the added complexity". Decision: add it only in a form where it cannot invent a number. The model's one job is to turn the question into filters the page already has (group_by, location, department, level), returning strict JSON with temperature 0. The database answers. A place or team ACME does not have is refused, not guessed. No key → 503 with a plain sentence, rest of the app unaffected. The model is injected so tests use a fake and never call the network. 500-character limit on questions.

## What Claude proposed

Passing Gemini the actual lists of locations, departments and levels in the
prompt and enforcing a response schema, so it can only choose from what
exists; mapping names to ids on our side and refusing unknown ones.

## Why not let the model answer directly

Pay numbers must be exact and repeatable. A model that writes SQL or quotes
figures can be wrong confidently. Here it can only pick filters, and the
page shows the same table it always shows.

## What I changed and why

Incubyte said an LLM interface was optional; I decided to add one. I also
proposed using Gemini for live exchange rates, and dropped that after weighing
that a model can invent numbers and the brief asked for static rates. On the
live site I reported a question about Pune answered as Austin, asked for a
clear button, and then asked for a chat panel at the bottom right instead of
an inline box; it was built that way, on the condition that each reply stays
the database's own summary.
