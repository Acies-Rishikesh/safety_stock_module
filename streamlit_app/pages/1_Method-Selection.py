# Step 1: Introduction & Method Selection (with gating for Step 2)

import sys, os
import streamlit as st

# Make backend importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend import config

st.set_page_config(page_title="Safety Stock | Intro", layout="wide")

st.title("Method Preference")

# --- State defaults ---
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "has_past" not in st.session_state:
    st.session_state.has_past = None
if "method_choice" not in st.session_state:
    st.session_state.method_choice = None
# Gate for upload page
if "intro_completed" not in st.session_state:
    st.session_state.intro_completed = False

def set_config_flags():
    has_past_bool = bool(st.session_state.has_past)
    config.PAST_SALES_DATA_AVAILABLE = has_past_bool
    config.PAST_FORECAST_DATA_AVAILABLE = has_past_bool
    choice = st.session_state.method_choice or ""
    config.BOTH_RULE_ML = (choice == "ML + Rule-based")
    config.ONLY_ML_BASED = (choice == "Only ML")
    config.ONLY_RULE_BASED = (choice == "Only Rule-based")

# ---------- Step 1 ----------
if st.session_state.wizard_step == 1:
    st.subheader("Past Data Availability")
    st.write("Do you have past **sales** and **forecast** data?")
    st.session_state.has_past = st.radio(
        "Select an option:",
        options=["Yes", "No"],
        index=0 if st.session_state.has_past is None else (0 if st.session_state.has_past else 1)
    ) == "Yes"

    st.divider()
    _, c = st.columns([1, 5])
    with c:
        if st.button("Next"):
            if st.session_state.has_past is None:
                st.warning("Please select Yes or No.")
            else:
                set_config_flags()
                st.session_state.wizard_step = 2
                st.rerun()

# ---------- Step 2 ----------
elif st.session_state.wizard_step == 2:
    st.subheader("Select Calculation Method")

    if st.session_state.has_past:
        st.session_state.method_choice = st.radio(
            "Choose a method:",
            options=["ML + Rule-based", "Only ML", "Only Rule-based"]
        )
    else:
        st.session_state.method_choice = "Only Rule-based"
        st.info("Since you don’t have past data, only Rule-based Safety Stock can be calculated.")

    st.divider()
    st.write(f"**Selected Method:** {st.session_state.method_choice or 'Not selected'}")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back"):
            st.session_state.wizard_step = 1
            st.rerun()
    with col2:
        if st.button("Continue"):
            if st.session_state.has_past and not st.session_state.method_choice:
                st.warning("Please select a method.")
            else:
                set_config_flags()
                st.session_state.intro_completed = True  
                try:
                    st.switch_page("pages/2_Data_Upload.py")
                except Exception:
                    st.success(" Go to **Step 2: Data Upload** from the sidebar.")
