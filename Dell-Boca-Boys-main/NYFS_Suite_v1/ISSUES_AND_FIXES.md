# NYFS_Suite_v1 - Issues & Fixes Reference Guide

## Quick Links to Specific Issues

---

## ISSUE 1: Pandas Dtype Deprecation Warning (aging.py:24,39)

### Problem
```python
# aging.py line 24
totals = pivot.sum(numeric_only=True)
totals["CustomerID"] = "TOTAL"  # String into float column!
pivot = pd.concat([pivot, pd.DataFrame([totals])], ignore_index=True)
```

**Error**: FutureWarning - Setting item incompatible dtype
**Status**: Functional now, breaks in pandas 3.0+

### Fix
```python
# Approach 1: Convert column dtype first
pivot = pivot.astype({"CustomerID": "object"}, errors='ignore')
totals["CustomerID"] = "TOTAL"

# Approach 2: Create proper DataFrame with correct dtypes
totals_df = pd.DataFrame({
    "CustomerID": ["TOTAL"],
    **{col: [totals[col]] for col in pivot.columns if col != "CustomerID"}
})
pivot = pd.concat([pivot, totals_df], ignore_index=True)

# Approach 3: Use loc with proper typing
pivot.loc[len(pivot)] = totals  # After ensuring dtype compatibility
```

### Location
- File: `/home/user/Dell-Boca-Boys/NYFS_Suite_v1/nyfs_suite/aging.py`
- Lines: 24 and 39 (same issue in `ap_aging()`)

### Effort: LOW (1 hour)

---

## ISSUE 2: Hard-Coded Account References (gl.py, statements.py, kpis.py)

### Problem
System assumes specific account ID names exist and uses them as string literals:

```python
# gl.py lines 20-21 (AR invoice)
j.append({"AccountID": "AR", ...})  # Hard-coded!
j.append({"AccountID": "Cash", ...})  # Hard-coded!

# statements.py line 9 (COGS detection)
cogs = inc[inc["AccountID"].str.contains("COGS", case=False, na=False)][...]

# kpis.py line 14-15 (Inventory detection)
inventory = tb[tb["AccountID"].str.contains("Inventory", case=False, na=False)][...]
cash = tb[tb["AccountID"].str.contains("Cash", case=False, na=False)][...]
```

**Impact**: 
- Client using "ACCT_REC" instead of "AR" → System fails
- Different COGS naming → Statement is wrong
- Different Cash account → Liquidity analysis fails

### Fix: Configuration-Based Approach

**Step 1: Create account mapping config**
```python
# nyfs_suite/config.py
class AccountMappingConfig:
    """Configuration for account ID mapping."""
    
    def __init__(self):
        # Standard US GAAP defaults
        self.ar_account = "AR"
        self.ap_account = "AP"
        self.cash_account = "Cash"
        self.revenue_accounts = ["Sales", "Revenue", "ServiceRevenue"]
        self.cogs_accounts = ["COGS", "CostOfSales"]
        self.inventory_accounts = ["Inventory"]
        self.expense_accounts = None  # All Type=Expense if not specified
        
    @classmethod
    def from_dict(cls, mapping_dict):
        """Load from dictionary (JSON/YAML)."""
        config = cls()
        config.__dict__.update(mapping_dict)
        return config
```

**Step 2: Refactor journal_from_subledgers()**
```python
# gl.py (BEFORE)
def journal_from_subledgers(coa, ar, ap, cash):
    j = []
    for _, r in ar.iterrows():
        ...
        j.append({"AccountID": "AR", ...})  # Hard-coded
        
# gl.py (AFTER)
def journal_from_subledgers(coa, ar, ap, cash, config=None):
    if config is None:
        config = AccountMappingConfig()
    
    j = []
    for _, r in ar.iterrows():
        ...
        j.append({"AccountID": config.ar_account, ...})  # Configurable
```

**Step 3: Update all calculation functions**
```python
# statements.py (BEFORE)
def income_statement(tb):
    cogs = inc[inc["AccountID"].str.contains("COGS", ...)]

# statements.py (AFTER)
def income_statement(tb, config=None):
    if config is None:
        config = AccountMappingConfig()
    cogs = tb[tb["AccountID"].isin(config.cogs_accounts)]
```

