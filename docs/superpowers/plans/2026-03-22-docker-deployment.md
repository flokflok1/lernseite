# Docker + Cloudflare Beta Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Containerize LernsystemX (Frontend + Backend + Celery) and deploy to srv01-docker01 with Cloudflare Tunnel access.

**Architecture:** 3 Docker containers in separate VLANs (50, 51, 53) with macvlan networking. Existing cloudflared, PostgreSQL, and Redis are reused. Auto-deploy via rsync + docker compose from dev02.

**Tech Stack:** Docker Compose v5, nginx:alpine, python:3.12-slim, node:20-alpine, macvlan networking, Cloudflare Tunnel

**Spec:** `docs/superpowers/specs/2026-03-22-docker-cloudflare-beta-design.md`

**IPs:** frontend=10.0.50.4, backend=10.0.51.4, celery=10.0.53.3

---

## File Map

### New files (docker/)
| File | Responsibility |
|------|---------------|
| `docker/backend/Dockerfile` | Python 3.12 image with requirements, psycopg3 deps |
| `docker/frontend/Dockerfile` | Multi-stage: Node 20 build → nginx:alpine |
| `docker/frontend/nginx.conf` | SPA routing + reverse proxy to backend + WebSocket |
| `docker/docker-compose.yml` | 3 services (frontend, backend, celery) + macvlan networks |
| `docker/.env.docker.example` | Template with CHANGE_ME placeholders |
| `docker/deploy.sh` | rsync + docker compose build/up from dev02 |

### Modified files (code fixes)
| File | Change |
|------|--------|
| `backend/wsgi.py` | eventlet monkey-patch (conditional on ENV) + celery export |
| `backend/app/setup/diagnostics/install.py:24` | INSTALL_MARKER_FILE from ENV |
| `backend/app/setup/diagnostics/install.py:27-40` | LSX_SKIP_SETUP support |
| `backend/app/setup/diagnostics/install.py:106-130` | Skip frontend marker in Docker |
| `backend/app/setup/diagnostics/verification/verify_part2.py:152` | Use InstallationChecker constant |
| `.gitignore` | Add `docker/.env.docker` |

---

## Task 1: Update spec with final IPs

**Files:**
- Modify: `docs/superpowers/specs/2026-03-22-docker-cloudflare-beta-design.md`

Must happen first — spec is the reference for pfSense rules and tunnel config.

- [ ] **Step 1: Replace all old IPs in the spec**

Replace throughout the spec file:
- `10.0.50.2` → `10.0.50.4` (frontend)
- `10.0.51.2` → `10.0.51.4` (backend)

This affects: container topology table, traffic-flow diagram, macvlan commands, pfSense rules, nginx config, docker-compose, Cloudflare tunnel route.

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/specs/2026-03-22-docker-cloudflare-beta-design.md
git commit -m "docs: update spec with final IPs (frontend=10.0.50.4, backend=10.0.51.4)"
```

---

## Task 2: Fix wsgi.py — eventlet monkey-patching + celery export

**Files:**
- Modify: `backend/wsgi.py`

eventlet must monkey-patch the standard library BEFORE any other import. Without this, psycopg3 pool threads deadlock under load and SocketIO breaks.

The patching is conditional on `GUNICORN_WORKER_CLASS=eventlet` (set in `.env.docker` and Dockerfile ENV). This is safe because:
- **Docker (backend):** ENV is set in Dockerfile → always patches
- **Docker (celery):** ENV comes from `.env.docker` (env_file) → always patches
- **Dev (python run.py):** ENV not set → no patching (dev server doesn't need it)

- [ ] **Step 1: Modify wsgi.py**

Replace the entire file with:

```python
"""
WSGI Entry Point for Production Deployment

Used by Gunicorn:
    gunicorn -c config/gunicorn.conf.py wsgi:app

With eventlet (Docker production):
    GUNICORN_WORKER_CLASS=eventlet gunicorn -c config/gunicorn.conf.py wsgi:app

CRITICAL: eventlet.monkey_patch() MUST be called before ANY other imports.
This ensures psycopg3 pool threads and Flask-SocketIO work correctly.
The GUNICORN_WORKER_CLASS env var is set in docker/.env.docker and the Dockerfile.
"""

import os

