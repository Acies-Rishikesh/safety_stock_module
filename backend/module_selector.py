import pandas as pd
from modules.rule_based import calculate_rule_based_safety_stock_df
from modules.rmse_based import calculate_mae_based_safety_stock, calculate_rmse_based_safety_stock
from modules.hybrid_based import calculate_hybrid_based_safety_stock
from modules.ml_based import calculate_ml_based_safety_stock

# def run_safety_stock_selector(
#     segmentation_df: pd.DataFrame,
#     raw_forecast_df: pd.DataFrame,
#     past_sales_df: pd.DataFrame,
#     past_forecast_df: pd.DataFrame
# ) -> pd.DataFrame:
#     """
#     Execute selected safety stock method for each SKU–Echelon–Location–Date.
#     """

#     results = []

#     # --- Precompute ML-based results ONCE ---
#     ml_result_df = None
#     if any(segmentation_df['Selected_method'].str.lower().str.startswith(('forecast', 'ml'))):
#         ml_result_df = calculate_ml_based_safety_stock(
#             past_sales_df, past_forecast_df, raw_forecast_df
#         )

#     for _, seg_row in segmentation_df.iterrows():
#         sku = seg_row['sku_id']
#         echelon = seg_row['echelon_type']
#         method = seg_row['Selected_method']

#         # Optional location handling
#         location = seg_row['location_id'] if 'location_id' in seg_row.index else None

#         # Filter future forecast for this SKU + Echelon (and location if exists)
#         if location is not None:
#             combo_df = raw_forecast_df[
#                 (raw_forecast_df['sku_id'] == sku) &
#                 (raw_forecast_df['echelon_type'] == echelon) &
#                 (raw_forecast_df['location_id'] == location)
#             ]
#         else:
#             combo_df = raw_forecast_df[
#                 (raw_forecast_df['sku_id'] == sku) &
#                 (raw_forecast_df['echelon_type'] == echelon)
#             ]

#         if combo_df.empty:
#             continue

#         # Build history df for methods that need actuals
#         history_df = None
#         if method.lower().startswith(("rule", "rmse", "mae", "hybrid")):
#             if location is not None:
#                 history_df = pd.merge(
#                     past_sales_df[
#                         (past_sales_df['sku_id'] == sku) &
#                         (past_sales_df['echelon_type'] == echelon) &
#                         (past_sales_df['location_id'] == location)
#                     ],
#                     past_forecast_df[
#                         (past_forecast_df['sku_id'] == sku) &
#                         (past_forecast_df['echelon_type'] == echelon) &
#                         (past_forecast_df['location_id'] == location)
#                     ],
#                     on=['sku_id', 'location_id', 'echelon_type', 'date'],
#                     suffixes=('_actual', '_forecast')
#                 )
#             else:
#                 history_df = pd.merge(
#                     past_sales_df[
#                         (past_sales_df['sku_id'] == sku) &
#                         (past_sales_df['echelon_type'] == echelon)
#                     ],
#                     past_forecast_df[
#                         (past_forecast_df['sku_id'] == sku) &
#                         (past_forecast_df['echelon_type'] == echelon)
#                     ],
#                     on=['sku_id', 'echelon_type', 'date'],
#                     suffixes=('_actual', '_forecast')
#                 )

#             # Normalize column names
#             if 'actual_actual' in history_df.columns:
#                 history_df['actual'] = history_df['actual_actual']
#             elif 'actual' not in history_df.columns and 'Actual' in history_df.columns:
#                 history_df['actual'] = history_df['Actual']
#             if 'forecast_forecast' in history_df.columns:
#                 history_df['forecast'] = history_df['forecast_forecast']

#         # --- Loop over each forecasted date ---
#         for _, fc_row in combo_df.iterrows():
#             ss_value = None  # Always initialize

#             if method.lower().startswith("rule") and history_df is not None:
#                 ss_value = calculate_rule_based_safety_stock(fc_row, seg_row, history_df)