**Step 4: Thread config through CLI**
```python
# cli.py
def run_pipeline(data_dir, out_path, as_of=None, account_mapping=None):
    config = AccountMappingConfig.from_dict(account_mapping or {})
    
    journal = journal_from_subledgers(coa, ar, ap, cash, config)
    is_df = income_statement(tb, config)
    kpi_df = kpis(tb, ar_detail, ap_detail, config)
    # ... etc
```

### Files to Modify
- `nyfs_suite/config.py` (new file)
- `nyfs_suite/gl.py` (lines 13-45)
- `nyfs_suite/statements.py` (lines 5-52)
- `nyfs_suite/kpis.py` (lines 5-37)
- `nyfs_suite/insights.py` (lines 5-29)
- `nyfs_suite/cli.py` (lines 13-47)

### Effort: HIGH (8-12 hours) - Requires refactoring multiple functions

---

## ISSUE 3: Missing Error Handling in I/O (io.py:6-21)

### Problem
```python
# io.py
def read_csvs(dirpath: str | Path):
    dirpath = Path(dirpath)
    for key, fname in [...]:
        p = dirpath / fname
        df = pd.read_csv(p)  # No error handling!
        validate_df(key, df)
    return data
```

**Impact**: 
- Missing file → FileNotFoundError (cryptic to user)
- Invalid CSV → pandas.errors.ParserError
- Wrong columns → ValueError (not helpful)

### Fix
```python
# io.py (BEFORE)
def read_csvs(dirpath: str | Path):
    dirpath = Path(dirpath)
    for key, fname in [...]:
        p = dirpath / fname
        df = pd.read_csv(p)
        validate_df(key, df)
    return data

# io.py (AFTER)
def read_csvs(dirpath: str | Path):
    dirpath = Path(dirpath)
    if not dirpath.exists():
        raise ValueError(f"Data directory not found: {dirpath}")
    
    data = {}
    for key, fname in [...]:
        p = dirpath / fname
        
        # Check file exists
        if not p.exists():
            raise FileNotFoundError(
                f"Required file missing: {fname}\n"
                f"Expected at: {p}\n"
                f"Please ensure all required CSVs are in {dirpath}"
            )
        
        # Try to read CSV
        try:
            df = pd.read_csv(p)
        except pd.errors.EmptyDataError:
            raise ValueError(f"{fname} is empty. Please provide data.")
        except Exception as e:
            raise ValueError(f"Failed to read {fname}: {e}")
        
        # Validate structure
        try:
            validate_df(key, df)
        except ValueError as e:
            raise ValueError(f"Validation failed for {fname}: {e}")
        
        data[key] = df
    
    return data
```

### Location
- File: `/home/user/Dell-Boca-Boys/NYFS_Suite_v1/nyfs_suite/io.py`
- Lines: 6-21

### Effort: LOW (2 hours)

---

## ISSUE 4: Incomplete Data Validation (schema.py:29-32)

### Problem
```python
# schema.py
def validate_df(name: str, df: pd.DataFrame):
    required = SCHEMA[name]
    ensure_columns(df, required, name)  # Only checks columns exist!
    return True

# Missing validation for:
# - Negative amounts
# - Duplicate invoices
# - Future-dated transactions
# - Payment > Amount + Tax
# - Required field nulls
```

