
import sys, os
import streamlit as st
import pandas as pd

# ---------------- Path setup ----------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.preprocessing.input_cleaner import clean_and_prepare_inputs
from backend.module_selector import run_safety_stock_selector

st.set_page_config(page_title="Safety Stock | Upload", layout="wide")

# ---------- Gate ----------
if "intro_completed" not in st.session_state or not st.session_state.intro_completed:
    st.warning("Please complete Step 1: Introduction & Method Selection before uploading data.")
    st.stop()

st.title("Step 2: Upload Data Files")

# ---------- User-defined sample paths ----------
SAMPLE_PATHS = {
    "Past Sales":      os.path.join("data","Past_Sales_Data_v2.csv"),
    "Past Forecast":   os.path.join("data","Past_Forecast_Data_v2.csv"),
    "Future Forecast": os.path.join("data","Future_Forecast_Data_v2.csv"),
}

# ---------- State ----------
has_past = st.session_state.get("has_past", False)
method_choice = st.session_state.get("method_choice", "Only Rule-based")

REQUIRED_COLUMNS = {
    "Past Sales":        ["sku_id", "location_id", "echelon_type", "date", "actual"],
    "Past Forecast":     ["sku_id", "location_id", "echelon_type", "date", "forecast", "lead_time"],
    "Future Forecast":   ["sku_id", "location_id", "echelon_type", "date", "forecast", "lead_time", "service_level"],
}

DATASET_STATE_KEYS = {
    "Past Sales": "actual_sales_df",
    "Past Forecast": "past_forecast_df",
    "Future Forecast": "future_forecast_df",
}

if has_past and method_choice in ("Only ML", "ML + Rule-based"):
    required_datasets = ["Past Sales", "Past Forecast", "Future Forecast"]
else:
    required_datasets = ["Future Forecast"]

if "upload_status" not in st.session_state:
    st.session_state.upload_status = {name: False for name in REQUIRED_COLUMNS.keys()}

if "column_mapping" not in st.session_state:
    st.session_state.column_mapping = {col: col for cols in REQUIRED_COLUMNS.values() for col in cols}


# ---------------- Helper functions ----------------
def render_column_checklist(dataset_name, df: pd.DataFrame | None):
    req_cols = REQUIRED_COLUMNS[dataset_name]
    name_col, status_col = st.columns([4, 1])
    with name_col:
        st.markdown("**Column**")
    with status_col:
        st.markdown("**Status**")
    for col in req_cols:
        has_col = df is not None and col in df.columns
        with name_col:
            st.markdown(col)
        with status_col:
            st.markdown("✅" if has_col else "❌")


def load_samples_into_state():
    for ds in required_datasets:
        path = SAMPLE_PATHS[ds]
        if not os.path.exists(path):
            raise FileNotFoundError(f"Sample file not found: {path}")
        if path.endswith(".csv"):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)
        st.session_state[DATASET_STATE_KEYS[ds]] = df
        st.session_state.upload_status[ds] = True


def process_and_go_to_results():
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
        return

    st.session_state["final_results_original"] = output_df.copy()
    st.session_state["data_uploaded"] = True

    try:
        st.switch_page("pages/3_Results.py")
    except Exception:
        st.session_state.goto_results = True
        st.rerun()


# ---------------- Header actions ----------------
_, right = st.columns([6, 1])
with right:
    if st.button("Use Sample Data"):
        try:
            load_samples_into_state()
            st.success("Sample data loaded successfully.")
            process_and_go_to_results()
        except Exception as e:
            st.error(f"Could not load sample data: {e}")


# ---------------- Manual Upload ----------------
dataset_to_upload = st.selectbox("Choose which dataset to upload:", required_datasets)
uploaded = st.file_uploader(f"Upload {dataset_to_upload} (CSV/Excel)", type=["csv", "xlsx"])

current_df = st.session_state.get(DATASET_STATE_KEYS[dataset_to_upload], None)

if uploaded is not None:
    try:
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)

        st.session_state[DATASET_STATE_KEYS[dataset_to_upload]] = df
        current_df = df

        missing = [c for c in REQUIRED_COLUMNS[dataset_to_upload] if c not in df.columns]
        if missing:
            st.warning(f"Missing columns: {missing}. Use mapping below to fix.")
            st.session_state.upload_status[dataset_to_upload] = False
        else:
            st.success(f"{dataset_to_upload} uploaded successfully.")
            st.session_state.upload_status[dataset_to_upload] = True

    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.session_state.upload_status[dataset_to_upload] = False

render_column_checklist(dataset_to_upload, current_df)

# ---------------- Submit & Process ----------------
all_ready = all(st.session_state.upload_status.get(n, False) for n in required_datasets)
if all_ready:
    if st.button("Submit & Process"):
        process_and_go_to_results()
else:
    st.info("Upload all required files or click 'Use Sample Data' to continue.")
