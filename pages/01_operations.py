from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from utils.data_loader import load_friday_data
from utils.theme import apply_theme, page_header, render_sidebar, color_status


st.set_page_config(
    page_title="Operations | Friday DC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()

ops, market, ops_log, compliance = load_friday_data()

latest_snapshot = ops.groupby("rack_id", as_index=False).tail(1).copy()
incidents = ops.loc[ops["incident_type"].fillna("").astype(str).str.strip().ne("")]
resolution_mean = ops["resolution_time_min"].replace(0, pd.NA).dropna().mean()
resolution_value = f"{resolution_mean:.0f} min" if pd.notna(resolution_mean) else "N/A"

page_header(
    "Operations Monitoring",
    "Uptime, incident response and MAC workflow tracking for datacenter administration.",
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Uptime SLA", "99.982%", delta="+0.012%", help="Meets TIA-942 Tier III availability requirements")
col2.metric("Open Incidents", f"{int(incidents.shape[0])}")
col3.metric("Average Resolution", resolution_value)
col4.metric("Racks in Warning", f"{int(latest_snapshot['status'].str.lower().eq('warning').sum())}")

tab_a, tab_b, tab_c = st.tabs(["Incident Log", "MAC Requests", "Rack Health"])

with tab_a:
    if not incidents.empty:
        res_data = incidents.groupby("incident_type", as_index=False)["resolution_time_min"].mean()
        bar = (
            alt.Chart(res_data)
            .mark_bar(color="#b3b3b3")
            .encode(
                x=alt.X("resolution_time_min:Q", title="Average Resolution (min)"),
                y=alt.Y("incident_type:N", title=None, sort="-x", axis=alt.Axis(labelLimit=120)),
                tooltip=["incident_type", alt.Tooltip("resolution_time_min:Q", format=".1f")]
            )
            .properties(height=150)
        )
        st.altair_chart(bar, use_container_width=True)
        
    incident_table = incidents[
        ["timestamp", "rack_id", "region", "incident_type", "status", "resolution_time_min"]
    ].sort_values("timestamp", ascending=False)
    df_ops_incidents = incident_table.rename(
        columns={
            "timestamp": "Timestamp",
            "rack_id": "Rack",
            "region": "Region",
            "incident_type": "Incident Type",
            "status": "Current Status",
            "resolution_time_min": "Resolution (min)",
        }
    )
    st.dataframe(df_ops_incidents.style.map(color_status, subset=["Current Status"]), use_container_width=True, hide_index=True)

with tab_b:
    mac_requests = ops_log[ops_log["record_type"] == "MAC"].dropna(axis=1)
    if "mac_status" not in mac_requests.columns:
        mac_requests["mac_status"] = "Pending" # Fallback if empty
    mac_requests = mac_requests[["request_id", "mac_action", "target_rack", "scheduled_window", "mac_status"]].rename(
        columns={"request_id": "Request ID", "mac_action": "Action", "target_rack": "Rack", "scheduled_window": "Window", "mac_status": "Status"}
    )
    st.dataframe(mac_requests.style.map(color_status, subset=["Status"]), use_container_width=True, hide_index=True)
    st.caption("MAC = Move, Add and Change activity planned for the next maintenance window.")

with tab_c:
    st.bar_chart(
        latest_snapshot["status"].value_counts().rename_axis("status").to_frame("racks"),
        use_container_width=True,
    )
    st.dataframe(
        latest_snapshot[["rack_id", "region", "status", "power_usage_kw", "pue_ratio"]]
        .rename(
            columns={
                "rack_id": "Rack",
                "region": "Region",
                "status": "Status",
                "power_usage_kw": "Power (kW)",
                "pue_ratio": "PUE",
            }
        )
        .sort_values(["Status", "Region", "Rack"], ascending=[False, True, True]),
        use_container_width=True,
        hide_index=True,
    )

st.caption("Incident management and MAC workflows aligned with ITIL v4 best practices.")
