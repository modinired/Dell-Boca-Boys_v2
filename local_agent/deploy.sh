#!/bin/bash

# Vito - Local Coding Agent Deployment Script
# Quick and easy deployment for local offline AI coding agent

set -e  # Exit on error

echo "========================================"
echo "🎩 Vito - Local Coding Agent"
echo "========================================"
echo "Quick Deployment Script"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3.10+ is installed
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is not installed${NC}"
    echo "Please install pip3"
    exit 1
fi
echo -e "${GREEN}✓ pip3 found${NC}"

# Create virtual environment (optional but recommended)
read -p "Create virtual environment? (recommended) [Y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"

    echo "Activating virtual environment..."
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"

    echo ""
    echo -e "${YELLOW}Note: To activate later, run: source venv/bin/activate${NC}"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env configuration file..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}Please edit .env to configure your Qwen endpoint${NC}"
fi

# Create Vito home directory
VITO_HOME="${VITO_HOME:-$HOME/.vito}"
mkdir -p "$VITO_HOME"
echo -e "${GREEN}✓ Vito home directory: $VITO_HOME${NC}"

# Make CLI executable
chmod +x cli.py
echo -e "${GREEN}✓ CLI made executable${NC}"

# Test Qwen connection
echo ""
echo "Testing Qwen connection..."
echo -e "${YELLOW}Make sure Qwen 2.5 Coder is running locally!${NC}"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

QWEN_ENDPOINT="${QWEN_ENDPOINT:-http://localhost:8000/v1}"

echo "Checking Qwen endpoint: $QWEN_ENDPOINT"

# Simple test using curl
if command -v curl &> /dev/null; then
    if curl -s --max-time 5 "$QWEN_ENDPOINT/models" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Qwen is reachable!${NC}"
    else
        echo -e "${RED}⚠ Warning: Cannot reach Qwen at $QWEN_ENDPOINT${NC}"
        echo "Please make sure Qwen is running before using Vito"
    fi
else
    echo -e "${YELLOW}curl not found, skipping Qwen connectivity test${NC}"
fi

# Create convenience launcher
echo ""
echo "Creating convenience launcher..."
cat > vito << 'EOF'
#!/bin/bash
# Vito launcher script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate venv if it exists
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

# Run CLI
python3 cli.py "$@"
EOF

chmod +x vito
echo -e "${GREEN}✓ Launcher created${NC}"

# Summary
echo ""
echo "========================================"
echo "✓ Deployment Complete!"
echo "========================================"
echo ""
echo "Quick Start:"
echo ""
echo "1. Make sure Qwen 2.5 Coder is running locally"
echo "   (vLLM, Ollama, llama.cpp, or LM Studio)"
echo ""
echo "2. Edit .env if needed:"
echo "   nano .env"
echo ""
echo "3. Start chatting with Vito:"
echo "   ./vito chat"
echo ""
echo "Other commands:"
echo "   ./vito generate \"description\"    # Generate code"
echo "   ./vito review file.py            # Review code"
echo "   ./vito explain file.py           # Explain code"
echo "   ./vito serve                     # Start API server"
echo ""
echo "For help:"
echo "   ./vito --help"
echo ""
echo "========================================"
echo "🎩 Vito Italian (Diet Bocca)"
echo "World-Class Local Coding Agent"
echo "========================================"
echo ""

# Offer to start chat immediately
read -p "Start interactive chat now? [Y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    ./vito chat
fi
