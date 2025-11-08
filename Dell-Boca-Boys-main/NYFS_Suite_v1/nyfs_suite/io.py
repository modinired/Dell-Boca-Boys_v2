from __future__ import annotations
import pandas as pd
from pathlib import Path
from .schema import validate_df

def read_csvs(dirpath: str | Path):
    dirpath = Path(dirpath)
    data = {}
    for key, fname in [
        ("chart_of_accounts","chart_of_accounts.csv"),
        ("customers","customers.csv"),
        ("vendors","vendors.csv"),
        ("items","items.csv"),
        ("ar_entries","ar_entries.csv"),
        ("ap_entries","ap_entries.csv"),
        ("cashbook","cashbook.csv"),
    ]:
        p = dirpath / fname
        df = pd.read_csv(p)
        validate_df(key, df)
        data[key] = df
    return data

def write_excel(outputs: dict[str, pd.DataFrame], out_path: str | Path):
    out_path = Path(out_path)
    with pd.ExcelWriter(out_path, engine="openpyxl") as xw:
        for name, df in outputs.items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
