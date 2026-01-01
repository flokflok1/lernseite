# LernsystemX - Sensitive Data Handling Guidelines

**Phase 20: Security Architecture & Hardening**
**Based on:** Dok 31 (Security Architecture), ISO 27001:2013, DSGVO/GDPR

---

## 1. Overview

This document provides guidelines for handling sensitive data throughout the LernsystemX backend.

**Objectives:**
- Protect user privacy and sensitive information
- Comply with DSGVO/GDPR requirements
- Prevent data leaks via logs, analytics, error messages
- Implement defense-in-depth strategy

---

## 2. Classification of Sensitive Data

### 2.1 Highly Sensitive (Never Log, Never Export Unencrypted)
- **Passwords** (hashed with Argon2id)
- **2FA secrets** (TOTP seeds)
- **JWT secrets & signing keys**
- **API keys & tokens** (Anthropic, OpenAI, Stripe)
- **Payment information** (credit card data, handled by Stripe)
- **Private encryption keys**

### 2.2 Sensitive (Log Only When Required, Redact in Production)
- **Email addresses** (required for audit logs, but redact in public logs)
- **IP addresses** (collect for security, anonymize after retention period)
- **Session IDs / JWT tokens**
- **User-generated content** (may contain PII)
- **Organisation internal data**

### 2.3 Internal Use (Can Be Logged with Restrictions)
- **User IDs** (numeric, non-identifying)
- **Resource IDs** (course_id, module_id, etc.)
- **Metadata** (sanitized, no PII)
- **Aggregated statistics**

---

## 3. Implementation Guidelines

### 3.1 Password Handling

**✅ CORRECT:**
```python
from app.repositories.user_repository import UserRepository

# Hash password before storing
user = UserRepository.create_user(
    email=email,
    password=password,  # Will be hashed with Argon2id internally
    first_name=first_name,
    last_name=last_name
)

# Authenticate without exposing password
user = UserRepository.authenticate(email, password)
```

**❌ INCORRECT:**
```python
# NEVER log passwords
app.logger.info(f"User {email} logged in with password {password}")  # BAD!

# NEVER return passwords in API responses
return jsonify({'user': user, 'password': user['password']})  # BAD!

# NEVER store passwords in plaintext
execute_query("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))  # BAD!
```

---

### 3.2 Audit Logging

**✅ CORRECT:**
```python
from app.services.audit_service import AuditService

# Log security events with sanitized metadata
AuditService.log_login_success(
    user_id=user['user_id'],
    user_email=user['email'],  # OK for audit logs
    user_role=user['role'],
    metadata={'2fa_used': True}  # Sanitized metadata
)

# Failed login - email is OK for security tracking
AuditService.log_login_failed(
    email=email,
    reason='Invalid credentials',
    metadata={'ip': client_ip}
)
```

**❌ INCORRECT:**
```python
# NEVER log passwords or secrets
AuditService.log_event(
    event_type='login',
    metadata={'password': password, '2fa_secret': totp_secret}  # BAD!
)
```

**Automatic Sanitization:**
The `AuditService._sanitize_metadata()` function automatically removes sensitive keys:
- password, passwd, pwd
- secret, token, api_key
- private_key, credit_card, cvv, ssn
- two_factor_secret, totp_secret

---

### 3.3 Error Messages (Production vs Development)

**✅ CORRECT:**
```python
from flask import current_app

try:
    result = some_database_operation()
except Exception as e:
    # Log full error for debugging
    current_app.logger.error(f"Database operation failed: {str(e)}")

    # Return generic error in production
    if current_app.config.get('LSX_ENV') == 'production':
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred. Please try again later.'
        }), 500
    else:
        # Development: return details for debugging
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'details': str(e)
        }), 500
```

**❌ INCORRECT:**
```python
# NEVER expose internal errors in production
return jsonify({
    'error': f'Database connection failed: {connection_string}'  # BAD! Exposes credentials
}), 500

# NEVER expose full stack traces to users
return jsonify({'error': traceback.format_exc()}), 500  # BAD!
```

---

### 3.4 API Response Sanitization

**✅ CORRECT:**
```python
from app.models.user import UserResponse

# Use Pydantic models to control what's returned
user_response = UserResponse(**user)  # Only returns whitelisted fields

return jsonify({
    'success': True,
    'user': user_response.model_dump(exclude={'password_hash', 'two_factor_secret'})
}), 200
```

**❌ INCORRECT:**
```python
# NEVER return raw database rows
user = UserRepository.find_by_id(user_id)
return jsonify(user), 200  # BAD! May include password_hash, secrets, etc.

# NEVER include sensitive fields in responses
return jsonify({
    'user': {
        'email': user['email'],
        'password_hash': user['password_hash'],  # BAD!
        'two_factor_secret': user['two_factor_secret']  # BAD!
    }
}), 200
```

---

### 3.5 Logging Best Practices

**✅ CORRECT:**
```python
# Log with appropriate level and sanitized data
app.logger.info(f"User {user_id} created course {course_id}")
app.logger.warning(f"Failed login attempt for email: {email_domain}")  # Redact email, log domain
app.logger.error(f"Payment processing failed for user {user_id}")

# Use structured logging
app.logger.info("Login successful", extra={
    'user_id': user_id,
    'role': role,
    'ip': client_ip,
    'event': 'login_success'
})
```

