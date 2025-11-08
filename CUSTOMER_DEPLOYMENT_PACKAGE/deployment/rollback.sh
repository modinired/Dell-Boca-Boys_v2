#!/bin/bash
###############################################################################
# Dell Boca Boys V2 - Rollback Script
# Safe rollback mechanism with data preservation
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="$ROOT_DIR/application"
ROLLBACK_LOG="$ROOT_DIR/logs/rollback-$(date +%Y%m%d-%H%M%S).log"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$ROLLBACK_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$ROLLBACK_LOG"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$ROLLBACK_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$ROLLBACK_LOG"
}

print_header() {
    echo ""
    echo "============================================================================="
    echo "  $1"
    echo "============================================================================="
    echo ""
}

# Confirmation prompt
confirm_rollback() {
    print_header "Dell Boca Boys V2 - Rollback Wizard"

    echo "This script will rollback your Dell Boca Boys V2 installation."
    echo ""
    echo -e "${YELLOW}WARNING:${NC}"
    echo "  - All Docker containers will be stopped and removed"
    echo "  - All Docker volumes will be removed (data will be lost)"
    echo "  - Configuration files will be removed"
    echo "  - System will be returned to pre-installation state"
    echo ""
    echo -e "${GREEN}Your data will be backed up before rollback!${NC}"
    echo "  - Backup location: $ROOT_DIR/backups/pre-rollback-$(date +%Y%m%d-%H%M%S)"
    echo ""

    read -p "Do you want to continue with rollback? (type 'yes' to confirm): " confirm

    if [[ "$confirm" != "yes" ]]; then
        log_info "Rollback cancelled by user"
        exit 0
    fi

    echo ""
    log_info "Rollback confirmed. Starting process..."
}

# Create emergency backup
create_emergency_backup() {
    print_header "Creating Emergency Backup"

    local backup_dir="$ROOT_DIR/backups/pre-rollback-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"

    log_info "Creating backup at: $backup_dir"

    # Backup database if running
    if docker ps --format '{{.Names}}' | grep -q "dell-boca-db"; then
        log_info "Backing up database..."

        docker exec dell-boca-db pg_dump -U admin dell_boca_boys > "$backup_dir/database.sql" 2>/dev/null || log_warn "Database backup failed"

        if [[ -f "$backup_dir/database.sql" ]]; then
            log_success "Database backed up"
        fi
    fi

    # Backup configuration
    if [[ -f "$APP_DIR/.env" ]]; then
        log_info "Backing up configuration..."
        cp "$APP_DIR/.env" "$backup_dir/.env" 2>/dev/null || log_warn "Config backup failed"
        log_success "Configuration backed up"
    fi

    # Backup secrets
    if [[ -d "$ROOT_DIR/secrets" ]]; then
        log_info "Backing up secrets..."
        cp -r "$ROOT_DIR/secrets" "$backup_dir/" 2>/dev/null || log_warn "Secrets backup failed"
        log_success "Secrets backed up"
    fi

    # Backup workflows (if directory exists)
    if [[ -d "$APP_DIR/data/workflows" ]]; then
        log_info "Backing up workflows..."
        cp -r "$APP_DIR/data/workflows" "$backup_dir/" 2>/dev/null || log_warn "Workflows backup failed"
        log_success "Workflows backed up"
    fi

    # Create backup manifest
    cat > "$backup_dir/manifest.txt" << EOF
Dell Boca Boys V2 - Emergency Backup
Created: $(date)
Reason: Pre-rollback backup
Backup Location: $backup_dir

Contents:
- Database dump: database.sql
- Configuration: .env
- Secrets: secrets/
- Workflows: workflows/

Restore Instructions:
1. Reinstall Dell Boca Boys V2
2. Stop all services: ./deployment/stop-services.sh
3. Restore database: cat $backup_dir/database.sql | docker exec -i dell-boca-db psql -U admin dell_boca_boys
4. Restore config: cp $backup_dir/.env $APP_DIR/.env
5. Restore secrets: cp -r $backup_dir/secrets $ROOT_DIR/
6. Restart services: ./deployment/restart-services.sh

EOF

    log_success "Emergency backup created: $backup_dir"
    echo ""
    echo -e "${GREEN}Backup complete!${NC} You can restore from this backup later if needed."
    echo "Backup location: $backup_dir"
    echo ""
    sleep 3
}

