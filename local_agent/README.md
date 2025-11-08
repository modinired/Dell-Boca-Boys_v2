# 🎩 Vito - Local Offline AI Coding Agent

**Vito Italian (Diet Bocca)** - Your comprehensive code expert that runs 100% locally and offline.

Powered by **Qwen 2.5 Coder**, Vito provides world-class code generation, review, refactoring, debugging, and more - all without sending your code to the cloud.

Built by the **Dell Boca Boys** for serious developers who demand:
- ✓ **Privacy** - Your code never leaves your machine
- ✓ **Performance** - Fast local inference
- ✓ **Persistence** - Memory system maintains context across sessions
- ✓ **Professionalism** - Production-ready, comprehensive code

---

## Features

### Core Capabilities

- **Code Generation** - Write complete, production-ready code from descriptions
- **Code Review** - Comprehensive analysis with actionable suggestions
- **Refactoring** - Modernize and optimize existing code
- **Debugging** - Find and fix bugs with detailed explanations
- **Code Explanation** - Clear, thorough explanations of complex code
- **Documentation** - Generate comprehensive docs and docstrings
- **Project Analysis** - Analyze file and project structures

### Technical Features

- **100% Local & Offline** - No cloud dependencies, complete privacy
- **Memory System** - Maintains coding context across sessions
- **Multi-Language** - Python, JavaScript, TypeScript, Java, C++, Go, Rust, and more
- **CLI Interface** - Simple command-line tool
- **REST API** - FastAPI-based HTTP interface
- **WebSocket Support** - Streaming responses
- **Lightweight** - Minimal dependencies, fast startup

---

## Quick Start

### Prerequisites

1. **Python 3.10+** installed
2. **Qwen 2.5 Coder** running locally via one of:
   - **vLLM** (recommended) - `http://localhost:8000`
   - **Ollama** - `http://localhost:11434`
   - **llama.cpp** - `http://localhost:8080`
   - **LM Studio** - `http://localhost:1234`

### Installation (30 seconds)

```bash
# Clone or download this directory
cd local_agent

# Run deployment script
./deploy.sh

# That's it! Start chatting:
./vito chat
```

The deployment script will:
- ✓ Check Python version
- ✓ Create virtual environment (optional)
- ✓ Install dependencies
- ✓ Create configuration file
- ✓ Test Qwen connection
- ✓ Create convenience launcher

### Manual Installation

```bash
# Install dependencies
pip3 install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # Set your QWEN_ENDPOINT

# Make CLI executable
chmod +x cli.py

# Start using Vito
python3 cli.py chat
```

---

## Usage

### Interactive Chat Mode

The easiest way to use Vito is interactive chat:

```bash
./vito chat
```

Then just ask questions naturally:
- "Generate a FastAPI endpoint for user authentication with JWT"
- "Review this function for performance issues"
- "Explain how Python decorators work"
- "Refactor this code to use modern async/await patterns"

**Chat Commands:**
- `/help` - Show available commands
- `/stats` - View agent statistics
- `/clear` - Clear screen
- `/exit` - Exit chat

### Command-Line Usage

#### Generate Code

```bash
./vito generate "Create a REST API client for GitHub with rate limiting"

./vito generate "Binary search tree implementation" --language python
```

#### Review Code

```bash
./vito review myfile.py

./vito review complex_algorithm.js
```

#### Explain Code

```bash
./vito explain difficult_code.py

./vito explain utils.js --level comprehensive
```

#### Refactor Code

```bash
./vito refactor legacy_code.py

./vito refactor old_script.js --goal "use modern ES6+ features"
```

#### Debug Code

```bash
./vito debug buggy_code.py

./vito debug broken.js --error "TypeError: cannot read property"
```

#### Analyze Files/Projects

```bash
# Analyze single file
./vito analyze myfile.py

# Analyze entire project
./vito analyze ./my_project
```

### REST API Mode

Start the API server:

```bash
./vito serve
# or
./vito serve --host 0.0.0.0 --port 8080
```

API will be available at: `http://localhost:8080`

**API Documentation:** `http://localhost:8080/docs`

#### Example API Requests

