#!/bin/bash

# =============================================================================
# N8n Agent - Integrated Web UI Launcher
# =============================================================================
# Launches the web interface connected to the full N8n Agent system
# =============================================================================

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}N8n Agent - Web Interface${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python found: $(python3 --version)"

# Check if we need to install dependencies
if ! python3 -c "import gradio" 2>/dev/null; then
    echo -e "${YELLOW}Installing required packages...${NC}"
    pip3 install gradio requests python-dotenv psycopg2-binary || {
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    }
fi

# Load environment
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} Loading environment from .env"
    set -a
    source .env
    set +a
else
    echo -e "${YELLOW}⚠${NC}  .env file not found, using defaults"
fi

# Check PostgreSQL (optional - can run without DB for basic features)
if command -v psql &> /dev/null; then
    if pg_isready -h ${PGHOST:-localhost} -p ${PGPORT:-5432} &> /dev/null; then
        echo -e "${GREEN}✓${NC} PostgreSQL connected"
    else
        echo -e "${YELLOW}⚠${NC}  PostgreSQL not accessible (some features may be limited)"
    fi
fi

# Check Ollama
if command -v ollama &> /dev/null && ollama list &> /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama connected"
else
    echo -e "${YELLOW}⚠${NC}  Ollama not running (starting...)"
    if command -v ollama &> /dev/null; then
        nohup ollama serve > /dev/null 2>&1 &
        sleep 2
    fi
fi

echo ""
echo -e "${GREEN}🚀 Starting Web Interface...${NC}"
echo ""

# Launch web UI
python3 app/web_interface.py
