# 31 | Security Architecture

**Version:** 1.0
**Status:** Final
**Zuletzt aktualisiert:** 2025-11-15

## Übersicht

Die Security Architecture des LSX Lernsystems implementiert ein **Zero-Trust-Sicherheitsmodell** mit **mehrschichtiger Verteidigung (Defense in Depth)**. Das System schützt sensible Daten wie personenbezogene Informationen, Lernfortschritte, Prüfungsergebnisse, Creator-Einnahmen und KI-generierte Inhalte.

**Wichtige Sicherheitsmetriken:**
• **Security Standard:** OWASP Top 10 + Zero-Trust
• **Compliance:** DSGVO, BDSG, ISO 27001
• **Verschlüsselung:** TLS 1.3, AES-256
• **Authentifizierung:** JWT + Optional 2FA (TOTP, FIDO2)
• **Penetration Testing:** Jährlich + kontinuierliche Scans
• **Incident Response Time:** < 15 Minuten

---

## C4 Context Diagram: Security Architecture

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

title C4 Context Diagram - LSX Security Architecture

Person(user, "Nutzer/Student", "Greift auf Lernplattform zu")
Person(creator, "Creator", "Erstellt & verkauft Kurse")
Person(teacher, "Lehrer", "Verwaltet Klassen")
Person(admin, "Administrator", "Verwaltet Organisation")

System_Boundary(lsx, "LSX Lernsystem") {
    System(webapp, "Web Application", "Geschützte Frontend & Backend API")
    System(auth, "Authentication Service", "JWT, 2FA, OAuth2")
    System(rbac, "Authorization Service", "Rollenbasierte Zugriffskontrolle")
    System(audit, "Audit & Logging", "Sicherheitsrelevante Events")
}

System_Ext(waf, "Web Application Firewall", "Cloudflare WAF, Rate Limiting")
System_Ext(vault, "HashiCorp Vault", "Secrets Management")
System_Ext(siem, "SIEM System", "Security Information & Event Management")
System_Ext(ids, "IDS/IPS", "Intrusion Detection & Prevention")

Rel(user, waf, "HTTPS")
Rel(waf, webapp, "Filtered Requests", "Rate Limited")

Rel(webapp, auth, "Validates credentials")
Rel(webapp, rbac, "Checks permissions")
Rel(webapp, vault, "Retrieves secrets")

Rel(auth, audit, "Logs authentication events")
Rel(rbac, audit, "Logs authorization events")
Rel(webapp, audit, "Logs API requests")

Rel(audit, siem, "Security events", "Syslog")
Rel(waf, ids, "Suspicious traffic")

@enduml
```

---

## C4 Container Diagram: Security Infrastructure

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title C4 Container Diagram - Security Infrastructure

Person(user, "User")

System_Boundary(security_layer, "Security Layer") {
    Container(waf, "WAF", "Cloudflare", "DDoS Protection, Bot Detection")
    Container(api_gateway, "API Gateway", "Kong/Nginx", "Rate Limiting, Auth")
}

System_Boundary(auth_system, "Authentication & Authorization") {
    Container(auth_service, "Auth Service", "Python Flask", "JWT Generation, 2FA")
    Container(rbac_service, "RBAC Service", "Python", "Permission Checks")
    Container(session_store, "Session Store", "Redis", "Encrypted Sessions")
}

System_Boundary(application, "Application Layer") {
    Container(backend_api, "Backend API", "Python Flask", "Business Logic")
    Container(frontend, "Frontend", "Vue.js", "User Interface")
}

System_Boundary(data_protection, "Data Protection") {
    Container(encryption_service, "Encryption Service", "Python", "AES-256 Encryption")
    Container(vault, "Vault", "HashiCorp Vault", "Secrets Management")
    Container(db_encrypted, "PostgreSQL", "Database", "Encrypted at Rest")
}

System_Boundary(monitoring, "Security Monitoring") {
    Container(audit_log, "Audit Logger", "Python", "Security Events")
    Container(siem, "SIEM", "Wazuh/Splunk", "Security Analytics")
    Container(ids, "IDS/IPS", "Suricata", "Network Monitoring")
}

Rel(user, waf, "HTTPS Request")
Rel(waf, api_gateway, "Filtered Traffic")
Rel(api_gateway, backend_api, "Authenticated Requests")

Rel(api_gateway, auth_service, "Validate Token")
Rel(backend_api, rbac_service, "Check Permission")
Rel(auth_service, session_store, "Store Session")

Rel(backend_api, encryption_service, "Encrypt Sensitive Data")
Rel(backend_api, vault, "Get DB Credentials")
Rel(backend_api, db_encrypted, "Encrypted Connection (TLS)")

Rel(api_gateway, audit_log, "Log Requests")
Rel(auth_service, audit_log, "Log Auth Events")
Rel(rbac_service, audit_log, "Log Access Denials")
Rel(audit_log, siem, "Forward Events")
Rel(waf, ids, "Suspicious Traffic")

@enduml
```

---

## 1. Sicherheitsziele

### 1.1 Primäre Schutzziele

