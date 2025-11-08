#!/bin/bash
# =============================================================================
# n8n Autonomous Agent - Master Build Script
# =============================================================================
#
# This script performs complete system setup:
# 1. Environment validation
# 2. Dependency checks
# 3. Docker image builds
# 4. Database initialization
# 5. Knowledge base loading
# 6. Health checks
# 7. First-run verification
#
# Usage: ./build.sh [options]
#   Options:
#     --no-cache    Build Docker images without cache
#     --skip-crawl  Skip initial template crawling
#     --gpu-check   Verify NVIDIA GPU availability
#     --prod        Production mode (strict validation)
#
# =============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/.env.example"

# Flags
NO_CACHE=false
SKIP_CRAWL=false
GPU_CHECK=false
PROD_MODE=false

# =============================================================================
# Helper Functions
# =============================================================================

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

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed"
        return 1
    fi
    log_success "$1 is installed"
    return 0
}

# =============================================================================
# Parse Arguments
# =============================================================================

for arg in "$@"; do
    case $arg in
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --skip-crawl)
            SKIP_CRAWL=true
            shift
            ;;
        --gpu-check)
            GPU_CHECK=true
            shift
            ;;
        --prod)
            PROD_MODE=true
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "^#!/" | sed 's/^# //g' | sed 's/^#//g'
            exit 0
            ;;
        *)
            log_error "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# =============================================================================
# Pre-flight Checks
# =============================================================================

log_info "Starting pre-flight checks..."

# Check required commands
log_info "Checking required dependencies..."
check_command docker || exit 1
check_command docker-compose || check_command "docker compose" || exit 1
check_command curl || exit 1
check_command jq || log_warning "jq not found (optional, for JSON parsing)"

# Check Docker daemon
if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running"
    exit 1
fi
log_success "Docker daemon is running"

# Check GPU if requested
if [ "$GPU_CHECK" = true ]; then
    log_info "Checking NVIDIA GPU availability..."
    if ! command -v nvidia-smi &> /dev/null; then
        log_warning "nvidia-smi not found - GPU may not be available"
    else
        nvidia-smi &> /dev/null && log_success "NVIDIA GPU detected" || log_warning "GPU check failed"
    fi
fi

# =============================================================================
# Environment Configuration
# =============================================================================

log_info "Checking environment configuration..."

if [ ! -f "$ENV_FILE" ]; then
    log_warning ".env file not found, creating from template..."
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    log_warning "Please edit .env file with your configuration"
    log_warning "CRITICAL: Set N8N_API_TOKEN before continuing"
    
    if [ "$PROD_MODE" = true ]; then
        log_error "Production mode requires configured .env file"
        exit 1
    else
        read -p "Press Enter to continue with default values, or Ctrl+C to exit and configure..."
    fi
fi

# Source environment
set -a
source "$ENV_FILE"
set +a

# Validate critical settings
if [ -z "${N8N_API_TOKEN:-}" ] || [ "$N8N_API_TOKEN" = "your_n8n_personal_access_token_here" ]; then
    log_error "N8N_API_TOKEN not set in .env"
    log_info "Generate token in n8n: Settings -> Personal Access Tokens"
    if [ "$PROD_MODE" = true ]; then
        exit 1
    else
        log_warning "Continuing anyway (workflow deployment will fail)"
    fi
fi

if [ "$PROD_MODE" = true ]; then
    if [ "${PGPASSWORD:-}" = "change_me_in_production_use_strong_password" ]; then
        log_error "Default database password in production mode"
        exit 1
    fi
    if [ "${APP_DEBUG:-false}" = "true" ]; then
        log_error "DEBUG mode enabled in production"
        exit 1
    fi
fi

log_success "Environment configuration validated"

# =============================================================================
# Docker Build
# =============================================================================

log_info "Building Docker images..."

BUILD_ARGS=""
if [ "$NO_CACHE" = true ]; then
    BUILD_ARGS="--no-cache"
    log_info "Building without cache"
fi

cd "$PROJECT_ROOT"

# Build API service
log_info "Building API service..."
docker-compose build $BUILD_ARGS api

log_success "Docker images built successfully"

# =============================================================================
# Start Services
# =============================================================================

log_info "Starting services..."

# Start database and redis first
log_info "Starting database and Redis..."
docker-compose up -d db redis

# Wait for database
log_info "Waiting for PostgreSQL to be ready..."
sleep 5
MAX_RETRIES=30
RETRY_COUNT=0
until docker-compose exec -T db pg_isready -U "${PGUSER:-n8n_agent}" &> /dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        log_error "PostgreSQL failed to start after $MAX_RETRIES attempts"
        docker-compose logs db
        exit 1
    fi
    log_info "Waiting for PostgreSQL... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done
