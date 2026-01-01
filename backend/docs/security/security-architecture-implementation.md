# Phase 20: Security Architecture & Hardening - Implementation

**LernsystemX Backend**
**Status:** ✅ Implemented
**Compliance:** ISO 27001:2013, DSGVO/GDPR, OWASP Top 10

---

## 1. Overview

Phase 20 implements enterprise-grade security hardening for the LernsystemX backend, based on **Dok 31 (Security Architecture)** and ISO 27001:2013 standards.

### 1.1 Implemented Features

| Feature | Status | Location |
|---------|--------|----------|
| **Security Configuration** | ✅ | `backend/app/config.py` |
| **RBAC/Permissions System** | ✅ | `backend/app/security/permissions.py` |
| **Rate Limiting & Brute-Force Protection** | ✅ | `backend/app/security/rate_limit.py` |
| **Security Headers Middleware** | ✅ | `backend/app/middleware/security_headers.py` |
| **Audit Logging** | ✅ | `backend/app/services/audit_service.py`, `backend/app/database/audit_log_schema.sql` |
| **Sensitive Data Handling Guidelines** | ✅ | `backend/docs/security/sensitive-data-handling.md` |

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
│  - Rate Limiting (IP-based)                                  │
│  - DDoS Protection                                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Flask Application                                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Security Headers Middleware                       │   │
│  │    - X-Frame-Options: DENY                           │   │
│  │    - X-Content-Type-Options: nosniff                 │   │
│  │    - HSTS, CSP, Referrer-Policy                      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 2. Rate Limiting (Flask-Limiter)                     │   │
│  │    - Login: 5/min per IP                             │   │
│  │    - API: 100/min per user                           │   │
│  │    - 2FA: 10/min (sensitive)                         │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 3. Authentication Middleware                         │   │
│  │    - JWT Token Verification                          │   │
│  │    - 2FA Verification                                │   │
│  │    - Brute-Force Protection                          │   │
│  │    - Account Lockout (5 attempts → 15 min lockout)  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 4. RBAC/Permission System                            │   │
│  │    - 9 Roles (user → superadmin)                     │   │
│  │    - 25+ Permissions                                 │   │
│  │    - Decorators: @require_permission()               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 5. Audit Logging                                     │   │
│  │    - All auth events                                 │   │
│  │    - Permission denied events                        │   │
│  │    - Admin actions                                   │   │
│  │    - 365-day retention                               │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  PostgreSQL + Redis                                          │
│  - audit_logs table                                          │
│  - rate limit counters (Redis)                              │
│  - brute-force tracking (Redis)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Components

### 3.1 Security Configuration (`backend/app/config.py`)

Added to `ProductionConfig`:

```python
# Password Policy
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGITS = True
PASSWORD_REQUIRE_SPECIAL = True

# Login Security & Account Lockout
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15
ACCOUNT_LOCKOUT_THRESHOLD = 10

# Rate Limiting
RATE_LIMIT_ENABLED = True
RATE_LIMIT_LOGIN = '5 per minute'
RATE_LIMIT_API = '100 per minute'
RATE_LIMIT_SENSITIVE = '10 per minute'

# Security Headers
SECURITY_HEADERS_ENABLED = True
HSTS_MAX_AGE = 31536000  # 1 year

# Audit Logging
AUDIT_LOG_ENABLED = True
AUDIT_LOG_RETENTION_DAYS = 365
```

**Environment Variables:** See `backend/.env.production.example` (lines 203-231)

---

### 3.2 RBAC/Permissions System (`backend/app/security/permissions.py`)

**Permission Model:**
- Format: `action:resource[:scope]`
- Examples: `admin:users`, `view:analytics:system`, `manage:billing`

**9 Roles:**
1. **user** (Free User) - View own data
2. **premium** - AI Basic/Premium, Create private courses
3. **creator** - AI Pro, Publish courses globally
4. **teacher** - Organization analytics, LiveRoom Pro
5. **school_admin** / **company_admin** - Manage organization, billing, tokens
6. **moderator** - Content moderation
7. **support** - View logs, help users
8. **admin** - Full management (no system config)
9. **superadmin** - All permissions (*)

**Usage:**

```python
from app.security import require_permission, Permissions, require_org_admin

@api_v1.route('/admin/users', methods=['GET'])
@require_permission(Permissions.MANAGE_USERS)
def manage_users():
    # Only admin/superadmin can access
    ...

@api_v1.route('/organisations/<org_id>/settings', methods=['POST'])
@require_org_admin
def update_org_settings(org_id):
    # Only org admin or higher can access
    ...
```

---

### 3.3 Rate Limiting & Brute-Force Protection

**3.3.1 Rate Limiting (`backend/app/security/rate_limit.py`)**

