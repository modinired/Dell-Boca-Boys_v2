# N8n Agent + Workflow Intelligence: Desktop Deployment Guide

**Production-Ready AI Workflow Generation with Advanced Analytics**

This system combines:
- **N8n Autonomous Agent** - AI-powered workflow generation from natural language
- **Workflow Intelligence Stack** - Process mining, causal analysis, and graph analytics

---

## ✅ Desktop Deployment Confirmed

**YES, this agent CAN be deployed on desktop!**

The system is fully optimized for desktop deployment with multiple configuration profiles to match your hardware:

### Deployment Profiles

1. **Minimal (Basic Desktop)** - 4GB RAM, 2 CPU cores
   - N8n Agent with CPU-based LLM (via Ollama)
   - Core features only

2. **Standard (Mid-Range Desktop)** - 8GB RAM, 4 CPU cores
   - Full agent system
   - Optional GPU acceleration

3. **Full (High-End Desktop/Workstation)** - 16GB+ RAM, 8+ CPU cores, NVIDIA GPU
   - Complete stack with all analytics
   - GPU-accelerated LLM inference
   - Neo4j graph analytics
   - Process mining capabilities

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** v2.0+
- **4GB+ RAM available**
- **10GB+ free disk space**

### Installation

```bash
# 1. Clone/navigate to repository
cd n8n-agent

# 2. Create environment file
cp .env.example .env

# 3. Edit .env and set N8N_API_TOKEN
# Generate token in n8n UI: Settings -> Personal Access Tokens
nano .env  # or use your favorite editor

# 4. Start the system (minimal profile)
docker-compose -f docker-compose.desktop.yml up -d

# 5. Wait for services to start (~2 minutes)
docker-compose -f docker-compose.desktop.yml ps

# 6. Initialize knowledge base
docker-compose -f docker-compose.desktop.yml exec api python scripts/load_embeddings.py
```

### Access the System

- **N8n UI:** http://localhost:5678
- **Agent API:** http://localhost:8080
- **API Documentation:** http://localhost:8080/docs (Swagger UI)
- **Database:** localhost:5432

---

## 🎯 Deployment Options

### Option 1: Minimal Deployment (Recommended for Most Desktops)

**Hardware Requirements:**
- 4GB RAM
- 2 CPU cores
- 10GB disk space

**Command:**
```bash
docker-compose -f docker-compose.desktop.yml up -d
```

**Includes:**
- PostgreSQL + pgvector (database)
- Redis (queue management)
- n8n (workflow platform)
- Agent API (workflow generation)
- Basic execution tracking

**Note:** Uses CPU for LLM. For better performance, install Ollama locally:
```bash
# Install Ollama (https://ollama.ai)
ollama pull qwen2.5:7b

# Update .env:
LLM_BASE_URL=http://host.docker.internal:11434/v1
LLM_MODEL=qwen2.5:7b
```

---

### Option 2: GPU-Accelerated Deployment

**Hardware Requirements:**
- 8GB+ RAM
- 4 CPU cores
- NVIDIA GPU with 8GB+ VRAM
- CUDA drivers installed
- 20GB disk space

**Command:**
```bash
docker-compose -f docker-compose.desktop.yml --profile gpu up -d
```

**Additional Features:**
- GPU-accelerated LLM inference (vLLM)
- Qwen 2.5 30B model (AWQ quantized)
- Significantly faster workflow generation
- Better quality AI-generated workflows

