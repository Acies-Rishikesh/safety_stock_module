# backend/module_selector.py
import pandas as pd
import backend.config as config  # import module, not constants

from backend.modules.rule_based import calculate_rule_based_safety_stock_df
from backend.modules.ml_based import calculate_ml_based_safety_stock

KEYS = ["sku_id", "location_id", "echelon_type", "date"]

def run_safety_stock_selector(
    PAST_SALES_DATA_AVAILABLE: bool,
    PAST_FORECAST_DATA_AVAILABLE: bool,
    cleaned_future_forecast: pd.DataFrame,
    cleaned_actual: pd.DataFrame | None = None,
    cleaned_forecast: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Selector that dynamically respects config flags."""
    if cleaned_future_forecast is None or cleaned_future_forecast.empty:
        return pd.DataFrame()

    out = cleaned_future_forecast.copy()
    has_past = bool(PAST_SALES_DATA_AVAILABLE and PAST_FORECAST_DATA_AVAILABLE)

    ml_part = None
    rule_part = None

    # --- ML path ---
    if has_past and (config.ONLY_ML_BASED or config.BOTH_RULE_ML):
        ml_df = calculate_ml_based_safety_stock(cleaned_actual, cleaned_forecast, cleaned_future_forecast)
        if "Safety_Stock" in ml_df.columns and "ml_ss" not in ml_df.columns:
            ml_df = ml_df.rename(columns={"Safety_Stock": "ml_ss"})
        if "ml_ss" in ml_df.columns:
            ml_part = ml_df[KEYS + ["ml_ss"]]

    # --- Rule path ---
    if (not has_past) or config.ONLY_RULE_BASED or config.BOTH_RULE_ML:
        rule_df = calculate_rule_based_safety_stock_df(cleaned_future_forecast)
        if "rule_ss" in rule_df.columns:
            rule_part = rule_df[KEYS + ["rule_ss"]]

    # --- Merge parts ---
    if ml_part is not None:
        out = out.merge(ml_part, on=KEYS, how="left")
    if rule_part is not None:
        out = out.merge(rule_part, on=KEYS, how="left")

    # --- final_ss (convenience) ---
    if config.BOTH_RULE_ML:
        pass  # keep both
    elif config.ONLY_ML_BASED and "ml_ss" in out.columns:
        out["final_ss"] = out["ml_ss"]
    elif config.ONLY_RULE_BASED and "rule_ss" in out.columns:
        out["final_ss"] = out["rule_ss"]

    out = out.loc[:, ~out.columns.duplicated()]
    return out
