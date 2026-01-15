from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from healthcare_signals.config import DEFAULT_CONFIG, ContractConfig
from healthcare_signals.validate_contract import ContractError, validate_contract


def compute_snapshot(df: pd.DataFrame, cfg: ContractConfig = DEFAULT_CONFIG) -> dict[str, Any]:
    validate_contract(df, cfg)

    df[cfg.provider_id_col] = df[cfg.provider_id_col].astype(str).str.zfill(4)

    df[cfg.as_of_date_col] = pd.to_datetime(df[cfg.as_of_date_col]).dt.date
    df[cfg.risk_score_col] = pd.to_numeric(df[cfg.risk_score_col], errors="raise")

    row_count = int(len(df))
    provider_count = int(df[cfg.provider_id_col].nunique())
    max_as_of_date = str(max(df[cfg.as_of_date_col]))

    risk_mean = float(df[cfg.risk_score_col].mean())
    risk_median = float(df[cfg.risk_score_col].median())

    latest_dt = max(df[cfg.as_of_date_col])
    latest = df[df[cfg.as_of_date_col] == latest_dt].copy()
    top10 = (
        latest.sort_values(cfg.risk_score_col, ascending=False)[cfg.provider_id_col]
        .head(10)
        .astype(str)
        .tolist()
    )

    return {
        "row_count": row_count,
        "provider_count": provider_count,
        "max_as_of_date": max_as_of_date,
        "risk_score_mean": risk_mean,
        "risk_score_median": risk_median,
        "top10_providers_by_risk": top10,
        "generated_on": str(date.today()),
    }


def overlap_ratio(a: list[str], b: list[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    return len(sa & sb) / max(len(sa), len(sb))


def regression_check(
    snapshot: dict[str, Any],
    baseline: dict[str, Any],
    cfg: ContractConfig,
) -> None:
    tol = cfg.snapshot_tolerances or {}

    def absdiff_ok(key: str) -> None:
        t = float(tol.get(key, 0.0))
        if t == 0.0:
            if snapshot[key] != baseline[key]:
                raise ContractError(
                    f"Snapshot regression failed for '{key}': {snapshot[key]} != {baseline[key]}"
                )
        else:
            if abs(float(snapshot[key]) - float(baseline[key])) > t:
                raise ContractError(
                    f"Snapshot regression failed for '{key}': {snapshot[key]} vs {baseline[key]} (tol ±{t})"
                )

    absdiff_ok("row_count")
    absdiff_ok("provider_count")
    absdiff_ok("risk_score_mean")
    absdiff_ok("risk_score_median")

    min_overlap = float(tol.get("top10_overlap_min", 0.7))
    ov = overlap_ratio(snapshot["top10_providers_by_risk"], baseline["top10_providers_by_risk"])
    if ov < min_overlap:
        raise ContractError(
            f"Top-10 overlap too low: {ov:.0%} < {min_overlap:.0%}. "
            f"New={snapshot['top10_providers_by_risk']} Baseline={baseline['top10_providers_by_risk']}"
        )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Compute snapshot + optional regression check.")
    p.add_argument("--csv", required=True, help="Path to provider_panel_risk_scored CSV")
    p.add_argument("--out", required=True, help="Write snapshot JSON to this path")
    p.add_argument("--baseline", required=False, help="Baseline snapshot JSON for regression check")
    args = p.parse_args(argv)

    df = pd.read_csv(args.csv)
    snap = compute_snapshot(df, DEFAULT_CONFIG)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    print(f"✅ Snapshot written: {out_path}")

    if args.baseline:
        base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        try:
            regression_check(snap, base, DEFAULT_CONFIG)
        except ContractError as e:
            print(f"❌ SNAPSHOT REGRESSION FAIL: {e}")
            return 2
        print("✅ SNAPSHOT REGRESSION PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
