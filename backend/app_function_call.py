import pandas as pd
import sys, os
path=sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from config import forecast_path,actual_path,column_mapping
from preprocessing.input_cleaner import clean_and_prepare_inputs
from preprocessing.forecast_aligner import align_forecast_to_actual
from accuracy.metrics_calculator import calculate_grouped_accuracy_metrics,data_availability_check
from segmentation.segmenter import segmentation_function


def initiate_function():
    input_function_call()

def input_function_call():
    forecast_df = pd.read_csv(forecast_path)
    actual_df = pd.read_csv(actual_path)
    cleaned_forecast, cleaned_actual = clean_and_prepare_inputs(forecast_df, actual_df, column_mapping)
    return cleaned_forecast, cleaned_actual

def forecast_aligner_function_call(cleaned_forecast, cleaned_actual):
    forecast_aligned_df = align_forecast_to_actual(cleaned_forecast, cleaned_actual)
    return forecast_aligned_df                  # this is the merged df

def metrics_calculator_function_call(forecast_aligned_df):
    if data_availability_check()==False:
        return "Past data not available"
    metrics_df = calculate_grouped_accuracy_metrics(forecast_aligned_df)
    return metrics_df

def segmenter_function_call(metrics_df,PAST_SALES_DATA_AVAILABLE,PAST_FORECAST_DATA_AVAILABLE):
    if data_availability_check()==False:
        return "Past data not available"
    segmented_df = segmentation_function(metrics_df,PAST_SALES_DATA_AVAILABLE,PAST_FORECAST_DATA_AVAILABLE)
    print(segmented_df.head())
    segmented_df.to_csv("grouped_accuracy_metrics.csv", index=False)

    return segmented_df





    