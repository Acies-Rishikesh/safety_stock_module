# import pandas as pd
# import numpy as np

# from config import PAST_SALES_DATA_AVAILABLE, PAST_FORECAST_DATA_AVAILABLE


# def calculate_grouped_accuracy_metrics(merged_df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Calculates RMSE, MAE, MAPE, Bias, and WAPE for each SKU + Echelon_Type.
#     Does NOT aggregate lead_time or service_level; keeps metrics purely on demand accuracy.

#     Parameters:
#     - merged_df: DataFrame with columns:
#         ['sku_id', 'location_id', 'echelon_type', 'date', 'forecast', 'actual', 'lead_time', 'service_level' (optional)]

#     Returns:
#     - DataFrame with one row per (sku_id, echelon_type)
#     """

#     results = []
#     grouped = merged_df.groupby(['sku_id', 'echelon_type'])

#     for (sku, echelon), group in grouped:
#         y_true = group['actual']
#         y_pred = group['forecast']

#         epsilon = 1e-10  # avoid division by zero
#         y_true_safe = y_true.replace(0, epsilon)

#         rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
#         mae = np.mean(np.abs(y_true - y_pred))
#         mape = np.mean(np.abs((y_true - y_pred) / y_true_safe)) * 100
#         bias = np.mean(y_pred - y_true)
#         wape = np.sum(np.abs(y_true - y_pred)) / np.sum(y_true_safe) * 100

#         results.append({
#             'sku_id': sku,
#             'echelon_type': echelon,
#             'RMSE': round(rmse, 2),
#             'MAE': round(mae, 2),
#             'MAPE (%)': round(mape, 2),
#             'Bias': round(bias, 2),
#             'WAPE (%)': round(wape, 2),
#             'n_samples': len(group)
#         })

#     return pd.DataFrame(results)


# def data_availability_check() -> bool:
#     """Checks if both past forecast & sales data are available."""
#     return PAST_FORECAST_DATA_AVAILABLE and PAST_SALES_DATA_AVAILABLE
import pandas as pd
import numpy as np

from config import PAST_SALES_DATA_AVAILABLE, PAST_FORECAST_DATA_AVAILABLE


def calculate_grouped_accuracy_metrics(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates RMSE, MAE, MAPE, Bias, and WAPE for each SKU + Echelon_Type.
    Includes lead_time and service_level in results without grouping by them.

    Parameters:
    - merged_df: DataFrame with columns:
        ['sku_id', 'location_id', 'echelon_type', 'date', 'forecast', 'actual', 'lead_time', 'service_level' (optional)]

    Returns:
    - DataFrame with one row per (sku_id, echelon_type) including lead_time and service_level
    """

    results = []
    grouped = merged_df.groupby(['sku_id', 'echelon_type'])

    for (sku, echelon), group in grouped:
        y_true = group['actual']
        y_pred = group['forecast']

        epsilon = 1e-10  # avoid division by zero
        y_true_safe = y_true.replace(0, epsilon)

        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        mae = np.mean(np.abs(y_true - y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / y_true_safe)) * 100
        bias = np.mean(y_pred - y_true)
        wape = np.sum(np.abs(y_true - y_pred)) / np.sum(y_true_safe) * 100

        results.append({
            'sku_id': sku,
            'echelon_type': echelon,
            'lead_time': group['lead_time'].dropna().iloc[0] if 'lead_time' in group.columns and not group['lead_time'].dropna().empty else None,
            'service_level': group['service_level'].dropna().iloc[0] if 'service_level' in group.columns and not group['service_level'].dropna().empty else None,
            'RMSE': round(rmse, 2),
            'MAE': round(mae, 2),
            'MAPE (%)': round(mape, 2),
            'Bias': round(bias, 2),
            'WAPE (%)': round(wape, 2),
            'n_samples': len(group)
        })

    return pd.DataFrame(results)


def data_availability_check() -> bool:
    """Checks if both past forecast & sales data are available."""
    return PAST_FORECAST_DATA_AVAILABLE and PAST_SALES_DATA_AVAILABLE
