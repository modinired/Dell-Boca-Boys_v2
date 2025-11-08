# User Guide

## 1) Data Inputs (CSV Schema)
- **chart_of_accounts.csv**: AccountID, Name, Type (Asset/Liability/Equity/Revenue/Expense), ParentID, IsActive
- **customers.csv**: CustomerID, Name, Terms, CreditLimit, Contact
- **vendors.csv**: VendorID, Name, Terms, Contact
- **items.csv**: ItemID, Name, SKU, Type (Product/Service), UnitPrice, COGSAccount, RevenueAccount, InventoryAccount
- **ar_entries.csv**: EntryID, CustomerID, InvoiceNo, InvoiceDate, DueDate, AccountID (Revenue), Amount, Tax, PaidAmount, PaymentDate, Status, Memo
- **ap_entries.csv**: EntryID, VendorID, InvoiceNo, InvoiceDate, DueDate, AccountID (Expense), Amount, Tax, PaidAmount, PaymentDate, Status, Memo
- **cashbook.csv**: Date, AccountID, Counterparty, Description, Amount, Type (Receipt/Payment), LinkEntryID

## 2) Running the Pipeline
```bash
python -m nyfs_suite.cli --data_dir sample_data --out excel/NYFS_Output.xlsx --as_of 2025-09-30
```
- `--as_of` controls AR/AP aging cutoff (optional).

## 3) Outputs
- **TrialBalance**: Signed balances by account
- **IncomeStatement**, **BalanceSheet**, **CashFlow_Indirect**
- **AR_Detail/AP_Detail** and **AR_Aging/AP_Aging**
- **KPIs**: Gross/Net margin, liquidity ratios, etc.
- **RevenueForecast**: 6-month exponential smoothing
- **Insights**: Plain-language flags and suggestions
- **Journal/GeneralLedger**: Normalized double-entry view

## 4) Excel Helpers (VBA)
- Import `.bas` files into a `.xlsm` and run `NYFS_Menu` macro.
- These helpers clean dates, validate chart of accounts, and produce an AR aging table inside Excel.

## 5) Customization
- Extend account mappings in `nyfs_suite/statements.py` for advanced IS/BS groupings.
- Replace `forecast.simple_exponential_smoothing` with your preferred model.
- Add new insights in `insights.py` (rule blocks).

## 6) Support Playbook
- Validate inputs → run pipeline → review Insights → iterate with client assumptions.
