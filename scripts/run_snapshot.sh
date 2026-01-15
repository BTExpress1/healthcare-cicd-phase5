#!/usr/bin/env bash
set -euo pipefail

CSV="${1:-data/sample/provider_panel_risk_scored_sample.csv}"
OUT="${2:-reports/snapshot.json}"

python -m healthcare_signals.snapshot --csv "$CSV" --out "$OUT" --baseline reports/baseline_snapshot.json
