import pandas as pd
import numpy as np
from scipy.stats import norm

def calculate_rule_based_safety_stock_df(future_forecast_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate rule-based safety stock for each row in the future forecast dataset.

    Args:
        future_forecast_df (pd.DataFrame): Must contain:
            ['sku_id', 'echelon_type', 'date', 'forecast', 'lead_time', 'service_level']
            and optionally 'location_id'

    Returns:
        pd.DataFrame: Same as input with an extra 'rule_ss' column.
    """
    # Copy to avoid modifying original
    df = future_forecast_df.copy()

    # Ensure needed columns exist
    required_cols = ['sku_id', 'echelon_type', 'date',
                     'forecast', 'lead_time', 'service_level']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column in future_forecast_df: {col}")

    # Calculate Z-score for each row from service level
    df['z_score'] = df['service_level'].apply(lambda sl: norm.ppf(sl))

    # Corrected Logic: Use the square root of the forecast as a proxy for the
    # standard deviation of daily demand, assuming demand follows a Poisson-like
    # distribution where variance is approximately equal to the mean.
    df['rule_ss'] = df.apply(
        lambda r: round(r['z_score'] * np.sqrt(r['forecast']) * np.sqrt(r['lead_time']), 2),
        axis=1
    )

    # Drop temp col
    df.drop(columns=['z_score'], inplace=True)

    return df