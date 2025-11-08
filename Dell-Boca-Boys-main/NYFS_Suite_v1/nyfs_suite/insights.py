from __future__ import annotations
import pandas as pd
import numpy as np

def insights(tb: pd.DataFrame, ar_detail: pd.DataFrame, ap_detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    def add(cat, msg, severity="info"):
        rows.append({"Category": cat, "Message": msg, "Severity": severity})

    revenue = tb[tb["Type"]=="Revenue"]["SignedBalance"].sum()
    expenses = tb[tb["Type"]=="Expense"]["SignedBalance"].sum()
    if revenue <= 0:
        add("Revenue", "No revenue recorded; verify mapping of revenue accounts.", "warn")
    elif expenses/revenue > 0.8:
        add("Profitability", "Operating expenses exceed 80% of revenue; evaluate cost controls.", "warn")

    # AR health
    if not ar_detail.empty:
        pct_90 = (ar_detail[ar_detail["DaysPastDue"]>90]["OpenAmount"].sum() / ar_detail["OpenAmount"].sum()) if ar_detail["OpenAmount"].sum() else 0
        if pct_90 > 0.1:
            add("AR", "More than 10% of AR is over 90 days; tighten collections.", "warn")

    # AP concentration
    if not ap_detail.empty:
        vendor_conc = ap_detail.groupby("VendorID")["OpenAmount"].sum().sort_values(ascending=False)
        if len(vendor_conc) and vendor_conc.iloc[0] > 0.3*vendor_conc.sum():
            add("AP", f"Top vendor accounts for >30% of open AP ({vendor_conc.index[0]}). Consider payment plan negotiation.", "info")

    return pd.DataFrame(rows) if rows else pd.DataFrame([{"Category":"General","Message":"Financials appear within normal ranges.","Severity":"info"}])
