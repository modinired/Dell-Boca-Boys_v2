#!/bin/bash
###############################################################################
# Dell Boca Boys V2 - Comprehensive Health Check System
# Production-ready health monitoring with detailed diagnostics
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
HEALTH_LOG="$ROOT_DIR/logs/health-check-$(date +%Y%m%d-%H%M%S).log"

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Health check results
declare -a FAILED_ITEMS=()
declare -a WARNING_ITEMS=()

# Logging
log_check() {
    local status=$1
    local name=$2
    local details=$3

    ((TOTAL_CHECKS++))

    case $status in
        "PASS")
            ((PASSED_CHECKS++))
            echo -e "${GREEN}✓ PASS${NC} - $name" | tee -a "$HEALTH_LOG"
            ;;
        "WARN")
            ((WARNING_CHECKS++))
            echo -e "${YELLOW}⚠ WARN${NC} - $name: $details" | tee -a "$HEALTH_LOG"
            WARNING_ITEMS+=("$name: $details")
            ;;
        "FAIL")
            ((FAILED_CHECKS++))
            echo -e "${RED}✗ FAIL${NC} - $name: $details" | tee -a "$HEALTH_LOG"
            FAILED_ITEMS+=("$name: $details")
            ;;
    esac
}

print_header() {
    echo ""
    echo "============================================================================="
    echo "  $1"
    echo "============================================================================="
    echo ""
}

# Health check functions

check_docker_running() {
    if docker info > /dev/null 2>&1; then
        log_check "PASS" "Docker daemon is running" ""
        return 0
    else
        log_check "FAIL" "Docker daemon" "Docker is not running"
        return 1
    fi
}

check_containers() {
    cd "$APP_DIR"

    # Expected containers
    local containers=("db" "api" "n8n" "vllm")

    for container in "${containers[@]}"; do
        local full_name="dell-boca-${container}"

        if docker ps --format '{{.Names}}' | grep -q "$full_name"; then
            # Check if healthy
            local status=$(docker inspect --format='{{.State.Health.Status}}' "$full_name" 2>/dev/null || echo "no-healthcheck")

            if [[ "$status" == "healthy" || "$status" == "no-healthcheck" ]]; then
                log_check "PASS" "Container $container is running" ""
            else
                log_check "WARN" "Container $container" "Status: $status"
            fi
        else
            log_check "FAIL" "Container $container" "Not running"
        fi
    done
}

check_container_health() {
    cd "$APP_DIR"

    # Check container resource usage
    local stats=$(docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | tail -n +2)

    while IFS= read -r line; do
        local name=$(echo "$line" | awk '{print $1}')
        local cpu=$(echo "$line" | awk '{print $2}' | sed 's/%//')
        local mem=$(echo "$line" | awk '{print $3}')

        # Check CPU usage
        if (( $(echo "$cpu > 90" | bc -l) )); then
            log_check "WARN" "High CPU usage on $name" "CPU: ${cpu}%"
        fi

        # Memory usage (simplified check)
        log_check "PASS" "Resource usage for $name" "CPU: ${cpu}%, Memory: $mem"
    done <<< "$stats"
}

