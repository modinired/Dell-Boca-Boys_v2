# Orchestration Pipeline Overview

## Components

- **Task Planner (`app/orchestration/planner.py`)**
  - Deterministically converts natural-language goals into a chain of tasks and actions.
  - Uses semantic memory hits and heuristic enrichments (reporting, observability, ML readiness).

- **Execution Engine (`app/orchestration/execution.py`)**
  - Executes planner output by dispatching to existing n8n agent capabilities.
  - Captures structured action results for auditing and analytics.

- **Background Scheduler (`app/orchestration/scheduler.py`)**
  - Stores scheduled jobs in PostgreSQL, executes them in-process, and persists results.
  - Currently ships with a knowledge-base health check (hourly) and planner self-test (every 6h).

## Database Tables

The migration `scripts/migrations/20241105_async_queue_and_credentials.sql` introduces:

- `workflow_generation_jobs` (async queue metadata)
- `workflow_scheduler_jobs` and `workflow_scheduler_results`
- Additional columns on `credential_registry` and `documents`

Run the migration once per environment:

```bash
psql "$DATABASE_URL" -f scripts/migrations/20241105_async_queue_and_credentials.sql
```

## Worker & Scheduler

1. Launch Redis (default `redis://redis:6379/0`).
2. Start the FastAPI service; it initializes the Dramatiq broker and scheduler.
3. Start the worker alongside the API:
   ```bash
   dramatiq app.core.task_queue --processes 1 --threads 4 --path .
   ```
4. For production installs, a sample systemd unit is available at `docs/operations/dramatiq-worker.service.example`.

## Metrics

The new orchestration surfaces the following Prometheus series:

- `workflow_generation_seconds`
- `workflow_generation_failures_total{stage}`
- `task_queue_jobs{status}`
- `credential_resolution_total{alias,status}`
- `code_execution_seconds` / `_failures_total`

Scrape `GET /metrics` from the API to integrate with Prometheus/Grafana.


## LLM Configuration

- The router now prioritises the local OpenAI-compatible endpoint defined by `LLM_BASE_URL`.
  When the base URL points at `localhost` or `127.0.0.1`, the provider is registered with the highest
  priority and tagged for planning/pattern-analysis tasks.
- If `GEMINI_API_KEY` is present (and optionally `GEMINI_ENABLED=true`), the router automatically
  registers Google Gemini as a fallback provider using the `GEMINI_MODEL` name.
- Update `.env` accordingly, for example:
  ```env
  LLM_BASE_URL=http://127.0.0.1:8000/v1
  LLM_MODEL=Qwen/Qwen2.5-32B-Instruct
  GEMINI_API_KEY=your_gemini_key
  GEMINI_MODEL=gemini-2.0-flash-exp
  ```

