---
name: doctor
description: Validate config, credentials, DB path, and (optionally) per-source network reachability. Wraps `uv run startup-radar doctor [--network]`.
when_to_use: When the user says "doctor", "/doctor", "check my setup", "diagnose", "is everything ok?", or after a failure they want triaged. NEVER auto-invoke.
allowed-tools: [Bash]
---

# /doctor — env / config / credential / source healthchecks

Wraps `uv run startup-radar doctor [--network]`.

## Procedure

### 1. Pick the mode

Default: fast (no `--network`). Adds network probes ONLY if the user explicitly says "deep", "full", "network", "check the feeds are reachable", or similar.

### 2. Run

```bash
uv run startup-radar doctor
```

…or:

```bash
uv run startup-radar doctor --network
```

### 3. Translate the output

Doctor exits 0 if everything is green, 1 if anything is broken. For exit 1, walk the user through each FAIL line in plain English:

- **Missing `config.yaml`** → suggest `/setup-radar`.
- **Missing `credentials.json` / `token.json` for an enabled source** → tell the user which source, and that they need to re-do the OAuth setup (handled in `/setup-radar`).
- **DB path not writable** → check perms on the `output.sqlite.path` directory.
- **Source healthcheck failed** → could be transient; suggest re-running with `--network` if they used fast mode, or `/run` to see the actual error.

For exit 0, just say "all green" and move on.

## Constraints

- Default to fast mode. `--network` is opt-in; it hits real endpoints and is rate-limited (SEC EDGAR especially).
- Don't try to fix the issues yourself — surface them and let the user (or `/setup-radar`) resolve.
