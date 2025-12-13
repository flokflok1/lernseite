# 28_Deployment-DevOps.md (Final)
Version: 1.0
Stand: Final

Dieses Dokument beschreibt die vollständige Deployment-, DevOps- und Betriebsarchitektur des LSX Lernsystems.
Es umfasst alles von Infrastruktur, Serverarchitektur, CI/CD, Monitoring, Logging, Skalierung, Containerisierung bis hin zur Ausfallsicherheit.

Die DevOps-Architektur ist entscheidend, damit LSX stabil, skalierbar und zuverlässig funktioniert.

---

# 1. Ziele der DevOps-Architektur

Das LSX Deployment- und DevOps-System soll:

- **hochverfügbar sein** – 99.9% Uptime (SLA)
- **skalierbar sein** – Von 100 auf 100.000 Nutzer ohne Umbau
- **automatisiert deployen** – CI/CD Pipeline für jeden Commit
- **KI-Workloads effizient verteilen** – Dedizierte Worker für KI-Jobs
- **Sicherheit gewährleisten** – Secrets Management, RBAC, Network Policies
- **Kosten kontrollieren** – Auto-Scaling, Spot Instances, Caching
- **Ausfälle automatisch kompensieren** – Self-Healing, Auto-Recovery
- **Entwickler produktiv halten** – Schnelles Feedback, Lokale Entwicklung
- **Zero-Downtime-Deployments ermöglichen** – Rolling Updates, Canary Deployments

**Kernvorteile:**

✅ **Hohe Verfügbarkeit** – Multi-Zone Deployment
✅ **Automatisierung** – Alles via CI/CD
✅ **Skalierbarkeit** – Horizontal & Vertical Scaling
✅ **Kostenoptimierung** – Auto-Scaling, Caching, Spot Instances
✅ **Sicherheit** – Secrets, RBAC, Network Policies
✅ **Observability** – Monitoring, Logging, Tracing

---

# 2. Infrastrukturübersicht

## 2.1 C4 Context Diagramm – LSX Infrastruktur

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

LAYOUT_WITH_LEGEND()

title C4 Context - LSX Infrastruktur im Cloud-Ökosystem

Person(users, "Nutzer", "Schüler, Lehrer, Creator, Org Admins")
Person(dev_team, "Dev Team", "Entwickler, DevOps, SRE")

System(lsx_platform, "LSX Platform", "Containerisierte Cloud-Native Plattform")

System_Ext(cloud_provider, "Cloud Provider", "AWS / GCP / Azure / Hetzner")
System_Ext(cdn, "CDN", "CloudFlare / AWS CloudFront")
System_Ext(openai, "OpenAI API", "GPT-4, Embeddings")
System_Ext(anthropic, "Anthropic API", "Claude 3.5")
System_Ext(deepl, "DeepL API", "Übersetzungen")
System_Ext(stripe, "Stripe", "Zahlungen")
System_Ext(monitoring, "Monitoring Stack", "Prometheus, Grafana, Sentry")
System_Ext(registry, "Container Registry", "Docker Hub / GHCR")

Rel(users, lsx_platform, "Nutzt Platform", "HTTPS")
Rel(dev_team, lsx_platform, "Deployed, Monitored", "CI/CD, K8s")

Rel(lsx_platform, cloud_provider, "Hosted auf", "K8s, VMs, Managed Services")
Rel(lsx_platform, cdn, "Statische Assets", "HTTPS")
Rel(lsx_platform, openai, "KI-Anfragen", "REST API")
Rel(lsx_platform, anthropic, "KI-Anfragen", "REST API")
Rel(lsx_platform, deepl, "Übersetzungen", "REST API")
Rel(lsx_platform, stripe, "Zahlungen", "REST API")
Rel(lsx_platform, monitoring, "Metrics, Logs, Errors", "Prometheus, Loki")
Rel(registry, lsx_platform, "Container Images", "Docker Pull")