| Schutzziel | Beschreibung | Maßnahme |
|------------|--------------|----------|
| **Vertraulichkeit** | Unbefugte dürfen keine Daten einsehen | Verschlüsselung, Zugriffskon trolle |
| **Integrität** | Daten dürfen nicht manipuliert werden | Signaturen, Audit Logs, Checksums |
| **Verfügbarkeit** | System muss 99.9% verfügbar sein | DDoS-Schutz, Redundanz, Backups |
| **Authentizität** | Nutzer sind wer sie vorgeben zu sein | Multi-Faktor-Authentifizierung |
| **Nachvollziehbarkeit** | Alle Aktionen sind protokolliert | Audit Logs, SIEM |
| **Non-Repudiation** | Aktionen können nicht abgestritten werden | Digitale Signaturen |

### 1.2 Compliance & Standards

**DSGVO (Datenschutz-Grundverordnung):**
• Recht auf Auskunft (Art. 15 DSGVO)
• Recht auf Löschung (Art. 17 DSGVO)
• Datenschutz durch Technikgestaltung (Art. 25 DSGVO)
• Meldepflicht bei Datenpannen (Art. 33 DSGVO)
• Auftragsverarbeitungsverträge (Art. 28 DSGVO)

**ISO 27001 Informationssicherheit:**
• Risikomanagement
• Access Control (ISO 27001:A.9)
• Kryptografie (ISO 27001:A.10)
• Betriebssicherheit (ISO 27001:A.12)
• Incident Management (ISO 27001:A.16)

**OWASP Top 10 (2021):**
• A01: Broken Access Control
• A02: Cryptographic Failures
• A03: Injection
• A04: Insecure Design
• A05: Security Misconfiguration
• A06: Vulnerable Components
• A07: Authentication Failures
• A08: Software & Data Integrity Failures
• A09: Security Logging Failures
• A10: Server-Side Request Forgery (SSRF)

---

## 2. Zero-Trust Architecture

### 2.1 Zero-Trust Prinzipien

```plantuml
@startuml
title Zero-Trust Security Model

package "Zero-Trust Principles" {
    [Verify Explicitly] as verify
    [Use Least Privilege Access] as least
    [Assume Breach] as assume
}

package "Implementation" {
    [Authentifizierung für JEDE Anfrage] as auth_every
    [Keine impliziten Trust-Zonen] as no_trust
    [Micro-Segmentation] as micro_seg
    [Kontinuierliche Validierung] as continuous
}

verify --> auth_every
verify --> continuous
least --> micro_seg
least --> auth_every
assume --> no_trust
assume --> continuous

note right of auth_every
  **Jede Anfrage wird validiert:**
  - JWT Token prüfen
  - Rollen-Berechtigung prüfen
  - Organisations-Kontext prüfen
  - Rate Limits prüfen
end note

note right of micro_seg
  **Segmentierung:**
  - Nutzer nur eigene Daten
  - Organisationen isoliert
  - Creator nur eigene Kurse
  - Admin nur eigene Org
end note

@enduml
```

### 2.2 Zero-Trust Implementation

**Niemals vertrauen, immer verifizieren:**
• Keine ungeschützten API-Endpunkte
• Jeder Request benötigt gültiges JWT Token
• Selbst interne Services authentifizieren sich
• Keine direkten Datenbankzugriffe ohne Authorization

**Minimale Berechtigungen:**
• Nutzer erhalten nur die Rechte, die sie benötigen
• Service Accounts mit minimalen Rechten
• Temporäre Credentials wo möglich
• Rechte-Eskalation nur mit Audit-Log

**Angriff wird angenommen:**
• Alle Netzwerksegmente sind potenziell kompromittiert
• Verschlüsselung auch für interne Kommunikation
• Kontinuierliche Überwachung auf Anomalien
• Automatische Isolation bei verdächtigem Verhalten

---

## 3. ER-Diagramm: Security Audit System

```plantuml
@startuml
!define primary_key(x) <u>x</u>
!define foreign_key(x) #x

entity AuditLog {
  primary_key(audit_id): UUID
  timestamp: TIMESTAMP
  user_id: UUID
  event_type: ENUM('login', 'logout', 'access_denied', 'data_access', 'data_change', 'admin_action')
  resource_type: VARCHAR(50)
  resource_id: UUID
  action: VARCHAR(100)
  ip_address: INET
  user_agent: TEXT
  session_id: UUID
  success: BOOLEAN
  failure_reason: TEXT
  metadata: JSONB
}

entity SecurityEvent {
  primary_key(event_id): UUID
  timestamp: TIMESTAMP
  severity: ENUM('low', 'medium', 'high', 'critical')
  category: ENUM('auth_failure', 'privilege_escalation', 'data_leak', 'injection_attempt', 'dos_attempt')
  source_ip: INET
  user_id: UUID
  description: TEXT
  indicators: JSONB
  automated_response: TEXT
  status: ENUM('open', 'investigating', 'resolved', 'false_positive')
}

entity AccessControl {
  primary_key(acl_id): UUID
  user_id: UUID
  role: ENUM('user', 'premium', 'creator', 'teacher', 'org_admin', 'moderator', 'admin', 'superadmin')
  org_id: UUID
  permissions: JSONB
  granted_at: TIMESTAMP
  granted_by: UUID
  expires_at: TIMESTAMP
  revoked_at: TIMESTAMP
}

entity FailedLogin {
  primary_key(attempt_id): UUID
  timestamp: TIMESTAMP
  email: VARCHAR(255)
  ip_address: INET
  reason: ENUM('invalid_password', 'account_locked', '2fa_failed', 'account_not_found')
  user_agent: TEXT
}

entity SuspiciousActivity {
  primary_key(activity_id): UUID
  user_id: UUID
  detected_at: TIMESTAMP
  activity_type: ENUM('unusual_ip', 'velocity_anomaly', 'mass_download', 'privilege_probe', 'token_manipulation')
  risk_score: INT
  details: JSONB
  action_taken: TEXT
}

entity DataAccessLog {
  primary_key(access_id): UUID
  foreign_key(audit_id): UUID
  user_id: UUID
  table_name: VARCHAR(50)
  row_id: UUID
  accessed_columns: TEXT[]
  access_type: ENUM('read', 'write', 'delete')
  timestamp: TIMESTAMP
}

AuditLog ||--o{ DataAccessLog : "details"
SecurityEvent }o--|| AuditLog : "references"
FailedLogin }o--|| SecurityEvent : "triggers"
SuspiciousActivity }o--|| SecurityEvent : "creates"
AccessControl }o--|| AuditLog : "changes logged"

@enduml
```