**GPU Setup (Linux):**
```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

---

### Option 3: Full Analytics Stack

**Hardware Requirements:**
- 16GB+ RAM
- 8 CPU cores
- NVIDIA GPU recommended
- 40GB disk space

**Command:**
```bash
docker-compose -f docker-compose.desktop.yml --profile gpu --profile analytics up -d
```

**Additional Features:**
- **Neo4j** - Knowledge graph for workflow relationships
- **Kafka** - Event streaming for real-time analytics
- **Temporal** - Advanced workflow orchestration
- **Process Mining** - Discover execution patterns
- **Causal Analysis** - Identify performance factors

---

## 📊 Features by Deployment

| Feature | Minimal | GPU | Full Analytics |
|---------|---------|-----|----------------|
| Workflow Generation | ✅ (CPU) | ✅ (GPU) | ✅ (GPU) |
| Knowledge Base | ✅ | ✅ | ✅ |
| Validation & Testing | ✅ | ✅ | ✅ |
| n8n Deployment | ✅ | ✅ | ✅ |
| Execution Tracking | ✅ | ✅ | ✅ |
| REST API | ✅ | ✅ | ✅ |
| CLI Interface | ✅ | ✅ | ✅ |
| Process Mining | ❌ | ✅ | ✅ |
| Graph Analytics | ❌ | ❌ | ✅ |
| Causal Analysis | ❌ | ❌ | ✅ |
| Real-time Events | ❌ | ❌ | ✅ |
| Advanced Automation | ❌ | ❌ | ✅ |

---

## 🔧 Configuration

### Environment Variables (.env)

**Required:**
```bash
N8N_API_TOKEN=your_n8n_personal_access_token_here
PGPASSWORD=change_me_in_production
```

**Optional (with defaults):**
```bash
# Database
PGUSER=n8n_agent
PGDATABASE=n8n_agent_memory

# LLM Configuration
LLM_MODEL=Qwen/Qwen2.5-30B-Instruct-AWQ
LLM_TEMPERATURE=0.1

# Application
APP_PORT=8080
APP_LOG_LEVEL=INFO
APP_ENV=development
```

### Resource Limits

Edit `docker-compose.desktop.yml` to adjust resources:

```yaml
services:
  vllm:
    deploy:
      resources:
        limits:
          memory: 16G  # Adjust based on your GPU
        reservations:
          devices:
            - capabilities: [gpu]
```

---

## 🎮 Usage Examples

### Generate a Workflow (REST API)

```bash
curl -X POST http://localhost:8080/api/v1/workflow/design \
  -H 'Content-Type: application/json' \
  -d '{
    "user_goal": "Create a webhook that receives customer orders, validates the data, saves to PostgreSQL, and sends Slack notification",
    "auto_stage": false
  }'
```

### Generate a Workflow (CLI)

```bash
docker-compose -f docker-compose.desktop.yml exec api \
  python -m app.cli generate "Send email notification when invoice is created"
```

### Search Knowledge Base

```bash
curl -X POST http://localhost:8080/api/v1/knowledge/search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "error handling best practices",
    "top_k": 5
  }'
```

### Get Analytics (Full Stack Only)

```bash
# Process mining analysis
curl http://localhost:8080/api/v1/analytics/process-mining/analyze \
  -H 'Content-Type: application/json' \
  -d '{"workflow_id": "your-workflow-id"}'

# Execution statistics
curl http://localhost:8080/api/v1/analytics/executions/statistics

# Workflow insights
curl http://localhost:8080/api/v1/analytics/intelligence/insights/your-workflow-id
```

---

## 🔍 Monitoring & Troubleshooting

### Check Service Status

```bash
# View running services
docker-compose -f docker-compose.desktop.yml ps

# View logs
docker-compose -f docker-compose.desktop.yml logs -f api

# Check specific service
docker-compose -f docker-compose.desktop.yml logs vllm
```

### Health Checks

```bash
# System health
curl http://localhost:8080/health

# Detailed status
curl http://localhost:8080/status

# Process mining availability
curl http://localhost:8080/api/v1/analytics/process-mining/status
```

### Common Issues

**1. Out of Memory**
```bash
# Solution: Increase Docker memory limit
# Docker Desktop: Settings -> Resources -> Memory -> Increase to 8GB+
```

**2. GPU Not Detected**
```bash
# Check NVIDIA drivers
nvidia-smi

# Restart Docker
sudo systemctl restart docker
```

**3. n8n Token Not Set**
```bash
# Edit .env file
nano .env

# Set: N8N_API_TOKEN=your_token_here

# Restart services
docker-compose -f docker-compose.desktop.yml restart api
```

**4. Slow LLM Inference (CPU)**
```bash
# Solution: Use lighter model or install Ollama
LLM_MODEL=qwen2.5:7b  # Smaller, faster model
```

---

## 🔐 Security for Desktop

### Production Deployment

If exposing to network:

1. **Change all passwords in .env:**
```bash
PGPASSWORD=YourSecurePassword123!
NEO4J_PASSWORD=AnotherSecurePassword456!
```

2. **Enable HTTPS:**
```bash
# Use reverse proxy (nginx/traefik) with SSL certificates
```

3. **Restrict access:**
```bash
# Bind to localhost only in docker-compose:
ports:
  - "127.0.0.1:8080:8080"  # Only accessible from local machine
