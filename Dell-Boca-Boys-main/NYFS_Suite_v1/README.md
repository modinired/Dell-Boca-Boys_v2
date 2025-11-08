# NYFS Suite v1.0.0

A production-grade, plug-and-play Financial Services Suite for SMBs.  
Includes AP/AR processing, GL, financial statements, aging, KPIs, forecasting, and rule-based insights.

## Highlights
- **Malleable**: CSV → Excel pipeline, easy to map into any client.
- **Fast**: Minimal setup; run the CLI and ship reports in minutes.
- **Extensible**: Python package; optional Excel VBA helpers.
- **No placeholders**: All code is real and runnable with standard Python libs.

## Quick Start
1. Install Python 3.10+ and `pip install -r requirements.txt`.
2. Put your data CSVs into `sample_data/` (or replace with client data following the schema).
3. Run the pipeline:

```bash
python -m nyfs_suite.cli --data_dir sample_data --out excel/NYFS_Output.xlsx --as_of 2025-10-29
```

Open `excel/NYFS_Output.xlsx` to view Trial Balance, IS/BS/CF, AR/AP aging, KPIs, revenue forecast, insights, journal, and GL.

## Excel-Only Users
- Use `excel/NYFS_Base.xlsx` as a container for your data.
- Import `.bas` modules from `vba/` into a macro-enabled workbook (.xlsm) to add helpers (Normalize Dates, Validate COA, Build AR Aging).

## Security & Privacy
- All processing is local. No external services are required.
- See `docs/SECURITY.md` for handling client PII/financials.
