-- Migration: async workflow queue, credential encryption, memory freshness
-- Run against the existing n8n_agent database prior to deploying the new release.

BEGIN;

-- 1. Credential registry enhancements --------------------------------------------------
ALTER TABLE credential_registry
    ADD COLUMN IF NOT EXISTS secret_ciphertext BYTEA,
    ADD COLUMN IF NOT EXISTS encryption_salt BYTEA,
    ADD COLUMN IF NOT EXISTS valid_from TIMESTAMPTZ DEFAULT now(),
    ADD COLUMN IF NOT EXISTS valid_until TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS scope TEXT,
    ADD COLUMN IF NOT EXISTS normalized_scope TEXT GENERATED ALWAYS AS (COALESCE(scope, '__global__')) STORED,
    ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMPTZ;

UPDATE credential_registry
SET secret_ciphertext = secret_ciphertext
WHERE secret_ciphertext IS NULL;

ALTER TABLE credential_registry
    ALTER COLUMN secret_ciphertext SET NOT NULL,
    ALTER COLUMN encryption_salt SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_credentials_scope ON credential_registry(normalized_scope);
CREATE INDEX IF NOT EXISTS idx_credentials_validity ON credential_registry(valid_until);

ALTER TABLE credential_registry
    ADD CONSTRAINT credential_alias_scope_unique
        UNIQUE (credential_name, normalized_scope);

-- 2. Documents table freshness metadata -------------------------------------------------
ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS fingerprint TEXT,
    ADD COLUMN IF NOT EXISTS content_hash TEXT,
    ADD COLUMN IF NOT EXISTS freshness_score REAL DEFAULT 1.0,
    ADD COLUMN IF NOT EXISTS last_ingested_at TIMESTAMPTZ DEFAULT now();

UPDATE documents
SET fingerprint = COALESCE(fingerprint, md5(lower(regexp_replace(content, '\s+', ' ', 'g')))),
    content_hash = COALESCE(content_hash, md5(content)),
    freshness_score = COALESCE(freshness_score, 1.0),
    last_ingested_at = COALESCE(last_ingested_at, updated_at);

CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_fingerprint ON documents(fingerprint);
CREATE INDEX IF NOT EXISTS idx_documents_last_ingested ON documents(last_ingested_at DESC);

-- 3. Workflow generation job tracking ----------------------------------------------------
CREATE TABLE IF NOT EXISTS workflow_generation_jobs (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status TEXT NOT NULL CHECK (status IN ('queued','running','succeeded','failed')),
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

-- trigger to keep updated_at fresh
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_workflow_jobs_updated_at ON workflow_generation_jobs;
CREATE TRIGGER update_workflow_jobs_updated_at
    BEFORE UPDATE ON workflow_generation_jobs
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 4. Scheduler metadata -------------------------------------------------------
CREATE TABLE IF NOT EXISTS workflow_scheduler_jobs (
    job_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    interval_seconds INTEGER NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workflow_scheduler_results (
    id BIGSERIAL PRIMARY KEY,
    job_id TEXT REFERENCES workflow_scheduler_jobs(job_id) ON DELETE CASCADE,
    executed_at TIMESTAMPTZ NOT NULL,
    success BOOLEAN NOT NULL,
    duration_seconds DOUBLE PRECISION NOT NULL,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scheduler_results_job ON workflow_scheduler_results(job_id);

COMMIT;
