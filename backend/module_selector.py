import pandas as pd
from modules.rule_based import calculate_rule_based_safety_stock_df
from modules.rmse_based import calculate_mae_based_safety_stock, calculate_rmse_based_safety_stock
from modules.hybrid_based import calculate_hybrid_based_safety_stock
from modules.ml_based import calculate_ml_based_safety_stock
from modules.bayesian import calculate_bayesian_safety_stock



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


        bayesian_df = calculate_bayesian_safety_stock(cleaned_actual,cleaned_forecast,cleaned_future_forecast)
        bayesian_df = bayesian_df.rename(columns={"bayesian_safety_stock": "bayesian_ss"})

        #Keep only the key columns + bayesian_ss to avoid duplicate data
        bayesian_df = bayesian_df[["sku_id", "location_id", "echelon_type", "date", "bayesian_ss"]]

        #Merge Bayesian results into your previous merged_df
        final_df = pd.merge(
            merged_df,
            bayesian_df,
            on=["sku_id", "location_id", "echelon_type", "date"],
            how="left"
        )

        #Remove any accidental duplicate columns
        final_df = final_df.loc[:, ~final_df.columns.duplicated()]
        final_df.to_excel("all_output_ss_merged_df.xlsx",index=False)

        # final_df now has ml_ss, rule_ss, bayesian_ss

        return ml_based_ss_df
    if PAST_SALES_DATA_AVAILABLE & PAST_FORECAST_DATA_AVAILABLE == False:
        rule_based_ss_df = calculate_rule_based_safety_stock_df(cleaned_future_forecast)
        rule_based_ss_df.to_excel("rule_based_ss_df.xlsx",index=False)
        return rule_based_ss_df