@enduml
```

## 2.2 C4 Container Diagramm – LSX Deployment Architektur

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

LAYOUT_WITH_LEGEND()

title C4 Container - LSX Deployment Komponenten

Person(user, "User", "Nutzer der Platform")

Container(load_balancer, "Load Balancer", "Nginx / Traefik", "SSL Termination, Routing")
Container(frontend, "Frontend Cluster", "Vue.js 3 / Next.js", "Web UI, SSR")
Container(api_gateway, "API Gateway", "Kong / Nginx", "Rate Limiting, Auth")
Container(backend_api, "Backend API Cluster", "Flask / FastAPI", "REST API, Business Logic")
Container(worker_gpt, "GPT Worker Cluster", "Celery + Python", "GPT-4 KI-Jobs")
Container(worker_claude, "Claude Worker Cluster", "Celery + Python", "Claude KI-Jobs")
Container(worker_pdf, "PDF Worker Cluster", "Celery + Python", "PDF-Verarbeitung")
Container(worker_misc, "Misc Worker Cluster", "Celery + Python", "Math, Translation, Validation")

ContainerDb(redis_cluster, "Redis Cluster", "Redis 7+", "Cache, Queues, Sessions")
ContainerDb(postgres_ha, "PostgreSQL HA", "PostgreSQL 15+", "Primary + Replicas")
ContainerDb(minio, "Object Storage", "MinIO / S3", "PDFs, Videos, Bilder")

Container(monitoring_stack, "Monitoring Stack", "Prometheus, Grafana, Loki", "Metrics, Dashboards, Logs")

Rel(user, load_balancer, "HTTPS Requests", "HTTPS")
Rel(load_balancer, frontend, "Route to Frontend", "HTTP")
Rel(load_balancer, api_gateway, "Route to API", "HTTP")

Rel(frontend, api_gateway, "API Calls", "HTTPS/JSON")
Rel(api_gateway, backend_api, "Forward Requests", "HTTP")

Rel(backend_api, redis_cluster, "Cache, Queues", "Redis Protocol")
Rel(backend_api, postgres_ha, "DB Queries", "SQL")
Rel(backend_api, minio, "File Storage", "S3 API")

Rel(backend_api, worker_gpt, "Queue KI Jobs", "Celery")
Rel(backend_api, worker_claude, "Queue KI Jobs", "Celery")
Rel(backend_api, worker_pdf, "Queue PDF Jobs", "Celery")
Rel(backend_api, worker_misc, "Queue Misc Jobs", "Celery")

Rel(worker_gpt, redis_cluster, "Get Jobs", "Redis")
Rel(worker_claude, redis_cluster, "Get Jobs", "Redis")
Rel(worker_pdf, redis_cluster, "Get Jobs", "Redis")
Rel(worker_misc, redis_cluster, "Get Jobs", "Redis")

Rel(backend_api, monitoring_stack, "Send Metrics", "Prometheus")
Rel(worker_gpt, monitoring_stack, "Send Metrics", "Prometheus")
Rel(redis_cluster, monitoring_stack, "Export Metrics", "Prometheus")
Rel(postgres_ha, monitoring_stack, "Export Metrics", "Prometheus")

@enduml
```

LSX verwendet eine **modulare, containerisierte Cloud-Architektur**:

```plantuml
@startuml
title LSX Infrastruktur Stack

rectangle "User Layer" #LightBlue {
  :Browser;
  :Mobile App;
}

rectangle "Edge Layer" #LightGreen {
  :CloudFlare CDN;
  :SSL/TLS Termination;
  :DDoS Protection;
}

rectangle "Load Balancing" #LightYellow {
  :Nginx / Traefik;
  :Health Checks;
  :Session Affinity;
}

rectangle "Application Layer" #LightPink {
  rectangle "Frontend" {
    :Vue.js Cluster;
    :SSR Rendering;
  }

  rectangle "Backend" {
    :API Cluster (Flask);
    :Auth Service;
    :Business Logic;
  }
}

rectangle "Worker Layer" #LightCyan {
  :GPT Worker;
  :Claude Worker;
  :PDF Worker;
  :Translation Worker;
  :Math Worker;
  :Validation Worker;
}

rectangle "Data Layer" #LightSalmon {
  :Redis Cluster;
  :PostgreSQL HA;
  :MinIO / S3;
}

rectangle "External Services" #LightGray {
  :OpenAI API;
  :Anthropic API;
  :DeepL API;
  :Stripe API;
}

rectangle "Observability" #White {
  :Prometheus;
  :Grafana;
  :Loki;
  :Sentry;
}

User Layer --> Edge Layer
Edge Layer --> Load Balancing
Load Balancing --> Application Layer
Application Layer --> Worker Layer
Application Layer --> Data Layer
Worker Layer --> Data Layer
Application Layer --> External Services
Application Layer --> Observability
Worker Layer --> Observability

@enduml
```

KI-Modelle wie GPT/Claude werden extern über API angebunden.
Lokale Modelle (Ollama / GPU) können optional hinzugefügt werden.

---

# 3. Containerisierung

LSX verwendet **Docker** für Containerisierung:

```plantuml
@startuml
title Docker Container Architektur

package "LSX Docker Containers" {
  rectangle "Frontend Container" #LightBlue {
    :Node.js 20;
    :Vue.js 3 / Next.js;
    :Port 3000;
  }

  rectangle "Backend API Container" #LightGreen {
    :Python 3.12;
    :Flask / FastAPI;
    :Port 8000;
  }

  rectangle "GPT Worker Container" #LightYellow {
    :Python 3.12;
    :Celery;
    :OpenAI SDK;
  }

  rectangle "Claude Worker Container" #LightPink {
    :Python 3.12;
    :Celery;
    :Anthropic SDK;
  }

  rectangle "PDF Worker Container" #LightCyan {
    :Python 3.12;
    :Celery;
    :PyMuPDF, ReportLab;
  }

  rectangle "Math Worker Container" #LightSalmon {
    :Python 3.12;
    :Celery;
    :NumPy, SymPy;
  }

  rectangle "Translation Worker Container" #LightGray {
    :Python 3.12;
    :Celery;
    :DeepL SDK;
  }

  rectangle "Validation Worker Container" #White {
    :Python 3.12;
    :Celery;
    :Validators;
  }

  rectangle "Redis Container" #LightCoral {
    :Redis 7.2;
    :Port 6379;
  }

  rectangle "PostgreSQL Container" #LightSkyBlue {
    :PostgreSQL 15;
    :Port 5432;
  }

  rectangle "Nginx Container" #LightSeaGreen {
    :Nginx 1.25;
    :Reverse Proxy;
    :Port 80, 443;
  }
}

@enduml
```

## 3.1 Hauptcontainer

