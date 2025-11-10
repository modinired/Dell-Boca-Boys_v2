# Vito's Local Coding Agent - Architecture

## Overview
Lightweight local offline AI agent powered by Qwen 2.5 Coder for world-class comprehensive code generation, analysis, and refactoring.

## Design Principles
- **100% Local & Offline** - No cloud dependencies, runs entirely on your machine
- **Lightweight** - Minimal dependencies, fast startup
- **Memory-Enabled** - Maintains context across sessions for better coding assistance
- **Comprehensive Code Focus** - Expert-level code generation, analysis, refactoring, debugging
- **Quick Deployment** - One command installation and setup

## Architecture Components

### 1. Local LLM Client (`llm_local.py`)
- Direct integration with Qwen 2.5 Coder via OpenAI-compatible API
- Assumes Qwen is already running locally (vLLM, llama.cpp, or Ollama)
- Optimized prompts for code generation tasks
- Streaming support for real-time responses

### 2. Memory System (`memory.py`)
- **Session Memory** - Current conversation context
- **Project Memory** - File changes, code patterns, project structure
- **Long-term Memory** - SQLite database for persistent storage
- **Code Context** - Automatic tracking of relevant files and functions
- **Smart Retrieval** - Semantic search for relevant past interactions

### 3. Code Agent (`code_agent.py`)
- **Vito Personality** - Diet Bocca, comprehensive code expert
- **Core Capabilities**:
  - Code Generation - Write complete, production-ready code
  - Code Analysis - Deep code review and improvement suggestions
  - Refactoring - Modernize and optimize existing code
  - Debugging - Identify and fix bugs
  - Documentation - Generate comprehensive docs
  - Code Explanation - Detailed explanations of complex code

### 4. CLI Interface (`cli.py`)
- Simple command-line interface
- Interactive REPL mode
- One-shot commands for quick tasks
- File-based operations (read code, write code)

### 5. REST API (`api.py`)
- FastAPI-based REST endpoints
- Simple HTTP interface for integrations
- WebSocket support for streaming responses
- Health monitoring

### 6. Quick Deployment (`deploy.sh`)
- Automatic dependency installation
- Database initialization
- Configuration setup
- Qwen connection test
- One-command deployment

## System Requirements

### Minimum
- Python 3.10+
- 8GB RAM (for agent + Qwen running)
- 10GB disk space
- Qwen 2.5 Coder already installed and running

### Recommended
- Python 3.11+
- 16GB+ RAM
- SSD storage
- GPU for faster Qwen inference

## Qwen Integration Options

The agent supports Qwen running via:
1. **vLLM** - High performance inference server (recommended)
2. **Ollama** - Simple local deployment
3. **llama.cpp** - Lightweight C++ implementation
4. **LM Studio** - GUI-based local LLM hosting

Default endpoint: `http://localhost:8000/v1` (vLLM)
Configurable via environment variable: `QWEN_ENDPOINT`

## Memory Architecture

```
Memory Store (SQLite)
├── Sessions
│   ├── session_id
│   ├── timestamp
│   ├── context_summary
│   └── messages[]
├── Code Context
│   ├── file_path
│   ├── content_hash
│   ├── last_modified
│   └── relevance_score
├── Code Snippets
│   ├── snippet_id
│   ├── language
│   ├── code
│   ├── description
│   └── tags[]
└── Project Knowledge
    ├── project_path
    ├── structure
    ├── tech_stack
    └── conventions
```

## Data Flow

```
User Request
    ↓
CLI/API Interface
    ↓
Code Agent (Vito)
    ↓
Memory System ←→ Code Agent
    ↓
Local LLM Client (Qwen 2.5 Coder)
    ↓
Response Processing
    ↓
Memory Update
    ↓
User Response
```

## Example Usage

```bash
# Interactive mode
vito chat

# One-shot code generation
vito generate "Create a FastAPI endpoint for user authentication"

# Code review
vito review myfile.py

# Refactor code
vito refactor myfile.py --style modern-python

# Explain code
vito explain complex_function.py

# Start API server
vito serve --port 8080
```

## Configuration

Configuration via environment variables or `.env` file:

```bash
# Qwen endpoint
QWEN_ENDPOINT=http://localhost:8000/v1
QWEN_MODEL=Qwen/Qwen2.5-Coder-32B-Instruct

# Memory database
MEMORY_DB_PATH=~/.vito/memory.db

# Agent settings
MAX_CONTEXT_LENGTH=8000
TEMPERATURE=0.1
MAX_TOKENS=4096

# Logging
LOG_LEVEL=INFO
```

## File Structure

```
local_agent/
├── ARCHITECTURE.md          # This file
├── README.md                # User guide
├── requirements.txt         # Python dependencies
├── deploy.sh                # Quick deployment script
├── .env.example             # Environment template
│
├── vito/                    # Main package
│   ├── __init__.py
│   ├── llm_local.py         # Qwen integration
│   ├── memory.py            # Memory system
│   ├── code_agent.py        # Core agent
│   ├── code_tools.py        # Code utilities
│   └── config.py            # Configuration
│
├── cli.py                   # CLI interface
├── api.py                   # REST API
│
├── tests/                   # Test suite
│   ├── test_llm.py
│   ├── test_memory.py
│   └── test_agent.py
│
└── examples/                # Usage examples
    ├── chat_example.py
    ├── code_gen_example.py
    └── api_example.py
```

## Security & Privacy

- **100% Local** - No data leaves your machine
- **No Telemetry** - Zero external communication
- **Encrypted Memory** - Optional encryption for sensitive code
- **Isolated Environment** - Runs in sandboxed Python environment

## Performance

- **Startup Time** - < 2 seconds
- **Response Time** - Depends on Qwen inference speed (typically 1-5s)
- **Memory Usage** - ~100MB for agent + Qwen's memory
- **Database Size** - Grows with usage (~1MB per 100 interactions)

## Vito's Character

Vito Italian (Diet Bocca) - The comprehensive code expert:
- **Personality** - Professional, detail-oriented, no-nonsense
- **Communication** - Clear, concise, comprehensive
- **Code Quality** - World-class, production-ready, well-documented
- **Approach** - Thorough analysis, best practices, modern patterns
- **Focus** - Correctness, performance, maintainability

---

**Built by the Dell Boca Boys for serious developers who demand world-class code.**
