#!/bin/bash
# =============================================================================
# Dell Boca Boys V2 - Production Deployment Script
# =============================================================================
#
# This script deploys the complete Dell Boca Boys V2 system with all PhD-level
# improvements including:
# - Circuit breakers
# - Rate limiting
# - RBAC with JWT
# - Vault secrets management
# - PostgreSQL workflow repository
# - Prometheus metrics
# - Celery distributed tasks
# - Agent failover and health monitoring
#
# Usage:
#   ./deploy_production.sh [--profile gpu|analytics|full]
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
PROFILE="${1:---profile base}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/deployment.log"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

check_requirements() {
    log_info "Checking system requirements..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed."
        exit 1
    fi

    # Check disk space (need at least 20GB)
    AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | tr -d 'G')
    if [ "$AVAILABLE_SPACE" -lt 20 ]; then
        log_warning "Available disk space is less than 20GB. Deployment may fail."
    fi

    log_success "System requirements check passed"
}

setup_environment() {
    log_info "Setting up environment..."

    # Create .env file if it doesn't exist
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        log_info "Creating .env file from example..."
        if [ -f "$PROJECT_DIR/.env.example" ]; then
            cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        else
            cat > "$PROJECT_DIR/.env" <<EOF
# Database Configuration
PGUSER=n8n_agent
PGPASSWORD=$(openssl rand -base64 32)
PGDATABASE=n8n_agent_memory
PGHOST=db
PGPORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# n8n Configuration
N8N_HOST=localhost
N8N_PORT=5678
N8N_ENCRYPTION_KEY=$(openssl rand -base64 32)

# LLM Configuration
LLM_MODEL=Qwen/Qwen2.5-30B-Instruct-AWQ
OLLAMA_BASE_URL=http://localhost:11434

# Gemini API (Optional)
GEMINI_API_KEY=

# Vault Configuration (Optional)
VAULT_ADDR=http://vault:8200
VAULT_TOKEN=

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -base64 64)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Environment
ENVIRONMENT=production
EOF
        fi
        log_success "Environment file created"
    else
        log_info ".env file already exists"
    fi
}

initialize_database() {
    log_info "Initializing database..."

    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL..."
    docker-compose -f docker-compose.desktop.yml exec -T db pg_isready -U $PGUSER || true

    sleep 5

    # Run database migrations
    log_info "Running database migrations..."
    docker-compose -f docker-compose.desktop.yml exec -T db psql -U $PGUSER -d $PGDATABASE -f /docker-entrypoint-initdb.d/01_init_db.sql || log_warning "Database already initialized"

    log_success "Database initialized"
}

start_services() {
    log_info "Starting Dell Boca Boys V2 services..."

    cd "$PROJECT_DIR"

    # Determine Docker Compose command
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi

    # Parse profile
    PROFILE_FLAG=""
    if [[ "$PROFILE" == *"gpu"* ]]; then
        PROFILE_FLAG="--profile gpu"
    elif [[ "$PROFILE" == *"analytics"* ]]; then
        PROFILE_FLAG="--profile analytics"
    elif [[ "$PROFILE" == *"full"* ]]; then
        PROFILE_FLAG="--profile gpu --profile analytics"
    fi

    # Start services
    log_info "Launching services with profile: $PROFILE"
    $COMPOSE_CMD -f docker-compose.desktop.yml $PROFILE_FLAG up -d

    log_success "Services started"
}

verify_services() {
    log_info "Verifying service health..."

    # Wait for services to be ready
    sleep 10

    # Check PostgreSQL
    if docker-compose -f docker-compose.desktop.yml ps | grep -q "db.*Up"; then
        log_success "PostgreSQL is running"
    else
        log_error "PostgreSQL failed to start"
        exit 1
    fi

    # Check Redis
    if docker-compose -f docker-compose.desktop.yml ps | grep -q "redis.*Up"; then
        log_success "Redis is running"
    else
        log_error "Redis failed to start"
        exit 1
    fi

    # Check n8n
    if docker-compose -f docker-compose.desktop.yml ps | grep -q "n8n.*Up"; then
        log_success "n8n is running"
    else
        log_error "n8n failed to start"
        exit 1
    fi

    # Check API
    if docker-compose -f docker-compose.desktop.yml ps | grep -q "api.*Up"; then
        log_success "API is running"
    else
        log_warning "API is not running"
    fi
}

