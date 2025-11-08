# n8n Workflow Autonomous Agent System
## Production-Ready, PhD-Quality Implementation

A complete autonomous AI agent system that creates world-class n8n workflows by combining deep platform knowledge, intelligent crawling, semantic memory, multi-agent orchestration, rigorous validation, and **AI-powered code generation**.

**Key Principles:**
- Zero placeholders or simulations
- Production-ready code throughout
- PhD-level attention to detail
- Deterministic, reproducible outputs
- Enterprise-grade error handling
- Complete observability

**NEW in v1.1.0:**
- 🚀 AI-powered code generation for n8n Code nodes
- 🔒 Sandboxed code execution with security validation
- 🎯 Multi-model LLM routing with automatic failover
- 📊 Comprehensive health monitoring system
- ⚡ Intelligent code optimization suggestions

---

## System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│                   (FastAPI REST API)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │   Face Agent          │
         │  (Chiccki Cammarano)  │
         │  - Query routing      │
         │  - Crew coordination  │
         └───────────┬───────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼─────┐  ┌─────▼─────┐  ┌─────▼──────┐
│Knowledge │  │Specialist │  │ Execution  │
│  Layer   │  │  Agents   │  │   Layer    │
└──────────┘  └───────────┘  └────────────┘
     │               │               │
┌────▼─────┐  ┌─────▼─────┐  ┌─────▼──────┐
│pgvector  │  │  Crawler  │  │ Validator  │
│ Memory   │  │  Pattern  │  │ Simulator  │
│          │  │  Planner  │  │  Deploy    │
└──────────┘  └───────────┘  └────────────┘
```

### Agent Crew Specializations

1. **Crawler Agent**: Systematically gathers n8n workflow templates, documentation, and YouTube transcripts
2. **Pattern Analyst**: Extracts best practices, anti-patterns, and architectural insights from n8n manual
3. **Flow Planner**: Designs robust workflow architectures following n8n best practices
4. **JSON Compiler**: Generates schema-valid n8n workflow JSON with complete metadata
5. **QA Fighter**: Validates against strict schemas and simulates execution
6. **Deploy Capo**: Stages workflows in n8n with safety checks before activation
7. **Code Generator** (NEW): Generates production-ready Python/JavaScript code for n8n Code nodes with automated testing

---

## Technology Stack

### Core Infrastructure
- **Python 3.11+**: Main application language
- **FastAPI 0.115+**: REST API framework with async support
- **PostgreSQL 16 + pgvector 0.2.5**: Vector similarity search and persistence
- **Redis 7+**: Queue system for worker mode scaling
- **Docker Compose**: Multi-container orchestration

### AI/ML Components
- **vLLM**: High-performance LLM serving with OpenAI-compatible API
- **Qwen/Qwen2.5-30B-Instruct-AWQ**: Primary reasoning model (30B parameters, AWQ quantized)
- **smolagents 0.2.2**: Agent framework for tool orchestration
- **sentence-transformers 3.2.1**: Embedding generation (BAAI/bge-small-en-v1.5)

### Data Processing
- **trafilatura 1.9**: Content extraction from HTML
- **BeautifulSoup4 4.12**: HTML parsing and navigation
- **youtube-transcript-api 0.6.2**: Transcript extraction
- **pandas 2.2.3**: Data manipulation

### Validation & Integration
- **jsonschema 4.23**: Strict schema validation
- **requests 2.32**: HTTP client for API interaction
- **tenacity 9.0**: Retry logic with exponential backoff
- **psycopg 3.2 + pgvector**: PostgreSQL driver with vector support
- **google-api-python-client (optional)**: Enable Google Drive ingestion via `pip install .[ingestion]`

---

## Quick Start

### Prerequisites

1. **Docker & Docker Compose** (v2.0+)
2. **NVIDIA GPU** with CUDA support (for vLLM) OR CPU-only mode with Ollama
3. **8GB+ RAM** minimum (16GB+ recommended)
4. **50GB+ disk space** for models and data

### Installation

```bash
# 1. Clone/extract the codebase
cd n8n-agent

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your settings
nano .env
# CRITICAL: Set N8N_API_TOKEN with a personal access token from your n8n instance

# 4. Build all services
docker compose build --no-cache

# 5. Start the system
docker compose up -d

# 6. Verify all services are running
docker compose ps

# 7. Check logs
docker compose logs -f api
```

### First Run - Knowledge Initialization

```bash
# Initialize database and load n8n knowledge
docker compose exec api python scripts/load_embeddings.py

# Crawl n8n template gallery (first 50 workflows)
docker compose exec api python scripts/crawl_templates.py --max-pages 50

# Crawl n8n documentation
docker compose exec api python scripts/crawl_docs.py

# Optional: Load YouTube transcripts
docker compose exec api python scripts/fetch_youtube_transcripts.py VIDEO_ID

# Optional: Pull knowledge from GitHub or local libraries
docker compose exec api python scripts/ingest_resources.py github n8n-io/n8n --max-files 50

