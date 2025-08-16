import sys, os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.modules.rule_based import calculate_rule_based_safety_stock_df

st.set_page_config(page_title="Safety Stock | Scenario Planner", layout="wide")
st.title("Dashboard & Scenario Planner")

# --- Guards: require unfiltered results from Results page ---
if "final_results_original" not in st.session_state or st.session_state["final_results_original"] is None:
    st.error("Original results not found. Please run Step 3: Results first.")
    st.stop()

base_df = st.session_state["final_results_original"].copy()
if base_df.empty:
    st.error("No data available. Please generate results in Step 3.")
    st.stop()

# --- Ensure required columns exist ---
for col in ["sku_id", "location_id", "echelon_type", "date", "forecast", "lead_time", "service_level"]:
    if col not in base_df.columns:
        base_df[col] = np.nan

if not pd.api.types.is_datetime64_any_dtype(base_df["date"]):
    base_df["date"] = pd.to_datetime(base_df["date"], errors="coerce")

# ---------------- Dashboard Filters (do not affect Results page) ----------------
st.markdown("### Filter Data for Analysis")
fc1, fc2, fc3, fc4 = st.columns(4)
with fc1:
    echelons = st.multiselect("Echelon", sorted(base_df["echelon_type"].dropna().unique()))
with fc2:
    skus = st.multiselect("SKU", sorted(base_df["sku_id"].dropna().unique()))
with fc3:
    locations = st.multiselect("Location", sorted(base_df["location_id"].dropna().unique()))
with fc4:
    if base_df["date"].notna().any():
        min_d, max_d = base_df["date"].min().date(), base_df["date"].max().date()
        date_range = st.date_input("Date range", value=(min_d, max_d))
    else:
        date_range = ()

filtered = base_df.copy()
if echelons:
    filtered = filtered[filtered["echelon_type"].isin(echelons)]
if skus:
    filtered = filtered[filtered["sku_id"].isin(skus)]
if locations:
    filtered = filtered[filtered["location_id"].isin(locations)]
if isinstance(date_range, (list, tuple)) and len(date_range) == 2 and all(date_range):
    start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["date"] >= start_d) & (filtered["date"] <= end_d)]

if filtered.empty:
    st.info("No rows after applying filters.")
    st.stop()

# ---------------- Baseline Safety Stock ----------------
baseline_df = filtered.copy()
if "service_level" not in baseline_df.columns or baseline_df["service_level"].isna().all():
    baseline_df["service_level"] = 0.95

if "rule_ss" not in baseline_df.columns:
    rb_base = calculate_rule_based_safety_stock_df(baseline_df)
    baseline_df["rule_ss"] = rb_base["rule_ss"]

# KPIs
rule_ss_num = pd.to_numeric(baseline_df["rule_ss"], errors="coerce")
total_ss = float(rule_ss_num.sum(skipna=True))
avg_ss_per_sku = (
    rule_ss_num.groupby(baseline_df["sku_id"]).sum().mean()
    if "sku_id" in baseline_df.columns else np.nan
)
sku_cnt = int(baseline_df["sku_id"].nunique())
loc_cnt = int(baseline_df["location_id"].nunique())
ech_cnt = int(baseline_df["echelon_type"].nunique())

# --- Uniform KPI card style ---
kpi_style = """
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; 
                height: 140px; display: flex; flex-direction: column; 
                justify-content: center;">
        <h3 style="margin: 0; color: #2c3e50; font-size: 16px;">{label}</h3>
        <h2 style="margin: 5px 0; color: #2980b9; font-size: 32px; font-weight: bold;">{value}</h2>
    </div>
"""

# ======= KPI (Responsive, Equal, Wider) =======
# compute metrics
rule_ss_num = pd.to_numeric(baseline_df["rule_ss"], errors="coerce")
total_ss = float(rule_ss_num.sum(skipna=True))
avg_ss_per_sku = (
    rule_ss_num.groupby(baseline_df["sku_id"]).sum().mean()
    if "sku_id" in baseline_df.columns else np.nan
)
sku_cnt = int(baseline_df["sku_id"].nunique())
loc_cnt = int(baseline_df["location_id"].nunique())
ech_cnt = int(baseline_df["echelon_type"].nunique())

# make the central content area wider (optional; helps KPI width)
st.markdown("""
<style>
/* widen Streamlit content area */
.block-container { max-width: 1400px; padding-left: 1.5rem; padding-right: 1.5rem; }

/* KPI grid: each card min 260px wide, grows to fill; equal heights via fixed height */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-top: 6px;
}

/* KPI card styling */
.kpi-card {
  background: #f8f9fa;
  border-radius: 12px;
  height: 150px;                       /* set equal height */
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  justify-content: center;             /* vertical center */
  align-items: center;                 /* horizontal center */
  padding: 18px;
}

/* label + value */
.kpi-label {
  margin: 0;
  color: #2c3e50;
  font-size: 15px;
  line-height: 1.2;
  text-align: center;
}
.kpi-value {
  margin: 6px 0 0 0;
  color: #1f77b4;
  font-size: 34px;                     /* bigger number */
  font-weight: 700;
  line-height: 1.1;
  text-align: center;
  word-break: break-word;
}
</style>
""", unsafe_allow_html=True)