log_success "PostgreSQL is ready"

# Start n8n
log_info "Starting n8n..."
docker-compose up -d n8n

# Wait for n8n
log_info "Waiting for n8n to be ready..."
sleep 10
MAX_RETRIES=30
RETRY_COUNT=0
until curl -sf http://localhost:5678/healthz &> /dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        log_error "n8n failed to start after $MAX_RETRIES attempts"
        docker-compose logs n8n
        exit 1
    fi
    log_info "Waiting for n8n... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done
log_success "n8n is ready"

# Start vLLM
log_info "Starting vLLM (this may take several minutes to download model)..."
docker-compose up -d vllm

# Wait for vLLM
log_info "Waiting for vLLM to be ready (downloading model if first run)..."
sleep 30
MAX_RETRIES=60
RETRY_COUNT=0
until curl -sf http://localhost:8000/health &> /dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        log_error "vLLM failed to start after $MAX_RETRIES attempts"
        docker-compose logs vllm
        exit 1
    fi
    log_info "Waiting for vLLM... ($RETRY_COUNT/$MAX_RETRIES - model download may take 10+ minutes)"
    sleep 10
done
log_success "vLLM is ready"

# Start API
log_info "Starting API service..."
docker-compose up -d api

# Wait for API
log_info "Waiting for API to be ready..."
sleep 5
MAX_RETRIES=30
RETRY_COUNT=0
until curl -sf http://localhost:8080/health &> /dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        log_error "API failed to start after $MAX_RETRIES attempts"
        docker-compose logs api
        exit 1
    fi
    log_info "Waiting for API... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done
log_success "API is ready"

log_success "All services started successfully"

# =============================================================================
# Knowledge Base Initialization
# =============================================================================

log_info "Initializing knowledge base..."

# Load n8n manual
log_info "Loading n8n super user manual..."
docker-compose exec -T api python scripts/load_embeddings.py || log_warning "Manual loading failed (will continue)"

# Crawl templates
if [ "$SKIP_CRAWL" = false ]; then
    log_info "Crawling n8n workflow templates..."
    docker-compose exec -T api python scripts/crawl_templates.py --max-pages 50 || log_warning "Template crawling failed (will continue)"
    
    log_info "Crawling n8n documentation..."
    docker-compose exec -T api python scripts/crawl_docs.py || log_warning "Docs crawling failed (will continue)"
else
    log_warning "Skipping template crawling (--skip-crawl flag)"
fi

log_success "Knowledge base initialized"

# =============================================================================
# Health Check & Verification
# =============================================================================

log_info "Performing system health check..."

# Check all services
SERVICES=("db" "redis" "n8n" "vllm" "api")
for service in "${SERVICES[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        log_success "$service is running"
    else
        log_error "$service is not running"
        docker-compose ps
        exit 1
    fi
done

# Test API endpoint
log_info "Testing API endpoint..."
if curl -sf http://localhost:8080/health | jq . &> /dev/null; then
    log_success "API health check passed"
else
    log_error "API health check failed"
    exit 1
fi

# Test LLM
log_info "Testing LLM connection..."
if curl -sf http://localhost:8000/v1/models &> /dev/null; then
    log_success "LLM connection successful"
else
    log_warning "LLM connection failed"
fi

# =============================================================================
# Summary
# =============================================================================

log_success "=========================================="
log_success "  n8n Autonomous Agent Build Complete!"
log_success "=========================================="
echo ""
log_info "Services:"
log_info "  - n8n UI:       http://localhost:5678"
log_info "  - API:          http://localhost:8080"
log_info "  - API Docs:     http://localhost:8080/docs"
log_info "  - LLM Server:   http://localhost:8000"
log_info "  - PostgreSQL:   localhost:5432"
echo ""
log_info "Quick Start:"
echo "  # Test the system"
echo "  curl -X POST http://localhost:8080/api/v1/workflow/design \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"user_goal\":\"Create a webhook that processes orders\"}' | jq ."
echo ""
echo "  # View logs"
echo "  docker-compose logs -f api"
echo ""
echo "  # Stop services"
echo "  docker-compose down"
echo ""
log_info "Documentation: See README.md for detailed usage"
echo ""

if [ "$PROD_MODE" = false ]; then
    log_warning "Running in DEVELOPMENT mode"
    log_warning "Set --prod flag and review .env for production deployment"
fi

log_success "Build script completed successfully!"
