# import numpy as np
# from scipy.stats import norm
# import pandas as pd

# def calculate_rule_based_safety_stock_without_variability(sku_df: pd.DataFrame, row_data: pd.Series) -> float:
#     """
#     sku_df: filtered data for a single SKU & Echelon
#     row_data: segmentation row containing lead_time & service_level
#     """

#     lt = row_data['lead_time']
#     sl = row_data['service_level']

#     sigma_d = sku_df['actual'].std(ddof=0)  # demand variability
#     avg_d = sku_df['actual'].mean()

#     z = norm.ppf(sl)

#     # No lead time variability
#     ss_no_var = z * sigma_d * np.sqrt(lt)

#     # With lead time variability (optional)
#     if 'lead_time' in sku_df.columns:
#         sigma_lt = sku_df['lead_time'].std(ddof=0)
#         ss_with_var = z * np.sqrt((sigma_d ** 2 * lt) + (sigma_lt ** 2 * avg_d ** 2))
#     else:
#         ss_with_var = None

#     return round(ss_no_var, 2)  # or return both if needed


# --- RULE-BASED ---
def calculate_rule_based_safety_stock(sku_df, row):
    """
    sku_df: historical actual demand data for SKU-echleon
    row: contains lead_time and service_level
    """
    from scipy.stats import norm
    import numpy as np

    lt = row['lead_time']
    sl = row['service_level']
    sigma_d = sku_df['forecast'].std(ddof=0)
    z = norm.ppf(sl)
    return round(z * sigma_d * np.sqrt(lt), 2)
