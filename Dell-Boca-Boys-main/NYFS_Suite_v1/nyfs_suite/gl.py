from __future__ import annotations
import pandas as pd
import numpy as np

ACCOUNT_TYPES = {
    "Asset": 1,
    "Liability": -1,
    "Equity": -1,
    "Revenue": -1,
    "Expense": 1
}

def journal_from_subledgers(coa, ar, ap, cash):
    # Create debit/credit rows from AR/AP/Cashbook
    j = []
    # AR (invoice increases AR asset, increases revenue; payment reduces AR)
    for _, r in ar.iterrows():
        total = float(r.get("Amount",0)) + float(r.get("Tax",0))
        if r.get("Status","").lower() != "void":
            j.append({"Date": r["InvoiceDate"], "JID": f"ARINV-{r['EntryID']}", "AccountID": r["AccountID"], "Debit": 0.0, "Credit": total, "Memo": r.get("Memo","")})
            j.append({"Date": r["InvoiceDate"], "JID": f"ARINV-{r['EntryID']}", "AccountID": "AR", "Debit": total, "Credit": 0.0, "Memo": r.get("Memo","")})
        # Cash receipt
        paid = float(r.get("PaidAmount",0) or 0.0)
        if paid > 0 and pd.notna(r.get("PaymentDate")):
            j.append({"Date": r["PaymentDate"], "JID": f"ARREC-{r['EntryID']}", "AccountID": "Cash", "Debit": paid, "Credit": 0.0, "Memo": "AR Receipt"})
            j.append({"Date": r["PaymentDate"], "JID": f"ARREC-{r['EntryID']}", "AccountID": "AR", "Debit": 0.0, "Credit": paid, "Memo": "AR Receipt"})
    # AP (bill increases expense, increases AP; payment reduces AP)
    for _, r in ap.iterrows():
        total = float(r.get("Amount",0)) + float(r.get("Tax",0))
        if r.get("Status","").lower() != "void":
            j.append({"Date": r["InvoiceDate"], "JID": f"APBIL-{r['EntryID']}", "AccountID": r["AccountID"], "Debit": total, "Credit": 0.0, "Memo": r.get("Memo","")})
            j.append({"Date": r["InvoiceDate"], "JID": f"APBIL-{r['EntryID']}", "AccountID": "AP", "Debit": 0.0, "Credit": total, "Memo": r.get("Memo","")})
        paid = float(r.get("PaidAmount",0) or 0.0)
        if paid > 0 and pd.notna(r.get("PaymentDate")):
            j.append({"Date": r["PaymentDate"], "JID": f"APPAY-{r['EntryID']}", "AccountID": "AP", "Debit": paid, "Credit": 0.0, "Memo": "AP Payment"})
            j.append({"Date": r["PaymentDate"], "JID": f"APPAY-{r['EntryID']}", "AccountID": "Cash", "Debit": 0.0, "Credit": paid, "Memo": "AP Payment"})
    # Cashbook free-form entries
    for _, r in cash.iterrows():
        amt = float(r.get("Amount",0))
        if str(r.get("Type","")).lower() == "receipt":
            j.append({"Date": r["Date"], "JID": f"CASH-{_}", "AccountID": "Cash", "Debit": amt, "Credit": 0.0, "Memo": r.get("Description","")})
            j.append({"Date": r["Date"], "JID": f"CASH-{_}", "AccountID": r["AccountID"], "Debit": 0.0, "Credit": amt, "Memo": r.get("Description","")})
        else:
            j.append({"Date": r["Date"], "JID": f"CASH-{_}", "AccountID": r["AccountID"], "Debit": amt, "Credit": 0.0, "Memo": r.get("Description","")})
            j.append({"Date": r["Date"], "JID": f"CASH-{_}", "AccountID": "Cash", "Debit": 0.0, "Credit": amt, "Memo": r.get("Description","")})
    jdf = pd.DataFrame(j)
    jdf["Date"] = pd.to_datetime(jdf["Date"])
    return jdf

def general_ledger(journal, coa):
    gl = journal.copy()
    # map account type where possible
    type_map = dict(zip(coa["AccountID"], coa["Type"]))
    gl["Type"] = gl["AccountID"].map(type_map).fillna("Unknown")
    gl["Net"] = gl["Debit"] - gl["Credit"]
    return gl

def trial_balance(gl):
    tb = gl.groupby(["AccountID","Type"], dropna=False).agg(
        Debit=("Debit","sum"),
        Credit=("Credit","sum"),
        Net=("Net","sum")
    ).reset_index()
    # Normalize sign by account type
    tb["SignedBalance"] = tb.apply(lambda r: r["Net"] * ACCOUNT_TYPES.get(str(r["Type"]), 1), axis=1)
    return tb
