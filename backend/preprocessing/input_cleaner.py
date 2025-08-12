import pandas as pd

def clean_and_prepare_inputs(forecast_df, actual_df,future_forecast_df, column_mapping):
    """
    Cleans and prepares forecast and actual dataframes.

    Parameters:
    - forecast_df: pd.DataFrame (forecast data)
    - actual_df: pd.DataFrame (actuals data)
    - column_mapping: dict mapping standard keys to actual CSV column names

    Returns:
    - cleaned_forecast_df, cleaned_actual_df,cleaned_future_forecast_df
    """

    # --- 1. Normalize all column names in the DataFrames ---
    forecast_df.columns = forecast_df.columns.str.strip().str.lower()
    actual_df.columns = actual_df.columns.str.strip().str.lower()
    future_forecast_df.columns = future_forecast_df.columns.str.strip().str.lower()

    # --- 2. Normalize the mapping dictionary (case-insensitive) ---
    column_mapping = {k.lower(): v.strip().lower() for k, v in column_mapping.items()}

    # --- 3. Build rename map for forecast ---
    rename_map_forecast = {
        column_mapping['sku_id']: 'sku_id',
        column_mapping['location_id']: 'location_id',
        column_mapping['echelon_type']: 'echelon_type',
        column_mapping['date']: 'date',
        column_mapping['forecast']: 'forecast',
        column_mapping['lead_time']: 'lead_time'
    }

    # Optional: Service Level column
    if 'service_level' in column_mapping and column_mapping['service_level'] in forecast_df.columns:
        rename_map_forecast[column_mapping['service_level']] = 'service_level'

    forecast_df.rename(columns=rename_map_forecast, inplace=True)

    # --- 4. Build rename map for actuals ---
    rename_map_actual = {
        column_mapping['sku_id']: 'sku_id',
        column_mapping['location_id']: 'location_id',
        column_mapping['date']: 'date',
        column_mapping['echelon_type']: 'echelon_type',
        column_mapping['actual']: 'actual'
    }

    actual_df.rename(columns=rename_map_actual, inplace=True)

    # --- 5. Drop rows with missing essentials (only if columns exist) ---
    required_forecast_cols = ['sku_id', 'location_id', 'date', 'forecast', 'lead_time']
    forecast_df.dropna(subset=[col for col in required_forecast_cols if col in forecast_df.columns], inplace=True)

    required_actual_cols = ['sku_id', 'location_id', 'date', 'actual']
    actual_df.dropna(subset=[col for col in required_actual_cols if col in actual_df.columns], inplace=True)
##

    # --- 3. Build rename map for forecast ---
    rename_map_future_forecast = {
        column_mapping['sku_id']: 'sku_id',
        column_mapping['location_id']: 'location_id',
        column_mapping['echelon_type']: 'echelon_type',
        column_mapping['date']: 'date',
        column_mapping['forecast']: 'forecast',
        column_mapping['lead_time']: 'lead_time'
    }

    # Optional: Service Level column
    if 'service_level' in column_mapping and column_mapping['service_level'] in future_forecast_df.columns:
        rename_map_future_forecast[column_mapping['service_level']] = 'service_level'

    future_forecast_df.rename(columns=rename_map_future_forecast, inplace=True)

    # --- 6. Convert data types safely ---
    if 'date' in forecast_df.columns:
        forecast_df['date'] = pd.to_datetime(forecast_df['date'], errors='coerce')
    if 'date' in actual_df.columns:
        actual_df['date'] = pd.to_datetime(actual_df['date'], errors='coerce')
    if 'date' in future_forecast_df.columns:
        future_forecast_df['date'] = pd.to_datetime(future_forecast_df['date'], errors='coerce')
       

    if 'forecast' in forecast_df.columns:
        forecast_df['forecast'] = pd.to_numeric(forecast_df['forecast'], errors='coerce')
    if 'lead_time' in forecast_df.columns:
        forecast_df['lead_time'] = pd.to_numeric(forecast_df['lead_time'], errors='coerce').astype('Int64')
    if 'actual' in actual_df.columns:
        actual_df['actual'] = pd.to_numeric(actual_df['actual'], errors='coerce')

    if 'forecast' in future_forecast_df.columns:
        future_forecast_df['forecast'] = pd.to_numeric(future_forecast_df['forecast'], errors='coerce')
    if 'lead_time' in future_forecast_df.columns:
        future_forecast_df['lead_time'] = pd.to_numeric(future_forecast_df['lead_time'], errors='coerce').astype('Int64')

    # --- 7. If service_level missing, add default 0.95 ---
    if 'service_level' not in forecast_df.columns:
        forecast_df['service_level'] = 0.95
    if 'service_level' not in future_forecast_df.columns:
        future_forecast_df['service_level'] = 0.95

    return forecast_df, actual_df,future_forecast_df
