"""SEC EDGAR source integration tests — cassette-backed, no live network.

EDGAR's request URL embeds today's date in `startdt`/`enddt`, so cassette
matching drops the query-string via `match_on=["method", "scheme", "host", "path"]`.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
import yaml

from startup_radar.config import AppConfig
from startup_radar.sources.sec_edgar import SECEdgarSource

EXAMPLE = Path(__file__).resolve().parents[2] / "config.example.yaml"
CASSETTE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "cassettes"


def _cfg() -> AppConfig:
    with open(EXAMPLE, encoding="utf-8") as f:
        return AppConfig.model_validate(yaml.safe_load(f))


@pytest.fixture
def edgar_cfg() -> AppConfig:
    cfg = _cfg()
    cfg.sources.sec_edgar.enabled = True
    cfg.sources.sec_edgar.industry_sic_codes = []
    cfg.sources.sec_edgar.lookback_days = 7
    return cfg


@pytest.mark.vcr(match_on=["method", "scheme", "host", "path"])
def test_sec_edgar_happy_path(edgar_cfg: AppConfig) -> None:
    """Cassette: sec_edgar/happy.yaml — real EDGAR search-index w/ >=2 Form D hits."""
    out = SECEdgarSource().fetch(edgar_cfg)
    assert len(out) >= 2
    # Parenthetical suffix stripping from display_names.
    assert all("(" not in s.company_name for s in out)
    assert all(s.source == "SEC EDGAR" for s in out)


@pytest.mark.vcr(match_on=["method", "scheme", "host", "path"])
def test_sec_edgar_empty(edgar_cfg: AppConfig) -> None:
    """Cassette: sec_edgar/empty.yaml — {"hits": {"hits": []}}."""
    assert SECEdgarSource().fetch(edgar_cfg) == []


@pytest.mark.vcr(match_on=["method", "scheme", "host", "path"])
def test_sec_edgar_http_500_logs_and_returns_empty(
    edgar_cfg: AppConfig, caplog: pytest.LogCaptureFixture
) -> None:
    """Cassette: sec_edgar/http_500.yaml — raise_for_status fires → warn + []."""
    caplog.set_level(logging.WARNING, logger="startup_radar.sources.sec_edgar")
    assert SECEdgarSource().fetch(edgar_cfg) == []
    assert any("fetch_failed" in r.message for r in caplog.records)


def test_cassette_headers_scrubbed() -> None:
    """The recorded UA must not be the real developer's identity."""
    cassette_path = CASSETTE_DIR / "sec_edgar" / "test_sec_edgar_happy_path.yaml"
    cassette = yaml.safe_load(cassette_path.read_text())
    for interaction in cassette["interactions"]:
        ua = interaction["request"]["headers"].get("User-Agent", [""])[0]
        assert "startup-radar-test" in ua, f"cassette leaks real UA: {ua!r}"
