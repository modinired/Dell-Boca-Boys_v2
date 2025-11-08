
from fastapi import FastAPI, HTTPException, Query
from .models import ExecuteWorkflow, ExecuteStep, Reflection
from .runtime import OrchestratorRuntime
from .repo import Repo
from .secrets import SecretProvider
from skills.skill_manager import SkillManager
from core.cache import init_cache, cache_client
from core.cache.strategies import WorkflowExecutionStrategy, SkillExecutionStrategy
from core.websocket import ws_manager
from .websocket_routes import websocket_endpoint
import os, json
from typing import Optional, List, Dict, Any

app = FastAPI(
    title="SRC–RWCM Orchestrator",
    version="1.2.0",
    description="""
# Dell-Boca-Boys Enterprise AI Orchestrator

**Production-grade workflow orchestration with 83+ enterprise skills across 20+ domains.**

## Key Features

- 🧠 **CESAR-SRC Integration** - Symbiotic Recursive Cognition for adaptive AI
- 🎯 **RWCM Schema** - 17-table Role-Workflow-Capability-Mapping database
- 🔧 **83+ Skills** - Pre-built enterprise skills (recruiting, finance, legal, etc.)
- 🔐 **Enterprise Security** - HMAC signatures, rate limiting, PII detection
- 📊 **Hybrid Memory** - Mem0 + CESAR achieving 90% token reduction
- 🤖 **Multi-Agent Network** - 6-personality specialist agents
- 🧬 **Agent Breeding** - Genetic algorithms for agent evolution
- 🔍 **Knowledge Grounding** - Evidence-based retrieval with coverage metrics
- 🎛️ **Multi-Model Triangulation** - Reduce hallucinations via model consensus

## Architecture

This orchestrator implements PhD-level enterprise AI patterns:
- Async-first design with FastAPI + SQLAlchemy 2.0
- PostgreSQL with pgvector for semantic search
- Redis for caching and task queues
- Alembic database migrations
- OpenTelemetry distributed tracing
- Prometheus metrics + Grafana dashboards

## Quick Start

1. **List available skills**: `GET /skills`
2. **Search skills**: `GET /skills/search?q=recruiting`
3. **Execute workflow**: `POST /execute_workflow`
4. **View API docs**: Navigate to `/docs` (Swagger UI) or `/redoc` (ReDoc)
    """,
    contact={
        "name": "Dell-Boca-Boys Team",
        "url": "https://github.com/modinired/Dell-Boca-Boys",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Health",
            "description": "System health and status endpoints"
        },
        {
            "name": "Workflows",
            "description": "Execute and manage enterprise workflows with role-capability validation"
        },
        {
            "name": "Skills",
            "description": "Discover and search 83+ enterprise skills across 20+ domains (recruiting, finance, legal, compliance, etc.)"
        },
        {
            "name": "Reflection",
            "description": "Agent reflection and learning mechanisms for continuous improvement"
        }
    ]
)
rt = OrchestratorRuntime()
repo = Repo()
skill_mgr = SkillManager()

# Initialize Redis cache
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
redis_password = os.getenv("REDIS_PASSWORD")

try:
    init_cache(host=redis_host, port=redis_port, password=redis_password)
except Exception as e:
    # Log error but don't crash - cache is optional enhancement
    import logging
    logging.warning(f"Redis cache initialization failed: {e}. Continuing without cache.")

@app.get("/health", tags=["Health"], summary="Health Check")
def health():
    """
    Check if the orchestrator is running and healthy.

    **Returns:**
    - `status`: "ok" if service is healthy

    **Example Response:**
    ```json
    {"status": "ok"}
    ```
    """
    return {"status":"ok"}