# Nightly (cron) example for summaries & ingestion
# 0 2 * * * docker compose exec api python scripts/generate_daily_summary.py --period daily --force
# 30 2 * * * docker compose exec api python scripts/ingest_resources.py github n8n-io/n8n --max-files 100
```

### Your First Workflow Request

```bash
curl -X POST http://localhost:8080/api/v1/workflow/design \
  -H 'Content-Type: application/json' \
  -d '{
    "user_goal": "Create a workflow that monitors a webhook for incoming orders, validates the order data, enriches it with customer information from a PostgreSQL database, calculates shipping costs via an external API, and sends a confirmation email. Include proper error handling for API failures with exponential backoff retry logic.",
    "options": {
      "include_tests": true,
      "auto_stage": false
    }
  }' | jq .

# Optional: ask for the Terry persona
curl -X POST http://localhost:8080/api/v1/workflow/design \
  -H 'Content-Type: application/json' \
  -d '{
    "user_goal": "Draft a workflow that watches a sales inbox, pushes leads into HubSpot, and pings the team in Slack when the lead score is high.",
    "persona": "terry"
  }' | jq .

# Interactive CLI (after sourcing your shell config)
Chiccki
# /help for commands, /persona formal, /output qa, /knowledge lead scoring, /summary weekly, /rebuild <id>

# Daily journal summaries
curl -X POST http://localhost:8080/api/v1/journal/generate \
  -H 'Content-Type: application/json' \
  -d '{ "period": "daily", "force": true }' | jq .
