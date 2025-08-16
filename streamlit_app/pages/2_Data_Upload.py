# Step 2: Upload Data Files (visible only after Intro's Continue)

import sys, os
import streamlit as st
import pandas as pd

# Make backend importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

st.set_page_config(page_title="Safety Stock | Upload", layout="wide")

# ---------- Gate: only after Intro ----------
if "intro_completed" not in st.session_state or not st.session_state.intro_completed:
    st.warning("Please complete **Step 1: Introduction & Method Selection** before uploading data.")
    st.stop()

st.title("Step 2: Upload Data Files")

# Guards for method choice
if "has_past" not in st.session_state or "method_choice" not in st.session_state:
    st.warning("Please complete Step 1 (Intro) first.")
    st.stop()

has_past = st.session_state["has_past"]
method_choice = st.session_state["method_choice"]

# Required columns
REQUIRED_COLUMNS = {
    "Past Sales":    ["sku_id", "location_id", "echelon_type", "date", "actual"],
    "Past Forecast": ["sku_id", "location_id", "echelon_type", "date", "forecast", "lead_time"],
    "Future Forecast": ["sku_id", "location_id", "echelon_type", "date", "forecast", "lead_time", "service_level"],
}

# Session keys (align with Results page & backend)
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

# Ensure keys exist
for name in REQUIRED_COLUMNS.keys():
    st.session_state.upload_status.setdefault(name, False)

# Helper: per-column tick/cross checklist
def render_column_checklist(dataset_name: str, df: pd.DataFrame | None):
    req_cols = REQUIRED_COLUMNS[dataset_name]
    st.subheader(f"Required columns for {dataset_name}")
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

# Dataset dropdown
dataset_to_upload = st.selectbox(
    "Datasets needed (choose one to upload):",
    required_datasets
)

# Uploader
uploaded = st.file_uploader(
    f"Upload {dataset_to_upload} CSV",
    type=["csv"],
    key=f"uploader_{dataset_to_upload}"
)

# Previously uploaded df (if any)
current_df = st.session_state.get(DATASET_STATE_KEYS[dataset_to_upload], None)

# Handle upload
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        missing = [c for c in REQUIRED_COLUMNS[dataset_to_upload] if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
            st.session_state.upload_status[dataset_to_upload] = False
        else:
            st.success(f"{dataset_to_upload} uploaded successfully ✅")
            st.session_state.upload_status[dataset_to_upload] = True
        st.session_state[DATASET_STATE_KEYS[dataset_to_upload]] = df
        current_df = df
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        st.session_state.upload_status[dataset_to_upload] = False

# Checklist for the selected dataset
render_column_checklist(dataset_to_upload, current_df)

# Status board
st.subheader("Upload status summary")
status_rows = []
for name in ["Past Sales", "Past Forecast", "Future Forecast"]:
    if name in required_datasets:
        ok = st.session_state.upload_status.get(name, False)
        status_rows.append({"Dataset": name, "Status": "✅ Uploaded" if ok else "❌ Not uploaded"})
    else:
        status_rows.append({"Dataset": name, "Status": "— Not needed"})
st.dataframe(pd.DataFrame(status_rows), use_container_width=True)

# Submit logic
# Submit logic
all_ready = all(st.session_state.upload_status.get(n, False) for n in required_datasets)

if all_ready:
    if st.button("Submit ", type="primary"):
        st.session_state["data_uploaded"] = True
        # 🔀 Jump to the Results page (adjust path/name if yours differs)
        st.switch_page("pages/3_Results.py")
else:
    st.info("Upload all required files to enable **Submit**.")

