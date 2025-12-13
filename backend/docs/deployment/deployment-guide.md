# LernsystemX Backend - Production Deployment Guide

**Version:** 1.0
**Last Updated:** 2025-11-16
**Status:** Production-Ready

This comprehensive guide covers the complete production deployment of the LernsystemX backend on a Linux server (Ubuntu 22.04 LTS recommended).

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Architecture](#server-architecture)
3. [Server Preparation](#server-preparation)
4. [PostgreSQL Setup](#postgresql-setup)
5. [Redis Setup](#redis-setup)
6. [Backend Application Setup](#backend-application-setup)
7. [Gunicorn Configuration](#gunicorn-configuration)
8. [systemd Service Setup](#systemd-service-setup)
9. [Nginx Reverse Proxy](#nginx-reverse-proxy)
10. [HTTPS with Let's Encrypt](#https-with-lets-encrypt)
11. [Logging & Monitoring](#logging--monitoring)
12. [Healthchecks](#healthchecks)
13. [Deployment Automation](#deployment-automation)
14. [Rollback Procedures](#rollback-procedures)
15. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements

**Minimum (for small deployments):**
- 2 CPU cores
- 4 GB RAM
- 50 GB SSD storage
- 100 Mbps network

**Recommended (for production):**
- 4+ CPU cores
- 8+ GB RAM
- 100+ GB SSD storage
- 1 Gbps network

### Software Requirements

- Ubuntu 22.04 LTS (or Debian 12+)
- Python 3.12+
- PostgreSQL 15+
- Redis 7.2+
- Nginx 1.24+
- Git
- Certbot (for HTTPS)

### Domain & DNS

- Domain name pointing to your server IP
- A record: `yourdomain.com` → `YOUR_SERVER_IP`
- Optional: `www.yourdomain.com` → `YOUR_SERVER_IP`

---

## Server Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERNET                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                   ┌──────────┐
                   │ Firewall │
                   │ Port 80  │
                   │ Port 443 │
                   └──────┬───┘
                          │
                          ▼
             ┌────────────────────────┐
             │   Nginx (Reverse       │
             │   Proxy + SSL)         │
             │   Port 80, 443         │
             └────┬──────────────┬────┘
                  │              │
        ┌─────────▼──────┐   ┌──▼────────────┐
        │  Frontend      │   │  Backend API   │
        │  (Static Files)│   │  (Gunicorn)    │
        │  /dist         │   │  Port 8000     │
        └────────────────┘   └──┬─────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼──────┐      ┌────────▼───────┐
            │  PostgreSQL  │      │     Redis      │
            │  Port 5432   │      │  Port 6379     │
            └──────────────┘      └────────────────┘
```

---

## Server Preparation

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Essential Packages

```bash
sudo apt install -y \
    build-essential \
    git \
    curl \
    wget \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx
```

### 3. Create Application User

```bash
sudo useradd -m -s /bin/bash lsx
sudo usermod -aG sudo lsx
```

### 4. Setup Firewall

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### 5. Configure Fail2Ban (Brute Force Protection)

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## PostgreSQL Setup

### 1. Install PostgreSQL 15

```bash
sudo apt install -y postgresql-15 postgresql-contrib-15 libpq-dev
```

### 2. Start PostgreSQL

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Create Database and User

```bash
sudo -u postgres psql
```

In PostgreSQL shell:

```sql
-- Create database
CREATE DATABASE lernsystemx_prod;

-- Create user with secure password
CREATE USER lsx_user WITH PASSWORD 'CHANGE_THIS_TO_SECURE_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE lernsystemx_prod TO lsx_user;

-- Switch to database
\c lernsystemx_prod

-- Grant schema permissions (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO lsx_user;
GRANT CREATE ON SCHEMA public TO lsx_user;

-- Exit
\q
```

### 4. Configure PostgreSQL for Network Access (if needed)

Edit `/etc/postgresql/15/main/postgresql.conf`:

```ini
listen_addresses = 'localhost'  # Only localhost for security
```

Edit `/etc/postgresql/15/main/pg_hba.conf`:

```
# Local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

### 5. Test Connection

```bash
psql -h localhost -U lsx_user -d lernsystemx_prod -W
```

---

## Redis Setup

### 1. Install Redis

```bash
sudo apt install -y redis-server
```

### 2. Configure Redis

Edit `/etc/redis/redis.conf`:

```ini
# Bind to localhost only
bind 127.0.0.1 ::1

# Enable persistence
save 900 1
save 300 10
save 60 10000

# Set max memory
maxmemory 1gb
maxmemory-policy allkeys-lru

# Enable protected mode
protected-mode yes

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

### 3. Start Redis

```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### 4. Test Redis

```bash
redis-cli ping
# Expected output: PONG
```

---

## Backend Application Setup

### 1. Create Directory Structure

```bash
sudo mkdir -p /opt/lsx/backend
sudo mkdir -p /opt/lsx/frontend
sudo mkdir -p /var/log/lsx
sudo mkdir -p /opt/lsx/scripts
sudo mkdir -p /opt/lsx/backups

# Set ownership
sudo chown -R lsx:lsx /opt/lsx
sudo chown -R lsx:lsx /var/log/lsx
```

### 2. Clone Repository (or copy files)

```bash
cd /opt/lsx/backend

# Option 1: Git clone
git clone https://github.com/your-org/lsx-backend.git .

# Option 2: Copy from local
scp -r /path/to/backend/* user@server:/opt/lsx/backend/
```

### 3. Install Python 3.12

```bash
# Add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.12
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

### 4. Create Virtual Environment

```bash
cd /opt/lsx/backend
python3.12 -m venv venv
source venv/bin/activate
```

### 5. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

### 6. Create Production Environment File

```bash
cp .env.production.example .env.production
nano .env.production
```

Fill in all values (see `.env.production.example` for details).

**Critical settings:**
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `JWT_SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `DATABASE_URL` - Use PostgreSQL connection string
- `REDIS_URL` - Use Redis connection string
- `CORS_ORIGINS` - Set to your frontend domain(s)

### 7. Run Database Migrations

```bash
cd /opt/lsx/backend
source venv/bin/activate

# Run setup wizard or migrations
python run.py setup
```

### 8. Create Uploads Directory

```bash
mkdir -p /opt/lsx/backend/uploads
chmod 755 /opt/lsx/backend/uploads
```

### 9. Test Backend Manually

```bash
cd /opt/lsx/backend
source venv/bin/activate

# Start with Gunicorn (test mode)
gunicorn -c gunicorn.conf.py "run_production:application"
```

Visit: `http://YOUR_SERVER_IP:8000/health`

Should return: `{"status": "healthy", ...}`

**Stop the test server (Ctrl+C)** before continuing.

---

## Gunicorn Configuration

Gunicorn config already exists in `backend/gunicorn.conf.py`.

**Key settings:**
- Workers: CPU cores * 2 + 1 (auto-detected)
- Threads: 2 per worker
- Timeout: 120 seconds
- Worker class: `gthread` (multi-threaded)

**Environment variables to override:**

```bash
export GUNICORN_WORKERS=4
export GUNICORN_THREADS=2
export GUNICORN_TIMEOUT=120
```

---

## systemd Service Setup

### 1. Copy Service File

```bash
sudo cp /opt/lsx/backend/deployment/systemd/lsx-backend.service \
    /etc/systemd/system/lsx-backend.service
```

### 2. Edit Service File (if needed)

```bash
sudo nano /etc/systemd/system/lsx-backend.service
```

Verify paths:
- `WorkingDirectory=/opt/lsx/backend`
- `ExecStart=/opt/lsx/backend/venv/bin/gunicorn ...`
- `EnvironmentFile=/opt/lsx/backend/.env.production`

### 3. Reload systemd

```bash
sudo systemctl daemon-reload
```

### 4. Enable and Start Service

```bash
sudo systemctl enable lsx-backend
sudo systemctl start lsx-backend
```

### 5. Check Service Status

```bash
sudo systemctl status lsx-backend

# View logs
sudo journalctl -u lsx-backend -f
```

**Expected output:** Service should be `active (running)`.

---

## Nginx Reverse Proxy

### 1. Install Nginx

```bash
sudo apt install -y nginx
```

### 2. Copy Nginx Config

```bash
sudo cp /opt/lsx/backend/deployment/nginx/lsx.conf \
    /etc/nginx/sites-available/lsx.conf
```

### 3. Edit Nginx Config

```bash
sudo nano /etc/nginx/sites-available/lsx.conf
```

**Update:**
- `server_name _;` → `server_name yourdomain.com www.yourdomain.com;`
- SSL certificate paths (after Let's Encrypt setup)

### 4. Enable Site

```bash
# Disable default site
sudo rm -f /etc/nginx/sites-enabled/default

# Enable LSX site
sudo ln -s /etc/nginx/sites-available/lsx.conf \
    /etc/nginx/sites-enabled/lsx.conf
```

### 5. Test Nginx Config

```bash
sudo nginx -t
```

**Expected:** `syntax is ok` and `test is successful`.

### 6. Start Nginx

```bash
sudo systemctl enable nginx
sudo systemctl restart nginx
```

### 7. Test Backend via Nginx

Visit: `http://YOUR_SERVER_IP/health`

Should return health check JSON.

---

## HTTPS with Let's Encrypt

### 1. Obtain SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow prompts:
- Enter email address
- Agree to Terms of Service
- Choose: Redirect HTTP to HTTPS (recommended)

### 2. Verify SSL

Visit: `https://yourdomain.com/health`

Should show secure connection (padlock icon).

### 3. Auto-Renewal Setup

Certbot auto-renewal is enabled by default. Test renewal:

```bash
sudo certbot renew --dry-run
```

**Expected:** `Congratulations, all simulated renewals succeeded`.

---

## Logging & Monitoring

### 1. Log Files

**Backend logs:**
- `/var/log/lsx/backend.log` - Application log
- `/var/log/lsx/error.log` - Error log
- `/var/log/lsx/access.log` - Access log

**Nginx logs:**
- `/var/log/nginx/lsx_access.log` - Access log
- `/var/log/nginx/lsx_error.log` - Error log

**systemd logs:**
```bash
sudo journalctl -u lsx-backend -f
```

### 2. Log Rotation

Logs rotate automatically (configured in `logging.conf`):
- Max size: 10 MB per file
- Backup count: 5 files
- Total: ~50 MB per log type

### 3. Monitoring Health

```bash
# Basic health
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/health/detailed

# Readiness (K8s)
curl http://localhost:8000/health/ready

# Liveness (K8s)
curl http://localhost:8000/health/live
```

### 4. Prometheus Metrics (Phase 19)

LernsystemX exports metrics in Prometheus format for monitoring and alerting.

#### Enable Monitoring

Add to `/opt/lsx/backend/.env.production`:

```env
# Monitoring & Alerting
MONITORING_ENABLED=True
MONITORING_EXPORTER=prometheus
MONITORING_METRICS_PATH=/metrics
MONITORING_SAMPLE_RATE=1.0
```

#### Metrics Endpoint

The `/metrics` endpoint is available at:
- **URL:** `http://localhost:8000/metrics` (internal only)
- **Access:** Restricted via Nginx (localhost + Prometheus server only)
- **Format:** Prometheus text format

**Test metrics endpoint:**
```bash
# From server (localhost)
curl http://localhost:8000/metrics

# Should return metrics like:
# lsx_http_requests_total{method="GET",endpoint="/api/courses",status_code="200"} 1234.0
# lsx_http_request_duration_seconds_bucket{method="GET",endpoint="/api/courses",le="0.1"} 1200.0
```

#### Available Metrics

**HTTP Request Metrics:**
- `lsx_http_requests_total` - Total HTTP requests by method, endpoint, status code
- `lsx_http_request_duration_seconds` - Request latency histogram
- `lsx_http_errors_total` - HTTP errors by type

**Business Metrics:**
- `lsx_analytics_events_total` - Analytics events tracked
- `lsx_ai_method_calls_total` - AI method calls
- `lsx_ai_cost_eur_total` - AI costs in EUR
- `lsx_cache_operations_total` - Cache hits/misses

**Infrastructure Metrics:**
- `lsx_db_connections_active` - Active database connections
- `lsx_celery_queue_length` - Celery task queue length

#### Nginx Security Configuration

The `/metrics` endpoint is protected via IP whitelist in `/etc/nginx/sites-enabled/lsx.conf`:

```nginx
location /metrics {
    # Allow only from localhost and Prometheus server
    allow 127.0.0.1;
    allow ::1;
    # allow YOUR_PROMETHEUS_IP;  # Add your Prometheus server IP
    deny all;

    proxy_pass http://lsx_backend/metrics;
    access_log off;
}
```

#### Quick Prometheus Setup

**1. Install Prometheus:**
```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-* /opt/prometheus
```

**2. Create config `/etc/prometheus/prometheus.yml`:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'lsx_backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

**3. Run Prometheus:**
```bash
/opt/prometheus/prometheus --config.file=/etc/prometheus/prometheus.yml
```

**4. Access Prometheus UI:**
- Open http://localhost:9090
- Go to **Status** → **Targets** to verify `lsx_backend` is "UP"

#### Install Grafana (Optional)

```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

sudo systemctl enable grafana-server
sudo systemctl start grafana-server

# Access: http://localhost:3000 (admin/admin)
```

#### Example PromQL Queries

```promql
# Request rate (requests per minute)
rate(lsx_http_requests_total[1m]) * 60

# p95 latency (milliseconds)
histogram_quantile(0.95, rate(lsx_http_request_duration_seconds_bucket[5m])) * 1000

# Error rate percentage
rate(lsx_http_errors_total[5m]) / rate(lsx_http_requests_total[5m]) * 100

# Cache hit ratio
rate(lsx_cache_operations_total{operation="get",result="hit"}[5m]) /
(rate(lsx_cache_operations_total{operation="get",result="hit"}[5m]) +
 rate(lsx_cache_operations_total{operation="get",result="miss"}[5m]))

# AI costs per hour (EUR)
rate(lsx_ai_cost_eur_total[1h]) * 3600
```

**For complete monitoring setup, alert rules, and Grafana dashboards, see:**
👉 **[`monitoring-alerting-guide.md`](./monitoring/monitoring-alerting-guide.md)**

---

## Healthchecks

### Available Endpoints

1. **`GET /health`** - Basic health check
   - Returns 200 if healthy, 503 if unhealthy
   - Checks: Redis, PostgreSQL

2. **`GET /health/detailed`** - Detailed health
   - Component-level status
   - Latency metrics
   - Version, environment info

3. **`GET /health/ready`** - Readiness probe
   - For load balancers / K8s
   - Returns 200 when ready to serve traffic

4. **`GET /health/live`** - Liveness probe
   - For K8s
   - Returns 200 if application is alive

### Integration with Load Balancers

Configure your load balancer to use `/health` as the health check endpoint.

**Example (AWS ALB):**
- Health check path: `/health`
- Healthy threshold: 2
- Unhealthy threshold: 3
- Timeout: 5 seconds
- Interval: 30 seconds

---

## Deployment Automation

### Deployment Script

Create `/opt/lsx/scripts/deploy-backend.sh`:

```bash
#!/bin/bash
set -e

echo "=== LernsystemX Backend Deployment ===" date

# Configuration
APP_DIR="/opt/lsx/backend"
VENV_DIR="$APP_DIR/venv"
REPO_URL="https://github.com/your-org/lsx-backend.git"
BRANCH="main"

# Navigate to app directory
cd "$APP_DIR"

# Pull latest code
echo "Pulling latest code from $BRANCH..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/update dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if any)
echo "Running database migrations..."
# python manage.py migrate  # If using migrations

# Collect static files (if needed)
# python manage.py collectstatic --noinput

# Restart backend service
echo "Restarting backend service..."
sudo systemctl restart lsx-backend

# Wait for service to be ready
sleep 5

# Health check
echo "Running health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend is healthy!"
else
    echo "✗ Backend health check failed!"
    exit 1
fi

echo "=== Deployment completed successfully ==="
date
```

Make executable:

```bash
chmod +x /opt/lsx/scripts/deploy-backend.sh
```

Run deployment:

```bash
/opt/lsx/scripts/deploy-backend.sh
```

---

## Rollback Procedures

### Manual Rollback

1. **Check Git History**

```bash
cd /opt/lsx/backend
git log --oneline
```

2. **Rollback to Previous Commit**

```bash
git checkout <previous-commit-hash>
```

3. **Restart Service**

```bash
sudo systemctl restart lsx-backend
```

4. **Verify Health**

```bash
curl http://localhost:8000/health
```

### Automated Rollback Script

Create `/opt/lsx/scripts/rollback-backend.sh`:

```bash
#!/bin/bash
set -e

cd /opt/lsx/backend

# Rollback to previous commit
git reset --hard HEAD~1

# Restart service
sudo systemctl restart lsx-backend

# Health check
sleep 5
curl -f http://localhost:8000/health

echo "Rollback completed"
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status lsx-backend

# View detailed logs
sudo journalctl -u lsx-backend -n 100 --no-pager

# Common issues:
# 1. Database connection failed
#    → Check DATABASE_URL in .env.production
#    → Verify PostgreSQL is running: systemctl status postgresql
#
# 2. Redis connection failed
#    → Check REDIS_URL in .env.production
#    → Verify Redis is running: systemctl status redis-server
#
# 3. Permission denied
#    → Check file ownership: chown -R lsx:lsx /opt/lsx/backend
#
# 4. Port already in use
#    → Check if Gunicorn is already running: ps aux | grep gunicorn
```

### Nginx Returns 502 Bad Gateway

```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, start it
sudo systemctl start lsx-backend

# Check Nginx error log
sudo tail -f /var/log/nginx/lsx_error.log
```

### High Memory Usage

```bash
# Check Gunicorn workers
ps aux | grep gunicorn

# Reduce workers in gunicorn.conf.py or via environment
export GUNICORN_WORKERS=2
sudo systemctl restart lsx-backend
```

### Database Connection Pool Exhausted

Edit `.env.production`:

```env
DB_POOL_MAX_SIZE=30  # Increase from default 20
```

Restart:

```bash
sudo systemctl restart lsx-backend
```

### SSL Certificate Renewal Failed

```bash
# Renew manually
sudo certbot renew

# Check renewal logs
sudo cat /var/log/letsencrypt/letsencrypt.log
```

---

## Security Best Practices

1. **Firewall:** Only allow ports 22, 80, 443
2. **SSH:** Use key-based authentication, disable password login
3. **Secrets:** Never commit `.env.production` to Git
4. **Updates:** Keep system packages updated
5. **Backups:** Regular database and file backups
6. **Monitoring:** Set up alerts for service failures
7. **Rate Limiting:** Nginx rate limiting enabled
8. **Headers:** Security headers configured in Nginx

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor logs for errors: `tail -f /var/log/lsx/error.log`
- Check disk space: `df -h`

**Weekly:**
- Review access logs: `less /var/log/lsx/access.log`
- Check SSL certificate expiry: `sudo certbot certificates`

**Monthly:**
- Update system packages: `sudo apt update && sudo apt upgrade`
- Database backup and verification
- Review and archive old logs

---

## Performance Optimization

1. **Database Indexing:** Ensure proper indexes on frequently queried columns
2. **Connection Pooling:** Already configured (psycopg pool)
3. **Redis Caching:** Already implemented (Phase 16)
4. **Gunicorn Workers:** Adjust based on CPU cores
5. **Nginx Caching:** Static file caching enabled
6. **HTTP/2:** Enabled in Nginx config
7. **Gzip Compression:** Enabled in Nginx config

---

## Backups & Recovery

**📋 For detailed backup & recovery procedures, see: [`backup-recovery-guide.md`](./backup-recovery-guide.md)**

### Quick Setup

#### 1. Create Backup Directories

```bash
sudo mkdir -p /var/backups/lsx/db
sudo chown -R postgres:postgres /var/backups/lsx
sudo chmod 750 /var/backups/lsx
```

#### 2. Make Backup Scripts Executable

```bash
sudo chmod +x /opt/lsx/deployment/backup/backup_db.sh
sudo chmod +x /opt/lsx/deployment/backup/restore_db.sh
sudo chmod +x /opt/lsx/deployment/backup/cleanup_backups.sh
```

#### 3. Install systemd Timers

```bash
# Copy systemd service files
sudo cp /opt/lsx/deployment/systemd/lsx-backup-db.service /etc/systemd/system/
sudo cp /opt/lsx/deployment/systemd/lsx-backup-db.timer /etc/systemd/system/
sudo cp /opt/lsx/deployment/systemd/lsx-backup-cleanup.service /etc/systemd/system/
sudo cp /opt/lsx/deployment/systemd/lsx-backup-cleanup.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timers
sudo systemctl enable --now lsx-backup-db.timer
sudo systemctl enable --now lsx-backup-cleanup.timer

# Verify timers
systemctl list-timers | grep lsx
```

**Expected output:**
```
Mon 2025-11-18 03:00:00 UTC  11h left  Mon 2025-11-17 03:00:00 UTC  1 day ago  lsx-backup-db.timer
Sun 2025-11-24 04:00:00 UTC  6 days left  Sun 2025-11-17 04:00:00 UTC  1 day ago  lsx-backup-cleanup.timer
```

#### 4. Test Manual Backup

```bash
# Run manual backup
sudo -u postgres bash /opt/lsx/deployment/backup/backup_db.sh

# Verify backup was created
ls -lh /var/backups/lsx/db/
```

### Backup Schedule

| Task | Frequency | Time | Retention |
|------|-----------|------|-----------|
| **Database Backup** | Daily | 3:00 AM | 30 days |
| **Backup Cleanup** | Weekly | Sunday 4:00 AM | - |

### Quick Restore

⚠️ **WARNING:** Restore procedure will **DROP** the current database!

```bash
# List available backups
ls -lh /var/backups/lsx/db/

# Restore from backup (interactive confirmation required)
sudo bash /opt/lsx/deployment/backup/restore_db.sh /var/backups/lsx/db/lsx_db_YYYYMMDD_HHMMSS.sql.gz
```

### View Backup Logs

```bash
# View backup execution logs
journalctl -u lsx-backup-db.service -n 50

# View cleanup logs
journalctl -u lsx-backup-cleanup.service -n 50

# View backup script logs
tail -f /var/backups/lsx/backup.log
```

### Configuration

Edit backup settings in `/opt/lsx/backend/.env.production`:

```env
BACKUP_DIR=/var/backups/lsx
BACKUP_RETENTION_DAYS=30
BACKUP_ENABLE_COMPRESSION=True
```

**For complete backup documentation, troubleshooting, and disaster recovery procedures, see:**
👉 **[`backup-recovery-guide.md`](./backup-recovery-guide.md)**

---

## Phase 20: Security Hardening

### Security Architecture Implementation

Phase 20 adds enterprise-grade security features to protect against common vulnerabilities and comply with ISO 27001:2013 and DSGVO/GDPR requirements.

**✅ Implemented Security Features:**
- RBAC/Permissions System (9 roles, 25+ permissions)
- Rate Limiting & Brute-Force Protection
- Security Headers Middleware
- Audit Logging System
- Sensitive Data Handling Guidelines

### Security Configuration

#### 1. Database Setup (Audit Logs)

```bash
# Run audit log schema migration
sudo -u postgres psql -d lernsystemx_prod -f /opt/lsx/backend/app/database/audit_log_schema.sql

# Verify table creation
sudo -u postgres psql -d lernsystemx_prod -c "\d audit_logs"
```

#### 2. Environment Variables

Add to `/opt/lsx/backend/.env.production`:

```env
# ==========================================
# SECURITY (Phase 20)
# ==========================================

# Password Policy
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_DIGITS=True
PASSWORD_REQUIRE_SPECIAL=True

# Login Security & Account Lockout
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_MINUTES=15
ACCOUNT_LOCKOUT_THRESHOLD=10

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_LOGIN=5 per minute
RATE_LIMIT_API=100 per minute
RATE_LIMIT_SENSITIVE=10 per minute

# Security Headers
SECURITY_HEADERS_ENABLED=True
HSTS_MAX_AGE=31536000

# Audit Logging
AUDIT_LOG_ENABLED=True
AUDIT_LOG_RETENTION_DAYS=365
```

#### 3. Nginx Security Headers

Update `/etc/nginx/sites-available/lsx-backend` (add to `server` block):

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL configuration (existing)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # ====================
    # SECURITY HEADERS (Phase 20)
    # ====================

    # HSTS - Force HTTPS for 1 year
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Prevent clickjacking
    add_header X-Frame-Options "DENY" always;

    # Prevent MIME-sniffing
    add_header X-Content-Type-Options "nosniff" always;

    # XSS Protection (legacy browsers)
    add_header X-XSS-Protection "1; mode=block" always;

    # Referrer Policy
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Permissions Policy - Disable dangerous features
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=(), usb=()" always;

    # Content Security Policy (adjust based on your frontend)
    add_header Content-Security-Policy "default-src 'self'; connect-src 'self' https://yourdomain.com; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; script-src 'self'; font-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests;" always;

    # Remove server header
    server_tokens off;

    # ====================
    # RATE LIMITING (Phase 20)
    # ====================

    # Limit login attempts (IP-based)
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;
    limit_req_status 429;

    # Proxy to backend
    location /api/v1/ {
        # Rate limit for login endpoint
        location /api/v1/auth/login {
            limit_req zone=login_limit burst=2 nodelay;
            proxy_pass http://127.0.0.1:8000;
            include /etc/nginx/proxy_params;
        }

        # General API pass-through
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/proxy_params;

        # Security: Don't expose backend errors
        proxy_intercept_errors on;
        error_page 500 502 503 504 = @error_page;
    }

    # Error page (generic, no details)
    location @error_page {
        return 503 '{"success":false,"error":"Service Temporarily Unavailable"}';
        add_header Content-Type application/json always;
    }

    # Restrict /metrics endpoint (Prometheus)
    location /metrics {
        # Only allow from monitoring server
        allow 10.0.0.0/8;     # Internal network
        allow 127.0.0.1;       # Localhost
        deny all;

        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/proxy_params;
    }
}
```

**Test Nginx configuration:**

```bash
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. Celery Task (Audit Log Cleanup)

Create `/opt/lsx/backend/app/tasks/security_tasks.py`:

```python
"""Security maintenance tasks (Phase 20)"""
from celery import Celery
from app.database.connection import execute_query
import logging

logger = logging.getLogger(__name__)

@celery.task
def cleanup_expired_audit_logs():
    """
    Daily task to clean up expired audit logs.
    Runs at 3:00 AM daily.
    """
    try:
        result = execute_query("SELECT cleanup_expired_audit_logs()")
        deleted_count = result[0][0] if result and len(result) > 0 else 0

        logger.info(f"Audit log cleanup completed: {deleted_count} logs deleted")
        return {'status': 'success', 'deleted': deleted_count}

    except Exception as e:
        logger.error(f"Audit log cleanup failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}
```

**Celery Beat Schedule** (in `backend/app/__init__.py` or `celeryconfig.py`):

```python
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'cleanup-audit-logs-daily': {
        'task': 'app.tasks.security_tasks.cleanup_expired_audit_logs',
        'schedule': crontab(hour=3, minute=0),  # 3:00 AM daily
    },
}
```

#### 5. Security Testing

**Test Rate Limiting:**

```bash
# Test login rate limit (should block after 5 attempts)
for i in {1..7}; do
    echo "Attempt $i:"
    curl -X POST https://api.yourdomain.com/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"wrong"}' \
        -w "\nHTTP: %{http_code}\n\n"
    sleep 1
done

# Expected: 401 for attempts 1-5, then 429 (rate limited)
```

**Test Brute-Force Protection:**

```bash
# Trigger account lockout (6th attempt should return 403)
for i in {1..6}; do
    curl -X POST https://api.yourdomain.com/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"wrong"}' \
        -i
done

# Expected: Attempt 6 returns 403 "Account locked for 15 minutes"
```

**Test Security Headers:**

```bash
curl -I https://api.yourdomain.com/api/v1/health

# Expected headers:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Content-Security-Policy: default-src 'self'; ...
```

**Query Audit Logs:**

```bash
# Check recent audit events
sudo -u postgres psql -d lernsystemx_prod -c "
SELECT event_type, user_email, ip_address, action, created_at
FROM audit_logs
ORDER BY created_at DESC
LIMIT 20;
"

# Check failed login attempts
sudo -u postgres psql -d lernsystemx_prod -c "
SELECT user_email, ip_address, COUNT(*) as attempts, MAX(created_at) as last_attempt
FROM audit_logs
WHERE event_type = 'login_failed' AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY user_email, ip_address
ORDER BY attempts DESC;
"
```

### Security Monitoring

Add to Prometheus alerts (`/etc/prometheus/alerts.yml`):

```yaml
groups:
  - name: security_alerts
    rules:
      # Failed login spike
      - alert: HighFailedLoginRate
        expr: rate(audit_logs_total{event_type="login_failed"}[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High failed login rate detected"
          description: "More than 10 failed logins per minute in the last 5 minutes"

      # Account lockouts
      - alert: MultipleAccountLockouts
        expr: increase(audit_logs_total{event_type="account_locked"}[1h]) > 5
        labels:
          severity: warning
        annotations:
          summary: "Multiple account lockouts detected"
          description: "More than 5 accounts locked in the last hour"

      # Permission denied spike
      - alert: PermissionDeniedSpike
        expr: rate(audit_logs_total{event_type="permission_denied"}[5m]) > 5
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "Unusual permission denied rate"
          description: "Potential unauthorized access attempts"
```

### Security Compliance Checklist

Before production deployment:

- [ ] Audit log schema migrated (`audit_logs` table exists)
- [ ] Security environment variables configured
- [ ] Nginx security headers enabled
- [ ] Rate limiting tested and working
- [ ] Brute-force protection tested
- [ ] HTTPS enabled with valid certificate
- [ ] Firewall configured (ports 80, 443 only)
- [ ] Database backups enabled (Phase 18)
- [ ] Monitoring alerts configured (Phase 19 + Phase 20)
- [ ] Celery task for audit log cleanup scheduled
- [ ] `.env.production` contains no secrets (use actual environment variables in production)
- [ ] All default passwords changed
- [ ] SSH key-based authentication enabled (password login disabled)

### Security Documentation

**For complete security architecture and guidelines, see:**
- 👉 **[`docs/security/security-architecture-implementation.md`](../security/security-architecture-implementation.md)**
- 👉 **[`docs/security/sensitive-data-handling.md`](../security/sensitive-data-handling.md)**

---

## Phase 21: API Gateway

### API Gateway Implementation

Phase 21 adds a centralized API Gateway layer for unified request routing, analytics, and multi-tenant support.

**✅ Implemented Features:**
- Gateway Router (route segmentation & organization)
- Gateway Middleware (request validation)
- Gateway Analytics (request tracking & metrics)
- Gateway Rate Limiting (per route group)
- Multi-Tenant Header Processing

### Gateway Configuration

#### 1. Environment Variables

Add to `/opt/lsx/backend/.env.production`:

```env
# ==========================================
# API GATEWAY (Phase 21)
# ==========================================

# Gateway Core Settings
API_GATEWAY_ENABLED=True
API_BASE_PATH=/api/v1
API_VERSION=1

# API Prefixes
API_PUBLIC_PREFIX=/api/v1/public
API_APP_PREFIX=/api/v1
API_ADMIN_PREFIX=/api/v1/admin
API_ORG_PREFIX=/api/v1/organisations

# Gateway Logging & Analytics
API_GATEWAY_LOG_REQUESTS=True
API_GATEWAY_TRACK_ANALYTICS=True
API_GATEWAY_REQUEST_ID_HEADER=X-LSX-Request-ID

# Gateway Rate Limiting (per route group)
API_GATEWAY_RATE_LIMIT_DEFAULT=100 per minute
API_GATEWAY_RATE_LIMIT_ADMIN=200 per minute
API_GATEWAY_RATE_LIMIT_PUBLIC=10 per minute
API_GATEWAY_RATE_LIMIT_KI=30 per minute
API_GATEWAY_RATE_LIMIT_ANALYTICS=60 per minute
API_GATEWAY_RATE_LIMIT_LIVEROOM=100 per minute

# Request Validation
API_GATEWAY_MAX_BODY_SIZE=20971520
API_GATEWAY_VALIDATE_CONTENT_TYPE=True

# Multi-Tenant Domain Routing
API_GATEWAY_MULTI_TENANT_ENABLED=True
API_GATEWAY_DEFAULT_ORG_HEADER=X-LSX-Org-ID
API_GATEWAY_CLIENT_HEADER=X-LSX-Client
```

#### 2. Restart Services

```bash
# Restart Gunicorn/uWSGI
sudo systemctl restart lsx-backend

# Reload Nginx (if needed)
sudo systemctl reload nginx

# Verify logs
journalctl -u lsx-backend -n 50 --no-pager
```

#### 3. Testing Gateway

**Test Request Headers:**

```bash
curl -I https://api.yourdomain.com/api/v1/health

# Expected headers:
# X-LSX-Request-ID: <uuid>
# X-LSX-API-Version: 1
```

**Test Multi-Tenant Headers:**

```bash
curl https://api.yourdomain.com/api/v1/courses \
  -H "Authorization: Bearer <token>" \
  -H "X-LSX-Org-ID: 51" \
  -H "X-LSX-Client: web"
```

**Test Rate Limiting (Admin):**

```bash
# Should handle 200 requests/min before limiting
for i in {1..210}; do
    curl https://api.yourdomain.com/api/v1/admin/analytics \
        -H "Authorization: Bearer <admin-token>" \
        -w "\nRequest $i: %{http_code}\n"
    sleep 0.3
done

# Expected: 200 for first ~200, then 429
```

**Test Request Size Limit:**

```bash
# Generate 25MB payload (exceeds 20MB limit)
dd if=/dev/zero bs=1M count=25 | \
    curl -X POST https://api.yourdomain.com/api/v1/courses \
    -H "Authorization: Bearer <token>" \
    -H "Content-Type: application/json" \
    --data-binary @-

# Expected: 413 Request Entity Too Large
```

### Gateway Monitoring

Gateway metrics are automatically integrated with Prometheus (Phase 19).

**Prometheus Queries:**

```promql
# Requests per minute by route group
sum(rate(http_requests_total[5m])) by (route_group)

# Admin API usage
sum(rate(http_requests_total{route_group="admin"}[5m]))

# Error rate by route group
sum(rate(http_requests_total{status=~"5.."}[5m])) by (route_group)

# P95 latency by route group
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) by (route_group)
```

**Grafana Dashboard:**

Create panels for:
- Request rate per route group (public/app/admin/org)
- Error rate by route group
- Average response time by route group
- Rate limit hits per group

### Gateway Logging

Gateway logs include request tracking:

```bash
# View gateway request logs
journalctl -u lsx-backend --since "1 hour ago" | grep "Gateway:"

# Example log entry:
# Gateway: {'request_id': 'abc-123', 'route_group': 'admin', 'method': 'GET',
#           'path': '/api/v1/admin/analytics', 'status': 200, 'duration_ms': 45.2,
#           'user_id': 123, 'org_id': 5, 'ip': '192.168.1.100'}
```

### Gateway Route Groups

| Route Group | Prefix | Rate Limit | Purpose |
|-------------|--------|------------|---------|
| **Public** | `/api/v1/public/*` | 10/min | Public APIs (future) |
| **Auth** | `/api/v1/auth/*` | 5/min | Authentication |
| **App** | `/api/v1/*` | 100/min | User/App APIs |
| **Admin** | `/api/v1/admin/*` | 200/min | Admin APIs |
| **Org** | `/api/v1/organisations/*` | 100/min | Organisation APIs |
| **Health** | `/health`, `/metrics` | unlimited | Monitoring |

### Troubleshooting

**Gateway disabled:**
```bash
# Check if gateway is enabled
grep API_GATEWAY_ENABLED /opt/lsx/backend/.env.production

# Should show: API_GATEWAY_ENABLED=True
```

**Missing request ID header:**
```bash
# Verify gateway analytics is enabled
grep API_GATEWAY_TRACK_ANALYTICS /opt/lsx/backend/.env.production

# Restart if needed
sudo systemctl restart lsx-backend
```

**Rate limits too strict:**
```bash
# Adjust limits in .env.production
nano /opt/lsx/backend/.env.production

# Example: Increase admin limit
API_GATEWAY_RATE_LIMIT_ADMIN=500 per minute

# Restart
sudo systemctl restart lsx-backend
```

### Gateway Documentation

**For complete API Gateway architecture and usage, see:**
- 👉 **[`docs/architecture/api-gateway-implementation.md`](../architecture/api-gateway-implementation.md)**

---

## Phase 22: API Versioning & Change Management

Phase 22 implements comprehensive API versioning, deprecation management, and change control for LernsystemX.

### Versioning Configuration

**Environment Variables (`/opt/lsx/backend/.env.production`):**

```env
# ==========================================
# API VERSIONING & CHANGE MANAGEMENT (Phase 22)
# ==========================================

# System Version (Semantic Versioning: MAJOR.MINOR.PATCH)
LSX_VERSION=1.0.0
LSX_ENV=production

# API Version Configuration
API_VERSION_CURRENT=1
API_VERSION_SUPPORTED=1
API_VERSION_DEFAULT=1

# API Version Headers
API_VERSION_HEADER=X-LSX-API-Version
API_SYSTEM_VERSION_HEADER=X-LSX-System-Version

# Deprecation Configuration
API_DEPRECATION_ENABLED=True
API_DEPRECATION_HEADER=X-LSX-Deprecated
API_DEPRECATION_DATE_HEADER=X-LSX-Deprecation-Date
API_SUNSET_DATE_HEADER=X-LSX-Sunset-Date
API_MIGRATION_GUIDE_HEADER=X-LSX-Migration-Guide
API_REPLACEMENT_HEADER=X-LSX-Replacement

# Deprecation Notice URL
API_DEPRECATION_NOTICE_URL=https://docs.lernsystemx.de/api/deprecation-notices

# Version Support Window (in months)
API_VERSION_SUPPORT_WINDOW=12
API_VERSION_DEPRECATION_WARNING=6

# Version Detection Strategy (url, header, both)
API_VERSION_DETECTION=url
API_VERSION_ALLOW_HEADER_OVERRIDE=False

# Breaking Change Protection
API_ENFORCE_VERSION_CHECK=True
API_REJECT_UNSUPPORTED_VERSIONS=True
```

### Version Detection Test

```bash
# Test version headers
curl -I https://yourdomain.com/api/v1/health

# Expected headers:
# HTTP/2 200
# x-lsx-api-version: 1
# x-lsx-system-version: 1.0.0
```

### Admin Version Endpoints

**Get System Version Info:**
```bash
# Requires admin authentication
curl https://yourdomain.com/api/v1/admin/system/version \
    -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response:**
```json
{
    "success": true,
    "data": {
        "system": {
            "version": "1.0.0",
            "environment": "production",
            "python_version": "3.12.0"
        },
        "api": {
            "current_version": 1,
            "supported_versions": [1],
            "default_version": 1,
            "support_window_months": 12,
            "deprecation_warning_months": 6
        },
        "detection": {
            "strategy": "url",
            "allow_header_override": false
        },
        "deprecation": {
            "enabled": true,
            "notice_url": "https://docs.lernsystemx.de/api/deprecation-notices"
        }
    }
}
```

**List Deprecated Endpoints:**
```bash
curl https://yourdomain.com/api/v1/admin/system/deprecated-endpoints \
    -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Version Update Procedure

**When releasing a new API version (e.g., v1 → v2):**

1. **Implement v2 endpoints:**
```bash
# Deploy new code with v2 endpoints
cd /opt/lsx/backend
git pull origin main
sudo systemctl restart lsx-backend
```

2. **Update environment:**
```bash
nano /opt/lsx/backend/.env.production

# Update versions
API_VERSION_CURRENT=2
API_VERSION_SUPPORTED=1,2  # Support both during transition
API_VERSION_DEFAULT=2

# Restart
sudo systemctl restart lsx-backend
```

3. **Monitor deprecated usage:**
```bash
# Check logs for deprecated endpoint calls
grep "deprecated_endpoint_usage" /var/log/lsx/application.log

# Get deprecation report
curl https://yourdomain.com/api/v1/admin/system/deprecated-endpoints \
    -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

4. **After support window (12 months), sunset v1:**
```bash
nano /opt/lsx/backend/.env.production

# Remove v1 from supported versions
API_VERSION_SUPPORTED=2

# Restart
sudo systemctl restart lsx-backend
```

### Database Migration Management

**Migration Workflow:**

1. **Create migration files:**
```bash
cd /opt/lsx/backend/migrations

# Example migration
nano 20250115_001_add_course_version_up.sql
nano 20250115_001_add_course_version_down.sql
```

2. **Test on staging:**
```bash
# On staging server
psql -U lernsystemx -d lernsystemx_staging \
    -f migrations/20250115_001_add_course_version_up.sql

# Verify
psql -U lernsystemx -d lernsystemx_staging \
    -c "SELECT * FROM migration_history ORDER BY executed_at DESC LIMIT 1;"
```

3. **Backup production database:**
```bash
# Create backup before migration
sudo -u postgres pg_dump lernsystemx_prod > \
    /var/backups/postgresql/pre_migration_$(date +%Y%m%d_%H%M%S).sql
```

4. **Execute migration:**
```bash
# Run migration on production
psql -U lernsystemx -d lernsystemx_prod \
    -f migrations/20250115_001_add_course_version_up.sql

# Record in migration history (automatic if using migration tool)
```

5. **Verify migration:**
```bash
# Check migration history
psql -U lernsystemx -d lernsystemx_prod \
    -c "SELECT * FROM migration_history ORDER BY executed_at DESC LIMIT 5;"

# Restart application
sudo systemctl restart lsx-backend

# Check logs
sudo journalctl -u lsx-backend -f
```

### Rollback Migration

```bash
# Rollback last migration
psql -U lernsystemx -d lernsystemx_prod \
    -f migrations/20250115_001_add_course_version_down.sql

# Update migration history
psql -U lernsystemx -d lernsystemx_prod \
    -c "DELETE FROM migration_history WHERE migration_name = '20250115_001_add_course_version';"

# Restart application
sudo systemctl restart lsx-backend
```

### Version Monitoring

**Prometheus Queries (if monitoring enabled):**

```promql
# API version usage
sum(rate(http_requests_total[5m])) by (api_version)

# Deprecated endpoint calls
sum(rate(deprecated_endpoint_calls[5m])) by (endpoint)
```

**Log Analysis:**

```bash
# Count requests per API version
grep "X-LSX-API-Version" /var/log/nginx/access.log | \
    awk '{print $NF}' | sort | uniq -c

# Find deprecated endpoint calls
grep "deprecated_endpoint_usage" /var/log/lsx/application.log | \
    jq -r '.endpoint' | sort | uniq -c | sort -rn
```

### Troubleshooting

**Unsupported version error:**
```bash
# Error: "API v99 is not supported"
# Fix: Check API_VERSION_SUPPORTED in .env.production

grep API_VERSION_SUPPORTED /opt/lsx/backend/.env.production
# Should be: API_VERSION_SUPPORTED=1,2 (or just current version)
```

**Version headers not appearing:**
```bash
# Verify versioning is enabled
grep API_GATEWAY_ENABLED /opt/lsx/backend/.env.production

# Check if versioning middleware is loaded
sudo journalctl -u lsx-backend | grep "API Version Management initialized"

# Restart if needed
sudo systemctl restart lsx-backend
```

**Deprecation headers missing:**
```bash
# Verify deprecation is enabled
grep API_DEPRECATION_ENABLED /opt/lsx/backend/.env.production

# Should be: API_DEPRECATION_ENABLED=True

# Restart
sudo systemctl restart lsx-backend
```

### Versioning Documentation

**For complete API versioning architecture and strategies, see:**
- 👉 **[`docs/architecture/versioning-implementation.md`](../architecture/versioning-implementation.md)**
- 👉 **[`docs/architecture/database-migration-strategy.md`](../architecture/database-migration-strategy.md)**

---

## Next Steps

1. **✅ Setup Monitoring:** Prometheus/Grafana configured (Phase 19)
2. **✅ Backups:** Automated backups configured (Phase 18)
3. **✅ Security Hardening:** RBAC, Rate Limiting, Audit Logs configured (Phase 20)
4. **✅ API Gateway:** Centralized routing, analytics, multi-tenant support (Phase 21)
5. **✅ API Versioning:** Version detection, deprecation management, migration strategy (Phase 22)
6. **CI/CD Pipeline:** GitHub Actions / GitLab CI (Future)
7. **Load Balancer:** For high-availability deployments (Future)
8. **CDN:** CloudFlare or AWS CloudFront for static assets (Future)

---

**Document Version:** 1.5
**Phases:** 17 (Deployment) + 18 (Backup & Recovery) + 19 (Monitoring & Alerting) + 20 (Security Hardening) + 21 (API Gateway) + 22 (Versioning & Change Management)
**Last Updated:** 2025-01-18
**Status:** ✅ Production-Ready
