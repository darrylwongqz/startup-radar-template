.PHONY: help install install-dev test lint format typecheck ci serve run doctor clean

PYTHON ?= python3
PIP    ?= $(PYTHON) -m pip

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS=":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## Install runtime deps from requirements.txt
	$(PIP) install -r requirements.txt

install-dev: install  ## Install runtime + dev deps (pytest, ruff, mypy)
	$(PIP) install -e ".[dev,google]" || $(PIP) install pytest pytest-cov ruff mypy vcrpy

test:  ## Run pytest
	$(PYTHON) -m pytest

lint:  ## Run ruff check
	$(PYTHON) -m ruff check .

format:  ## Auto-format with ruff
	$(PYTHON) -m ruff format .

format-check:  ## Check formatting without writing
	$(PYTHON) -m ruff format --check .

typecheck:  ## Run mypy on typed modules
	$(PYTHON) -m mypy

ci: lint format-check typecheck test  ## Full local CI: lint + format + typecheck + test

serve:  ## Start the Streamlit dashboard
	$(PYTHON) -m streamlit run app.py

run:  ## Run the discovery pipeline once
	$(PYTHON) main.py

doctor:  ## Quick environment check (Phase 3 will replace with `startup-radar doctor`)
	@$(PYTHON) --version
	@test -f config.yaml && echo "config.yaml: ok" || echo "config.yaml: MISSING (copy from config.example.yaml)"
	@test -f startup_radar.db && echo "DB exists" || echo "DB not yet created"

clean:  ## Remove build/cache artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