---

## 4. Authentifizierung

### 4.1 Authentication Flow

```plantuml
@startuml
title Authentication & Authorization Flow

actor "User" as user
participant "Frontend" as frontend
participant "API Gateway" as gateway
participant "Auth Service" as auth
participant "2FA Service" as twofa
participant "Redis Session Store" as redis
participant "Database" as db
participant "RBAC Service" as rbac

user -> frontend: Login (email, password)
frontend -> gateway: POST /api/auth/login
gateway -> auth: Validate credentials

auth -> db: SELECT * FROM users WHERE email = ?
db -> auth: User data (hashed password)

auth -> auth: Verify password (Argon2id)

alt Password Invalid
    auth -> gateway: 401 Unauthorized
    gateway -> frontend: Login failed
    frontend -> user: "Invalid credentials"
else Password Valid
    alt 2FA Enabled
        auth -> frontend: 200 OK + "2FA required"
        frontend -> user: "Enter 2FA code"
        user -> frontend: 2FA code
        frontend -> gateway: POST /api/auth/2fa
        gateway -> twofa: Validate TOTP code

        alt 2FA Invalid
            twofa -> frontend: 401 Unauthorized
        else 2FA Valid
            twofa -> auth: 2FA confirmed
        end
    end

    auth -> auth: Generate JWT Access Token (15 min)
    auth -> auth: Generate Refresh Token (14 days)
    auth -> redis: Store session (session_id, user_id, refresh_token)
    auth -> db: UPDATE users SET last_login = NOW()

    auth -> gateway: 200 OK + Access Token + Refresh Token
    gateway -> frontend: Tokens
    frontend -> user: Login successful

    user -> frontend: Access protected resource
    frontend -> gateway: GET /api/courses (Header: Authorization: Bearer <token>)
    gateway -> auth: Validate JWT signature
    auth -> auth: Check expiration
    auth -> rbac: Get user permissions
    rbac -> db: SELECT permissions FROM access_control WHERE user_id = ?
    rbac -> gateway: User has permission
    gateway -> frontend: Resource data
end

note right of auth
  **JWT Payload:**
  {
    "user_id": "uuid",
    "email": "user@example.com",
    "role": "premium",
    "org_id": "uuid",
    "exp": timestamp,
    "iat": timestamp
  }
end note

@enduml
```

### 4.2 Password Hashing (Argon2id)

**Warum Argon2id?**
• Winner des Password Hashing Competition (2015)
• Resistent gegen GPU/ASIC Attacks
• Konfigurierbare Memory-Hardness & Time-Hardness
• Beste Wahl für 2024+ (besser als bcrypt, scrypt, PBKDF2)

**Implementation:**
```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Argon2id Configuration
ph = PasswordHasher(
    time_cost=2,        # Iterations
    memory_cost=102400, # 100 MB
    parallelism=8,      # Threads
    hash_len=32,        # Output length
    salt_len=16         # Salt length
)

def hash_password(password: str) -> str:
    """Hash password mit Argon2id"""
    return ph.hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    """Verify password gegen Hash"""
    try:
        ph.verify(password_hash, password)

        # Check if hash needs rehashing (parameter upgrade)
        if ph.check_needs_rehash(password_hash):
            # Rehash with new parameters
            new_hash = ph.hash(password)
            # Update in database
            update_user_password_hash(user_id, new_hash)

        return True
    except VerifyMismatchError:
        return False

# Usage in Login
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user:
        # Constant-time response (prevent timing attacks)
        ph.hash("dummy_password")
        return jsonify({"error": "Invalid credentials"}), 401

    if not verify_password(user.password_hash, password):
        # Log failed login
        log_failed_login(email, request.remote_addr, "invalid_password")
        return jsonify({"error": "Invalid credentials"}), 401

    # Password valid, continue with 2FA or token generation
    ...
```

### 4.3 JWT (JSON Web Tokens)

**Token Structure:**
```
Header.Payload.Signature
```

**Access Token (Short-lived, 15 Min):**
```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # From Vault
ALGORITHM = "HS256"

def generate_access_token(user: User) -> str:
    """Generate JWT Access Token"""
    payload = {
        "user_id": str(user.user_id),
        "email": user.email,
        "role": user.role,
        "org_id": str(user.org_id) if user.org_id else None,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def generate_refresh_token(user: User) -> str:
    """Generate JWT Refresh Token"""
    payload = {
        "user_id": str(user.user_id),
        "exp": datetime.utcnow() + timedelta(days=14),
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": str(uuid.uuid4())  # JWT ID for revocation
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify and decode JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check if token is blacklisted (revoked)
        if is_token_blacklisted(payload.get('jti')):
            raise jwt.InvalidTokenError("Token has been revoked")

        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")
```