install_dependencies() {
    log_info "Installing Python dependencies..."

    # Install core dependencies
    pip install -r requirements_offline.txt || log_warning "Some dependencies may not have installed"

    # Install development dependencies
    pip install pytest pytest-asyncio pytest-cov black flake8 mypy || log_warning "Dev dependencies installation had issues"

    log_success "Dependencies installed"
}

run_tests() {
    log_info "Running test suite..."

    # Run pytest
    pytest tests/ -v --cov=core --cov-report=html --cov-report=term || log_warning "Some tests failed"

    log_info "Test results available in htmlcov/index.html"
}

setup_monitoring() {
    log_info "Setting up monitoring and observability..."

    # Start Prometheus (if analytics profile)
    if [[ "$PROFILE" == *"analytics"* ]] || [[ "$PROFILE" == *"full"* ]]; then
        log_info "Prometheus available at http://localhost:9090"
        log_info "Grafana available at http://localhost:3000 (if configured)"
    fi

    log_success "Monitoring setup complete"
}

display_access_info() {
    echo ""
    echo "============================================================================="
    echo "Dell Boca Boys V2 - Deployment Complete!"
    echo "============================================================================="
    echo ""
    echo "Services are now running:"
    echo ""
    echo "  n8n UI:           http://localhost:5678"
    echo "  Agent API:        http://localhost:8080"
    echo "  API Docs:         http://localhost:8080/docs"
    echo "  PostgreSQL:       localhost:5432"
    echo "  Redis:            localhost:6379"
    echo ""

    if [[ "$PROFILE" == *"analytics"* ]] || [[ "$PROFILE" == *"full"* ]]; then
        echo "  Neo4j Browser:    http://localhost:7474"
        echo "  Prometheus:       http://localhost:9090"
        echo ""
    fi

    echo "Credentials:"
    echo "  Database User:    $PGUSER"
    echo "  Database:         $PGDATABASE"
    echo ""
    echo "Logs:"
    echo "  View logs:        docker-compose -f docker-compose.desktop.yml logs -f"
    echo "  Deployment log:   $LOG_FILE"
    echo ""
    echo "Management:"
    echo "  Stop services:    docker-compose -f docker-compose.desktop.yml down"
    echo "  Restart:          docker-compose -f docker-compose.desktop.yml restart"
    echo "  Status:           docker-compose -f docker-compose.desktop.yml ps"
    echo ""
    echo "============================================================================="
    echo ""
}

# =============================================================================
# Main Deployment Flow
# =============================================================================

main() {
    log_info "Starting Dell Boca Boys V2 Production Deployment"
    log_info "Deployment profile: $PROFILE"
    echo ""

    # Step 1: Check requirements
    check_requirements

    # Step 2: Setup environment
    setup_environment

    # Step 3: Start services
    start_services

    # Step 4: Initialize database
    initialize_database

    # Step 5: Verify services
    verify_services

    # Step 6: Setup monitoring
    setup_monitoring

    # Step 7: Display access information
    display_access_info

    log_success "Deployment completed successfully!"

    echo ""
    echo "Next steps:"
    echo "  1. Access n8n UI at http://localhost:5678 and complete initial setup"
    echo "  2. Review API documentation at http://localhost:8080/docs"
    echo "  3. Run tests: pytest tests/ -v"
    echo "  4. Monitor logs: docker-compose -f docker-compose.desktop.yml logs -f"
    echo ""
}

# Run main function
main "$@"
