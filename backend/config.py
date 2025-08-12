# import sys
# import os

# # Add backend to path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # Import the cleaning function
# from preprocessing.input_cleaner import clean_and_prepare_inputs

# # Define the correct path to test data folder
# data_dir = os.path.join(os.path.dirname(__file__), "data","raw")

# #  Print to verify file paths
# forecast_path = os.path.join(data_dir, "Forecast_Data.csv")
# actual_path = os.path.join(data_dir, "Actual_Sales_Data.csv")


import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the cleaning function
from backend.preprocessing.input_cleaner import clean_and_prepare_inputs

# Correct path to raw data folder
# data_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
data_dir = os.path.abspath(data_dir)

#  File paths
forecast_path = os.path.join(data_dir, "Past_Forecast_Data (1).csv")
actual_path = os.path.join(data_dir, "Past_Sales_Data (2).csv")

column_mapping = {
    "forecast": "Forecasted_Demand",
    "actual": "Actual_Sales",
    "sku_id": "SKU_ID",
    "location_id": "Location_ID",
    "date": "Date",
    "lead_time": "Lead_Time_Days",
    "echelon_type": "Echelon_Type",
    "service_level": "Service_Level"
}

#Flags
PAST_SALES_DATA_AVAILABLE = True
PAST_FORECAST_DATA_AVAILABLE = True

