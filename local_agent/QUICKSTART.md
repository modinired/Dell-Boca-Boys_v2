# 🎩 Vito - Quick Start Guide

Get up and running with Vito in under 2 minutes!

## Prerequisites

1. **Qwen 2.5 Coder running locally** (skip if already installed)

   Choose one method:

   **Option A: vLLM (Recommended)**
   ```bash
   pip install vllm
   python -m vllm.entrypoints.openai.api_server \
     --model Qwen/Qwen2.5-Coder-32B-Instruct \
     --port 8000
   ```

   **Option B: Ollama (Easiest)**
   ```bash
   # Install from ollama.ai
   ollama pull qwen2.5-coder:32b
   # Runs automatically on port 11434
   ```

   **Option C: Already have Qwen running?**
   - Just note your endpoint URL (e.g., `http://localhost:8000/v1`)

## Install Vito (30 seconds)

```bash
cd local_agent
./deploy.sh
```

That's it! The script will:
- ✓ Install dependencies
- ✓ Create configuration
- ✓ Test Qwen connection
- ✓ Set up everything

## Start Using Vito

### Interactive Chat (Easiest)

```bash
./vito chat
```

Then ask questions:
- "Generate a REST API endpoint for user authentication"
- "Review this code for bugs"
- "Explain how async/await works"

### Command Examples

```bash
# Generate code
./vito generate "Binary search implementation in Python"

# Review a file
./vito review myfile.py

# Explain code
./vito explain complex_function.py

# Refactor code
./vito refactor old_code.js

# Start API server
./vito serve
```

## Configuration

Edit `.env` if needed:

```bash
nano .env
```

Key settings:
- `QWEN_ENDPOINT` - Your Qwen endpoint (default: http://localhost:8000/v1)
- `QWEN_MODEL` - Model name
- `ENABLE_MEMORY` - Enable persistent memory (default: true)

## Troubleshooting

**"Cannot connect to Qwen"**
```bash
# Test Qwen is running:
curl http://localhost:8000/v1/models

# Check your endpoint in .env
cat .env | grep QWEN_ENDPOINT
```

**Dependencies issue**
```bash
pip install -r requirements.txt
```

## What's Next?

- Read the full [README.md](README.md) for all features
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- See [examples/](examples/) for Python API usage
- Start the API server: `./vito serve`

## Need Help?

1. Check README.md
2. Review .env.example for configuration options
3. Make sure Qwen is running: `curl http://localhost:8000/v1/models`

---

**🎩 That's it! Start coding with Vito!**

```bash
./vito chat
```
