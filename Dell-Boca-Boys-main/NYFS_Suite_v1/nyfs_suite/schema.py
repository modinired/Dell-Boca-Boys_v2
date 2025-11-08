from __future__ import annotations
import pandas as pd
from .utils import ensure_columns

SCHEMA = {
    "chart_of_accounts": [
        "AccountID","Name","Type","ParentID","IsActive"
    ],
    "customers": [
        "CustomerID","Name","Terms","CreditLimit","Contact"
    ],
    "vendors": [
        "VendorID","Name","Terms","Contact"
    ],
    "items": [
        "ItemID","Name","SKU","Type","UnitPrice","COGSAccount","RevenueAccount","InventoryAccount"
    ],
    "ar_entries": [
        "EntryID","CustomerID","InvoiceNo","InvoiceDate","DueDate","AccountID","Amount","Tax","PaidAmount","PaymentDate","Status","Memo"
    ],
    "ap_entries": [
        "EntryID","VendorID","InvoiceNo","InvoiceDate","DueDate","AccountID","Amount","Tax","PaidAmount","PaymentDate","Status","Memo"
    ],
    "cashbook": [
        "Date","AccountID","Counterparty","Description","Amount","Type","LinkEntryID"
    ]
}

def validate_df(name: str, df: pd.DataFrame):
    required = SCHEMA[name]
    ensure_columns(df, required, name)
    return True