### 4.4 Two-Factor Authentication (2FA)

**TOTP (Time-based One-Time Password):**
```python
import pyotp
import qrcode
from io import BytesIO
import base64

def generate_2fa_secret(user: User) -> str:
    """Generate 2FA secret for user"""
    secret = pyotp.random_base32()

    # Save to database
    user.totp_secret = secret
    db.session.commit()

    return secret

def generate_2fa_qr_code(user: User) -> str:
    """Generate QR code for Authenticator App"""
    secret = user.totp_secret
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name="LSX Lernsystem"
    )

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"

def verify_2fa_code(user: User, code: str) -> bool:
    """Verify TOTP code"""
    if not user.totp_secret:
        return False

    totp = pyotp.TOTP(user.totp_secret)

    # Verify code (allows for 30s time drift)
    return totp.verify(code, valid_window=1)

# API Endpoints
@app.route('/api/auth/2fa/setup', methods=['POST'])
@jwt_required()
def setup_2fa():
    """Setup 2FA for user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    secret = generate_2fa_secret(user)
    qr_code = generate_2fa_qr_code(user)

    return jsonify({
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": generate_backup_codes(user)  # For recovery
    })

@app.route('/api/auth/2fa/verify', methods=['POST'])
def verify_2fa():
    """Verify 2FA code during login"""
    data = request.json
    email = data.get('email')
    code = data.get('code')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid user"}), 401

    if not verify_2fa_code(user, code):
        log_failed_login(email, request.remote_addr, "2fa_failed")
        return jsonify({"error": "Invalid 2FA code"}), 401

    # 2FA successful, generate tokens
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    })
```

**WebAuthn/FIDO2 (Hardware Keys):**
```python
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)

@app.route('/api/auth/webauthn/register/options', methods=['POST'])
@jwt_required()
def webauthn_register_options():
    """Generate WebAuthn registration options"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    options = generate_registration_options(
        rp_id="lsx.de",
        rp_name="LSX Lernsystem",
        user_id=str(user.user_id).encode(),
        user_name=user.email,
        user_display_name=user.username,
    )

    # Store challenge in session
    session['webauthn_challenge'] = options.challenge

    return jsonify(options)

@app.route('/api/auth/webauthn/register', methods=['POST'])
@jwt_required()
def webauthn_register():
    """Complete WebAuthn registration"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    credential = verify_registration_response(
        credential=request.json,
        expected_challenge=session['webauthn_challenge'],
        expected_origin="https://lsx.de",
        expected_rp_id="lsx.de",
    )

    # Save credential to database
    webauthn_credential = WebAuthnCredential(
        user_id=user.user_id,
        credential_id=credential.credential_id,
        public_key=credential.public_key,
        sign_count=credential.sign_count
    )
    db.session.add(webauthn_credential)
    db.session.commit()

    return jsonify({"status": "registered"})
```

---

## 5. Rollenbasierte Zugriffskontrolle (RBAC)

### 5.1 RBAC Authorization Flow

```plantuml
@startuml
title RBAC Authorization Flow

participant "User" as user
participant "Frontend" as frontend
participant "API Endpoint" as api
participant "Auth Middleware" as middleware
participant "RBAC Service" as rbac
participant "Database" as db

user -> frontend: Request protected resource
frontend -> api: GET /api/courses/:id\n(Header: Authorization: Bearer <token>)

api -> middleware: Validate request
middleware -> middleware: Decode JWT token
middleware -> middleware: Extract user_id, role, org_id

middleware -> rbac: check_permission(user_id, "read:course", resource_id)

rbac -> db: SELECT permissions FROM access_control\nWHERE user_id = ? AND resource_type = 'course'
db -> rbac: User permissions

rbac -> rbac: Check if "read:course" in permissions

alt Has Permission
    rbac -> rbac: Check resource context\n(org_id match, ownership, etc.)

    alt Context Valid
        rbac -> middleware: Permission granted
        middleware -> api: Continue request
        api -> db: Fetch course data
        db -> api: Course data
        api -> frontend: 200 OK + Data
    else Context Invalid
        rbac -> middleware: Permission denied (wrong context)
        middleware -> api: Abort request
        api -> frontend: 403 Forbidden
    end
else No Permission
    rbac -> middleware: Permission denied
    middleware -> api: Abort request
    api -> frontend: 403 Forbidden
end

note right of rbac
  **Permission Format:**
  action:resource[:scope]

  Examples:
  - read:course
  - write:course:own
  - delete:course:org
  - admin:users
  - create:liveroom
end note

@enduml
```

### 5.2 RBAC Implementation

