import pandas as pd
from backend.preprocessing.input_cleaner import clean_and_prepare_inputs
from backend.module_selector import run_safety_stock_selector
from backend import config

def run_pipeline(past_forecast_df=None, actual_df=None, future_forecast_df=None):
    """
    Takes raw uploaded dataframes and runs full safety stock pipeline.
    Returns final results dataframe.
    """

    # Clean
    cleaned_forecast, cleaned_actual, cleaned_future = clean_and_prepare_inputs(
        forecast_df=past_forecast_df if past_forecast_df is not None else pd.DataFrame(),
        actual_df=actual_df if actual_df is not None else pd.DataFrame(),
        future_forecast_df=future_forecast_df if future_forecast_df is not None else pd.DataFrame(),
        column_mapping=config.column_mapping,
    )

    # Run model selector
    results = run_safety_stock_selector(
        PAST_SALES_DATA_AVAILABLE=config.PAST_SALES_DATA_AVAILABLE,
        PAST_FORECAST_DATA_AVAILABLE=config.PAST_FORECAST_DATA_AVAILABLE,
        cleaned_future_forecast=cleaned_future,
        cleaned_actual=cleaned_actual,
        cleaned_forecast=cleaned_forecast,
    )

    return results
