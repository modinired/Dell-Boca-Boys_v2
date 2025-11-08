from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from .io import read_csvs, write_excel
from .gl import journal_from_subledgers, general_ledger, trial_balance
from .statements import income_statement, balance_sheet, cash_flow_indirect
from .aging import ar_aging, ap_aging
from .kpis import kpis
from .forecast import forecast_revenue
from .insights import insights

def run_pipeline(data_dir: str, out_path: str, as_of: str | None = None):
    data = read_csvs(data_dir)
    coa, ar, ap, cash = data["chart_of_accounts"], data["ar_entries"], data["ap_entries"], data["cashbook"]

    journal = journal_from_subledgers(coa, ar, ap, cash)
    gl = general_ledger(journal, coa)
    tb = trial_balance(gl)

    ar_detail, ar_pivot = ar_aging(ar, as_of=as_of)
    ap_detail, ap_pivot = ap_aging(ap, as_of=as_of)

    is_df = income_statement(tb)
    bs_df = balance_sheet(tb)
    cf_df = cash_flow_indirect(tb)
    kpi_df = kpis(tb, ar_detail, ap_detail)
    fc_df = forecast_revenue(ar_detail)

    insights_df = insights(tb, ar_detail, ap_detail)

    outputs = {
        "TrialBalance": tb,
        "IncomeStatement": is_df,
        "BalanceSheet": bs_df,
        "CashFlow_Indirect": cf_df,
        "AR_Detail": ar_detail,
        "AR_Aging": ar_pivot,
        "AP_Detail": ap_detail,
        "AP_Aging": ap_pivot,
        "KPIs": kpi_df,
        "RevenueForecast": fc_df,
        "Insights": insights_df,
        "Journal": journal,
        "GeneralLedger": gl,
    }
    write_excel(outputs, out_path)

def main():
    parser = argparse.ArgumentParser(description="NYFS Suite Pipeline")
    parser.add_argument("--data_dir", required=True, help="Directory with CSVs")
    parser.add_argument("--out", required=True, help="Output Excel path")
    parser.add_argument("--as_of", default=None, help="As-of date (YYYY-MM-DD)")
    args = parser.parse_args()
    run_pipeline(args.data_dir, args.out, args.as_of)

if __name__ == "__main__":
    main()
