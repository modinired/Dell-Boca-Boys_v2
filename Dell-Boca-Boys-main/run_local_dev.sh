#!/bin/bash
# =============================================================================
# Dell Boca Boys V2 - Local Development Mode (No Docker Required)
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

log_info "Starting Dell Boca Boys V2 in Local Development Mode"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is required but not found"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
log_success "Python available: $PYTHON_VERSION"

# Check Redis
if command -v redis-server &> /dev/null; then
    log_success "Redis server available"

    # Start Redis if not running
    if ! pgrep redis-server > /dev/null; then
        log_info "Starting Redis server..."
        redis-server --daemonize yes --port 6379
        sleep 2
    else
        log_info "Redis already running"
    fi
else
    log_warning "Redis not available - some features will be limited"
fi

# Create workspace directory
mkdir -p workspace_dell_boca

# Install minimal dependencies
log_info "Installing core dependencies..."
pip install -q gradio requests sqlite3 2>/dev/null || true

log_success "Dependencies installed"

# Create minimal environment file
cat > .env.local <<EOF
# Local Development Environment
ENVIRONMENT=development
OLLAMA_BASE_URL=http://localhost:11434
GEMINI_API_KEY=${GEMINI_API_KEY:-}
REDIS_HOST=localhost
REDIS_PORT=6379
EOF

log_success "Environment configured"

echo ""
echo "============================================================================="
echo "Dell Boca Boys V2 - Local Development Mode"
echo "============================================================================="
echo ""
echo "Available modes:"
echo ""
echo "  1. Web UI (Gradio) - Collaborative chat with dual-model support"
echo "  2. Interactive Python - Direct component access"
echo "  3. Test Suite - Run all tests"
echo ""
echo "Choose mode [1-3]: "
read -r MODE

case $MODE in
    1)
        log_info "Starting Web UI..."
        python3 web_ui_dell_boca_vista_v2.py
        ;;
    2)
        log_info "Starting Interactive Python..."
        python3 -i <<EOF
import sys
sys.path.insert(0, '.')

print("Dell Boca Boys V2 - Interactive Mode")
print("=" * 60)
print("Available imports:")
print("  from core.exceptions import *")
print("  from core.circuit_breaker import *")
print("  from core.rate_limiter import *")
print("  from core.rbac import *")
print("  from core.metrics import *")
print("")
print("Example: rbac = init_rbac()")
print("=" * 60)
EOF
        ;;
    3)
        log_info "Running test suite..."
        if command -v pytest &> /dev/null; then
            pytest tests/ -v
        else
            log_error "pytest not installed. Install with: pip install pytest pytest-asyncio"
        fi
        ;;
    *)
        log_error "Invalid mode selection"
        exit 1
        ;;
esac
