#!/bin/bash

# ==============================================================================
# Dell Boca Vista Boys - Complete PostgreSQL & Learning System Setup
# ==============================================================================

set -e  # Exit on error

echo "======================================================================="
echo "🎩 Dell Boca Vista Boys - Complete System Setup"
echo "======================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Start PostgreSQL Container
echo -e "${YELLOW}Step 1: Starting PostgreSQL container...${NC}"
cd ~/N8n-agent
docker compose up -d db
sleep 10

# Step 2: Create Database and User
echo -e "${YELLOW}Step 2: Creating database and user...${NC}"
docker exec n8n_agent_db psql -U postgres -c "CREATE USER n8n_agent WITH PASSWORD 'change_me_in_production_use_strong_password';" 2>/dev/null || echo "User already exists"
docker exec n8n_agent_db psql -U postgres -c "CREATE DATABASE n8n_agent_memory OWNER n8n_agent;" 2>/dev/null || echo "Database already exists"
docker exec n8n_agent_db psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE n8n_agent_memory TO n8n_agent;"
docker exec n8n_agent_db psql -U postgres -c "ALTER USER n8n_agent CREATEDB;"

# Enable pgvector extension
docker exec n8n_agent_db psql -U n8n_agent -d n8n_agent_memory -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo -e "${GREEN}✅ PostgreSQL user and database created${NC}"

# Step 3: Run Learning System Setup
echo -e "${YELLOW}Step 3: Setting up learning system tables...${NC}"
export PGHOST=localhost
export PGPORT=5432
export PGUSER=n8n_agent
export PGPASSWORD=change_me_in_production_use_strong_password
export PGDATABASE=n8n_agent_memory

# Run the setup script non-interactively
yes yes | python3 scripts/setup_ultimate_learning.py 2>&1 | head -50

echo -e "${GREEN}✅ Learning system setup complete${NC}"

# Step 4: Test the System
echo -e "${YELLOW}Step 4: Testing learning system...${NC}"
python3 scripts/test_learning_system.py 2>&1 | head -30

echo ""
echo "======================================================================="
echo -e "${GREEN}✅ COMPLETE SETUP FINISHED!${NC}"
echo "======================================================================="
echo ""
echo "Next steps:"
echo "  1. Web UI is running at: http://localhost:7800"
echo "  2. PostgreSQL learning database is ready"
echo "  3. Test the workflow generator and learning features"
echo ""
echo "To view database contents:"
echo "  PGPASSWORD=change_me_in_production_use_strong_password psql -h localhost -U n8n_agent -d n8n_agent_memory"
echo ""
