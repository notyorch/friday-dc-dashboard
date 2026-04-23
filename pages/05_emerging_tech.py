from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.data_loader import load_friday_data
from utils.theme import apply_theme, page_header, render_sidebar


st.set_page_config(
    page_title="Emerging Tech | Friday DC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()
ops, market, ops_log, compliance = load_friday_data()

page_header(
    "Emerging Technologies",
    "Technology radar, adoption timeline and strategic recommendations for future datacenter upgrades.",
)

radar = market[["dominant_tech", "maturity_level", "tech_category"]].drop_duplicates().dropna()
radar = radar.rename(columns={"dominant_tech": "Technology", "maturity_level": "Maturity", "tech_category": "Category"})
radar["Adoption Year"] = radar["Maturity"].map({"Adopt": 2024, "Trial": 2026, "Assess": 2028, "Hold": 2030}).fillna(2025)
radar["Priority"] = radar["Maturity"].map({"Adopt": 5, "Trial": 3, "Assess": 2, "Hold": 1}).fillna(3)
radar["Impact"] = radar["Maturity"].map({"Adopt": "High", "Trial": "Medium", "Assess": "Low", "Hold": "Low"}).fillna("Medium")
radar = radar[["Technology", "Adoption Year", "Impact", "Priority", "Maturity", "Category"]]

# Mock-up metrics for UI simulation (additional curated items)
radar = pd.concat(
    [
        radar,
        pd.DataFrame(
            [
                {"Technology": "Digital twins", "Adoption Year": 2027, "Impact": "Medium", "Priority": 3, "Maturity": "Assess", "Category": "Software/AI"},
                {"Technology": "On-site battery analytics", "Adoption Year": 2025, "Impact": "High", "Priority": 4, "Maturity": "Trial", "Category": "Sustainability"},
            ]
        ),
    ],
    ignore_index=True,
).drop_duplicates(subset=["Technology"])

timeline = radar.groupby("Adoption Year", as_index=True)["Priority"].sum().sort_index()

col1, col2 = st.columns((1.1, 1), gap="large")

with col1:
    st.subheader("Technology radar")
    cats = radar["Category"].unique().tolist()
    selected_cats = st.multiselect("Filter by Category", cats, default=cats)
    st.dataframe(radar[radar["Category"].isin(selected_cats)], use_container_width=True, hide_index=True)

with col2:
    st.subheader("Adoption timeline 2024-2030")
    st.bar_chart(timeline, use_container_width=True)
    st.markdown("- **2025**: Battery analytics roll-out.\n- **2027**: Widespread 5G Edge deployment in Querétaro clusters.")

st.info("Strategic Impact for Friday: Liquid cooling loop integration should be prioritized immediately (Adopt) to maintain PUE < 1.3 targets under heavy AI training workloads.")

st.subheader("Strategic recommendations")
# Mock-up metrics for UI simulation
recommendations = pd.DataFrame(
    [
        {"Horizon": "0-6 months", "Recommendation": "Validate liquid cooling readiness in the highest-density racks."},
        {"Horizon": "6-12 months", "Recommendation": "Pilot a digital twin for thermal monitoring and capacity planning."},
        {"Horizon": "12-24 months", "Recommendation": "Expand modular edge capacity in regions with growing demand."},
    ]
)
st.dataframe(recommendations, use_container_width=True, hide_index=True)
st.caption("Projections aligned with Gartner Top Strategic Technology Trends 2025.")