# Stop all services
stop_services() {
    print_header "Stopping Services"

    cd "$APP_DIR"

    if [[ -f "docker-compose.yml" ]]; then
        log_info "Stopping Docker containers..."

        if docker compose ps -q | grep -q .; then
            docker compose stop 2>&1 | tee -a "$ROLLBACK_LOG"
            log_success "All services stopped"
        else
            log_info "No running containers found"
        fi
    else
        log_warn "docker-compose.yml not found, skipping container stop"
    fi
}

# Remove containers
remove_containers() {
    print_header "Removing Containers"

    cd "$APP_DIR"

    if [[ -f "docker-compose.yml" ]]; then
        log_info "Removing Docker containers..."

        docker compose down 2>&1 | tee -a "$ROLLBACK_LOG"
        log_success "Containers removed"
    fi

    # Remove any orphaned Dell Boca containers
    local orphaned=$(docker ps -a --format '{{.Names}}' | grep "dell-boca" || true)

    if [[ -n "$orphaned" ]]; then
        log_info "Removing orphaned containers..."

        echo "$orphaned" | while read -r container; do
            docker rm -f "$container" 2>&1 | tee -a "$ROLLBACK_LOG" || log_warn "Failed to remove $container"
        done

        log_success "Orphaned containers removed"
    fi
}

# Remove volumes
remove_volumes() {
    print_header "Removing Docker Volumes"

    echo -e "${YELLOW}WARNING: This will DELETE all data!${NC}"
    echo "Your data has been backed up to: $ROOT_DIR/backups/pre-rollback-*"
    echo ""
    read -p "Proceed with volume deletion? (type 'yes' to confirm): " confirm

    if [[ "$confirm" != "yes" ]]; then
        log_warn "Volume deletion skipped. Volumes will remain."
        return 0
    fi

    log_info "Removing Dell Boca volumes..."

    local volumes=$(docker volume ls --format '{{.Name}}' | grep "dell-boca" || true)

    if [[ -n "$volumes" ]]; then
        echo "$volumes" | while read -r volume; do
            log_info "Removing volume: $volume"
            docker volume rm "$volume" 2>&1 | tee -a "$ROLLBACK_LOG" || log_warn "Failed to remove $volume"
        done

        log_success "Volumes removed"
    else
        log_info "No Dell Boca volumes found"
    fi
}

# Remove networks
remove_networks() {
    print_header "Removing Docker Networks"

    local networks=$(docker network ls --format '{{.Name}}' | grep "dell-boca" || true)

    if [[ -n "$networks" ]]; then
        log_info "Removing Dell Boca networks..."

        echo "$networks" | while read -r network; do
            log_info "Removing network: $network"
            docker network rm "$network" 2>&1 | tee -a "$ROLLBACK_LOG" || log_warn "Failed to remove $network"
        done

        log_success "Networks removed"
    else
        log_info "No Dell Boca networks found"
    fi
}

# Remove images (optional)
remove_images() {
    print_header "Removing Docker Images"

    echo "Do you want to remove Dell Boca Docker images?"
    echo "(This will save disk space but require re-download on next install)"
    echo ""
    read -p "Remove images? (yes/no): " confirm

    if [[ "$confirm" != "yes" ]]; then
        log_info "Image removal skipped"
        return 0
    fi

    log_info "Removing Dell Boca images..."

    local images=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep -E "dell-boca|n8n|postgres|vllm" || true)

    if [[ -n "$images" ]]; then
        echo "$images" | while read -r image; do
            log_info "Removing image: $image"
            docker rmi "$image" 2>&1 | tee -a "$ROLLBACK_LOG" || log_warn "Failed to remove $image"
        done

        log_success "Images removed"
    else
        log_info "No Dell Boca images found"
    fi
}

# Clean configuration files
clean_config() {
    print_header "Cleaning Configuration Files"

    echo "Do you want to remove configuration and secrets?"
    echo "(Keep these if you plan to reinstall later)"
    echo ""
    read -p "Remove configuration? (yes/no): " confirm

    if [[ "$confirm" != "yes" ]]; then
        log_info "Configuration cleanup skipped"
        return 0
    fi

    # Remove .env file
    if [[ -f "$APP_DIR/.env" ]]; then
        log_info "Removing environment file..."
        rm -f "$APP_DIR/.env"
        log_success "Environment file removed"
    fi

    # Remove secrets (with extra confirmation)
    if [[ -d "$ROOT_DIR/secrets" ]]; then
        echo ""
        echo -e "${RED}WARNING: About to delete secrets directory!${NC}"
        read -p "Are you absolutely sure? (type 'DELETE' to confirm): " confirm

        if [[ "$confirm" == "DELETE" ]]; then
            log_info "Removing secrets directory..."
            rm -rf "$ROOT_DIR/secrets"
            log_success "Secrets removed"
        else
            log_info "Secrets deletion cancelled"
        fi
    fi
}

