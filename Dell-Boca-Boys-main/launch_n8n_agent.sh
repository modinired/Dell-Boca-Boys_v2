#!/bin/bash

# =============================================================================
# N8n Autonomous Agent - Desktop Launcher
# =============================================================================
# This script launches the N8n Agent system with all dependencies
# Compatible with macOS desktop environments
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Log file
LOG_FILE="$SCRIPT_DIR/logs/launcher.log"
mkdir -p "$SCRIPT_DIR/logs"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# =============================================================================
# Pre-flight Checks
# =============================================================================

log "Starting N8n Autonomous Agent..."
log "Working directory: $SCRIPT_DIR"

# Check if .env exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    error ".env file not found!"
    error "Please copy .env.example to .env and configure it"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    error "Docker is not installed!"
    error "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    warn "Docker daemon is not running. Starting Docker Desktop..."
    open -a Docker
    info "Waiting for Docker to start (this may take 30-60 seconds)..."

    # Wait for Docker to be ready (max 2 minutes)
    COUNTER=0
    while ! docker info &> /dev/null && [ $COUNTER -lt 24 ]; do
        sleep 5
        COUNTER=$((COUNTER + 1))
        echo -n "."
    done
    echo ""

    if ! docker info &> /dev/null; then
        error "Docker failed to start. Please start Docker Desktop manually."
        exit 1
    fi
    log "Docker is now running!"
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    warn "Ollama is not installed!"
    warn "Please install Ollama from https://ollama.ai"
    warn "N8n Agent will continue but LLM features may not work"
else
    # Check if Ollama is running
    if ! ollama list &> /dev/null; then
        warn "Ollama is not running. Starting Ollama..."
        # Start Ollama in background
        nohup ollama serve > "$SCRIPT_DIR/logs/ollama.log" 2>&1 &
        sleep 3
    fi

    # Check if required model is available
    REQUIRED_MODEL="qwen2.5-coder:7b"
    if ! ollama list | grep -q "$REQUIRED_MODEL"; then
        warn "Required model $REQUIRED_MODEL not found"
        info "Pulling model (this may take 10-20 minutes on first run)..."
        ollama pull "$REQUIRED_MODEL"
    fi
    log "Ollama is ready with model: $REQUIRED_MODEL"
fi

# =============================================================================
# Start Services
# =============================================================================

log "Starting Docker services..."

# Stop any existing containers
docker compose down 2>/dev/null || true

# Start services
if [ "$1" == "minimal" ]; then
    info "Starting in minimal mode (database and API only)..."
    docker compose up -d db redis api
elif [ "$1" == "desktop" ]; then
    info "Starting in desktop mode..."
    docker compose -f docker-compose.desktop.yml up -d
else
    info "Starting all services..."
    docker compose up -d
fi

# =============================================================================
# Wait for Services to be Ready
# =============================================================================

log "Waiting for services to be ready..."

# Wait for database
info "Waiting for PostgreSQL..."
COUNTER=0
until docker compose exec -T db pg_isready -U n8n_agent &> /dev/null || [ $COUNTER -eq 30 ]; do
    sleep 2
    COUNTER=$((COUNTER + 1))
    echo -n "."
done
echo ""

if [ $COUNTER -eq 30 ]; then
    error "PostgreSQL failed to start"
    docker compose logs db
    exit 1
fi
log "PostgreSQL is ready!"

# Wait for API
info "Waiting for API..."
COUNTER=0
until curl -f http://localhost:8080/health &> /dev/null || [ $COUNTER -eq 60 ]; do
    sleep 2
    COUNTER=$((COUNTER + 1))
    echo -n "."
done
echo ""

if [ $COUNTER -eq 60 ]; then
    warn "API may not be ready yet. Check logs with: docker compose logs api"
else
    log "API is ready!"
fi

# =============================================================================
# Initialize Knowledge Base (First Run)
# =============================================================================

if [ ! -f "$SCRIPT_DIR/.initialized" ]; then
    log "First run detected. Initializing knowledge base..."

    info "Loading n8n documentation embeddings..."
    docker compose exec -T api python scripts/load_embeddings.py 2>&1 | tee -a "$LOG_FILE" || warn "Failed to load embeddings"

    info "Crawling n8n templates (this may take a few minutes)..."
    docker compose exec -T api python scripts/crawl_templates.py --max-pages 20 2>&1 | tee -a "$LOG_FILE" || warn "Failed to crawl templates"

    # Mark as initialized
    touch "$SCRIPT_DIR/.initialized"
    log "Knowledge base initialized!"
fi

# =============================================================================
# Display Status
# =============================================================================

log ""
log "========================================="
log "N8n Autonomous Agent is Running!"
log "========================================="
log ""
log "Services:"
log "  - API:          http://localhost:8080"
log "  - n8n:          http://localhost:5678"
log "  - PostgreSQL:   localhost:5432"
log "  - Redis:        localhost:6379"
log ""
log "Quick Commands:"
log "  - API Health:   curl http://localhost:8080/health"
log "  - View Logs:    docker compose logs -f api"
log "  - Stop:         docker compose down"
log ""
log "Logs saved to: $LOG_FILE"
log ""

# Open browser to API docs
if [ "$2" == "open" ] || [ "$1" == "open" ]; then
    sleep 3
    open http://localhost:8080/docs
    open http://localhost:5678
fi

# Keep script running if requested
if [ "$1" == "foreground" ] || [ "$2" == "foreground" ]; then
    log "Running in foreground mode. Press Ctrl+C to stop..."
    docker compose logs -f
fi