```

---

## API Endpoints

### Core Workflow Design

**POST** `/api/v1/workflow/design`
```json
{
  "user_goal": "string (required) - Natural language description of the workflow",
  "options": {
    "include_tests": "boolean - Generate test payloads (default: true)",
    "auto_stage": "boolean - Automatically stage in n8n (default: false)",
    "require_approval": "boolean - Require manual approval before staging (default: true)"
  }
}
```

**Response:**
```json
{
  "workflow_id": "uuid",
  "workflow": { /* Complete n8n JSON */ },
  "validation": {
    "schema_valid": true,
    "best_practices_score": 0.95,
    "issues": []
  },
  "test_results": { /* Simulation results */ },
  "staging_info": { /* n8n staging details if auto_stage=true */ },
  "provenance": [
    "https://n8n.io/workflows/1234",
    "n8n docs: Error Handling"
  ]
}
```

### Knowledge Management

**POST** `/api/v1/knowledge/ingest`
- Ingest custom documentation or templates

**GET** `/api/v1/knowledge/search?q={query}&k={results}`
- Search the vector knowledge base

**POST** `/api/v1/knowledge/crawl`
- Trigger on-demand crawling

### Reflection & Journaling

**POST** `/api/v1/journal/generate`
- Build or refresh a daily/weekly/monthly summary (with reflective thought)

**GET** `/api/v1/journal/summaries?limit=7`
- Fetch the most recent stored summaries for dashboards or reviews

### Deployment Operations

**POST** `/api/v1/deployment/stage`
- Stage a workflow in n8n (inactive)

**POST** `/api/v1/deployment/activate/{workflow_id}`
- Activate a staged workflow

**GET** `/api/v1/deployment/status/{workflow_id}`
- Check deployment status

---

## Configuration

### Environment Variables

See `.env.example` for complete configuration. Key variables:

#### Database
```bash
PGHOST=localhost
PGPORT=5432
PGUSER=n8n_agent
PGPASSWORD=<secure_password>
PGDATABASE=n8n_agent_memory
```

#### LLM Configuration
```bash
LLM_BASE_URL=http://localhost:8000/v1
LLM_API_KEY=not_used_but_required
LLM_MODEL=Qwen/Qwen2.5-30B-Instruct-AWQ
LLM_MAX_TOKENS=4096
LLM_TEMPERATURE=0.1  # Low for deterministic output
```

#### n8n Integration
```bash
N8N_BASE_URL=http://localhost:5678
N8N_API_TOKEN=<your_n8n_personal_access_token>
N8N_WEBHOOK_BASE_URL=http://localhost:5678/webhook
```

#### Embedding Model
```bash
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIM=768
EMBEDDING_DEVICE=cpu  # or 'cuda' if GPU available
```

#### Crawler Settings
```bash
CRAWL_RATE_LIMIT_PER_SEC=0.5
CRAWL_MAX_RETRIES=3
CRAWL_TIMEOUT_SEC=30
USER_AGENT=n8nAutonomousAgent/1.0 (+https://yoursite.com; research)
```

---

## n8n Workflow Schema

### Complete Schema Enforcement

The system validates ALL workflows against a comprehensive schema that includes:

1. **Required Top-Level Fields:**
   - `name` (string): Workflow name
   - `nodes` (array): List of node definitions
   - `connections` (object): Node interconnections
   - `settings` (object): Workflow-level settings
   - `staticData` (object): Persistent data storage

2. **Node Schema (every node must have):**
   ```json
   {
     "id": "string (UUID v4)",
     "name": "string (unique within workflow)",
     "type": "string (must start with n8n-nodes-base.)",
     "typeVersion": "number (node version)",
     "position": "[number, number] (x, y coordinates)",
     "parameters": "object (node-specific configuration)"
   }
   ```

3. **Connection Schema:**
   ```json
   {
     "NodeName": {
       "main": [
         [
           {
             "node": "string (target node name)",
             "type": "main",
             "index": 0
           }
         ]
       ]
     }
   }
   ```

4. **Credential References:**
   - All credentials MUST use aliases via `credentialId` or credential name references
   - NEVER include actual credential values
   - Format: `{ "id": "string", "name": "string" }`

5. **Error Handling Requirements:**
   - At least one error handling path OR
   - Error Trigger workflow configured OR
   - Try-catch pattern with explicit error nodes

6. **Retry Logic Requirements (for HTTP/API nodes):**
   - `maxRetries` parameter configured
   - Exponential backoff via `retryWaitTime` OR
   - Custom retry logic in Code node

7. **Loop Termination:**
   - All loop constructs must have explicit termination conditions
   - Split in Batches nodes must have `batchSize` and logic to handle completion

---

## Architecture Deep Dive

### Memory System (pgvector)

The knowledge base uses semantic search to retrieve relevant information:

```python
# Embedding generation
embeddings = sentence_transformers.encode(text_chunks, normalize_embeddings=True)

# Storage
INSERT INTO embeddings (doc_id, chunk_index, embedding) 
VALUES (?, ?, ?::vector(768))

# Retrieval (inner product for normalized vectors = cosine similarity)
SELECT * FROM embeddings 
ORDER BY embedding <#> query_embedding 
LIMIT k
```

**Indexing Strategy:**
- HNSW index for approximate nearest neighbor search
- Chunk size: 800 tokens with 100 token overlap
- Retrieval: Top-k (default k=8) most similar chunks

### Agent Orchestration (smolagents)

Each specialist agent is a `CodeAgent` with specific tools:

```python
class SpecialistAgent(CodeAgent):
    def __init__(self, llm, tools: list[Tool], system_prompt: str):
        super().__init__(
            tools=tools,
            llm=llm,
            system_prompt=system_prompt,
            max_steps=32,  # Prevent infinite loops
            verbose=True
        )
```

**Tool Execution Flow:**
1. Agent receives task from Face
2. Determines which tools to call based on system prompt
3. Executes tools sequentially or in parallel
4. Synthesizes results
5. Returns structured output to Face

### Validation Pipeline

**Stage 1: Schema Validation**
```python
def validate_workflow_basic(wf: dict) -> list[str]:
    errors = []
    # Check required keys
    missing = REQUIRED_KEYS - set(wf.keys())
    if missing:
        errors.append(f"Missing: {missing}")
    
    # Validate each node
    for node in wf["nodes"]:
        if not node.get("id"):
            errors.append(f"Node missing ID")
        # ... comprehensive checks
    
    return errors
```

**Stage 2: Best Practices Validation**
```python
def validate_best_practices(wf: dict) -> list[str]:
    warnings = []
    # Check for error handling
    has_error_handler = any("error" in n["type"].lower() for n in wf["nodes"])
    if not has_error_handler:
        warnings.append("No error handling detected")
    
    # Check retry logic on HTTP nodes
    for node in wf["nodes"]:
        if node["type"] == "n8n-nodes-base.httpRequest":
            if "maxRetries" not in node.get("parameters", {}):
                warnings.append(f"HTTP node '{node['name']}' lacks retry logic")
    
    return warnings
```

**Stage 3: Simulation**
```python
def simulate_execution(wf: dict, test_payloads: list[dict]):
    # Create workflow in n8n as inactive
    # Use test webhook or manual trigger
    # Execute with each payload
    # Collect execution logs
    # Analyze for errors, data flow issues
    return simulation_report
```

### Workflow Compilation Process

1. **Planning Phase:**
   - Parse user goal
   - Identify required integrations
   - Retrieve relevant patterns from memory
   - Design node sequence
   - Plan error handling strategy

2. **Compilation Phase:**
   - Generate unique IDs for each node
   - Configure node parameters
   - Set up connections
   - Add credential references (aliases only)
   - Position nodes for visual clarity

3. **Enrichment Phase:**
   - Add error handling nodes
   - Configure retry logic
   - Add logging/monitoring hooks
   - Set workflow-level settings

4. **Validation Phase:**
   - Schema validation
   - Best practices check
   - Credential reference verification
   - Connection graph validation

5. **Testing Phase:**
   - Generate test payloads
   - Simulate execution
   - Verify data flow
   - Check error paths

---

## n8n Best Practices (Embedded Knowledge)

Based on the comprehensive manual analysis, the system enforces:

### 1. Data Flow Principles
- **JSON Array-of-Objects Model**: Every item is an object, collections are arrays
- **Output → Input Chain**: Each node's output becomes the next node's input
- **Expression Language**: Use `$input.all()`, `$json.fiel
