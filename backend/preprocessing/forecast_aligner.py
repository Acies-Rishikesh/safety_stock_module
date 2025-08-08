import pandas as pd

def align_forecast_to_actual(forecast_df: pd.DataFrame, actual_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aligns forecast and actual data on SKU, Location, Date, Echelon Type.
    Returns a single merged DataFrame for grouped metric calculations.

    Parameters:
    - forecast_df: cleaned forecast DataFrame with ['sku_id', 'location_id', 'echelon_type', 'date', 'forecast', 'lead_time']
    - actual_df: cleaned actual sales DataFrame with ['sku_id', 'location_id', 'echelon_type', 'date', 'actual']

    Returns:
    - merged_df: Aligned DataFrame with forecast, actual, and metadata
    """

    # Keys to align on
    common_keys = ['sku_id', 'location_id', 'echelon_type', 'date']

    # Merge data on keys
    merged = pd.merge(
        forecast_df,
        actual_df,
        on=common_keys,
        how='inner'
    )

    # Final columns
    return merged[['sku_id', 'location_id', 'echelon_type', 'date', 'forecast', 'actual', 'lead_time']]



