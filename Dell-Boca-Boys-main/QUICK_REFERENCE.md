# n8n Autonomous Agent - Quick Reference

## 🚀 Installation (One Command)
```bash
tar -xzf n8n-autonomous-agent.tar.gz && cd n8n-agent && cp .env.example .env && chmod +x scripts/build.sh && ./scripts/build.sh
```
**Don't forget:** Edit `.env` and set `N8N_API_TOKEN` before running build.sh

## 📍 Service URLs
| Service | URL | Purpose |
|---------|-----|---------|
| n8n UI | http://localhost:5678 | Workflow editor |
| API | http://localhost:8080 | Agent API |
| API Docs | http://localhost:8080/docs | Swagger UI |
| LLM | http://localhost:8000 | vLLM server |
| PostgreSQL | localhost:5432 | Database |

## 🎯 Common Commands

### Start/Stop
```bash
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose restart api        # Restart specific service
docker-compose ps                 # Check status
```

### Logs
```bash
docker-compose logs -f            # All logs (follow)
docker-compose logs -f api        # API logs only
docker-compose logs --tail=100 api # Last 100 lines
```

### Create Workflow
```bash
curl -X POST http://localhost:8080/api/v1/workflow/design \
  -H 'Content-Type: application/json' \
  -d '{"user_goal":"YOUR WORKFLOW DESCRIPTION"}' | jq .
```

### Database Access
```bash
docker-compose exec db psql -U n8n_agent -d n8n_agent_memory
```

### Common SQL Queries
```sql
-- View all workflows
SELECT id, name, status, created_at FROM workflows ORDER BY created_at DESC;

-- Check knowledge base
SELECT source, COUNT(*) as count FROM documents GROUP BY source;

-- View recent audit events
SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 20;

-- Workflow statistics
SELECT * FROM agent_workflow_statistics;
```

### Knowledge Base Management
```bash
# Load n8n manual
docker-compose exec api python scripts/load_embeddings.py

# Crawl templates
docker-compose exec api python scripts/crawl_templates.py --max-pages 50

# Crawl documentation
docker-compose exec api python scripts/crawl_docs.py

# Search knowledge base
curl -X GET "http://localhost:8080/api/v1/knowledge/search?q=error+handling&k=5" | jq .
```

### Health Checks
```bash
# All services
curl http://localhost:8080/health | jq .

# Individual services
curl http://localhost:5678/healthz          # n8n
curl http://localhost:8000/health           # vLLM
docker-compose exec db pg_isready           # PostgreSQL
docker-compose exec redis redis-cli ping    # Redis
```

### Testing
```bash
# Run tests
docker-compose exec api pytest app/tests/ -v

# Specific test
docker-compose exec api pytest app/tests/test_validator.py -v

# With coverage
docker-compose exec api pytest app/tests/ --cov=app --cov-report=html
```

## 🔧 Configuration Quick Edits

### Change LLM Temperature
```bash
# Edit .env
LLM_TEMPERATURE=0.1    # More deterministic
LLM_TEMPERATURE=0.7    # More creative

# Restart
docker-compose restart api
```

### Adjust Crawler Rate
```bash
# Edit .env
CRAWL_RATE_LIMIT_PER_SEC=0.5    # Slower (polite)
CRAWL_RATE_LIMIT_PER_SEC=2.0    # Faster

# Restart
docker-compose restart api
```

### Enable Debug Mode
```bash
# Edit .env
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG

# Restart
docker-compose restart api
```

## 🐛 Troubleshooting Quick Fixes

### Service Won't Start
```bash
docker-compose down
docker-compose up -d
docker-compose logs -f [service_name]
```

### Out of Disk Space
```bash
# Clean Docker
docker system prune -a --volumes

# Check space
df -h
docker system df
```

### Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d db
sleep 10
docker-compose up -d
```

### n8n Token Invalid
1. Visit: http://localhost:5678
2. Settings → Personal Access Tokens → Create
3. Copy token to `.env` as `N8N_API_TOKEN`
4. `docker-compose restart api`

### vLLM Out of Memory
```yaml
# Edit docker-compose.yml, change:
--gpu-memory-utilization 0.90
# To:
--gpu-memory-utilization 0.70

# Then restart:
docker-compose restart vllm
```

## 📊 Monitoring Quick Checks

### System Resources
```bash
docker stats                      # Real-time resource usage
nvidia-smi                        # GPU stats (if using GPU)
docker-compose top                # Process list
```

### Database Statistics
```sql
-- Connection count
SELECT count(*) FROM pg_stat_activity;

-- Database size
SELECT pg_size_pretty(pg_database_size('n8n_agent_memory'));

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### API Performance
```bash
# Response time test
time curl -X GET http://localhost:8080/health

# Load test (install ab first)
ab -n 100 -c 10 http://localhost:8080/health
```

## 🔐 Security Quick Checks

### Verify Credentials
```bash
# Check credential aliases in n8n
curl -H "Authorization: Bearer $N8N_API_TOKEN" \
  http://localhost:5678/rest/credentials | jq .

# Verify no raw credentials in workflows
docker-compose exec db psql -U n8n_agent -d n8n_agent_memory -c \
  "SELECT id, name FROM workflows WHERE workflow_json::text LIKE '%password%';"
```

### Audit Recent Activity
```sql
SELECT event_type, event_category, created_at, details 
FROM audit_log 
ORDER BY created_at DESC 
LIMIT 20;
```

## 📦 Backup & Restore

### Backup Database
```bash
docker-compose exec db pg_dump -U n8n_agent n8n_agent_memory > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
cat backup_20250101.sql | docker-compose exec -T db psql -U n8n_agent n8n_agent_memory
```

### Backup n8n Data
```bash
docker run --rm --volumes-from n8n_agent_n8n -v $(pwd):/backup ubuntu tar czf /backup/n8n_backup_$(date +%Y%m%d).tar.gz /home/node/.n8n
```

## 🚀 Production Deployment

### Pre-Production Checklist
```bash
# 1. Set strong passwords
sed -i 's/change_me_in_production.*/YOUR_STRONG_PASSWORD/' .env

# 2. Disable debug
sed -i 's/APP_DEBUG=true/APP_DEBUG=false/' .env

# 3. Run build with production flag
./scripts/build.sh --prod

# 4. Verify security settings
docker-compose exec api python -c "from app.settings import settings; print(f'Debug: {settings.app_debug}, Env: {settings.app_env}')"
```

### Update to Latest
```bash
# Pull latest images
docker-compose pull

# Rebuild API
docker-compose build --no-cache api

# Restart
docker-compose down && docker-compose up -d
```

## 💡 Pro Tips

1. **Monitor GPU Usage**: `watch -n 1 nvidia-smi` in separate terminal
2. **Pretty Logs**: `docker-compose logs -f api | jq -R 'fromjson?'`
3. **Quick Test**: Keep `curl` command in shell history for fast testing
4. **Backup Regularly**: Add cron job for automated database backups
5. **Log Rotation**: Configure Docker log rotation in `/etc/docker/daemon.json`

## 📞 Need Help?

1. Check logs: `docker-compose logs -f`
2. Enable debug: `APP_DEBUG=true` in `.env`
3. Review DEPLOYMENT_GUIDE.md for detailed troubleshooting
4. Check Docker status: `docker-compose ps`
5. Verify .env configuration

---

**Quick Start**: `./scripts/build.sh`  
**Stop All**: `docker-compose down`  
**View Logs**: `docker-compose logs -f api`  
**Create Workflow**: See "Common Commands" above

**Full Documentation**: See DEPLOYMENT_GUIDE.md
