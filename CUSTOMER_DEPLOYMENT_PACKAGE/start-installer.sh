#!/bin/bash
###############################################################################
# Dell Boca Boys V2 - Installer Launcher (Mac/Linux)
# Starts the web-based installation wizard
###############################################################################

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              Dell Boca Boys V2 - Installer                    ║
║          Enterprise AI Workflow Automation                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${GREEN}Starting installation wizard...${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER_DIR="$SCRIPT_DIR/installer"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is required but not installed.${NC}"
    echo ""
    echo "Please install Python 3:"
    echo "  - macOS: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  - Fedora/RHEL: sudo dnf install python3 python3-pip"
    echo ""
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}pip3 is required but not installed.${NC}"
    echo "Installing pip3..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        python3 -m ensurepip --upgrade
    else
        sudo apt install python3-pip || sudo dnf install python3-pip || sudo yum install python3-pip
    fi
fi

# Create virtual environment if it doesn't exist
if [[ ! -d "$INSTALLER_DIR/venv" ]]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$INSTALLER_DIR/venv"
fi

# Activate virtual environment
source "$INSTALLER_DIR/venv/bin/activate"

# Install required packages
echo "Installing installer dependencies..."
pip3 install --quiet --upgrade pip
pip3 install --quiet flask flask-socketio flask-cors psutil

# Make installer executable
chmod +x "$INSTALLER_DIR/installer.py"

# Start the installer
echo ""
echo -e "${GREEN}Starting installer web interface...${NC}"
echo ""
echo -e "Opening browser to: ${BLUE}http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC}"
echo "  - Do NOT close this terminal window"
echo "  - The installer will open in your web browser"
echo "  - If browser doesn't open automatically, go to: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the installer"
echo ""

# Wait a moment for the message to be read
sleep 2

# Start the installer server
cd "$INSTALLER_DIR"
python3 installer.py

# Open browser (in background)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sleep 2 && open "http://localhost:3000" &
elif command -v xdg-open &> /dev/null; then
    # Linux
    sleep 2 && xdg-open "http://localhost:3000" &
fi

# Wait for Ctrl+C
wait