check_database() {
    cd "$APP_DIR"

    # Check database connectivity
    if docker compose exec -T db pg_isready -U admin > /dev/null 2>&1; then
        log_check "PASS" "Database connectivity" ""

        # Check database size
        local db_size=$(docker compose exec -T db psql -U admin -d dell_boca_boys -t -c "SELECT pg_size_pretty(pg_database_size('dell_boca_boys'));" 2>/dev/null | tr -d ' ')

        if [[ -n "$db_size" ]]; then
            log_check "PASS" "Database size" "$db_size"
        fi

        # Check table counts
        local table_count=$(docker compose exec -T db psql -U admin -d dell_boca_boys -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

        if [[ "$table_count" -gt 0 ]]; then
            log_check "PASS" "Database tables" "$table_count tables found"
        else
            log_check "WARN" "Database tables" "No tables found"
        fi

    else
        log_check "FAIL" "Database connectivity" "Cannot connect to database"
    fi
}

check_api_health() {
    # Check API endpoint
    local api_url="http://localhost:8080/health"

    if curl -f -s "$api_url" > /dev/null 2>&1; then
        local response=$(curl -s "$api_url")
        log_check "PASS" "API health endpoint" "Response: $response"
    else
        log_check "FAIL" "API health endpoint" "API not responding at $api_url"
    fi

    # Check API documentation
    if curl -f -s "http://localhost:8080/api/docs" > /dev/null 2>&1; then
        log_check "PASS" "API documentation" "Available"
    else
        log_check "WARN" "API documentation" "Not accessible"
    fi
}

check_n8n_health() {
    # Check n8n web interface
    if curl -f -s "http://localhost:5678" > /dev/null 2>&1; then
        log_check "PASS" "n8n web interface" "Accessible"
    else
        log_check "FAIL" "n8n web interface" "Not accessible at http://localhost:5678"
    fi
}

check_disk_space() {
    local threshold_percent=80
    local usage=$(df -h "$ROOT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')

    if [[ $usage -gt $threshold_percent ]]; then
        log_check "WARN" "Disk space" "${usage}% used (threshold: ${threshold_percent}%)"
    else
        log_check "PASS" "Disk space" "${usage}% used"
    fi
}

check_memory() {
    local mem_used_percent=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    local threshold=85

    if [[ $mem_used_percent -gt $threshold ]]; then
        log_check "WARN" "Memory usage" "${mem_used_percent}% used (threshold: ${threshold}%)"
    else
        log_check "PASS" "Memory usage" "${mem_used_percent}% used"
    fi
}

check_cpu_load() {
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    local cpu_count=$(nproc)
    local load_per_cpu=$(echo "scale=2; $load_avg / $cpu_count" | bc)

    if (( $(echo "$load_per_cpu > 2.0" | bc -l) )); then
        log_check "WARN" "CPU load" "Load: $load_avg (${load_per_cpu} per CPU)"
    else
        log_check "PASS" "CPU load" "Load: $load_avg"
    fi
}

check_docker_volumes() {
    cd "$APP_DIR"

    # Check if volumes exist
    local volumes=$(docker volume ls --filter "name=dell-boca" --format "{{.Name}}")

    if [[ -n "$volumes" ]]; then
        local volume_count=$(echo "$volumes" | wc -l)
        log_check "PASS" "Docker volumes" "$volume_count volumes found"

        # Check volume sizes
        while IFS= read -r volume; do
            if docker volume inspect "$volume" > /dev/null 2>&1; then
                log_check "PASS" "Volume $volume" "Exists"
            fi
        done <<< "$volumes"
    else
        log_check "WARN" "Docker volumes" "No Dell Boca volumes found"
    fi
}

check_docker_networks() {
    cd "$APP_DIR"

    # Check if network exists
    if docker network ls --format "{{.Name}}" | grep -q "dell-boca"; then
        log_check "PASS" "Docker network" "Dell Boca network exists"
    else
        log_check "WARN" "Docker network" "Dell Boca network not found"
    fi
}

check_logs() {
    # Check if logs directory exists and has recent logs
    if [[ -d "$ROOT_DIR/logs" ]]; then
        local log_count=$(find "$ROOT_DIR/logs" -type f -name "*.log" | wc -l)

        if [[ $log_count -gt 0 ]]; then
            log_check "PASS" "Log files" "$log_count log files found"
        else
            log_check "WARN" "Log files" "No log files found"
        fi
    else
        log_check "WARN" "Logs directory" "Directory not found"
    fi
}

check_backups() {
    # Check if backups exist
    if [[ -d "$ROOT_DIR/backups" ]]; then
        local backup_count=$(find "$ROOT_DIR/backups" -type d -name "202*" | wc -l)

        if [[ $backup_count -gt 0 ]]; then
            local latest_backup=$(find "$ROOT_DIR/backups" -type d -name "202*" | sort -r | head -1)
            local backup_age_days=$(( ( $(date +%s) - $(stat -c %Y "$latest_backup" 2>/dev/null || echo 0) ) / 86400 ))

            if [[ $backup_age_days -le 1 ]]; then
                log_check "PASS" "Recent backups" "Latest backup: $(basename $latest_backup)"
            else
                log_check "WARN" "Recent backups" "Latest backup is $backup_age_days days old"
            fi
        else
            log_check "WARN" "Backups" "No backups found"
        fi
    else
        log_check "WARN" "Backup directory" "Directory not found"
    fi
}

check_security() {
    # Check file permissions
    if [[ -f "$APP_DIR/.env" ]]; then
        local env_perms=$(stat -c %a "$APP_DIR/.env" 2>/dev/null || echo "000")

        if [[ "$env_perms" == "600" || "$env_perms" == "400" ]]; then
            log_check "PASS" "Environment file permissions" "Secure ($env_perms)"
        else
            log_check "WARN" "Environment file permissions" "Insecure ($env_perms), should be 600"
        fi
    fi

    # Check secrets directory permissions
    if [[ -d "$ROOT_DIR/secrets" ]]; then
        local secrets_perms=$(stat -c %a "$ROOT_DIR/secrets" 2>/dev/null || echo "000")

        if [[ "$secrets_perms" == "700" || "$secrets_perms" == "500" ]]; then
            log_check "PASS" "Secrets directory permissions" "Secure ($secrets_perms)"
        else
            log_check "WARN" "Secrets directory permissions" "Insecure ($secrets_perms), should be 700"
        fi
    fi
}

check_ports() {
    # Check if required ports are listening
    local ports=(80 443 5678 5432 8000 8080)

    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_check "PASS" "Port $port" "Listening"
        else
            log_check "WARN" "Port $port" "Not listening"
        fi
    done
}

check_ai_model() {
    cd "$APP_DIR"

    # Check if vLLM container is running and responding
    if docker ps --format '{{.Names}}' | grep -q "vllm"; then
        # Try to query the model (simplified check)
        if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
            log_check "PASS" "AI model (vLLM)" "Running and healthy"
        else
            log_check "WARN" "AI model (vLLM)" "Running but health check failed"
        fi
    else
        log_check "WARN" "AI model (vLLM)" "Not running (may be in CPU mode)"
    fi
}

# Generate summary report
generate_summary() {
    print_header "Health Check Summary"

    local total_percent=$(( PASSED_CHECKS * 100 / TOTAL_CHECKS ))

    echo "Total Checks: $TOTAL_CHECKS"
    echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "Warnings: ${YELLOW}$WARNING_CHECKS${NC}"
    echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
    echo ""
    echo -e "Overall Health: ${total_percent}%"

    if [[ $FAILED_CHECKS -gt 0 ]]; then
        echo ""
        echo -e "${RED}Failed Checks:${NC}"
        for item in "${FAILED_ITEMS[@]}"; do
            echo "  - $item"
        done
    fi

    if [[ $WARNING_CHECKS -gt 0 ]]; then
        echo ""
        echo -e "${YELLOW}Warnings:${NC}"
        for item in "${WARNING_ITEMS[@]}"; do
            echo "  - $item"
        done
    fi

    # Overall status
    echo ""
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        if [[ $WARNING_CHECKS -eq 0 ]]; then
            echo -e "${GREEN}✓ System is HEALTHY${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ System is functional with WARNINGS${NC}"
            return 0
        fi
    else
        echo -e "${RED}✗ System has CRITICAL ISSUES${NC}"
        return 1
    fi
}

# Main execution
main() {
    mkdir -p "$ROOT_DIR/logs"

    print_header "Dell Boca Boys V2 - Health Check"

    echo "Starting comprehensive health check..."
    echo "Log file: $HEALTH_LOG"
    echo ""

    # Infrastructure checks
    print_header "Infrastructure Health"
    check_docker_running
    check_disk_space
    check_memory
    check_cpu_load

    # Container checks
    print_header "Container Health"
    check_containers
    check_container_health

    # Service checks
    print_header "Service Health"
    check_database
    check_api_health
    check_n8n_health
    check_ai_model

    # Network checks
    print_header "Network Health"
    check_docker_networks
    check_ports

    # Storage checks
    print_header "Storage Health"
    check_docker_volumes
    check_backups

    # Security checks
    print_header "Security Health"
    check_security

    # Operational checks
    print_header "Operational Health"
    check_logs

    # Generate summary
    generate_summary

    exit_code=$?

    echo ""
    echo "Detailed log saved to: $HEALTH_LOG"

    return $exit_code
}

# Run health checks
main "$@"