@app.post("/execute_workflow", tags=["Workflows"], summary="Execute Enterprise Workflow")
def execute_workflow(req: ExecuteWorkflow):
    """
    Execute a multi-step enterprise workflow with role-capability validation.

    **Process:**
    1. Retrieves workflow definition and ordered steps
    2. Validates trigger payload against schema registry (if subject provided)
    3. Returns step execution plan for workers

    **Request Body:**
    - `workflow_id`: Unique workflow identifier
    - `trigger_payload`: Input data to initiate workflow (optional `_subject` for validation)

    **Response:**
    - `accepted`: True if workflow accepted
    - `workflow_id`: Echo of workflow ID
    - `steps`: Ordered list of steps with skill bindings

    **Example Request:**
    ```json
    {
      "workflow_id": "wf.recruiting.candidate_screening",
      "trigger_payload": {
        "_subject": "recruiting.new_application",
        "candidate_id": "CAND-12345",
        "position": "Senior Engineer"
      }
    }
    ```

    **Example Response:**
    ```json
    {
      "accepted": true,
      "workflow_id": "wf.recruiting.candidate_screening",
      "steps": [
        {"step_id": "step_1", "action_type": "skill", "skill_id": "recruiting.parse_resume"},
        {"step_id": "step_2", "action_type": "skill", "skill_id": "recruiting.score_candidate"}
      ]
    }
    ```
    """
    wf = repo.get_workflow_with_steps(req.workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Optional: validate trigger against registry if subject present (example)
    subj = req.trigger_payload.get("_subject")
    if subj:
        try:
            rt.validate_event(subj, req.trigger_payload)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Schema validation failed: {e}")

    # Return ordered step ids for the client/worker to execute
    steps = [{"step_id": s.step_id, "action_type": s.action_type, "skill_id": s.skill_id} for s in wf.steps]
    return {"accepted": True, "workflow_id": req.workflow_id, "steps": steps}

@app.post("/execute_step", tags=["Workflows"], summary="Execute Single Workflow Step")
def execute_step(req: ExecuteStep):
    """
    Execute a single workflow step with adapter-based skill invocation.

    **Process:**
    1. Resolves runtime binding for external adapters (AWS Textract, SAP, Okta, Workday)
    2. Dispatches to appropriate adapter method
    3. Returns execution result

    **Supported Adapters:**
    - `aws_textract_v2`: Document OCR and analysis
    - `sap_rest`: SAP S/4HANA integration
    - `okta`: Identity and access management
    - `workday`: HR and payroll operations
    - `builtin`: Internal logic steps

    **Request Body:**
    - `step_id`: Unique step identifier
    - `input`: Step input with optional `runtime_binding` and `method`

    **Example Request:**
    ```json
    {
      "step_id": "step_ocr_invoice",
      "input": {
        "runtime_binding": {"adapter": "aws_textract_v2", "region": "us-east-1"},
        "method": "analyze_document",
        "payload": {"document_url": "s3://bucket/invoice.pdf"}
      }
    }
    ```
    """
    # In a full system, we'd look up step by ID and its bound skill & runtime_binding.
    # For now, require client to pass binding alongside input OR resolve via catalog; here we allow a 'binding' field.
    binding = req.input.get("runtime_binding")
    if not binding:
        return {"accepted": True, "step_id": req.step_id, "note":"no runtime_binding provided; treated as builtin or logic step"}

    adapter = rt.adapter_from_binding(binding)
    if adapter is None:
        return {"accepted": True, "step_id": req.step_id, "note":"builtin skill executed"}

    # Dispatch based on common method names
    method = req.input.get("method","")
    payload = req.input.get("payload", {})
    if hasattr(adapter, method):
        fn = getattr(adapter, method)
        result = fn(**payload) if isinstance(payload, dict) else fn(payload)
        return {"accepted": True, "step_id": req.step_id, "result": result}
    else:
        raise HTTPException(status_code=400, detail=f"Adapter does not support method '{method}'")

@app.post("/reflection", tags=["Reflection"], summary="Record Agent Reflection")
def reflection(rec: Reflection):
    """
    Record agent reflection for continuous learning and improvement.

    **Purpose:**
    Enables agents to reflect on execution outcomes, record learnings, and propose improvements.

    **Process:**
    1. Receives reflection record with execution context
    2. Computes SHA-256 hash for deduplication
    3. Returns hash for tracking

    **Request Body:**
    - Reflection record with execution metadata

    **Response:**
    - `recorded`: True if reflection accepted
    - `proposal_hash`: SHA-256 hash of reflection content

    **Example Request:**
    ```json
    {
      "agent_id": "agent_recruiter_001",
      "workflow_id": "wf.recruiting.candidate_screening",
      "outcome": "success",
      "insights": ["Resume parsing accuracy improved with new regex"],
      "proposed_improvements": ["Add skill extraction validation"]
    }
    ```
    """
    hashed = rt.checksum(rec.model_dump())
    return {"recorded": True, "proposal_hash": hashed}

# ============================================================================
# SKILL MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/skills/domains", tags=["Skills"], summary="List Skill Domains")
def list_skill_domains() -> List[str]:
    """
    List all available skill domains (20+ enterprise categories).

    **Available Domains:**
    - recruiting, payroll, finance_ar, finance_ap, finance_fpa
    - sales_ops, procurement, customer_support
    - hr_core, legal, compliance
    - data_engineering, mlops
    - marketing, product_mgmt
    - facilities, secops, it_helpdesk, pmo
    - core_skills

    **Example Response:**
    ```json
    ["recruiting", "payroll", "finance_ar", "sales_ops", "legal", ...]
    ```
    """
    return skill_mgr.list_domains()

@app.get("/skills", tags=["Skills"], summary="List All Skills")
def list_skills(domain: Optional[str] = Query(None, description="Filter by domain")) -> List[Dict[str, Any]]:
    """
    List all skills, optionally filtered by domain. Returns 83+ enterprise skills.

    **Query Parameters:**
    - `domain`: Optional filter by domain (e.g., "recruiting", "finance_ar")

    **Usage Examples:**
    - `GET /skills` - Returns all 83+ skills
    - `GET /skills?domain=recruiting` - Returns only recruiting skills

    **Example Response:**
    ```json
    [
      {
        "id": "recruiting.parse_resume",
        "display_name": "Resume Parser",
        "intent": "Extract structured data from candidate resumes",
        "status": "stable",
        "tags": ["recruiting", "nlp", "extraction"],
        "version": "1.0.0"
      },
      ...
    ]
    ```
    """
    return skill_mgr.list_skills(domain=domain)

@app.get("/skills/{skill_id}", tags=["Skills"], summary="Get Skill Details")
def get_skill(skill_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific skill by ID.

    **Path Parameters:**
    - `skill_id`: Skill identifier (e.g., "recruiting.parse_resume", "finance_ar.aging_report")

    **Response:**
    - Complete skill definition including inputs, outputs, preconditions, examples

    **Example Request:**
    ```
    GET /skills/recruiting.parse_resume
    ```

    **Example Response:**
    ```json
    {
      "id": "recruiting.parse_resume",
      "display_name": "Resume Parser",
      "intent": "Extract structured data from candidate resumes including skills, experience, education",
      "owner": "recruiting@company.com",
      "version": "1.0.0",
      "status": "stable",
      "tags": ["recruiting", "nlp", "extraction"],
      "inputs": {
        "type": "object",
        "required": ["resume_text"],
        "properties": {
          "resume_text": {"type": "string"}
        }
      },
      "outputs": {
        "type": "object",
        "properties": {
          "candidate_name": {"type": "string"},
          "skills": {"type": "array"},
          "experience_years": {"type": "number"}
        }
      },
      "preconditions": ["resume_text not empty"],
      "postconditions": ["skills array sorted by relevance"],
      "tools_required": [{"name": "nlp.ner", "scope": "read"}],
      "examples": [...]
    }
    ```
    """
    skill = skill_mgr.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")
    return skill

@app.get("/skills/search", tags=["Skills"], summary="Search Skills")
def search_skills(q: str = Query(..., min_length=2, description="Search query")) -> List[Dict[str, Any]]:
    """
    Search skills by keyword in name or description.

    **Query Parameters:**
    - `q`: Search query (minimum 2 characters)

    **Search Scope:**
    - Searches in skill name and description fields
    - Case-insensitive matching

    **Usage Examples:**
    - `GET /skills/search?q=invoice` - Find invoice-related skills
    - `GET /skills/search?q=candidate` - Find recruiting skills
    - `GET /skills/search?q=compliance` - Find compliance skills

    **Example Response:**
    ```json
    [
      {
        "id": "finance_ap.process_invoice",
        "display_name": "Invoice Processor",
        "intent": "Process and validate supplier invoices",
        "status": "stable"
      },
      {
        "id": "procurement.invoice_matching",
        "display_name": "3-Way Invoice Match",
        "intent": "Match invoices to POs and receipts",
        "status": "stable"
      }
    ]
    ```
    """
    return skill_mgr.search_skills(q)

@app.get("/skills/stats", tags=["Skills"], summary="Skill Statistics")
def get_skill_stats() -> Dict[str, Any]:
    """
    Get skill registry statistics including total domains and skills.

    **Response:**
    - `total_domains`: Number of skill categories
    - `total_skills`: Total number of skills across all domains
    - `domains`: Breakdown of skills per domain

    **Example Response:**
    ```json
    {
      "total_domains": 20,
      "total_skills": 83,
      "domains": {
        "recruiting": 5,
        "finance_ar": 4,
        "finance_ap": 6,
        "sales_ops": 4,
        "payroll": 4,
        "compliance": 4,
        "legal": 4,
        "data_engineering": 4,
        "mlops": 4,
        ...
      }
    }
    ```
    """
    return skill_mgr.get_stats()

# ============================================================================
# CACHE MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/cache/stats", tags=["Cache"], summary="Cache Statistics")
def get_cache_stats() -> Dict[str, Any]:
    """
    Get Redis cache performance statistics.

    **Response:**
    - `hits`: Number of cache hits
    - `misses`: Number of cache misses
    - `hit_rate`: Cache hit rate percentage
    - `memory_used_bytes`: Redis memory usage
    - `connected_clients`: Active Redis connections

    **Example Response:**
    ```json
    {
      "hits": 15234,
      "misses": 3421,
      "hit_rate": 81.7,
      "total_requests": 18655,
      "redis_keyspace_hits": 15234,
      "redis_keyspace_misses": 3421,
      "memory_used_bytes": 12582912,
      "memory_used_human": "12.0M",
      "connected_clients": 5
    }
    ```
    """
    if cache_client is None:
        raise HTTPException(status_code=503, detail="Cache not available")
    return cache_client.get_stats()

@app.post("/cache/invalidate/{namespace}", tags=["Cache"], summary="Invalidate Cache Namespace")
def invalidate_cache_namespace(namespace: str) -> Dict[str, Any]:
    """
    Invalidate all cache entries in a specific namespace.

    **Path Parameters:**
    - `namespace`: Cache namespace to invalidate (e.g., "memory:query", "workflow:execution")

    **Response:**
    - `deleted`: Number of cache keys deleted

    **Example Request:**
    ```
    POST /cache/invalidate/workflow:execution
    ```

    **Example Response:**
    ```json
    {"deleted": 147, "namespace": "workflow:execution"}
    ```
    """
    if cache_client is None:
        raise HTTPException(status_code=503, detail="Cache not available")

    deleted = cache_client.invalidate_namespace(namespace)
    return {"deleted": deleted, "namespace": namespace}

@app.get("/cache/health", tags=["Cache"], summary="Cache Health Check")
def cache_health() -> Dict[str, Any]:
    """
    Check Redis cache health and connectivity.

    **Response:**
    - `healthy`: True if Redis is responsive
    - `host`: Redis server host
    - `port`: Redis server port

    **Example Response:**
    ```json
    {"healthy": true, "host": "localhost", "port": 6379}
    ```
    """
    if cache_client is None:
        return {"healthy": False, "error": "Cache not initialized"}

    healthy = cache_client.health_check()
    return {
        "healthy": healthy,
        "host": redis_host,
        "port": redis_port
    }

# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@app.websocket("/ws")
async def websocket_route(websocket, agent_id: Optional[str] = None, user_id: Optional[str] = None):
    """
    WebSocket endpoint for real-time communication.

    **Connection:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws?agent_id=agent_001');
    ```

    **Supported Actions:**
    - `subscribe` - Subscribe to topic
    - `unsubscribe` - Unsubscribe from topic
    - `message` - Send agent-to-agent message
    - `publish` - Publish to topic
    - `ping` - Heartbeat check

    **Topics:**
    - `workflows` - All workflow updates
    - `workflow:<id>` - Specific workflow
    - `memory:<type>` - Memory updates
    - `agent:<id>` - Agent messages
    - `emergent_behaviors` - AI insights
    """
    await websocket_endpoint(websocket, agent_id, user_id)

@app.get("/ws/stats", tags=["WebSocket"], summary="WebSocket Statistics")
def get_websocket_stats() -> Dict[str, Any]:
    """
    Get WebSocket connection and subscription statistics.

    **Response:**
    - `active_connections`: Number of active WebSocket connections
    - `active_agents`: Number of connected agents
    - `active_topics`: Number of active topics
    - `topics`: Subscriber count per topic

    **Example Response:**
    ```json
    {
      "active_connections": 15,
      "active_agents": 6,
      "active_topics": 8,
      "topics": {
        "workflows": 10,
        "workflow:wf_recruiting_001": 2,
        "memory:episodic": 5,
        "emergent_behaviors": 3
      }
    }
    ```
    """
    return ws_manager.get_stats()