st.markdown("### Baseline KPIs")
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">No. of Locations</div>
    <div class="kpi-value">{loc_cnt:,}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">No. of Echelons</div>
    <div class="kpi-value">{ech_cnt:,}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Unique SKUs</div>
    <div class="kpi-value">{sku_cnt:,}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Safety Stock</div>
    <div class="kpi-value">{total_ss:,.0f}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Avg SS per SKU</div>
    <div class="kpi-value">{avg_ss_per_sku:,.2f}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- Baseline Charts ----------------
st.subheader("Baseline Charts")
top_n = st.slider("Top N SKUs for charts", min_value=3, max_value=50, value=10, step=1)

ss_by_sku = (
    baseline_df.groupby("sku_id", dropna=False)["rule_ss"]
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .reset_index()
)
if not ss_by_sku.empty:
    fig_top = px.bar(
        ss_by_sku, x="sku_id", y="rule_ss",
        title=f"Top {top_n} SKUs by Total Rule-based Safety Stock",
        labels={"sku_id": "SKU", "rule_ss": "Total Safety Stock"},
        text_auto=True
    )
    fig_top.update_layout(xaxis_tickangle=-30, hovermode="x unified")
    st.plotly_chart(fig_top, use_container_width=True)

if baseline_df["echelon_type"].notna().any():
    share_df = baseline_df.groupby("echelon_type", dropna=False)["rule_ss"].sum().reset_index()
    name_col = "echelon_type"
    title = "Safety Stock Share by Echelon"
else:
    share_df = baseline_df.groupby("location_id", dropna=False)["rule_ss"].sum().reset_index()
    name_col = "location_id"
    title = "Safety Stock Share by Location"

if not share_df.empty:
    fig_share = px.pie(share_df, names=name_col, values="rule_ss", hole=0.45, title=title)
    fig_share.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_share, use_container_width=True)

# ===================== Scenario Manager =====================
st.markdown("---")
st.header("Scenario Manager")

# Store scenarios in session
if "scenarios" not in st.session_state:
    st.session_state["scenarios"] = {}  # {name: {"service_level":..., "lead_time_mult":..., "demand_mult":..., "df":...}}

def build_scenario_df(source_df: pd.DataFrame, service_level: float, lt_mult: float, demand_mult: float) -> pd.DataFrame:
    sc_df = source_df.copy()
    sc_df["service_level"] = service_level
    if "lead_time" in sc_df.columns and sc_df["lead_time"].notna().any():
        sc_df["lead_time"] = sc_df["lead_time"] * lt_mult
    if "forecast" in sc_df.columns and sc_df["forecast"].notna().any():
        sc_df["forecast"] = sc_df["forecast"] * demand_mult
    rb = calculate_rule_based_safety_stock_df(sc_df)
    sc_df["rule_ss"] = rb["rule_ss"]
    return sc_df