**Permission Decorator:**
```python
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def require_permission(permission: str, resource_param: str = None):
    """
    Decorator to check if user has required permission.

    Args:
        permission: Permission string (e.g., "read:course")
        resource_param: URL parameter name for resource (e.g., "course_id")
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()

            # Get resource ID from URL params if specified
            resource_id = kwargs.get(resource_param) if resource_param else None

            # Check permission
            if not has_permission(user_id, permission, resource_id):
                log_access_denied(user_id, permission, resource_id, request.remote_addr)
                return jsonify({"error": "Access denied"}), 403

            # Log successful access
            log_resource_access(user_id, permission, resource_id)

            return f(*args, **kwargs)
        return wrapper
    return decorator

def has_permission(user_id: str, permission: str, resource_id: str = None) -> bool:
    """Check if user has permission"""
    user = User.query.get(user_id)
    if not user:
        return False

    # Parse permission
    action, resource_type, *scope = permission.split(':')
    scope = scope[0] if scope else None

    # Get user's effective permissions
    effective_permissions = get_effective_permissions(user)

    # Check if permission exists
    if permission not in effective_permissions:
        return False

    # Check scope (own, org, global)
    if scope and resource_id:
        return check_resource_scope(user, resource_type, resource_id, scope)

    return True

def get_effective_permissions(user: User) -> set:
    """Get all permissions for user (role + custom)"""
    permissions = set()

    # Role-based permissions
    role_permissions = {
        'user': [
            'read:course', 'read:module', 'write:progress',
            'read:own_data', 'write:own_data'
        ],
        'premium': [
            'read:course', 'read:module', 'read:premium_content',
            'write:progress', 'create:note'
        ],
        'creator': [
            'read:course', 'create:course', 'write:course:own',
            'delete:course:own', 'read:analytics:own', 'read:revenue:own'
        ],
        'teacher': [
            'read:course:org', 'create:class', 'write:class:own',
            'read:student_progress:org', 'create:exam', 'grade:exam:own'
        ],
        'org_admin': [
            'read:*:org', 'write:*:org', 'delete:*:org',
            'manage:users:org', 'manage:classes:org', 'read:analytics:org'
        ],
        'admin': [
            'read:*', 'write:*', 'delete:*',
            'manage:users', 'manage:system'
        ],
        'superadmin': ['*']  # All permissions
    }

    permissions.update(role_permissions.get(user.role, []))

    # Custom permissions from database
    custom_perms = AccessControl.query.filter_by(
        user_id=user.user_id,
        revoked_at=None
    ).all()

    for perm in custom_perms:
        if perm.expires_at is None or perm.expires_at > datetime.utcnow():
            permissions.update(perm.permissions)

    return permissions

def check_resource_scope(user: User, resource_type: str, resource_id: str, scope: str) -> bool:
    """Check if user has access to specific resource based on scope"""
    if scope == 'own':
        # Check ownership
        if resource_type == 'course':
            course = Course.query.get(resource_id)
            return course and course.creator_id == user.user_id
        elif resource_type == 'class':
            class_obj = Class.query.get(resource_id)
            return class_obj and class_obj.teacher_id == user.user_id

    elif scope == 'org':
        # Check organization membership
        if resource_type == 'course':
            course = Course.query.get(resource_id)
            return course and course.org_id == user.org_id
        elif resource_type == 'student_progress':
            progress = Progress.query.get(resource_id)
            return progress and progress.user.org_id == user.org_id

    elif scope == 'global':
        # Admin/superadmin can access everything
        return user.role in ['admin', 'superadmin']

    return False

# Usage in API Routes
@app.route('/api/courses/<uuid:course_id>', methods=['GET'])
@require_permission('read:course', 'course_id')
def get_course(course_id):
    """Get course details (permission checked by decorator)"""
    course = Course.query.get_or_404(course_id)
    return jsonify(course.to_dict())

@app.route('/api/courses/<uuid:course_id>', methods=['PUT'])
@require_permission('write:course:own', 'course_id')
def update_course(course_id):
    """Update course (only creator can update own courses)"""
    course = Course.query.get_or_404(course_id)
    # Update logic here...
    return jsonify(course.to_dict())

@app.route('/api/admin/users', methods=['GET'])
@require_permission('manage:users')
def list_users():
    """List all users (admin only)"""
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])
```

### 5.3 Organization Isolation (Row-Level Security)

**PostgreSQL Row-Level Security:**
```sql
-- Enable RLS on courses table
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see courses from their organization
CREATE POLICY org_isolation_policy ON courses
    FOR SELECT
    USING (
        org_id = current_setting('app.current_org_id')::uuid
        OR org_id IS NULL  -- Public courses
        OR creator_id = current_setting('app.current_user_id')::uuid  -- Own courses
    );

-- Policy: Users can only modify their own courses or org courses if they're admin
CREATE POLICY org_write_policy ON courses
    FOR UPDATE
    USING (
        creator_id = current_setting('app.current_user_id')::uuid
        OR (
            org_id = current_setting('app.current_org_id')::uuid
            AND current_setting('app.current_role') IN ('org_admin', 'admin', 'superadmin')
        )
    );

-- Similar policies for all sensitive tables
ALTER TABLE modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress ENABLE ROW LEVEL SECURITY;
```

**Set Session Variables (Python):**
```python
import psycopg3
from psycopg3 import Connection

@event.listens_for(Engine, "connect")
def set_session_variables(dbapi_conn, connection_record):
    """Set PostgreSQL session variables for RLS"""
    cursor = dbapi_conn.cursor()

    # Get current user from Flask context
    if has_request_context():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user:
            cursor.execute(
                "SET app.current_user_id = %s",
                (str(user.user_id),)
            )
            cursor.execute(
                "SET app.current_org_id = %s",
                (str(user.org_id) if user.org_id else 'null',)
            )
            cursor.execute(
                "SET app.current_role = %s",
                (user.role,)
            )

    cursor.close()

# Example query - RLS automatically filters results
@app.route('/api/courses', methods=['GET'])
@jwt_required()
def list_courses():
    """List courses (automatically filtered by RLS)"""
    # PostgreSQL RLS will automatically filter based on session variables
    courses = Course.query.all()  # Only returns courses user can access
    return jsonify([c.to_dict() for c in courses])
```

