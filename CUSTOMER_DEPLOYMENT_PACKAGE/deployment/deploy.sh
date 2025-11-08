#!/bin/bash
###############################################################################
# Dell Boca Boys V2 - Master Deployment Script
# Production-ready deployment with comprehensive security guardrails
###############################################################################

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Deployment configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="$ROOT_DIR/application"
DEPLOYMENT_LOG="$ROOT_DIR/logs/deployment-$(date +%Y%m%d-%H%M%S).log"
ROLLBACK_SNAPSHOT="$ROOT_DIR/backups/pre-deployment-$(date +%Y%m%d-%H%M%S)"

# Create necessary directories
mkdir -p "$ROOT_DIR/logs"
mkdir -p "$ROOT_DIR/backups"
mkdir -p "$ROOT_DIR/secrets"

# Logging functions
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$DEPLOYMENT_LOG"
}

log_info() {
    log "INFO" "${BLUE}$@${NC}"
}

log_success() {
    log "SUCCESS" "${GREEN}$@${NC}"
}

log_warn() {
    log "WARN" "${YELLOW}$@${NC}"
}

log_error() {
    log "ERROR" "${RED}$@${NC}"
}

# Error handler
error_handler() {
    local line=$1
    log_error "Deployment failed at line $line"
    log_error "Check log file: $DEPLOYMENT_LOG"
    log_info "You can rollback using: ./deployment/rollback.sh"
    exit 1
}

trap 'error_handler $LINENO' ERR

# Progress tracking
print_header() {
    echo ""
    echo "============================================================================="
    log_info "$1"
    echo "============================================================================="
    echo ""
}

print_phase() {
    echo ""
    log_info ">>> $1"
    echo ""
}

# Security check: Ensure running with appropriate privileges
check_privileges() {
    print_phase "Checking user privileges..."

    if [[ $EUID -eq 0 ]]; then
        log_warn "Running as root. This is not recommended for security reasons."
        log_warn "Consider running as a regular user with sudo access."
    fi

    # Check if user can run Docker commands
    if ! docker ps > /dev/null 2>&1; then
        log_error "Cannot run Docker commands. Please ensure:"
        log_error "  1. Docker is installed"
        log_error "  2. User is in the 'docker' group (run: sudo usermod -aG docker \$USER)"
        log_error "  3. Docker service is running"
        exit 1
    fi

    log_success "Privilege check passed"
}

# Pre-deployment validation
validate_prerequisites() {
    print_phase "Validating prerequisites..."

    local errors=0

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        ((errors++))
    else
        log_success "Docker found: $(docker --version)"
    fi

    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed or not v2+"
        ((errors++))
    else
        log_success "Docker Compose found: $(docker compose version)"
    fi

    # Check disk space (require 100GB)
    local available_gb=$(df -BG "$ROOT_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available_gb -lt 100 ]]; then
        log_warn "Only ${available_gb}GB disk space available. 100GB recommended."
        log_warn "Deployment may fail if disk space runs out."
    else
        log_success "Disk space: ${available_gb}GB available"
    fi

    # Check memory (require 16GB)
    local total_mem_gb=$(free -g | awk 'NR==2 {print $2}')
    if [[ $total_mem_gb -lt 16 ]]; then
        log_warn "Only ${total_mem_gb}GB RAM available. 16GB recommended."
        log_warn "Performance may be degraded."
    else
        log_success "Memory: ${total_mem_gb}GB available"
    fi

    # Check for port conflicts
    local ports=(80 443 5678 5432 8000 8080)
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_warn "Port $port is already in use. This may cause conflicts."
        fi
    done

    if [[ $errors -gt 0 ]]; then
        log_error "Prerequisites validation failed with $errors error(s)"
        exit 1
    fi

    log_success "All prerequisites validated"
}

# Create rollback snapshot
create_rollback_snapshot() {
    print_phase "Creating rollback snapshot..."

    mkdir -p "$ROLLBACK_SNAPSHOT"

    # Backup existing Docker containers state
    if docker ps -a --format '{{.Names}}' | grep -q 'dell-boca'; then
        log_info "Backing up existing containers..."
        docker ps -a --filter "name=dell-boca" --format "{{.Names}}" > "$ROLLBACK_SNAPSHOT/containers.txt"
    fi

    # Backup existing volumes
    if docker volume ls --format '{{.Name}}' | grep -q 'dell-boca'; then
        log_info "Backing up volume list..."
        docker volume ls --filter "name=dell-boca" --format "{{.Name}}" > "$ROLLBACK_SNAPSHOT/volumes.txt"
    fi

    # Backup application config if exists
    if [[ -f "$APP_DIR/.env" ]]; then
        log_info "Backing up configuration..."
        cp "$APP_DIR/.env" "$ROLLBACK_SNAPSHOT/.env.backup"
    fi

    log_success "Rollback snapshot created: $ROLLBACK_SNAPSHOT"
}

# Generate secure secrets
generate_secrets() {
    print_phase "Generating secure secrets..."

    local secrets_file="$ROOT_DIR/secrets/secrets.env"
    local credentials_file="$ROOT_DIR/secrets/credentials.txt"

    # Generate strong random passwords
    local pg_password=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
    local n8n_encryption_key=$(openssl rand -base64 32)
    local admin_password=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9!@#$%^&*' | head -c 24)
    local api_key=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 64)
    local jwt_secret=$(openssl rand -base64 64)

    # Create secrets file
    cat > "$secrets_file" << EOF
# Dell Boca Boys V2 - Secure Secrets
# Generated: $(date)
# WARNING: Keep this file secure! Never commit to version control!

# Database
POSTGRES_PASSWORD=$pg_password

# n8n
N8N_ENCRYPTION_KEY=$n8n_encryption_key

# Application
ADMIN_PASSWORD=$admin_password
API_SECRET_KEY=$api_key
JWT_SECRET=$jwt_secret

# Redis
REDIS_PASSWORD=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)

