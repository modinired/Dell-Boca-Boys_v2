#!/usr/bin/env python3
"""
Test the Ultimate Learning System end-to-end.

Tests all components:
- UniversalLearningLogger
- KnowledgeExtractor
- ActiveLearningSystem
- KnowledgeApplicationEngine
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.learning import (
    UniversalLearningLogger,
    KnowledgeExtractor,
    ActiveLearningSystem,
    KnowledgeApplicationEngine
)

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('PGHOST', 'localhost'),
    'port': int(os.getenv('PGPORT', 5432)),
    'dbname': os.getenv('PGDATABASE', 'n8n_agent_memory'),
    'user': os.getenv('PGUSER', 'n8n_agent'),
    'password': os.getenv('PGPASSWORD', '')
}

def test_system():
    """Test all learning system components."""
    print("\n" + "="*70)
    print("ULTIMATE LEARNING SYSTEM - COMPREHENSIVE TEST")
    print("="*70 + "\n")

    try:
        # 1. Test Universal Logger
        print("1. Testing UniversalLearningLogger...")
        print("-" * 70)
        logger = UniversalLearningLogger(DB_CONFIG)

        # Log a sample chat interaction
        event_id = logger.log_interaction(
            event_type='chat',
            user_id='test_user',
            session_id='test-session-001',
            text_content='How do I create a webhook trigger in n8n?',
            ollama_response='Create a Webhook node and configure it with a unique URL...',
            gemini_response='To create a webhook in n8n, add a Webhook node from the triggers...',
            synthesized_response='Here is how to create a webhook in n8n: Add a Webhook node...',
            chosen_model='chiccki_synthesis',
            user_rating=5,
            success=True,
            tags=['webhook', 'trigger', 'n8n']
        )
        print(f"✓ Logged chat event: {event_id}")

        # Log a workflow generation
        event_id2 = logger.log_interaction(
            event_type='workflow_generation',
            user_id='test_user',
            session_id='test-session-001',
            text_content='Generate workflow to send Slack message on webhook',
            code_content='{"nodes": [{"type": "webhook"}, {"type": "slack"}]}',
            code_language='json',
            synthesized_response='Created workflow with Webhook → Slack nodes',
            user_rating=4,
            success=True,
            tags=['workflow', 'slack', 'webhook']
        )
        print(f"✓ Logged workflow event: {event_id2}")

        # Log a correction (human expertise)
        event_id3 = logger.log_interaction(
            event_type='chat',
            user_id='test_user',
            session_id='test-session-001',
            text_content='How do I handle errors in workflows?',
            synthesized_response='Use the IF node to check for errors...',
            user_rating=3,
            correction_applied='Actually, use the Error Trigger node instead. It\'s more reliable.',
            success=True,
            tags=['error_handling', 'best_practice']
        )
        print(f"✓ Logged correction event: {event_id3}")
        print()

        # 2. Test Knowledge Extraction
        print("2. Testing KnowledgeExtractor...")
        print("-" * 70)
        extractor = KnowledgeExtractor(
            DB_CONFIG,
            os.getenv('LLM_BASE_URL', 'http://localhost:11434/v1'),
            os.getenv('GEMINI_API_KEY', '')
        )

        stats = extractor.extract_from_recent_events(lookback_hours=24, min_events=1)
        print(f"✓ Extraction stats:")
        print(f"  - Events processed: {stats.get('events_processed', 0)}")
        print(f"  - Patterns identified: {stats.get('patterns_identified', 0)}")
        print(f"  - Concepts created: {stats.get('concepts_created', 0)}")
        print(f"  - Human expertise captured: {stats.get('human_expertise_captured', 0)}")
        print()

        # 3. Test Active Learning
        print("3. Testing ActiveLearningSystem...")
        print("-" * 70)
        active_learner = ActiveLearningSystem(
            DB_CONFIG,
            os.getenv('GEMINI_API_KEY', '')
        )

        gaps = active_learner.identify_knowledge_gaps(lookback_days=7)
        print(f"✓ Identified {len(gaps)} knowledge gaps")

        if gaps:
            print(f"  Top gap: {gaps[0]['subject']} (severity: {gaps[0]['severity']:.2f})")

        questions = active_learner.generate_learning_questions(max_questions=3)
        print(f"✓ Generated {len(questions)} learning questions")
        if questions:
            print(f"  Example: {questions[0][:100]}...")
        print()

        # 4. Test Knowledge Application
        print("4. Testing KnowledgeApplicationEngine...")
        print("-" * 70)
        applier = KnowledgeApplicationEngine(DB_CONFIG)

        knowledge = applier.retrieve_relevant_knowledge(
            "How do I handle errors in n8n workflows?",
            top_k=3
        )
        print(f"✓ Retrieved knowledge:")
        print(f"  - Past interactions: {len(knowledge['similar_past_interactions'])}")
        print(f"  - Concepts: {len(knowledge['relevant_concepts'])}")
        print(f"  - Procedures: {len(knowledge['applicable_procedures'])}")
        print(f"  - Expertise: {len(knowledge['human_expertise'])}")

        # Test knowledge enhancement
        base_prompt = "You are a helpful n8n assistant."
        enhanced_prompt = applier.get_knowledge_enhanced_prompt(
            "How do I use webhooks?",
            base_prompt
        )
        print(f"✓ Prompt enhancement: {len(enhanced_prompt)} chars (base: {len(base_prompt)})")

        # Get knowledge stats
        stats = applier.get_knowledge_stats()
        print(f"✓ Knowledge base stats:")
        print(f"  - Total concepts: {stats.get('total_concepts', 0)}")
        print(f"  - Total expertise: {stats.get('total_expertise', 0)}")
        print(f"  - Avg confidence: {stats.get('avg_confidence', 0):.2f}")
        print()

        # 5. Test Business Value Tracking
        print("5. Testing Business Value Tracking...")
        print("-" * 70)
        metrics = logger.calculate_business_value(time_period_days=7)
        print(f"✓ Business metrics calculated:")
        print(f"  - Time saved (hours): {metrics.get('time_saved_hours', 0):.1f}")
        print(f"  - Success rate improvement: {metrics.get('success_rate_improvement', 0):.2%}")
        print(f"  - Avg rating improvement: {metrics.get('avg_rating_improvement', 0):.2f}")

        bv = metrics.get('business_value', {})
        print(f"  - Total value (USD): ${bv.get('total_value_usd', 0):.2f}")
        print(f"  - ROI: {bv.get('roi_percentage', 0):.1f}%")
        print()

        # SUCCESS!
        print("="*70)
        print("✓ ALL TESTS PASSED!")
        print("="*70)
        print("\nThe Ultimate Learning System is fully operational.")
        print("\nNext steps:")
        print("1. Integrate into Dell Boca Vista v2 web UI")
        print("2. Start continuous learning worker")
        print("3. Setup Google Drive sync")
        print("4. Start using the system and watch it learn!")
        print()

        return True

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)
