"""Generate a static HTML dashboard from the Living Data Brain SQLite database."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect

DEFAULT_DB = Path(__file__).with_name("living_data_brain.db")
DEFAULT_OUTPUT = Path(__file__).with_name("living_data_brain_dashboard.html")


def load_tables(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    frames: dict[str, pd.DataFrame] = {}
    for table in tables:
        try:
            frames[table] = pd.read_sql_table(table, engine)
        except Exception as exc:
            print(f"Warning: could not load table '{table}': {exc}", file=sys.stderr)
    return frames


def runs_summary(df: pd.DataFrame) -> dict[str, object]:
    summary: dict[str, object] = {}
    if df.empty:
        return summary
    summary["total_runs"] = int(len(df))
    if "confidence_score" in df.columns and df["confidence_score"].notna().any():
        summary["avg_confidence"] = float(df["confidence_score"].mean())
    if "cost_usd" in df.columns and df["cost_usd"].notna().any():
        summary["total_cost"] = float(df["cost_usd"].sum())
    if "run_ts" in df.columns:
        ts = pd.to_datetime(df["run_ts"], errors="coerce")
        summary["run_history"] = ts.dropna().dt.date.value_counts().sort_index().to_dict()
    if "script_name" in df.columns and df["script_name"].notna().any():
        summary["script_counts"] = df["script_name"].value_counts().head(10).to_dict()
    return summary


def safe_json(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def build_html(runs_info: dict[str, object], tables: dict[str, pd.DataFrame]) -> str:
    generated_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    table_html_blocks: list[str] = []
    for name, frame in tables.items():
        preview = frame.head(100)
        table_html_blocks.append(
            f"<section><h3>{name}</h3>" + preview.to_html(index=False, classes="data-table") + "</section>"
        )

    runs_cards: list[str] = []
    if runs_info:
        if "total_runs" in runs_info:
            runs_cards.append(f"<div class='card'><span>Total Runs</span><strong>{runs_info['total_runs']:,}</strong></div>")
        if "avg_confidence" in runs_info:
            runs_cards.append(
                f"<div class='card'><span>Avg Confidence</span><strong>{runs_info['avg_confidence']:.2%}</strong></div>"
            )
        if "total_cost" in runs_info:
            runs_cards.append(
                f"<div class='card'><span>Total Cost</span><strong>${runs_info['total_cost']:,.2f}</strong></div>"
            )
    else:
        runs_cards.append("<div class='card'><span>No run records found.</span></div>")

    script_chart_data = safe_json(runs_info.get("script_counts", {}))
    history_chart_data = safe_json(runs_info.get("run_history", {}))

    table_sections = "\n".join(table_html_blocks)

    return f"""
<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<title>Living Data Brain Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f7fb; color: #1a202c; }}
header {{ background: #1a365d; color: #fff; padding: 24px; }}
header h1 {{ margin: 0; font-size: 28px; }}
main {{ padding: 24px; max-width: 1200px; margin: 0 auto; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin: 24px 0; }}
.card {{ background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(26, 54, 93, 0.1); }}
.card span {{ display: block; font-size: 14px; color: #4a5568; margin-bottom: 6px; }}
.card strong {{ font-size: 24px; color: #1a202c; }}
section {{ background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(26, 54, 93, 0.08); }}
section h2 {{ margin-top: 0; }}
section h3 {{ margin-top: 0; color: #2c5282; }}
.data-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
.data-table th, .data-table td {{ padding: 8px 10px; border: 1px solid #e2e8f0; text-align: left; }}
.data-table th {{ background: #edf2f7; color: #2d3748; }}
.chart {{ width: 100%; height: 320px; }}
footer {{ text-align: center; padding: 16px; color: #718096; font-size: 13px; }}
</style>
<script>
function renderCharts() {{
    const scriptCounts = {script_chart_data};
    const historyCounts = {history_chart_data};

    if (Object.keys(scriptCounts).length) {{
        const canvas = document.getElementById('scriptChart');
        new window.Chart(canvas, {{
            type: 'bar',
            data: {{
                labels: Object.keys(scriptCounts),
                datasets: [{{
                    label: 'Runs by Script',
                    backgroundColor: '#2c5282',
                    data: Object.values(scriptCounts)
                }}]
            }}
        }});
    }} else {{
        document.getElementById('scriptChart').replaceWith('No script distribution data available.');
    }}

    if (Object.keys(historyCounts).length) {{
        const canvas = document.getElementById('historyChart');
        new window.Chart(canvas, {{
            type: 'line',
            data: {{
                labels: Object.keys(historyCounts),
                datasets: [{{
                    label: 'Runs per Day',
                    borderColor: '#38a169',
                    fill: false,
                    tension: 0.3,
                    data: Object.values(historyCounts)
                }}]
            }}
        }});
    }} else {{
        document.getElementById('historyChart').replaceWith('No temporal run data available.');
    }}
}}
</script>
<script src=\"https://cdn.jsdelivr.net/npm/chart.js@4.4.6/dist/chart.umd.min.js\"></script>
</head>
<body onload=\"renderCharts()\">
<header>
  <h1>Living Data Brain Dashboard</h1>
  <p>Generated {generated_ts}</p>
</header>
<main>
  <section>
    <h2>Key Metrics</h2>
    <div class=\"cards\">{''.join(runs_cards)}</div>
  </section>
  <section>
    <h2>Workflow Activity</h2>
    <canvas id=\"historyChart\" class=\"chart\"></canvas>
    <canvas id=\"scriptChart\" class=\"chart\"></canvas>
  </section>
  <section>
    <h2>Table Snapshots</h2>
    {table_sections}
  </section>
</main>
<footer>Living Data Brain static dashboard. Data is read-only.</footer>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a static Living Data Brain dashboard.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to the SQLite database.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output HTML file.")
    args = parser.parse_args()

    if not args.db.exists():
        print(f"Database not found: {args.db}", file=sys.stderr)
        return 1

    engine = create_engine(f"sqlite:///{args.db}")
    tables = load_tables(engine)
    runs_info: dict[str, object] = {}
    if "runs" in tables:
        runs_info = runs_summary(tables["runs"])
    html = build_html(runs_info, tables)
    args.output.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
