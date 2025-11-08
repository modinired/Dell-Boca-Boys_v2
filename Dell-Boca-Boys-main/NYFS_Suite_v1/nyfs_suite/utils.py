from __future__ import annotations
import pandas as pd
import numpy as np

def parse_date(s: str):
    if pd.isna(s) or s is None or s == "":
        return pd.NaT
    return pd.to_datetime(s, errors="coerce")

def as_month(dt):
    if pd.isna(dt):
        return pd.NaT
    dt = pd.to_datetime(dt)
    return pd.Timestamp(year=dt.year, month=dt.month, day=1)

def currency_fmt(x: float) -> str:
    try:
        return f"${x:,.2f}"
    except Exception:
        return str(x)

def ensure_columns(df: pd.DataFrame, required: list[str], name: str):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name}: missing required columns: {missing}")
    return True
