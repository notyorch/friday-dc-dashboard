from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"


THEME = {
    "background": "#000000",
    "surface": "#000000",
    "surface_alt": "#050505",
    "text": "#f5f5f5",
    "muted": "#8a8a8a",
    "border": "#151515",
    "accent": "#e8e8e8",
}


def _data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def apply_theme() -> dict[str, str]:
    theme = THEME
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&family=Roboto+Mono:wght@400;500&family=Raleway:wght@400;500;600;700&family=Courier+Prime:wght@400;700&display=swap');

        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background: {theme["background"]};
            color: {theme["text"]};
        }}

        html, body, [class*="css"] {{
            font-family: "Raleway", sans-serif;
        }}

        #MainMenu, footer {{
            visibility: hidden;
        }}

        [data-testid="collapsedControl"] {{
            color: {theme["text"]};
        }}

        [data-testid="stSidebar"] {{
            background: {theme["surface"]};
            border-right: 1px solid {theme["border"]};
        }}

        [data-testid="stSidebar"] * {{
            background: transparent !important;
        }}

        [data-testid="stSidebarNav"] {{
            display: none;
        }}

        [data-testid="stSidebar"] [data-testid="stPageLink"] {{
            margin-bottom: 0.2rem;
        }}

        [data-testid="stSidebar"] [data-testid="stPageLink"] a {{
            color: {theme["muted"]} !important;
            text-decoration: none !important;
            border-radius: 0 !important;
            border: 0 !important;
            padding: 0.45rem 0 !important;
            font-family: "Courier Prime", monospace !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            font-size: 0.78rem !important;
        }}

        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{
            color: {theme["text"]} !important;
            background: transparent !important;
        }}

        [data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {{
            color: {theme["text"]} !important;
        }}

        [data-testid="stSidebar"] button[title*="View fullscreen"] {{
            display: none !important;
        }}

        .friday-sidebar-brand {{
            text-align: center;
            margin-bottom: 0.6rem;
        }}

        .friday-sidebar-brand a {{
            display: inline-block;
        }}

        .friday-sidebar-brand img {{
            display: block;
            margin: 0 auto;
            width: 100%;
            max-width: 190px;
            height: auto;
            pointer-events: none;
        }}

        .friday-sidebar-caption {{
            color: #b3b3b3;
            font-family: "Raleway", sans-serif;
            font-size: 0.72rem;
            letter-spacing: 0.14em;
            margin-top: 0.75rem;
            text-align: center;
            text-transform: uppercase;
        }}

        .friday-sidebar-time {{
            border-top: 1px solid {theme["border"]};
            color: {theme["muted"]};
            font-family: Consolas, "Courier Prime", monospace;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            line-height: 1.7;
            margin-top: 2rem;
            padding-top: 1rem;
        }}

        .block-container {{
            padding-top: 1.35rem;
            padding-bottom: 2rem;
        }}

        h1 {{
            color: {theme["text"]};
            font-family: "Inter", sans-serif;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-align: center;
            text-transform: uppercase;
        }}

        h2, h3 {{
            color: {theme["text"]};
            font-family: "Roboto Mono", monospace;
            font-weight: 500;
            letter-spacing: -0.02em;
        }}

        p, li, label, .stMarkdown, .stCaption {{
            color: {theme["text"]};
        }}

        [data-testid="stMetric"], [data-testid="stDataFrame"], .stAlert {{
            border-radius: 16px;
        }}

        [data-testid="stMetric"] {{
            background: {theme["surface"]};
            border: 1px solid {theme["border"]};
            padding: 0.85rem 1rem;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {{
            color: {theme["muted"]};
            font-family: "Raleway", sans-serif;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 1.25rem;
            border-bottom: 1px solid {theme["border"]};
            padding-bottom: 0;
        }}

        .stTabs [data-baseweb="tab"] {{
            background: {theme["surface"]};
            border: 0;
            border-bottom: 1px solid transparent;
            border-radius: 0;
            color: {theme["muted"]};
            font-family: "Raleway", sans-serif;
            font-size: 0.95rem;
            font-weight: 500;
            padding: 0.65rem 0 0.8rem 0;
            margin-bottom: -1px;
            box-shadow: none !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: transparent;
            border-bottom-color: {theme["text"]};
            color: {theme["accent"]};
        }}

        div[data-testid="stButton"] > button,
        div[data-testid="baseButton-secondary"] {{
            border-radius: 0;
        }}

        div[data-testid="stButton"] > button {{
            border: 0;
            background: transparent;
            color: {theme["text"]};
            box-shadow: none;
            padding-left: 0;
            padding-right: 0;
            font-family: "Courier Prime", monospace;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        div[data-testid="stButton"] > button:hover {{
            color: {theme["accent"]};
            background: transparent;
        }}

        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        div[data-testid="stNumberInput"] input {{
            background: {theme["surface"]};
            color: {theme["text"]};
            border-color: {theme["border"]};
        }}

        div[data-testid="stSelectbox"] label,
        div[data-testid="stNumberInput"] label,
        .stCaption,
        [data-testid="stMarkdownContainer"] p {{
            font-family: "Raleway", sans-serif;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid {theme["border"]};
            background: {theme["surface_alt"]};
        }}

        .stAlert {{
            background: {theme["surface_alt"]};
            border: 1px solid {theme["border"]};
            color: {theme["text"]};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return theme


def render_sidebar() -> None:
    local_now = datetime.now(ZoneInfo("America/Mexico_City"))
    utc_now = datetime.now(timezone.utc)

    with st.sidebar:
        st.markdown(
            f"""
            <div class="friday-sidebar-brand">
                <a href="/" target="_self">
                    <img src="{_data_uri(ASSETS_DIR / 'logo_w.png')}" alt="FRIDAY logo">
                </a>
                <div class="friday-sidebar-caption">DATACENTER MONITORING DASHBOARD</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.page_link("app.py", label="Overview")
        st.page_link("pages/01_operations.py", label="Operations")
        st.page_link("pages/02_energy.py", label="Energy")
        st.page_link("pages/03_security.py", label="Security")
        st.page_link("pages/04_market.py", label="Market")
        st.page_link("pages/05_emerging_tech.py", label="Emerging Tech")

        st.markdown(
            f"""
            <div class="friday-sidebar-time">
                LOCAL {local_now.strftime('%H:%M:%S')}<br/>
                UTC&nbsp;&nbsp;&nbsp;{utc_now.strftime('%H:%M:%S')}
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_header(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 2.5rem; padding-top: 1rem;">
            <h1 style="margin-bottom: 0.5rem; padding-bottom: 0;">{title}</h1>
            <p style="color: {{THEME['muted']}}; font-size: 1.05rem; margin-top: 0; font-family: 'Raleway', sans-serif;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def color_status(val):
    if not isinstance(val, str):
        return ""
    val_str = val.lower()
    if any(x in val_str for x in ["active", "critical", "pending", "non-compliant", "high impact"]):
        color = "#ff4b4b" # red
    elif any(x in val_str for x in ["in progress", "scheduled", "warning", "investigating", "needs review"]):
        color = "#ffa421" # orange
    elif any(x in val_str for x in ["resolved", "approved", "completed", "online", "closed", "compliant", "normal"]):
        color = "#09ab3b" # green
    elif any(x in val_str for x in ["cancelled", "unknown"]):
        color = "#0068c9" # blue
    else:
        color = "gray"
    return f'color: {color}; font-weight: bold;'