```python
from app.security import login_rate_limit, twofa_rate_limit, api_rate_limit

@api_v1.route('/auth/login', methods=['POST'])
@login_rate_limit()  # 5 per minute per IP
def login():
    ...

@api_v1.route('/auth/2fa/verify', methods=['POST'])
@twofa_rate_limit()  # 10 per minute (sensitive)
def verify_2fa():
    ...
```

**3.3.2 Brute-Force Protection**

```python
from app.security import BruteForceProtection

# Check for lockout before authentication
is_blocked, error_message = BruteForceProtection.check_login_lockout(email, ip)
if is_blocked:
    return jsonify({'error': 'Account locked', 'message': error_message}), 403

# Record failed attempt (increments Redis counter)
BruteForceProtection.record_failed_attempt(email, ip)

# Reset counters on successful login
BruteForceProtection.record_successful_login(email, ip)
```

**Mechanism:**
- Redis keys: `attempts:email:{email}`, `lockout:email:{email}`
- **5 failed attempts** → 15-minute lockout
- Counters expire after lockout period
- Tracks both email-based and IP-based attempts

---

### 3.4 Security Headers Middleware (`backend/app/middleware/security_headers.py`)

**Headers Added:**

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME-sniffing |
| `X-XSS-Protection` | `1; mode=block` | XSS filter (legacy) |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Force HTTPS |
| `Content-Security-Policy` | `default-src 'self'; ...` | Prevent XSS, data injection |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer info |
| `Permissions-Policy` | `geolocation=(), microphone=(), ...` | Disable dangerous features |

**CSP Policy:**
```
default-src 'self';
connect-src 'self' https://frontend-url;
img-src 'self' data: https:;
style-src 'self' 'unsafe-inline';
script-src 'self';
font-src 'self' data:;
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
upgrade-insecure-requests;
```

**Setup:** Auto-configured in `backend/app/__init__.py:setup_security_headers()`

---

### 3.5 Audit Logging

**3.5.1 Database Schema (`backend/app/database/audit_log_schema.sql`)**

```sql
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    user_email VARCHAR(255),
    user_role VARCHAR(50),
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    description TEXT,
    metadata JSONB,
    success BOOLEAN NOT NULL DEFAULT true,
    error_message TEXT,
    retained_until DATE
);
```

**Indexes:** 9 optimized indexes for common queries (user_id, event_type, IP, timestamps)

**Retention:** Automatic cleanup via `cleanup_expired_audit_logs()` function (run daily via Celery)

**3.5.2 Audit Service (`backend/app/services/audit_service.py`)**

```python
from app.services.audit_service import AuditService

# Login success
AuditService.log_login_success(
    user_id=user['user_id'],
    user_email=user['email'],
    user_role=user['role'],
    metadata={'2fa_used': True}
)

# Login failed
AuditService.log_login_failed(
    email=email,
    reason='Invalid credentials',
    metadata={'ip': client_ip}
)

# Permission denied
AuditService.log_permission_denied(
    user_id=user_id,
    user_email=email,
    permission='admin:users',
    resource='/admin/users'
)

# 2FA enabled/disabled
AuditService.log_2fa_enabled(user_id, user_email)
AuditService.log_2fa_disabled(user_id, user_email)

# Account locked
AuditService.log_account_locked(email, reason='Too many failed attempts')
```

**Event Types:**
- Authentication: login, logout, 2fa_enable, 2fa_disable, password_reset
- Authorization: permission_denied, role_change
- Data: create, read, update, delete, export
- Admin: user_created, user_updated, org_created, config_changed
- System: rate_limit_exceeded, account_locked, suspicious_activity

**Automatic Sanitization:**
- Removes passwords, secrets, tokens from metadata
- Sensitive keys: password, secret, token, api_key, credit_card, ssn, two_factor_secret

---

## 4. Integration Points

### 4.1 App Factory (`backend/app/__init__.py`)

```python
def create_app(config_name=None):
    ...
    setup_monitoring(app)
    setup_rate_limiting(app)      # Phase 20
    setup_security_headers(app)   # Phase 20
    return app
```

### 4.2 Auth Endpoints (`backend/app/api/auth.py`)

**Login Endpoint:**
1. Check brute-force lockout
2. Authenticate user
3. Verify 2FA (if enabled)
4. Record failed/successful attempt
5. Log audit event
6. Create JWT tokens

**2FA Endpoints:**
- `/auth/2fa/setup` - Generate TOTP secret, QR code
- `/auth/2fa/verify` - Verify and enable 2FA → Audit log
- `/auth/2fa/disable` - Disable 2FA → Audit log

---

## 5. Deployment Checklist

### 5.1 Database Setup

```bash
# Run audit log schema migration
psql -U lsx_user -d lernsystemx_prod -f backend/app/database/audit_log_schema.sql
```

### 5.2 Environment Variables

Update `.env.production`:

