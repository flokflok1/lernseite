# Phase 22: API Versioning & Change Management - Implementation

**LernsystemX Backend**
**Status:** ✅ Implemented
**Based on:** Dok 33 (Versioning-Change-Management.md)

---

## 1. Overview

Phase 22 implements comprehensive API versioning and change management for LernsystemX, enabling controlled evolution of the API while maintaining backward compatibility.

### 1.1 Implemented Features

| Feature | Status | Location |
|---------|--------|----------|
| **Versioning Configuration** | ✅ | `backend/app/config.py` |
| **Version Detection** | ✅ | `backend/app/gateway/versioning.py` |
| **Deprecation Decorator** | ✅ | `backend/app/api/deprecation.py` |
| **System Version Endpoints** | ✅ | `backend/app/api/admin_system.py` |
| **Gateway Integration** | ✅ | `backend/app/__init__.py` |
| **Migration Strategy** | ✅ | `backend/docs/architecture/database-migration-strategy.md` |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Request                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Version Detection (before_request)                       │
│     - Extract from URL: /api/v{N}/                          │
│     - Optional header: X-LSX-API-Version                     │
│     - Store in g.api_version                                 │
│     - Validate against supported versions                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Deprecation Check (optional)                             │
│     - @deprecated decorator on endpoint                      │
│     - Check sunset date                                      │
│     - Log deprecated usage                                   │
│     - Return 410 Gone if past sunset                         │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Request Processing                                       │
│     - Normal endpoint execution                              │
│     - Version-specific logic (if needed)                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Response Headers (after_request)                         │
│     - X-LSX-API-Version: 1                                   │
│     - X-LSX-System-Version: 1.0.0                            │
│     - X-LSX-Deprecated: true/false                           │
│     - X-LSX-Deprecation-Date: YYYY-MM-DD                     │
│     - X-LSX-Sunset-Date: YYYY-MM-DD                          │
│     - X-LSX-Replacement: /api/v2/...                         │
│     - X-LSX-Migration-Guide: URL                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Client Response                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Components

### 3.1 Configuration (`backend/app/config.py`)

Added to `ProductionConfig` (lines 357-400):

```python
# System Version (Semantic Versioning: MAJOR.MINOR.PATCH)
LSX_VERSION = os.getenv('LSX_VERSION', '1.0.0')
LSX_ENV = os.getenv('LSX_ENV', 'production')

# API Version Configuration
API_VERSION_CURRENT = int(os.getenv('API_VERSION_CURRENT', '1'))
API_VERSION_SUPPORTED = os.getenv('API_VERSION_SUPPORTED', '1').split(',')
API_VERSION_DEFAULT = int(os.getenv('API_VERSION_DEFAULT', '1'))

# API Version Headers
API_VERSION_HEADER = os.getenv('API_VERSION_HEADER', 'X-LSX-API-Version')
API_SYSTEM_VERSION_HEADER = os.getenv('API_SYSTEM_VERSION_HEADER', 'X-LSX-System-Version')

# Deprecation Configuration
API_DEPRECATION_ENABLED = os.getenv('API_DEPRECATION_ENABLED', 'True').lower() == 'true'
API_DEPRECATION_HEADER = os.getenv('API_DEPRECATION_HEADER', 'X-LSX-Deprecated')
API_DEPRECATION_DATE_HEADER = os.getenv('API_DEPRECATION_DATE_HEADER', 'X-LSX-Deprecation-Date')
API_SUNSET_DATE_HEADER = os.getenv('API_SUNSET_DATE_HEADER', 'X-LSX-Sunset-Date')
API_MIGRATION_GUIDE_HEADER = os.getenv('API_MIGRATION_GUIDE_HEADER', 'X-LSX-Migration-Guide')
API_REPLACEMENT_HEADER = os.getenv('API_REPLACEMENT_HEADER', 'X-LSX-Replacement')

# Deprecation Notice URL
API_DEPRECATION_NOTICE_URL = os.getenv(
    'API_DEPRECATION_NOTICE_URL',
    'https://docs.lernsystemx.de/api/deprecation-notices'
)

# Version Support Window (in months)
API_VERSION_SUPPORT_WINDOW = int(os.getenv('API_VERSION_SUPPORT_WINDOW', '12'))
API_VERSION_DEPRECATION_WARNING = int(os.getenv('API_VERSION_DEPRECATION_WARNING', '6'))

# Version Detection Strategy
API_VERSION_DETECTION = os.getenv('API_VERSION_DETECTION', 'url')  # url, header, both
API_VERSION_ALLOW_HEADER_OVERRIDE = os.getenv('API_VERSION_ALLOW_HEADER_OVERRIDE', 'False').lower() == 'true'

# Breaking Change Protection
API_ENFORCE_VERSION_CHECK = os.getenv('API_ENFORCE_VERSION_CHECK', 'True').lower() == 'true'
API_REJECT_UNSUPPORTED_VERSIONS = os.getenv('API_REJECT_UNSUPPORTED_VERSIONS', 'True').lower() == 'true'
```