```

4. **Enable authentication:**
```bash
# Add API key middleware (implement in main.py)
```

---

## 🎓 Advanced Features

### Process Mining (Analytics Profile)

Analyze workflow execution patterns:

```python
# Install process mining dependencies
docker-compose -f docker-compose.desktop.yml exec api \
  pip install pm4py==2.7.9

# Run process mining analysis
curl -X POST http://localhost:8080/api/v1/analytics/process-mining/analyze \
  -d '{"workflow_id": "abc-123"}'
```

### Neo4j Graph Queries (Analytics Profile)

Explore workflow relationships:

1. Access Neo4j Browser: http://localhost:7474
2. Login: neo4j / neo4jStrongP@55
3. Run Cypher queries:
```cypher
// Find all workflows using HTTP Request node
MATCH (w:Workflow)-[:CONTAINS]->(n:Node {type: 'httpRequest'})
RETURN w.name, COUNT(n) as http_count
ORDER BY http_count DESC
```

---

## 📦 Backup & Restore

### Backup Data

```bash
# Backup database
docker-compose -f docker-compose.desktop.yml exec db \
  pg_dump -U n8n_agent n8n_agent_memory > backup.sql

# Backup n8n data
docker cp n8n_unified_n8n:/home/node/.n8n ./n8n_backup

# Backup volumes
docker run --rm -v n8n_unified_db_data:/data \
  -v $(pwd):/backup ubuntu \
  tar czf /backup/db_data.tar.gz /data
```

### Restore Data

```bash
# Restore database
docker-compose -f docker-compose.desktop.yml exec -T db \
  psql -U n8n_agent n8n_agent_memory < backup.sql

# Restore n8n data
docker cp ./n8n_backup n8n_unified_n8n:/home/node/.n8n
```

---

## 🔄 Updates

### Update System

```bash
# Pull latest images
docker-compose -f docker-compose.desktop.yml pull

# Rebuild API
docker-compose -f docker-compose.desktop.yml build api

# Restart with new images
docker-compose -f docker-compose.desktop.yml up -d
```

### Update Knowledge Base

```bash
# Re-crawl templates
docker-compose -f docker-compose.desktop.yml exec api \
  python scripts/crawl_templates.py --max-pages 100

# Re-crawl docs
docker-compose -f docker-compose.desktop.yml exec api \
  python scripts/crawl_docs.py
```

---

## 📈 Performance Tuning

### For Low-Resource Desktops

```yaml
# docker-compose.desktop.yml
services:
  api:
    environment:
      - SEARCH_TOP_K=3  # Reduce search results
      - CHUNK_SIZE=500  # Smaller chunks

  vllm:
    command:
      - "--max-model-len=8192"  # Reduce context window
      - "--gpu-memory-utilization=0.75"  # More conservative
```

### For High-Performance Desktops

```yaml
services:
  vllm:
    command:
      - "--max-model-len=32768"  # Full context
      - "--gpu-memory-utilization=0.95"  # Max GPU usage
      - "--tensor-parallel-size=2"  # Multi-GPU
```

---

## 🆘 Support

### Documentation
- **API Docs:** http://localhost:8080/docs
- **README:** See main README.md
- **System Summary:** SYSTEM_SUMMARY.md

### Logs
```bash
# All logs
docker-compose -f docker-compose.desktop.yml logs

# Specific service
docker-compose -f docker-compose.desktop.yml logs api -f
```

### Reset Everything
```bash
# Stop and remove all containers/volumes
docker-compose -f docker-compose.desktop.yml down -v

# Start fresh
docker-compose -f docker-compose.desktop.yml up -d
```

---

## ✅ Confirmation Checklist

- [x] Agent can be deployed on desktop
- [x] Multiple deployment profiles (minimal/GPU/full)
- [x] Resource requirements documented
- [x] Step-by-step installation guide
- [x] Troubleshooting section
- [x] Security guidelines
- [x] Performance tuning options
- [x] Backup/restore procedures

**The N8n Agent System is fully desktop-deployment ready!** 🎉

Choose your deployment profile based on your hardware and start generating AI-powered workflows in minutes.