**Chat:**
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Python decorators"}'
```

**Generate Code:**
```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "FastAPI endpoint for user login",
    "language": "python",
    "style": "modern best practices"
  }'
```

**Review Code:**
```bash
curl -X POST http://localhost:8080/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def calc(x,y):\n  return x+y",
    "language": "python",
    "focus": "best practices"
  }'
```

---

## Configuration

Configuration is done via `.env` file or environment variables.

### Key Settings

```bash
# Qwen endpoint (adjust for your setup)
QWEN_ENDPOINT=http://localhost:8000/v1

# Qwen model name
QWEN_MODEL=Qwen/Qwen2.5-Coder-32B-Instruct

# Enable memory (recommended)
ENABLE_MEMORY=true

# Streaming responses
STREAMING=true

# Temperature (0.0 = deterministic, 1.0 = creative)
TEMPERATURE=0.1

# Maximum tokens in response
MAX_TOKENS=4096
```

See `.env.example` for all options.

### Qwen Deployment Options

#### Option 1: vLLM (Recommended)

```bash
# Install vLLM
pip install vllm

# Start Qwen server
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-32B-Instruct \
  --port 8000
```

Set in `.env`:
```bash
QWEN_ENDPOINT=http://localhost:8000/v1
QWEN_MODEL=Qwen/Qwen2.5-Coder-32B-Instruct
```

#### Option 2: Ollama

```bash
# Install Ollama from ollama.ai

# Pull Qwen model
ollama pull qwen2.5-coder:32b

# Ollama runs automatically on port 11434
```

Set in `.env`:
```bash
QWEN_ENDPOINT=http://localhost:11434/v1
QWEN_MODEL=qwen2.5-coder:32b
```

#### Option 3: llama.cpp

```bash
# Build llama.cpp with server support
# Download Qwen GGUF model
# Start server:
./server -m qwen2.5-coder-32b.gguf --port 8080
```

Set in `.env`:
```bash
QWEN_ENDPOINT=http://localhost:8080/v1
QWEN_MODEL=qwen2.5-coder
```

#### Option 4: LM Studio

1. Download and install LM Studio
2. Download Qwen 2.5 Coder model
3. Start local server (default port 1234)

Set in `.env`:
```bash
QWEN_ENDPOINT=http://localhost:1234/v1
QWEN_MODEL=qwen2.5-coder-32b
```

---

## Memory System

Vito maintains memory across sessions to provide better context-aware assistance.

### What's Stored

- **Conversation History** - Recent messages for context
- **Code Context** - Files you've worked with
- **Code Snippets** - Reusable patterns
- **Project Knowledge** - Project structure and conventions

### Memory Location

Default: `~/.vito/memory.db` (SQLite database)

### Disable Memory

Set in `.env`:
```bash
ENABLE_MEMORY=false
```

### Clear Memory

```bash
rm ~/.vito/memory.db
```

---

## Examples

### Example 1: Generate a Complex Function

```bash
./vito chat
```

```
You: Generate a Python function that implements a LRU cache with TTL support.
Include proper type hints, comprehensive error handling, and thread safety.

Vito: [Generates production-ready code with full implementation]
```

### Example 2: Code Review

```bash
./vito review legacy_auth.py
```

Vito analyzes:
- Correctness and bugs
- Performance issues
- Security vulnerabilities
- Best practices compliance
- Improvement suggestions

### Example 3: Refactor to Modern Code

```bash
./vito refactor old_callbacks.js --goal "convert to async/await"
```

Vito refactors callback-based code to modern async/await patterns.

### Example 4: Debug with Error Message

```bash
./vito chat
```

```
You: I'm getting "AttributeError: 'NoneType' object has no attribute 'id'"
in this code:

[paste code]

Vito: [Analyzes code, identifies the bug, explains root cause, provides fix]
```

---

## Python API

Use Vito programmatically in your Python code:

```python
from vito import VitoAgent

# Create agent
vito = VitoAgent()

# Chat
response = vito.chat("How do I implement a binary search?")
print(response)

# Generate code
code = vito.generate_code(
    description="FastAPI endpoint for file upload",
    language="python"
)
print(code)

# Review code
review = vito.review_code(
    code=my_code,
    language="python",
    focus="security"
)
print(review)

