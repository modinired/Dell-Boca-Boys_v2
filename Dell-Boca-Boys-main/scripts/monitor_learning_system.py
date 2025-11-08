#!/usr/bin/env python3
"""
Monitor learning system health.

Checks:
- Event ingestion rate
- Knowledge extraction activity
- Reflection generation
- Knowledge base growth

Usage:
    python scripts/monitor_learning_system.py

    # Or run periodically
    watch -n 300 python scripts/monitor_learning_system.py  # Every 5 minutes
"""

import os
import sys
from dotenv import load_dotenv
import psycopg
from datetime import datetime, timedelta

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('PGHOST', 'localhost'),
    'port': int(os.getenv('PGPORT', 5432)),
    'dbname': os.getenv('PGDATABASE', 'n8n_agent_memory'),
    'user': os.getenv('PGUSER', 'n8n_agent'),
    'password': os.getenv('PGPASSWORD', '')
}

def check_health():
    """Check learning system health."""
    print("="*70)
    print(f"LEARNING SYSTEM HEALTH CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print()

    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. Event ingestion
        print("1. Event Ingestion")
        print("-" * 70)

        cursor.execute("""
            SELECT COUNT(*) FROM episodic_events
            WHERE timestamp >= NOW() - INTERVAL '24 hours'
        """)
        events_today = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM episodic_events
            WHERE timestamp >= NOW() - INTERVAL '7 days'
        """)
        events_week = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM episodic_events")
        events_total = cursor.fetchone()[0]

        print(f"  Events today:    {events_today:,}")
        print(f"  Events this week: {events_week:,}")
        print(f"  Events total:     {events_total:,}")

        if events_today == 0:
            print("  ⚠️  WARNING: No events logged today!")
        else:
            print("  ✓ Event ingestion active")
        print()

        # 2. Knowledge extraction
        print("2. Knowledge Extraction")
        print("-" * 70)

        cursor.execute("""
            SELECT COUNT(*) FROM semantic_concepts
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        concepts_week = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM semantic_concepts")
        concepts_total = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(confidence_score) FROM semantic_concepts")
        avg_confidence = cursor.fetchone()[0] or 0

        print(f"  Concepts this week: {concepts_week}")
        print(f"  Concepts total:     {concepts_total}")
        print(f"  Avg confidence:     {avg_confidence:.2f}")

        if concepts_week == 0 and events_today > 100:
            print("  ⚠️  WARNING: No concepts extracted this week despite high activity!")
        else:
            print("  ✓ Knowledge extraction working")
        print()

        # 3. Reflections
        print("3. Daily Reflections")
        print("-" * 70)

        cursor.execute("""
            SELECT COUNT(*) FROM learning_reflections
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        reflections_week = cursor.fetchone()[0]

        cursor.execute("""
            SELECT MAX(created_at) FROM learning_reflections
        """)
        last_reflection = cursor.fetchone()[0]

        print(f"  Reflections this week: {reflections_week}")
        if last_reflection:
            print(f"  Last reflection:       {last_reflection.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"  Last reflection:       Never")

        if reflections_week == 0:
            print("  ⚠️  WARNING: No reflections generated this week!")
        else:
            print("  ✓ Reflection generation active")
        print()

        # 4. Human expertise
        print("4. Human Expertise")
        print("-" * 70)

        cursor.execute("""
            SELECT COUNT(*) FROM human_expertise
            WHERE captured_at >= NOW() - INTERVAL '7 days'
        """)
        expertise_week = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM human_expertise")
        expertise_total = cursor.fetchone()[0]

        print(f"  Expertise this week: {expertise_week}")
        print(f"  Expertise total:     {expertise_total}")

        if expertise_week > 0:
            print("  ✓ Capturing human corrections")
        else:
            print("  ℹ️  No corrections captured this week")
        print()

        # 5. User satisfaction
        print("5. User Satisfaction")
        print("-" * 70)

        cursor.execute("""
            SELECT
                AVG(user_rating) FILTER (WHERE timestamp >= NOW() - INTERVAL '7 days'),
                AVG(user_rating) FILTER (WHERE timestamp >= NOW() - INTERVAL '30 days'),
                COUNT(*) FILTER (WHERE user_rating IS NOT NULL AND timestamp >= NOW() - INTERVAL '7 days')
            FROM episodic_events
        """)
        rating_week, rating_month, rated_count = cursor.fetchone()

        if rating_week:
            print(f"  Avg rating (7d):  {rating_week:.2f}/5.0")
        else:
            print(f"  Avg rating (7d):  N/A")

        if rating_month:
            print(f"  Avg rating (30d): {rating_month:.2f}/5.0")
        else:
            print(f"  Avg rating (30d): N/A")

        print(f"  Rated interactions:  {rated_count}")

        if rating_week and rating_week < 3.5:
            print("  ⚠️  WARNING: User satisfaction below 3.5!")
        elif rating_week:
            print("  ✓ User satisfaction good")
        print()

        # 6. Success rate
        print("6. Success Rate")
        print("-" * 70)

        cursor.execute("""
            SELECT
                SUM(CASE WHEN success THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0)
            FROM episodic_events
            WHERE timestamp >= NOW() - INTERVAL '7 days'
        """)
        success_rate = cursor.fetchone()[0] or 0

        print(f"  Success rate (7d): {success_rate:.1%}")

        if success_rate < 0.7:
            print("  ⚠️  WARNING: Success rate below 70%!")
        else:
            print("  ✓ Success rate healthy")
        print()

        # Overall health
        print("="*70)

        health_score = 0
        max_score = 6

        if events_today > 0:
            health_score += 1
        if concepts_week > 0 or events_today < 100:
            health_score += 1
        if reflections_week > 0:
            health_score += 1
        if rating_week and rating_week >= 3.5:
            health_score += 1
        elif not rating_week:
            health_score += 0.5
        if success_rate >= 0.7:
            health_score += 1
        health_score += 1  # Base score

        health_pct = (health_score / max_score) * 100

        if health_pct >= 80:
            status = "✓ HEALTHY"
        elif health_pct >= 60:
            status = "⚠️  NEEDS ATTENTION"
        else:
            status = "✗ CRITICAL"

        print(f"OVERALL HEALTH: {status} ({health_pct:.0f}%)")
        print("="*70)
        print()

        conn.close()

    except Exception as e:
        print(f"\n✗ Health check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_health()
