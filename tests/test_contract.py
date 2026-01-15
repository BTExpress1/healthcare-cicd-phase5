import pandas as pd
import pytest

from healthcare_signals.config import DEFAULT_CONFIG
from healthcare_signals.validate_contract import ContractError, validate_contract


def test_contract_passes_on_sample():
    df = pd.read_csv("data/sample/provider_panel_risk_scored_sample.csv")
    validate_contract(df, DEFAULT_CONFIG)


def test_contract_fails_on_missing_column():
    df = pd.read_csv("data/sample/provider_panel_risk_scored_sample.csv")
    df = df.drop(columns=["provider_risk_score"])
    with pytest.raises(ContractError):
        validate_contract(df, DEFAULT_CONFIG)


def test_contract_fails_on_risk_out_of_bounds():
    df = pd.read_csv("data/sample/provider_panel_risk_scored_sample.csv")
    df.loc[0, "provider_risk_score"] = 1.5
    with pytest.raises(ContractError):
        validate_contract(df, DEFAULT_CONFIG)
