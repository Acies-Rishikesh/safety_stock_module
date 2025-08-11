import numpy as np
from scipy.stats import norm



def calculate_rmse_based_safety_stock(sku_df, row_data):
    """
    RMSE-based Safety Stock (Forecast-Based)
    Formula: Z * RMSE * sqrt(Lead Time)
    """
    lt = row_data['lead_time']
    sl = row_data['service_level']

    # Calculate RMSE between forecast & actual
    rmse = np.sqrt(np.mean((sku_df['forecast'] - sku_df['actual']) ** 2))

    z = norm.ppf(sl)

    # Without lead time variability
    ss_no_var = z * rmse * np.sqrt(lt)

    # With lead time variability (optional)
    if 'lead_time' in sku_df.columns:
        sigma_lt = sku_df['lead_time'].std(ddof=0)
        avg_error = np.mean(np.abs(sku_df['forecast'] - sku_df['actual']))
        ss_with_var = z * np.sqrt((rmse ** 2 * lt) + (sigma_lt ** 2 * avg_error ** 2))
    else:
        ss_with_var = None

    return round(ss_no_var, 2), round(ss_with_var, 2) if ss_with_var else None

def calculate_mae_based_safety_stock(sku_df, row_data):
    """
    MAE-based Safety Stock
    Assumes MAE ~ 0.8 * sigma_d (approx. for normal demand) — can adjust factor.
    Formula: Z * sigma_est * sqrt(Lead Time)
    """
    lt = row_data['lead_time']
    sl = row_data['service_level']

    mae = np.mean(np.abs(sku_df['forecast'] - sku_df['actual']))

    # Approx. sigma from MAE under normal assumption
    sigma_est = mae / 0.8

    z = norm.ppf(sl)
    ss_no_var = z * sigma_est * np.sqrt(lt)

    if 'lead_time' in sku_df.columns:
        sigma_lt = sku_df['lead_time'].std(ddof=0)
        avg_error = mae
        ss_with_var = z * np.sqrt((sigma_est ** 2 * lt) + (sigma_lt ** 2 * avg_error ** 2))
    else:
        ss_with_var = None

    return round(ss_no_var, 2), round(ss_with_var, 2) if ss_with_var else None
