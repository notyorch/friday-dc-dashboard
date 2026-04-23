from __future__ import annotations

import altair as alt
import streamlit as st

from utils.data_loader import load_friday_data
from utils.theme import apply_theme, page_header, render_sidebar, color_status


st.set_page_config(
    page_title="Friday DC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()

ops, market, ops_log, compliance = load_friday_data()

latest_snapshot = ops.groupby("rack_id", as_index=False).tail(1).copy()
incident_window = ops.tail(48)
recent_incidents = incident_window.loc[
    incident_window["incident_type"].fillna("").astype(str).str.strip().ne("")
]

total_racks = int(latest_snapshot["rack_id"].nunique())
online_racks = int(latest_snapshot["status"].str.lower().eq("online").sum())
avg_pue = float(latest_snapshot["pue_ratio"].dropna().mean()) if latest_snapshot["pue_ratio"].notna().any() else 0.0
power_kw = float(latest_snapshot["power_usage_kw"].fillna(0).sum())
active_incidents = int(recent_incidents.shape[0])
market_capacity = float(market.loc[market["year"] == 2030, "market_capacity_mw"].sum())

page_header(
    "Datacenter Executive Overview",
    "Live operations summary for the monitored datacenter fleet and the Mexico market context.",
)

metric_cols = st.columns(5)
metric_cols[0].metric("Racks Monitored", f"{total_racks}")
metric_cols[1].metric("Online Racks", f"{online_racks}")
metric_cols[2].metric("Average PUE", f"{avg_pue:.2f}")
metric_cols[3].metric("Current Load", f"{power_kw:,.1f} kW")
metric_cols[4].metric("2030 Capacity (Colocation & Edge)", f"{market_capacity:,.1f} MW")

left_col, right_col = st.columns((1.5, 1), gap="large")

with left_col:
    st.subheader("Operational trend")
    trend = (
        ops.set_index("timestamp")
        .resample("D")
        .agg(power_usage_kw=("power_usage_kw", "mean"), pue_ratio=("pue_ratio", "mean"))
        .dropna(how="all")
        .tail(30)
    )
    st.line_chart(trend, use_container_width=True)

    st.subheader("Latest rack snapshot")
    rack_columns = ["rack_id", "region", "status", "power_usage_kw", "pue_ratio"]
    df_snapshot = latest_snapshot[rack_columns].sort_values(["region", "rack_id"]).rename(
        columns={
            "rack_id": "Rack",
            "region": "Region",
            "status": "Status",
            "power_usage_kw": "Power (kW)",
            "pue_ratio": "PUE",
        }
    )
    st.dataframe(df_snapshot.style.map(color_status, subset=["Status"]), use_container_width=True, hide_index=True)

with right_col:
    st.subheader("Incident watch")
    if active_incidents:
        st.warning(f"{active_incidents} incidents found in the latest 48 records.")
        incident_table = recent_incidents[
            ["timestamp", "rack_id", "incident_type", "status", "resolution_time_min"]
        ].sort_values("timestamp", ascending=False)
        df_incident = incident_table.rename(
            columns={
                "timestamp": "Timestamp",
                "rack_id": "Rack",
                "incident_type": "Incident",
                "status": "Status",
                "resolution_time_min": "Resolution (min)",
            }
        )
        st.dataframe(df_incident.style.map(color_status, subset=["Status"]), use_container_width=True, hide_index=True)
    else:
        st.success("No incidents were detected in the most recent monitoring window.")

    st.subheader("Market investment by region")
    investment = (
        market.groupby("region", as_index=False)["investment_usd_billions"]
        .sum()
        .sort_values("investment_usd_billions", ascending=False)
        .set_index("region")
    )
    st.bar_chart(investment, use_container_width=True)
    st.caption("Source: CBRE & Statista Industry Reports (2024)")

st.subheader("Deployment status summary")
status_col, projects_col = st.columns(2, gap="large")

with status_col:
    health_data = latest_snapshot["status"].value_counts().reset_index()
    health_data.columns = ["status", "count"]
    donut = (
        alt.Chart(health_data)
        .mark_arc(innerRadius=40)
        .encode(
            theta=alt.Theta(field="count", type="quantitative"),
            color=alt.Color(field="status", type="nominal", legend=alt.Legend(orient="bottom", title=None)),
            tooltip=["status", "count"]
        )
        .properties(height=250)
    )
    st.altair_chart(donut, use_container_width=True)

with projects_col:
    projects = ops_log[ops_log["record_type"] == "PROJECT"].dropna(axis=1)
    projects = projects[["project_name", "project_progress_pct", "project_phase"]].rename(
        columns={"project_name": "Project", "project_progress_pct": "Progress", "project_phase": "Phase"}
    ).set_index("Project")
    st.dataframe(projects.style.map(color_status, subset=["Phase"]), use_container_width=True)
