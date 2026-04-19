---
name: run
description: Run the Startup Radar discovery pipeline once. Wraps `uv run startup-radar run`.
when_to_use: When the user says "run", "/run", "run the pipeline", "scan", "find new startups", or any natural-language request to fetch fresh signals. NEVER auto-invoke.
allowed-tools: [Bash]
---

# /run — discovery pipeline

Wraps `uv run startup-radar run [--scheduled]`.

## Procedure

### 1. Pick the mode

Default: foreground run (`uv run startup-radar run`). Pass `--scheduled` only if the user mentions cron, scheduling, automation, "as if it were running on a schedule", or asks for the unattended mode (file logging + 15-min timeout + stdout-redirect).

### 2. Run

```bash
uv run startup-radar run
```

…or, for scheduled mode:

```bash
uv run startup-radar run --scheduled
```

### 3. Interpret the output

- **Exit 0, new candidates found:** tell the user how many new rows landed, and suggest `/serve` to browse them.
- **Exit 0, zero new candidates:** that's normal on quiet news days — say so. Don't report it as failure.
- **Exit non-zero:** surface the last 20 lines of stderr, and suggest `/doctor` to triage.

## Constraints

- Don't pass `--once` or other flags the user didn't ask about.
- Don't tail logs/ unless the user asks; the foreground command already prints to stdout.
- Don't follow up with `/serve` unless the user asked, but it's fine to mention.