**Environment Variables:** See `.env.production.example` (lines 270-309)

---

### 3.2 Version Detection (`backend/app/gateway/versioning.py`)

**Responsibilities:**
- Extract API version from URL or header
- Validate version support
- Add version headers to responses
- Manage deprecation information

**Key Classes:**

#### `APIVersionManager`

```python
class APIVersionManager:
    """Manages API version detection, validation, and headers."""

    def detect_api_version(self):
        """Detect version from URL or header before each request"""
        # 1. Extract from URL: /api/v{N}/
        version = self._extract_version_from_url(request.path)

        # 2. Optional: Override from header
        if allow_header_override:
            header_version = self._extract_version_from_header()
            if header_version:
                version = header_version

        # 3. Validate and store
        g.api_version = version
        return self._validate_version(version)

    def add_version_headers(self, response):
        """Add version headers to response"""
        response.headers['X-LSX-API-Version'] = str(api_version)
        response.headers['X-LSX-System-Version'] = system_version
        # ... deprecation headers if applicable
        return response
```

**Usage:**

```python
from app.gateway.versioning import get_api_version, get_version_info

# Get current request's API version
version = get_api_version()  # Returns: 1

# Get comprehensive version info
info = get_version_info()
# Returns: {
#   'system_version': '1.0.0',
#   'api': {'current_version': 1, 'supported_versions': [1], ...},
#   'detection': {'strategy': 'url', ...},
#   'deprecation': {'enabled': True, ...}
# }
```

---

### 3.3 Deprecation Decorator (`backend/app/api/deprecation.py`)

**Responsibilities:**
- Mark endpoints as deprecated
- Add deprecation headers
- Log deprecated usage
- Enforce sunset dates (return 410 Gone)

**Usage:**

```python
from app.api.deprecation import deprecated

@app.route('/api/v1/old-endpoint')
@deprecated(
    deprecation_date='2025-06-01',
    sunset_date='2026-06-01',
    replacement='/api/v2/new-endpoint',
    migration_guide='https://docs.lernsystemx.de/api/v1-to-v2/migration',
    reason='Replaced by improved v2 implementation'
)
def old_endpoint():
    return {'data': 'old'}
```

**Response Headers (when deprecated):**

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-LSX-Deprecated: true
X-LSX-Deprecation-Date: 2025-06-01
X-LSX-Sunset-Date: 2026-06-01
X-LSX-Replacement: /api/v2/new-endpoint
X-LSX-Migration-Guide: https://docs.lernsystemx.de/api/v1-to-v2/migration
X-LSX-Days-Until-Sunset: 180
```

**After Sunset Date:**

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
    "success": false,
    "error": "Endpoint Sunset",
    "message": "This endpoint was sunset on 2026-06-01",
    "deprecation_date": "2025-06-01",
    "sunset_date": "2026-06-01",
    "replacement": "/api/v2/new-endpoint",
    "migration_guide": "https://docs.lernsystemx.de/api/v1-to-v2/migration"
}
```

**Logging:**