# Analyze file
analysis = vito.analyze_file("myfile.py")
print(analysis)
```

See `examples/` directory for more examples.

---

## Architecture

```
local_agent/
├── vito/                    # Core package
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── llm_local.py         # Qwen integration
│   ├── memory.py            # Memory system
│   ├── code_agent.py        # Main agent
│   └── code_tools.py        # Code utilities
│
├── cli.py                   # CLI interface
├── api.py                   # REST API
├── deploy.sh                # Deployment script
├── requirements.txt         # Dependencies
├── .env.example             # Config template
└── README.md                # This file
```

See `ARCHITECTURE.md` for detailed architecture documentation.

---

## System Requirements

### Minimum

- Python 3.10+
- 8GB RAM (for agent + Qwen)
- 10GB disk space
- Qwen 2.5 Coder running locally

### Recommended

- Python 3.11+
- 16GB+ RAM
- SSD storage
- GPU for faster Qwen inference

---

## Troubleshooting

### "Cannot connect to Qwen"

**Solution:**
1. Make sure Qwen is running: `curl http://localhost:8000/v1/models`
2. Check your `QWEN_ENDPOINT` in `.env`
3. Verify Qwen is using OpenAI-compatible API

### "Module not found" errors

**Solution:**
```bash
pip3 install -r requirements.txt
```

### Slow responses

**Possible causes:**
- CPU-only inference (use GPU for faster responses)
- Large model on insufficient RAM
- Try smaller Qwen model (7B or 14B instead of 32B)

### Memory database errors

**Solution:**
```bash
# Clear and reinitialize memory
rm ~/.vito/memory.db
```

---

## Performance Tips

1. **Use GPU** - Dramatically faster inference
2. **Smaller Model** - Qwen 7B is faster, still excellent for code
3. **Adjust Temperature** - Lower = faster (less sampling)
4. **Limit Context** - Reduce `MAX_CONTEXT_LENGTH` if needed
5. **Disable Memory** - Slight speedup if context not needed

---

## Privacy & Security

- ✓ **100% Local** - No data sent to cloud
- ✓ **No Telemetry** - Zero external communication
- ✓ **Isolated** - Runs in local environment
- ✓ **Open Source** - Transparent, auditable code

Your code stays on your machine. Always.

---

## Comparison to Cloud AI

| Feature | Vito (Local) | Cloud AI |
|---------|-------------|----------|
| Privacy | ✓ Complete | ❌ Code sent to cloud |
| Offline | ✓ Works offline | ❌ Requires internet |
| Latency | Fast (local) | Varies (network) |
| Cost | Free | Pay per token |
| Customization | ✓ Full control | Limited |
| Memory | ✓ Persistent | Session-based |

---

## FAQ

**Q: What models does Vito support?**
A: Any OpenAI-compatible API. Optimized for Qwen 2.5 Coder.

**Q: Can I use different LLMs?**
A: Yes! Change `QWEN_ENDPOINT` to any OpenAI-compatible endpoint.

**Q: Does it work offline?**
A: Yes, 100% offline once Qwen is running locally.

**Q: How much RAM do I need?**
A: 8GB minimum, 16GB+ recommended (includes Qwen).

**Q: Can I use GPT-4 or Claude?**
A: You can, but that defeats the "local offline" purpose.

**Q: Is it as good as GPT-4?**
A: Qwen 2.5 Coder is specifically optimized for code and rivals GPT-4 for programming tasks.

---

## Contributing

This is a Dell Boca Boys project. Contributions welcome!

---

## License

See LICENSE file for details.

---

## Credits

Built by the **Dell Boca Boys** crew:
- **Vito Italian (Diet Bocca)** - Comprehensive code expert
- Powered by **Qwen 2.5 Coder** from Alibaba Cloud
- Repurposed from Dell Boca Boys V2 multi-agent system

---

## Support

For issues or questions:
1. Check this README
2. Check `ARCHITECTURE.md`
3. Review `.env.example` for configuration
4. Check Qwen is running: `curl http://localhost:8000/v1/models`

---

**🎩 Vito Italian (Diet Bocca) - World-Class Local Coding Agent**

*"Keep your code local. Keep it professional. Keep it comprehensive."*

---
