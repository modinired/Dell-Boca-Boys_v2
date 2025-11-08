#!/usr/bin/env python3
"""
Continuous Learning Worker - Runs knowledge extraction daily

This worker:
1. Extracts knowledge from yesterday's events
2. Generates daily reflection
3. Identifies knowledge gaps
4. Syncs with Google Drive (if enabled)

Run as background process or cron job.

Usage:
    # Run continuously (checks every hour, executes at 2 AM daily)
    python scripts/continuous_learning_worker.py

    # Run once now (for testing)
    python scripts/continuous_learning_worker.py --once

    # Background mode
    nohup python scripts/continuous_learning_worker.py > logs/learning_worker.log 2>&1 &
"""

import os
import sys
import time
import schedule
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.learning import (
    KnowledgeExtractor,
    ActiveLearningSystem
)

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('PGHOST', 'localhost'),
    'port': int(os.getenv('PGPORT', 5432)),
    'dbname': os.getenv('PGDATABASE', 'n8n_agent_memory'),
    'user': os.getenv('PGUSER', 'n8n_agent'),
    'password': os.getenv('PGPASSWORD', '')
}

def daily_learning_job():
    """Run daily knowledge extraction and reflection."""
    print(f"\n{'='*70}")
    print(f"DAILY LEARNING JOB - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    try:
        # Initialize extractor
        extractor = KnowledgeExtractor(
            DB_CONFIG,
            os.getenv('LLM_BASE_URL', 'http://localhost:11434/v1'),
            os.getenv('GEMINI_API_KEY', '')
        )

        # 1. Extract knowledge from last 24 hours
        print("1. Extracting knowledge from last 24 hours...")
        print("-" * 70)
        stats = extractor.extract_from_recent_events(lookback_hours=24, min_events=5)
        print(f"✓ Extraction complete:")
        print(f"  - Events processed: {stats.get('events_processed', 0)}")
        print(f"  - Patterns identified: {stats.get('patterns_identified', 0)}")
        print(f"  - Concepts created: {stats.get('concepts_created', 0)}")
        print(f"  - Human expertise captured: {stats.get('human_expertise_captured', 0)}")
        print()

        # 2. Generate daily reflection
        print("2. Generating daily reflection...")
        print("-" * 70)
        reflection = extractor.generate_daily_reflection()
        print(f"✓ Reflection generated ({len(reflection)} chars)")
        print()
        print("Reflection Preview:")
        print("-" * 70)
        print(reflection[:500] + "..." if len(reflection) > 500 else reflection)
        print("-" * 70)
        print()

        # 3. Identify knowledge gaps
        print("3. Identifying knowledge gaps...")
        print("-" * 70)
        active_learner = ActiveLearningSystem(
            DB_CONFIG,
            os.getenv('GEMINI_API_KEY', '')
        )

        gaps = active_learner.identify_knowledge_gaps(lookback_days=7)
        print(f"✓ Identified {len(gaps)} knowledge gaps")
        if gaps:
            print("  Top 3 gaps:")
            for i, gap in enumerate(gaps[:3], 1):
                print(f"    {i}. {gap['subject']} (severity: {gap['severity']:.2f})")
        print()

        # 4. Google Drive sync (if enabled)
        if os.getenv('GOOGLE_DRIVE_SYNC_ENABLED', 'false').lower() == 'true':
            print("4. Syncing with Google Drive...")
            print("-" * 70)

            try:
                from app.learning.google_drive_sync import GoogleDriveKnowledgeSync

                gdrive = GoogleDriveKnowledgeSync(
                    credentials_path=os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH'),
                    learning_logger=None,  # Not needed for upload
                    knowledge_extractor=extractor
                )

                # Upload reflection
                file_id = gdrive.upload_daily_reflection(reflection)
                if file_id:
                    print(f"✓ Reflection uploaded to Google Drive: {file_id[:20]}...")

                # Sync input documents
                sync_stats = gdrive.sync_input_folder()
                print(f"✓ Input sync: {sync_stats['files_processed']} files processed")
                print()

            except Exception as e:
                print(f"⚠️  Google Drive sync failed: {e}")
                print()
        else:
            print("4. Google Drive sync disabled (set GOOGLE_DRIVE_SYNC_ENABLED=true to enable)")
            print()

        # Success summary
        print(f"{'='*70}")
        print("✓ DAILY LEARNING JOB COMPLETE!")
        print(f"{'='*70}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    except Exception as e:
        print(f"\n✗ DAILY LEARNING JOB FAILED: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run continuous learning worker."""
    parser = argparse.ArgumentParser(description='Continuous Learning Worker')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--time', default='02:00', help='Time to run daily (HH:MM format)')
    args = parser.parse_args()

    print("="*70)
    print("CONTINUOUS LEARNING WORKER - STARTED")
    print("="*70)
    print(f"Mode: {'One-time execution' if args.once else 'Continuous (daemon)'}")
    if not args.once:
        print(f"Scheduled: Daily at {args.time}")
    print()

    if args.once:
        # Run once and exit
        daily_learning_job()
    else:
        # Schedule daily execution
        schedule.every().day.at(args.time).do(daily_learning_job)

        # Also run on startup (for testing)
        print("Running initial learning job...")
        daily_learning_job()

        print(f"\nWorker running. Next execution: {args.time}")
        print("Press Ctrl+C to stop\n")

        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\nContinuous learning worker stopped.")
            print("="*70)

if __name__ == "__main__":
    main()
