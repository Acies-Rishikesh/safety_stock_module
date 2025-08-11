import pandas as pd
import numpy as np

from config import PAST_SALES_DATA_AVAILABLE,PAST_FORECAST_DATA_AVAILABLE

def calculate_grouped_accuracy_metrics(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates RMSE, MAE, MAPE, Bias, and WAPE for each SKU + Echelon_Type.

    Parameters:
    - merged_df: DataFrame with ['sku_id', 'location_id', 'echelon_type', 'date', 'forecast', 'actual', 'lead_time']

    Returns:
    - DataFrame with metrics per (sku_id, echelon_type)
    """
    results = []

    grouped = merged_df.groupby(['sku_id', 'echelon_type'])

    for (sku, echelon), group in grouped:
        y_true = group['actual']
        y_pred = group['forecast']

        epsilon = 1e-10
        y_true_safe = y_true.replace(0, epsilon)

        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        mae = np.mean(np.abs(y_true - y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / y_true_safe)) * 100
        bias = np.mean(y_pred - y_true)
        wape = np.sum(np.abs(y_true - y_pred)) / np.sum(y_true_safe) * 100

        results.append({
            'sku_id': sku,
            'echelon_type': echelon,
            'Service_Level': group['service_level'].iloc[0] if 'service_level' in group.columns else 0.95,
            'RMSE': round(rmse, 2),
            'MAE': round(mae, 2),
            'MAPE (%)': round(mape, 2),
            'Bias': round(bias, 2),
            'WAPE (%)': round(wape, 2),
            'n_samples': len(group)
        })

    return pd.DataFrame(results)

def data_availability_check():
    return PAST_FORECAST_DATA_AVAILABLE and PAST_SALES_DATA_AVAILABLE
