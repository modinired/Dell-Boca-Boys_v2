# 🎯 Little Jim Spedines - Hybrid AI Agent

**Little Jim Spedines (Spedines)** - A comprehensive hybrid AI agent combining local Qwen 2.5 Coder with Google Gemini for world-class reasoning, continual learning, and autonomous task execution.

---

## 🌟 Features

### Core Capabilities
- **Hybrid Intelligence** - Draft-and-Polish collaboration between local Qwen and Gemini
- **Persistent Memory** - ChromaDB-powered semantic memory with RAG
- **Continual Learning** - Daily reflection, training data collection, and fine-tuning
- **Google Integration** - Drive ingestion, Sheets logging, full audit trail
- **Data Ingestion** - Automated pulls from financial APIs, scholarly sources
- **Ethical Activity Tracking** - Consent-based app/window monitoring (NO keylogging)
- **Safe Execution** - Sandboxed Python code execution
- **Daily Reflection** - Self-analysis and Q&A sessions with user

### Agent Persona
**Little Jim Spedines (Spedines)** - Sharp, witty, highly capable. Professional yet playful when appropriate. Focused on helping you accomplish tasks efficiently while learning and self-optimizing continually.

---

## 📋 Prerequisites

### Required
- **Python 3.10+**
- **Local LLM** - Qwen 2.5 Coder running via:
  - Ollama (recommended) - `ollama run qwen2.5-coder:32b`
  - vLLM - `python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-Coder-32B-Instruct`
  - LM Studio
- **Google Cloud Project** with:
  - Gemini API key
  - Service account with Sheets and Drive API enabled
- **16GB+ RAM** (8GB for agent + models)
- **50GB+ disk space**

### Optional
- Docker (for sandbox execution)
- PostgreSQL (for production deployment)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd spedines_agent
./scripts/setup.sh
```

This will:
- Create Python virtual environment
- Install all required packages
- Initialize ChromaDB
- Create necessary directories

### 2. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your API keys
```