**❌ INCORRECT:**
```python
# NEVER log sensitive data
app.logger.info(f"Login: {email} with password {password}")  # BAD!
app.logger.debug(f"JWT token: {access_token}")  # BAD!
app.logger.info(f"Stripe secret key: {stripe_secret_key}")  # BAD!

# Avoid logging full user objects (may contain sensitive fields)
app.logger.info(f"User logged in: {user}")  # RISKY!
```

---

### 3.6 Analytics & Metrics

**✅ CORRECT:**
```python
# Collect aggregated, anonymized metrics
from app.monitoring import track_metric

track_metric('login_attempts', labels={'status': 'success', 'role': user_role})
track_metric('api_requests', labels={'endpoint': '/api/v1/courses', 'method': 'GET'})

# Store only required fields for analytics
analytics_event = {
    'user_id': user_id,  # OK - numeric ID
    'event_type': 'course_completed',
    'course_id': course_id,
    'timestamp': datetime.utcnow()
    # NO email, NO IP, NO user agent
}
```

**❌ INCORRECT:**
```python
# NEVER include PII in analytics
analytics_event = {
    'email': user_email,  # BAD!
    'ip_address': client_ip,  # BAD! (unless explicitly for security)
    'full_name': user_name,  # BAD!
    'credit_card': '****1234'  # BAD! Even redacted
}
```

---

### 3.7 Database Queries (Preventing Injection)

**✅ CORRECT:**
```python
from app.database.connection import execute_query, fetch_one

# Use parameterized queries (prevents SQL injection)
user = fetch_one(
    "SELECT * FROM users WHERE email = %s",
    (email,)
)

# Multi-parameter query
results = fetch_all(
    "SELECT * FROM courses WHERE category_id = %s AND level = %s",
    (category_id, level)
)
```

**❌ INCORRECT:**
```python
# NEVER use string interpolation for SQL (SQL injection risk!)
user = fetch_one(f"SELECT * FROM users WHERE email = '{email}'")  # BAD!

# NEVER trust user input directly
query = f"SELECT * FROM {table_name} WHERE id = {user_id}"  # BAD!
```

---

### 3.8 Environment Variables & Configuration

**✅ CORRECT:**
```python
import os
from app.config import config

# Load secrets from environment
SECRET_KEY = os.getenv('SECRET_KEY')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# NEVER commit .env.production to git
# Use .env.production.example as template
```

**❌ INCORRECT:**
```python
# NEVER hardcode secrets
SECRET_KEY = 'my-super-secret-key-12345'  # BAD!
STRIPE_SECRET_KEY = 'sk_live_abc123def456'  # BAD!

# NEVER log secrets
app.logger.debug(f"Using API key: {ANTHROPIC_API_KEY}")  # BAD!
```

---

## 4. Data Retention & Deletion

### 4.1 Audit Logs
- **Retention:** 365 days (configurable via `AUDIT_LOG_RETENTION_DAYS`)
- **Cleanup:** Automated via `cleanup_expired_audit_logs()` function (run daily via Celery)

### 4.2 User Data (DSGVO/GDPR Right to be Forgotten)
```python
def delete_user_data(user_id: int):
    """
    Delete or anonymize user data per DSGVO Art. 17.

    Steps:
    1. Delete PII (email, name, etc.)
    2. Anonymize audit logs (replace user_email with 'deleted-user@example.com')
    3. Retain aggregated analytics (without PII)
    4. Keep audit logs for legal compliance (365 days)
    """
    # Delete user account
    execute_query("DELETE FROM users WHERE user_id = %s", (user_id,))

    # Anonymize audit logs (keep for compliance, but remove PII)
    execute_query(
        "UPDATE audit_logs SET user_email = %s WHERE user_id = %s",
        ('deleted-user@example.com', user_id)
    )
```

### 4.3 IP Address Anonymization
After security retention period (90 days), anonymize IP addresses:
```sql
-- Anonymize IPs older than 90 days
UPDATE audit_logs
SET ip_address = host(set_masklen(ip_address, 24))
WHERE created_at < NOW() - INTERVAL '90 days'
  AND ip_address IS NOT NULL;
```

---

## 5. Security Checklist for Developers

Before deploying code, verify:

- [ ] No passwords, secrets, or tokens in logs
- [ ] No sensitive data in error messages (production)
- [ ] All SQL queries use parameterized statements
- [ ] API responses use Pydantic models (whitelist fields)
- [ ] Audit logs use `AuditService._sanitize_metadata()`
- [ ] Analytics do not contain PII
- [ ] Environment variables used for secrets
- [ ] `.env.production` not committed to git
- [ ] Error handlers return generic messages in production
- [ ] Data retention policies implemented

---

## 6. Incident Response

If sensitive data is accidentally logged or exposed:

1. **Immediate:** Rotate affected secrets (API keys, JWT secrets)
2. **Cleanup:** Purge logs containing sensitive data
3. **Notify:** Inform affected users (if PII exposed)
4. **Document:** Create incident report in audit logs
5. **Prevent:** Update code to prevent recurrence

---

## 7. References

- **Dok 31:** Security Architecture (LernsystemX)
- **ISO 27001:2013:** A.9 Access Control, A.12 Operations Security
- **DSGVO/GDPR:** Art. 5 (Data Minimization), Art. 17 (Right to Erasure), Art. 32 (Security)
- **OWASP Top 10:** A01 (Broken Access Control), A03 (Injection), A04 (Insecure Design)

---

**Last Updated:** Phase 20 - Security Architecture & Hardening
**Compliance:** ISO 27001:2013, DSGVO/GDPR, OWASP Top 10
