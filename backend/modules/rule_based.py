# import pandas as pd
# import numpy as np
# from scipy.stats import norm


# def get_service_level_z(service_level: float) -> float:
#     """
#     Converts service level (e.g., 0.95) to Z-score.
#     """
#     return round(norm.ppf(service_level), 2)


# def fetch_service_level(row, service_level_dict, fallback_level):
#     """
#     Dynamically fetch service level based on available keys.
#     Priority: SKU + Echelon + Region > SKU + Echelon > SKU > Echelon > Region > Global
#     """
#     keys_to_try = [
#         (row['sku_id'], row['echelon_type'], row['region']),
#         (row['sku_id'], row['echelon_type']),
#         (row['sku_id'],),
#         (row['echelon_type'],),
#         (row['region'],),
#         ('GLOBAL',)
#     ]

#     for key in keys_to_try:
#         if key in service_level_dict:
#             return service_level_dict[key]

#     return fallback_level  # Final fallback


# def calculate_rule_based_safety_stock_without_variability(
#     df: pd.DataFrame,
#     service_level_dict: dict,
#     default_service_level: float = 0.95
# ) -> pd.DataFrame:
#     """
#     Calculates rule-based safety stock using: SS = Z * σ * sqrt(Lead Time)

#     Parameters:
#     - df: DataFrame with ['sku_id', 'echelon_type', 'region', 'lead_time', 'actual']
#     - service_level_dict: Dictionary with keys like ('sku_id', 'echelon_type') or ('echelon_type',) etc. → values are service levels (e.g., 0.95)
#     - default_service_level: Default service level to use if no match found

#     Returns:
#     - DataFrame with safety stock per SKU/Location/Date
#     """

#     # Ensure lead_time is numeric
#     df['lead_time'] = pd.to_numeric(df['lead_time'], errors='coerce')

#     # Calculate rolling std dev per SKU+Echelon+Region over past demand
#     group_cols = ['sku_id', 'echelon_type', 'region']
#     demand_std = df.groupby(group_cols)['actual'].std().reset_index().rename(columns={'actual': 'demand_std'})

#     # Merge with original
#     df = pd.merge(df, demand_std, on=group_cols, how='left')

#     # Fill missing std with zero (optional: could drop instead)
#     df['demand_std'] = df['demand_std'].fillna(0)

#     # Fetch service level
#     df['service_level'] = df.apply(lambda row: fetch_service_level(row, service_level_dict, default_service_level), axis=1)

#     # Compute Z-score
#     df['z_score'] = df['service_level'].apply(get_service_level_z)

#     # Final Rule-Based SS
#     df['rule_based_ss'] = (df['z_score'] * df['demand_std'] * np.sqrt(df['lead_time'])).round(2)

#     return df[['sku_id', 'echelon_type', 'region', 'lead_time', 'demand_std', 'service_level', 'z_score', 'rule_based_ss']]



import numpy as np
from scipy.stats import norm
import pandas as pd

def calculate_rule_based_safety_stock_without_variability(sku_df: pd.DataFrame, row_data: pd.Series) -> float:
    """
    sku_df: filtered data for a single SKU & Echelon
    row_data: segmentation row containing lead_time & service_level
    """

    lt = row_data['lead_time']
    sl = row_data['service_level']

    sigma_d = sku_df['actual'].std(ddof=0)  # demand variability
    avg_d = sku_df['actual'].mean()

    z = norm.ppf(sl)

    # No lead time variability
    ss_no_var = z * sigma_d * np.sqrt(lt)

    # With lead time variability (optional)
    if 'lead_time' in sku_df.columns:
        sigma_lt = sku_df['lead_time'].std(ddof=0)
        ss_with_var = z * np.sqrt((sigma_d ** 2 * lt) + (sigma_lt ** 2 * avg_d ** 2))
    else:
        ss_with_var = None

    return round(ss_no_var, 2)  # or return both if needed
