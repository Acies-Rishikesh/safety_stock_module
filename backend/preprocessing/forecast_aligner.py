import pandas as pd
import numpy as np
def align_forecast_to_actual(forecast_df: pd.DataFrame, actual_df: pd.DataFrame) -> pd.DataFrame:
    # Ensure datetime format
    forecast_df['date'] = pd.to_datetime(forecast_df['date'], errors='coerce')
    actual_df['date'] = pd.to_datetime(actual_df['date'], errors='coerce')

    keys = ['sku_id', 'location_id', 'echelon_type', 'date']

    # Left join to keep all forecast rows (and their lead_time, service_level)
    merged = pd.merge(
        forecast_df,
        actual_df[['sku_id', 'location_id', 'echelon_type', 'date', 'actual']],
        on=keys,
        how='left'
    )

    # Normalize service_level (convert % to decimal)
    merged['service_level'] = merged['service_level'].where(
        merged['service_level'].isna() | (merged['service_level'] <= 1),
        merged['service_level'] / 100.0
    )
    merged['service_level'] = merged['service_level'].clip(lower=0.5, upper=0.999)

    # Ensure numeric
    for col in ['forecast', 'actual', 'lead_time', 'service_level']:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors='coerce')

    return merged
