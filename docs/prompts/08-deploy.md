# 08 — One service, online

## Prompts

> Decision: one service. FastAPI serves the built UI at / and the API at /api. The database is a SQLite file at DATABASE_URL. On startup the tables are created and the seed runs if the database is empty. Deploy on Render's free plan. Test first: the screens are served for any address outside /api.

Deployed from Claude Code on my Mac:

> Deploy this repo to Render using the render.yaml in the repo root (one Docker web service, free plan, health check /api/health). ... Watch the deploy until it is Live or fails. If it fails, show me the last 30 lines of the build log and stop. Do not change any code. When Live, check /api/health and /api/pay/summary?group_by=location returns 6 groups, and give me the public URL.

## What Claude proposed

A two-stage Dockerfile (Node builds the screens, the Python image serves them)
instead of a Render native build, so the same image runs locally and live.
Database setup happens on server start only, so tests that pass their own
in-memory database never create a file.

## Checked

Before deploying, ran the exact `uv sync --frozen` step with the uv version in
the Dockerfile against the committed lock file. Live result: health 200, six
groups, 9,682 active people.

## What I changed and why

<!-- Sagar: write 1-3 lines in your own words. -->
