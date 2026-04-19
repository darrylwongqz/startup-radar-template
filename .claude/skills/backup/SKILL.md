---
name: backup
description: Write a local tarball of DB + config + OAuth files to `backups/`. Wraps `uv run startup-radar backup [--no-secrets] [--db-only]`.
when_to_use: When the user says "backup", "/backup", "snapshot", "save a copy", or before a risky operation (schema change, migration, etc.). NEVER auto-invoke.
allowed-tools: [Bash]
---

# /backup — local snapshot

Wraps `uv run startup-radar backup`.

## Procedure

### 1. Ask about secrets posture FIRST

The default backup includes `token.json` and `credentials.json` — fine for local disaster recovery, dangerous if the tarball leaves the machine. ALWAYS ask before running:

> Are you keeping this backup local (personal recovery), or sharing/uploading it somewhere?
> - **local** → I'll include OAuth secrets so you can restore fully.
> - **sharing** → I'll pass `--no-secrets`; you'll have to re-do OAuth on restore.
> - **just the DB** → I'll pass `--db-only`; smallest tarball, no config or OAuth.

Skip the prompt only if the user already specified the posture in their request (e.g. "backup just the db" → `--db-only`).

### 2. Run

```bash
uv run startup-radar backup
```

…or:

```bash
uv run startup-radar backup --no-secrets
uv run startup-radar backup --db-only
```

### 3. Confirm

Report the tarball path under `backups/` and its size. Remind the user that `backups/` is gitignored — they need to copy it off-machine themselves if they want offsite redundancy.

## Constraints

- Don't skip the secrets prompt. The user might have habituated to "yes" answers; force the posture decision.
- Don't suggest committing the tarball — `backups/` is gitignored on purpose, and DBs in git history are bad.
- Don't `tar tf` the result to verify contents unless the user asks; the CLI's own success message is enough.
