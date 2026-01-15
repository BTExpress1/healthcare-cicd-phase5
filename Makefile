PY := python
PIP := pip
SRC := src
CSV := data/sample/provider_panel_risk_scored_sample.csv
BASELINE := reports/baseline_snapshot.json

.PHONY: setup lint test validate snapshot ci

setup:
	$(PY) -m $(PIP) install -U pip
	$(PY) -m $(PIP) install -e ".[dev]"

lint:
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

test:
	$(PY) -m pytest

validate:
	$(PY) -m healthcare_signals.validate_contract --csv $(CSV)

snapshot:
	$(PY) -m healthcare_signals.snapshot --csv $(CSV) --out reports/snapshot.json --baseline $(BASELINE)

ci: lint test validate snapshot
