import json
from pathlib import Path

import pandas as pd

from healthcare_signals.config import DEFAULT_CONFIG
from healthcare_signals.snapshot import compute_snapshot, regression_check


def test_snapshot_matches_baseline():
    df = pd.read_csv("data/sample/provider_panel_risk_scored_sample.csv")
    snap = compute_snapshot(df, DEFAULT_CONFIG)

    baseline = json.loads(Path("reports/baseline_snapshot.json").read_text(encoding="utf-8"))
    regression_check(snap, baseline, DEFAULT_CONFIG)
