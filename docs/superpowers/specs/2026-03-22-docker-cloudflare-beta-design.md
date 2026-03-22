# LernsystemX Docker + Cloudflare Beta Deployment — Design Spec

**Datum:** 2026-03-22
**Status:** REVIEWED
**Ziel:** LernsystemX als Docker-Stack auf srv01-docker01 deployen mit Cloudflare Tunnel

---

## 1. Architektur-Uebersicht

### Container-Topologie

3 neue Container auf srv01-docker01, jeder in eigenem VLAN mit /32 IPAM-Range:

| Container | VLAN | macvlan | IP | IPAM Range | Funktion |
|-----------|------|---------|-----|------------|----------|
| lsx-frontend | 50 (APP_Web) | macvlan50 | 10.0.50.4 | /32 | Nginx + Vite Build + Reverse Proxy |
| lsx-backend | 51 (APP_API) | macvlan51 | 10.0.51.4 | /32 | Gunicorn + eventlet (Flask API + SocketIO) |
| lsx-celery | 53 (APP_Worker) | macvlan53 | 10.0.53.3 | /32 | Celery Worker (Background Jobs) |

**Isolation:** Container sind in **getrennten VLANs** (50, 51, 53). Die /32 IPAM-Range stellt sicher, dass Docker nur eine IP pro Netzwerk zuweist. Layer-2 Isolation kommt primaer durch die VLAN-Trennung, Layer-3 Routing immer ueber pfSense.

### Bestehende Infrastruktur (wird wiederverwendet)

| Dienst | VLAN | IP | Status |
|--------|------|----|--------|
| cloudflared | 30 (SVC_Proxy) | 10.0.30.4 (macvlan30) | Laeuft bereits |
| NPM | 30 (SVC_Proxy) | 10.0.30.2 | Laeuft bereits (wird NICHT genutzt fuer LSX) |
| PostgreSQL | 40 (DB_PostgreSQL) | db.internal.example | srv01-db01 |
| Redis | 43 (DB_Redis) | 10.0.43.2 | Docker Container |

### Traffic-Flow

```
Internet → Cloudflare Edge → cloudflared (10.0.30.4) → lsx-frontend (10.0.50.4:80)
                                                              |
                                                              | /api/* + /socket.io/* + /setup/*
                                                              ↓
                                                        lsx-backend (10.0.51.4:8000)
                                                              |
                                              ┌───────────────┼───────────────┐
                                              ↓               ↓               ↓
                                        PostgreSQL      Redis          AI APIs (443)
                                        db.internal.example       10.0.43.2      (ausgehend)
                                              ↑
                                              |
                                        lsx-celery (10.0.53.3)
                                              |
                                              ↓
                                           Redis (Queue)
                                           10.0.43.2
```

---

## 2. Netzwerk

### Neue macvlan-Netzwerke

```bash
# macvlan50 (VLAN 50 - APP_Web)
docker network create -d macvlan \
  --subnet=10.0.50.0/29 \
  --ip-range=10.0.50.4/32 \
  --gateway=10.0.50.1 \
  -o parent=ens19.50 \
  macvlan50

# macvlan51 (VLAN 51 - APP_API)
docker network create -d macvlan \
  --subnet=10.0.51.0/29 \
  --ip-range=10.0.51.4/32 \
  --gateway=10.0.51.1 \
  -o parent=ens19.51 \
  macvlan51

# macvlan53 existiert bereits
```

### VLAN Interfaces (auf Docker Host)

```bash
# Pruefen/erstellen:
ip link show ens19.50 || (ip link add link ens19 name ens19.50 type vlan id 50 && ip link set ens19.50 up)
ip link show ens19.51 || (ip link add link ens19 name ens19.51 type vlan id 51 && ip link set ens19.51 up)
```

### pfSense Firewall-Regeln

| # | Von | Nach | Port | Protokoll | Beschreibung |
|---|-----|------|------|-----------|--------------|
| 1 | 10.0.30.4 (cloudflared) | 10.0.50.4 | 80 | TCP | Tunnel → Frontend |
| 2 | 10.0.50.4 | 10.0.51.4 | 8000 | TCP | Frontend → Backend (API + WS) |
| 3 | 10.0.51.4 | db.internal.example | 5432 | TCP | Backend → PostgreSQL |
| 4 | 10.0.51.4 | 10.0.43.2 | 6379 | TCP | Backend → Redis |
| 5 | 10.0.53.3 | db.internal.example | 5432 | TCP | Celery → PostgreSQL |
| 6 | 10.0.53.3 | 10.0.43.2 | 6379 | TCP | Celery → Redis |
| 7 | 10.0.51.4 | ANY | 443 | TCP | Backend → AI APIs |
| 8 | 10.0.53.3 | ANY | 443 | TCP | Celery → AI APIs |

