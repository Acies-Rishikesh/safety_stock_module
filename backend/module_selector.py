import pandas as pd
from modules.rule_based import calculate_rule_based_safety_stock_without_variability
from modules.rmse_based import calculate_mae_based_safety_stock,calculate_rmse_based_safety_stock
from modules.hybrid_based import calculate_hybrid_based_safety_stock
from modules.ml_based import calculate_ml_based_safety_stock


def run_safety_stock_selector(segmentation_df: pd.DataFrame, raw_forecast_df: pd.DataFrame) -> pd.DataFrame:
    """
    Iterates through segmentation_df and calls the respective safety stock method
    for each SKU-Echelon row, returning a combined output.
    
    segmentation_df: output from segmentation step containing columns:
        ['sku_id', 'echelon_type', 'lead_time', 'service_level', 'Selected_method', ...]
    raw_forecast_df: cleaned raw forecast + actual data for all SKUs and echelons
    
    Returns: DataFrame with calculated SS values for all SKUs.
    """

    results = []

    for _, row in segmentation_df.iterrows():
        sku = row['sku_id']
        echelon = row['echelon_type']
        method = row['Selected_method']

        # Filter raw data for this SKU & Echelon
        sku_df = raw_forecast_df[
            (raw_forecast_df['sku_id'] == sku) &
            (raw_forecast_df['echelon_type'] == echelon)
        ].copy()

        if sku_df.empty:
            continue

        # Select method
        if method.lower().startswith("rule"):
            ss_value = calculate_rule_based_safety_stock_without_variability(sku_df, row)  # Pass only this SKU's DF + segmentation row
            segmentation_df.loc[_,"std_dev_ss"] = ss_value
        elif method.lower().startswith("rmse"):
            ss_value = calculate_rmse_based_safety_stock(sku_df, row)
            segmentation_df.loc[_,"rmse_ss"] = ss_value
        elif method.lower().startswith("mae"):
            ss_value = calculate_rmse_based_safety_stock(sku_df, row)
            segmentation_df.loc[_,"mae_ss"] = ss_value
        elif method.lower().startswith("hybrid"):
            ss_value = calculate_hybrid_based_safety_stock(sku_df, row)
            segmentation_df.loc[_,"hybrid_with_no_var_ss"] = ss_value["ss_no_var"]
            segmentation_df.loc[_,"hybrid_with_var_ss"] = ss_value["ss_with_var"]
        elif method.lower().startswith("ml"):
            ss_value = calculate_ml_based_safety_stock(sku_df, row)
            segmentation_df.loc[_,"ml_ss"] = ss_value
        else:
            ss_value = None

        results.append({
            'sku_id': sku,
            'echelon_type': echelon,
            'Selected_method': method,
            'Safety_Stock': ss_value
        })

    # return pd.DataFrame(results)
    return segmentation_df
