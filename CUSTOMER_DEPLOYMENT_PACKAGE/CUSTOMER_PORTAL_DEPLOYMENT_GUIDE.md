# Dell Boca Boys Customer Portal - Deployment Guide

## Overview

The Dell Boca Boys Customer Portal is a modern, full-stack web application that provides customers with a dedicated interface for managing their workflow automation requests, monitoring deployed workflows, and accessing analytics.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Customer Portal Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   React Frontend │ ◄─────► │  FastAPI Backend │          │
│  │  (Port 3001)     │         │   (Port 8000)    │          │
│  └──────────────────┘         └──────────────────┘          │
│         │                              │                     │
│         │                              │                     │
│         ▼                              ▼                     │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Static Assets   │         │   PostgreSQL DB  │          │
│  │  (Vite Build)    │         │   (Port 5432)    │          │
│  └──────────────────┘         └──────────────────┘          │
│                                                               │
│         Integration with Dell Boca Boys Core System          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  • Multi-Agent Network (8 Dell Boca Boys agents)      │  │
│  │  • Workflow Automation Engine (n8n)                   │  │
│  │  • Email Communication (ace.llc.nyc@gmail.com)        │  │
│  │  • PostgreSQL Workflow Repository                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Customer-Facing Features
- **Dashboard** - Real-time overview of requests, workflows, and metrics
- **Request Management** - Submit and track workflow automation requests
- **Workflow Library** - View and manage deployed automations
- **Template Marketplace** - Browse and deploy pre-built templates
- **Analytics** - Detailed performance metrics and insights
- **Notifications** - Real-time updates on request status
- **Responsive Design** - Mobile, tablet, and desktop support

### Technical Features
- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access Control** - Customer-specific data isolation
- **Real-time Updates** - WebSocket support for live notifications
- **File Upload** - Attachment support for workflow requests
- **Search & Filtering** - Advanced filtering and search capabilities
- **Pagination** - Efficient data loading for large datasets
- **Type Safety** - Full TypeScript implementation

## Prerequisites

### System Requirements
- **Node.js** 18+ and npm
- **Python** 3.9+
- **PostgreSQL** 14+
- **Redis** (optional, for caching and background tasks)

### Development Tools
- **Git** for version control
- **VS Code** or similar IDE (recommended)
- **Postman** or similar for API testing (optional)

## Installation

### 1. Frontend Setup (React Portal)

Navigate to the customer portal directory:

```bash
cd CUSTOMER_DEPLOYMENT_PACKAGE/customer-portal
```

Install dependencies:

```bash
npm install
```

Create environment file:

```bash
cp .env.example .env
```

Configure environment variables in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_ENVIRONMENT=development
```

Start the development server:

```bash
npm run dev
```

The portal will be available at `http://localhost:3001`.

### 2. Backend Setup (FastAPI)

Navigate to the backend directory:

```bash
cd CUSTOMER_DEPLOYMENT_PACKAGE/backend
```

Create a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create environment file:

```bash
cp .env.example .env
```

Configure environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dell_boca_boys

# JWT Authentication
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3001,http://localhost:5173

# Email (Dell Boca Boys communication)
EMAIL_ADDRESS=ace.llc.nyc@gmail.com
EMAIL_PASSWORD=your-email-password

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

Start the FastAPI server:

