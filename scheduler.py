# scheduler.py — runs the Gmail Cleanup Agent on a configurable schedule
#
# Usage:
#   python scheduler.py
#
# Configure schedule settings in config.py:
#   ENABLE_SCHEDULER   — must be True to use this file
#   USE_DAILY_SCHEDULE — True = run once daily at SCHEDULE_DAILY_AT time
#                        False = run every SCHEDULE_INTERVAL hours/minutes
#
# Keep this process running (e.g. in a VS Code terminal or tmux session).
# It logs run times and any errors so you can leave it unattended.

import schedule
import time
import logging
from datetime import datetime
from main import run
from config import (
    ENABLE_SCHEDULER,
    USE_DAILY_SCHEDULE,
    SCHEDULE_DAILY_AT,
    SCHEDULE_INTERVAL,
    SCHEDULE_INTERVAL_UNIT,
)

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),                          # prints to terminal
        logging.FileHandler("scheduler.log", mode="a"),  # appends to log file
    ],
)
log = logging.getLogger(__name__)


def safe_run():
    """Wraps main.run() with error handling so the scheduler keeps going
    even if a single run fails (e.g. network blip, Gmail API hiccup)."""
    log.info("=" * 55)
    log.info("Scheduled run starting...")
    try:
        run()
        log.info("Run completed successfully.")
    except Exception as e:
        log.error(f"Run failed: {e}", exc_info=True)
    log.info("=" * 55)


def setup_schedule():
    """Registers the job based on config settings."""
    if USE_DAILY_SCHEDULE:
        schedule.every().day.at(SCHEDULE_DAILY_AT).do(safe_run)
        log.info(f"Scheduler configured: daily at {SCHEDULE_DAILY_AT}")
    else:
        if SCHEDULE_INTERVAL_UNIT == "minutes":
            schedule.every(SCHEDULE_INTERVAL).minutes.do(safe_run)
        else:
            schedule.every(SCHEDULE_INTERVAL).hours.do(safe_run)
        log.info(
            f"Scheduler configured: every {SCHEDULE_INTERVAL} {SCHEDULE_INTERVAL_UNIT}"
        )


def next_run_info() -> str:
    """Returns a human-readable string for when the next run is due."""
    jobs = schedule.get_jobs()
    if not jobs:
        return "No jobs scheduled."
    next_run = min(j.next_run for j in jobs)
    delta = next_run - datetime.now()
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        return "Overdue — running now."
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"Next run in {hours}h {minutes}m (at {next_run.strftime('%H:%M')})"
    elif minutes:
        return f"Next run in {minutes}m {seconds}s"
    else:
        return f"Next run in {seconds}s"


def main():
    if not ENABLE_SCHEDULER:
        print(
            "\n[scheduler.py] ENABLE_SCHEDULER is False in config.py.\n"
            "Set it to True to activate the scheduler, then rerun.\n"
        )
        return

    log.info("Gmail Cleanup Agent — Scheduler starting up")
    setup_schedule()

    # Run once immediately on startup so you don't wait for the first interval
    log.info("Running immediately on startup...")
    safe_run()

    log.info(next_run_info())
    log.info("Scheduler is running. Press Ctrl+C to stop.\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)   # check every 30 seconds — low CPU overhead
    except KeyboardInterrupt:
        log.info("Scheduler stopped by user.")


if __name__ == "__main__":
    main()
