import pandas as pd



def segmentation_function(metrics_df_original,PAST_SALES_DATA_AVAILABLE,PAST_FORECAST_DATA_AVAILABLE):
    metrics_df = metrics_df_original.copy()
    metrics_df[["std_dev_ss","rmse_ss","mae_ss","hybrid_with_no_var_ss","hybrid_with_var_ss","ml_ss"]] = None
    if PAST_FORECAST_DATA_AVAILABLE and PAST_SALES_DATA_AVAILABLE:
        for i in range(len(metrics_df)):
            rmse_level,bias_level,mape_level = select_method(metrics_df.loc[i,"RMSE"],metrics_df.loc[i,"Bias"],metrics_df.loc[i,"MAPE (%)"])
            metrics_df.loc[i,"Selected_method"] = take_decision(rmse_level,bias_level,mape_level)
        return metrics_df
    else:
        return "There are no past Data"

def select_method(rmse_pct, bias_pct, mape_pct):
     # RMSE levels
    rmse_level = "low" if rmse_pct <= 10 else "medium" if rmse_pct <= 20 else "high"
    # Bias levels
    bias_level = "low" if abs(bias_pct) <= 5 else "medium" if abs(bias_pct) <= 10 else "high"
    # MAPE levels
    mape_level = "low" if mape_pct <= 10 else "medium" if mape_pct <= 20 else "high"

    return rmse_level,bias_level,mape_level

def take_decision(rmse_level,bias_level,mape_level):

    # Decision rules
    if rmse_level == "high" or bias_level == "high":
        return "Rule-based SS"

    if rmse_level == "low" and bias_level == "low":
        if mape_level == "low" or mape_level == "medium":
            return "Forecast-based SS"
        else:
            return "Hybrid"

    if rmse_level == "low" and bias_level == "medium":
        if mape_level == "low":
            return "Hybrid"
        else:
            return "Rule-based SS"

    if rmse_level == "medium" and bias_level == "low":
        if mape_level == "low" or mape_level == "medium":
            return "Hybrid"
        else:
            return "Rule-based SS"

    if rmse_level == "medium" and bias_level == "medium":
        if mape_level == "low":
            return "Hybrid"
        else:
            return "Rule-based SS"

    return "Rule-based SS"