#             elif method.lower().startswith("rmse") and history_df is not None:
#                 ss_value = calculate_rmse_based_safety_stock(history_df, seg_row)

#             elif method.lower().startswith("mae") and history_df is not None:
#                 ss_value = calculate_mae_based_safety_stock(history_df, seg_row)

#             elif method.lower().startswith("hybrid") and history_df is not None:
#                 ss_dict = calculate_hybrid_based_safety_stock(history_df, seg_row)
#                 ss_value = ss_dict.get("ss_with_var", None)

#             elif method.lower().startswith(("forecast", "ml")) and ml_result_df is not None:
#                 if location is not None:
#                     match_row = ml_result_df[
#                         (ml_result_df["sku_id"] == sku) &
#                         (ml_result_df["echelon_type"] == echelon) &
#                         (ml_result_df["location_id"] == location) &
#                         (ml_result_df["date"] == fc_row["date"])
#                     ]
#                 else:
#                     match_row = ml_result_df[
#                         (ml_result_df["sku_id"] == sku) &
#                         (ml_result_df["echelon_type"] == echelon) &
#                         (ml_result_df["date"] == fc_row["date"])
#                     ]
#                 if not match_row.empty and "Safety_Stock" in match_row.columns:
#                     ss_value = match_row["Safety_Stock"].iloc[0]

#             results.append({
#                 "sku_id": sku,
#                 "location_id": location if location is not None else None,
#                 "echelon_type": echelon,
#                 "date": fc_row["date"],
#                 "Selected_method": method,
#                 "Safety_Stock": ss_value
#             })

#     return pd.DataFrame(results)


def run_safety_stock_selector(PAST_SALES_DATA_AVAILABLE,PAST_FORECAST_DATA_AVAILABLE,cleaned_future_forecast,cleaned_actual,cleaned_forecast):

    #SHOULD RUN THIS CODE NORMALLY

    if (PAST_SALES_DATA_AVAILABLE == True) & (PAST_FORECAST_DATA_AVAILABLE == True):
        ml_based_ss_df = calculate_ml_based_safety_stock(cleaned_actual,cleaned_forecast,cleaned_future_forecast)
        rule_based_ss_df = calculate_rule_based_safety_stock_df(cleaned_future_forecast)
        # ml_based_ss_df.to_excel("ml_based_ss_df.xlsx",index=False)

        # Ensure consistent column names for merging
        ml_based_ss_df = ml_based_ss_df.rename(columns={"Safety_Stock": "ml_ss"})
        rule_based_ss_df = rule_based_ss_df.rename(columns={"rule_ss": "rule_ss"})

        # Keep only required columns from SS dataframes
        ml_based_ss_df = ml_based_ss_df[["sku_id", "location_id", "echelon_type", "date", "ml_ss"]]
        rule_based_ss_df = rule_based_ss_df[["sku_id", "location_id", "echelon_type", "date", "rule_ss"]]

        # Merge ML results into future forecast
        merged_df = pd.merge(
            cleaned_future_forecast,  # Base df
            ml_based_ss_df,
            on=["sku_id", "location_id", "echelon_type", "date"],
            how="left"
        )

        # Merge Rule-based results
        merged_df = pd.merge(
            merged_df,
            rule_based_ss_df,
            on=["sku_id", "location_id", "echelon_type", "date"],
            how="left"
        )

        # Remove duplicate columns if any got in by accident
        merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]
        merged_df.to_excel("output_ss_merged_df.xlsx",index=False)
        return ml_based_ss_df
    if PAST_SALES_DATA_AVAILABLE & PAST_FORECAST_DATA_AVAILABLE == False:
        rule_based_ss_df = calculate_rule_based_safety_stock_df(cleaned_future_forecast)
        rule_based_ss_df.to_excel("rule_based_ss_df.xlsx",index=False)
        return rule_based_ss_df

