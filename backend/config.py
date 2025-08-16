# backend/config.py

# Column mapping
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

# Flags (default)
PAST_SALES_DATA_AVAILABLE = False
PAST_FORECAST_DATA_AVAILABLE = False
ONLY_RULE_BASED = False
ONLY_ML_BASED = False
BOTH_RULE_ML = False


def set_config_flags(has_past: bool, method_choice: str):
    """Update global config flags from Intro page selection."""
    global PAST_SALES_DATA_AVAILABLE, PAST_FORECAST_DATA_AVAILABLE
    global ONLY_RULE_BASED, ONLY_ML_BASED, BOTH_RULE_ML

    # past data flags
    PAST_SALES_DATA_AVAILABLE = has_past
    PAST_FORECAST_DATA_AVAILABLE = has_past

    # reset
    ONLY_RULE_BASED = False
    ONLY_ML_BASED = False
    BOTH_RULE_ML = False

    # method flags
    if method_choice == "Only Rule-based":
        ONLY_RULE_BASED = True
    elif method_choice == "Only ML":
        ONLY_ML_BASED = True
    elif method_choice == "ML + Rule-based":
        BOTH_RULE_ML = True