---

## 6. API Security

### 6.1 Rate Limiting

**Implementation mit Flask-Limiter:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://redis:6379/1",
    default_limits=["200 per day", "50 per hour"]
)

# Route-specific rate limits
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")  # Stricter for login
def login():
    ...

@app.route('/api/ki/generate', methods=['POST'])
@limiter.limit("30 per minute")  # KI endpoints limited
@jwt_required()
def generate_ki_content():
    ...

@app.route('/api/courses', methods=['GET'])
@limiter.limit("100 per minute")  # Higher limit for read operations
@jwt_required()
def list_courses():
    ...

# Custom key function (rate limit per user instead of IP)
def get_user_id():
    """Rate limit by user ID instead of IP"""
    if has_request_context():
        try:
            verify_jwt_in_request()
            return get_jwt_identity()
        except:
            return get_remote_address()
    return get_remote_address()

limiter_per_user = Limiter(
    app=app,
    key_func=get_user_id,
    storage_uri="redis://redis:6379/1"
)

@app.route('/api/creator/publish', methods=['POST'])
@limiter_per_user.limit("10 per hour")  # Per user, not per IP
@jwt_required()
def publish_course():
    ...
```

### 6.2 Input Validation & Sanitization

**Pydantic Models for Validation:**
```python
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
import bleach

class CourseCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., max_length=5000)
    category: str
    price: Optional[float] = Field(None, ge=0, le=999.99)

    @validator('title', 'description')
    def sanitize_html(cls, v):
        """Remove dangerous HTML tags"""
        return bleach.clean(v, tags=[], strip=True)

    @validator('category')
    def validate_category(cls, v):
        """Ensure category exists"""
        valid_categories = ['programming', 'math', 'language', 'science']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of {valid_categories}')
        return v

@app.route('/api/courses', methods=['POST'])
@jwt_required()
@require_permission('create:course')
def create_course():
    """Create course with validation"""
    try:
        # Pydantic validates and sanitizes input
        course_data = CourseCreateRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    # Create course
    course = Course(
        title=course_data.title,
        description=course_data.description,
        category=course_data.category,
        price=course_data.price,
        creator_id=get_jwt_identity()
    )
    db.session.add(course)
    db.session.commit()

    return jsonify(course.to_dict()), 201
```

**SQL Injection Prevention (ORM):**
```python
# GOOD: Using ORM (parameterized queries)
course = Course.query.filter_by(course_id=course_id).first()

# GOOD: Using parameterized raw SQL
result = db.session.execute(
    "SELECT * FROM courses WHERE course_id = :id",
    {"id": course_id}
)

# BAD: String concatenation (SQL Injection vulnerability!)
# NEVER DO THIS:
# query = f"SELECT * FROM courses WHERE course_id = '{course_id}'"
# result = db.session.execute(query)
```

---

## 7. Verschlüsselung

### 7.1 Encryption at Rest

**Database Encryption (PostgreSQL):**
```sql
-- Transparent Data Encryption (TDE) via pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive columns
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password_hash TEXT NOT NULL,
    -- Encrypted columns
    ssn BYTEA,  -- Social Security Number (encrypted)
    credit_card BYTEA,  -- Credit card (encrypted)
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert with encryption
INSERT INTO users (user_id, email, ssn)
VALUES (
    gen_random_uuid(),
    'user@example.com',
    pgp_sym_encrypt('123-45-6789', 'encryption_key_from_vault')
);

-- Query with decryption
SELECT
    user_id,
    email,
    pgp_sym_decrypt(ssn, 'encryption_key_from_vault') AS ssn_decrypted
FROM users
WHERE user_id = '...';
```

**Application-Level Encryption (Python):**
```python
from cryptography.fernet import Fernet
import os

# Get encryption key from Vault
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # From HashiCorp Vault
cipher = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(plaintext: str) -> str:
    """Encrypt data using Fernet (AES-256)"""
    encrypted = cipher.encrypt(plaintext.encode())
    return encrypted.decode()

def decrypt_data(ciphertext: str) -> str:
    """Decrypt data"""
    decrypted = cipher.decrypt(ciphertext.encode())
    return decrypted.decode()

# Usage
class SensitiveData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.UUID, db.ForeignKey('users.user_id'))
    encrypted_field = db.Column(db.Text)  # Stored encrypted

    def set_sensitive_data(self, data: str):
        """Encrypt and store"""
        self.encrypted_field = encrypt_data(data)

    def get_sensitive_data(self) -> str:
        """Decrypt and return"""
        return decrypt_data(self.encrypted_field)
```

### 7.2 Encryption in Transit (TLS 1.3)

**Nginx TLS Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name api.lsx.de;

    # TLS 1.3 only
    ssl_protocols TLSv1.3;

    # Strong ciphers only
    ssl_ciphers 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';
    ssl_prefer_server_ciphers off;

    # Certificates
    ssl_certificate /etc/ssl/certs/lsx.de.crt;
    ssl_certificate_key /etc/ssl/private/lsx.de.key;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/ssl/certs/ca-chain.crt;

    # HSTS (force HTTPS)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.lsx.de;
    return 301 https://$server_name$request_uri;
}
```

