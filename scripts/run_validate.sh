#!/usr/bin/env bash
set -euo pipefail

python -m healthcare_signals.validate_contract --csv "${1:-data/sample/provider_panel_risk_scored_sample.csv}"
