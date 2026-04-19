"""PRAGMA user_version migrator.

Walks ``NNNN_*.sql`` files in ``migrations/``, applies any above the
database's current ``user_version`` inside one transaction each, bumps the
pragma after success. No down-migrations (``docs/CRITIQUE_APPENDIX.md`` §4).
"""

from __future__ import annotations

import logging
import re
import sqlite3
from pathlib import Path

_FILE_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")


def _discover(migrations_dir: Path) -> list[tuple[int, Path]]:
    out: list[tuple[int, Path]] = []
    for p in sorted(migrations_dir.glob("*.sql")):
        m = _FILE_RE.match(p.name)
        if not m:
            raise ValueError(f"bad migration filename: {p.name}")
        out.append((int(m.group(1)), p))
    for i, (v, _) in enumerate(out, start=1):
        if v != i:
            raise ValueError(f"expected migration {i:04d}, found {v:04d}")
    return out


def apply_pending(
    conn: sqlite3.Connection,
    migrations_dir: Path,
    *,
    logger: logging.Logger | None = None,
) -> list[int]:
    log = logger or logging.getLogger(__name__)
    (current,) = conn.execute("PRAGMA user_version").fetchone()
    applied: list[int] = []
    for version, path in _discover(migrations_dir):
        if version <= current:
            continue
        sql = path.read_text(encoding="utf-8")
        try:
            with conn:
                conn.executescript(sql)
                conn.execute(f"PRAGMA user_version = {version}")
        except sqlite3.Error:
            log.exception("migration.failed", extra={"version": version, "file": path.name})
            raise
        log.info("migration.applied", extra={"version": version, "file": path.name})
        applied.append(version)
    return applied