```bash
cd api
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

API documentation will be available at:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### 3. Database Setup

Create the PostgreSQL database:

```sql
CREATE DATABASE dell_boca_boys;
CREATE USER dell_boca_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE dell_boca_boys TO dell_boca_user;
```

Run database migrations (if using Alembic):

```bash
cd CUSTOMER_DEPLOYMENT_PACKAGE/backend
alembic upgrade head
```

### 4. Integration with Dell Boca Boys Core

The customer portal integrates with the existing Dell Boca Boys multi-agent system:

1. **Email Integration**: Workflow requests can trigger emails to `ace.llc.nyc@gmail.com`
2. **Agent Assignment**: Requests are automatically assigned to appropriate agents
3. **Workflow Repository**: Deployed workflows are stored in the PostgreSQL repository
4. **n8n Workflows**: Templates map to actual n8n workflow definitions

Ensure the core system is running:

```bash
cd Dell-Boca-Boys-main
python -m core.intelligence.cesar_multi_agent_network
```

## Production Deployment

### Frontend (React)

1. Build for production:

```bash
cd customer-portal
npm run build
```

2. Serve static files with Nginx or similar:

```nginx
server {
    listen 80;
    server_name customer.dellbocaboys.com;

    root /path/to/customer-portal/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Enable HTTPS with Let's Encrypt:

```bash
sudo certbot --nginx -d customer.dellbocaboys.com
```

### Backend (FastAPI)

1. Install production dependencies:

```bash
pip install gunicorn
```

2. Create systemd service (`/etc/systemd/system/dell-boca-api.service`):

```ini
[Unit]
Description=Dell Boca Boys Customer API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/CUSTOMER_DEPLOYMENT_PACKAGE/backend/api
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

3. Start and enable the service:

```bash
sudo systemctl start dell-boca-api
sudo systemctl enable dell-boca-api
```

### Database (PostgreSQL)

1. **Production configuration**:
   - Enable SSL connections
   - Configure connection pooling
   - Set up regular backups
   - Enable query logging

2. **Backup strategy**:

```bash
# Daily backup script
#!/bin/bash
pg_dump -U dell_boca_user dell_boca_boys > /backups/db_$(date +%Y%m%d).sql
```

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong, random value
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure CORS with specific allowed origins (no wildcards)
- [ ] Set up rate limiting on API endpoints
- [ ] Enable PostgreSQL SSL connections
- [ ] Use environment variables for all secrets
- [ ] Set up firewall rules (only expose necessary ports)
- [ ] Enable database connection encryption
- [ ] Implement API request logging
- [ ] Set up monitoring and alerts

## Testing

### Frontend Tests

```bash
cd customer-portal
npm run test
```

### Backend Tests

```bash
cd backend
pytest
```

### End-to-End Tests

```bash
cd customer-portal
npm run test:e2e
```

## Monitoring

### Application Monitoring

1. **Backend metrics** (using Prometheus):
   - Request count and latency
   - Error rates
   - Database query performance

2. **Frontend monitoring** (using Sentry):
   - JavaScript errors
   - Performance metrics
   - User experience tracking

### Health Checks

- Frontend: `http://localhost:3001`
- Backend: `http://localhost:8000/health`
- Database: Check connection with `psql`

## Troubleshooting

### Common Issues

**Frontend won't start:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Backend 500 errors:**
```bash
# Check logs
journalctl -u dell-boca-api -f

# Verify database connection
psql -U dell_boca_user -d dell_boca_boys
```

**CORS errors:**
- Verify `ALLOWED_ORIGINS` in backend `.env`
- Check browser console for specific error

**Authentication issues:**
- Verify `SECRET_KEY` matches between sessions
- Check token expiration times
- Clear browser local storage

## Maintenance

### Regular Tasks

1. **Database backups** (daily)
2. **Log rotation** (weekly)
3. **Dependency updates** (monthly)
4. **Security patches** (as needed)
5. **Performance monitoring** (ongoing)

### Update Procedure

1. Backend updates:
```bash
cd backend
git pull
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart dell-boca-api
```

2. Frontend updates:
```bash
cd customer-portal
git pull
npm install
npm run build
# Copy dist/ to web server
```

## Support

For issues or questions:
- **Email**: ace.llc.nyc@gmail.com (subject: "Dell Bocca Boys")
- **Documentation**: See `/docs` directory
- **API Docs**: http://localhost:8000/api/docs

## Architecture Decisions

### Why React + TypeScript?
- Type safety prevents runtime errors
- Large ecosystem and community support
- Excellent developer experience
- Production-ready performance

### Why FastAPI?
- Modern, fast Python framework
- Automatic API documentation
- Built-in validation with Pydantic
- Async support for high performance
- Easy integration with existing Python codebase

### Why PostgreSQL?
- ACID compliance for data integrity
- JSON support for flexible schemas
- Excellent performance at scale
- Robust backup and replication

### Why Zustand for state management?
- Lightweight (1KB)
- Simple API
- No boilerplate
- TypeScript-first

## License

Proprietary - Dell Boca Boys Workflow Automation Platform
