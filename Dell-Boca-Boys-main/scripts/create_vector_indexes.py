#!/usr/bin/env python3
"""
Create vector indexes for the learning system.

Run this AFTER you have at least ~1000 events in the database.
Vector indexes improve similarity search performance dramatically.

Usage:
    python scripts/create_vector_indexes.py
"""

import os
import sys
from dotenv import load_dotenv
import psycopg

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('PGHOST', 'localhost'),
    'port': int(os.getenv('PGPORT', 5432)),
    'dbname': os.getenv('PGDATABASE', 'n8n_agent_memory'),
    'user': os.getenv('PGUSER', 'n8n_agent'),
    'password': os.getenv('PGPASSWORD', '')
}

def main():
    """Create vector indexes."""
    print("="*70)
    print("VECTOR INDEX CREATION")
    print("="*70)
    print()

    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Check event count
        cursor.execute("SELECT COUNT(*) FROM episodic_events WHERE text_embedding IS NOT NULL")
        event_count = cursor.fetchone()[0]

        print(f"Events with embeddings: {event_count}")

        if event_count < 100:
            print("\n⚠️  WARNING: Less than 100 events with embeddings.")
            print("Vector indexes work best with at least 1000 events.")
            print()
            response = input("Continue anyway? (yes/no): ").lower()
            if response != 'yes':
                print("Cancelled.")
                return

        print("\nCreating vector indexes (this may take a few minutes)...")
        print()

        # 1. Episodic events - text embedding
        print("1. Creating index: idx_episodic_text_embedding...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodic_text_embedding
                ON episodic_events
                USING ivfflat (text_embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
            print("   ✓ Created")
        except Exception as e:
            print(f"   ⚠️  {e}")

        # 2. Episodic events - code embedding
        print("2. Creating index: idx_episodic_code_embedding...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodic_code_embedding
                ON episodic_events
                USING ivfflat (code_embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
            print("   ✓ Created")
        except Exception as e:
            print(f"   ⚠️  {e}")

        # 3. Semantic concepts - concept embedding
        print("3. Creating index: idx_semantic_embedding...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_semantic_embedding
                ON semantic_concepts
                USING ivfflat (concept_embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
            print("   ✓ Created")
        except Exception as e:
            print(f"   ⚠️  {e}")

        # 4. Human expertise - embedding
        print("4. Creating index: idx_expertise_embedding...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expertise_embedding
                ON human_expertise
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 50)
            """)
            print("   ✓ Created")
        except Exception as e:
            print(f"   ⚠️  {e}")

        # 5. Procedural knowledge - embedding
        print("5. Creating index: idx_procedural_embedding...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_procedural_embedding
                ON procedural_knowledge
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 50)
            """)
            print("   ✓ Created")
        except Exception as e:
            print(f"   ⚠️  {e}")

        conn.commit()
        conn.close()

        print()
        print("="*70)
        print("✓ VECTOR INDEXES CREATED SUCCESSFULLY!")
        print("="*70)
        print()
        print("Similarity search queries will now be much faster.")
        print()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
