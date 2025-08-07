import os
import pandas as pd
import sys

# Add module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.preprocessing.input_cleaner import clean_and_prepare_inputs
from backend.preprocessing.forecast_aligner import align_forecast_to_actual
from backend.accuracy.metrics_calculator import calculate_grouped_accuracy_metrics

# Load files
data_dir = os.path.join(os.path.dirname(__file__), "data")

forecast_df = pd.read_csv(os.path.join(data_dir, "Forecast_Data.csv"))
actual_df = pd.read_csv(os.path.join(data_dir, "Actual_Sales_Data.csv"))

# Column mapping
column_mapping = {
    "forecast": "Forecasted_Demand",
    "actual": "Actual_Sales",
    "sku_id": "SKU_ID",
    "location_id": "Location_ID",
    "date": "Date",
    "lead_time": "Lead_Time_Days",
    "echelon_type": "Echelon_Type"   # ✅ ADD THIS LINE
}


# Clean
cleaned_forecast, cleaned_actual = clean_and_prepare_inputs(forecast_df, actual_df, column_mapping)

# Align
aligned_df = align_forecast_to_actual(cleaned_forecast, cleaned_actual)

# Metrics
metrics_df = calculate_grouped_accuracy_metrics(aligned_df)

# Show
print(metrics_df.head())