---

## 3. Docker-Konfiguration

### Verzeichnisstruktur

```
docker/
├── docker-compose.yml
├── .env.docker                 # Credentials (NICHT in Git!)
├── .env.docker.example         # Template
├── backend/
│   └── Dockerfile
├── frontend/
│   ├── Dockerfile
│   └── nginx.conf
└── deploy.sh                   # Auto-Deploy von dev02
```

### Backend Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# System deps fuer psycopg3
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Data directories
RUN mkdir -p uploads logs data

EXPOSE 8000

# eventlet monkey-patching muss VOR allen Imports passieren.
# Daher wird ein Wrapper-Entrypoint verwendet statt direktem Gunicorn-Aufruf.
# GUNICORN_WORKER_CLASS env var wird in gunicorn.conf.py gelesen.
ENV GUNICORN_WORKER_CLASS=eventlet

CMD ["gunicorn", "-c", "config/gunicorn.conf.py", "wsgi:app"]
```

**WICHTIG: eventlet monkey-patching**

`wsgi.py` muss als ERSTE Zeilen (vor allen anderen Imports) eventlet monkey-patchen:

```python
import eventlet
eventlet.monkey_patch()

from app import create_app
app = create_app()
```

Dies ist notwendig weil:
- psycopg3 ConnectionPool Background-Threads (pool-worker, pool-scheduler) kooperativ sein muessen
- Flask-SocketIO mit eventlet async_mode laeuft
- Ohne Monkey-Patching → potenzielle Deadlocks unter Last

### Frontend Dockerfile (Multi-stage)

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

### Nginx Config

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
    }

    # WebSocket (SocketIO)
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

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 256;
}
```

### docker-compose.yml

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
  lsx-logs:
  lsx-data:

networks:
  macvlan50:
    external: true
  macvlan51:
    external: true
  macvlan53:
    external: true
```

**Celery Entrypoint:** Nutzt `wsgi:celery` statt `app.core.bootstrap.extensions.celery`. Dafuer wird in `wsgi.py` das Celery-Objekt exportiert:

```python
import eventlet
eventlet.monkey_patch()

from app import create_app
from app.core.bootstrap.extensions import celery

app = create_app()
# celery ist jetzt via wsgi:celery importierbar
```

---

## 4. Cloudflare Tunnel Routing

Bestehender cloudflared-Container (10.0.30.4) wird konfiguriert:

**Cloudflare Dashboard → Zero Trust → Tunnels → Public Hostname hinzufuegen:**

| Public Hostname | Service | Optionen |
|----------------|---------|----------|
| (trycloudflare.com oder eigene Domain) | http://10.0.50.4:80 | WebSocket: enabled |

Domain austauschbar: Nur Cloudflare Route + `.env.docker` (FRONTEND_URL, CORS_ORIGINS) aendern.

---

## 5. Auto-Deploy von Dev (dev02 → Docker)

### deploy.sh (auf dev02)

```bash
#!/bin/bash
set -e

DOCKER_HOST="srv01-docker01-dockeradm"
PROJECT_DIR="/home/pascal/Lernsystem"
REMOTE_DIR="/opt/lsx"

echo "=== LSX Deploy ==="

# 1. Sync Code zum Docker Host (NICHT .env.docker ueberschreiben!)
rsync -avz --delete \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='.env.docker' \
  --exclude='*.pyc' \
  --exclude='.superpowers' \
  "$PROJECT_DIR/" "$DOCKER_HOST:$REMOTE_DIR/"

# 2. Build + Restart auf Docker Host
ssh "$DOCKER_HOST" "cd $REMOTE_DIR/docker && docker compose build && docker compose up -d"

