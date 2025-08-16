import sys, os
import streamlit as st
import pandas as pd

# Add backend path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.preprocessing.input_cleaner import clean_and_prepare_inputs
from backend.module_selector import run_safety_stock_selector
from backend import config as backend_config

st.set_page_config(page_title="Safety Stock | Results", layout="wide")
st.title("Safety Stock Result")

# --- Guards ---
if "data_uploaded" not in st.session_state or not st.session_state["data_uploaded"]:
    st.error("Please Upload Data before viewing results.")
    st.stop()

has_past = st.session_state["has_past"]
method_choice = st.session_state["method_choice"]

# --- Data cleaning ---
if has_past and method_choice in ("Only ML", "ML + Rule-based"):
    if not all(k in st.session_state for k in ["actual_sales_df", "past_forecast_df", "future_forecast_df"]):
        st.error("Some required datasets are missing. Please re-upload in Step 2.")
        st.stop()

    cleaned_forecast, cleaned_actual, cleaned_future_forecast = clean_and_prepare_inputs(
        forecast_df=st.session_state["past_forecast_df"],
        actual_df=st.session_state["actual_sales_df"],
        future_forecast_df=st.session_state["future_forecast_df"],
        column_mapping=backend_config.column_mapping
    )

    output_df = run_safety_stock_selector(
        PAST_SALES_DATA_AVAILABLE=True,
        PAST_FORECAST_DATA_AVAILABLE=True,
        cleaned_future_forecast=cleaned_future_forecast,
        cleaned_actual=cleaned_actual,
        cleaned_forecast=cleaned_forecast
    )

else:
    if "future_forecast_df" not in st.session_state:
        st.error("Missing Future Forecast data. Please upload it in Step 2.")
        st.stop()

    _empty = pd.DataFrame()
    _, _, cleaned_future_forecast = clean_and_prepare_inputs(
        forecast_df=_empty,
        actual_df=_empty,
        future_forecast_df=st.session_state["future_forecast_df"],
        column_mapping=backend_config.column_mapping
    )

    output_df = run_safety_stock_selector(
        PAST_SALES_DATA_AVAILABLE=False,
        PAST_FORECAST_DATA_AVAILABLE=False,
        cleaned_future_forecast=cleaned_future_forecast,
        cleaned_actual=None,
        cleaned_forecast=None
    )

# --- Safety net ---
if output_df is None or output_df.empty:
    st.error("No results were generated. Check method selection and uploaded data.")
    st.stop()

# --- Filters (TOP of page) ---
st.subheader("Filters")
col1, col2, col3, col4 = st.columns(4)

with col1:
    echelons = st.multiselect("Echelon", options=output_df["echelon_type"].unique())
with col2:
    skus = st.multiselect("SKU", options=output_df["sku_id"].unique())
with col3:
    locations = st.multiselect("Location", options=output_df["location_id"].unique())
with col4:
    if pd.api.types.is_datetime64_any_dtype(output_df["date"]):
        dates = st.multiselect("Date", options=output_df["date"].dt.date.unique())
    else:
        dates = st.multiselect("Date", options=output_df["date"].unique())

filtered_df = output_df.copy()
if echelons:
    filtered_df = filtered_df[filtered_df["echelon_type"].isin(echelons)]
if skus:
    filtered_df = filtered_df[filtered_df["sku_id"].isin(skus)]
if locations:
    filtered_df = filtered_df[filtered_df["location_id"].isin(locations)]
if dates:
    if pd.api.types.is_datetime64_any_dtype(filtered_df["date"]):
        filtered_df = filtered_df[filtered_df["date"].dt.date.isin(dates)]
    else:
        filtered_df = filtered_df[filtered_df["date"].isin(dates)]

# --- Results table ---
st.dataframe(filtered_df, use_container_width=True)

# --- Save both filtered & unfiltered for use in other pages ---
st.session_state["final_results_original"] = output_df.copy()   # Unfiltered data
st.session_state["final_results_filtered"] = filtered_df.copy() # Filtered data

# --- Download filtered data ---
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "safety_stock_results.csv", "text/csv")