1. **frontend** – Vue.js / Next.js Frontend
2. **backend-api** – Flask / FastAPI REST API
3. **worker-gpt** – GPT-4 KI-Worker
4. **worker-claude** – Claude 3.5 KI-Worker
5. **worker-pdf** – PDF-Generierung & Verarbeitung
6. **worker-math** – Math-Rendering (LaTeX, SymPy)
7. **worker-translate** – DeepL Übersetzungen
8. **worker-validator** – Content-Validation
9. **redis** – Cache & Job Queue
10. **postgres** – Datenbank
11. **reverse-proxy** – Nginx / Traefik

Jeder Container ist **isoliert** und **unabhängig skalierbar**.

## 3.2 Dockerfile Beispiele

### 3.2.1 Backend API Dockerfile

```dockerfile
# Backend API Dockerfile
FROM python:3.12-slim

WORKDIR /app

# System Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application Code
COPY . .

# Non-root User
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose Port
EXPOSE 8000

# Start Command
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### 3.2.2 Worker Dockerfile

```dockerfile
# Worker Dockerfile (GPT Worker)
FROM python:3.12-slim

WORKDIR /app

# System Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies
COPY requirements-worker.txt .
RUN pip install --no-cache-dir -r requirements-worker.txt

# Application Code
COPY worker/ ./worker/
COPY shared/ ./shared/

# Non-root User
RUN useradd -m -u 1000 worker && chown -R worker:worker /app
USER worker

# Environment
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0

# Start Celery Worker
CMD ["celery", "-A", "worker.gpt_worker", "worker", "--loglevel=info", "--concurrency=4"]
```

### 3.2.3 Frontend Dockerfile

```dockerfile
# Frontend Dockerfile (Multi-Stage Build)
FROM node:20-alpine AS builder

WORKDIR /app

# Dependencies
COPY package*.json ./
RUN npm ci

# Build
COPY . .
RUN npm run build

# Production Image
FROM node:20-alpine

WORKDIR /app

# Copy Build
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

# Non-root User
RUN addgroup -g 1000 appgroup && adduser -D -u 1000 -G appgroup appuser
USER appuser

# Expose Port
EXPOSE 3000

# Start
CMD ["npm", "start"]
```

---

# 4. Orchestrierung: Docker Compose → Kubernetes

LSX verwendet zwei Betriebsmodi:

## 4.1 Entwicklungsmodus (Docker Compose)

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/lsx
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis

  worker-gpt:
    build:
      context: ./backend
      dockerfile: Dockerfile.worker
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - redis

  worker-claude:
    build:
      context: ./backend
      dockerfile: Dockerfile.worker
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis

  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=lsx
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend

volumes:
  redis_data:
  postgres_data:
```

**Starten:**
```bash
docker compose up --build
```

**Nutzen:**
- ✅ Einfacher Start
- ✅ Lokale Datenbanken
- ✅ Kiesbare Worker
- ✅ Hot-Reload für Development

## 4.2 Produktionsmodus (Kubernetes)

LSX setzt auf **Kubernetes (K8s)** mit:

- **Horizontal Pod Autoscaler** – Auto-Scaling basierend auf CPU/Memory
- **Node Scaling** – Cluster Auto-Scaling
- **Health Checks** – Liveness & Readiness Probes
- **Ingress Controller** – SSL Termination, Routing
- **Secrets Manager** – Sichere Speicherung von Secrets
- **RBAC Control** – Rollenbasierte Zugriffskontrolle
- **Rolling Updates** – Zero-Downtime Deployments

```plantuml
@startuml
title Kubernetes Cluster Architektur

package "Kubernetes Cluster" {
  rectangle "Control Plane" #LightBlue {
    :API Server;
    :etcd;
    :Scheduler;
    :Controller Manager;
  }

  rectangle "Worker Nodes" {
    rectangle "Node 1" #LightGreen {
      :Kubelet;
      :Frontend Pod (3 Replicas);
      :Backend Pod (5 Replicas);
    }

    rectangle "Node 2" #LightYellow {
      :Kubelet;
      :Worker-GPT Pod (4 Replicas);
      :Worker-Claude Pod (2 Replicas);
    }

    rectangle "Node 3" #LightPink {
      :Kubelet;
      :Redis Pod (3 Replicas);
      :PostgreSQL Pod (Primary);
    }

    rectangle "Node 4" #LightCyan {
      :Kubelet;
      :PostgreSQL Pod (Replica);
      :Worker-PDF Pod (2 Replicas);
    }
  }

  rectangle "Persistent Storage" #LightSalmon {
    :PersistentVolumes;
    :StorageClass;
  }

  rectangle "Networking" #LightGray {
    :Ingress Controller;
    :Service Mesh (Optional);
    :Network Policies;
  }
}

@enduml
```

### 4.2.1 Kubernetes Deployment Beispiel (Backend API)

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-api
  namespace: lsx-prod
spec:
  replicas: 5
  selector:
    matchLabels:
      app: backend-api
  template:
    metadata:
      labels:
        app: backend-api
    spec:
      containers:
      - name: backend
        image: ghcr.io/lsx/backend-api:v1.2.3
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-api
  namespace: lsx-prod
spec:
  selector:
    app: backend-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-api-hpa
  namespace: lsx-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 4.2.2 Ingress Configuration

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: lsx-ingress
  namespace: lsx-prod
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - lsx.de
    - www.lsx.de
    - api.lsx.de
    secretName: lsx-tls
  rules:
  - host: lsx.de
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
  - host: api.lsx.de
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-api
            port:
              number: 80