```json
{
    "event": "deprecated_endpoint_usage",
    "endpoint": "/api/v1/old-endpoint",
    "method": "GET",
    "user_id": 123,
    "ip": "192.168.1.100",
    "deprecation_date": "2025-06-01",
    "sunset_date": "2026-06-01",
    "days_until_sunset": 180,
    "replacement": "/api/v2/new-endpoint",
    "user_agent": "Mozilla/5.0 ..."
}
```

---

### 3.4 Admin System Endpoints (`backend/app/api/admin_system.py`)

**Endpoints:**

#### GET /api/v1/admin/system/version

Returns comprehensive system version information.

**Authentication:** Required (Admin only)

**Response:**
```json
{
    "success": true,
    "data": {
        "system": {
            "version": "1.0.0",
            "environment": "production",
            "python_version": "3.12.0",
            "platform": "Linux",
            "platform_version": "5.15.0"
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
        },
        "build": {
            "timestamp": "2025-01-15T10:30:00Z",
            "git_commit": "abc123def456"
        }
    },
    "timestamp": "2025-01-15T10:30:00Z"
}
```

#### GET /api/v1/admin/system/deprecated-endpoints

Returns list of all deprecated endpoints.

**Response:**
```json
{
    "success": true,
    "data": {
        "total_deprecated": 2,
        "endpoints": [
            {
                "endpoint": "old_users_endpoint",
                "path": "/api/v1/users/old",
                "methods": ["GET", "POST"],
                "deprecation_date": "2025-06-01",
                "sunset_date": "2026-06-01",
                "days_until_sunset": 365,
                "replacement": "/api/v2/users",
                "migration_guide": "https://docs.lernsystemx.de/api/v1-to-v2/users",
                "reason": "Replaced by improved v2 implementation"
            }
        ]
    },
    "timestamp": "2025-01-15T10:30:00Z"
}
```

#### GET /api/v1/admin/system/health/detailed

Enhanced health check with version info.

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "version": {
            "system": "1.0.0",
            "api_current": 1,
            "api_supported": [1]
        },
        "components": {
            "database": "healthy",
            "redis": "healthy",
            "celery": "healthy"
        },
        "deprecation": {
            "total_deprecated_endpoints": 2,
            "deprecation_enabled": true
        }
    }
}
```

---

## 4. Integration

### 4.1 Flask Factory (`backend/app/__init__.py`)

```python
def setup_gateway(app):
    """
    Setup API Gateway (Phase 21 + Phase 22).
    """
    from app.gateway import setup_gateway_versioning
    # ... other gateway setup

    # Setup API versioning (Phase 22)
    setup_gateway_versioning(app)
```

The versioning system integrates seamlessly with the existing API Gateway from Phase 21.

---

## 5. Version Support Strategy

### 5.1 Support Windows

Based on Dok 33:

| Stage | Duration | Description |
|-------|----------|-------------|
| **Active** | Current | Full support, new features |
| **Deprecated** | 6 months warning | Still supported, deprecation headers added |
| **Sunset** | After 12 months total | Version removed, 410 Gone responses |

### 5.2 Example Timeline

```
v1 Released: 2025-01-01

v2 Released: 2026-01-01
├─ v1 Deprecated: 2026-01-01 (6 months warning)
│  └─ X-LSX-Deprecated: true
│  └─ X-LSX-Deprecation-Date: 2026-01-01
│  └─ X-LSX-Sunset-Date: 2026-07-01

