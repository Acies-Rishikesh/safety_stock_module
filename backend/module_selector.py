import pandas as pd
from backend.modules.rule_based import calculate_rule_based_safety_stock_df
from backend.modules.ml_based import calculate_ml_based_safety_stock
from backend.config import BOTH_RULE_ML, ONLY_ML_BASED, ONLY_RULE_BASED

KEYS = ["sku_id", "location_id", "echelon_type", "date"]

def run_safety_stock_selector(
    PAST_SALES_DATA_AVAILABLE: bool,
    PAST_FORECAST_DATA_AVAILABLE: bool,
    cleaned_future_forecast: pd.DataFrame,
    cleaned_actual: pd.DataFrame | None = None,
    cleaned_forecast: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Run the appropriate safety stock calculation(s) based on flags and available data."""
    if cleaned_future_forecast is None or cleaned_future_forecast.empty:
        return pd.DataFrame()

    # With past data
    if PAST_SALES_DATA_AVAILABLE and PAST_FORECAST_DATA_AVAILABLE:
        if BOTH_RULE_ML:
            ml_df = calculate_ml_based_safety_stock(cleaned_actual, cleaned_forecast, cleaned_future_forecast)
            if "Safety_Stock" in ml_df.columns and "ml_ss" not in ml_df.columns:
                ml_df = ml_df.rename(columns={"Safety_Stock": "ml_ss"})
            ml_keep = ml_df[KEYS + ["ml_ss"]] if "ml_ss" in ml_df.columns else ml_df[KEYS]

            rule_df = calculate_rule_based_safety_stock_df(cleaned_future_forecast)
            rule_keep = rule_df[KEYS + ["rule_ss"]] if "rule_ss" in rule_df.columns else rule_df[KEYS]

            out = cleaned_future_forecast.merge(ml_keep, on=KEYS, how="left")
            out = out.merge(rule_keep, on=KEYS, how="left")
            return out

        if ONLY_ML_BASED:
            ml_df = calculate_ml_based_safety_stock(cleaned_actual, cleaned_forecast, cleaned_future_forecast)
            if "Safety_Stock" in ml_df.columns and "ml_ss" not in ml_df.columns:
                ml_df = ml_df.rename(columns={"Safety_Stock": "ml_ss"})
            return ml_df

        if ONLY_RULE_BASED:
            return calculate_rule_based_safety_stock_df(cleaned_future_forecast)

        # Fallback
        return calculate_rule_based_safety_stock_df(cleaned_future_forecast)

    # Without past data -> Rule-based only
    return calculate_rule_based_safety_stock_df(cleaned_future_forecast)