```

---

# 5. CI/CD Pipeline

```plantuml
@startuml
title CI/CD Pipeline Workflow

actor "Developer" as dev
participant "GitHub" as github
participant "GitHub Actions" as actions
participant "Container Registry" as registry
participant "Kubernetes Staging" as staging
participant "Kubernetes Production" as prod
participant "Monitoring" as monitor

dev -> github: git push

github -> actions: Trigger Pipeline

actions -> actions: **Stage 1: Linting**\n- ESLint (Frontend)\n- Flake8, Black (Backend)\n- Terraform Validate

alt Linting Failed
  actions -> dev: ❌ Pipeline Failed
  stop
end

actions -> actions: **Stage 2: Tests**\n- Unit Tests (Backend)\n- Integration Tests\n- API Tests\n- Frontend Tests

alt Tests Failed
  actions -> dev: ❌ Tests Failed
  stop
end

actions -> actions: **Stage 3: Security Checks**\n- Trivy (Container Scan)\n- OWASP Dependency Check\n- Secret Scan (GitGuardian)

alt Security Issues
  actions -> dev: ⚠️ Security Warnings
end

actions -> actions: **Stage 4: Build Container Images**\n- docker build\n- docker tag

actions -> registry: **Stage 5: Push to Registry**\n- docker push

registry --> actions: ✅ Images Pushed

actions -> staging: **Stage 6: Deploy to Staging**\n- kubectl apply\n- Helm upgrade

staging --> actions: ✅ Deployed

actions -> actions: **Stage 7: Automated Tests on Staging**\n- Smoke Tests\n- E2E Tests

alt Staging Tests Failed
  actions -> dev: ❌ Staging Tests Failed
  stop
end

actions -> dev: ⏸️ **Stage 8: Manual Approval Required**

dev -> actions: ✅ Approve Production Deployment

actions -> prod: **Stage 9: Deploy to Production**\n- kubectl apply --dry-run\n- kubectl apply (Rolling Update)

prod --> actions: ✅ Deployed

actions -> monitor: Send Deployment Event

monitor -> monitor: Track Deployment Metrics

actions -> dev: ✅ Pipeline Complete

@enduml
```

**Verwendete Systeme:**
- GitHub Actions
- GitLab CI
- Bitbucket CI

**Pipeline Stufen:**

1. **Linting** – Code-Qualität prüfen (Backend, Frontend, Infra)
2. **Tests** – Unit, Integration, API Tests
3. **Security Checks** – Container Scan, Dependency Check
4. **Build Container Images** – Docker Build & Tag
5. **Push to Registry** – GHCR / Docker Hub
6. **Deploy to Staging** – Kubernetes Staging Cluster
7. **Automatisierte Tests auf Staging** – Smoke Tests, E2E
8. **Manual Approval** – DevOps genehmigt Production Deploy
9. **Deploy to Production** – Kubernetes Production Cluster

## 5.1 GitHub Actions Workflow Beispiel

```yaml
# .github/workflows/deploy.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Lint Frontend
        run: |
          cd frontend
          npm install
          npm run lint

      - name: Lint Backend
        run: |
          cd backend
          pip install flake8 black
          flake8 .
          black --check .

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3

      - name: Run Backend Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/ --cov=app --cov-report=xml

      - name: Run Frontend Tests
        run: |
          cd frontend
          npm install
          npm test

  security:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3

      - name: Run Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'

  build:
    runs-on: ubuntu-latest
    needs: security
    steps:
      - uses: actions/checkout@v3

      - name: Build Backend Image
        run: |
          docker build -t ghcr.io/lsx/backend-api:${{ github.sha }} ./backend

      - name: Build Frontend Image
        run: |
          docker build -t ghcr.io/lsx/frontend:${{ github.sha }} ./frontend

      - name: Push to GHCR
        run: |
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ghcr.io/lsx/backend-api:${{ github.sha }}
          docker push ghcr.io/lsx/frontend:${{ github.sha }}

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Staging
        run: |
          kubectl set image deployment/backend-api backend=ghcr.io/lsx/backend-api:${{ github.sha }} -n lsx-staging
          kubectl rollout status deployment/backend-api -n lsx-staging

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Production
        run: |
          kubectl set image deployment/backend-api backend=ghcr.io/lsx/backend-api:${{ github.sha }} -n lsx-prod
          kubectl rollout status deployment/backend-api -n lsx-prod
```

## 5.2 Zero Downtime Deployment Strategien

```plantuml
@startuml
title Deployment Strategien

rectangle "Rolling Update" #LightBlue {
  :Version v1 → v2;
  :Pod-by-Pod Replacement;
  :Health Checks;
  :Rollback bei Fehler;
  --
  ✅ Zero Downtime
  ✅ Gradual Rollout
  ⚠️ Beide Versionen laufen kurzzeitig
}

rectangle "Blue/Green Deployment" #LightGreen {
  :Blue (v1) Production;
  :Green (v2) Staging;
  :Traffic Switch;
  :Rollback = Switch zurück;
  --
  ✅ Sofortiger Rollback
  ✅ Vollständige Tests
  ⚠️ Doppelte Ressourcen
}

rectangle "Canary Deployment" #LightYellow {
  :v1: 90% Traffic;
  :v2: 10% Traffic;
  :Monitor Metrics;
  :Schrittweise erhöhen;
  --
  ✅ Risikominimierung
  ✅ A/B Testing möglich
  ⚠️ Komplex
}

