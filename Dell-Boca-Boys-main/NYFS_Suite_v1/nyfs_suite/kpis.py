from __future__ import annotations
import pandas as pd
import numpy as np

def kpis(tb: pd.DataFrame, ar_detail: pd.DataFrame, ap_detail: pd.DataFrame):
    # Classic ratios (simple forms)
    revenue = tb[tb["Type"]=="Revenue"]["SignedBalance"].sum()
    cogs = tb[tb["AccountID"].str.contains("COGS", case=False, na=False)]["SignedBalance"].sum()
    expenses = tb[tb["Type"]=="Expense"]["SignedBalance"].sum() - cogs
    gross_margin = (revenue - cogs) / revenue if revenue else np.nan
    net_margin = (revenue - cogs - expenses) / revenue if revenue else np.nan

    current_assets = tb[(tb["Type"]=="Asset") & (~tb["AccountID"].str.contains("Fixed|PPE|NonCurrent|LT", case=False, na=False))]["SignedBalance"].sum()
    inventory = tb[tb["AccountID"].str.contains("Inventory", case=False, na=False)]["SignedBalance"].sum()
    cash = tb[tb["AccountID"].str.contains("Cash", case=False, na=False)]["SignedBalance"].sum()
    current_liab = tb[(tb["Type"]=="Liability") & (~tb["AccountID"].str.contains("LongTerm|LT", case=False, na=False))]["SignedBalance"].sum()

    current_ratio = current_assets / current_liab if current_liab else np.nan
    quick_ratio = (current_assets - inventory) / current_liab if current_liab else np.nan

    avg_ar = ar_detail["OpenAmount"].mean() if len(ar_detail) else np.nan
    avg_ap = ap_detail["OpenAmount"].mean() if len(ap_detail) else np.nan

    data = [
        ["Revenue", revenue],
        ["COGS", cogs],
        ["Operating Expenses (ex COGS)", expenses],
        ["Gross Margin %", gross_margin],
        ["Net Margin %", net_margin],
        ["Cash", cash],
        ["Inventory", inventory],
        ["Current Ratio", current_ratio],
        ["Quick Ratio", quick_ratio],
        ["Avg Open AR", avg_ar],
        ["Avg Open AP", avg_ap],
    ]
    return pd.DataFrame(data, columns=["Metric","Value"])
