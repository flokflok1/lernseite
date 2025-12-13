# Phase 21: API Gateway - Implementation

**LernsystemX Backend**
**Status:** ✅ Implemented
**Based on:** Dok 32 (API-Gateway)

---

## 1. Overview

Phase 21 implements a centralized API Gateway for LernsystemX, providing unified request routing, rate limiting, analytics, and multi-tenant support.

### 1.1 Implemented Features

| Feature | Status | Location |
|---------|--------|----------|
| **Gateway Configuration** | ✅ | `backend/app/config.py` |
| **Gateway Router** | ✅ | `backend/app/gateway/router.py` |
| **Gateway Middleware** | ✅ | `backend/app/gateway/middleware.py` |
| **Gateway Analytics** | ✅ | `backend/app/gateway/analytics.py` |
| **Gateway Rate Limiting** | ✅ | `backend/app/gateway/rate_limiting.py` |
| **Integration** | ✅ | `backend/app/__init__.py` |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Request                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Nginx (Reverse Proxy)                                       │
│  - SSL/TLS Termination                                       │
│  - IP-based Rate Limiting                                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  API Gateway (Application Layer - Phase 21)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Gateway Middleware                                │   │
│  │    - Request size validation                         │   │
│  │    - Content-Type validation                         │   │
│  │    - Multi-tenant header processing                  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 2. Gateway Analytics                                 │   │
│  │    - Request ID generation                           │   │
│  │    - Route group detection                           │   │
│  │    - Duration tracking                               │   │
│  │    - Prometheus metrics                              │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 3. Gateway Rate Limiting                             │   │
│  │    - Public: 10/min                                  │   │
│  │    - App: 100/min                                    │   │
│  │    - Admin: 200/min                                  │   │
│  │    - KI: 30/min                                      │   │
│  │    - Analytics: 60/min                               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 4. Route Segmentation                                │   │
│  │    - /api/v1/public/*     (Public APIs)             │   │
│  │    - /api/v1/*            (App/User APIs)           │   │
│  │    - /api/v1/admin/*      (Admin APIs)              │   │
│  │    - /api/v1/organisations/* (Org APIs)             │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Flask Blueprints (Existing API Endpoints)                   │
│  - Auth, Users, Courses, Orgs, Analytics, etc.              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Components

### 3.1 Gateway Configuration (`backend/app/config.py`)

Added to `ProductionConfig` (lines 324-355):

```python
# API Gateway Configuration (Phase 21)
API_GATEWAY_ENABLED = True
API_BASE_PATH = '/api/v1'
API_VERSION = '1'

# API Gateway Prefixes
API_PUBLIC_PREFIX = '/api/v1/public'
API_APP_PREFIX = '/api/v1'
API_ADMIN_PREFIX = '/api/v1/admin'
API_ORG_PREFIX = '/api/v1/organisations'

# Gateway Logging & Analytics
API_GATEWAY_LOG_REQUESTS = True
API_GATEWAY_TRACK_ANALYTICS = True
API_GATEWAY_REQUEST_ID_HEADER = 'X-LSX-Request-ID'

# Gateway Rate Limiting (per route group)
API_GATEWAY_RATE_LIMIT_DEFAULT = '100 per minute'
API_GATEWAY_RATE_LIMIT_ADMIN = '200 per minute'
API_GATEWAY_RATE_LIMIT_PUBLIC = '10 per minute'
API_GATEWAY_RATE_LIMIT_KI = '30 per minute'
API_GATEWAY_RATE_LIMIT_ANALYTICS = '60 per minute'
API_GATEWAY_RATE_LIMIT_LIVEROOM = '100 per minute'

# Gateway Request Validation
API_GATEWAY_MAX_BODY_SIZE = 20 * 1024 * 1024  # 20MB
API_GATEWAY_VALIDATE_CONTENT_TYPE = True

# Multi-Tenant Domain Routing
API_GATEWAY_MULTI_TENANT_ENABLED = True
API_GATEWAY_DEFAULT_ORG_HEADER = 'X-LSX-Org-ID'
API_GATEWAY_CLIENT_HEADER = 'X-LSX-Client'
```

**Environment Variables:** See `.env.production.example` (lines 233-268)

---

### 3.2 Gateway Router (`backend/app/gateway/router.py`)

**Responsibilities:**
- Central route registration
- Route group segmentation
- Backward compatibility with existing blueprints

**Route Groups:**

| Group | Prefix | Description |
|-------|--------|-------------|
| **Public** | `/api/v1/public/*` | Public APIs (future, limited access) |
| **Auth** | `/api/v1/auth/*` | Authentication endpoints |
| **App** | `/api/v1/*` | User/App APIs (authenticated) |
| **Admin** | `/api/v1/admin/*` | Admin APIs (system admins) |
| **Org** | `/api/v1/organisations/*` | Organisation APIs |
| **Health** | `/health`, `/metrics` | Health checks, monitoring |

**Usage:**

```python
from app.gateway import register_gateway_routes

# In Flask factory
register_gateway_routes(app)
```

**Route Group Detection:**

```python
from app.gateway.router import get_route_group

route_group = get_route_group('/api/v1/admin/users')
# Returns: 'admin'

route_group = get_route_group('/api/v1/courses')
# Returns: 'app'
```

---

### 3.3 Gateway Middleware (`backend/app/gateway/middleware.py`)

**Request Validation:**

1. **Request Size Validation**
   - Max: 20MB (configurable via `API_GATEWAY_MAX_BODY_SIZE`)
   - Returns `413 Request Entity Too Large` if exceeded

2. **Content-Type Validation**
   - POST/PUT/PATCH must have `Content-Type: application/json` or `multipart/form-data`
   - Returns `415 Unsupported Media Type` if invalid

3. **Multi-Tenant Header Processing**
   - Extracts `X-LSX-Org-ID` → `g.gateway_org_id`
   - Extracts `X-LSX-Client` → `g.gateway_client_type` (web|mobile|admin)

**Setup:**

```python
from app.gateway.middleware import setup_gateway_middleware

setup_gateway_middleware(app)
```

---

### 3.4 Gateway Analytics (`backend/app/gateway/analytics.py`)

**Request Tracking:**

1. **Before Request:**
   - Generate unique request ID (UUID)
   - Store start time
   - Detect route group

2. **After Request:**
   - Calculate duration
   - Add response headers:
     - `X-LSX-Request-ID`: Request tracking ID
     - `X-LSX-API-Version`: API version (1)
     - `X-LSX-Route-Group`: Route group (debug only)
   - Log analytics (no sensitive data)
   - Track Prometheus metrics

**Log Format:**

```json
{
  "request_id": "abc-123-xyz",
  "route_group": "admin",
  "method": "GET",
  "path": "/api/v1/admin/analytics",
  "status": 200,
  "duration_ms": 45.2,
  "user_id": 123,
  "org_id": 5,
  "ip": "192.168.1.100"
}
```

**Prometheus Metrics:**

```python
# Request count by route group
http_requests_total{method="GET", endpoint="...", status="200", route_group="admin"}

# Request duration by route group
http_request_duration_seconds{method="GET", endpoint="...", route_group="admin"}
```

**Setup:**

```python
from app.gateway.analytics import setup_gateway_analytics

setup_gateway_analytics(app)
```

---

### 3.5 Gateway Rate Limiting (`backend/app/gateway/rate_limiting.py`)

**Rate Limits per Route Group:**

| Route Group | Default Limit | Config Key |
|-------------|---------------|------------|
| Public | 10/min | `API_GATEWAY_RATE_LIMIT_PUBLIC` |
| App/User | 100/min | `API_GATEWAY_RATE_LIMIT_DEFAULT` |
| Admin | 200/min | `API_GATEWAY_RATE_LIMIT_ADMIN` |
| KI | 30/min | `API_GATEWAY_RATE_LIMIT_KI` |
| Analytics | 60/min | `API_GATEWAY_RATE_LIMIT_ANALYTICS` |
| LiveRoom | 100/min | `API_GATEWAY_RATE_LIMIT_LIVEROOM` |

**Usage:**

```python
from app.gateway.rate_limiting import gateway_rate_limit

# Automatic route group detection
@app.route('/api/v1/admin/users')
@gateway_rate_limit()
def admin_users():
    # Rate limit: 200/min (admin group)
    ...

# Custom scope
@app.route('/api/v1/ki/generate')
@gateway_rate_limit(scope='ki')
def generate_content():
    # Rate limit: 30/min (KI scope)
    ...
```

**Rate Limit Keys:**
- User-based: `user:{user_id}` (if authenticated)
- IP-based: `ip:{ip_address}` (fallback)

**Setup:**

```python
from app.gateway.rate_limiting import setup_gateway_rate_limiting

setup_gateway_rate_limiting(app)
```

---

## 4. Integration

### 4.1 Flask Factory (`backend/app/__init__.py`)

```python
def create_app(config_name=None):
    app = Flask(__name__)

    # ... (existing setup)

    # Setup API Gateway (Phase 21) - BEFORE blueprint registration
    setup_gateway(app)

    # Register blueprints via gateway
    register_blueprints(app)

    # ... (rest of setup)

    return app


def setup_gateway(app):
    """Setup all gateway components"""
    from app.gateway import setup_gateway_middleware
    from app.gateway.analytics import setup_gateway_analytics
    from app.gateway.rate_limiting import setup_gateway_rate_limiting

    setup_gateway_middleware(app)
    setup_gateway_analytics(app)
    setup_gateway_rate_limiting(app)


def register_blueprints(app):
    """Register routes through Gateway"""
    from app.gateway import register_gateway_routes

    register_gateway_routes(app)
```

---

## 5. Response Headers

All API responses include gateway headers:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-LSX-Request-ID: abc-123-xyz-456
X-LSX-API-Version: 1
X-LSX-Route-Group: admin  # Debug mode only
```

---

## 6. Multi-Tenant Support

### 6.1 Request Headers

Clients can specify organisation and client type:

```http
POST /api/v1/courses HTTP/1.1
Authorization: Bearer <jwt>
Content-Type: application/json
X-LSX-Org-ID: 51
X-LSX-Client: web
```

### 6.2 Backend Usage

```python
from flask import g, request

@app.route('/api/v1/courses')
@token_required
def get_courses():
    # Access extracted headers
    org_id = g.gateway_org_id  # From X-LSX-Org-ID
    client_type = g.gateway_client_type  # From X-LSX-Client (web|mobile|admin)

    # Use for multi-tenant filtering
    courses = CourseRepository.find_by_organisation(org_id)
    return jsonify(courses)
```

---

## 7. Testing

### 7.1 Gateway Headers Test

```bash
curl -I http://localhost:5000/api/v1/health

# Expected headers:
# X-LSX-Request-ID: abc-123-xyz
# X-LSX-API-Version: 1
```

### 7.2 Rate Limiting Test

```bash
# Test admin rate limit (200/min)
for i in {1..210}; do
    curl -X GET http://localhost:5000/api/v1/admin/analytics \
        -H "Authorization: Bearer <admin-token>" \
        -w "\n%{http_code}\n"
done

# Expected: 200 for first 200 requests, 429 after
```

### 7.3 Request Size Validation Test

```bash
# Test 20MB limit
dd if=/dev/zero bs=1M count=25 | curl -X POST http://localhost:5000/api/v1/courses \
    -H "Content-Type: application/json" \
    --data-binary @-

# Expected: 413 Request Entity Too Large
```

### 7.4 Content-Type Validation Test

```bash
# Missing Content-Type
curl -X POST http://localhost:5000/api/v1/courses \
    -d '{"title":"Test"}' \
    -H "Authorization: Bearer <token>"

# Expected: 400 Bad Request (Missing Content-Type header)

# Invalid Content-Type
curl -X POST http://localhost:5000/api/v1/courses \
    -H "Content-Type: text/plain" \
    -d '{"title":"Test"}' \
    -H "Authorization: Bearer <token>"

# Expected: 415 Unsupported Media Type
```

---

## 8. Monitoring

### 8.1 Prometheus Queries

```promql
# Requests per minute by route group
rate(http_requests_total[5m])

# Requests by route group
sum(rate(http_requests_total[5m])) by (route_group)

# Admin API usage
sum(rate(http_requests_total{route_group="admin"}[5m]))

# Error rate by route group
sum(rate(http_requests_total{status=~"5.."}[5m])) by (route_group)

# Average response time by route group
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
) by (route_group)
```

### 8.2 Grafana Dashboard

Create panels for:
- Request rate per route group
- Error rate per route group
- P95 latency per route group
- Rate limit hits per group
- Top users by request count

---

## 9. Configuration Reference

### 9.1 Core Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `API_GATEWAY_ENABLED` | `True` | Enable/disable gateway |
| `API_BASE_PATH` | `/api/v1` | Base API path |
| `API_VERSION` | `1` | API version number |

### 9.2 Rate Limiting

| Setting | Default | Description |
|---------|---------|-------------|
| `API_GATEWAY_RATE_LIMIT_DEFAULT` | `100 per minute` | Default rate limit |
| `API_GATEWAY_RATE_LIMIT_ADMIN` | `200 per minute` | Admin endpoints |
| `API_GATEWAY_RATE_LIMIT_PUBLIC` | `10 per minute` | Public endpoints |
| `API_GATEWAY_RATE_LIMIT_KI` | `30 per minute` | KI endpoints |
| `API_GATEWAY_RATE_LIMIT_ANALYTICS` | `60 per minute` | Analytics endpoints |

### 9.3 Validation

| Setting | Default | Description |
|---------|---------|-------------|
| `API_GATEWAY_MAX_BODY_SIZE` | `20971520` | Max request size (bytes) |
| `API_GATEWAY_VALIDATE_CONTENT_TYPE` | `True` | Enforce Content-Type |

### 9.4 Multi-Tenant

| Setting | Default | Description |
|---------|---------|-------------|
| `API_GATEWAY_MULTI_TENANT_ENABLED` | `True` | Enable multi-tenant routing |
| `API_GATEWAY_DEFAULT_ORG_HEADER` | `X-LSX-Org-ID` | Organisation header |
| `API_GATEWAY_CLIENT_HEADER` | `X-LSX-Client` | Client type header |

---

## 10. Best Practices

1. **Always use route group detection** instead of hardcoding paths
2. **Include X-LSX-Request-ID** in error logs for tracing
3. **Monitor rate limit hits** to identify legitimate high-traffic users
4. **Use X-LSX-Org-ID** for multi-tenant filtering
5. **Track route group metrics** separately in Prometheus
6. **Test rate limits** in staging before adjusting production
7. **Document custom rate limits** when applying `@gateway_rate_limit(scope='custom')`

---

## 11. Future Enhancements

**Phase 22+ (Planned):**
- Public API endpoints (`/api/v1/public/*`)
- API key authentication for external integrations
- GraphQL gateway (alternative to REST)
- WebSocket gateway for LiveRoom
- Circuit breaker pattern for service failures
- Request transformation/enrichment
- Response caching at gateway level

---

## 12. References

- **Dok 32:** API-Gateway (LernsystemX)
- **Dok 15:** API-Spezifikation
- **Phase 19:** Monitoring & Alerting (Prometheus integration)
- **Phase 20:** Security Architecture (Rate limiting base)
- **Flask-Limiter:** https://flask-limiter.readthedocs.io/

---

**Implementation Date:** Phase 21
**Last Updated:** 2025
**Status:** ✅ Production Ready
