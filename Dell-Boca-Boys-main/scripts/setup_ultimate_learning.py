#!/usr/bin/env python3
"""
Ultimate Learning System - Database Setup Script
=================================================

Sets up the complete database schema for the Ultimate Symbiotic Recursive Learning System.

This script creates all tables, indexes, and extensions needed for:
- Episodic Memory (every interaction)
- Semantic Memory (learned concepts)
- Procedural Memory (how-to knowledge)
- Meta-Learning (reflections)
- Human Expertise (corrections)
- Knowledge Graphs (relationships)

Author: Dell Boca Vista Boys Technical Architecture Team
Version: 1.0.0

Usage:
    python scripts/setup_ultimate_learning.py
"""

import psycopg
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('PGHOST', 'localhost'),
    'port': int(os.getenv('PGPORT', 5432)),
    'dbname': os.getenv('PGDATABASE', 'n8n_agent_memory'),
    'user': os.getenv('PGUSER', 'n8n_agent'),
    'password': os.getenv('PGPASSWORD', '')
}

# SQL for complete schema
SCHEMA_SQL = """
-- ============================================================================
-- ENABLE EXTENSIONS
-- ============================================================================

-- pgvector for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- EPISODIC MEMORY: Every specific interaction
-- ============================================================================

CREATE TABLE IF NOT EXISTS episodic_events (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,

    -- Event classification
    event_type VARCHAR(50) NOT NULL,
    event_subtype VARCHAR(50),

    -- Content (multi-modal)
    text_content TEXT,
    code_content TEXT,
    code_language VARCHAR(50),
    document_content TEXT,
    document_metadata JSONB,
    audio_transcript TEXT,
    screen_capture_analysis TEXT,

    -- AI responses
    ollama_response TEXT,
    ollama_latency_ms REAL,
    gemini_response TEXT,
    gemini_latency_ms REAL,
    synthesized_response TEXT,
    chosen_model VARCHAR(50),

    -- Context
    conversation_history JSONB,
    active_workflow JSONB,
    user_intent VARCHAR(255),
    detected_entities JSONB,

    -- Outcomes
    success BOOLEAN,
    error_message TEXT,
    user_feedback TEXT,
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),

    -- Learning signals
    correction_applied TEXT,
    alternative_chosen TEXT,
    time_to_resolution_sec REAL,
    iterations_needed INTEGER,

    -- Embeddings for similarity search
    text_embedding vector(768),
    code_embedding vector(768),

    -- Metadata
    tags TEXT[],
    complexity_score REAL,
    business_value_score REAL,
    metadata JSONB,

    -- Constraints
    CONSTRAINT valid_event_type CHECK (event_type IN (
        'chat', 'workflow_generation', 'code_written', 'code_review',
        'document_shared', 'voice_interaction', 'screen_share',
        'debugging', 'refactoring', 'deployment', 'testing',
        'learning_query', 'feedback', 'correction'
    ))
);

-- Indexes for episodic_events
CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_episodic_user ON episodic_events(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_episodic_session ON episodic_events(session_id);
CREATE INDEX IF NOT EXISTS idx_episodic_type ON episodic_events(event_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_episodic_success ON episodic_events(success, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_episodic_rating ON episodic_events(user_rating DESC) WHERE user_rating IS NOT NULL;

-- Vector indexes (IMPORTANT: Run AFTER inserting some data for better performance)
-- These will be created after initial data is loaded
-- CREATE INDEX idx_episodic_text_embedding ON episodic_events
--     USING ivfflat (text_embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX idx_episodic_code_embedding ON episodic_events
--     USING ivfflat (code_embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================================
-- SEMANTIC MEMORY: Extracted knowledge, patterns, concepts
-- ============================================================================

CREATE TABLE IF NOT EXISTS semantic_concepts (
    id BIGSERIAL PRIMARY KEY,
    concept_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Concept identity
    concept_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    -- Source provenance
    extracted_from_events UUID[] NOT NULL,
    extraction_method VARCHAR(100) NOT NULL,
    confidence_score REAL NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),

    -- Concept content
    formal_representation JSONB,
    example_instances JSONB[],
    counter_examples JSONB[],

    -- Relationships to other concepts
    parent_concepts UUID[],
    child_concepts UUID[],
    related_concepts JSONB,
    prerequisites UUID[],

    -- Usage statistics
    times_retrieved INTEGER DEFAULT 0,
    times_applied_successfully INTEGER DEFAULT 0,
    times_applied_unsuccessfully INTEGER DEFAULT 0,
    avg_user_rating REAL,

    -- Temporal dynamics
    first_seen TIMESTAMPTZ NOT NULL,
    last_validated TIMESTAMPTZ,
    concept_stability_score REAL,

    -- Embedding for similarity
    concept_embedding vector(768),

    -- Business impact
    estimated_time_saved_minutes REAL,
    estimated_error_reduction_pct REAL,
    business_criticality INTEGER CHECK (business_criticality BETWEEN 1 AND 5),

    -- Metadata
    tags TEXT[],
    domain VARCHAR(100),
    complexity_level VARCHAR(20) CHECK (complexity_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    metadata JSONB
);

-- Indexes for semantic_concepts
CREATE INDEX IF NOT EXISTS idx_semantic_type ON semantic_concepts(concept_type);
CREATE INDEX IF NOT EXISTS idx_semantic_domain ON semantic_concepts(domain);
CREATE INDEX IF NOT EXISTS idx_semantic_updated ON semantic_concepts(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_semantic_confidence ON semantic_concepts(confidence_score DESC);

-- Vector index (create after data loaded)
-- CREATE INDEX idx_semantic_embedding ON semantic_concepts
--     USING ivfflat (concept_embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================================
-- PROCEDURAL MEMORY: How to do things (workflows, processes)
-- ============================================================================

CREATE TABLE IF NOT EXISTS procedural_knowledge (
    id BIGSERIAL PRIMARY KEY,
    procedure_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Procedure identity
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    goal TEXT NOT NULL,

    -- Procedure definition
    steps JSONB NOT NULL,
    decision_points JSONB,
    error_handling JSONB,
    success_criteria JSONB,

    -- Learning history
    learned_from_events UUID[] NOT NULL,
    times_executed INTEGER DEFAULT 0,
    success_rate REAL,
    avg_execution_time_sec REAL,

    -- Improvement tracking
    version INTEGER DEFAULT 1,
    previous_version UUID,
    improvements_over_previous TEXT,

    -- Context applicability
    prerequisites TEXT[],
    applicable_when JSONB,
    not_applicable_when JSONB,

    -- Human expertise
    expert_tips JSONB,
    common_mistakes JSONB,
    troubleshooting_guide JSONB,

    -- Metadata
    domain VARCHAR(100),
    tags TEXT[],
    embedding vector(768)
);

-- Indexes for procedural_knowledge
CREATE INDEX IF NOT EXISTS idx_procedural_domain ON procedural_knowledge(domain);
CREATE INDEX IF NOT EXISTS idx_procedural_success ON procedural_knowledge(success_rate DESC);

-- ============================================================================
-- META-LEARNING: How the system learns
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_reflections (
    id BIGSERIAL PRIMARY KEY,
    reflection_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Reflection scope
    time_period_start TIMESTAMPTZ NOT NULL,
    time_period_end TIMESTAMPTZ NOT NULL,
    event_count INTEGER NOT NULL,

    -- What was learned
    new_concepts_discovered INTEGER,
    concepts_refined INTEGER,
    procedures_learned INTEGER,
    patterns_identified JSONB,

    -- Learning quality
    knowledge_conflicts_found INTEGER,
    conflicts_resolved INTEGER,
    uncertainty_areas JSONB,

    -- Improvement metrics
    response_quality_improvement_pct REAL,
    user_satisfaction_improvement_pct REAL,
    error_rate_change_pct REAL,

    -- Strategic insights
    high_value_knowledge_gaps JSONB,
    recommended_learning_focuses TEXT[],
    suggested_experiments JSONB,

    -- Generated by
    reflection_method VARCHAR(100),
    llm_model_used VARCHAR(100),

    -- Full reflection text
    reflection_text TEXT NOT NULL,

    -- Metadata
    metadata JSONB
);

-- Indexes for learning_reflections
CREATE INDEX IF NOT EXISTS idx_reflections_period ON learning_reflections(time_period_end DESC);

-- ============================================================================
-- HUMAN EXPERTISE CAPTURE
-- ============================================================================

CREATE TABLE IF NOT EXISTS human_expertise (
    id BIGSERIAL PRIMARY KEY,
    expertise_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Source
    user_id VARCHAR(255) NOT NULL,
    capture_method VARCHAR(100),
    source_event_id UUID,

    -- Expertise content
    expertise_type VARCHAR(50) NOT NULL,
    subject_area VARCHAR(255) NOT NULL,
    expertise_text TEXT NOT NULL,
    formalized_rule JSONB,

    -- Context
    situation_when_applicable JSONB,
    exceptions JSONB,

    -- Validation
    times_confirmed INTEGER DEFAULT 1,
    times_contradicted INTEGER DEFAULT 0,
    confidence REAL DEFAULT 0.5,

    -- Integration status
    integrated_into_concepts UUID[],
    integrated_into_procedures UUID[],

    -- Metadata
    tags TEXT[],
    embedding vector(768)
);

-- Indexes for human_expertise
CREATE INDEX IF NOT EXISTS idx_expertise_user ON human_expertise(user_id);
CREATE INDEX IF NOT EXISTS idx_expertise_type ON human_expertise(expertise_type);
CREATE INDEX IF NOT EXISTS idx_expertise_confidence ON human_expertise(confidence DESC);

-- ============================================================================
-- CROSS-MODAL RELATIONSHIPS
-- ============================================================================

CREATE TABLE IF NOT EXISTS knowledge_graph_edges (
    id BIGSERIAL PRIMARY KEY,
    edge_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Edge definition
    source_type VARCHAR(50) NOT NULL,
    source_id UUID NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id UUID NOT NULL,

    -- Relationship
    relationship_type VARCHAR(100) NOT NULL,
    relationship_strength REAL CHECK (relationship_strength BETWEEN 0 AND 1),

    -- Evidence
    evidence_events UUID[],
    confidence REAL NOT NULL,

    -- Temporal
    first_observed TIMESTAMPTZ NOT NULL,
    last_confirmed TIMESTAMPTZ,
    times_observed INTEGER DEFAULT 1,

    -- Metadata
    metadata JSONB,

    CONSTRAINT valid_source CHECK (source_type IN ('episodic_event', 'semantic_concept', 'procedural_knowledge', 'human_expertise')),
    CONSTRAINT valid_target CHECK (target_type IN ('episodic_event', 'semantic_concept', 'procedural_knowledge', 'human_expertise'))
);

-- Indexes for knowledge_graph_edges
CREATE INDEX IF NOT EXISTS idx_kg_source ON knowledge_graph_edges(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_kg_target ON knowledge_graph_edges(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_kg_relationship ON knowledge_graph_edges(relationship_type);
CREATE INDEX IF NOT EXISTS idx_kg_strength ON knowledge_graph_edges(relationship_strength DESC);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for semantic_concepts
DROP TRIGGER IF EXISTS update_semantic_concepts_updated_at ON semantic_concepts;
CREATE TRIGGER update_semantic_concepts_updated_at
    BEFORE UPDATE ON semantic_concepts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for procedural_knowledge
DROP TRIGGER IF EXISTS update_procedural_knowledge_updated_at ON procedural_knowledge;
CREATE TRIGGER update_procedural_knowledge_updated_at
    BEFORE UPDATE ON procedural_knowledge
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SUMMARY
-- ============================================================================

-- Tables created:
-- 1. episodic_events - Every interaction captured
-- 2. semantic_concepts - Learned patterns and knowledge
-- 3. procedural_knowledge - How-to procedures
-- 4. learning_reflections - Meta-learning insights
-- 5. human_expertise - Captured corrections and preferences
-- 6. knowledge_graph_edges - Cross-modal relationships

-- Vector indexes should be created AFTER loading initial data for better performance

"""