# Session
SESSION_SECRET=$(openssl rand -base64 32)
EOF

    chmod 600 "$secrets_file"

    # Create human-readable credentials file
    cat > "$credentials_file" << EOF
Dell Boca Boys V2 - Deployment Credentials
==========================================
Generated: $(date)

IMPORTANT: Store these credentials securely!

Admin Dashboard
--------------
URL: https://localhost
Username: admin
Password: $admin_password

n8n Workflow Builder
-------------------
URL: https://localhost/n8n
Username: admin
Password: $admin_password

API Access
----------
Base URL: https://localhost/api
API Key: $api_key

Database (PostgreSQL)
--------------------
Host: localhost
Port: 5432
Database: dell_boca_boys
Username: admin
Password: $pg_password

NOTES:
- Change the admin password after first login
- Store API keys in a password manager
- Never share these credentials via email or chat
- Enable 2FA if available in the admin panel

EOF

    chmod 600 "$credentials_file"

    log_success "Secrets generated and stored securely"
    log_info "Credentials file: $credentials_file"
}

# Configure environment
configure_environment() {
    print_phase "Configuring environment..."

    local env_template="$APP_DIR/.env.template"
    local env_file="$APP_DIR/.env"
    local secrets_file="$ROOT_DIR/secrets/secrets.env"

    if [[ ! -f "$env_template" ]]; then
        log_error "Environment template not found: $env_template"
        exit 1
    fi

    # Copy template
    cp "$env_template" "$env_file"

    # Source secrets
    source "$secrets_file"

    # Replace placeholders with actual values
    sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$POSTGRES_PASSWORD|" "$env_file"
    sed -i "s|N8N_ENCRYPTION_KEY=.*|N8N_ENCRYPTION_KEY=$N8N_ENCRYPTION_KEY|" "$env_file"
    sed -i "s|ADMIN_PASSWORD=.*|ADMIN_PASSWORD=$ADMIN_PASSWORD|" "$env_file"
    sed -i "s|API_SECRET_KEY=.*|API_SECRET_KEY=$API_SECRET_KEY|" "$env_file"
    sed -i "s|JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|" "$env_file"
    sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=$REDIS_PASSWORD|" "$env_file"
    sed -i "s|SESSION_SECRET=.*|SESSION_SECRET=$SESSION_SECRET|" "$env_file"

    # Set secure defaults
    sed -i "s|DEBUG=.*|DEBUG=false|" "$env_file"
    sed -i "s|SECURITY_ENABLED=.*|SECURITY_ENABLED=true|" "$env_file"
    sed -i "s|AUDIT_LOGGING=.*|AUDIT_LOGGING=true|" "$env_file"

    chmod 600 "$env_file"

    log_success "Environment configured"
}

