# 12 — Found on the live site, fixed the same evening

Commits: be0fa21 .. 6e1bb0a

Everything here was found by using the deployed app, not by the tests, and
each fix went in test first.

| Seen | Cause | Fix |
| --- | --- | --- |
| "what do we pay in Pune by level" showed Austin | the model mis-picked the city | a city or level typed in the question wins over the model (3e1c238) |
| the Gemini key appeared in the host logs | it was sent in the request address; errors print the address | sent in the x-goog-api-key header; key rotated (248d8b9) |
| "Request failed (500)" when Google was busy | Google's 503 passed through as our 500 | retry, then a plain "busy, try again" 503 (248d8b9, a6729fe) |
| still busy on every try | the main model overloaded (503 every time, never 429) | fall back to a second model (f428822) |
| "senior people in Berlin" showed the People department | my typed-name rule matched the word "people" | that rule now covers cities and levels only; departments are the model's call (1f1dccc) |
| the test for that passed before the fix | test data had no People department | test seeds one, verified red against the old code (5d18a88) |
| answers page 1.9 s on the free host | 0.85 s is the host; ~1 s our query on a slow CPU | summary in one ranked pass (1accf17) and answers cached until pay changes (86c8b2b) |
| "what do we pay in Mumbai" refused with a generic message | the model correctly said unclear | the refusal now lists the known locations, departments and levels (67a27d0) |
| no way back after a question set filters; import button hard to find | — | clear + Show everything; chat panel; import button beside the heading (49c3a6b, 67a27d0, 6e1bb0a) |

## Prompts (abridged; the full text is in the commit messages)

> Push main to origin, wait for Render to be Live, then from this Mac time these with curl ... Then type "what do we pay in Pune by level" in the Ask box on the live site and tell me exactly what it shows.

> ... read the log and tell me which status code Google returned on the failed attempts (429 or 503). Do not print the key.

## What I changed and why

Reported that the live site felt slow; measuring it led to the one-pass
summary and the cache. Ran the live page and the README through an AI-content
checker and rejected the first "how I used Claude Code" text as reading
generated; it was rewritten in plain sentences. Decided not to let the model
guess what "senior" means: all levels are shown, highest first.
