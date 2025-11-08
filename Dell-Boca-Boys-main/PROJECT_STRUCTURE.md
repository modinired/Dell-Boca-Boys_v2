# N8n Agent Project Structure

**Consolidated and Organized Repository Structure**

This document describes the clean, organized structure of the N8n Autonomous Agent + Workflow Intelligence system.

---

## 📁 Directory Overview

```
N8n-agent/
├── README.md                      # Main project documentation
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # Docker image for API service
├── docker-compose.yml             # Standard deployment
├── docker-compose.desktop.yml     # Desktop-optimized deployment
├── pyproject.toml                 # Python project configuration
│
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── settings.py               # Configuration management
│   ├── agent_face_chiccki.py     # Face agent orchestrator
│   ├── cli.py                    # Command-line interface
│   │
│   ├── crew/                     # Specialist agents
│   │   ├── __init__.py
│   │   └── agents.py             # 6 specialist agents
│   │
│   ├── routers/                  # API route handlers
│   │   ├── __init__.py
│   │   └── analytics.py          # Workflow intelligence endpoints
│   │
│   ├── tools/                    # Agent tools and integrations
│   │   ├── __init__.py
│   │   ├── memory.py             # Semantic memory (pgvector)
│   │   ├── n8n_api.py            # N8n REST API client
│   │   ├── schema.py             # N8n schema definitions
│   │   ├── validators.py         # Workflow validators
│   │   ├── simulator.py          # Workflow simulator
│   │   ├── crawler.py            # Web crawler
│   │   ├── process_mining.py     # Process mining integration
│   │   └── execution_tracker.py  # CEL execution logging
│   │
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   ├── database.py           # Database connections
│   │   ├── json_utils.py         # JSON parsing utilities
│   │   └── logging.py            # Structured logging
│   │
│   └── tests/                    # Test suite
│       ├── __init__.py
│       └── test_validators.py
│
├── scripts/                      # Operational scripts
│   ├── build.sh                  # Master build/deployment script
│   ├── init_db.sql              # Database schema initialization
│   ├── load_embeddings.py       # Load n8n manual into KB
│   ├── crawl_templates.py       # Crawl n8n templates
│   └── crawl_docs.py            # Crawl n8n documentation
│
├── docs/                         # Documentation
│   ├── DEPLOYMENT_GUIDE.md      # Full deployment guide
│   ├── DESKTOP_DEPLOYMENT.md    # Desktop-specific guide
│   ├── QUICK_REFERENCE.md       # Quick reference commands
│   ├── INDEX.md                 # Documentation navigation
│   ├── SYSTEM_SUMMARY.md        # Architecture summary
│   └── n8n-super-user-manual.pdf # N8n expertise
│
├── workflow-intelligence/        # Workflow Intelligence Stack
│   ├── README.md                # WI stack documentation
│   ├── requirements.txt         # Python dependencies
│   │
│   ├── db/                      # Database schemas
│   │   ├── cel_schema.sql       # Canonical Event Log
│   │   └── dimensions_schema.sql
│   │
│   ├── ingestion/               # Data ingestion
│   │   ├── ingest_samples.py
│   │   └── ingest_smartsheet.py
│   │
│   ├── slimming/                # Data deduplication
│   │   ├── dedup_identity.py
│   │   └── text_canonicalize.py
│   │
│   ├── mining/                  # Process mining
│   │   └── process_mining.py
│   │
│   ├── graph/                   # Graph analytics
│   │   └── build_graph.py       # Neo4j graph builder
│   │
│   ├── causal/                  # Causal analysis
│   │   └── causal_effects.py
│   │
│   ├── automation/              # Workflow automation
│   │   └── temporal_worker.py   # Temporal worker
│   │
│   ├── orchestration/           # Orchestration
│   │   └── init_db.py
│   │
│   ├── policies/                # Policy definitions
│   │   └── allow.rego           # OPA policies
│   │
│   ├── docker/                  # WI stack Docker config
│   │   └── compose.yml
│   │
│   ├── samples/                 # Sample data
│   │   └── smartsheet_rows.csv
│   │
│   └── tests/                   # WI stack tests
│       ├── test_validate.py
│       └── great_expectations/
│
└── archive/                      # Archived files
    └── n8n-autonomous-agent.tar.gz
```

---

## 🎯 Key Directories

### **`app/`** - Main Application
All Python application code for the N8n Agent system.

- **`main.py`** - FastAPI application with all API endpoints
- **`agent_face_chiccki.py`** - Orchestrator coordinating 6 specialist agents
- **`settings.py`** - Configuration with Pydantic validation
- **`cli.py`** - Command-line interface for direct agent access

### **`app/crew/`** - Multi-Agent System
Implementation of 6 specialist agents:
1. Crawler Agent - Knowledge gathering
2. Pattern Analyst - Best practices extraction
3. Flow Planner - Workflow architecture design
4. JSON Compiler - N8n JSON generation
5. QA Fighter - Validation and testing
6. Deploy Capo - Deployment to n8n

### **`app/tools/`** - Agent Tools
Reusable tools for agents:
- **memory.py** - Semantic memory with pgvector (768-dim embeddings)
- **n8n_api.py** - Complete n8n REST API client
- **process_mining.py** - PM4PY integration for pattern discovery
- **execution_tracker.py** - Canonical Event Log implementation
- **validators.py** - Schema, connection, credential, best practices validation
- **simulator.py** - Pre-deployment workflow testing