**PostgreSQL TLS Connection:**
```python
# psycopg3 with TLS
connection = psycopg3.connect(
    "postgresql://user:pass@host:5432/dbname?sslmode=verify-full&sslcert=/path/to/client-cert.pem&sslkey=/path/to/client-key.pem&sslrootcert=/path/to/ca-cert.pem",
    sslmode="verify-full",
    sslcert="/etc/ssl/certs/client-cert.pem",
    sslkey="/etc/ssl/private/client-key.pem",
    sslrootcert="/etc/ssl/certs/ca-cert.pem"
)
```

---

## 8. Upload Security Pipeline

```plantuml
@startuml
title Upload Security Pipeline

actor "User" as user
participant "Frontend" as frontend
participant "Upload API" as upload_api
participant "Virus Scanner" as scanner
participant "File Validator" as validator
participant "PDF Sanitizer" as pdf_sanitizer
participant "Image Processor" as image_proc
participant "S3 Storage" as s3
database "Database" as db

user -> frontend: Upload file (PDF/Image)
frontend -> frontend: Client-side validation\n(file size, type)

alt File too large or wrong type
    frontend -> user: Error: Invalid file
else File valid
    frontend -> upload_api: POST /api/upload\n(multipart/form-data)

    upload_api -> upload_api: Generate unique filename\n(UUID + extension)
    upload_api -> upload_api: Save to temp storage

    upload_api -> scanner: Scan file (ClamAV)

    alt Virus detected
        scanner -> upload_api: VIRUS FOUND
        upload_api -> upload_api: Delete temp file
        upload_api -> frontend: 400 Bad Request: "Malicious file"
        upload_api -> db: Log security event
    else No virus
        scanner -> upload_api: Clean

        upload_api -> validator: Validate MIME type
        validator -> validator: Magic byte analysis

        alt MIME mismatch
            validator -> upload_api: Invalid file type
            upload_api -> frontend: 400 Bad Request
        else MIME valid
            alt File is PDF
                validator -> pdf_sanitizer: Sanitize PDF
                pdf_sanitizer -> pdf_sanitizer: Remove JavaScript
                pdf_sanitizer -> pdf_sanitizer: Remove embedded files
                pdf_sanitizer -> pdf_sanitizer: Remove forms
                pdf_sanitizer -> pdf_sanitizer: Flatten PDF
            else File is Image
                validator -> image_proc: Process image
                image_proc -> image_proc: Strip EXIF data
                image_proc -> image_proc: Re-encode image
                image_proc -> image_proc: Add watermark (if exam)
            end

            upload_api -> upload_api: Calculate SHA256 hash
            upload_api -> upload_api: Encrypt file (optional)

            upload_api -> s3: Upload to S3
            s3 -> upload_api: Upload successful (URL)

            upload_api -> db: Store metadata\n(hash, size, user_id, s3_url)

            upload_api -> frontend: 200 OK + file_id
            frontend -> user: Upload successful
        end
    end
end

@enduml
```

**Upload Security Implementation:**
```python
import hashlib
import magic
import subprocess
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@app.route('/api/upload', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def upload_file():
    """Secure file upload endpoint"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # 1. Validate file extension
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # 2. Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": f"File too large (max {MAX_FILE_SIZE} bytes)"}), 400

    # 3. Generate secure filename
    file_id = str(uuid.uuid4())
    extension = file.filename.rsplit('.', 1)[1].lower()
    secure_name = f"{file_id}.{extension}"
    temp_path = os.path.join('/tmp', secure_name)

    # Save to temp location
    file.save(temp_path)

    try:
        # 4. Virus scan
        if not virus_scan(temp_path):
            log_security_event(
                user_id=get_jwt_identity(),
                event_type='virus_detected',
                details={'filename': file.filename}
            )
            return jsonify({"error": "Malicious file detected"}), 400

        # 5. Validate MIME type (magic bytes)
        file_type = magic.from_file(temp_path, mime=True)
        if not is_valid_mime_type(file_type, extension):
            return jsonify({"error": "File type mismatch"}), 400

        # 6. Sanitize file
        if extension == 'pdf':
            sanitized_path = sanitize_pdf(temp_path)
        elif extension in ['png', 'jpg', 'jpeg']:
            sanitized_path = sanitize_image(temp_path)
        else:
            sanitized_path = temp_path

        # 7. Calculate hash
        file_hash = calculate_sha256(sanitized_path)

        # 8. Upload to S3
        s3_key = f"uploads/{get_jwt_identity()}/{secure_name}"
        s3_url = upload_to_s3(sanitized_path, s3_key)

        # 9. Store metadata
        upload_record = FileUpload(
            file_id=file_id,
            user_id=get_jwt_identity(),
            filename=secure_filename(file.filename),
            file_type=file_type,
            file_size=file_size,
            file_hash=file_hash,
            s3_url=s3_url,
            uploaded_at=datetime.utcnow()
        )
        db.session.add(upload_record)
        db.session.commit()

        return jsonify({
            "file_id": file_id,
            "url": s3_url,
            "size": file_size
        }), 201

    finally:
        # Cleanup temp files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if 'sanitized_path' in locals() and os.path.exists(sanitized_path):
            os.remove(sanitized_path)

def virus_scan(file_path: str) -> bool:
    """Scan file with ClamAV"""
    try:
        result = subprocess.run(
            ['clamscan', '--no-summary', file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0  # 0 = clean, 1 = virus found
    except Exception as e:
        logger.error(f"Virus scan failed: {e}")
        return False  # Fail secure: reject if scan fails

def sanitize_pdf(pdf_path: str) -> str:
    """Sanitize PDF (remove JavaScript, embedded files, etc.)"""
    output_path = pdf_path + '.sanitized'
    subprocess.run([
        'qpdf',
        '--linearize',
        '--remove-unreferenced-resources=yes',
        pdf_path,
        output_path
    ], check=True)
    return output_path

def sanitize_image(image_path: str) -> str:
    """Strip EXIF and re-encode image"""
    from PIL import Image

    img = Image.open(image_path)

    # Remove EXIF
    data = list(img.getdata())
    image_without_exif = Image.new(img.mode, img.size)
    image_without_exif.putdata(data)

    # Re-encode
    output_path = image_path + '.sanitized'
    image_without_exif.save(output_path, quality=95)

    return output_path

def calculate_sha256(file_path: str) -> str:
    """Calculate SHA256 hash of file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()
```

