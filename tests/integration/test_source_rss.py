"""RSS source integration tests.

feedparser uses `urllib.request` directly, not `requests`. vcrpy's stubs
don't reliably intercept that path (plan Phase 8 §5 Risk #1), so this file
monkeypatches `feedparser.parse` to return synthetic FeedParserDicts
instead of using cassettes. The contract under test is the same:
`RSSSource.fetch(cfg) -> list[Startup]` against the three canonical
shapes (populated feed, empty feed, malformed/bozo feed).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import feedparser
import pytest
import yaml

from startup_radar.config import AppConfig
from startup_radar.config.schema import RSSFeed
from startup_radar.sources import rss as rss_module
from startup_radar.sources.rss import RSSSource

EXAMPLE = Path(__file__).resolve().parents[2] / "config.example.yaml"


def _cfg() -> AppConfig:
    with open(EXAMPLE, encoding="utf-8") as f:
        return AppConfig.model_validate(yaml.safe_load(f))


@pytest.fixture
def rss_cfg() -> AppConfig:
    cfg = _cfg()
    cfg.sources.rss.enabled = True
    cfg.sources.rss.feeds = [RSSFeed(name="Example", url="https://example.test/funding.rss")]
    return cfg


def _feed(entries: list[dict[str, Any]]) -> feedparser.util.FeedParserDict:
    """Build a FeedParserDict mimicking feedparser.parse() output."""
    parsed = feedparser.util.FeedParserDict()
    parsed.entries = [feedparser.util.FeedParserDict(e) for e in entries]
    parsed.bozo = 0
    return parsed


def test_rss_happy_path(rss_cfg: AppConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feed with >=2 funding-shaped items → Startup rows with amount + company."""
    canned = _feed(
        [
            {
                "title": "Acme raises $5M Series A to reinvent widgets",
                "summary": "Acme, a widget startup, raised $5M Series A led by Sequoia.",
                "link": "https://example.test/acme",
            },
            {
                "title": "Globex secures $12M Series B",
                "summary": "Globex secured $12M Series B funding.",
                "link": "https://example.test/globex",
            },
            {
                "title": "Unrelated post about cats",
                "summary": "Not a funding item.",
                "link": "https://example.test/cats",
            },
        ]
    )
    monkeypatch.setattr(rss_module, "feedparser", type("M", (), {"parse": lambda _url: canned}))
    out = RSSSource().fetch(rss_cfg)
    assert len(out) == 2
    first = out[0]
    assert first.company_name == "Acme"
    assert first.source == "Example"
    assert first.amount_raised.startswith("$")
    assert first.funding_stage.lower().startswith("series")


def test_rss_empty_feed(rss_cfg: AppConfig, monkeypatch: pytest.MonkeyPatch) -> None:
    """Valid feed with zero entries → [] cleanly."""
    canned = _feed([])
    monkeypatch.setattr(rss_module, "feedparser", type("M", (), {"parse": lambda _url: canned}))
    assert RSSSource().fetch(rss_cfg) == []


def test_rss_fetch_exception_logs_and_returns_empty(
    rss_cfg: AppConfig,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """feedparser raises (e.g. malformed XML / network hiccup) → warn + []."""

    def _boom(_url: str) -> Any:
        raise RuntimeError("malformed feed")

    monkeypatch.setattr(rss_module, "feedparser", type("M", (), {"parse": staticmethod(_boom)}))
    caplog.set_level(logging.WARNING, logger="startup_radar.sources.rss")
    out = RSSSource().fetch(rss_cfg)
    assert out == []
    assert any(r.name.endswith("rss") and "fetch_failed" in r.message for r in caplog.records)