### Fix
```python
# schema.py (AFTER)
def validate_df(name: str, df: pd.DataFrame, raise_on_error=True):
    """Validate dataframe against schema and business rules."""
    errors = []
    warnings = []
    
    # Check required columns
    required = SCHEMA[name]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
    
    # Common validations
    if "Amount" in df.columns:
        negative = df[df["Amount"] < 0]
        if not negative.empty:
            warnings.append(f"Found {len(negative)} negative amounts")
    
    if "EntryID" in df.columns:
        dups = df[df.duplicated(subset=["EntryID"], keep=False)]
        if not dups.empty:
            errors.append(f"Duplicate EntryIDs found: {dups['EntryID'].unique().tolist()}")
    
    # Invoice-specific validation
    if name == "ar_entries":
        # Check PaidAmount <= Amount + Tax
        df_copy = df.copy()
        df_copy["Total"] = df_copy["Amount"].fillna(0) + df_copy["Tax"].fillna(0)
        df_copy["Paid"] = df_copy["PaidAmount"].fillna(0)
        overpaid = df_copy[df_copy["Paid"] > df_copy["Total"]]
        if not overpaid.empty:
            errors.append(f"Overpayment detected: {overpaid['EntryID'].tolist()}")
        
        # Check PaymentDate >= InvoiceDate
        df_copy["InvoiceDate"] = pd.to_datetime(df_copy["InvoiceDate"], errors="coerce")
        df_copy["PaymentDate"] = pd.to_datetime(df_copy["PaymentDate"], errors="coerce")
        late_payment = df_copy[
            (df_copy["PaymentDate"].notna()) & 
            (df_copy["PaymentDate"] < df_copy["InvoiceDate"])
        ]
        if not late_payment.empty:
            errors.append(f"Payment before invoice date: {late_payment['EntryID'].tolist()}")
    
    # Report results
    if errors:
        msg = f"\n{name} validation failed:\n" + "\n".join(errors)
        if raise_on_error:
            raise ValueError(msg)
        return False
    
    if warnings:
        print(f"Warnings for {name}: {' | '.join(warnings)}")
    
    return True
```

### Location
- File: `/home/user/Dell-Boca-Boys/NYFS_Suite_v1/nyfs_suite/schema.py`
- Lines: 29-32

### Effort: MEDIUM (4-6 hours)

---

## ISSUE 5: Incomplete Cash Flow Statement (statements.py:39-52)

### Problem
```python
# statements.py
def cash_flow_indirect(tb: pd.DataFrame):
    rows = [
        ["Net Income (proxy)", calculated_value],
        ["Operating Cash Flow (approx)", None],  # Empty!
        ["Investing Cash Flow (approx)", None],  # Empty!
        ["Financing Cash Flow (approx)", None],  # Empty!
        ["Net Change in Cash (approx)", None]    # Empty!
    ]
    return pd.DataFrame(rows, columns=["Line","Amount"])
```

### Fix: Proper Indirect Method CF
```python
# statements.py (AFTER)
def cash_flow_indirect(gl: pd.DataFrame, periods: list = None):
    """
    Calculate cash flow using indirect method.
    Requires period GL data for proper calculation.
    
    Args:
        gl: General Ledger with Date column
        periods: List of period dates for comparison (e.g., [start_date, end_date])
    """
    
    if periods is None:
        # Approximation with single period (less accurate)
        rows = [
            ["Net Income", ...],  # From IS
            ["Adjustments:"],
            ["  Depreciation & Amortization", 0],  # TODO: Calculate
            ["  Loss/Gain on disposal", 0],        # TODO: Calculate
            ["Changes in Working Capital:"],
            ["  Increase in AR", 0],               # TODO: Calculate
            ["  Decrease in AR", 0],
            ["  Increase in AP", 0],
            ["  Decrease in AP", 0],
            ["Net Operating Cash Flow", None],
            ["Investing Activities:"],
            ["  Asset Purchases", 0],              # TODO: Calculate
            ["  Asset Sales", 0],
            ["Net Investing Cash Flow", None],
            ["Financing Activities:"],
            ["  Debt Proceeds", 0],
            ["  Debt Repayment", 0],
            ["  Equity Contributions", 0],
            ["  Distributions", 0],
            ["Net Financing Cash Flow", None],
            ["Net Change in Cash", None],
        ]
    else:
        # Proper calculation with period comparison
        start_period = periods[0]
        end_period = periods[-1]
        
        # Get cash balance at start and end
        start_cash = gl[gl["Date"] <= start_period]["Cash"].iloc[0] if len(gl) else 0
        end_cash = gl[gl["Date"] <= end_period]["Cash"].iloc[-1] if len(gl) else 0
        
        # Get period GL balances
        gl_start = gl[gl["Date"] <= start_period].groupby("AccountID").sum()
        gl_end = gl[gl["Date"] <= end_period].groupby("AccountID").sum()
        
        # Calculate changes
        # ... (full implementation)
        
        rows = [...]
    
    return pd.DataFrame(rows, columns=["Line","Amount"])
```