v1 Sunset: 2026-07-01 (12 months after v2 release)
└─ Returns 410 Gone
```

### 5.3 Compatibility Matrix

| API Version | System Version | DB Schema | Status |
|-------------|----------------|-----------|--------|
| v1 | 1.0.0 - 1.9.x | 1.0 - 1.9 | ✅ Active |
| v2 | 2.0.0+ | 2.0+ | 🔮 Planned |

---

## 6. Response Headers Reference

### 6.1 Version Headers (Always Present)

| Header | Example | Description |
|--------|---------|-------------|
| `X-LSX-API-Version` | `1` | Current API version used for this request |
| `X-LSX-System-Version` | `1.0.0` | System version (SEMVER) |

### 6.2 Deprecation Headers (When Endpoint Deprecated)

| Header | Example | Description |
|--------|---------|-------------|
| `X-LSX-Deprecated` | `true` | Indicates endpoint is deprecated |
| `X-LSX-Deprecation-Date` | `2025-06-01` | Date when deprecation was announced |
| `X-LSX-Sunset-Date` | `2026-06-01` | Date when endpoint will be removed |
| `X-LSX-Replacement` | `/api/v2/users` | Replacement endpoint path |
| `X-LSX-Migration-Guide` | `https://...` | URL to migration guide |
| `X-LSX-Days-Until-Sunset` | `180` | Days remaining until sunset |

---

## 7. Testing

### 7.1 Version Detection Test

```bash
# URL-based version detection
curl -I http://localhost:5000/api/v1/health

# Expected headers:
# X-LSX-API-Version: 1
# X-LSX-System-Version: 1.0.0

# Header-based version override (if enabled)
curl -I http://localhost:5000/api/health \
    -H "X-LSX-API-Version: 1"
```

### 7.2 Unsupported Version Test

```bash
# Request unsupported version
curl http://localhost:5000/api/v99/health

# Expected response:
# {
#   "success": false,
#   "error": "Unsupported API version",
#   "message": "API v99 is not supported",
#   "current_version": 1,
#   "supported_versions": [1]
# }
# Status: 410 Gone
```

### 7.3 Deprecation Test

```python
# Test endpoint (example)
@api_v1.route('/test/deprecated')
@deprecated(
    deprecation_date='2025-01-01',
    sunset_date='2025-12-31',
    replacement='/api/v2/test/new'
)
def test_deprecated():
    return {'message': 'This endpoint is deprecated'}
```

```bash
# Test deprecated endpoint
curl -I http://localhost:5000/api/v1/test/deprecated

# Expected headers:
# X-LSX-Deprecated: true
# X-LSX-Deprecation-Date: 2025-01-01
# X-LSX-Sunset-Date: 2025-12-31
# X-LSX-Replacement: /api/v2/test/new
# X-LSX-Days-Until-Sunset: 350
```

### 7.4 Admin Endpoints Test

```bash
# Get system version (admin only)
curl http://localhost:5000/api/v1/admin/system/version \
    -H "Authorization: Bearer <admin-token>"

# Get deprecated endpoints list
curl http://localhost:5000/api/v1/admin/system/deprecated-endpoints \
    -H "Authorization: Bearer <admin-token>"
```

---

## 8. Migration from v1 to v2 (Example)

### 8.1 Step 1: Implement v2 Endpoints

```python
# backend/app/api/v2/users.py (future)
from app.api.v2 import api_v2

@api_v2.route('/users/<int:user_id>')
def get_user_v2(user_id):
    # New v2 implementation with enhanced features
    return {
        'id': user_id,
        'profile': {...},
        'metadata': {...}  # New in v2
    }
```

### 8.2 Step 2: Mark v1 as Deprecated

```python
# backend/app/api/users.py
from app.api.deprecation import deprecated

@api_v1.route('/users/<int:user_id>')
@deprecated(
    deprecation_date='2026-01-01',
    sunset_date='2026-07-01',
    replacement='/api/v2/users/{user_id}',
    migration_guide='https://docs.lernsystemx.de/api/v1-to-v2/users',
    reason='v2 provides enhanced user metadata and improved response structure'
)
def get_user_v1(user_id):
    # Old v1 implementation (still works, but deprecated)
    return {'id': user_id, 'name': '...'}
```

### 8.3 Step 3: Update Configuration

```env
# .env.production
API_VERSION_CURRENT=2
API_VERSION_SUPPORTED=1,2  # Support both v1 and v2
API_VERSION_DEFAULT=2
```

### 8.4 Step 4: Monitor Deprecated Usage

```bash
# Check deprecated endpoint usage
curl http://localhost:5000/api/v1/admin/system/deprecated-endpoints \
    -H "Authorization: Bearer <admin-token>"

# Check logs for deprecated usage
grep "deprecated_endpoint_usage" logs/application.log
```