def main():
    """Main setup function."""
    print("="*70)
    print("Ultimate Symbiotic Recursive Learning System - Database Setup")
    print("="*70)
    print()

    # Validate configuration
    print("Database Configuration:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['dbname']}")
    print(f"  User: {DB_CONFIG['user']}")
    print()

    # Confirm
    response = input("Proceed with database setup? (yes/no): ").lower()
    if response != 'yes':
        print("Setup cancelled.")
        sys.exit(0)

    try:
        # Connect to database
        print("\nConnecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Execute schema
        print("Creating schema...")
        cursor.execute(SCHEMA_SQL)

        # Commit
        conn.commit()
        print("✓ Schema created successfully!")

        # Verify tables
        print("\nVerifying tables...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN (
                'episodic_events',
                'semantic_concepts',
                'procedural_knowledge',
                'learning_reflections',
                'human_expertise',
                'knowledge_graph_edges'
            )
            ORDER BY table_name
        """)

        tables = cursor.fetchall()
        print(f"✓ Created {len(tables)} tables:")
        for (table_name,) in tables:
            print(f"  - {table_name}")

        # Get table sizes
        print("\nTable statistics:")
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count} rows")

        conn.close()

        print("\n" + "="*70)
        print("✓ Database setup complete!")
        print("="*70)
        print()
        print("Next steps:")
        print("1. Start using the learning system in your application")
        print("2. After inserting ~1000 events, create vector indexes:")
        print("   python scripts/create_vector_indexes.py")
        print("3. Schedule daily knowledge extraction:")
        print("   python scripts/continuous_learning_worker.py &")
        print()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
