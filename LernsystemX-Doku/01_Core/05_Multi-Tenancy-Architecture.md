# 05 – Multi-Tenancy Architecture (Hybrid Approach)

**Status:** ACTIVE (Planning Complete)
**Version:** 1.0
**Date:** 2026-01-22
**Architecture Type:** Hybrid (Shared Backend + Dedicated Frontend per Org)
**Scalability:** Single-instance ready, Kubernetes-scalable

---

## 🎯 Executive Summary

LernSystemX implements a **Hybrid Multi-Tenancy** architecture:

| Aspect | Implementation |
|--------|-----------------|
| **Backend** | Single shared instance (cost-efficient) |
| **Frontend** | Dedicated Docker container per organisation |
| **Routing** | Cloudflare + CNAME (single Public IP) |
| **Isolation** | Row-Level Security (RLS) + organisation_id everywhere |
| **Scalability** | Horizontal (add containers), Vertical (upgrade backend) |
| **Deployment** | Docker Compose (dev/staging), Kubernetes (production) |

**Key Benefits:**
- ✅ Cost-efficient (single backend instance serves all)
- ✅ Data isolation guaranteed (RLS at database level)
- ✅ Independent frontend deployments per organisation
- ✅ Easy customization per organisation
- ✅ True multi-tenant (not just multi-user)

---

## 📐 Architecture Overview

### High-Level Topology

```
Internet (Users worldwide)
    ↓
Public IP: 1.2.3.4
    ↓
Cloudflare (Global CDN + DDoS Protection)
    ↓
DNS Resolution: firma.lsx.com → CNAME → frontend-firma.internal
    ↓
    ├─ Frontend Container (firma)
    │   ├─ nginx reverse proxy
    │   ├─ Vue.js SPA (Compiled)
    │   ├─ Static assets cached
    │   └─ Port: 80/443 (routing via HAProxy)
    │
    ├─ Frontend Container (gymnasium)
    │   ├─ nginx reverse proxy
    │   ├─ Vue.js SPA (Compiled)
    │   ├─ Static assets cached
    │   └─ Port: 80/443 (routing via HAProxy)
    │
    └─ Frontend Container (universität)
        └─ ...

    ↓
HAProxy Load Balancer
    (Distributes based on HTTP Host header)

    ↓
Shared Backend Cluster
    ├─ Backend API #1 (port 5000) - Gunicorn + Flask
    ├─ Backend API #2 (port 5000) - Gunicorn + Flask
    ├─ Backend API #3 (port 5000) - Gunicorn + Flask
    └─ Load Balancer (nginx)

    ↓
Shared Databases & Services
    ├─ PostgreSQL 16 (with Row-Level Security)
    ├─ Redis (cache + sessions)
    ├─ Celery (async jobs)
    └─ Elasticsearch (search)
```

---

## 🏗️ Component Architecture

### 1. Frontend Containers (Per-Organisation)

**Container Structure:**
```
lernsystemx-frontend-firma:latest
├── Dockerfile (multi-stage build)
├── src/ (Vue.js application)
├── nginx.conf (routing + security headers)
├── docker-compose.yml
└── .env (organisation-specific)
```

**Dockerfile:**
```dockerfile
# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Pass organisation_id at build time
ARG VITE_ORG_ID
ENV VITE_ORG_ID=$VITE_ORG_ID
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Stage 2: nginx
FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost/health || exit 1
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Per-Organisation Configuration:**
```bash
# build-frontend.sh - Script to build per organisation

for org in firma gymnasium universität; do
  docker build \
    --build-arg VITE_ORG_ID=$org \
    --build-arg VITE_API_BASE_URL=https://api.lsx.com \
    -t lernsystemx-frontend-$org:latest \
    -f frontend/Dockerfile \
    ./frontend
