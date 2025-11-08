#!/usr/bin/env python3
"""Generate daily/weekly/monthly journal summaries.

Usage examples:
    python scripts/generate_daily_summary.py --period daily
    python scripts/generate_daily_summary.py --period weekly --date 2025-01-15

The script can be scheduled via cron/k8s job to produce reflective summaries
that feed back into the agent's long-term memory routines.
"""
import argparse
from datetime import datetime

from app.tools.journal import daily_journal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate journal summaries")
    parser.add_argument(
        "--period",
        default="daily",
        choices=["daily", "weekly", "monthly"],
        help="Summary granularity",
    )
    parser.add_argument(
        "--date",
        help="Reference date (YYYY-MM-DD). Defaults to today in UTC",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate summary even if one already exists",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ref_date = None
    if args.date:
        ref_date = datetime.strptime(args.date, "%Y-%m-%d").date()

    summary = daily_journal.generate_summary(
        period=args.period,
        reference_date=ref_date,
        force=args.force,
    )

    print("=== Journal Summary ===")
    print(f"Period: {summary['period']} \nRange: {summary['period_start']} -> {summary['period_end']}")
    print("Summary:\n", summary["summary"])
    if summary.get("daily_thought"):
        print("\nDaily Thought:\n", summary["daily_thought"])


if __name__ == "__main__":
    main()