```env
# Security (Phase 20)
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_DIGITS=True
PASSWORD_REQUIRE_SPECIAL=True

MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_MINUTES=15

RATE_LIMIT_ENABLED=True
RATE_LIMIT_LOGIN=5 per minute
RATE_LIMIT_API=100 per minute
RATE_LIMIT_SENSITIVE=10 per minute

SECURITY_HEADERS_ENABLED=True
HSTS_MAX_AGE=31536000

AUDIT_LOG_ENABLED=True
AUDIT_LOG_RETENTION_DAYS=365
```

### 5.3 Celery Task (Daily Audit Log Cleanup)

```python
from celery import Celery
from app.database.connection import execute_query

@celery.task
def cleanup_old_audit_logs():
    """Run daily at 3 AM"""
    result = execute_query("SELECT cleanup_expired_audit_logs()")
    deleted_count = result[0][0] if result else 0
    return f"Deleted {deleted_count} expired audit logs"
```

**Cron:** `0 3 * * *` (daily at 3 AM)

### 5.4 Nginx Configuration

See `backend/docs/deployment/deployment-guide.md` (Phase 20 additions)

---

## 6. Testing

### 6.1 Rate Limiting Test

```bash
# Test login rate limit (should block after 5 attempts)
for i in {1..10}; do
    curl -X POST http://localhost:5000/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"wrong"}' \
        -w "\n%{http_code}\n"
    sleep 1
done

# Expected: 401 (attempts 1-5), 429 (attempts 6-10)
```

### 6.2 Brute-Force Protection Test

```bash
# Trigger account lockout
for i in {1..6}; do
    curl -X POST http://localhost:5000/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"wrong"}' \
        -w "\nAttempt $i: %{http_code}\n"
done

# Expected: Attempt 6 returns 403 "Account locked for 15 minutes"
```

### 6.3 Security Headers Test

```bash
curl -I https://your-domain.com/api/v1/health

# Expected headers:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# Content-Security-Policy: default-src 'self'; ...
```

### 6.4 Audit Log Test

```python
from app.services.audit_service import AuditService

# Trigger audit events
AuditService.log_login_failed("test@example.com", "Invalid credentials")

# Query audit logs
from app.database.connection import fetch_all
logs = fetch_all("SELECT * FROM audit_logs WHERE event_type = 'login_failed' ORDER BY created_at DESC LIMIT 10")
print(logs)
```

---

## 7. Monitoring & Alerts

### 7.1 Metrics to Monitor

- **Failed login rate** (> 50/hour → alert)
- **Account lockouts** (> 10/hour → investigate)
- **Permission denied events** (unexpected spike → investigate)
- **Rate limit exceeded** (track top IPs)
- **Audit log size** (monitor growth, trigger cleanup if needed)

### 7.2 Prometheus Queries

```promql
# Failed logins per minute
rate(audit_logs_total{event_type="login_failed"}[5m])

# Account lockouts
increase(audit_logs_total{event_type="account_locked"}[1h])

# Rate limit hits
rate(http_requests_total{status="429"}[5m])
```

---

## 8. Compliance

### 8.1 ISO 27001:2013
- ✅ **A.9.2** User Access Management (RBAC)
- ✅ **A.9.4** Access Control (Permissions)
- ✅ **A.12.4** Logging & Monitoring (Audit Logs)
- ✅ **A.14.2** Security in Development (Guidelines)
- ✅ **A.18.1** Compliance with Legal Requirements (DSGVO)

### 8.2 DSGVO/GDPR
- ✅ **Art. 5** Data Minimization (Sensitive Data Guidelines)
- ✅ **Art. 17** Right to Erasure (User deletion function)
- ✅ **Art. 25** Data Protection by Design (Security architecture)
- ✅ **Art. 32** Security of Processing (Encryption, Access Control, Audit)

### 8.3 OWASP Top 10 (2021)
- ✅ **A01** Broken Access Control → RBAC/Permissions
- ✅ **A02** Cryptographic Failures → Argon2id, HTTPS, JWT
- ✅ **A03** Injection → Parameterized queries
- ✅ **A04** Insecure Design → Zero-Trust architecture
- ✅ **A05** Security Misconfiguration → Security headers, hardening
- ✅ **A06** Vulnerable Components → Regular updates (requirements.txt)
- ✅ **A07** Identification/Authentication Failures → 2FA, brute-force protection
- ✅ **A09** Security Logging Failures → Comprehensive audit logs

---

## 9. References

- **Dok 31:** Security Architecture (LernsystemX)
- **Dok 19:** Sicherheit & Berechtigungen
- **Dok 01:** Rollenmodell
- **ISO 27001:2013:** Information Security Management
- **DSGVO/GDPR:** General Data Protection Regulation
- **OWASP Top 10:** https://owasp.org/Top10/
- **Flask-Limiter:** https://flask-limiter.readthedocs.io/
- **Argon2:** https://en.wikipedia.org/wiki/Argon2

---

**Implementation Date:** Phase 20
**Last Updated:** 2025
**Status:** ✅ Production Ready
