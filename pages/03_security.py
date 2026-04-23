from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.data_loader import load_friday_data
from utils.theme import apply_theme, page_header, render_sidebar


st.set_page_config(
    page_title="Security | Friday DC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()

ops, market, ops_log, compliance = load_friday_data()

page_header(
    "Security and Compliance",
    "Physical security controls and checklist alignment with TIA-942 and ISO 27001 expectations.",
)

tier_full = st.selectbox("TIA-942 target tier", ["Tier I", "Tier II", "Tier III", "Tier IV"], index=2)
tier_level = tier_full.split(" ")[1]

checklist = compliance[compliance["tier_level"] == tier_level].dropna(axis=1)
checklist = checklist[["requirement_name", "framework", "status"]].rename(
    columns={"requirement_name": "Control", "framework": "Framework", "status": "Status"}
)

redundancy_mapping = {
    "I": "Basic capacity components",
    "II": "Redundant capacity components",
    "III": "Concurrent maintainability",
    "IV": "Fault tolerance"
}

open_exceptions = int((checklist["Status"] != "Compliant").sum())

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Tier Objective", tier_full)
metric_col2.metric("Redundancy Model", redundancy_mapping.get(tier_level, "Unknown"))
metric_col3.metric("Open Security Exceptions", f"{open_exceptions}")

if open_exceptions > 0:
    st.warning("Active Security Exception: Firmware update pending on core Firewall-02. Scheduled for next maintenance window.")

left_col, right_col = st.columns((1.2, 1), gap="large")

with left_col:
    st.subheader("Compliance checklist")
    st.dataframe(checklist, use_container_width=True, hide_index=True)

with right_col:
    st.subheader("Physical control summary")
    sec_ops = ops_log[(ops_log["record_type"] == "SECURITY") & (ops_log["control_category"] == "Physical")].dropna(axis=1)
    if not sec_ops.empty:
        controls = sec_ops[["control_name", "control_score"]].rename(columns={"control_name": "Control", "control_score": "Score"}).set_index("Control")
        st.bar_chart(controls, use_container_width=True)
    st.caption("The selected TIA-942 tier changes the checklist, exception count and target control posture.")

st.subheader("Operations status relevant to security")
status_table = ops["status"].value_counts(dropna=False).rename_axis("Status").to_frame("Records").reset_index()
def get_security_impact(status):
    if pd.isna(status): return "Unknown"
    status = str(status).lower()
    if status == "critical": return "High (e.g. Unauthorized Access Detected)"
    if status == "warning": return "Medium (e.g. Door Left Open)"
    if status == "maintenance": return "Low (Supervised)"
    return "Nominal"
status_table["Security Impact"] = status_table["Status"].apply(get_security_impact)
st.dataframe(status_table, use_container_width=True, hide_index=True)

st.caption("Compliance logic based on TIA-942-B Telecommunications Infrastructure Standard for Data Centers.")
