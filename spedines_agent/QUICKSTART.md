# Spedines Agent - Quick Start Guide

## 🚀 Current Status

**Branch**: `claude/local-offline-ai-agent-011CUvTj6GrDG4wiH74uWG9v`
**Location**: `/home/user/Dell-Boca-Boys_v2/spedines_agent/`
**Status**: Core agent complete (~7,540 lines), ready for deployment

## 📍 What's Been Built

✅ **LLM Integration** - Local Qwen + Gemini with Draft-and-Polish
✅ **Memory System** - ChromaDB with semantic search and RAG
✅ **Google Integration** - Sheets logging + Drive ingestion
✅ **Main Agent** - Complete SpedinesAgent orchestrator
✅ **CLI Interface** - Interactive chat with commands
✅ **Examples** - Comprehensive usage examples

Total: **~7,540 lines** of production-ready code

## 🎯 Deployment Options

### Option 1: Local-Only Mode (Recommended for Testing)

**Requirements**:
- Python 3.8+
- Ollama with Qwen model (or any OpenAI-compatible endpoint)

**Setup**:
```bash
cd /home/user/Dell-Boca-Boys_v2/spedines_agent

# 1. Install dependencies
pip install -r requirements.txt

# 2. Configuration is already created (.env file)
# Edit if needed: nano .env

# 3. Start Ollama (in another terminal)
ollama serve

# 4. Pull Qwen model (first time only)
ollama pull qwen2.5-coder:7b

# 5. Launch Spedines
python -m spedines.cli
```

### Option 2: Hybrid Mode (Local + Gemini)

**Additional Requirements**:
- Gemini API key

**Setup**:
```bash
# 1. Edit .env and add your Gemini API key
nano .env
# Set: GEMINI_API_KEY=your_key_here
# Set: ROUTING_STRATEGY=draft_polish

# 2. Launch
python -m spedines.cli
```

### Option 3: Full Mode (All Features)

**Additional Requirements**:
- Google Cloud service account
- Google Sheets spreadsheet
- Google Drive folder

**Setup**:
```bash
# 1. Place service account JSON in config/
cp /path/to/service-account.json config/

# 2. Edit .env
nano .env
# Set: GOOGLE_APPLICATION_CREDENTIALS=./config/service-account.json
# Set: GOOGLE_SHEET_ID=your_sheet_id
# Set: GOOGLE_DRIVE_FOLDER_ID=your_folder_id
# Set: ENABLE_SHEETS_LOGGING=true
# Set: ENABLE_DRIVE_INGESTION=true

# 3. Launch
python -m spedines.cli
```

## 🧪 Testing

### Quick Test (No LLM Required)
```bash
cd /home/user/Dell-Boca-Boys_v2/spedines_agent

# Test imports
python -c "from spedines.agent import SpedinesAgent; print('✅ Imports work')"

# Test configuration
python -c "from spedines.config import SpedinesConfig; c = SpedinesConfig.from_env(); print('✅ Config loads')"
```

### With Mock LLM
If you don't have Ollama set up yet, you can test with a mock endpoint or wait for Ollama installation.

### Full Test
```bash
# Run example script
python scripts/example_usage.py

# Or interactive CLI
python -m spedines.cli
```

## 📝 CLI Commands

Once launched, you can use:
- `/help` - Show available commands
- `/health` - Check system health
- `/metrics` - View usage metrics
- `/search <query>` - Search memory
- `/quit` - Exit

## 🔧 Troubleshooting

### "Cannot import spedines"
```bash
# Make sure you're in the right directory
cd /home/user/Dell-Boca-Boys_v2/spedines_agent

# Install dependencies
pip install -r requirements.txt
```

### "Ollama connection failed"
```bash
# Start Ollama
ollama serve

# In another terminal, verify it's running
curl http://localhost:11434/api/tags

# Pull model if not present
ollama pull qwen2.5-coder:7b
```

### "Memory/ChromaDB errors"
```bash
# Create data directory
mkdir -p data/chromadb

# Check permissions
chmod -R 755 data/
```

## 📊 Current Configuration

The `.env` file is pre-configured for **LOCAL-ONLY** mode:
- ✅ Local Qwen via Ollama
- ❌ Gemini (disabled, no API key needed)
- ✅ Memory system (ChromaDB)
- ❌ Google Sheets (disabled)
- ❌ Google Drive (disabled)

This allows you to test immediately with just Ollama!

## 🎉 Next Steps

Once deployed:
1. Chat with Spedines via CLI
2. Test memory and knowledge features
3. Add your Gemini API key for hybrid mode
4. Configure Google Cloud for full features
5. Build additional features (reflection, data ingestion, etc.)

## 📚 Documentation

- **Full README**: `README.md`
- **Implementation Status**: `IMPLEMENTATION_STATUS.md`
- **Configuration Reference**: `.env.example`
- **Examples**: `scripts/example_usage.py`

---

**Repository**: Dell-Boca-Boys_v2
**Agent**: Little Jim Spedines
**Version**: 1.0.0-beta