### 8.5 Step 5: Sunset v1 (After 12 Months)

```env
# .env.production
API_VERSION_CURRENT=2
API_VERSION_SUPPORTED=2  # Remove v1 from supported versions
API_VERSION_DEFAULT=2
```

Now requests to v1 endpoints return:
```json
{
    "success": false,
    "error": "Unsupported API version",
    "message": "API v1 is not supported",
    "current_version": 2,
    "supported_versions": [2]
}
```

---

## 9. Best Practices

### 9.1 Versioning

1. **Use URL-based versioning** (`/api/v1/`, `/api/v2/`) for clarity
2. **Maintain backward compatibility** within major version
3. **Only increment major version** for breaking changes
4. **Provide 12 months support** for deprecated versions
5. **Give 6 months warning** before sunset

### 9.2 Deprecation

1. **Always provide replacement endpoint** in deprecation notice
2. **Write migration guides** for deprecated endpoints
3. **Log deprecated usage** for monitoring
4. **Enforce sunset dates** to maintain clean codebase
5. **Communicate clearly** in headers and documentation

### 9.3 Documentation

1. **Update CHANGELOG.md** for all version changes
2. **Document breaking changes** explicitly
3. **Provide migration examples** in docs
4. **Keep version matrix** up to date
5. **Reference CR numbers** in migration docs

---

## 10. Configuration Reference

### 10.1 Core Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `LSX_VERSION` | `1.0.0` | System version (SEMVER) |
| `API_VERSION_CURRENT` | `1` | Current active API version |
| `API_VERSION_SUPPORTED` | `1` | Comma-separated supported versions |
| `API_VERSION_DEFAULT` | `1` | Default version if not specified |

### 10.2 Detection Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `API_VERSION_DETECTION` | `url` | Detection strategy (url, header, both) |
| `API_VERSION_ALLOW_HEADER_OVERRIDE` | `False` | Allow header to override URL version |
| `API_ENFORCE_VERSION_CHECK` | `True` | Enforce version validation |
| `API_REJECT_UNSUPPORTED_VERSIONS` | `True` | Return 410 for unsupported versions |

### 10.3 Deprecation Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `API_DEPRECATION_ENABLED` | `True` | Enable deprecation mechanism |
| `API_VERSION_SUPPORT_WINDOW` | `12` | Support window in months |
| `API_VERSION_DEPRECATION_WARNING` | `6` | Warning period in months |
| `API_DEPRECATION_NOTICE_URL` | `https://...` | URL for deprecation notices |

---

## 11. Monitoring & Metrics

### 11.1 Prometheus Metrics (Future)

```promql
# Requests per API version
sum(rate(http_requests_total[5m])) by (api_version)

# Deprecated endpoint calls
sum(rate(deprecated_endpoint_calls[5m])) by (endpoint)

# Days until sunset (alert threshold)
deprecated_endpoint_days_until_sunset < 30
```

### 11.2 Log Analysis

```bash
# Count deprecated endpoint calls
grep "deprecated_endpoint_usage" logs/application.log | wc -l

# Find top deprecated endpoints
grep "deprecated_endpoint_usage" logs/application.log | \
    jq -r '.endpoint' | sort | uniq -c | sort -rn
```

---

## 12. Future Enhancements

**Phase 23+ (Planned):**
- GraphQL API (parallel to REST)
- Automated deprecation reports
- Version-specific documentation generator
- Client SDK version compatibility matrix
- Automated migration testing
- Version analytics dashboard
- A/B testing for new API versions
- WebSocket protocol versioning

---

## 13. References

- **Dok 33:** Versioning-Change-Management.md
- **Dok 32:** API-Gateway.md (Phase 21)
- **Phase 21 Docs:** api-gateway-implementation.md
- **DB Migration Strategy:** database-migration-strategy.md
- **CHANGELOG.md:** System version history

---

**Implementation Date:** Phase 22
**Last Updated:** 2025
**Status:** ✅ Production Ready
