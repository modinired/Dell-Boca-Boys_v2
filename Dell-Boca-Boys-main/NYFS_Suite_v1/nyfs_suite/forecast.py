from __future__ import annotations
import pandas as pd
import numpy as np

def simple_exponential_smoothing(series: pd.Series, alpha: float = 0.3, periods: int = 6):
    s = None
    for val in series.dropna():
        s = val if s is None else alpha * val + (1 - alpha) * s
    # Forecast flat using last smoothed value
    last = s if s is not None else (series.dropna().iloc[-1] if len(series.dropna()) else 0.0)
    return pd.Series([last]*periods, name="forecast")

def monthly_revenue_series(ar_detail: pd.DataFrame):
    d = ar_detail.copy()
    d["InvoiceDate"] = pd.to_datetime(d["InvoiceDate"])
    d["month"] = d["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    s = d.groupby("month")["Amount"].sum().sort_index()
    return s

def forecast_revenue(ar_detail: pd.DataFrame, periods: int = 6, alpha: float = 0.3):
    s = monthly_revenue_series(ar_detail)
    fc = simple_exponential_smoothing(s, alpha=alpha, periods=periods)
    fc.index = pd.date_range(s.index.max() + pd.offsets.MonthBegin(), periods=periods, freq="MS")
    return pd.DataFrame({"Month": fc.index, "ForecastRevenue": fc.values})
