from __future__ import annotations
import pandas as pd
from .gl import ACCOUNT_TYPES

def income_statement(tb: pd.DataFrame):
    inc = tb.copy()
    def filt(t): return inc[inc["Type"]==t]
    revenue = filt("Revenue")["SignedBalance"].sum()
    cogs = inc[inc["AccountID"].str.contains("COGS", case=False, na=False)]["SignedBalance"].sum()
    operating_exp = filt("Expense")["SignedBalance"].sum() - cogs
    gross_profit = revenue - cogs
    operating_income = gross_profit - operating_exp
    net_income = operating_income  # no interest/taxes modeled here (can be extended)
    rows = [
        ["Revenue", revenue],
        ["COGS", -cogs],
        ["Gross Profit", gross_profit],
        ["Operating Expenses", -operating_exp],
        ["Operating Income", operating_income],
        ["Net Income", net_income],
    ]
    return pd.DataFrame(rows, columns=["Line","Amount"])

def balance_sheet(tb: pd.DataFrame):
    def sum_type(t):
        return tb[tb["Type"]==t]["SignedBalance"].sum()
    assets = sum_type("Asset")
    liabilities = sum_type("Liability")
    equity = sum_type("Equity")
    # sanity check: Assets = Liabilities + Equity
    rows = [
        ["Assets", assets],
        ["Liabilities", liabilities],
        ["Equity", equity],
        ["Check (Assets - L - E)", assets - liabilities - equity]
    ]
    return pd.DataFrame(rows, columns=["Line","Amount"])

def cash_flow_indirect(tb: pd.DataFrame):
    # Minimal indirect method from TB deltas would require periods.
    # Here we provide a structure derived from TB snapshot (extend with periods for real CF).
    rows = [
        ["Net Income (proxy)", tb[tb['Type']=="Revenue"]["SignedBalance"].sum()
         - tb[tb['AccountID'].str.contains("COGS", case=False, na=False)]["SignedBalance"].sum()
         - (tb[(tb["Type"]=="Expense") & (~tb["AccountID"].str.contains("COGS", case=False, na=False))]["SignedBalance"].sum())
        ],
        ["Operating Cash Flow (approx)", None],
        ["Investing Cash Flow (approx)", None],
        ["Financing Cash Flow (approx)", None],
        ["Net Change in Cash (approx)", None],
    ]
    return pd.DataFrame(rows, columns=["Line","Amount"])
