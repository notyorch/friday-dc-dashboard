from __future__ import annotations

import altair as alt
import streamlit as st

from utils.data_loader import load_friday_data
from utils.theme import apply_theme, page_header, render_sidebar


st.set_page_config(
    page_title="Energy | Friday DC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()

ops, market, ops_log, compliance = load_friday_data()

daily_energy = (
    ops.set_index("timestamp")
    .resample("D")
    .agg(avg_pue=("pue_ratio", "mean"), avg_power_kw=("power_usage_kw", "mean"))
    .dropna(how="all")
)

page_header(
    "Energy Efficiency",
    "PUE monitoring, energy consumption behavior and a native calculator for improvement scenarios.",
)

col1, col2, col3 = st.columns(3)
col1.metric("Current Avg. PUE", f"{daily_energy['avg_pue'].tail(7).mean():.2f}")
col2.metric("Average Load", f"{daily_energy['avg_power_kw'].tail(7).mean():.1f} kW")
col3.metric("Best Daily PUE", f"{daily_energy['avg_pue'].min():.2f}", help="Industry benchmark: Google Datacenters avg 1.10 PUE")

st.subheader("PUE and power trend")
base = alt.Chart(daily_energy.tail(30).reset_index()).encode(x=alt.X("timestamp:T", title=None))
pue_line = base.mark_line(color="#e8e8e8", size=3).encode(y=alt.Y("avg_pue:Q", title="Avg PUE", scale=alt.Scale(domain=[1.0, 2.0])))
power_line = base.mark_line(color="#8a8a8a", strokeDash=[5, 5]).encode(y=alt.Y("avg_power_kw:Q", title="Load (kW)"))
dual_chart = alt.layer(pue_line, power_line).resolve_scale(y="independent").properties(height=300)
st.altair_chart(dual_chart, use_container_width=True)

st.subheader("PUE improvement calculator")
calc_col1, calc_col2, calc_col3 = st.columns(3)

with calc_col1:
    current_pue = st.number_input("Current PUE", min_value=1.00, max_value=2.50, value=float(daily_energy['avg_pue'].tail(7).mean()), step=0.01)
with calc_col2:
    it_load_kw = st.number_input("IT load (kW)", min_value=50, max_value=5000, value=480, step=10)
with calc_col3:
    cooling_gain = st.slider("Cooling optimization", min_value=0, max_value=20, value=8, help="Simulates efficiency gains via containment or liquid cooling introduction.")

estimated_pue = max(1.10, current_pue - (cooling_gain * 0.01))
annual_saving_kwh = max(0, int((current_pue - estimated_pue) * it_load_kw * 24 * 365))

result_col1, result_col2 = st.columns(2)
result_col1.metric("Estimated New PUE", f"{estimated_pue:.2f}", delta=f"{estimated_pue - current_pue:.2f}")
annual_usd = annual_saving_kwh * 0.10
result_col2.metric("Estimated Annual Saving", f"{annual_saving_kwh:,} kWh", help=f"Estimated ~${annual_usd:,.0f} USD at $0.10/kWh")

st.info("Recommended use: compare the current baseline against a better airflow or liquid cooling scenario.")
