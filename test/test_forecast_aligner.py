import sys
import os
import pandas as pd

# Add backend path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.preprocessing.input_cleaner import clean_and_prepare_inputs
from backend.preprocessing.forecast_aligner import align_forecast_to_actual

# Sample test data location
data_dir = os.path.join(os.path.dirname(__file__), "data")

# Load test data
forecast_df = pd.read_csv(os.path.join(data_dir, "Forecast_Data.csv"))
actual_df = pd.read_csv(os.path.join(data_dir, "Actual_Sales_Data.csv"))

# Column mapping as per input
column_mapping = {
    "forecast": "Forecasted_Demand",
    "actual": "Actual_Sales",
    "sku_id": "SKU_ID",
    "location_id": "Location_ID",
    "date": "Date",
    "lead_time": "Lead_Time_Days",
    "echelon_type": "echelon_type"
}

# Clean inputs
cleaned_forecast, cleaned_actual = clean_and_prepare_inputs(forecast_df, actual_df, column_mapping)

# Align forecast and actuals
aligned_forecast, aligned_actual = align_forecast_to_actual(forecast_df, actual_df)

print("\nAligned Forecast:\n", aligned_forecast.head())
print("\nAligned Actuals:\n", aligned_actual.head())
