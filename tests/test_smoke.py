"""Phase 0 smoke tests — placeholder so `make test` exits 0.

Real coverage lands in Phase 4 (vcrpy fixtures + per-source tests).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_models_importable() -> None:
    from models import JobMatch, Startup  # noqa: F401


def test_dedup_strips_legal_suffixes() -> None:
    """Phase 0 #2: 'OpenAI' and 'Open AI Inc.' must dedupe to the same key."""
    from main import _normalize_company

    assert _normalize_company("OpenAI") == _normalize_company("Open AI Inc.")
    assert _normalize_company("Acme Corp") == _normalize_company("acme")
    assert _normalize_company("WeWork") == _normalize_company("We Work")
    assert _normalize_company("Foo Labs LLC") == _normalize_company("Foo")


def test_oauth_scopes_unified() -> None:
    """Phase 0 #3: Gmail and Sheets must share the same SCOPES list."""
    from sinks.google_sheets import SCOPES as sheets_scopes
    from sources.gmail import SCOPES as gmail_scopes

    assert set(gmail_scopes) == set(sheets_scopes)
    assert "https://www.googleapis.com/auth/gmail.readonly" in gmail_scopes
    assert "https://www.googleapis.com/auth/spreadsheets" in gmail_scopes


def test_rss_socket_timeout_set() -> None:
    """Phase 0 #4: RSS module must set a socket-level timeout at import."""
    import socket

    import sources.rss  # noqa: F401

    assert socket.getdefaulttimeout() is not None
    assert socket.getdefaulttimeout() <= 30
