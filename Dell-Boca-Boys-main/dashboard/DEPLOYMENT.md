# Dell Bocca Boys Dashboard - Deployment Guide

Complete guide for deploying the Dell Bocca Boys Dashboard to production.

## 📋 Prerequisites

- Node.js 18+ and npm 9+
- Python 3.10+
- PostgreSQL 16 (for backend)
- Redis 7 (for caching)
- Domain name (optional)
- SSL certificate (recommended for production)

## 🚀 Deployment Options

### Option 1: Local Development

**Quick Start (5 minutes)**

```bash
# 1. Clone repository
git clone https://github.com/modinired/Dell-Boca-Boys.git
cd Dell-Boca-Boys

# 2. Install dashboard dependencies
cd dashboard
npm install

# 3. Set up environment
cp .env.example .env.local
nano .env.local  # Add configuration

# 4. Start backend API (in separate terminal)
cd ../api
python dashboard_api.py

# 5. Start dashboard
cd ../dashboard
npm run dev

# Access at http://localhost:3000
```

### Option 2: Docker Deployment

**Full Stack with Docker Compose**

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Dashboard Frontend
  dashboard:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
      - NEXT_PUBLIC_WS_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped

  # Backend API
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dellbocca
      - REDIS_URL=redis://redis:6379
      - AGENT_EMAIL_PASSWORD=${AGENT_EMAIL_PASSWORD}
    depends_on:
      - db
      - redis
    restart: unless-stopped

  # PostgreSQL Database
  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=dellbocca
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - dashboard
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

```bash
# Deploy with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f dashboard

# Scale services
docker-compose up -d --scale api=3
```

### Option 3: Cloud Deployment (AWS)

**Architecture**

```
┌─────────────────────────────────────────┐
│         CloudFront (CDN)                │
│         SSL/TLS Termination             │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│         Application Load Balancer       │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────┴──────┐ ┌─────┴──────┐
│   ECS       │ │   ECS      │
│ Dashboard   │ │   API      │
│ (Fargate)   │ │ (Fargate)  │
└─────────────┘ └────────────┘
       │               │
       └───────┬───────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────┴─────┐   ┌──────┴──────┐
│   RDS     │   │ ElastiCache │
│PostgreSQL │   │    Redis    │
└───────────┘   └─────────────┘
```

**Terraform Configuration**

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# Dashboard Service
resource "aws_ecs_service" "dashboard" {
  name            = "dell-bocca-dashboard"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.dashboard.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.dashboard.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.dashboard.arn
    container_name   = "dashboard"
    container_port   = 3000
  }
}

# API Service
resource "aws_ecs_service" "api" {
  name            = "dell-bocca-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 3
  launch_type     = "FARGATE"

  # ... configuration
}

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier        = "dell-bocca-db"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  storage_encrypted = true

  # ... configuration
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "main" {
  cluster_id      = "dell-bocca-cache"
  engine          = "redis"
  engine_version  = "7.0"
  node_type       = "cache.t3.medium"
  num_cache_nodes = 2

  # ... configuration
}
```

### Option 4: Vercel + Railway

**Fastest Deployment (2 minutes)**

```bash
# 1. Deploy Frontend to Vercel
cd dashboard
vercel --prod

# 2. Deploy Backend to Railway
# Visit https://railway.app
# Connect GitHub repo
# Deploy /api/dashboard_api.py
# Copy deployment URL

# 3. Update Vercel environment variables
vercel env add NEXT_PUBLIC_API_URL
# Paste Railway URL

# 4. Redeploy
vercel --prod
```

## 🔐 Security Configuration

### SSL/TLS Setup

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name dashboard.dellboccaboys.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://dashboard:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://api:8000;
        # ... proxy settings
    }

    location /ws {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Environment Variables (Production)

```bash
# Dashboard (.env.production)
NEXT_PUBLIC_API_URL=https://api.dellboccaboys.com
NEXT_PUBLIC_WS_URL=wss://api.dellboccaboys.com
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn
NODE_ENV=production

# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/dellbocca
REDIS_URL=redis://localhost:6379
AGENT_EMAIL=ace.llc.nyc@gmail.com
AGENT_EMAIL_PASSWORD=your_app_password
EMAIL_POLL_INTERVAL=60
CORS_ORIGINS=https://dashboard.dellboccaboys.com
SECRET_KEY=your_secret_key_here
```

### Authentication Setup

```typescript
// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')

  if (!token && !request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

## 📊 Monitoring & Logging

### Application Monitoring

```typescript
// Sentry Integration
// src/lib/sentry.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
})
```

### Logging

```python
# backend logging
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'dashboard_api.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)
```

### Health Checks

```python
# api/dashboard_api.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": check_db_connection(),
            "redis": check_redis_connection(),
            "email": email_service.is_running if email_service else False
        }
    }
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy Dashboard

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd dashboard && npm ci
      - run: cd dashboard && npm run lint
      - run: cd dashboard && npm run type-check
      - run: cd dashboard && npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Production
        run: |
          # Deploy commands here
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## 📈 Performance Optimization

### Next.js Configuration

```javascript
// next.config.js
module.exports = {
  // Enable compression
  compress: true,

  // Image optimization
  images: {
    domains: ['localhost', 'api.dellboccaboys.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // Output standalone for Docker
  output: 'standalone',

  // Webpack optimizations
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks.cacheGroups = {
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      }
    }
    return config
  },
}
```

### Caching Strategy

```nginx
# Cache static assets
location /_next/static {
    proxy_cache STATIC;
    proxy_pass http://dashboard:3000;
    add_header Cache-Control "public, max-age=31536000, immutable";
}

# Cache API responses
location /api {
    proxy_cache API;
    proxy_cache_valid 200 5m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
}
```

## 🧪 Testing in Production

```bash
# Health check
curl https://dashboard.dellboccaboys.com/health

# API test
curl https://api.dellboccaboys.com/api/agents

# WebSocket test
wscat -c wss://api.dellboccaboys.com/ws
```

## 🔧 Maintenance

### Backup Strategy

```bash
# Database backup
pg_dump -h localhost -U user dellbocca > backup_$(date +%Y%m%d).sql

# Automated daily backups
0 2 * * * /usr/local/bin/backup_db.sh
```

### Updates

```bash
# Update dashboard
cd dashboard
git pull
npm install
npm run build
pm2 restart dashboard

# Update backend
cd ../api
git pull
pip install -r requirements.txt
pm2 restart api
```

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Check firewall/security group rules
4. Test WebSocket connectivity
5. Review error messages in Sentry

---

**Deployment Checklist:**

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database migrations run
- [ ] Redis cache configured
- [ ] Email service credentials set
- [ ] CORS origins configured
- [ ] Monitoring/logging enabled
- [ ] Backups configured
- [ ] Health checks passing
- [ ] Load testing completed

**Version**: 1.0.0
**Last Updated**: 2025-01-07
