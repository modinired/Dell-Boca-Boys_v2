"""Generate a text-based Living Data Brain report without any web UI."""

from __future__ import annotations

import argparse
from datetime import datetime, UTC
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect

DEFAULT_DB = Path(__file__).with_name("living_data_brain.db")
DEFAULT_OUTPUT = Path(__file__).with_name("living_data_brain_report.md")


def summarize_runs(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["No runs found in the database."]

    lines: list[str] = []
    lines.append(f"Total runs: {len(df):,}")

    if "confidence_score" in df.columns and df["confidence_score"].notna().any():
        lines.append(f"Average confidence score: {df['confidence_score'].mean():.2%}")

    if "cost_usd" in df.columns and df["cost_usd"].notna().any():
        lines.append(f"Aggregate cost: ${df['cost_usd'].sum():,.2f}")

    if "script_name" in df.columns and df["script_name"].notna().any():
        script_counts = df["script_name"].value_counts().head(10)
        lines.append("Top scripts:")
        for script, count in script_counts.items():
            lines.append(f"  - {script}: {count}")

    if "run_ts" in df.columns:
        ts = pd.to_datetime(df["run_ts"], errors="coerce").dropna()
        if not ts.empty:
            lines.append(f"Latest run: {ts.max().isoformat()}")
            lines.append(f"Earliest run: {ts.min().isoformat()}")

    return lines


def format_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "(empty table)"
    preview = df.head(max_rows)
    return preview.to_markdown(index=False)


def build_report(database: Path) -> str:
    engine = create_engine(f"sqlite:///{database}")
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = ["# Living Data Brain Report", "", f"Generated: {timestamp}", "", f"Database: `{database}`", ""]

    if not tables:
        lines.append("No tables found in the database.")
        return "\n".join(lines)

    if "runs" in tables:
        runs_df = pd.read_sql_table("runs", engine)
        lines.append("## Runs Summary")
        lines.extend(summarize_runs(runs_df))
        lines.append("")
    else:
        lines.append("Runs table not found; skipping run summary.\n")

    lines.append("## Table Previews")
    for table in tables:
        df = pd.read_sql_table(table, engine)
        lines.append(f"### `{table}`")
        lines.append(format_table(df))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Produce a markdown report from the Living Data Brain DB.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to SQLite database (default: living_data_brain.db).")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Report output path (default: living_data_brain_report.md).")
    args = parser.parse_args()

    if not args.db.exists():
        print(f"Database not found: {args.db}")
        return 1

    report = build_report(args.db)
    args.output.write_text(report, encoding="utf-8")
    print(f"Report written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
