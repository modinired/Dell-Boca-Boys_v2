"""Seed the Living Data Brain SQLite database with demo data."""

from __future__ import annotations

from pathlib import Path

from living_data_brain import ExportEngine

DB_PATH = Path(__file__).with_name("living_data_brain.db")

def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    engine = ExportEngine()
    engine.seed_demo_data(force=True)
    print(f"Living Data Brain database seeded with demo data at {DB_PATH}.")

if __name__ == "__main__":
    main()