@enduml
```

**Mit:**
- **Kubernetes Rolling Updates** – Standard-Strategie
- **Canary Deployments** – 10% Traffic auf neue Version
- **Blue/Green Deployment** – Sofortiger Switch zwischen Versionen

---

# 6. Environments

LSX besitzt **4 Umgebungen**:

```plantuml
@startuml
title Environment Strategy

rectangle "Local" #LightBlue {
  :Developer Laptop;
  :Docker Compose;
  :Mock Services;
  :Lokale DB;
}

rectangle "Development" #LightGreen {
  :Shared Dev Cluster;
  :Latest Code;
  :Feature Testing;
  :Mock Payment;
}

rectangle "Staging" #LightYellow {
  :Production-Like;
  :Real Services;
  :Full Integration Tests;
  :Real Payment (Test Mode);
}

rectangle "Production" #LightPink {
  :Live Users;
  :HA Setup;
  :Real Payments;
  :Monitoring 24/7;
}

Local --> Development : git push
Development --> Staging : Merge to develop
Staging --> Production : Merge to main + Approval

@enduml
```

| Environment | Zweck | Datenbank | KI-Keys | Domains |
|-------------|-------|-----------|---------|---------|
| **local** | Developer Laptop | SQLite / Local Postgres | Mock / Test Keys | localhost:3000 |
| **development** | Shared Dev Cluster | Dev Postgres | Test Keys | dev.lsx.internal |
| **staging** | Pre-Production Tests | Staging Postgres | Real Keys (Test Mode) | staging.lsx.de |
| **production** | Live Users | Production Postgres HA | Real Keys (Production) | lsx.de |

Jede Umgebung hat eigene:
- **Datenbank**
- **Secrets**
- **Tokens**
- **KI-Schlüssel**
- **API Keys**
- **Domains**

---

# 7. Environment Variablen & Secrets

Alle sensiblen Informationen:

- **API Keys** – OpenAI, Anthropic, DeepL
- **JWT Secrets** – Token-Signierung
- **KI-Schlüssel** – GPT, Claude
- **Stripe Keys** – Zahlungen
- **DB Passwörter** – PostgreSQL, Redis

werden über **Secrets Management** gespeichert:

```plantuml
@startuml
title Secrets Management

rectangle "Secrets Sources" {
  rectangle "Development" #LightBlue {
    :.env Files;
    :Docker Compose Secrets;
  }

  rectangle "Production" #LightGreen {
    :Kubernetes Secrets;
    :HashiCorp Vault;
    :AWS Secrets Manager;
    :Azure Key Vault;
  }
}

rectangle "Application" #LightYellow {
  :Environment Variables;
  :Runtime Loading;
}

Development --> Application : Load Secrets
Production --> Application : Load Secrets

@enduml
```

**Niemals im Code.**

**Kubernetes Secret Beispiel:**

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: openai-secret
  namespace: lsx-prod
type: Opaque
stringData:
  api-key: sk-proj-xxxxxxxxxx
---
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: lsx-prod
type: Opaque
stringData:
  url: postgresql://user:password@postgres-primary:5432/lsx
```

**Verwendung im Pod:**
```yaml
env:
- name: OPENAI_API_KEY
  valueFrom:
    secretKeyRef:
      name: openai-secret
      key: api-key
```

---

# 8. Monitoring

Überwachung in Echtzeit:

```plantuml
@startuml
title Monitoring Stack Architektur

rectangle "LSX Application" #LightBlue {
  :Backend API;
  :Workers;
  :Frontend;
}

rectangle "Metrics Collection" #LightGreen {
  :Prometheus;
  :Node Exporter;
  :Redis Exporter;
  :PostgreSQL Exporter;
}

rectangle "Visualization" #LightYellow {
  :Grafana Dashboards;
  :Real-Time Metrics;
  :Alerts;
}

rectangle "Logging" #LightPink {
  :Loki;
  :Fluent Bit;
  :Log Aggregation;
}

rectangle "Error Tracking" #LightCyan {
  :Sentry;
  :Error Reports;
  :Stack Traces;
}

rectangle "Alerting" #LightSalmon {
  :Alertmanager;
  :Slack Notifications;
  :Email Alerts;
  :PagerDuty;
}

LSX Application --> Metrics Collection : Export Metrics
Metrics Collection --> Visualization : Scrape Metrics
LSX Application --> Logging : Send Logs
LSX Application --> Error Tracking : Send Errors
Visualization --> Alerting : Trigger Alerts

@enduml
```

## 8.1 Tools

- **Prometheus** – Metrics Collection
- **Grafana** – Dashboards & Visualization
- **Loki** – Log Aggregation
- **Alertmanager** – Alert Routing
- **UptimeRobot / Betterstack** – External Monitoring
- **Sentry** – Error Tracking & Reporting

## 8.2 Wichtige Metriken

📊 **System Metriken:**
- CPU / RAM pro Pod
- Disk I/O
- Network Traffic

📊 **Application Metriken:**
- API Response Time (P50, P95, P99)
- Errors 4xx/5xx
- Request Rate (requests/sec)

📊 **Database Metriken:**
- Query Latency
- Connection Pool Usage
- Replication Lag

📊 **Cache Metriken:**
- Redis Hit/Miss Rate
- Memory Usage
- Evictions

