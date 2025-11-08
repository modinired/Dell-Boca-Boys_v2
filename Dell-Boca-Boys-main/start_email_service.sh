#!/bin/bash
#
# Dell Bocca Boys Email Service Startup Script
#
# This script starts the email communication service for Dell Bocca Boys agents.
# Official Agent Email: ace.llc.nyc@gmail.com
#

set -e  # Exit on error

echo "============================================================"
echo "  Dell Bocca Boys Email Service Startup"
echo "============================================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo ""
    echo "Creating .env file from template..."

    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Created .env file from .env.example"
        echo ""
        echo "Please edit .env and set your AGENT_EMAIL_PASSWORD"
        echo ""
        echo "To get a Gmail app password:"
        echo "1. Go to https://myaccount.google.com/"
        echo "2. Navigate to Security → 2-Step Verification"
        echo "3. Enable 2-Step Verification if not enabled"
        echo "4. Go to App passwords"
        echo "5. Generate a new app password for 'Mail'"
        echo "6. Copy the 16-character password to .env"
        echo ""
        read -p "Press Enter when you've set AGENT_EMAIL_PASSWORD in .env..."
    else
        echo "❌ Error: .env.example not found"
        exit 1
    fi
fi

# Load environment variables
echo "Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Check if password is set
if [ -z "$AGENT_EMAIL_PASSWORD" ]; then
    echo "❌ Error: AGENT_EMAIL_PASSWORD not set in .env"
    exit 1
fi

echo "✓ Environment variables loaded"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"
echo ""

# Install dependencies if needed
echo "Checking dependencies..."
if ! python3 -c "import aioimaplib" 2>/dev/null; then
    echo "Installing email dependencies..."
    pip install -q aioimaplib aiosmtplib
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi
echo ""

# Start the service
echo "============================================================"
echo "  Starting Email Communication Service"
echo "============================================================"
echo ""
echo "Agent Email: ${AGENT_EMAIL:-ace.llc.nyc@gmail.com}"
echo "Poll Interval: ${EMAIL_POLL_INTERVAL:-60} seconds"
echo "Subject Filter: 'Dell Bocca Boys'"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

# Run the service
python3 core/communication/email_service.py
