from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from utils.data_loader import load_friday_data
from utils.theme import apply_theme, page_header, render_sidebar


st.set_page_config(
    page_title="Market | Friday DC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()

ops, market, ops_log, compliance = load_friday_data()

page_header(
    "Market Intelligence",
    "Mexico datacenter market capacity, investment concentration and deployment patterns.",
)

filter_type = st.radio("Filter Type", ["hub", "state"], horizontal=True)
all_regions = market[filter_type].dropna().unique().tolist()
selected_regions = st.multiselect(f"Filter by {filter_type.title()}", all_regions, default=all_regions)
filtered_market = market[market[filter_type].isin(selected_regions)]

investment_by_region = (
    filtered_market.groupby(filter_type, as_index=True)["investment_usd_billions"].sum().sort_values(ascending=False)
)
player_share = filtered_market.groupby("operator", as_index=False)["estimated_mw"].sum()
player_share["share_pct"] = (
    player_share["estimated_mw"] / max(player_share["estimated_mw"].sum(), 1) * 100
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Market Capacity", f"{filtered_market['estimated_mw'].sum():,.1f} MW")
col2.metric("Accumulated Investment", f"{filtered_market['investment_usd_billions'].sum():,.2f} B USD")
col3.metric("Locations Tracked", f"{filtered_market[filter_type].nunique()}")
col4.metric("CAGR (2024-2030)", "12.4%", help="Compound Annual Growth Rate projection")

trend_col, region_col = st.columns(2, gap="large")
with trend_col:
    st.subheader("Top Facilities by Capacity")
    top_facilities = filtered_market.sort_values("estimated_mw", ascending=False).head(10)
    fac_bar = alt.Chart(top_facilities).mark_bar(color="#3366cc").encode(
        x=alt.X("estimated_mw:Q", title="Capacity (MW)"),
        y=alt.Y("name:N", sort="-x", title=None),
        tooltip=["name", "estimated_mw"]
    ).properties(height=250)
    st.altair_chart(fac_bar, use_container_width=True)

with region_col:
    st.subheader("Investment by region")
    st.bar_chart(investment_by_region, use_container_width=True)

st.subheader("Competitive landscape")
st.dataframe(
    player_share[["operator", "share_pct"]].rename(
        columns={"operator": "Top player", "share_pct": "Market share (%)"}
    ),
    use_container_width=True,
    hide_index=True,
)

left_chart, right_chart = st.columns(2, gap="large")
with left_chart:
    st.subheader("Deployment models")
    deployment_models = filtered_market.groupby("deployment_model", as_index=False)["estimated_mw"].sum()
    total_mw = deployment_models["estimated_mw"].sum()
    deployment_models["Share (%)"] = (deployment_models["estimated_mw"] / max(total_mw, 1) * 100).round(1)
    deployment_models = deployment_models.rename(columns={"deployment_model": "Model", "estimated_mw": "Capacity (MW)"})
    
    # Create combined label for the axis
    deployment_models["Model_Label"] = deployment_models["Model"] + " (" + deployment_models["Share (%)"].astype(str) + "%)"
    
    bar = alt.Chart(deployment_models).mark_bar(color="#b3b3b3").encode(
        x=alt.X("Capacity (MW):Q", title="Total Capacity (MW)"),
        y=alt.Y("Model_Label:N", sort="-x", title=None),
        tooltip=["Model", "Capacity (MW)", "Share (%)"]
    ).properties(height=150)
    st.altair_chart(bar, use_container_width=True)
    st.info("Strategic Position: Friday operates as an Edge Computing provider in Emerging Regions.")

with right_chart:
    st.subheader("Est. Investment by Operator")
    investment_operator = filtered_market.groupby("operator", as_index=False)["investment_est_usd_m"].sum()
    investment_operator = investment_operator.sort_values("investment_est_usd_m", ascending=False).head(10)
    bar_inv = alt.Chart(investment_operator).mark_bar(color="#8a8a8a").encode(
        x=alt.X("investment_est_usd_m:Q", title="Investment (M USD)"),
        y=alt.Y("operator:N", sort="-x", title=None),
        tooltip=["operator", "investment_est_usd_m"]
    ).properties(height=150)
    st.altair_chart(bar_inv, use_container_width=True)

import streamlit.components.v1 as components

st.subheader("Data Center Locations in Mexico")

map_url = "https://www.datacentermap.com/mexico/"
components.iframe(map_url, height=600, scrolling=True)

st.info("Global interactive map provided by Data Center Map. Loading depends on client connection. [Ir a original](https://www.datacentermap.com/mexico/)")

st.subheader("Market dataset")
st.dataframe(
    filtered_market.sort_values(["year", "region"], ascending=[False, True]),
    use_container_width=True,
    hide_index=True,
)

st.caption("Data processed locally. Dataset available at: https://www.kaggle.com/datasets/jorgeenriquevp/mexico-data-centers-2025")
