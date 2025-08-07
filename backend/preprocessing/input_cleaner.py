import pandas as pd
def clean_and_prepare_inputs(forecast_df, actual_df, column_mapping):
    # ✅ Rename forecast columns to standard
    forecast_df.rename(columns={
        column_mapping['sku_id']: 'sku_id',
        column_mapping['location_id']: 'location_id',
        column_mapping['echelon_type']: 'echelon_type',  # ✅ REQUIRED
        column_mapping['date']: 'date',
        column_mapping['forecast']: 'forecast',
        column_mapping['lead_time']: 'lead_time'
    }, inplace=True)

    # ✅ Rename actual columns to standard
    actual_df.rename(columns={
        column_mapping['sku_id']: 'sku_id',
        column_mapping['location_id']: 'location_id',
        column_mapping['date']: 'date',
        column_mapping['echelon_type']: 'echelon_type',
        column_mapping['actual']: 'actual'
    }, inplace=True)

    # ✅ Drop missing essentials
    forecast_df.dropna(subset=['sku_id', 'location_id', 'date', 'forecast', 'lead_time'], inplace=True)
    actual_df.dropna(subset=['sku_id', 'location_id', 'date', 'actual'], inplace=True)

    # ✅ Convert types
    forecast_df['date'] = pd.to_datetime(forecast_df['date'])
    actual_df['date'] = pd.to_datetime(actual_df['date'])

    forecast_df['forecast'] = pd.to_numeric(forecast_df['forecast'], errors='coerce')
    forecast_df['lead_time'] = pd.to_numeric(forecast_df['lead_time'], errors='coerce').astype('Int64')
    actual_df['actual'] = pd.to_numeric(actual_df['actual'], errors='coerce')

    return forecast_df, actual_df
