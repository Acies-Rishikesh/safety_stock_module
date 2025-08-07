import sys
import os
import pandas as pd

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the cleaning function
from backend.preprocessing.input_cleaner import clean_and_prepare_inputs

# Define the correct path to test data folder
data_dir = os.path.join(os.path.dirname(__file__), "data")

# ✅ Print to verify file paths
forecast_path = os.path.join(data_dir, "Forecast_Data.csv")
actual_path = os.path.join(data_dir, "Actual_Sales_Data.csv")
# ✅ Read CSVs
forecast_df = pd.read_csv(forecast_path)
actual_df = pd.read_csv(actual_path)

# ✅ Define column mapping: standard name → actual column name in your file
column_mapping = {
    "forecast": "Forecasted_Demand",
    "actual": "Actual_Sales",
    "sku_id": "SKU_ID",
    "location_id": "Location_ID",
    "date": "Date",
    "lead_time": "Lead_Time_Days",
    "echelon_type": "echelon_type"
}

# ✅ Run cleaner
cleaned_forecast, cleaned_actual = clean_and_prepare_inputs(forecast_df, actual_df, column_mapping)

# ✅ Show output
print("\n Cleaned Forecast Preview:\n", cleaned_forecast.head(10))
print("\n Cleaned Actual Preview:\n", cleaned_actual.head(10))
