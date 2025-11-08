-- =============================================================================
-- n8n Autonomous Agent - PostgreSQL Schema Initialization
-- =============================================================================
--
-- This script initializes the database with:
-- 1. pgvector extension for semantic search
-- 2. Documents table for storing knowledge
-- 3. Embeddings table for vector storage
-- 4. Workflows table for tracking generated workflows
-- 5. Executions table for workflow execution logs
-- 6. Audit log table for security events
-- 7. Necessary indexes for performance
--
-- =============================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- Documents Table
-- =============================================================================
-- Stores all knowledge base documents (templates, docs, transcripts)
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL CHECK (source IN (
        'templates',
        'docs',
        'youtube',
        'patterns',
        'manual',
        'custom'
    )),
    url TEXT,
    title TEXT,
    content TEXT NOT NULL,
    meta JSONB NOT NULL DEFAULT '{}',
    fingerprint TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    freshness_score REAL NOT NULL DEFAULT 1.0,
    last_ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for source filtering
CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source);

-- Fingerprint index to prevent duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_fingerprint ON documents(fingerprint);

-- Index for full-text search on content
CREATE INDEX IF NOT EXISTS idx_documents_content_fts ON documents USING GIN (to_tsvector('english', content));

-- Index for metadata queries
CREATE INDEX IF NOT EXISTS idx_documents_meta ON documents USING GIN (meta);

-- Index for temporal queries
CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_last_ingested ON documents(last_ingested_at DESC);

-- =============================================================================
-- Embeddings Table
-- =============================================================================
-- Stores vector embeddings for semantic search
-- Default dimension: 768 (BAAI/bge-small-en-v1.5)
-- Adjust if using different embedding model
CREATE TABLE IF NOT EXISTS embeddings (
    id BIGSERIAL PRIMARY KEY,
    doc_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (doc_id, chunk_index)
);

-- HNSW index for fast approximate nearest neighbor search
-- Using inner product (IP) for normalized vectors (equivalent to cosine similarity)
CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw ON embeddings 
    USING hnsw (embedding vector_ip_ops)
    WITH (m = 16, ef_construction = 64);

-- Index for document lookup
CREATE INDEX IF NOT EXISTS idx_embeddings_doc_id ON embeddings(doc_id);

-- =============================================================================
-- Workflows Table
-- =============================================================================
-- Tracks generated workflows
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    user_goal TEXT NOT NULL,
    workflow_json JSONB NOT NULL,
    n8n_workflow_id TEXT,
    status TEXT NOT NULL DEFAULT 'created' CHECK (status IN (
        'created',
        'validated',
        'staged',
        'active',
        'failed',
        'archived'
    )),
    validation_errors JSONB DEFAULT '[]',
    best_practices_score REAL,
    test_results JSONB,
    provenance JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    staged_at TIMESTAMPTZ,
    activated_at TIMESTAMPTZ,
    created_by TEXT DEFAULT 'system'
);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);

-- Index for temporal queries
CREATE INDEX IF NOT EXISTS idx_workflows_created ON workflows(created_at DESC);

-- Index for n8n workflow ID lookup
CREATE INDEX IF NOT EXISTS idx_workflows_n8n_id ON workflows(n8n_workflow_id) WHERE n8n_workflow_id IS NOT NULL;

-- Index for user goal search
CREATE INDEX IF NOT EXISTS idx_workflows_goal_fts ON workflows USING GIN (to_tsvector('english', user_goal));

-- =============================================================================
-- Executions Table
-- =============================================================================
-- Logs workflow execution attempts and results
CREATE TABLE IF NOT EXISTS executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    n8n_execution_id TEXT,
    status TEXT NOT NULL CHECK (status IN (
        'running',
        'success',
        'error',
        'waiting',
        'canceled'
    )),
    mode TEXT NOT NULL CHECK (mode IN (
        'test',
        'staging',
        'production'
    )),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    error_message TEXT,
    execution_data JSONB,
    test_payload JSONB
);

