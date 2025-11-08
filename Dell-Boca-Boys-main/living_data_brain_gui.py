"""Desktop GUI dashboard for the Living Data Brain SQLite database."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

DB_PATH = Path(__file__).with_name("living_data_brain.db")


@dataclass
class RunMetrics:
    total_runs: int = 0
    avg_confidence: float | None = None
    total_cost: float | None = None
    latest_run: str | None = None
    earliest_run: str | None = None
    script_counts: Dict[str, int] | None = None

    def as_lines(self) -> List[str]:
        lines: List[str] = [f"Total runs: {self.total_runs:,}"]
        if self.avg_confidence is not None:
            lines.append(f"Average confidence: {self.avg_confidence:.2%}")
        if self.total_cost is not None:
            lines.append(f"Aggregate cost: ${self.total_cost:,.2f}")
        if self.latest_run:
            lines.append(f"Latest run: {self.latest_run}")
        if self.earliest_run:
            lines.append(f"Earliest run: {self.earliest_run}")
        if self.script_counts:
            lines.append("Top scripts:")
            for name, count in self.script_counts.items():
                lines.append(f"  - {name}: {count}")
        return lines


def load_tables(db_path: Path) -> dict[str, pd.DataFrame]:
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall()]
        frames: dict[str, pd.DataFrame] = {}
        for table_name in tables:
            try:
                frames[table_name] = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            except Exception as exc:  # pragma: no cover - defensive
                print(f"Warning: failed to load {table_name}: {exc}")
        return frames
    finally:
        conn.close()


def compute_run_metrics(df: pd.DataFrame) -> RunMetrics:
    metrics = RunMetrics(total_runs=int(len(df)))
    if df.empty:
        return metrics

    if "confidence_score" in df.columns and df["confidence_score"].notna().any():
        metrics.avg_confidence = float(df["confidence_score"].mean())

    if "cost_usd" in df.columns and df["cost_usd"].notna().any():
        metrics.total_cost = float(df["cost_usd"].sum())

    if "run_ts" in df.columns:
        ts = pd.to_datetime(df["run_ts"], errors="coerce").dropna()
        if not ts.empty:
            metrics.latest_run = ts.max().isoformat()
            metrics.earliest_run = ts.min().isoformat()

    if "script_name" in df.columns and df["script_name"].notna().any():
        metrics.script_counts = df["script_name"].value_counts().head(5).to_dict()

    return metrics


class DataBrainApp(ttk.Frame):
    def __init__(self, master: tk.Tk, database: Path) -> None:
        super().__init__(master, padding=12)
        self.master.title("Living Data Brain Desktop Dashboard")
        self.master.geometry("960x640")
        self.database = database
        self.table_frames: dict[str, pd.DataFrame] = {}

        self.create_widgets()
        self.refresh_data()

    def create_widgets(self) -> None:
        header = ttk.Label(self, text="Living Data Brain", font=("Helvetica", 20, "bold"))
        header.grid(row=0, column=0, sticky="w")

        self.timestamp_var = tk.StringVar()
        timestamp = ttk.Label(self, textvariable=self.timestamp_var, font=("Helvetica", 10))
        timestamp.grid(row=1, column=0, sticky="w", pady=(0, 10))

        # Metrics box
        self.metrics_text = tk.Text(self, width=60, height=8, state="disabled", bg="#f7fafc", relief="flat")
        self.metrics_text.grid(row=2, column=0, sticky="nsew")

        # Table selector
        selector_frame = ttk.Frame(self)
        selector_frame.grid(row=3, column=0, sticky="ew", pady=(12, 4))
        ttk.Label(selector_frame, text="Table:").pack(side=tk.LEFT)
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(selector_frame, textvariable=self.table_var, state="readonly")
        self.table_combo.pack(side=tk.LEFT, padx=8)
        self.table_combo.bind("<<ComboboxSelected>>", lambda _event: self.show_selected_table())

        refresh_btn = ttk.Button(selector_frame, text="Refresh", command=self.refresh_data)
        refresh_btn.pack(side=tk.RIGHT)

        # Treeview for data preview
        self.tree = ttk.Treeview(self, show="headings")
        tree_scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        self.tree.grid(row=4, column=0, sticky="nsew")
        tree_scroll_y.grid(row=4, column=1, sticky="ns")
        tree_scroll_x.grid(row=5, column=0, sticky="ew")

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.pack(fill="both", expand=True)

    def refresh_data(self) -> None:
        if not self.database.exists():
            messagebox.showerror("Database Missing", f"Could not find database at {self.database}")
            return
        self.table_frames = load_tables(self.database)
        self.timestamp_var.set(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if not self.table_frames:
            self.update_metrics_text(["No tables found in the database."])
            self.table_combo.configure(values=[])
            self.tree.delete(*self.tree.get_children())
            return

        tables = sorted(self.table_frames.keys())
        self.table_combo.configure(values=tables)
        if self.table_var.get() not in tables:
            self.table_var.set(tables[0])
        self.update_metrics_panel()
        self.show_selected_table()

    def update_metrics_panel(self) -> None:
        lines: List[str]
        if "runs" in self.table_frames:
            metrics = compute_run_metrics(self.table_frames["runs"])
            lines = metrics.as_lines()
        else:
            lines = ["Runs table not present; showing first table summary."]
            first_df = self.table_frames[next(iter(self.table_frames))]
            lines.append(f"Rows previewed: {len(first_df):,}")
        self.update_metrics_text(lines)

    def update_metrics_text(self, lines: List[str]) -> None:
        self.metrics_text.configure(state="normal")
        self.metrics_text.delete("1.0", tk.END)
        self.metrics_text.insert(tk.END, "\n".join(lines))
        self.metrics_text.configure(state="disabled")

    def show_selected_table(self) -> None:
        table_name = self.table_var.get()
        if not table_name or table_name not in self.table_frames:
            return
        df = self.table_frames[table_name]
        self.populate_tree(df)

    def populate_tree(self, df: pd.DataFrame) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree.configure(columns=list(df.columns))
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=max(120, len(col) * 10))

        for _, row in df.head(200).iterrows():
            values: List[Any] = []
            for value in row.tolist():
                if isinstance(value, float):
                    values.append(f"{value:.4f}")
                else:
                    values.append(str(value))
            self.tree.insert("", tk.END, values=values)


def main() -> None:
    root = tk.Tk()
    DataBrainApp(root, DB_PATH)
    root.mainloop()


if __name__ == "__main__":
    main()
