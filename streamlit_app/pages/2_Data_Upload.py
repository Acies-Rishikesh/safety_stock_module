import sys, os
import streamlit as st
import pandas as pd

# Add backend path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.preprocessing.input_cleaner import clean_and_prepare_inputs
from backend.module_selector import run_safety_stock_selector
from backend import config as backend_config

st.set_page_config(page_title="Safety Stock | Upload", layout="wide")

# ---------- Gate: only after Intro ----------
if "intro_completed" not in st.session_state or not st.session_state.intro_completed:
    st.warning("Please complete **Step 1: Introduction & Method Selection** before uploading data.")
    st.stop()

st.title("Step 2: Upload Data Files")

# ---------- State ----------
has_past = st.session_state.get("has_past", False)
method_choice = st.session_state.get("method_choice", "Only Rule-based")

# Required columns for each dataset
REQUIRED_COLUMNS = {
    "Past Sales":    ["sku_id", "location_id", "echelon_type", "date", "actual"],
    "Past Forecast": ["sku_id", "location_id", "echelon_type", "date", "forecast", "lead_time"],
    "Future Forecast": ["sku_id", "location_id", "echelon_type", "date", "forecast", "lead_time", "service_level"],
}

# Session keys
DATASET_STATE_KEYS = {
    "Past Sales": "actual_sales_df",
    "Past Forecast": "past_forecast_df",
    "Future Forecast": "future_forecast_df",
}

# Which datasets are required?
if has_past and method_choice in ("Only ML", "ML + Rule-based"):
    required_datasets = ["Past Sales", "Past Forecast", "Future Forecast"]
else:
    required_datasets = ["Future Forecast"]

# Init upload status
if "upload_status" not in st.session_state:
    st.session_state.upload_status = {name: False for name in REQUIRED_COLUMNS.keys()}

# Init column mapping
if "column_mapping" not in st.session_state:
    st.session_state.column_mapping = {col: col for cols in REQUIRED_COLUMNS.values() for col in cols}

# ---------------- Helper: render checklist ----------------
def render_column_checklist(dataset_name: str, df: pd.DataFrame | None):
    req_cols = REQUIRED_COLUMNS[dataset_name]
    name_col, status_col = st.columns([4, 1])
    with name_col:
        st.markdown("**Column**")
    with status_col:
        st.markdown("**Status**")
    for col in req_cols:
        has_col = df is not None and isinstance(df, pd.DataFrame) and col in df.columns
        with name_col:
            st.markdown(col)
        with status_col:
            st.markdown("✅" if has_col else "❌")

# ---------------- File Uploader (one dataset at a time) ----------------
dataset_to_upload = st.selectbox(
    "Choose which dataset to upload:",
    required_datasets
)

uploaded = st.file_uploader(
    f"Upload {dataset_to_upload} CSV",
    type=["csv"],
    key=f"uploader_{dataset_to_upload}"
)

current_df = st.session_state.get(DATASET_STATE_KEYS[dataset_to_upload], None)

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)

        # Save uploaded
        st.session_state[DATASET_STATE_KEYS[dataset_to_upload]] = df
        current_df = df

        # Mark upload status
        missing = [c for c in REQUIRED_COLUMNS[dataset_to_upload] if c not in df.columns]
        if missing:
            st.warning(f"Some expected columns missing: {missing}. Use mapping below to fix.")
            st.session_state.upload_status[dataset_to_upload] = False
        else:
            st.success(f"{dataset_to_upload} uploaded successfully ✅")
            st.session_state.upload_status[dataset_to_upload] = True

    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        st.session_state.upload_status[dataset_to_upload] = False

# Show checklist
render_column_checklist(dataset_to_upload, current_df)

# ---------------- Column Mapping (minimized view) ----------------
if current_df is not None:
    with st.expander("Map columns (only if your CSV uses different names)", expanded=False):
        mapping = {}
        for req in REQUIRED_COLUMNS[dataset_to_upload]:
            options = [req] + list(current_df.columns)
            default_idx = options.index(req) if req in current_df.columns else 0
            sel = st.selectbox(f"Map for `{req}`", options, index=default_idx, key=f"map_{dataset_to_upload}_{req}")
            mapping[req] = sel

        # Save mapping
        st.session_state.column_mapping.update(mapping)

# ---------------- Upload Status Summary ----------------
st.subheader("Upload Status")
status_rows = []
for name in ["Past Sales", "Past Forecast", "Future Forecast"]:
    if name in required_datasets:
        ok = st.session_state.upload_status.get(name, False)
        status_rows.append({"Dataset": name, "Status": "✅ Uploaded" if ok else "❌ Not uploaded"})
    else:
        status_rows.append({"Dataset": name, "Status": "— Not needed"})
st.dataframe(pd.DataFrame(status_rows), use_container_width=True)

# ---------------- Submit & Process ----------------
all_ready = all(st.session_state.upload_status.get(n, False) for n in required_datasets)

if all_ready:
    if st.button("Submit & Process"):
        # Run backend pipeline
        if has_past and method_choice in ("Only ML", "ML + Rule-based"):
            cleaned_forecast, cleaned_actual, cleaned_future_forecast = clean_and_prepare_inputs(
                forecast_df=st.session_state["past_forecast_df"],
                actual_df=st.session_state["actual_sales_df"],
                future_forecast_df=st.session_state["future_forecast_df"],
                column_mapping=st.session_state["column_mapping"]
            )
            output_df = run_safety_stock_selector(
                PAST_SALES_DATA_AVAILABLE=True,
                PAST_FORECAST_DATA_AVAILABLE=True,
                cleaned_future_forecast=cleaned_future_forecast,
                cleaned_actual=cleaned_actual,
                cleaned_forecast=cleaned_forecast
            )
        else:
            _empty = pd.DataFrame()
            _, _, cleaned_future_forecast = clean_and_prepare_inputs(
                forecast_df=_empty,
                actual_df=_empty,
                future_forecast_df=st.session_state["future_forecast_df"],
                column_mapping=st.session_state["column_mapping"]
            )
            output_df = run_safety_stock_selector(
                PAST_SALES_DATA_AVAILABLE=False,
                PAST_FORECAST_DATA_AVAILABLE=False,
                cleaned_future_forecast=cleaned_future_forecast,
                cleaned_actual=None,
                cleaned_forecast=None
            )

        if output_df is None or output_df.empty:
            st.error("Processing complete, but no results were generated. Please check your data.")
        else:
            # Save for Results & Dashboard
            st.session_state["final_results_original"] = output_df.copy()
            st.session_state["data_uploaded"] = True
            st.success("✅ Data processed successfully! Redirecting to Results...")

            try:
                # Redirect directly to Step 3 Results
                st.switch_page("pages/3_Results.py")
            except Exception:
                # Fallback if switch_page not available
                st.session_state.goto_results = True
                st.rerun()
else:
    st.info("Upload all required files to enable **Submit & Process**.")

# --- Fallback redirect if switch_page not supported ---
if st.session_state.get("goto_results", False):
    st.session_state.goto_results = False
    st.switch_page("pages/3_Results.py")