-- Index for workflow lookup
CREATE INDEX IF NOT EXISTS idx_executions_workflow ON executions(workflow_id);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);

-- Index for temporal queries
CREATE INDEX IF NOT EXISTS idx_executions_started ON executions(started_at DESC);

-- Index for n8n execution ID lookup
CREATE INDEX IF NOT EXISTS idx_executions_n8n_id ON executions(n8n_execution_id) WHERE n8n_execution_id IS NOT NULL;

-- =============================================================================
-- Workflow Generation Jobs Table
-- =============================================================================
-- Tracks asynchronous workflow generation requests
CREATE TABLE IF NOT EXISTS workflow_generation_jobs (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status TEXT NOT NULL CHECK (status IN (
        'queued',
        'running',
        'succeeded',
        'failed'
    )),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    workflow_id UUID REFERENCES workflows(id) ON DELETE SET NULL,
    failure_reason TEXT,
    request_payload JSONB NOT NULL,
    result_snapshot JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_workflow_jobs_status ON workflow_generation_jobs(status);
CREATE INDEX IF NOT EXISTS idx_workflow_jobs_submitted ON workflow_generation_jobs(submitted_at DESC);

-- =============================================================================
-- Audit Log Table
-- =============================================================================
-- Security and compliance audit trail
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    event_category TEXT NOT NULL CHECK (event_category IN (
        'workflow_creation',
        'workflow_staging',
        'workflow_activation',
        'credential_access',
        'validation_failure',
        'security',
        'system'
    )),
    workflow_id UUID REFERENCES workflows(id) ON DELETE SET NULL,
    user_id TEXT,
    details JSONB NOT NULL DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for event type filtering
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_log(event_type);

-- Index for category filtering
CREATE INDEX IF NOT EXISTS idx_audit_category ON audit_log(event_category);

-- Index for temporal queries
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at DESC);

-- Index for workflow correlation
CREATE INDEX IF NOT EXISTS idx_audit_workflow ON audit_log(workflow_id) WHERE workflow_id IS NOT NULL;

-- =============================================================================
-- Credentials Registry Table
-- =============================================================================
-- Tracks credential aliases used in workflows
CREATE TABLE IF NOT EXISTS credential_registry (
    id BIGSERIAL PRIMARY KEY,
    credential_name TEXT NOT NULL,
    credential_type TEXT NOT NULL,
    n8n_credential_id TEXT,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    secret_ciphertext BYTEA NOT NULL,
    encryption_salt BYTEA NOT NULL,
    valid_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_until TIMESTAMPTZ,
    scope TEXT,
    normalized_scope TEXT GENERATED ALWAYS AS (COALESCE(scope, '__global__')) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_verified_at TIMESTAMPTZ,
    CONSTRAINT credential_alias_scope_unique UNIQUE (credential_name, normalized_scope)
);

