import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy.stats import norm


def calculate_ml_based_safety_stock(
    past_sales_df, past_forecast_df, future_forecast_df, service_level=0.9
):
    """
    Calculate safety stock per SKU-location-echelon-date using ML to predict forecast error variability.

    Args:
        past_sales_df (pd.DataFrame): Historical actual sales data
        past_forecast_df (pd.DataFrame): Historical forecast data
        future_forecast_df (pd.DataFrame): Future forecast data
        service_level (float): Desired service level (default=0.9 for 90%)

    Returns:
        pd.DataFrame: future_forecast_df with 'Safety_Stock' column
    """

    # Merge past sales with past forecast to calculate errors
    merge_keys = ["sku_id", "location_id", "echelon_type", "date"]
    past_df = pd.merge(
        past_sales_df,
        past_forecast_df,
        on=merge_keys,
        suffixes=('_act', '_fcst')
    )

    # Calculate forecast error (actual - forecast)
    past_df["error"] = past_df["actual"] - past_df["forecast"]
    past_df["abs_error"] = past_df["error"].abs()

    # Columns never used as features
    drop_cols = [
        "actual", "forecast", "error", "abs_error",
        "sku_id", "location_id", "echelon_type", "date"
    ]

    # Z-score for desired service level (from normal distribution)
    z_score = norm.ppf(service_level)

    results = []

    # Process each SKU/location/echelon group separately
    for (sku, loc, echelon), sku_df in past_df.groupby(["sku_id", "location_id", "echelon_type"]):

        # Feature columns in past merged dataset (include _act/_fcst)
        past_feature_cols = [col for col in sku_df.columns if col not in drop_cols]

        # Map to possible future dataset column names (remove suffixes)
        future_feature_cols = [c.replace('_act', '').replace('_fcst', '') for c in past_feature_cols]

        # Keep only those columns that actually exist in future_forecast_df
        future_feature_cols = [c for c in future_feature_cols if c in future_forecast_df.columns]

        # One-hot encode & deduplicate training features
        X = pd.get_dummies(sku_df[past_feature_cols], drop_first=True)
        X = X.loc[:, ~X.columns.duplicated()]

        y = sku_df["abs_error"]

        # Get relevant rows in future forecast
        future_subset = future_forecast_df[
            (future_forecast_df["sku_id"] == sku) &
            (future_forecast_df["location_id"] == loc) &
            (future_forecast_df["echelon_type"] == echelon)
        ]

        if future_subset.empty:
            continue

        # Fallback if not enough historical data or no variance in y
        if len(X) < 5 or y.nunique() <= 1:
            fallback_std = y.std(ddof=0) if len(y) > 0 else 0
            fallback_ss = z_score * fallback_std
            for _, row in future_subset.iterrows():
                results.append({
                    "sku_id": row["sku_id"],
                    "location_id": row["location_id"],
                    "echelon_type": row["echelon_type"],
                    "date": row["date"],
                    "Safety_Stock": fallback_ss
                })
            continue

        # Train ML model
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        model = RandomForestRegressor(n_estimators=200, random_state=42)
        model.fit(X_train, y_train)

        # Prepare future features
        future_features = pd.get_dummies(future_subset[future_feature_cols], drop_first=True)
        future_features = future_features.loc[:, ~future_features.columns.duplicated()]

        # Align with training columns
        future_features = future_features.reindex(columns=X.columns, fill_value=0)

        # Predict future abs_error (std proxy)
        predicted_abs_error = model.predict(future_features)

        # Compute safety stock
        safety_stock = z_score * predicted_abs_error

        for i, (_, row) in enumerate(future_subset.iterrows()):
            results.append({
                "sku_id": row["sku_id"],
                "location_id": row["location_id"],
                "echelon_type": row["echelon_type"],
                "date": row["date"],
                "Safety_Stock": safety_stock[i]
            })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Merge results into future forecast
    output_df = pd.merge(
        future_forecast_df, results_df,
        on=["sku_id", "location_id", "echelon_type", "date"],
        how="left"
    )

    output_df.to_excel("final.xlsx",index=False)

    return output_df