📊 **Queue Metriken:**
- Job Queue Status (Pending, Processing, Failed)
- Worker Utilization
- Job Duration

📊 **Business Metriken:**
- Token Verbrauch KI
- Active Users
- Course Completions
- Revenue

📊 **LiveRoom Metriken:**
- Active Connections
- Bandwidth Usage
- Latency

## 8.3 Grafana Dashboard Beispiel

```yaml
# grafana-dashboard.json (simplified)
{
  "dashboard": {
    "title": "LSX Production Metrics",
    "panels": [
      {
        "title": "API Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "P95"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m]))",
            "legendFormat": "5xx Errors"
          }
        ]
      },
      {
        "title": "Redis Cache Hit Rate",
        "targets": [
          {
            "expr": "rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m])) * 100",
            "legendFormat": "Hit Rate %"
          }
        ]
      },
      {
        "title": "Worker Queue Status",
        "targets": [
          {
            "expr": "sum(celery_tasks_total{state=\"PENDING\"})",
            "legendFormat": "Pending Tasks"
          }
        ]
      }
    ]
  }
}
```

---

# 9. Logging

LSX verwendet **strukturierte JSON Logs**:

```plantuml
@startuml
title Logging Pipeline

rectangle "Application Logs" #LightBlue {
  :Backend API Logs;
  :Worker Logs;
  :Frontend Logs (Server);
}

rectangle "Log Collection" #LightGreen {
  :Fluent Bit Agent;
  :STDOUT/STDERR Capture;
}

rectangle "Log Aggregation" #LightYellow {
  :Loki;
  :Label-based Indexing;
}

rectangle "Log Visualization" #LightPink {
  :Grafana Loki;
  :Log Queries;
  :Filtering;
}

rectangle "Log Retention" #LightCyan {
  :7 Days (Hot);
  :30 Days (Warm);
  :90 Days (Cold);
}

Application Logs --> Log Collection
Log Collection --> Log Aggregation
Log Aggregation --> Log Visualization
Log Aggregation --> Log Retention

@enduml
```

**Features:**
- ✅ Strukturierte JSON Logs
- ✅ Zentrale Log-Sammlung (Loki / ELK)
- ✅ Pro Microservice eigene Logs
- ✅ Zugriff auf historische Logs
- ✅ Alerting bei kritischen Fehlern

**Beispiel Log-Format:**

```json
{
  "timestamp": "2025-02-15T12:45:00Z",
  "service": "backend-api",
  "level": "error",
  "message": "Database connection timeout",
  "user_id": 1523,
  "endpoint": "/api/v1/course/15",
  "method": "GET",
  "latency_ms": 5385,
  "error": "psycopg2.OperationalError: connection timeout"
}
```

**Python Logging Setup:**

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'service': 'backend-api',
            'level': record.levelname.lower(),
            'message': record.getMessage(),
        }

        # Add custom fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint

        return json.dumps(log_data)

# Configure Logger
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
logger.info('User logged in', extra={'user_id': 123, 'endpoint': '/api/v1/login'})
```

---

# 10. Skalierungsstrategien

```plantuml
@startuml
title Scaling Strategies

rectangle "Horizontal Scaling" #LightBlue {
  :API Pods: 3 → 20;
  :Worker Pods: 4 → 16;
  :Frontend Pods: 2 → 10;
  --
  ✅ Load Distribution
  ✅ High Availability
  ⚠️ Stateless Required
}

rectangle "Vertical Scaling" #LightGreen {
  :CPU: 1 Core → 4 Cores;
  :RAM: 2GB → 8GB;
  :Disk: 50GB → 200GB;
  --
  ✅ Simple
  ⚠️ Downtime Required
  ⚠️ Hardware Limits
}

rectangle "Auto Scaling" #LightYellow {
  :HPA (CPU > 70%);
  :HPA (Memory > 80%);
  :VPA (Vertical Pod Autoscaler);
  :Cluster Autoscaler;
  --
  ✅ Dynamic
  ✅ Cost Efficient
}

@enduml
```

## 10.1 Horizontal Scaling

**Was wird skaliert:**

✅ **API Pods** – Backend API vervielfacht (3 → 20 Pods)
✅ **Worker Cluster** – GPT/Claude Worker erhöht (4 → 16 Pods)
✅ **Redis Cluster** – Mehr Redis-Knoten
✅ **Frontend Instanzen** – SSR Frontend vervielfacht (2 → 10 Pods)
✅ **LiveRoom Media Server** – Mehr Media Server Instances

**HPA Beispiel:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 10.2 Vertical Scaling

**Mehr RAM/CPU für Worker:**
- GPT Worker: 2GB → 8GB RAM (für große PDF-Verarbeitung)
- Claude Worker: 1 Core → 4 Cores
- PostgreSQL: 4 Cores → 8 Cores, 16GB → 32GB RAM

**Größere DB-Instanz:**
- PostgreSQL: db.t3.medium → db.r5.xlarge

**GPU-Knoten für lokale KI:**
- NVIDIA A100 / T4 GPUs für Ollama, Whisper

## 10.3 Auto-Scaling

```python
# Auto-Scaling Logic Beispiel
def should_scale_workers():
    pending_jobs = redis.llen('celery:queue:gpt')
    active_workers = get_active_workers()

    # Scale up if queue is full
    if pending_jobs > 100 and active_workers < 20:
        scale_workers(active_workers + 5)

    # Scale down if queue is empty
    elif pending_jobs < 10 and active_workers > 3:
        scale_workers(active_workers - 2)
