from __future__ import annotations

import argparse
from datetime import date

import pandas as pd

from healthcare_signals.config import DEFAULT_CONFIG, ContractConfig


class ContractError(RuntimeError):
    pass


def _parse_date_series(s: pd.Series, col: str) -> pd.Series:
    try:
        parsed = pd.to_datetime(s, errors="raise").dt.date
        return parsed
    except Exception as e:
        raise ContractError(f"Column '{col}' cannot be parsed as dates: {e}") from e


def _null_rate(s: pd.Series) -> float:
    return float(s.isna().mean())


def validate_contract(df: pd.DataFrame, cfg: ContractConfig = DEFAULT_CONFIG) -> None:
    missing = [c for c in cfg.required_columns if c not in df.columns]
    if missing:
        raise ContractError(f"Missing required columns: {missing}")

    df[cfg.as_of_date_col] = _parse_date_series(df[cfg.as_of_date_col], cfg.as_of_date_col)

    key_cols = [cfg.provider_id_col, cfg.as_of_date_col]
    dup_mask = df.duplicated(subset=key_cols, keep=False)
    if dup_mask.any():
        dups = df.loc[dup_mask, key_cols].head(10).to_dict(orient="records")
        raise ContractError(f"Duplicate key rows detected for {key_cols}. Examples: {dups}")

    for col, ceiling in (cfg.null_rate_max or {}).items():
        if col not in df.columns:
            continue
        r = _null_rate(df[col])
        if r > ceiling:
            raise ContractError(f"Null rate too high for '{col}': {r:.2%} > {ceiling:.2%}")

    lo, hi = cfg.risk_score_bounds
    rs = pd.to_numeric(df[cfg.risk_score_col], errors="coerce")
    if rs.isna().any():
        raise ContractError(f"'{cfg.risk_score_col}' has non-numeric values.")
    out = df[(rs < lo) | (rs > hi)]
    if not out.empty:
        examples = (
            out[[cfg.provider_id_col, cfg.as_of_date_col, cfg.risk_score_col]]
            .head(10)
            .to_dict(orient="records")
        )
        raise ContractError(
            f"'{cfg.risk_score_col}' out of bounds [{lo},{hi}]. Examples: {examples}"
        )

    max_dt = max(df[cfg.as_of_date_col])
    age_days = (date.today() - max_dt).days
    if age_days > cfg.max_age_days:
        raise ContractError(
            f"Freshness check failed: max({cfg.as_of_date_col})={max_dt} is {age_days} days old "
            f"(max allowed {cfg.max_age_days})."
        )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate provider_panel_risk_scored data contract.")
    p.add_argument("--csv", required=True, help="Path to provider_panel_risk_scored CSV")
    args = p.parse_args(argv)

    df = pd.read_csv(args.csv)
    try:
        validate_contract(df, DEFAULT_CONFIG)
    except ContractError as e:
        print(f"❌ CONTRACT FAIL: {e}")
        return 2

    print("✅ CONTRACT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
