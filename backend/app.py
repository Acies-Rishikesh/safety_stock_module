
from app_function_call import initiate_function,input_function_call,forecast_aligner_function_call,metrics_calculator_function_call,segmenter_function_call,model_selector_function_call
from config import PAST_FORECAST_DATA_AVAILABLE,PAST_SALES_DATA_AVAILABLE
# initiate_function()

cleaned_forecast, cleaned_actual,cleaned_future_forecast = input_function_call()
forecast_aligned_df = forecast_aligner_function_call(cleaned_forecast, cleaned_actual)
# print(cleaned_forecast.head())
# print(forecast_aligned_df.head())
# print(cleaned_future_forecast.head())
metrics_df = metrics_calculator_function_call(forecast_aligned_df)
segmented_df = segmenter_function_call(metrics_df,PAST_SALES_DATA_AVAILABLE,PAST_FORECAST_DATA_AVAILABLE)
# print(segmented_df)
output_df = model_selector_function_call(segmented_df,cleaned_future_forecast)
print(output_df)