### **`app/routers/`** - API Routes
Modular API route handlers:
- **analytics.py** - Workflow intelligence endpoints (process mining, insights, benchmarking)

### **`scripts/`** - Operational Scripts
Scripts for deployment, data loading, and maintenance:
- **build.sh** - Master deployment script with health checks
- **load_embeddings.py** - Load n8n manual (5000+ words of expertise)
- **crawl_templates.py** - Gather real-world n8n examples
- **crawl_docs.py** - Fetch official n8n documentation

### **`docs/`** - Documentation
Comprehensive documentation (60KB+):
- **DESKTOP_DEPLOYMENT.md** - Desktop deployment guide (400+ lines)
- **DEPLOYMENT_GUIDE.md** - Full production deployment
- **QUICK_REFERENCE.md** - Common commands and troubleshooting
- **SYSTEM_SUMMARY.md** - Architecture deep dive

### **`workflow-intelligence/`** - Analytics Stack
Process mining, graph analytics, and causal analysis components.
Integrated but can be deployed independently.

### **`archive/`** - Historical Files
Original tar.gz and deprecated files for reference.

---

## 🔧 Configuration Files

### **Root Level**
- **`.env.example`** - Template for environment variables (copy to `.env`)
- **`Dockerfile`** - Container image for API service
- **`docker-compose.yml`** - Standard deployment configuration
- **`docker-compose.desktop.yml`** - Desktop-optimized with profiles
- **`pyproject.toml`** - Python dependencies and project metadata
- **`.gitignore`** - Git ignore patterns

---

## 🚀 Entry Points

### **API Server**
```bash
# Via Docker
docker-compose up -d

# Via Python
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### **CLI**
```bash
# Generate workflow
python -m app.cli generate "Create webhook workflow"

# Search knowledge
python -m app.cli search "error handling"

# Check health
python -m app.cli health
```

### **Scripts**
```bash
# Full deployment
./scripts/build.sh

# Load knowledge base
python scripts/load_embeddings.py

# Crawl templates
python scripts/crawl_templates.py --max-pages 50
```

---

## 📦 Deployment Configurations

### **Standard Deployment**
```bash
docker-compose up -d
```
Uses: `docker-compose.yml`
- All services
- Standard resource allocation
- Best for servers

### **Desktop Deployment**
```bash
# Minimal (4GB RAM)
docker-compose -f docker-compose.desktop.yml up -d

# With GPU (8GB RAM)
docker-compose -f docker-compose.desktop.yml --profile gpu up -d

# Full analytics (16GB RAM)
docker-compose -f docker-compose.desktop.yml --profile gpu --profile analytics up -d
```
Uses: `docker-compose.desktop.yml`
- Resource-optimized
- Optional components
- Best for desktops/laptops

---

## 🔍 Import Structure

All imports use absolute paths from project root:

```python
# From anywhere in the project
from app.tools.memory import memory
from app.agent_face_chiccki import face_agent
from app.settings import settings
from app.utils.logging import logger
```

---

## 🧪 Testing

```bash
# Run tests
pytest app/tests/

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific test
pytest app/tests/test_validators.py -v
```

---

## 📊 Data Directories (Created at Runtime)

These directories are created automatically by the application:

```
data/                    # Created by build script
├── raw/                 # Raw crawled data
│   ├── templates/
│   ├── docs/
│   └── youtube/
└── processed/           # Processed data

artifacts/               # Created by process mining
└── process_tree.png     # Generated visualizations
```

---

## 🔐 Environment Variables

Key variables in `.env`:

```bash
# Required
N8N_API_TOKEN=your_token_here
PGPASSWORD=strong_password

# Optional (have defaults)
PGHOST=db
PGPORT=5432
LLM_MODEL=Qwen/Qwen2.5-30B-Instruct-AWQ
APP_PORT=8080
```

See `.env.example` for complete list.

---

## 🌟 Key Features by Directory

| Directory | Features |
|-----------|----------|
| `app/` | Workflow generation, validation, deployment |
| `app/crew/` | Multi-agent orchestration (6 agents) |
| `app/tools/` | Semantic search, n8n API, process mining |
| `app/routers/` | REST API endpoints |
| `scripts/` | Deployment automation, data loading |
| `docs/` | Comprehensive guides |
| `workflow-intelligence/` | Process mining, causal analysis, graph analytics |

---

## 📝 Notes

### **Clean Structure Benefits**
✅ No nested `n8n-agent/n8n-agent/` structure
✅ All code at root level
✅ Clear separation of concerns
✅ Organized documentation
✅ Easy navigation
✅ Standard Python project layout

### **Backward Compatibility**
All import paths remain unchanged. Docker volumes and scripts work as before.

### **Documentation**
Complete documentation in `docs/` directory with:
- Deployment guides (standard and desktop)
- Quick reference
- Architecture summaries
- Navigation index

---

## 🔄 Migration Notes

**Previous Structure:**
```
N8n-agent/
├── n8n-agent/          # Nested subdirectory
│   ├── app/
│   └── ...
└── ...
```

**New Structure:**
```
N8n-agent/
├── app/                # Direct at root
├── docs/               # Organized documentation
├── workflow-intelligence/  # Clean name
└── ...
```

All functionality preserved, structure improved!

---

**Last Updated:** November 4, 2024
**Version:** 2.0 (Consolidated)
