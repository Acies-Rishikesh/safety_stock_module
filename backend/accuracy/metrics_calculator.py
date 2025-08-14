
import pandas as pd
import numpy as np
from config import PAST_FORECAST_DATA_AVAILABLE, PAST_SALES_DATA_AVAILABLE


def calculate_grouped_accuracy_metrics(merged_df: pd.DataFrame) -> pd.DataFrame:
    results = []
    grouped = merged_df.groupby(['sku_id', 'echelon_type'], dropna=False)

    for (sku, echelon), g in grouped:
        y_true = pd.to_numeric(g['actual'], errors='coerce')
        y_pred = pd.to_numeric(g['forecast'], errors='coerce')
        mask = y_true.notna() & y_pred.notna()
        y_true = y_true[mask]; y_pred = y_pred[mask]
        if len(y_true) == 0:
            continue

        err = y_pred - y_true
        abs_err = np.abs(err)

        rmse = float(np.sqrt(np.mean(err**2)))
        mae  = float(np.mean(abs_err))
        bias = float(np.mean(err))
        wape = float(abs_err.sum() / max(y_true.abs().sum(), 1e-9) * 100)

        # MAPE guarded (ignore tiny actuals)
        mape_mask = (y_true.abs() >= 10)  # drop tiny-actual rows
        mape = float(np.mean((abs_err[mape_mask] / y_true[mape_mask].abs())) * 100) if mape_mask.any() else np.nan

        results.append({
            'sku_id': sku,
            'echelon_type': echelon,
            'lead_time': g['lead_time'].dropna().iloc[0] if 'lead_time' in g and g['lead_time'].notna().any() else None,
            'service_level': g['service_level'].dropna().iloc[0] if 'service_level' in g and g['service_level'].notna().any() else None,
            'RMSE': round(rmse, 2),
            'MAE': round(mae, 2),
            'MAPE (%)': round(mape, 2) if not np.isnan(mape) else np.nan,
            'Bias': round(bias, 2),
            'WAPE (%)': round(wape, 2),
            'n_samples': int(len(y_true))
        })
    return pd.DataFrame(results)



def data_availability_check() -> bool:
    """Checks if both past forecast & sales data are available."""
    return PAST_FORECAST_DATA_AVAILABLE and PAST_SALES_DATA_AVAILABLE