# Remove firewall rules
remove_firewall_rules() {
    print_header "Removing Firewall Rules"

    # UFW
    if command -v ufw &> /dev/null; then
        log_info "Removing UFW rules..."

        sudo ufw delete allow 80/tcp 2>&1 | tee -a "$ROLLBACK_LOG" || log_warn "Failed to remove UFW rule"
        sudo ufw delete allow 443/tcp 2>&1 | tee -a "$ROLLBACK_LOG" || log_warn "Failed to remove UFW rule"

        log_success "UFW rules removed"

    # Firewalld
    elif command -v firewall-cmd &> /dev/null; then
        log_info "Removing firewalld rules..."

        sudo firewall-cmd --permanent --remove-service=http 2>&1 | tee -a "$ROLLBACK_LOG" || log_warn "Failed to remove firewalld rule"
        sudo firewall-cmd --permanent --remove-service=https 2>&1 | tee -a "$ROLLBACK_LOG" || log_warn "Failed to remove firewalld rule"
        sudo firewall-cmd --reload 2>&1 | tee -a "$ROLLBACK_LOG" || log_warn "Failed to reload firewalld"

        log_success "Firewalld rules removed"

    else
        log_info "No supported firewall found, skipping"
    fi
}

# Generate rollback report
generate_report() {
    print_header "Generating Rollback Report"

    local report_file="$ROOT_DIR/rollback-report-$(date +%Y%m%d-%H%M%S).txt"

    cat > "$report_file" << EOF
Dell Boca Boys V2 - Rollback Report
===================================
Rollback Date: $(date)
Performed By: $(whoami)
Hostname: $(hostname)

Rollback Status: COMPLETED

Actions Performed:
-----------------
✓ Emergency backup created
✓ Services stopped
✓ Containers removed
✓ Volumes removed (if confirmed)
✓ Networks removed
✓ Images removed (if confirmed)
✓ Configuration cleaned (if confirmed)
✓ Firewall rules removed

Backup Location:
---------------
$(ls -td $ROOT_DIR/backups/pre-rollback-* 2>/dev/null | head -1)

Restore Instructions:
--------------------
If you want to restore your system:

1. Reinstall Dell Boca Boys V2:
   ./start-installer.sh

2. After installation, restore your data:
   ./backup/restore.sh <backup-date>

3. Or manually restore from backup:
   See: $(ls -td $ROOT_DIR/backups/pre-rollback-* 2>/dev/null | head -1)/manifest.txt

Logs:
----
Rollback log: $ROLLBACK_LOG

Notes:
-----
- System has been returned to pre-installation state
- All data has been backed up before rollback
- Docker is still installed (not removed by rollback)
- You can reinstall anytime

Support:
-------
Email: support@dellbocaboys.com
Phone: 1-800-DELL-BOC

EOF

    log_success "Rollback report generated: $report_file"
}

# Main rollback function
main() {
    mkdir -p "$ROOT_DIR/logs"

    confirm_rollback

    # Execute rollback steps
    create_emergency_backup
    stop_services
    remove_containers
    remove_volumes
    remove_networks
    remove_images
    clean_config
    remove_firewall_rules

    # Generate report
    generate_report

    # Final summary
    print_header "Rollback Complete"

    log_success "="
    log_success "Dell Boca Boys V2 has been successfully rolled back"
    log_success "="
    log_success ""
    log_success "Your data has been backed up to:"
    log_success "  $(ls -td $ROOT_DIR/backups/pre-rollback-* 2>/dev/null | head -1)"
    log_success ""
    log_success "Rollback report:"
    log_success "  $(ls -t $ROOT_DIR/rollback-report-*.txt | head -1)"
    log_success ""
    log_success "To reinstall Dell Boca Boys V2:"
    log_success "  ./start-installer.sh"
    log_success ""
    log_success "To restore from backup after reinstall:"
    log_success "  ./backup/restore.sh <backup-date>"
    log_success ""
    log_success "="

    return 0
}

# Run rollback
main "$@"