done
```

### 2. Shared Backend (Single Instance)

**Backend Structure:**
```
backend/
├── Dockerfile
├── app/
│   ├── __init__.py (create_app factory)
│   ├── models/ (organisation-aware)
│   ├── repositories/ (all have organisation_id filtering)
│   ├── blueprints/
│   │   ├── auth.py (organisation-specific login)
│   │   ├── courses.py (filtered by organisation_id)
│   │   └── ...
│   └── middleware/
│       ├── auth.py (extract organisation from token)
│       ├── tenant_isolation.py (enforce organisation_id)
│       └── rate_limit.py (per-organisation limits)
└── requirements.txt
```

**Tenant-Aware Request Processing:**

```python
# app/middleware/tenant_isolation.py

from flask import request, g
from functools import wraps

def extract_organisation_from_request():
    """
    Extract organisation_id from JWT token or HTTP header.

    Priority:
    1. JWT token (organisation_id claim)
    2. X-Organisation-ID header (for API calls)
    3. Default to None (public endpoints)
    """
    from app.utils.jwt import decode_token

    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            payload = decode_token(token)
            g.organisation_id = payload.get('organisation_id')
            g.current_user = payload
            return payload
        except:
            pass

    # Fallback to X-Organisation-ID header
    org_id = request.headers.get('X-Organisation-ID')
    if org_id:
        g.organisation_id = org_id
        return {'organisation_id': org_id}

    # No organisation context
    g.organisation_id = None
    return None

# Apply to all requests
@app.before_request
def before_request():
    extract_organisation_from_request()

