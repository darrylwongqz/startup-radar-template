---
name: status
description: Print branch, version, last-run age, and DB row counts. Wraps `uv run startup-radar status`.
when_to_use: When the user says "status", "/status", "what's the state", "when did the pipeline last run?", or asks for a quick health snapshot. NEVER auto-invoke (the session-init hook already prints similar info).
allowed-tools: [Bash]
---

# /status — repo + DB snapshot

Wraps `uv run startup-radar status`.

## Procedure

### 1. Run

```bash
uv run startup-radar status
```

### 2. Interpret last-run age

`status` prints the age of the last scheduled run. If it's:

- **<24h** — fresh; just confirm and stop.
- **24h–48h** — getting stale; mention that a daily cron should be more frequent.
- **>48h** — actually stale; suggest `/run` to backfill, or check whether the GH Actions schedule is firing (`/data-branch-restore` will pull whatever the cloud has).
- **"(none)"** — pipeline has never run on this machine; suggest `/run` for a first run.

### 3. Interpret DB row counts

If all counts are zero, the DB is empty — suggest `/run` to populate it (or `/data-branch-restore` if they're on a fresh clone of a fork that's been running).

## Constraints

- Pure read; no side effects. Safe to invoke anytime.
- Don't auto-chain into `/run` — surface the suggestion, let the user decide.