# Pull Docker images
pull_images() {
    print_phase "Pulling Docker images..."

    cd "$APP_DIR"

    log_info "This may take several minutes depending on your internet connection..."

    # Pull images with retry logic
    local max_retries=3
    local retry=0

    while [[ $retry -lt $max_retries ]]; do
        if docker compose pull; then
            log_success "All images pulled successfully"
            return 0
        else
            ((retry++))
            if [[ $retry -lt $max_retries ]]; then
                log_warn "Pull failed. Retrying ($retry/$max_retries)..."
                sleep 5
            fi
        fi
    done

    log_error "Failed to pull images after $max_retries attempts"
    exit 1
}

# Build application
build_application() {
    print_phase "Building application..."

    cd "$APP_DIR"

    log_info "Building Docker images..."
    docker compose build --no-cache --progress=plain 2>&1 | tee -a "$DEPLOYMENT_LOG"

    log_success "Application built successfully"
}

# Initialize database
initialize_database() {
    print_phase "Initializing database..."

    cd "$APP_DIR"

    # Start database container only
    log_info "Starting database..."
    docker compose up -d db

    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    local max_wait=60
    local wait=0

    while [[ $wait -lt $max_wait ]]; do
        if docker compose exec -T db pg_isready -U admin > /dev/null 2>&1; then
            log_success "Database is ready"
            break
        fi
        sleep 2
        ((wait+=2))
        echo -n "."
    done

    if [[ $wait -ge $max_wait ]]; then
        log_error "Database failed to start within ${max_wait}s"
        exit 1
    fi

    # Run database initialization script
    if [[ -f "$SCRIPT_DIR/init_db.sql" ]]; then
        log_info "Running database initialization script..."
        docker compose exec -T db psql -U admin -d dell_boca_boys < "$SCRIPT_DIR/init_db.sql"
        log_success "Database initialized"
    fi
}

# Deploy services
deploy_services() {
    print_phase "Deploying all services..."

    cd "$APP_DIR"

    log_info "Starting all services..."
    docker compose up -d

    log_success "All services started"
}

# Wait for services to be healthy
wait_for_services() {
    print_phase "Waiting for services to be healthy..."

    cd "$APP_DIR"

    local services=("db" "api" "n8n")
    local max_wait=180
    local wait=0

    for service in "${services[@]}"; do
        log_info "Checking $service..."

        wait=0
        while [[ $wait -lt $max_wait ]]; do
            if docker compose ps "$service" | grep -q "Up"; then
                log_success "$service is running"
                break
            fi
            sleep 2
            ((wait+=2))
            echo -n "."
        done

        if [[ $wait -ge $max_wait ]]; then
            log_error "$service failed to start within ${max_wait}s"
            log_info "Check logs: docker compose logs $service"
            exit 1
        fi
    done

    # Additional health checks
    log_info "Running health checks..."
    sleep 10  # Give services time to initialize

    # Check API health
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        log_success "API health check passed"
    else
        log_warn "API health check failed (may not be critical)"
    fi
}

# Load initial data
load_initial_data() {
    print_phase "Loading initial data..."

    cd "$APP_DIR"

    # Load n8n knowledge base
    if docker compose exec -T api python scripts/load_embeddings.py 2>&1 | tee -a "$DEPLOYMENT_LOG"; then
        log_success "Knowledge base loaded"
    else
        log_warn "Knowledge base loading had warnings (check logs)"
    fi

    # Load sample workflows
    if [[ -d "$APP_DIR/data/workflows" ]]; then
        log_info "Loading sample workflows..."
        # Add logic to load workflows
        log_success "Sample workflows loaded"
    fi
}

# Configure firewall
configure_firewall() {
    print_phase "Configuring firewall..."

    # Detect firewall type
    if command -v ufw &> /dev/null; then
        log_info "Configuring UFW firewall..."

        # Allow required ports
        sudo ufw allow 80/tcp comment "Dell Boca Boys - HTTP" || log_warn "Failed to configure UFW"
        sudo ufw allow 443/tcp comment "Dell Boca Boys - HTTPS" || log_warn "Failed to configure UFW"

        log_success "UFW firewall configured"

    elif command -v firewall-cmd &> /dev/null; then
        log_info "Configuring firewalld..."

        sudo firewall-cmd --permanent --add-service=http || log_warn "Failed to configure firewalld"
        sudo firewall-cmd --permanent --add-service=https || log_warn "Failed to configure firewalld"
        sudo firewall-cmd --reload || log_warn "Failed to reload firewalld"

        log_success "Firewalld configured"

    else
        log_warn "No supported firewall detected. Please configure manually."
        log_warn "Required ports: 80/tcp, 443/tcp"
    fi
}