# Decorator for endpoints requiring organisation context
def require_organisation(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.organisation_id:
            return {'error': 'organisation_id required'}, 400
        return f(*args, **kwargs)
    return decorated_function
```

### 3. HAProxy Load Balancer

**Configuration for Frontend Routing:**

```haproxy
# /etc/haproxy/haproxy.cfg

global
    maxconn 4096
    log stdout local0
    log stdout local1 notice

defaults
    mode http
    log global
    option httplog
    timeout connect 5000
    timeout client 50000
    timeout server 50000
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http

# Frontend: Listen on public port 80/443
frontend http_in
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/combined.pem

    # Extract hostname
    http-request set-var(req.hostname) req.hdr(host)

    # Route based on hostname
    acl is_firma hdr(host) -i firma.lsx.com
    acl is_gymnasiumm hdr(host) -i gymnasium.lsx.com
    acl is_uni hdr(host) -i universität.lsx.com
    acl is_api hdr(host) -i api.lsx.com

    # Backend mapping
    use_backend backend_firma if is_firma
    use_backend backend_gymnasium if is_gymnasium
    use_backend backend_universität if is_universität
    use_backend backend_api if is_api

    # Default: 404
    default_backend backend_404

# Backend: Frontend containers
backend backend_firma
    balance roundrobin
    server frontend-firma frontend-firma:80 check

backend backend_gymnasium
    balance roundrobin
    server frontend-gymnasium frontend-gymnasium:80 check

backend backend_universität
    balance roundrobin
    server frontend-universität frontend-universität:80 check

# Backend: Shared API
backend backend_api
    balance leastconn
    option httpclose
    option forwardfor
    server api-1 backend-api-1:5000 check
    server api-2 backend-api-2:5000 check
    server api-3 backend-api-3:5000 check

backend backend_404
    errorfile 503 /etc/haproxy/errors/404.http
```

### 4. Database (PostgreSQL with Row-Level Security)

**Tenant Isolation via RLS:**

```sql
-- Enable RLS on all tenant-aware tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
-- etc for all tables

-- Set application context (must be called at start of each request)
CREATE FUNCTION set_current_organisation_id(org_id UUID) RETURNS void AS $$
BEGIN
  PERFORM set_config('app.current_organisation_id', org_id::text, false);
END;
$$ LANGUAGE plpgsql;

-- Example RLS Policy for users table
CREATE POLICY users_isolation ON users
  USING (organisation_id = current_setting('app.current_organisation_id')::UUID)
  WITH CHECK (organisation_id = current_setting('app.current_organisation_id')::UUID);

-- Example RLS Policy for courses table
CREATE POLICY courses_isolation ON courses
  USING (organisation_id = current_setting('app.current_organisation_id')::UUID)
  WITH CHECK (organisation_id = current_setting('app.current_organisation_id')::UUID);
```

**Application Code (Python):**

```python
# app/database.py

def execute_with_tenant_context(query, params, organisation_id):
    """
    Execute SQL query with tenant context (RLS enabled).

    Steps:
    1. Set application context (organisation_id)
    2. Execute query (RLS enforces filtering)
    3. Return results
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Step 1: Set organisation context
            cursor.execute(
                "SELECT set_current_organisation_id(%s);",
                (organisation_id,)
            )

            # Step 2: Execute query (RLS will automatically filter)
            cursor.execute(query, params)

            # Step 3: Return results
            return cursor.fetchall()

# Usage in repositories
class CourseRepository(BaseRepository):
    def find_by_id(self, id: str, organisation_id: str):
        # RLS automatically ensures we only get courses from this organisation
        return execute_with_tenant_context(
            "SELECT * FROM courses WHERE id = %s",
            (id,),
            organisation_id
        )
```

---

## 🌐 DNS & Domain Management

### Subdomain-Based Routing

**DNS Configuration:**

```bash
# Cloudflare DNS Records

Type    Name                 Value              Proxy
------- -------------------- --------- ----------
A       lsx.com              1.2.3.4   Proxied
CNAME   firma                lsx.com   Proxied
CNAME   gymnasium            lsx.com   Proxied
CNAME   universität          lsx.com   Proxied
CNAME   api                  lsx.com   Proxied
TXT     _acme-challenge.api  (for SSL) -
```

**Cloudflare Page Rules (Optional):**

```
URL Pattern: firma.lsx.com/*
  - Browser Caching TTL: 1 hour
  - Cache Level: Standard
  - Security Level: High

URL Pattern: api.lsx.com/*
  - Browser Caching TTL: None (cache 404s)
  - Cache Level: Cache Everything
  - Security Level: Ultra
```

### Custom Domain Support

**Architecture for Custom Domains:**

```
Customer buys domain: firma-custom.de
Goal: firma-custom.de → Loads LernSystemX Firma instance

Solution:
1. Customer points firma-custom.de CNAME to api.lsx.com (via Cloudflare)
2. In LernSystemX database: Store mapping
   organisation.id = 'firma'
   organisation.custom_domains = ['firma-custom.de']
3. HAProxy/frontend checks domain against mapping
4. Routes firma-custom.de → frontend-firma container
```

**Implementation:**

```python
# app/models/organisation.py

from dataclasses import dataclass
from typing import List

@dataclass
class Organisation:
    id: str
    name: str
    subdomain: str                    # firma (required)
    custom_domains: List[str] = None  # ['firma-custom.de'] (optional)
    custom_domain_verified: bool = False

    def get_domains(self) -> List[str]:
        """Return all domains for this organisation."""
        domains = [f"{self.subdomain}.lsx.com"]
        if self.custom_domains and self.custom_domain_verified:
            domains.extend(self.custom_domains)
        return domains

# API Endpoint: Add custom domain
@bp.route('/organisations/<org_id>/custom-domain', methods=['POST'])
@require_auth
@require_permission('owner_admin:organisations:settings')
def add_custom_domain(org_id):
    """
    Add custom domain to organisation.

    Process:
    1. Owner-Admin submits custom domain
    2. System generates DNS verification token
    3. Owner-Admin adds TXT record to their DNS
    4. We verify TXT record exists
    5. Mark domain as verified
    6. Deploy SSL certificate (Let's Encrypt)
    """
    data = request.get_json()
    domain = data.get('custom_domain')

    with get_db_connection() as conn:
        org_repo = OrganisationRepository(conn)
        org = org_repo.find_by_id(org_id)

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)

        # Add to database (unverified)
        org_repo.add_custom_domain(org_id, {
            'domain': domain,
            'verification_token': verification_token,
            'verified': False
        })

    return jsonify({
        'domain': domain,
        'verification_required': True,
        'instruction': f'Add TXT record: _lernsystemx.{domain} = {verification_token}',
        'verification_url': f'/organisations/{org_id}/verify-custom-domain?token={verification_token}'
    }), 201

# Celery Task: Verify custom domain
@app.task
def verify_custom_domain(organisation_id: str, domain: str):
    """
    Celery task to verify custom domain and setup SSL.
    """
    import dns.resolver

    # Check TXT record
    try:
        answers = dns.resolver.resolve(f'_lernsystemx.{domain}', 'TXT')
        if answers:
            with get_db_connection() as conn:
                org_repo = OrganisationRepository(conn)

                # Mark as verified
                org_repo.verify_custom_domain(organisation_id, domain)

                # Setup SSL with Let's Encrypt
                # (Using certbot or similar)
                setup_ssl_certificate(domain)

                return {
                    'status': 'verified',
                    'domain': domain,
                    'ssl_ready': True
                }
    except:
        return {
            'status': 'failed',
            'domain': domain,
            'error': 'TXT record not found'
        }
```

---

## 🔐 Security & Isolation Layers

### Layer 1: JWT Token (Organisation Context)

```python
# app/utils/jwt.py

def create_token(user_id: str, organisation_id: str, role: str):
    """Create JWT with organisation context."""
    payload = {
        'user_id': user_id,
        'organisation_id': organisation_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    """Decode JWT and extract organisation_id."""
    try:
        return jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired")
```

### Layer 2: Row-Level Security (PostgreSQL)

```sql
-- Every query automatically filtered by organisation_id
-- Even if user somehow bypasses app logic, database enforces isolation
SELECT * FROM courses;  -- Returns only courses from set_current_organisation_id()
```

### Layer 3: Repository Pattern Filtering

```python
# app/repositories/course.py

def find_by_id(self, id: str, organisation_id: str) -> Optional[Course]:
    """
    Triple validation:
    1. JWT token contains organisation_id
    2. Repository method requires organisation_id parameter
    3. RLS enforces filtering at database level
    """
    cursor.execute(
        "SELECT * FROM courses WHERE id = %s AND organisation_id = %s",
        (id, organisation_id)  # Always include organisation_id
    )
    return cursor.fetchone()
```

### Layer 4: Frontend Organisation Context

```vue
<!-- frontend/src/App.vue -->

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Frontend knows ONLY its organisation_id (from build-time or auth token)
const currentOrgId = authStore.organisation_id

// All API calls include organisation context
const api = createApiClient({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'X-Organisation-ID': currentOrgId
  }
})
</script>
```

---

## 📊 Deployment Topology

### Development (docker-compose)

```yaml
version: '3.8'

services:
  # Frontend: Firma
  frontend-firma:
    build:
      context: ./frontend
      args:
        VITE_ORG_ID: firma
        VITE_API_BASE_URL: http://localhost:5000
    ports:
      - "3001:80"
    environment:
      - ORG_ID=firma

  # Frontend: Gymnasium
  frontend-gymnasium:
    build:
      context: ./frontend
      args:
        VITE_ORG_ID: gymnasium
        VITE_API_BASE_URL: http://localhost:5000
    ports:
      - "3002:80"

  # Backend (shared)
  backend-api:
    build: ./backend
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - redis

  # Shared Services
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: lernsystemx

  redis:
    image: redis:7-alpine
```

### Production (Kubernetes)

```yaml
# kubernetes/frontend-firma.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-firma
  labels:
    app: lernsystemx
    organisation: firma
    component: frontend

spec:
  replicas: 3  # 3 instances for HA
  selector:
    matchLabels:
      app: lernsystemx-frontend
      organisation: firma

  template:
    metadata:
      labels:
        app: lernsystemx-frontend
        organisation: firma
    spec:
      containers:
      - name: frontend
        image: docker.io/yourregistry/lernsystemx-frontend-firma:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: frontend-firma-service
spec:
  selector:
    app: lernsystemx-frontend
    organisation: firma
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend-firma-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - firma.lsx.com
    - firma-custom.de  # Custom domain support
    secretName: firma-tls
  rules:
  - host: firma.lsx.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-firma-service
            port:
              number: 80
  - host: firma-custom.de
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-firma-service
            port:
              number: 80
```

---

## 🚀 Scaling Strategy

### Horizontal Scaling (Add More Containers)

```bash
# Add new frontend container (new organisation)
docker build --build-arg VITE_ORG_ID=new-org -t lernsystemx-frontend-new-org:latest .
docker run -d --name frontend-new-org lernsystemx-frontend-new-org:latest

# Add backend API instances
docker run -d --name backend-api-4 -p 5004:5000 backend:latest
docker run -d --name backend-api-5 -p 5005:5000 backend:latest

# Update HAProxy config to include new instances
# Reload HAProxy (no downtime)
docker exec haproxy haproxy -f /etc/haproxy/haproxy.cfg -c
docker exec haproxy kill -HUP 1
```

### Vertical Scaling (Upgrade Server Resources)

```bash
# Scale PostgreSQL
# 1. Increase allocated memory/CPU for DB container
# 2. PostgreSQL automatically uses more resources

# Scale Redis
# 1. Increase allocated memory
# 2. Redis maintains all data in memory

# Scale Backend
# 1. Increase gunicorn workers in startup
# 2. Increase container resource limits
```

### Database Sharding (Future)

For extreme scale (1000+ organisations):

```python
# Instead of single PostgreSQL instance, partition by organisation_id

organisations_1_to_500:
  # PostgreSQL instance 1
  Host: db-1.internal
  Orgs: 1-500

organisations_501_to_1000:
  # PostgreSQL instance 2
  Host: db-2.internal
  Orgs: 501-1000

# Routing logic:
shard_number = hash(organisation_id) % num_shards
db_host = shards[shard_number].host
```

---

## 📋 Data Isolation Verification

### Checklist: Verify Tenant Isolation

```sql
-- Test 1: RLS blocks cross-org access
SELECT set_current_organisation_id('firma'::uuid);
SELECT * FROM courses WHERE organisation_id = 'gymnasium'::uuid;
-- Result: 0 rows (RLS blocked it)

-- Test 2: RLS allows same-org access
SELECT set_current_organisation_id('firma'::uuid);
SELECT * FROM courses WHERE organisation_id = 'firma'::uuid;
-- Result: Courses from firma only

-- Test 3: Row-level policy enforced on INSERT
SELECT set_current_organisation_id('firma'::uuid);
INSERT INTO courses (organisation_id, name)
  VALUES ('gymnasium'::uuid, 'Math');
-- Result: Error (RLS policy blocks INSERT with different org_id)

-- Test 4: Verify organisation_id in every table
SELECT
  tablename,
  CASE WHEN 'organisation_id' = ANY(array_agg(attname)) THEN '✓ Has org_id'
       ELSE '✗ MISSING org_id' END
FROM pg_tables
JOIN pg_attribute ON pg_class.oid = attrelid
GROUP BY tablename;
```

---

## 🔄 Multi-Tenancy Request Flow

**Example: User from "Firma" requests their courses**

```
1. Browser: firma.lsx.com
   → Cloudflare resolves → frontend-firma container

2. Frontend: Loads SPA with organisationId = 'firma'
   → Sends: GET /api/courses
      Header: Authorization: Bearer {token with org=firma}

3. HAProxy: Receives request
   → Checks Host header: firma.lsx.com
   → Routes to backend-api-1 (load balanced)

4. Backend App Middleware:
   → Decodes JWT
   → Extracts organisation_id = 'firma'
   → Calls: set_current_organisation_id('firma')
   → Sets: g.organisation_id = 'firma'

5. Repository Layer:
   → Execute: SELECT * FROM courses WHERE organisation_id = %s
   → RLS automatically filters (only firma's courses)
   → Returns: 5 courses

6. Database (PostgreSQL RLS):
   → Before executing query, checks RLS policy
   → Query context: app.current_organisation_id = 'firma'
   → Policy: USING (organisation_id = current_setting(...))
   → Returns: Only courses with organisation_id = 'firma'

7. Backend Response:
   → Returns 5 courses to frontend

8. Frontend: Renders courses for firma.lsx.com user

✓ Result: Complete tenant isolation, multiple layers enforced
```

---

## 📊 Comparison: Single-Tenant vs Multi-Tenant vs Hybrid

| Aspect | Single-Tenant | Multi-Tenant (DB) | Hybrid (Our Approach) |
|--------|--------------|-------------------|----------------------|
| **Backend Instances** | 1 per org | 1 shared | 1 shared |
| **Database** | Separate DB per org | Shared DB with RLS | Shared DB with RLS |
| **Frontend** | Deployed once | Deployed once | Per org (can customize) |
| **Cost** | 🔴 Very high | 🟢 Very low | 🟢 Low (shared) + 🟡 Medium (frontend) |
| **Isolation** | 🟢 Perfect | 🟡 Code-dependent | 🟢 Perfect (RLS) |
| **Customization** | 🟢 Easy | 🔴 Hard | 🟢 Easy (frontend only) |
| **Scalability** | 🔴 N containers | 🟢 1 backend | 🟢 N frontend + 1 backend |
| **Data Privacy** | 🟢 Perfect | 🟡 Risky | 🟢 Perfect |
| **Maintenance** | 🔴 Complex | 🟢 Simple | 🟢 Simple |

---

## 🔐 Disaster Recovery & Backup

### Backup Strategy

```bash
# Daily backup of PostgreSQL (all organisations)
0 3 * * * pg_dump lernsystemx | gzip > /backups/lernsystemx-$(date +\%Y\%m\%d).sql.gz

# Weekly backup to S3
0 4 * * 0 aws s3 cp /backups/lernsystemx-$(date +\%Y\%m\%d).sql.gz s3://backups/

# Retain backups: 30 days local, 1 year in S3
find /backups -mtime +30 -delete
```

### Disaster Recovery Plan

**Scenario 1: PostgreSQL data loss (single table)**

```bash
# 1. Identify organization
SELECT organisation_id, COUNT(*) as deleted_rows
FROM courses_deleted_log
WHERE deleted_at > NOW() - INTERVAL '1 hour';

# 2. Restore from backup (all organisations affected)
pg_restore -d lernsystemx /backups/lernsystemx-YYYYMMDD.sql.gz

# 3. Manual fix: Re-apply changes for other orgs that were modified
# (This is why daily backups are important)
```

**Scenario 2: Frontend container crash**

```bash
# 1. Docker automatically restarts container (restart policy)
# 2. If persistent issue, deploy fresh container from image
docker rm frontend-firma
docker run -d --name frontend-firma frontend-firma:latest
```

**Scenario 3: Complete data center loss**

```bash
# 1. Use S3 backups to restore PostgreSQL
aws s3 cp s3://backups/lernsystemx-LATEST.sql.gz /tmp/
pg_restore -d lernsystemx /tmp/lernsystemx-LATEST.sql.gz

# 2. Re-deploy backend on new server
docker pull backend:latest
docker run -d --name backend-api backend:latest

# 3. Re-deploy all frontend containers
for org in firma gymnasium universität; do
  docker pull frontend-$org:latest
  docker run -d --name frontend-$org frontend-$org:latest
done

# RTO: ~1 hour | RPO: ~1 day
```

---

## 🎓 Learning & Roadmap

### Phase 1: Current State (✅ Complete)
- Single shared backend
- Per-organisation frontend containers
- Subdomain routing (firma.lsx.com)

### Phase 2: Enhancements (Planned)
- [ ] Custom domain support
- [ ] Kubernetes deployment
- [ ] Automated SSL certificates (Let's Encrypt)
- [ ] Blue-green deployments for zero downtime

### Phase 3: Advanced (Future)
- [ ] Database sharding (for extreme scale)
- [ ] Multi-region deployment
- [ ] Federated authentication (SSO per org)
- [ ] Full SaaS capabilities

---

## 📚 References

- [Cloudflare DNS + CDN](https://www.cloudflare.com/)
- [PostgreSQL Row-Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [HAProxy Load Balancing](http://www.haproxy.org/)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Kubernetes Multi-Tenant Applications](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/cpu-default-namespace/)

---

**Version:** 1.0
**Status:** ACTIVE (Architecture Planning Complete)
**Last Updated:** 2026-01-22
**Maintainer:** Development Team

> 💡 **Hinweis:** Dieses Dokument spezifiziert die Hybrid Multi-Tenancy Architektur für LernSystemX.
> Implementierung folgt nach completion der Group-Permission-System (Phase 1).