Required configuration:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON
- `GOOGLE_SHEET_ID` - Google Sheet for logging
- `QWEN_ENDPOINT` - Local Qwen endpoint (default: http://localhost:11434)

### 3. Setup Google Cloud

Follow `docs/GOOGLE_SETUP.md` for:
- Creating service account
- Enabling APIs
- Creating audit Sheet
- Setting up Drive folder

### 4. Launch Spedines

```bash
./scripts/start_spedines.sh
```

This starts:
- FastAPI server (http://localhost:8080)
- Memory system (ChromaDB)
- Activity tracker (with consent)
- Data ingestion scheduler
- Daily reflection scheduler

### 5. Access the Agent

- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **Chat Interface**: http://localhost:8080 (web UI)

---

## 🏗️ Architecture

```
┌─────────────┐
│   User UI   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│      FastAPI Orchestrator           │
│  ┌───────────────────────────────┐  │
│  │   Draft-and-Polish Router     │  │
│  │  (Qwen → Gemini → Combine)    │  │
│  └───────────────────────────────┘  │
└──┬────┬────┬────┬────┬────┬────┬──┘
   │    │    │    │    │    │    │
   ▼    ▼    ▼    ▼    ▼    ▼    ▼
┌────┐┌──┐┌───┐┌───┐┌───┐┌───┐┌──┐
│Qwen││G ││Mem││Sht││Drv││Act││Sb│
│Loc ││e ││ory││ets││ive││Trk││ox│
│al  ││m │├───┤│   ││   ││   ││  │
│    ││i ││Chr││Log││Ing││   ││  │
│    ││n ││oma││   ││est││   ││  │
└────┘└──┘└───┘└───┘└───┘└───┘└──┘
```

### Component Details

1. **Local LLM (Qwen)** - Fast local drafts, private data handling
2. **Remote LLM (Gemini)** - Complex reasoning, polishing, critique
3. **Memory (ChromaDB)** - Vector embeddings, semantic search
4. **Google Sheets** - Audit log, training data, feedback
5. **Google Drive** - Learning materials ingestion
6. **Activity Tracker** - Ethical app/window monitoring
7. **Sandbox** - Safe code execution

---

## 📖 Usage

### Chat with Spedines

```bash
# CLI
python -m spedines.cli chat

# API
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain Python decorators"}'
```

### Daily Reflection Session

```bash
# Trigger reflection manually
curl -X POST http://localhost:8080/reflection/daily

# Or wait for automatic evening session (default: 8 PM)
```

### Execute Code Safely

```bash
curl -X POST http://localhost:8080/sandbox/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(sum(range(100)))", "language": "python"}'
```

### Ingest Learning Materials

```bash
# Upload to Google Drive folder
# Spedines automatically ingests and indexes

# Or manually trigger
curl -X POST http://localhost:8080/ingest/drive
```

---

## 🔧 Configuration

### Environment Variables

See `.env.example` for all options.

**Core Settings:**
```bash
# LLM Configuration
GEMINI_API_KEY=your_api_key
QWEN_ENDPOINT=http://localhost:11434/v1
QWEN_MODEL=qwen2.5-coder:32b

# Google Integration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_DRIVE_FOLDER_ID=your_folder_id

# Memory
CHROMA_DB_PATH=./data/chromadb
ENABLE_MEMORY=true

# Activity Tracking (requires explicit consent)
ENABLE_ACTIVITY_TRACKING=false
ACTIVITY_CONSENT_GIVEN=false

# Scheduling
DAILY_REFLECTION_TIME=20:00
DATA_PULL_INTERVAL=86400  # 24 hours in seconds
```

### Persona Customization

Edit `config/persona.yaml` to customize Spedines' personality, communication style, and behavior.

---

## 🔒 Privacy & Ethics

### What We Track (with your consent)
- ✅ Interactions with the agent
- ✅ App/window usage (productivity tracking)
- ✅ Files you explicitly share
- ✅ Feedback and corrections

### What We DON'T Track
- ❌ Keystrokes (no keylogging)
- ❌ Screen content without permission
- ❌ Private data without explicit sharing
- ❌ Activity when tracking is disabled

### Your Rights
- **Opt-in only** - Activity tracking requires explicit consent
- **View everything** - Full audit log in Google Sheets
- **Delete anytime** - `python -m spedines.cli privacy --delete-all`
- **Local first** - Sensitive data never sent to cloud
- **Encrypted storage** - All local logs encrypted at rest

---

## 🔄 Continual Learning

Spedines improves through:

1. **Daily Reflection** - Reviews day's activities, interactions, mistakes
2. **User Feedback** - Your corrections and ratings
3. **Training Data Collection** - High-quality interactions → Sheets
4. **Periodic Fine-tuning** - Local model updated weekly (optional)
5. **Memory Growth** - Continuously indexes new knowledge

### Training Pipeline

```
Interactions → Sheets → Curation → Dataset → Fine-tune → Deploy
     ↓            ↓          ↓          ↓         ↓         ↓
  Logged     Human     Export    LoRA    New    Gradual
           Review     JSONL    Training  Model  Rollout
```

---

## 📊 Monitoring & Analytics

### Built-in Dashboard

Access at http://localhost:8080/dashboard

**Metrics tracked:**
- Model usage (local vs Gemini)
- Response quality (user ratings)
- Learning progress (memory growth)
- Task completion rates
- Cost tracking (Gemini API usage)

### Export Reports

```bash
# Weekly report
python -m spedines.cli report --period week

# Custom date range
python -m spedines.cli report --start 2024-01-01 --end 2024-01-31
```

---

## 🛠️ Development

### Project Structure

```
spedines_agent/
├── spedines/              # Core package
│   ├── __init__.py
│   ├── agent.py           # Main Spedines agent
│   ├── orchestrator.py    # Draft-and-Polish router
│   ├── llm/               # LLM clients
│   │   ├── local.py       # Qwen client
│   │   ├── gemini.py      # Gemini client
│   │   └── router.py      # Routing logic
│   ├── memory/            # Memory system
│   │   ├── chroma.py      # ChromaDB integration
│   │   ├── embeddings.py  # Embedding generation
│   │   └── retrieval.py   # RAG retrieval
│   ├── google/            # Google integrations
│   │   ├── sheets.py      # Sheets API
│   │   ├── drive.py       # Drive API
│   │   └── auth.py        # Authentication
│   ├── ingest/            # Data ingestion
│   │   ├── drive.py       # Drive file ingestion
│   │   ├── finance.py     # Financial data
│   │   ├── scholarly.py   # Research papers
│   │   └── scheduler.py   # Scheduled jobs
│   ├── reflection/        # Reflection system
│   │   ├── daily.py       # Daily summaries
│   │   ├── questions.py   # Q&A generation
│   │   └── analysis.py    # Self-analysis
│   ├── tracking/          # Activity tracking
│   │   ├── activity.py    # App/window tracking
│   │   ├── consent.py     # Consent management
│   │   └── logger.py      # Activity logger
│   ├── sandbox/           # Code execution
│   │   ├── executor.py    # Safe execution
│   │   └── docker.py      # Docker sandbox
│   └── api/               # FastAPI application
│       ├── main.py        # Main app
│       ├── routes.py      # API routes
│       └── models.py      # Pydantic models
├── config/                # Configuration
│   ├── persona.yaml       # Agent persona
│   └── routing.yaml       # LLM routing rules
├── scripts/               # Deployment scripts
│   ├── setup.sh           # Initial setup
│   ├── start_spedines.sh  # Start agent
│   └── stop_spedines.sh   # Stop agent
├── tests/                 # Test suite
├── docs/                  # Documentation
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image
├── docker-compose.yml     # Docker Compose
└── README.md              # This file
```

### Running Tests

```bash
pytest tests/
```

---

## 📚 Documentation

- **[Google Setup Guide](docs/GOOGLE_SETUP.md)** - Configure Google Cloud
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Architecture Deep Dive](docs/ARCHITECTURE.md)** - Technical architecture
- **[Privacy Policy](docs/PRIVACY.md)** - Data handling and privacy
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing guidelines
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues

---

## 🐛 Troubleshooting

### Common Issues

**"Cannot connect to Qwen"**
```bash
# Check Ollama is running
ollama list
ollama run qwen2.5-coder:32b "test"
```

**"Google authentication failed"**
```bash
# Verify service account JSON
python -c "import json; print(json.load(open('service-account.json')))"

# Check API is enabled
# Visit: https://console.cloud.google.com/apis/dashboard
```

**"Memory system not working"**
```bash
# Reinitialize ChromaDB
rm -rf data/chromadb
python -m spedines.memory.init
```

For more issues, see `docs/TROUBLESHOOTING.md`

---

## 🤝 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: spedines-support@dellbocaboys.com

---

## 📄 License

Proprietary - Dell Boca Boys
See LICENSE file for details

---

## 🙏 Credits

Built by the **Dell Boca Boys** crew:
- **Little Jim Spedines** - The Crawler, Template Expert
- **Vito Italian (Diet Bocca)** - The Code Expert
- Powered by **Qwen 2.5 Coder** (Alibaba) and **Google Gemini**

---

**Little Jim Spedines - Sharp, efficient, always learning. Capisce?**