echo "=== Deploy fertig ==="
```

---

## 6. Setup Wizard — Docker-Kompatibilitaet

### Identifizierte Probleme und Fixes

| Problem | Fix |
|---------|-----|
| `.lsx-installed` Pfad relativ zum CWD | `InstallationChecker.INSTALL_MARKER_FILE = os.environ.get('LSX_INSTALL_MARKER', '.lsx-installed')` + Volume `lsx-data` |
| Frontend-Marker schreibt nach `frontend/public/` | Im Docker nicht noetig, Frontend prueft via API. Frontend-Marker-Code skip wenn ENV `DOCKER=1` gesetzt |
| `verify_installation()` hat legacy SQLAlchemy-Imports | Kein Blocker (nicht im Hauptfluss), aber fix: try/except um den Import |
| `verify_part2.py` hat hardcoded `.lsx-installed` String | Muss auf `InstallationChecker.INSTALL_MARKER_FILE` geaendert werden |

### eventlet Monkey-Patching

`wsgi.py` muss als ALLERERSTE Zeilen vor allen Imports:
```python
import eventlet
eventlet.monkey_patch()
```

Ohne dies:
- psycopg3 Pool-Threads sind nicht kooperativ → Deadlocks
- SocketIO eventlet Worker-Class funktioniert nicht korrekt

---

## 7. Environment Configuration (.env.docker.example)

```env
# Flask
FLASK_ENV=production
SECRET_KEY=CHANGE_ME_random_64_chars
DEBUG=False
DOCKER=1

# Database (external — srv01-db01)
DATABASE_URL=postgresql://lsx_user:CHANGE_ME@db.internal.example:5432/lernsystemx
DB_HOST=db.internal.example
DB_PORT=5432
DB_NAME=lernsystemx
DB_USER=lsx_user
DB_PASSWORD=CHANGE_ME

# Redis (external — 10.0.43.2)
REDIS_URL=redis://10.0.43.2:6379/0
REDIS_HOST=10.0.43.2
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=redis://10.0.43.2:6379/1
CELERY_RESULT_BACKEND=redis://10.0.43.2:6379/2

# JWT
JWT_SECRET_KEY=CHANGE_ME_random_64_chars
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# AI APIs
ANTHROPIC_API_KEY=CHANGE_ME
OPENAI_API_KEY=CHANGE_ME
DEEPL_API_KEY=CHANGE_ME

# CORS (austauschbar — Domain hier aendern!)
FRONTEND_URL=https://CHANGE_ME_DOMAIN
CORS_ORIGINS=https://CHANGE_ME_DOMAIN
SOCKETIO_CORS_ALLOWED_ORIGINS=https://CHANGE_ME_DOMAIN

# SocketIO
SOCKETIO_MESSAGE_QUEUE=redis://10.0.43.2:6379/3

# Session
SESSION_TYPE=redis
SESSION_REDIS_URL=redis://10.0.43.2:6379/5

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://10.0.43.2:6379/4

# Install Marker (persistent volume)
LSX_INSTALL_MARKER=/app/data/.lsx-installed

# Gunicorn
GUNICORN_WORKER_CLASS=eventlet

# Logging
LOG_LEVEL=WARNING
```

---

## 8. Zusammenfassung

### Was gebaut wird (Code)
1. `docker/backend/Dockerfile`
2. `docker/frontend/Dockerfile` (Multi-stage)
3. `docker/frontend/nginx.conf`
4. `docker/docker-compose.yml`
5. `docker/.env.docker.example`
6. `docker/deploy.sh`
7. Fix: `wsgi.py` — eventlet monkey-patching + celery export
8. Fix: `InstallationChecker` — Marker-Pfad via ENV
9. Fix: `verify_part2.py` — hardcoded Pfad ersetzen

### Was manuell konfiguriert wird
1. VLAN 50 + 51 in pfSense erstellen (falls nicht vorhanden)
2. VLAN Interfaces auf Docker Host (`ens19.50`, `ens19.51`)
3. macvlan50 + macvlan51 Docker Networks
4. pfSense Firewall-Regeln (8 Regeln)
5. `.env.docker` auf Docker Host erstellen (aus Template)
6. PostgreSQL DB + User anlegen auf srv01-db01
7. Cloudflare Tunnel Route konfigurieren

### Reihenfolge
1. pfSense: VLANs 50 + 51 erstellen (falls noetig)
2. Docker Host: VLAN-Interfaces + macvlan Networks erstellen
3. Docker Host: `/opt/lsx/docker/.env.docker` anlegen
4. Dev: Code-Fixes (wsgi.py, InstallationChecker)
5. Dev: `docker/` Verzeichnis mit allen Dateien erstellen
6. PostgreSQL: DB + User anlegen
7. pfSense: Firewall-Regeln setzen
8. Cloudflare: Tunnel Route setzen
9. Deploy: `./deploy.sh`
10. Browser: Setup Wizard durchlaufen
