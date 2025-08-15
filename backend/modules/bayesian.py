# import pandas as pd
# import numpy as np
# import pymc as pm
# import arviz as az
# from scipy.stats import norm

# def calculate_bayesian_safety_stock(past_sales_df, past_forecast_df, future_forecast_df, service_level=0.9, draws=2000, tune=1000):
#     """
#     Bayesian hierarchical model to estimate safety stock per SKU-location-echelon-date.

#     Args:
#         past_sales_df (pd.DataFrame): Historical actual sales—must include sku_id, location_id, echelon_type, date, actual
#         past_forecast_df (pd.DataFrame): Historical forecast—must include sku_id, location_id, echelon_type, date, forecast
#         future_forecast_df (pd.DataFrame): Data to produce safety stock for, must include sku_id, location_id, echelon_type, date, forecast, lead_time
#         service_level (float): Desired service level (default 0.9)
#         draws (int): Number of posterior samples to draw
#         tune (int): Number of tuning steps

#     Returns:
#         pd.DataFrame: future_forecast_df with new column 'bayesian_safety_stock'
#     """

#     # Merge past actual and forecast to compute historical errors
#     merge_keys = ['sku_id', 'location_id', 'echelon_type', 'date']
#     past = pd.merge(past_sales_df, past_forecast_df, on=merge_keys, suffixes=('_act', '_fcst'))
#     past['error'] = past['actual'] - past['forecast']

#     # Prepare an output column in future forecasts
#     future_forecast_df = future_forecast_df.copy()
#     future_forecast_df['bayesian_safety_stock'] = np.nan

#     # Calculate z-score for service level
#     z = norm.ppf(service_level)

#     # Process each SKU-location-echelon group independently
#     groups = past.groupby(['sku_id', 'location_id', 'echelon_type'])

#     for (sku, loc, echelon), group in groups:
#         errors = group['error'].values

#         if len(errors) < 5:
#             # Not enough data to reliably estimate variability; fallback to zero or simple rule
#             # Fill safety stock with zeros or a fallback value
#             future_rows = future_forecast_df[
#                 (future_forecast_df['sku_id'] == sku) & 
#                 (future_forecast_df['location_id'] == loc) &
#                 (future_forecast_df['echelon_type'] == echelon)
#             ]
#             future_forecast_df.loc[future_rows.index, 'bayesian_safety_stock'] = 0.0
#             continue

#         # Bayesian model: assume errors ~ Normal(mu, sigma), mu ~ Normal(0, 5), sigma ~ HalfNormal(5)
#         with pm.Model() as model:
#             mu = pm.Normal('mu', mu=0, sigma=5)
#             sigma = pm.HalfNormal('sigma', sigma=5)
#             obs = pm.Normal('obs', mu=mu, sigma=sigma, observed=errors)

#             trace = pm.sample(draws=draws, tune=tune, chains=2, target_accept=0.9, progressbar=False, random_seed=42)

#         # Extract posterior sigma (variability) estimate as mean of samples
#         posterior_sigma = np.mean(trace.posterior['sigma'].values)

#         # Calculate safety stock per corresponding future forecast row using formula Z*sigma*sqrt(lead_time)
#         future_rows = future_forecast_df[
#             (future_forecast_df['sku_id'] == sku) & 
#             (future_forecast_df['location_id'] == loc) &
#             (future_forecast_df['echelon_type'] == echelon)
#         ]

#         for idx, row in future_rows.iterrows():
#             lead_time = row['lead_time']
#             safety_stock = z * posterior_sigma * np.sqrt(lead_time)
#             future_forecast_df.at[idx, 'bayesian_safety_stock'] = round(safety_stock, 2)

#     return future_forecast_df
