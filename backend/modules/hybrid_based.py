import numpy as np
from scipy.stats import norm


def calculate_hybrid_based_safety_stock(sku_df, row_data):
    """
    Hybrid Safety Stock with dynamic RMSE weight.
    Uses RMSE vs actual demand variability to decide weight.
    """
    lt = row_data['lead_time']
    sl = row_data['service_level']
    z = norm.ppf(sl)

    # RMSE-based component
    rmse = np.sqrt(np.mean((sku_df['forecast'] - sku_df['actual']) ** 2))
    ss_rmse = z * rmse * np.sqrt(lt)

    # Rule-based component
    sigma_d = sku_df['actual'].std(ddof=0)
    ss_rule = z * sigma_d * np.sqrt(lt)

    # Dynamic weight calculation
    if rmse + sigma_d == 0:
        weight_rmse = 0.5  # fallback if both are zero
    else:
        weight_rmse = 1 - (rmse / (rmse + sigma_d))
        weight_rmse = max(0, min(weight_rmse, 1))  # clamp between 0 and 1

    # Weighted blend
    ss_no_var = weight_rmse * ss_rmse + (1 - weight_rmse) * ss_rule

    # Lead time variability version
    if 'lead_time' in sku_df.columns:
        sigma_lt = sku_df['lead_time'].std(ddof=0)
        avg_d = sku_df['actual'].mean()

        ss_with_var_rmse = z * np.sqrt((rmse ** 2 * lt) + (sigma_lt ** 2 * avg_d ** 2))
        ss_with_var_rule = z * np.sqrt((sigma_d ** 2 * lt) + (sigma_lt ** 2 * avg_d ** 2))

        ss_with_var = weight_rmse * ss_with_var_rmse + (1 - weight_rmse) * ss_with_var_rule
    else:
        ss_with_var = None

    return {
        "ss_no_var": round(ss_no_var, 2),
        "ss_with_var": round(ss_with_var, 2) if ss_with_var else None,
        "weight_rmse": round(weight_rmse, 2)
    }