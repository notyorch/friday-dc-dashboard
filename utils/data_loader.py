from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OPS_PATH = DATA_DIR / "legacy" / "friday_internal_ops.csv"
MARKET_PATH = DATA_DIR / "market_trends.csv"
OPS_LOG_PATH = DATA_DIR / "operations_log.csv"
COMPLIANCE_PATH = DATA_DIR / "compliance_framework.csv"


def _infer_ops_region(rack_id: str) -> str:
    rack = str(rack_id).upper()
    if "A" in rack:
        return "Queretaro"
    if "B" in rack:
        return "CDMX"
    if "C" in rack:
        return "Monterrey"
    if "D" in rack:
        return "Saltillo"
    return "Queretaro"


def _read_csv(path: Path) -> pd.DataFrame:
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path)


def _repair_text(value):
    if not isinstance(value, str):
        return value
    if any(marker in value for marker in ("Ã", "â", "Â")):
        try:
            return value.encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return value
    return value


@st.cache_data(show_spinner=False)
def load_friday_data():
    if not OPS_PATH.exists() or not MARKET_PATH.exists() or not OPS_LOG_PATH.exists() or not COMPLIANCE_PATH.exists():
        missing = [str(path) for path in (OPS_PATH, MARKET_PATH, OPS_LOG_PATH, COMPLIANCE_PATH) if not path.exists()]
        raise FileNotFoundError(f"Missing CSV files in data directory: {', '.join(missing)}")

    ops = _read_csv(OPS_PATH)
    market = _read_csv(MARKET_PATH)
    ops_log = _read_csv(OPS_LOG_PATH)
    compliance = _read_csv(COMPLIANCE_PATH)

    for frame in (ops, market):
        object_columns = frame.select_dtypes(include="object").columns
        for column in object_columns:
            frame[column] = frame[column].map(_repair_text)

    ops["timestamp"] = pd.to_datetime(ops["timestamp"], errors="coerce")
    ops = ops.dropna(subset=["timestamp"]).sort_values("timestamp")
    ops["power_usage_kw"] = pd.to_numeric(ops["power_usage_kw"], errors="coerce")
    ops["pue_ratio"] = pd.to_numeric(ops["pue_ratio"], errors="coerce")
    ops["resolution_time_min"] = pd.to_numeric(ops["resolution_time_min"], errors="coerce")
    ops["incident_type"] = ops["incident_type"].fillna("").replace("None", "")
    ops["status"] = ops["status"].fillna("Unknown")
    ops["region"] = ops["rack_id"].map(_infer_ops_region)

    if "year" in market.columns:
        market["year"] = pd.to_numeric(market["year"], errors="coerce").astype("Int64")
    else:
        market["year"] = 2024 # default fallback
        
    if "estimated_mw" in market.columns:
        market["market_capacity_mw"] = pd.to_numeric(market["estimated_mw"], errors="coerce")
    elif "market_capacity_mw" in market.columns:
        market["market_capacity_mw"] = pd.to_numeric(market["market_capacity_mw"], errors="coerce")
        
    if "investment_est_usd_m" in market.columns:
        market["investment_usd_billions"] = pd.to_numeric(market["investment_est_usd_m"], errors="coerce") / 1000.0
    elif "investment_usd_billions" in market.columns:
        market["investment_usd_billions"] = pd.to_numeric(market["investment_usd_billions"], errors="coerce")

    if "state" in market.columns:
        market["region"] = market["state"].fillna("Unknown")
    elif "region" in market.columns:
        market["region"] = market["region"].fillna("Unknown")

    return ops, market, ops_log, compliance
