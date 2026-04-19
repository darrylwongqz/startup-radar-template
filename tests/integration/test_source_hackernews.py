"""Hacker News source integration tests — cassette-backed, no live network."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
import yaml

from startup_radar.config import AppConfig
from startup_radar.sources.hackernews import HackerNewsSource

EXAMPLE = Path(__file__).resolve().parents[2] / "config.example.yaml"


def _cfg() -> AppConfig:
    with open(EXAMPLE, encoding="utf-8") as f:
        return AppConfig.model_validate(yaml.safe_load(f))


@pytest.fixture
def hn_cfg() -> AppConfig:
    """Minimal AppConfig for Hacker News with cassette-compatible queries."""
    cfg = _cfg()
    cfg.sources.hackernews.enabled = True
    cfg.sources.hackernews.queries = ["raised Series A"]
    cfg.sources.hackernews.lookback_hours = 48
    return cfg


@pytest.mark.vcr(match_on=["method", "scheme", "host", "path"])
def test_hackernews_happy_path(hn_cfg: AppConfig) -> None:
    """Cassette: hackernews/happy.yaml — Algolia response with >=3 company-pattern hits."""
    out = HackerNewsSource().fetch(hn_cfg)
    assert len(out) >= 3
    companies = {s.company_name for s in out}
    assert len(companies) == len(out)  # dedup via seen_titles
    assert any(s.funding_stage and s.amount_raised for s in out)


@pytest.mark.vcr(match_on=["method", "scheme", "host", "path"])
def test_hackernews_empty(hn_cfg: AppConfig) -> None:
    """Cassette: hackernews/empty.yaml — {"hits": []}."""
    assert HackerNewsSource().fetch(hn_cfg) == []


@pytest.mark.vcr(match_on=["method", "scheme", "host", "path"])
def test_hackernews_http_500_logs_and_returns_empty(
    hn_cfg: AppConfig, caplog: pytest.LogCaptureFixture
) -> None:
    """Cassette: hackernews/http_500.yaml — raise_for_status fires → warn + []."""
    caplog.set_level(logging.WARNING, logger="startup_radar.sources.hackernews")
    assert HackerNewsSource().fetch(hn_cfg) == []
    assert any("fetch_failed" in r.message for r in caplog.records)
