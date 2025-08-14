
# def calculate_rule_based_safety_stock(fc_row, seg_row, history_df=None):
#     """
#     Calculate safety stock using only the future forecast row 
#     (no historical data).

#     Args:
#         fc_row (pd.Series): Single row from future forecast DF
#         seg_row (pd.Series): Row from segmentation_df (contains config info)
#         history_df (ignored): Only present to keep signature compatible

#     Returns:
#         float: Safety Stock value
#     """
#     from scipy.stats import norm
#     import numpy as np

#     # Lead time: prefer segmentation config, then from forecast row
#     lt = seg_row.get('lead_time', fc_row.get('lead_time', 0))

#     # Service level: prefer segmentation config, then from forecast row
#     sl = seg_row.get('service_level', fc_row.get('service_level', 0.9))

#     # Convert service level to Z-score
#     z = norm.ppf(sl)

#     # For this rule, std dev is taken as 0 (no variability) or based on forecast as proxy
#     sigma_d = fc_row.get('forecast', 0) * 0.0  # if you want pure forecast quantity, change formula below

#     # EXAMPLE RULE: SS proportional to forecast and lead time
#     # Here using: Z * forecast * sqrt(lead_time)
#     sigma_d = fc_row.get('forecast', 0)

#     ss_value = z * sigma_d * np.sqrt(lt)

#     return round(ss_value, 2)


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

    # Here, instead of actual demand stddev, use forecast as scale proxy
    df['rule_ss'] = df.apply(
        lambda r: round(r['z_score'] * r['forecast'] * np.sqrt(r['lead_time']), 2),
        axis=1
    )

    # Drop temp col
    df.drop(columns=['z_score'], inplace=True)

    return df

# Example usage:
# future_forecast_df = pd.read_csv("future_forecast.csv")
# result_df = calculate_rule_based_safety_stock_df(future_forecast_df)
# print(result_df[['sku_id','location_id','echelon_type','date','forecast','rule_ss']])
