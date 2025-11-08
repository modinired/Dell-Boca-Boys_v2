from __future__ import annotations
import pandas as pd
import numpy as np
from .utils import parse_date

def _age_bucket(days):
    if days <= 0: return "Current"
    if days <= 30: return "1-30"
    if days <= 60: return "31-60"
    if days <= 90: return "61-90"
    return "90+"

def ar_aging(ar: pd.DataFrame, as_of: str | None = None):
    as_of = pd.to_datetime(as_of) if as_of else pd.Timestamp.today().normalize()
    df = ar.copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["DueDate"] = pd.to_datetime(df["DueDate"])
    df["PaidAmount"] = df["PaidAmount"].fillna(0.0)
    df["OpenAmount"] = df["Amount"].fillna(0.0) + df["Tax"].fillna(0.0) - df["PaidAmount"]
    df["DaysPastDue"] = (as_of - df["DueDate"]).dt.days
    df["Bucket"] = df["DaysPastDue"].apply(_age_bucket)
    pivot = df.pivot_table(index="CustomerID", columns="Bucket", values="OpenAmount", aggfunc="sum", fill_value=0.0).reset_index()
    totals = pivot.sum(numeric_only=True)
    totals["CustomerID"] = "TOTAL"
    pivot = pd.concat([pivot, pd.DataFrame([totals])], ignore_index=True)
    return df, pivot

def ap_aging(ap: pd.DataFrame, as_of: str | None = None):
    as_of = pd.to_datetime(as_of) if as_of else pd.Timestamp.today().normalize()
    df = ap.copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["DueDate"] = pd.to_datetime(df["DueDate"])
    df["PaidAmount"] = df["PaidAmount"].fillna(0.0)
    df["OpenAmount"] = df["Amount"].fillna(0.0) + df["Tax"].fillna(0.0) - df["PaidAmount"]
    df["DaysPastDue"] = (as_of - df["DueDate"]).dt.days
    df["Bucket"] = df["DaysPastDue"].apply(_age_bucket)
    pivot = df.pivot_table(index="VendorID", columns="Bucket", values="OpenAmount", aggfunc="sum", fill_value=0.0).reset_index()
    totals = pivot.sum(numeric_only=True)
    totals["VendorID"] = "TOTAL"
    pivot = pd.concat([pivot, pd.DataFrame([totals])], ignore_index=True)
    return df, pivot