```

---

# 11. Ausfallsicherheit

```plantuml
@startuml
title High Availability Architecture

rectangle "Multi-Zone Deployment" #LightBlue {
  rectangle "Zone A" {
    :Backend Pods;
    :Worker Pods;
    :PostgreSQL Primary;
  }

  rectangle "Zone B" {
    :Backend Pods;
    :Worker Pods;
    :PostgreSQL Replica;
  }

  rectangle "Zone C" {
    :Backend Pods;
    :Redis Sentinel;
  }
}

rectangle "Auto Recovery" #LightGreen {
  :Pod Crash → Auto Restart;
  :Node Failure → Reschedule Pods;
  :DB Primary Down → Promote Replica;
  :Worker Timeout → Retry Job;
}

rectangle "Health Checks" #LightYellow {
  :Liveness Probe;
  :Readiness Probe;
  :Startup Probe;
}

rectangle "Backup & Disaster Recovery" #LightPink {
  :Automated DB Backups (Hourly);
  :Point-in-Time Recovery;
  :Multi-Region Replication;
}

@enduml
```

## 11.1 Mehrere Zonen

✅ **Backend in zwei Rechenzentren** – Zone A + Zone B
✅ **Datenbank mit Replikation** – Primary (Zone A) + Replica (Zone B)
✅ **Redis-Cluster mit Sentinel** – Auto-Failover
✅ **Frontend gecached durch CDN** – Global Edge Locations

## 11.2 Auto Recovery

✅ **Worker crash → Neustart** – Kubernetes RestartPolicy: Always
✅ **Pod unhealthy → Kill & Replace** – Liveness Probe Failed → Pod Restart
✅ **DB Replica wird Master bei Ausfall** – Automatic Failover mit Patroni
✅ **API fallback bei KI-Ausfällen** – Retry Logic, Fallback Responses

**Health Check Beispiel:**

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

**Python Health Endpoint:**

```python
@app.route('/health')
def health():
    """Liveness Probe"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/ready')
def ready():
    """Readiness Probe"""
    # Check DB connection
    try:
        db.session.execute('SELECT 1')
        redis_client.ping()
        return jsonify({'status': 'ready'}), 200
    except Exception as e:
        return jsonify({'status': 'not ready', 'error': str(e)}), 503
```

---

# 12. Kostenoptimierung

```plantuml
@startuml
title Cost Optimization Strategies

rectangle "Caching" #LightBlue {
  :Aggressive Redis Caches;
  :KI-Cache (60%+ Savings);
  :CDN Edge Caching;
  --
  💰 60%+ KI Cost Reduction
}

rectangle "Auto-Scaling" #LightGreen {
  :Scale Down bei Low Traffic;
  :Spot Instances für Worker;
  :Scheduled Scaling;
  --
  💰 30-50% Infrastructure Savings
}

rectangle "Resource Optimization" #LightYellow {
  :Right-Sizing Pods;
  :Resource Limits;
  :Node Affinity;
  --
  💰 20% Resource Savings
}

rectangle "Cold vs Hot Services" #LightPink {
  :Hot: Frontend, API;
  :Cold: Analytics, Reports;
  :Cold Services: Spot Instances;
  --
  💰 40% Savings on Cold Services
}

@enduml
```

**Strategien:**

💰 **Aggressive Redis-Caches** – 85%+ Cache Hit Rate
💰 **KI-Cache-Verwendung** – 60%+ der KI-Anfragen aus Cache
💰 **Abschalten von überflüssigen Worker-Nodes** – Auto-Scale to Zero bei Nacht
💰 **Nutzung von Spot-Instances** – 70% günstiger für Worker
💰 **Auto-scaling Down** – Bei Low Traffic (nachts) runterskalieren
💰 **Trennung von kalten & heißen Services** – Analytics auf Spot Instances
💰 **Cloudflare CDN** – Reduziert Bandwidth-Kosten um 80%

**Cost Monitoring:**

```yaml
# FinOps Dashboard
Panels:
  - Total Monthly Cost
  - Cost per Service
  - Cost per Environment
  - Savings from Caching
  - Savings from Spot Instances
  - Projected Cost (next month)
```

---

# 13. DevOps Tools

```plantuml
@startuml
title DevOps Tool Stack

rectangle "Containerization" #LightBlue {
  :Docker;
  :Docker Compose;
}

rectangle "Orchestration" #LightGreen {
  :Kubernetes;
  :Helm Charts;
}

rectangle "CI/CD" #LightYellow {
  :GitHub Actions;
  :GitLab CI;
  :ArgoCD;
}

rectangle "Infrastructure as Code" #LightPink {
  :Terraform;
  :Ansible;
  :Pulumi;
}

rectangle "Monitoring" #LightCyan {
  :Prometheus;
  :Grafana;
  :Loki;
  :Sentry;
}

rectangle "Security" #LightSalmon {
  :Trivy;
  :Falco;
  :OPA;
}

rectangle "Networking" #LightGray {
  :CloudFlare;
  :Nginx;
  :Traefik;
}

@enduml
```

**Liste:**

- **Docker** – Containerization
- **Kubernetes** – Orchestration
- **Helm Charts** – K8s Package Manager
- **GitHub Actions** – CI/CD
- **Terraform** – Infrastructure as Code (optional)
- **Ansible** – Configuration Management (optional)
- **Prometheus/Grafana** – Monitoring & Visualization
- **Loki** – Log Aggregation
- **Sentry** – Error Tracking
- **CloudFlare** – CDN & DDoS Protection
- **Trivy** – Container Security Scanning
- **ArgoCD** – GitOps Continuous Delivery (optional)

---

# 14. Branching Strategy (Git)

```plantuml
@startuml
title Git Branching Strategy (GitFlow)

rectangle "main" #LightBlue {
  :Production Code;
  :Tagged Releases;
  :v1.0.0, v1.1.0, v1.2.0;
}

rectangle "develop" #LightGreen {
  :Staging Code;
  :Integration Branch;
  :Latest Features;
}

rectangle "feature/*" #LightYellow {
  :feature/user-auth;
  :feature/ki-glossar;
  :feature/org-dashboard;
}

rectangle "hotfix/*" #LightPink {
  :hotfix/critical-bug;
  :Dringende Fixes;
}

rectangle "release/*" #LightCyan {
  :release/v1.2.0;
  :Versionsvorbereitung;
}

feature/* --> develop : Pull Request
develop --> release/* : Create Release
release/* --> main : Merge & Tag
release/* --> develop : Merge back
main --> hotfix/* : Branch from Production
hotfix/* --> main : Merge & Tag
hotfix/* --> develop : Merge back

@enduml
```

**Empfohlene Strategie:**

```
main        → Produktion (Stable)
develop     → Staging (Integration)
feature/*   → Feature Entwicklung
hotfix/*    → Dringende Fixes
release/*   → Versionsvorbereitung
```

**Workflow:**

1. Feature Branch von `develop` erstellen: `feature/new-dashboard`
2. Code schreiben, committen
3. Pull Request → `develop`
4. CI/CD läuft, Tests
5. Merge in `develop`
6. Deploy auf Staging
7. Release Branch: `release/v1.2.0`
8. Merge in `main` + Tag `v1.2.0`
9. Deploy auf Production

---

# 15. Developer Workflow

```plantuml
@startuml
title Developer Workflow

actor "Developer" as dev
participant "Local Machine" as local
participant "GitHub" as github
participant "CI/CD" as cicd
participant "Staging" as staging
participant "Production" as prod

dev -> local: git checkout -b feature/xyz

dev -> local: Code schreiben
dev -> local: Tests lokal\n(docker compose up)

local -> local: ✅ Tests pass

dev -> github: git push origin feature/xyz

github -> dev: Pull Request erstellen

dev -> github: Create PR → develop

github -> cicd: Trigger CI/CD Pipeline

cicd -> cicd: Linting, Tests, Security Checks

alt Pipeline Failed
  cicd -> dev: ❌ Pipeline Failed\n(Fix erforderlich)
  dev -> local: Code fixen
  dev -> github: git push (update PR)
else Pipeline Success
  cicd -> dev: ✅ Pipeline Success

  dev -> github: Request Review

  github -> dev: Code Review & Approve

  dev -> github: Merge PR

  github -> cicd: Deploy to Staging

  cicd -> staging: kubectl apply

  staging -> staging: ✅ Deployed

  dev -> staging: Manual Testing

  alt Staging OK
    dev -> github: Create Release PR\n(develop → main)

    github -> cicd: Manual Approval Required

    dev -> cicd: ✅ Approve Production Deploy

    cicd -> prod: Deploy to Production\n(Rolling Update)

    prod -> prod: ✅ Deployed

    cicd -> dev: ✅ Deployment Complete
  else Staging Failed
    dev -> local: Debug & Fix
  end
end

@enduml
```

**Schritte:**

1. **Feature Branch erstellen** – `git checkout -b feature/new-feature`
2. **Code schreiben** – Lokale Entwicklung
3. **Tests lokal** – `docker compose up`, `pytest`
4. **Pull Request → develop** – Code Review
5. **Pipeline baut & testet** – Automated CI/CD
6. **Staging Test** – Manual Testing auf Staging
7. **Merge Release** – `develop` → `main`
8. **Deploy Production** – Kubernetes Rolling Update

---

# 16. Zusammenfassung

Die LSX DevOps & Deployment Architektur ist:

✅ **Modern** – Kubernetes, Docker, CI/CD
✅ **Stabil** – High Availability, Auto-Recovery
✅ **Skalierbar** – Horizontal & Vertical Scaling
✅ **Sicher** – Secrets Management, RBAC, Security Scans
✅ **Professionell** – Production-Ready Setup
✅ **Vollautomatisiert** – Zero-Touch Deployments
✅ **Flexibel erweiterbar** – Neue Services einfach hinzufügbar
✅ **Kosteneffizient** – Auto-Scaling, Caching, Spot Instances

**Kern-Komponenten:**

🔹 **Docker** – Containerization aller Services
🔹 **Kubernetes** – Orchestration & Auto-Scaling
🔹 **CI/CD** – Automated Testing & Deployment
🔹 **Monitoring** – Prometheus, Grafana, Loki, Sentry
🔹 **High Availability** – Multi-Zone, Auto-Recovery
🔹 **Security** – Secrets, RBAC, Container Scanning

Sie bildet das **technische Rückgrat** für ein globales, KI-gestütztes Lernsystem.

---

**Dokument abgeschlossen.**
Stand: Final
Version: 1.0