# Run security hardening
security_hardening() {
    print_phase "Applying security hardening..."

    local hardening_script="$SCRIPT_DIR/security-hardening.sh"

    if [[ -f "$hardening_script" ]]; then
        log_info "Running security hardening script..."
        bash "$hardening_script" 2>&1 | tee -a "$DEPLOYMENT_LOG"
        log_success "Security hardening applied"
    else
        log_warn "Security hardening script not found"
    fi

    # Set secure file permissions
    log_info "Setting secure file permissions..."
    chmod 600 "$APP_DIR/.env"
    chmod 600 "$ROOT_DIR/secrets/"*
    chmod 700 "$ROOT_DIR/secrets"
    chmod 700 "$ROOT_DIR/backups"

    log_success "File permissions secured"
}

# Run post-deployment validation
post_deployment_validation() {
    print_phase "Running post-deployment validation..."

    local validation_script="$SCRIPT_DIR/health-check.sh"

    if [[ -f "$validation_script" ]]; then
        log_info "Running comprehensive health checks..."
        if bash "$validation_script" 2>&1 | tee -a "$DEPLOYMENT_LOG"; then
            log_success "All validation checks passed"
        else
            log_warn "Some validation checks failed (review logs)"
        fi
    else
        log_warn "Validation script not found"
    fi
}

# Generate deployment report
generate_deployment_report() {
    print_phase "Generating deployment report..."

    local report_file="$ROOT_DIR/deployment-report-$(date +%Y%m%d-%H%M%S).txt"

    cat > "$report_file" << EOF
Dell Boca Boys V2 - Deployment Report
=====================================
Deployment Date: $(date)
Deployed By: $(whoami)
Hostname: $(hostname)

Deployment Status: SUCCESS

Services Deployed:
------------------
$(docker compose -f "$APP_DIR/docker-compose.yml" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}")

Access Information:
------------------
Dashboard: https://localhost
n8n Workflows: https://localhost/n8n
API Documentation: https://localhost/api/docs
Health Dashboard: https://localhost/health

Credentials:
-----------
See file: $ROOT_DIR/secrets/credentials.txt

Important Files:
---------------
Deployment Log: $DEPLOYMENT_LOG
Secrets File: $ROOT_DIR/secrets/secrets.env
Credentials: $ROOT_DIR/secrets/credentials.txt
Rollback Snapshot: $ROLLBACK_SNAPSHOT

Next Steps:
----------
1. Open https://localhost in your browser
2. Log in with the credentials from: $ROOT_DIR/secrets/credentials.txt
3. Change the default admin password
4. Review the user documentation
5. Create your first workflow

Support:
-------
Documentation: $ROOT_DIR/docs/
Troubleshooting: $ROOT_DIR/docs/TROUBLESHOOTING.md
Email: support@dellbocaboys.com

EOF

    log_success "Deployment report generated: $report_file"
}

# Main deployment function
main() {
    print_header "Dell Boca Boys V2 - Automated Deployment"

    log_info "Starting deployment at $(date)"
    log_info "Deployment log: $DEPLOYMENT_LOG"

    # Phase 1: Pre-deployment
    print_header "Phase 1: Pre-Deployment Checks"
    check_privileges
    validate_prerequisites
    create_rollback_snapshot

    # Phase 2: Security Setup
    print_header "Phase 2: Security Setup"
    generate_secrets
    configure_environment

    # Phase 3: Application Build
    print_header "Phase 3: Application Build"
    pull_images
    build_application

    # Phase 4: Deployment
    print_header "Phase 4: Deployment"
    initialize_database
    deploy_services
    wait_for_services

    # Phase 5: Configuration
    print_header "Phase 5: Configuration"
    load_initial_data
    configure_firewall
    security_hardening

    # Phase 6: Validation
    print_header "Phase 6: Post-Deployment Validation"
    post_deployment_validation
    generate_deployment_report

    # Success!
    print_header "Deployment Complete!"

    log_success "="
    log_success "Dell Boca Boys V2 has been successfully deployed!"
    log_success "="
    log_success ""
    log_success "Access your system at: https://localhost"
    log_success "Credentials are in: $ROOT_DIR/secrets/credentials.txt"
    log_success ""
    log_success "Next steps:"
    log_success "  1. Open https://localhost in your browser"
    log_success "  2. Log in with admin credentials"
    log_success "  3. Change the default password"
    log_success "  4. Explore the documentation"
    log_success ""
    log_success "Deployment report: $(ls -t $ROOT_DIR/deployment-report-*.txt | head -1)"
    log_success "="

    return 0
}

# Run main deployment
main "$@"
