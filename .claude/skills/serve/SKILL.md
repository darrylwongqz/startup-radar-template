---
name: serve
description: Open the Startup Radar Streamlit dashboard in the user's browser. Wraps `uv run startup-radar serve`.
when_to_use: When the user says "serve", "/serve", "open the dashboard", "show me the dashboard", "launch the UI", or similar. NEVER auto-invoke.
allowed-tools: [Bash]
---

# /serve — Streamlit dashboard

Wraps `uv run startup-radar serve`.

## Procedure

### 1. Run in the background

Streamlit blocks the foreground. Use `run_in_background: true`:

```bash
uv run startup-radar serve
```

### 2. Tell the user the URL

Default URL: `http://localhost:8501`. Tell the user it's opening, and that Streamlit will print a "Local URL" line in the background output once it's ready.

### 3. Cleanup

When the user says "stop the dashboard" or similar, kill the background process. They can also `Ctrl-C` from the Bash output panel, or run:

```bash
pkill -f 'streamlit run'
```

## Constraints

- ALWAYS background. Foregrounding hangs the conversation.
- Don't pass `--port` or `--reload` unless the user asks.
- Don't try to open the URL in a browser via `open` / `xdg-open` — Streamlit already does that by default; double-opening confuses the user.