-- Index for active credentials
CREATE INDEX IF NOT EXISTS idx_credentials_active ON credential_registry(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_credentials_scope ON credential_registry(normalized_scope);
CREATE INDEX IF NOT EXISTS idx_credentials_validity ON credential_registry(valid_until);

-- =============================================================================
-- Pattern Library Table
-- =============================================================================
-- Stores extracted n8n best practices and patterns
CREATE TABLE IF NOT EXISTS pattern_library (
    id BIGSERIAL PRIMARY KEY,
    pattern_name TEXT NOT NULL,
    pattern_type TEXT NOT NULL CHECK (pattern_type IN (
        'error_handling',
        'retry_logic',
        'data_transformation',
        'integration',
        'security',
        'performance',
        'general'
    )),
    description TEXT NOT NULL,
    example_json JSONB,
    source_documents JSONB DEFAULT '[]',
    usage_count INTEGER NOT NULL DEFAULT 0,
    confidence_score REAL NOT NULL DEFAULT 0.5 CHECK (confidence_score BETWEEN 0 AND 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for pattern type filtering
CREATE INDEX IF NOT EXISTS idx_patterns_type ON pattern_library(pattern_type);

-- Index for confidence scoring
CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON pattern_library(confidence_score DESC);

-- Index for usage statistics
CREATE INDEX IF NOT EXISTS idx_patterns_usage ON pattern_library(usage_count DESC);

-- =============================================================================
-- Views
-- =============================================================================

-- View for workflow statistics
CREATE OR REPLACE VIEW agent_workflow_statistics AS
SELECT 
    status,
    COUNT(*) as count,
    AVG(best_practices_score) as avg_score,
    MIN(created_at) as first_created,
    MAX(created_at) as last_created
FROM workflows
GROUP BY status;

-- View for execution statistics
CREATE OR REPLACE VIEW execution_statistics AS
SELECT 
    w.id as workflow_id,
    w.name as workflow_name,
    COUNT(e.id) as total_executions,
    SUM(CASE WHEN e.status = 'success' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN e.status = 'error' THEN 1 ELSE 0 END) as failed,
    AVG(EXTRACT(EPOCH FROM (e.finished_at - e.started_at))) as avg_duration_seconds
FROM workflows w
LEFT JOIN executions e ON w.id = e.workflow_id
GROUP BY w.id, w.name;

-- View for recent audit events
CREATE OR REPLACE VIEW recent_audit_events AS
SELECT 
    event_type,
    event_category,
    workflow_id,
    user_id,
    details,
    created_at
FROM audit_log
ORDER BY created_at DESC
LIMIT 100;

-- =============================================================================
-- Functions
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_credentials_updated_at BEFORE UPDATE ON credential_registry
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patterns_updated_at BEFORE UPDATE ON pattern_library
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_jobs_updated_at BEFORE UPDATE ON workflow_generation_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to log audit events
CREATE OR REPLACE FUNCTION log_audit_event(
    p_event_type TEXT,
    p_event_category TEXT,
    p_workflow_id UUID DEFAULT NULL,
    p_user_id TEXT DEFAULT NULL,
    p_details JSONB DEFAULT '{}'::jsonb
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO audit_log (event_type, event_category, workflow_id, user_id, details)
    VALUES (p_event_type, p_event_category, p_workflow_id, p_user_id, p_details);
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Initial Data
-- =============================================================================

-- Insert default patterns (will be enriched by the agent)
INSERT INTO pattern_library (pattern_name, pattern_type, description, confidence_score) VALUES
    ('Error Handler Workflow', 'error_handling', 'Separate workflow triggered by Error Trigger node', 0.9),
    ('HTTP Retry with Backoff', 'retry_logic', 'HTTP Request node with maxRetries and exponential backoff', 0.95),
    ('Loop Termination', 'general', 'Split in Batches with explicit batchSize and completion handling', 0.85),
    ('Credential Aliases', 'security', 'All credentials referenced via aliases, never raw values', 1.0),
    ('Data Validation', 'data_transformation', 'IF node to validate required fields before processing', 0.8)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Permissions (adjust as needed)
-- =============================================================================

-- Grant appropriate permissions to the application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- =============================================================================
-- Maintenance
-- =============================================================================

-- Analyze tables for query optimization
ANALYZE documents;
ANALYZE embeddings;
ANALYZE workflows;
ANALYZE executions;
ANALYZE audit_log;
ANALYZE credential_registry;
ANALYZE pattern_library;

-- Success message
DO $$ 
BEGIN
    RAISE NOTICE 'Database initialization complete!';
    RAISE NOTICE 'Tables created: documents, embeddings, workflows, executions, audit_log, credential_registry, pattern_library';
    RAISE NOTICE 'Indexes optimized for semantic search and temporal queries';
    RAISE NOTICE 'Ready for n8n agent operations';
END $$;
