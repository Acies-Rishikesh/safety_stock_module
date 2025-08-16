import sys, os
import streamlit as st
import pandas as pd

# Guards: must complete Step 1
if "intro_completed" not in st.session_state or not st.session_state.intro_completed:
    st.warning("⚠ Please complete Method Selection before uploading data.")
    st.stop()

# Make backend importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Required columns for each dataset
REQUIRED_COLUMNS = {
    "Past Sales":    ["sku_id", "location_id", "echelon_type", "date", "actual"],
    "Past Forecast": ["sku_id", "location_id", "echelon_type", "date", "forecast", "lead_time"],
    "Future Forecast": ["sku_id", "location_id", "echelon_type", "date", "forecast", "lead_time", "service_level"],
}

# Session keys for storage
DATASET_STATE_KEYS = {
    "Past Sales": "actual_sales_df",
    "Past Forecast": "past_forecast_df",
    "Future Forecast": "future_forecast_df",
}

st.title("Step 2: Upload Data Files")

# Guards: must complete Intro first
if "has_past" not in st.session_state or "method_choice" not in st.session_state:
    st.warning("Please complete Step 1 (Intro) first.")
    st.stop()

has_past = st.session_state["has_past"]
method_choice = st.session_state["method_choice"]

# Required datasets depend on method choice
if has_past and method_choice in ("Only ML", "ML + Rule-based"):
    required_datasets = ["Past Sales", "Past Forecast", "Future Forecast"]
else:
    required_datasets = ["Future Forecast"]

# Initialize upload status
if "upload_status" not in st.session_state:
    st.session_state.upload_status = {name: False for name in REQUIRED_COLUMNS.keys()}

# Ensure keys exist
for name in REQUIRED_COLUMNS.keys():
    st.session_state.upload_status.setdefault(name, False)

# Helper to render required column checklist
def render_column_checklist(dataset_name: str, df: pd.DataFrame | None):
    req_cols = REQUIRED_COLUMNS[dataset_name]
    st.subheader(f"Required columns for {dataset_name}")

    # Table-like layout
    name_col, status_col = st.columns([3, 1])
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

    # Put the whole mapping feature inside expander
    if df is not None:
        with st.expander("Map Columns (click to expand)", expanded=False):
            st.write("Map your dataset columns to required names:")
            for col in req_cols:
                st.selectbox(
                    f"Map for {col}",
                    options=["-- Select --"] + list(df.columns),
                    index=(list(df.columns).index(col) + 1) if col in df.columns else 0,
                    key=f"map_{dataset_name}_{col}_key"
                )

# Dataset dropdown
dataset_to_upload = st.selectbox(
    "Datasets needed (choose one to upload):",
    required_datasets
)

# File uploader
uploaded = st.file_uploader(
    f"Upload {dataset_to_upload} CSV",
    type=["csv"],
    key=f"uploader_{dataset_to_upload}"
)

# Retrieve stored df if available
current_df = st.session_state.get(DATASET_STATE_KEYS[dataset_to_upload], None)

# Handle new upload
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

# Column checklist + mapping (mapping minimized by default)
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

# Submit button with navigation
all_ready = all(st.session_state.upload_status.get(n, False) for n in required_datasets)
if all_ready:
    if st.button("Submit and Go to Results ▶", key="submit_to_results", type="primary"):
        st.session_state["data_uploaded"] = True
        st.switch_page("pages/3_Results.py")
else:
    st.info("Upload all required files to enable **Submit**.")
