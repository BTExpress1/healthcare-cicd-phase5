from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContractConfig:
    # Core keys
    provider_id_col: str = "provider_id"
    as_of_date_col: str = "as_of_date"

    # Outputs
    risk_score_col: str = "provider_risk_score"

    # Freshness
    max_age_days: int = 45  # fail if newest as_of_date is older than this many days

    # Required columns (strict, but you can loosen later)
    required_columns: tuple[str, ...] = (
        "provider_id",
        "as_of_date",
        "provider_risk_score",
        "provider_risk_raw",
        "risk_rank",
        "anomaly_rank",
        "anomaly_total_flags",
        "iforest_score",
        "iforest_norm",
        "iforest_flag",
        "lof_score",
        "lof_norm",
        "lof_flag",
        "recency_norm",
        "momentum_norm",
        "zscore_shift_norm",
        "flags_norm",
        "first_activity_dt",
        "last_activity_dt",
        "days_since_last",
        "total_claims_30d",
        "total_claims_90d",
        "total_claims_180d",
        "total_claims_365d",
        "total_claims_lifetime",
    )

    # Null ceilings for a few high-value fields
    null_rate_max: dict[str, float] | None = None

    # Numeric bounds
    risk_score_bounds: tuple[float, float] = (0.0, 1.0)

    # Snapshot tolerances (used by regression check)
    snapshot_tolerances: dict[str, float] | None = None


DEFAULT_CONFIG = ContractConfig(
    null_rate_max={
        "provider_id": 0.0,
        "as_of_date": 0.0,
        "provider_risk_score": 0.0,
        "last_activity_dt": 0.2,
    },
    snapshot_tolerances={
        "risk_score_mean": 0.10,  # +/- 0.10 absolute
        "risk_score_median": 0.10,  # +/- 0.10 absolute
        "row_count": 0.0,  # exact match for sample
        "provider_count": 0.0,  # exact match for sample
        "top10_overlap_min": 0.70,  # >= 70% overlap expected
    },
)