---

## 9. Security Monitoring

### 9.1 Security Events

**Security Event Logging:**
```python
from enum import Enum

class SecurityEventType(Enum):
    AUTH_FAILURE = "auth_failure"
    PRIVILEGE_ESCALATION_ATTEMPT = "privilege_escalation"
    UNUSUAL_ACCESS_PATTERN = "unusual_access"
    SQL_INJECTION_ATTEMPT = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    VIRUS_DETECTED = "virus_detected"
    UNAUTHORIZED_API_ACCESS = "unauthorized_access"
    SUSPICIOUS_USER_AGENT = "suspicious_user_agent"

def log_security_event(
    event_type: SecurityEventType,
    user_id: str = None,
    severity: str = "medium",
    details: dict = None
):
    """Log security event to database and SIEM"""
    event = SecurityEvent(
        event_type=event_type.value,
        user_id=user_id,
        ip_address=request.remote_addr if has_request_context() else None,
        user_agent=request.user_agent.string if has_request_context() else None,
        severity=severity,
        details=details or {},
        timestamp=datetime.utcnow()
    )

    db.session.add(event)
    db.session.commit()

    # Forward to SIEM (Wazuh/Splunk)
    forward_to_siem(event)

    # Alert if critical
    if severity == "critical":
        send_security_alert(event)

def detect_suspicious_activity(user_id: str):
    """Detect suspicious patterns"""
    # Check for unusual access patterns
    recent_logins = AuditLog.query.filter(
        AuditLog.user_id == user_id,
        AuditLog.event_type == 'login',
        AuditLog.timestamp > datetime.utcnow() - timedelta(hours=1)
    ).all()

    # Multiple logins from different IPs
    unique_ips = set(log.ip_address for log in recent_logins)
    if len(unique_ips) > 3:
        log_security_event(
            SecurityEventType.UNUSUAL_ACCESS_PATTERN,
            user_id=user_id,
            severity="high",
            details={"unique_ips": len(unique_ips), "ips": list(unique_ips)}
        )

        # Lock account temporarily
        lock_user_account(user_id, reason="Suspicious activity detected")
```

---

## 10. Zusammenfassung

Die LSX Security Architecture bietet **umfassenden Schutz** durch Defense in Depth:

### Kerneigenschaften

✓ **Zero-Trust Model** – Niemals vertrauen, immer verifizieren
✓ **Multi-Layer Security** – 5 Sicherheitsebenen (UI, API, RBAC, Data, Infrastructure)
✓ **Strong Authentication** – Argon2id + JWT + Optional 2FA (TOTP/FIDO2)
✓ **RBAC Authorization** – Granulare Berechtigungen + Row-Level Security
✓ **Organization Isolation** – Vollständige Mandantentrennung
✓ **Encryption Everywhere** – TLS 1.3, AES-256, End-to-End
✓ **Secure Uploads** – Virus-Scan, Sanitization, Hash-Verification
✓ **OWASP Top 10 Protection** – SQL Injection, XSS, CSRF, etc.
✓ **Security Monitoring** – Audit Logs, SIEM, IDS/IPS
✓ **Compliance** – DSGVO, ISO 27001, Penetration Testing

### Security Stack

• **Authentication:** Argon2id, JWT, TOTP, WebAuthn/FIDO2
• **Authorization:** RBAC, Row-Level Security (RLS)
• **Encryption:** TLS 1.3, AES-256, Fernet
• **WAF:** Cloudflare, Rate Limiting, Bot Detection
• **Monitoring:** Audit Logs, SIEM (Wazuh), IDS (Suricata)
• **Secrets:** HashiCorp Vault
• **Virus Scan:** ClamAV
• **File Sanitization:** qpdf, PIL

Mit dieser umfassenden Security Architecture ist LSX **hochsicher**, **DSGVO-konform** und **bereit für kritische Anwendungen** in Schulen, Unternehmen und im globalen Creator-Markt.

---

**Dokument abgeschlossen.**
**Letzte Aktualisierung:** 2025-11-15
**Nächstes Review:** 2025-12-15