with st.expander("Add or Update Scenario", expanded=True):
    f1, f2, f3, f4 = st.columns([2,1,1,1])
    with f1:
        sc_name = st.text_input("Scenario Name", value="Scenario A")
    with f2:
        sc_service = st.number_input("Service Level (%)", min_value=50.0, max_value=99.9, value=95.0, step=0.1) / 100
    with f3:
        sc_lt_mult = st.number_input("Lead Time Multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
    with f4:
        sc_demand_mult = st.number_input("Demand Multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

    cadd, cdel, creset = st.columns([1,1,1])
    with cadd:
        if st.button("Save / Recompute Scenario", use_container_width=True):
            sc_df = build_scenario_df(baseline_df, sc_service, sc_lt_mult, sc_demand_mult)
            st.session_state["scenarios"][sc_name] = {
                "service_level": sc_service,
                "lead_time_mult": sc_lt_mult,
                "demand_mult": sc_demand_mult,
                "df": sc_df
            }
            st.success(f"Saved scenario: {sc_name}")
    with cdel:
        if st.button("Delete Scenario", use_container_width=True) and sc_name in st.session_state["scenarios"]:
            del st.session_state["scenarios"][sc_name]
            st.warning(f"Deleted scenario: {sc_name}")
    with creset:
        if st.button("Clear All Scenarios", use_container_width=True):
            st.session_state["scenarios"].clear()
            st.info("All scenarios cleared.")

# Summary table of saved scenarios
if st.session_state["scenarios"]:
    meta_rows = []
    for nm, meta in st.session_state["scenarios"].items():
        total = float(pd.to_numeric(meta["df"]["rule_ss"], errors="coerce").sum(skipna=True))
        meta_rows.append({
            "Scenario": nm,
            "Service Level": round(meta["service_level"], 4),
            "Lead Time Mult": meta["lead_time_mult"],
            "Demand Mult": meta["demand_mult"],
            "Total Safety Stock": total
        })
    meta_df = pd.DataFrame(meta_rows).sort_values("Scenario")
    st.dataframe(meta_df, use_container_width=True)

# Picker to compare 2 or more scenarios
scenario_names = list(st.session_state["scenarios"].keys())
selected_scenarios = st.multiselect("Select scenarios to compare (2+ recommended)", scenario_names, default=scenario_names[:2] if len(scenario_names) >= 2 else [])

# KPI comparison row
baseline_total = float(pd.to_numeric(baseline_df["rule_ss"], errors="coerce").sum(skipna=True))
kpi_comp = [{"Scenario": "Baseline", "Total Safety Stock": baseline_total, "Change % vs Baseline": 0.0}]
for nm in selected_scenarios:
    total = float(pd.to_numeric(st.session_state["scenarios"][nm]["df"]["rule_ss"], errors="coerce").sum(skipna=True))
    chg = ((total - baseline_total) / baseline_total) * 100 if baseline_total else np.nan
    kpi_comp.append({"Scenario": nm, "Total Safety Stock": total, "Change % vs Baseline": chg})
st.subheader("KPI Comparison")
st.dataframe(pd.DataFrame(kpi_comp), use_container_width=True)

# ===================== Chart Analysis =====================
st.subheader("Chart Analysis")
chart_option = st.selectbox(
    "Select chart type",
    [
        "Baseline vs Scenarios by SKU (Bar)",
        "Baseline vs Scenarios by SKU (Line)",
        "Baseline vs Scenarios Trend Over Time"
    ],
    index=0
)

# Common: build combined data for chosen scenarios
def combine_sku_aggregate(df: pd.DataFrame, label: str) -> pd.DataFrame:
    tmp = df.groupby("sku_id", dropna=False)["rule_ss"].sum().reset_index()
    tmp["Scenario"] = label
    return tmp

def combine_date_aggregate(df: pd.DataFrame, label: str) -> pd.DataFrame:
    tmp = df.dropna(subset=["date"]).groupby("date", dropna=False)["rule_ss"].sum().reset_index()
    tmp["Scenario"] = label
    return tmp

# Respect top_n SKUs based on Baseline
top_skus = (
    baseline_df.groupby("sku_id", dropna=False)["rule_ss"]
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .index
)

if chart_option in ["Baseline vs Scenarios by SKU (Bar)", "Baseline vs Scenarios by SKU (Line)"]:
    combined = [combine_sku_aggregate(baseline_df, "Baseline")]
    for nm in selected_scenarios:
        combined.append(combine_sku_aggregate(st.session_state["scenarios"][nm]["df"], nm))
    sku_long = pd.concat(combined, ignore_index=True)
    sku_long = sku_long[sku_long["sku_id"].isin(top_skus)].rename(columns={"rule_ss": "Safety Stock"})

    if chart_option == "Baseline vs Scenarios by SKU (Bar)":
        fig = px.bar(
            sku_long, x="sku_id", y="Safety Stock", color="Scenario",
            barmode="group", title="Baseline vs Scenarios Safety Stock by SKU (Top N)"
        )
    else:  # Line
        fig = px.line(
            sku_long, x="sku_id", y="Safety Stock", color="Scenario",
            markers=True, title="Baseline vs Scenarios Safety Stock by SKU (Top N)"
        )
    fig.update_layout(xaxis_title="SKU", yaxis_title="Safety Stock", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Baseline vs Scenarios Trend Over Time":
    # Trend style toggle
    trend_style = st.radio("Trend style", ["Line", "Bar"], index=0, horizontal=True)

    combined_t = [combine_date_aggregate(baseline_df, "Baseline")]
    for nm in selected_scenarios:
        combined_t.append(combine_date_aggregate(st.session_state["scenarios"][nm]["df"], nm))
    trend_long = pd.concat(combined_t, ignore_index=True).rename(columns={"rule_ss": "Safety Stock"})

    if not pd.api.types.is_datetime64_any_dtype(trend_long["date"]):
        st.info("Date column missing or invalid. Trend chart cannot be rendered.")
    else:
        if trend_style == "Line":
            fig_t = px.line(
                trend_long, x="date", y="Safety Stock", color="Scenario",
                markers=True, title="Baseline vs Scenarios Safety Stock Trend"
            )
        else:
            fig_t = px.bar(
                trend_long, x="date", y="Safety Stock", color="Scenario",
                barmode="group", title="Baseline vs Scenarios Safety Stock Trend"
            )
        fig_t.update_layout(xaxis_title="Date", yaxis_title="Safety Stock", hovermode="x unified")
        st.plotly_chart(fig_t, use_container_width=True)