### Location
- File: `/home/user/Dell-Boca-Boys/NYFS_Suite_v1/nyfs_suite/statements.py`
- Lines: 39-52

### Effort: MEDIUM (6-8 hours) - Requires proper GL period tracking

---

## ISSUE 6: Missing Financial Ratios (kpis.py)

### Problem
Only 4 ratios calculated; missing 8+ standard financial metrics.

### Fix: Add Comprehensive Ratio Suite
```python
# kpis.py (AFTER)
def kpis(tb: pd.DataFrame, ar_detail: pd.DataFrame, ap_detail: pd.DataFrame, 
         config: AccountMappingConfig = None):
    """Calculate comprehensive financial ratios."""
    
    if config is None:
        from .config import AccountMappingConfig
        config = AccountMappingConfig()
    
    # Profitability Ratios
    revenue = tb[tb["Type"]=="Revenue"]["SignedBalance"].sum()
    cogs = tb[tb["AccountID"].isin(config.cogs_accounts)]["SignedBalance"].sum()
    expenses = tb[tb["Type"]=="Expense"]["SignedBalance"].sum() - cogs
    net_income = revenue - cogs - expenses
    
    gross_margin = (revenue - cogs) / revenue if revenue else np.nan
    net_margin = net_income / revenue if revenue else np.nan
    
    # Efficiency Ratios
    total_assets = tb[tb["Type"]=="Asset"]["SignedBalance"].sum()
    asset_turnover = revenue / total_assets if total_assets else np.nan
    
    # Return Ratios
    roa = net_income / total_assets if total_assets else np.nan
    
    total_equity = tb[tb["Type"]=="Equity"]["SignedBalance"].sum()
    roe = net_income / total_equity if total_equity else np.nan
    
    # Liquidity Ratios
    current_assets = tb[(tb["Type"]=="Asset") & 
                       (~tb["AccountID"].isin(config.fixed_asset_accounts))]["SignedBalance"].sum()
    current_liab = tb[(tb["Type"]=="Liability") & 
                     (~tb["AccountID"].isin(config.longterm_liab_accounts))]["SignedBalance"].sum()
    
    current_ratio = current_assets / current_liab if current_liab else np.nan
    
    # Working Capital
    working_capital = current_assets - current_liab
    
    # Days ratios
    avg_ar = ar_detail["OpenAmount"].mean()
    dso = (avg_ar / revenue * 365) if revenue else np.nan  # Days Sales Outstanding
    
    avg_ap = ap_detail["OpenAmount"].mean()
    dpo = (avg_ap / cogs * 365) if cogs else np.nan  # Days Payable Outstanding
    
    # Leverage
    total_liab = tb[tb["Type"]=="Liability"]["SignedBalance"].sum()
    debt_to_equity = total_liab / total_equity if total_equity else np.nan
    
    data = [
        ["PROFITABILITY"],
        ["  Gross Margin %", gross_margin],
        ["  Net Margin %", net_margin],
        ["  Return on Assets (ROA) %", roa * 100 if not np.isnan(roa) else np.nan],
        ["  Return on Equity (ROE) %", roe * 100 if not np.isnan(roe) else np.nan],
        [""],
        ["EFFICIENCY"],
        ["  Asset Turnover", asset_turnover],
        ["  Days Sales Outstanding (DSO)", dso],
        ["  Days Payable Outstanding (DPO)", dpo],
        [""],
        ["LIQUIDITY"],
        ["  Current Ratio", current_ratio],
        ["  Working Capital", working_capital],
        [""],
        ["LEVERAGE"],
        ["  Debt-to-Equity", debt_to_equity],
        [""],
        ["SCALE"],
        ["  Revenue", revenue],
        ["  COGS", cogs],
        ["  Operating Expenses", expenses],
        ["  Total Assets", total_assets],
        ["  Total Equity", total_equity],
    ]
    
    return pd.DataFrame(data, columns=["Metric","Value"])
```