# Monkey-patch stdlib if using eventlet worker class.
# Must happen BEFORE any other imports (psycopg3, flask, etc.).
# In Docker: always set via Dockerfile ENV + .env.docker.
# In dev: not set, so no patching (flask dev server doesn't need it).
if os.environ.get('GUNICORN_WORKER_CLASS') == 'eventlet':
    import eventlet
    eventlet.monkey_patch()

from app import create_app, socketio
from app.core.bootstrap.extensions import db_pool, celery

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    app.run()
```

- [ ] **Step 2: Verify app still starts in dev mode**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from wsgi import app; print('OK')"`
Expected: `OK` (no eventlet patching since GUNICORN_WORKER_CLASS not set)

- [ ] **Step 3: Commit**

```bash
git add backend/wsgi.py
git commit -m "fix(wsgi): add conditional eventlet monkey-patching + celery export for Docker"
```

---

## Task 3: Fix InstallationChecker — ENV-based marker path + Docker skip

**Files:**
- Modify: `backend/app/setup/diagnostics/install.py`
- Modify: `backend/app/setup/diagnostics/verification/verify_part2.py`

- [ ] **Step 1: Modify INSTALL_MARKER_FILE (line 24)**

Change from:
```python
INSTALL_MARKER_FILE = '.lsx-installed'
```
to:
```python
INSTALL_MARKER_FILE = os.environ.get('LSX_INSTALL_MARKER', '.lsx-installed')
```

- [ ] **Step 2: Add LSX_SKIP_SETUP support to is_installed() (line 27-40)**

Replace the method body:
```python
@staticmethod
def is_installed() -> bool:
    """
    Check if system is installed

    Returns:
        bool: True if installation completed, False otherwise
    """
    # Docker: skip setup wizard if LSX_SKIP_SETUP=true (existing DB)
    if os.environ.get('LSX_SKIP_SETUP', '').lower() == 'true':
        # Auto-create marker if it doesn't exist
        if not os.path.exists(InstallationChecker.INSTALL_MARKER_FILE):
            InstallationChecker.mark_as_installed(
                version='docker-skip',
                database_version='existing'
            )
        return True
    return os.path.exists(InstallationChecker.INSTALL_MARKER_FILE)
```

- [ ] **Step 3: Skip frontend marker write in Docker (mark_as_installed, lines ~110-130)**

Wrap the frontend marker block with Docker check:
```python
# Skip frontend marker in Docker (frontend is a separate container)
if not os.environ.get('DOCKER'):
    try:
        frontend_marker_path = os.path.join(...)
        # ... existing frontend marker code ...
    except Exception as fe:
        print(f"[Install Check] Warning: Could not create frontend marker: {fe}")
```

- [ ] **Step 4: Fix verify_part2.py hardcoded path (line 152)**

Change from:
```python
marker_file = '.lsx-installed'
```
to:
```python
from app.setup.diagnostics.install import InstallationChecker
marker_file = InstallationChecker.INSTALL_MARKER_FILE
```

- [ ] **Step 5: Verify dev still works**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app.setup.diagnostics.install import InstallationChecker; print(InstallationChecker.INSTALL_MARKER_FILE)"`
Expected: `.lsx-installed` (default, no ENV set)

- [ ] **Step 6: Commit**

```bash
git add backend/app/setup/diagnostics/install.py backend/app/setup/diagnostics/verification/verify_part2.py
git commit -m "fix(setup): make install marker path configurable via ENV for Docker"
```

---

## Task 4: Create Backend Dockerfile

**Files:**
- Create: `docker/backend/Dockerfile`

- [ ] **Step 1: Create docker/backend/Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg3 (libpq) and health checks (wget)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc wget && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (cache layer)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create data directories
RUN mkdir -p uploads logs data

EXPOSE 8000

# Worker class controlled by GUNICORN_WORKER_CLASS env var (read in wsgi.py)
ENV GUNICORN_WORKER_CLASS=eventlet

