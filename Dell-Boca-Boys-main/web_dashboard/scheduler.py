"""Utility functions for scheduling periodic jobs in the Dell Boca Vista dashboard.

This module encapsulates the APScheduler integration used for the automated
summary functionality.  Importing APScheduler is deferred within the
`create_summary_scheduler` function so that the dashboard can run in
environments where APScheduler is not installed.  The returned scheduler
object can be shutdown on application exit.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional


def create_summary_scheduler(agent: Any) -> Optional[object]:
    """Create and start the automated summary scheduler.

    If APScheduler is available, this function creates a BackgroundScheduler
    instance, schedules three daily jobs to call
    ``agent.generate_automated_summary()``, starts the scheduler and prints
    status messages.  If APScheduler is not installed, a warning is printed
    and ``None`` is returned.

    Args:
        agent: The agent object providing ``generate_automated_summary``.

    Returns:
        The running scheduler instance, or ``None`` if APScheduler is not
        available.
    """
    try:
        from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
        from apscheduler.triggers.cron import CronTrigger  # type: ignore
    except Exception:
        # APScheduler not installed; disable automated summaries
        print("\n⚠️ APScheduler not available; automated summaries disabled")
        return None

    scheduler: Any = BackgroundScheduler()

    def scheduled_summary_job() -> None:
        """Wrapper job to trigger summary generation."""
        print(
            f"\n⏰ [Scheduler] Triggered automated summary at "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )
        agent.generate_automated_summary()

    # Define the cron schedules: 9 AM, 2 PM, 8 PM
    scheduler.add_job(
        scheduled_summary_job,
        CronTrigger(hour=9, minute=0),
        id="morning_summary",
        name="Morning Summary (9 AM)",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_summary_job,
        CronTrigger(hour=14, minute=0),
        id="afternoon_summary",
        name="Afternoon Summary (2 PM)",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_summary_job,
        CronTrigger(hour=20, minute=0),
        id="evening_summary",
        name="Evening Summary (8 PM)",
        replace_existing=True,
    )

    scheduler.start()
    print("\n📅 Automated Summary Scheduler Started:")
    print("   ⏰ Morning Review: 9:00 AM")
    print("   ⏰ Afternoon Review: 2:00 PM")
    print("   ⏰ Evening Review: 8:00 PM")

    return scheduler