### Location
- File: `/home/user/Dell-Boca-Boys/NYFS_Suite_v1/nyfs_suite/kpis.py`
- Lines: 5-37

### Effort: LOW (2-3 hours)

---

## ISSUE 7: No Audit Trail

### Problem
No tracking of who created/modified entries or when.

### Fix: Add Audit Fields
```python
# Extended schema in schema.py
EXTENDED_SCHEMA = {
    "ar_entries": [
        # Original fields
        "EntryID", "CustomerID", "InvoiceNo", "InvoiceDate", "DueDate",
        "AccountID", "Amount", "Tax", "PaidAmount", "PaymentDate", "Status", "Memo",
        # New audit fields
        "CreatedDate", "CreatedBy", "ModifiedDate", "ModifiedBy",
        "ApprovedDate", "ApprovedBy", "PostedDate",
        "ChangeReason"  # Why was it modified?
    ],
    "ap_entries": [
        # Original fields
        "EntryID", "VendorID", "InvoiceNo", "InvoiceDate", "DueDate",
        "AccountID", "Amount", "Tax", "PaidAmount", "PaymentDate", "Status", "Memo",
        # New audit fields
        "CreatedDate", "CreatedBy", "ModifiedDate", "ModifiedBy",
        "ApprovedDate", "ApprovedBy", "PostedDate",
        "ChangeReason"
    ],
    # Similar for other transaction tables
}

# Add audit handling in CLI
def run_pipeline(data_dir, out_path, as_of=None, user_id=None):
    """
    Run pipeline with audit trail support.
    
    Args:
        user_id: Current user (required for audit trail)
    """
    if user_id is None:
        user_id = "system"
    
    data = read_csvs(data_dir)
    
    # Add processing timestamp
    timestamp = pd.Timestamp.now()
    
    # Thread audit info through pipeline
    journal = journal_from_subledgers(coa, ar, ap, cash, user_id=user_id)
    # ... etc
```

### Effort: MEDIUM (4-6 hours) - Schema change + field threading

---

## Summary of All Issues

| ID | Severity | Issue | File | Effort | Impact |
|----|----------|-------|------|--------|--------|
| 1 | LOW | Pandas dtype warning | aging.py | 1h | Will error in pandas 3.0+ |
| 2 | HIGH | Hard-coded account IDs | Multiple | 8-12h | Non-scalable, breaks with different COAs |
| 3 | MEDIUM | Missing error handling | io.py | 2h | Cryptic failures, poor UX |
| 4 | MEDIUM | Incomplete validation | schema.py | 4-6h | Data quality risk |
| 5 | MEDIUM | Empty CF statement | statements.py | 6-8h | Incomplete reporting |
| 6 | LOW | Missing ratios | kpis.py | 2-3h | Limited financial analysis |
| 7 | HIGH | No audit trail | Multiple | 4-6h | Compliance risk |

---

## Testing for Fixes

After implementing each fix, test with:

```python
# Test hard-coded account fix
import json
config_dict = {
    "ar_account": "ACCT_REC",  # Different from default
    "ap_account": "ACCT_PAY",
    "cash_account": "CHECKING"
}
config = AccountMappingConfig.from_dict(config_dict)
# Run pipeline with different account names

# Test error handling fix
def test_missing_file():
    try:
        read_csvs("/nonexistent/path")
    except FileNotFoundError as e:
        assert "Required file missing" in str(e)
        print("✓ Helpful error message shown")

# Test validation fix
def test_validation():
    bad_data = pd.DataFrame({
        'EntryID': [1, 1, 2],  # Duplicate
        'Amount': [100, -50, 200],  # Negative
        'PaidAmount': [150, 20, 200]  # Overpayment
    })
    try:
        validate_df("ar_entries", bad_data)
    except ValueError as e:
        assert "Duplicate" in str(e)
        assert "Overpayment" in str(e)
        print("✓ All validations caught")
```