CMD ["gunicorn", "-c", "config/gunicorn.conf.py", "wsgi:app"]
```

- [ ] **Step 2: Commit**

```bash
git add docker/backend/Dockerfile
git commit -m "feat(docker): add backend Dockerfile with python 3.12 + psycopg3"
```

---

## Task 5: Create Frontend Dockerfile + Nginx Config

**Files:**
- Create: `docker/frontend/Dockerfile`
- Create: `docker/frontend/nginx.conf`

- [ ] **Step 1: Create docker/frontend/Dockerfile**

```dockerfile
# Stage 1: Build Vue app
FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 2: Create docker/frontend/nginx.conf**

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # SPA Routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API Reverse Proxy
    location /api/ {
        proxy_pass http://10.0.51.4:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        client_max_body_size 50M;
    }

    # WebSocket (Flask-SocketIO)
    location /socket.io/ {
        proxy_pass http://10.0.51.4:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # Setup Wizard
    location /setup/ {
        proxy_pass http://10.0.51.4:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health endpoint
    location /health {
        proxy_pass http://10.0.51.4:8000;
        proxy_set_header Host $host;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
    gzip_min_length 256;
    gzip_vary on;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add docker/frontend/Dockerfile docker/frontend/nginx.conf
git commit -m "feat(docker): add frontend multi-stage Dockerfile + nginx reverse proxy"
```

---

## Task 6: Create docker-compose.yml

**Files:**
- Create: `docker/docker-compose.yml`

- [ ] **Step 1: Create docker/docker-compose.yml**

```yaml
services:
  frontend:
    build:
      context: ..
      dockerfile: docker/frontend/Dockerfile
    container_name: lsx-frontend
    restart: unless-stopped
    networks:
      macvlan50:
        ipv4_address: 10.0.50.4
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:80"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

  backend:
    build:
      context: ..
      dockerfile: docker/backend/Dockerfile
    container_name: lsx-backend
    restart: unless-stopped
    env_file: .env.docker
    volumes:
      - lsx-uploads:/app/uploads
      - lsx-logs:/app/logs
      - lsx-data:/app/data
    working_dir: /app
    networks:
      macvlan51:
        ipv4_address: 10.0.51.4
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  celery:
    build:
      context: ..
      dockerfile: docker/backend/Dockerfile
    container_name: lsx-celery
    restart: unless-stopped
    env_file: .env.docker
    volumes:
      - lsx-uploads:/app/uploads
      - lsx-logs:/app/logs
    working_dir: /app
    command: celery -A wsgi:celery worker --loglevel=info
    networks:
      macvlan53:
        ipv4_address: 10.0.53.3

volumes:
  lsx-uploads:
    name: lsx-uploads
  lsx-logs:
    name: lsx-logs
  lsx-data:
    name: lsx-data

networks:
  macvlan50:
    external: true
  macvlan51:
    external: true
  macvlan53:
    external: true
```

- [ ] **Step 2: Commit**

```bash
git add docker/docker-compose.yml
git commit -m "feat(docker): add docker-compose with 3 services + macvlan networking"
```

---

## Task 7: Create .env.docker.example + deploy.sh + .gitignore

**Files:**
- Create: `docker/.env.docker.example`
- Create: `docker/deploy.sh`
- Modify: `.gitignore`

- [ ] **Step 1: Create docker/.env.docker.example**

```env
# LernsystemX Docker Production Environment
# Copy to .env.docker and fill in values
# NEVER commit .env.docker to git!

# === Flask ===
FLASK_ENV=production
SECRET_KEY=CHANGE_ME_random_64_chars
DEBUG=False
DOCKER=1

# === Database (external — srv01-db01) ===
DATABASE_URL=postgresql://lsx_user:CHANGE_ME@db.internal.example:5432/lernsystemx
DB_HOST=db.internal.example
DB_PORT=5432
DB_NAME=lernsystemx
DB_USER=lsx_user
DB_PASSWORD=CHANGE_ME

# === Redis (external — 10.0.43.2) ===
REDIS_URL=redis://10.0.43.2:6379/0
REDIS_HOST=10.0.43.2
REDIS_PORT=6379

# === Celery ===
CELERY_BROKER_URL=redis://10.0.43.2:6379/1
CELERY_RESULT_BACKEND=redis://10.0.43.2:6379/2

# === JWT ===
JWT_SECRET_KEY=CHANGE_ME_random_64_chars
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# === AI APIs ===
ANTHROPIC_API_KEY=CHANGE_ME
OPENAI_API_KEY=CHANGE_ME
DEEPL_API_KEY=CHANGE_ME

# === CORS (change domain here!) ===
FRONTEND_URL=https://CHANGE_ME_DOMAIN
CORS_ORIGINS=https://CHANGE_ME_DOMAIN
SOCKETIO_CORS_ALLOWED_ORIGINS=https://CHANGE_ME_DOMAIN

# === SocketIO ===
SOCKETIO_MESSAGE_QUEUE=redis://10.0.43.2:6379/3

# === Session ===
SESSION_TYPE=redis
SESSION_REDIS_URL=redis://10.0.43.2:6379/5

# === Rate Limiting ===
RATELIMIT_STORAGE_URL=redis://10.0.43.2:6379/4

# === Docker-specific ===
LSX_INSTALL_MARKER=/app/data/.lsx-installed
GUNICORN_WORKER_CLASS=eventlet
# Set to 'true' to skip setup wizard (existing DB)
# LSX_SKIP_SETUP=true

# === Logging ===
LOG_LEVEL=WARNING
```

- [ ] **Step 2: Create docker/deploy.sh**

```bash
#!/bin/bash
set -e

DOCKER_HOST="srv01-docker01-dockeradm"
PROJECT_DIR="/home/pascal/Lernsystem"
REMOTE_DIR="/opt/lsx"

echo "=== LSX Deploy ==="
echo "Syncing code to $DOCKER_HOST..."

# Sync code to Docker host (protect .env.docker on remote!)
rsync -avz --delete \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='.env.docker' \
  --exclude='*.pyc' \
  --exclude='.superpowers' \
  --exclude='.worktrees' \
  --exclude='backend/logs/*' \
  --exclude='backend/uploads/*' \
  "$PROJECT_DIR/" "$DOCKER_HOST:$REMOTE_DIR/"

echo "Building and restarting containers..."

# Build images + restart containers on Docker host
ssh "$DOCKER_HOST" "cd $REMOTE_DIR/docker && docker compose build --parallel && docker compose up -d"

echo ""
echo "=== Deploy complete ==="
echo "Frontend: http://10.0.50.4"
echo "Backend:  http://10.0.51.4:8000"
ssh "$DOCKER_HOST" "docker ps --filter name=lsx --format 'table {{.Names}}\t{{.Status}}'"
```

- [ ] **Step 3: Make deploy.sh executable**

```bash
chmod +x docker/deploy.sh
```

- [ ] **Step 4: Add docker/.env.docker to .gitignore**

Append to `.gitignore`:
```
# Docker production env (contains secrets)
docker/.env.docker
```

- [ ] **Step 5: Commit**

```bash
git add docker/.env.docker.example docker/deploy.sh .gitignore
git commit -m "feat(docker): add env template, deploy script, gitignore update"
```

---

## Task 8: Setup Docker Host Infrastructure

**Files:** None (remote commands on srv01-docker01)

Prerequisites for `docker compose up`. Creates VLAN interfaces and macvlan networks.

- [ ] **Step 1: Create VLAN interfaces on Docker host**

```bash
ssh srv01-docker01-dockeradm "
  ip link show ens19.50 2>/dev/null || (ip link add link ens19 name ens19.50 type vlan id 50 && ip link set ens19.50 up)
  ip link show ens19.51 2>/dev/null || (ip link add link ens19 name ens19.51 type vlan id 51 && ip link set ens19.51 up)
  echo 'VLAN interfaces ready'
"
```

- [ ] **Step 2: Create macvlan50 network**

```bash
ssh srv01-docker01-dockeradm "
  docker network inspect macvlan50 >/dev/null 2>&1 || \
  docker network create -d macvlan \
    --subnet=10.0.50.0/29 \
    --ip-range=10.0.50.4/32 \
    --gateway=10.0.50.1 \
    -o parent=ens19.50 \
    macvlan50
  echo 'macvlan50 ready'
"
```

- [ ] **Step 3: Create macvlan51 network**

```bash
ssh srv01-docker01-dockeradm "
  docker network inspect macvlan51 >/dev/null 2>&1 || \
  docker network create -d macvlan \
    --subnet=10.0.51.0/29 \
    --ip-range=10.0.51.4/32 \
    --gateway=10.0.51.1 \
    -o parent=ens19.51 \
    macvlan51
  echo 'macvlan51 ready'
"
```

- [ ] **Step 4: Verify macvlan53 exists**

```bash
ssh srv01-docker01-dockeradm "docker network inspect macvlan53 >/dev/null 2>&1 && echo 'macvlan53 OK' || echo 'ERROR: macvlan53 does not exist!'"
```

Expected: `macvlan53 OK`. If not, create it:
```bash
ssh srv01-docker01-dockeradm "
  docker network create -d macvlan \
    --subnet=10.0.53.0/29 \
    --ip-range=10.0.53.3/32 \
    --gateway=10.0.53.1 \
    -o parent=ens19.53 \
    macvlan53
"
```

- [ ] **Step 5: Create remote project directory + copy .env.docker template**

```bash
ssh srv01-docker01-dockeradm "mkdir -p /opt/lsx/docker"
scp docker/.env.docker.example srv01-docker01-dockeradm:/opt/lsx/docker/.env.docker
echo "IMPORTANT: Edit /opt/lsx/docker/.env.docker on Docker host with real credentials!"
```

- [ ] **Step 6: Verify all 3 networks exist**

```bash
ssh srv01-docker01-dockeradm "docker network ls | grep macvlan5"
```

Expected: macvlan50, macvlan51, macvlan53 all listed.

---

## Task 9: pfSense Firewall Rules + Cloudflare Tunnel (MANUAL — user does this)

**Files:** None (pfSense WebGUI + Cloudflare Dashboard)

These 8 firewall rules and the tunnel route must be configured before the containers can communicate. Print the rules for the user and pause.

- [ ] **Step 1: Print pfSense rules for user**

Display these rules — user configures them in pfSense WebGUI:

| # | VLAN (Source) | Von | Nach | Port | Protokoll | Beschreibung |
|---|---------------|-----|------|------|-----------|--------------|
| 1 | VLAN 30 | 10.0.30.4 | 10.0.50.4 | 80 | TCP | cloudflared → Frontend |
| 2 | VLAN 50 | 10.0.50.4 | 10.0.51.4 | 8000 | TCP | Frontend → Backend |
| 3 | VLAN 51 | 10.0.51.4 | db.internal.example | 5432 | TCP | Backend → PostgreSQL |
| 4 | VLAN 51 | 10.0.51.4 | 10.0.43.2 | 6379 | TCP | Backend → Redis |
| 5 | VLAN 53 | 10.0.53.3 | db.internal.example | 5432 | TCP | Celery → PostgreSQL |
| 6 | VLAN 53 | 10.0.53.3 | 10.0.43.2 | 6379 | TCP | Celery → Redis |
| 7 | VLAN 51 | 10.0.51.4 | ANY | 443 | TCP | Backend → AI APIs |
| 8 | VLAN 53 | 10.0.53.3 | ANY | 443 | TCP | Celery → AI APIs |

- [ ] **Step 2: Print Cloudflare Tunnel config for user**

Cloudflare Dashboard → Zero Trust → Networks → Tunnels → Public Hostname:

| Public Hostname | Service | WebSocket |
|----------------|---------|-----------|
| (trycloudflare.com or custom domain) | http://10.0.50.4:80 | Enabled |

- [ ] **Step 3: User confirms rules and tunnel are configured**

Wait for user confirmation before proceeding to deploy.

---

## Task 10: First Deploy + Smoke Test

**Files:** None (deploy + verify)

- [ ] **Step 1: Run deploy script**

```bash
cd /home/pascal/Lernsystem && ./docker/deploy.sh
```

- [ ] **Step 2: Check containers are running**

```bash
ssh srv01-docker01-dockeradm "docker ps --filter name=lsx"
```

Expected: 3 containers (lsx-frontend, lsx-backend, lsx-celery) all Up.

- [ ] **Step 3: Test frontend serves HTML**

```bash
ssh srv01-docker01-dockeradm "wget -q -O- http://10.0.50.4 | head -5"
```

Expected: HTML with `<div id="app">` (Vue SPA).

- [ ] **Step 4: Test backend health endpoint**

```bash
ssh srv01-docker01-dockeradm "wget -q -O- http://10.0.51.4:8000/health"
```

Expected: JSON response (healthy or setup-needed).

- [ ] **Step 5: Test nginx reverse proxy**

```bash
ssh srv01-docker01-dockeradm "wget -q -O- http://10.0.50.4/setup/status"
```

Expected: JSON response from backend (proxied through nginx).

- [ ] **Step 6: Check logs for errors**

```bash
ssh srv01-docker01-dockeradm "docker logs lsx-backend --tail 20"
ssh srv01-docker01-dockeradm "docker logs lsx-celery --tail 20"
```

Expected: No critical errors. Celery should show "ready" message.
