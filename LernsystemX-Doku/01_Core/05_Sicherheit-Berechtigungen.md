# 19 – Sicherheit & Berechtigungen (Final)

**Version:** 1.0  
**Stand:** Final

---

## Überblick

Dieses Dokument definiert die komplette **Sicherheitsarchitektur** und alle **Berechtigungsmechanismen** des LSX Lernsystems.

Es enthält:
- 🔒 **Regeln & Modelle**
- 🔐 **Datenflüsse**
- 👥 **Rollenprüfungen**
- 🛡️ **Schutzmechanismen**
- 📝 **Logging & Monitoring**
- 🤖 **KI-spezifische Sicherheit**

---

## 1. Sicherheitsarchitektur (C4 Model)

### 🔒 Security System Context

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(user, "User", "Verschiedene Rollen")
Person(attacker, "Attacker", "Böswilliger Akteur")

System_Boundary(security, "Security System") {
    Container(auth, "Authentication", "JWT", "Token Management")
    Container(authz, "Authorization", "RBAC", "Permission Check")
    Container(rate_limit, "Rate Limiter", "Redis", "Request Throttling")
    Container(input_val, "Input Validator", "Sanitizer", "XSS/Injection Protection")
    Container(audit, "Audit Logger", "PostgreSQL", "Activity Tracking")
    Container(monitor, "Monitor", "Alerting", "Abuse Detection")
}

System_Boundary(app, "LSX Application") {
    Container(api, "API Endpoints", "Flask", "Business Logic")
    Container(ki, "KI Services", "Anthropic/OpenAI", "AI Processing")
}

Rel(user, auth, "Login", "HTTPS")
Rel(auth, authz, "Validate")
Rel(authz, rate_limit, "Check Limits")
Rel(rate_limit, input_val, "Validate Input")
Rel(input_val, api, "Process Request")

Rel(api, audit, "Log Action")
Rel(api, monitor, "Track Usage")
Rel(ki, monitor, "Track KI Usage")

Rel(attacker, auth, "Attack Attempt", "X")
Rel(attacker, rate_limit, "DOS Attempt", "X")
Rel(rate_limit, monitor, "Alert", "!")

note right of monitor
  Erkennt und blockt:
  - Brute Force
  - Rate Abuse
  - KI Abuse
  - Anomalien
end note

@enduml
```

---

## 2. Ziele der Sicherheitsarchitektur

### ✅ Sicherheitsziele

| Ziel | Umsetzung |
|------|-----------|
| 🔐 **Benutzerdaten** | Verschlüsselt, Isoliert |
| 🤖 **KI-Schutz** | Rate Limits, Logging |
| 🚫 **Missbrauch** | Detection & Prevention |
| 🔒 **Unauth. Zugriff** | Zero-Trust, RBAC |
| 👥 **Granulare Kontrolle** | Rollenbasiertes System |
| 📜 **DSGVO** | Compliant |
| 🛡️ **Injection/XSS** | Sanitization |
| 📝 **Auditierbarkeit** | Vollständiges Logging |
| 🏢 **Org-Schutz** | Datenisolierung |

---

## 3. Sicherheitsgrundlagen

### 🎯 Zero-Trust-Ansatz

```plantuml
@startuml
|Request|
start
:Eingehender Request;

|Zero-Trust Check|
fork
  :Authentifizierung;
  if (Valid Token?) then (no)
    :401 Unauthorized;
    stop
  endif
fork again
  :Rollenberechtigung;
  if (Has Permission?) then (no)
    :403 Forbidden;
    stop
  endif
fork again
  :Zugriffskontext;
  if (Valid Context?) then (no)
    :403 Forbidden;
    stop
  endif
fork again
  :Ressourcenbesitz;
  if (Owns Resource?) then (no)
    :403 Forbidden;
    stop
  endif
end fork

:Allow Request;
stop

note right
  Jeder Request wird
  vollständig geprüft
  - Trust Nothing
  - Verify Everything
end note
@enduml
```

---

### 🔐 Least Privilege Principle

```plantuml
@startuml
!define ROLE_COLOR #E8F4F8

package "Least Privilege Model" {
  rectangle "Free User" ROLE_COLOR {
    [Lesen von Public Content]
    [Eigene Lernfortschritte]
  }
  
  rectangle "Premium User" ROLE_COLOR {
    [Lesen von Public Content]
    [Eigene Lernfortschritte]
    [Premium Content Zugriff]
    [KI-Features (Limited)]
    [Dashboard Anpassen]
  }
  
  rectangle "Creator" ROLE_COLOR {
    [Premium Features]
    [Kurse Erstellen]
    [KI-Features (Extended)]
    [Analytics]
  }
  
  rectangle "Admin" ROLE_COLOR {
    [System-weite Rechte]
    [User Management]
    [Content Moderation]
    [System Logs]
  }
}

note bottom
  Jede Rolle hat nur
  exakt die benötigten Rechte
  - Keine Überschneidungen
  - Strikte Trennung
end note
@enduml
```

---

## 4. Authentifizierung

### 🔑 JWT Token System

```plantuml
@startuml
participant "Client" as client
participant "Auth API" as auth
participant "Redis" as redis
database "PostgreSQL" as db

== Login ==
client -> auth: POST /auth/login\n{email, password}
activate auth

auth -> db: Validate credentials
db --> auth: User data

auth -> auth: Generate Access Token (15min)
auth -> auth: Generate Refresh Token (7d)
auth -> redis: Store refresh token
auth --> client: {access_token, refresh_token}
deactivate auth

== Authenticated Request ==
client -> auth: API Request\nAuthorization: Bearer <token>
activate auth

auth -> auth: Verify Access Token
alt Token Valid
  auth -> db: Get user & role
  db --> auth: User data
  auth --> client: Process request
else Token Expired
  auth --> client: 401 Token Expired
  
  == Token Refresh ==
  client -> auth: POST /auth/refresh\n{refresh_token}
  auth -> redis: Validate refresh token
  
  alt Refresh Valid
    auth -> auth: Generate new Access Token
    auth --> client: {access_token}
  else Refresh Invalid
    auth --> client: 401 Re-login required
  end
end
deactivate auth

@enduml
```

---

### 🍪 Token Storage Strategy

```plantuml
@startuml
package "Token Storage" {
  component "Client" {
    [Vue.js App]
    
    note right of [Vue.js App]
      ❌ NO LocalStorage
      ❌ NO SessionStorage
      ✅ HTTP-only Cookies
      ✅ SameSite=Strict
    end note
  }
  
  component "Server" {
    [Flask API]
    [Redis Cache]
    
    note right of [Redis Cache]
      Refresh Tokens
      - TTL: 7 days
      - Revocable
      - Device-bound
    end note
  }
}

[Vue.js App] -down-> [Flask API] : "Cookie: token=..."
[Flask API] -down-> [Redis Cache] : "Validate"

note bottom
  Security Features:
  - HTTP-only (No JS access)
  - Secure flag (HTTPS only)
  - SameSite (CSRF protection)
end note
@enduml
```

---

### 🔒 Session Hardening

| Feature | Implementation |
|---------|---------------|
| 🖥️ **Gerätebindung** | Device Fingerprint Hash |
| 🌍 **IP-Tracking** | IP Hash Verification |
| 🔍 **User-Agent** | Browser Fingerprint |
| 🔄 **Token Rotation** | Refresh on every use |
| 🚫 **Invalidation** | On role/password change |

---

## 5. Berechtigungsmodell (RBAC)

### 👥 Role-Based Access Control

```plantuml
@startuml
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x

entity users {
  primary_key(user_id) : UUID
  --
  foreign_key(role_id) : INTEGER
  ...
}

entity roles {
  primary_key(role_id) : SERIAL
  --
  role_name : VARCHAR(50)
  description : TEXT
}

entity permissions {
  primary_key(permission_id) : SERIAL
  --
  permission_key : VARCHAR(100)
  description : TEXT
}

entity role_permissions {
  foreign_key(role_id) : INTEGER
  foreign_key(permission_id) : INTEGER
  --
  PRIMARY KEY (role_id, permission_id)
}

entity role_feature_assignments {
  primary_key(assignment_id) : SERIAL
  --
  foreign_key(role_id) : INTEGER
  foreign_key(feature_id) : INTEGER
  column(enabled) : BOOLEAN
  column(created_by) : UUID
}

entity system_features {
  primary_key(feature_id) : SERIAL
  --
  column(feature_code) : VARCHAR(50) UNIQUE
  column(feature_name) : VARCHAR(100)
  column(category) : VARCHAR(50)
}

users }o--|| roles : "n:1"
roles ||--o{ role_permissions : "1:n"
permissions ||--o{ role_permissions : "1:n"
roles ||--o{ role_feature_assignments : "1:n"
system_features ||--o{ role_feature_assignments : "1:n"

note right of roles
  Standard-Rollen:
  - free (1)
  - premium (2)
  - creator (3)
  - teacher (4)
  - school_admin (5)
  - company_admin (6)
  - admin (7)

  Custom-Rollen:
  - is_custom = TRUE
  - Erstellt via Admin-Panel
end note

note right of role_feature_assignments
  RBAC 2.0:
  Dynamische Feature-Zuweisung
  für Custom-Rollen
  (25 System-Features)
end note

note right of permissions
  Beispiel-Permissions:
  - courses.create
  - courses.edit.own
  - courses.publish
  - ki.generate
  - admin.users.view
end note
@enduml
```

---

### 🎯 Permission Check Flow

```plantuml
@startuml
|API Endpoint|
start
:Receive Request;

|Middleware|
:Extract JWT Token;

if (Token Valid?) then (no)
  :401 Unauthorized;
  stop
endif

:Get User from Token;
:Get User Role;

|Authorization|
:Check Endpoint Permission;

if (Has Role Permission?) then (no)
  :403 Forbidden;
  stop
endif

if (Ownership Required?) then (yes)
  :Check Resource Owner;
  if (Is Owner?) then (no)
    :403 Forbidden;
    stop
  endif
endif

|API Logic|
:Process Request;
:Return Response;
stop

note right
  RBAC Layers:
  1. Token Validation
  2. Role Check
  3. Permission Check
  4. Ownership Check
end note
@enduml
```

---

### 📋 Rollen-Matrix

| Rolle | Kurse Erstellen | KI Nutzen | Global Publish | Admin Panel |
|-------|-----------------|-----------|----------------|-------------|
| 🆓 **Free** | ❌ | ❌ | ❌ | ❌ |
| 💎 **Premium** | ✅ (privat) | ✅ (limit) | ❌ | ❌ |
| ✨ **Creator** | ✅ | ✅ (extended) | ✅ | ❌ |
| 👨‍🏫 **Teacher** | ✅ (Schule) | ✅ (pool) | ❌ | ❌ |
| 🏫 **School Admin** | ✅ | ✅ (pool) | ❌ | ⚠️ (Org) |
| 🏢 **Company Admin** | ✅ | ✅ (pool) | ❌ | ⚠️ (Org) |
| 👑 **Admin** | ✅ | ✅ (unlimited) | ✅ | ✅ |

---

### 👑 Owner-Admin & Custom Roles (RBAC 2.0)

**Status:** ✅ **IMPLEMENTIERT** (Migration 067, 068)

#### Owner-Admin System

Der **Owner-Admin** ist eine spezielle Admin-Rolle mit erweiterten Berechtigungen:

```sql
-- users table
ALTER TABLE users ADD COLUMN is_owner BOOLEAN DEFAULT FALSE;
CREATE UNIQUE INDEX idx_single_owner ON users(is_owner) WHERE is_owner = TRUE;
```

**Eigenschaften:**
- ✅ Nur **EIN** Owner-Admin möglich (Database Constraint)
- ✅ Wird automatisch beim **Setup Wizard** erstellt (erster Admin = Owner)
- ✅ Kann **Custom-Rollen** erstellen/bearbeiten/löschen
- ✅ Kann **Ownership übertragen** (an anderen Admin)
- ✅ Hat Zugriff auf **vollständige Audit-Logs**
- ✅ Kann **Compliance-Einstellungen** verwalten

**Owner-Admin Berechtigungen (Exklusiv):**
```python
OWNER_ADMIN_ONLY_PERMISSIONS = [
    'manage_roles',           # Create/Edit/Delete Custom-Rollen
    'manage_owner_transfer',  # Owner an anderen Admin übertragen
    'delete_system_data',     # System-Daten löschen
    'access_audit_logs',      # Vollständige Audit Logs
    'manage_compliance',      # Compliance-Einstellungen
    'emergency_access'        # Notfall-Zugriff auf alles
]
```

#### Custom Roles (Dynamisches Rollen-System)

**Zweck:** Owner-Admin kann neue Rollen über Admin-Panel erstellen und Features zuweisen.

**Datenbank-Schema:**

```sql
-- roles table (erweitert)
ALTER TABLE roles ADD COLUMN is_custom BOOLEAN DEFAULT FALSE;
ALTER TABLE roles ADD COLUMN created_by UUID REFERENCES users(user_id);
ALTER TABLE roles ADD COLUMN template_name VARCHAR(50);

-- role_feature_assignments (NEW)
CREATE TABLE core.role_feature_assignments (
    assignment_id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    feature_id INTEGER NOT NULL REFERENCES support_systems.system_features(feature_id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(user_id),
    UNIQUE(role_id, feature_id)
);
```

**Role Templates (Vordefiniert):**

| Template | Beschreibung | Features |
|----------|--------------|----------|
| 👪 **Parent** | Eltern-Rolle für Kinderkontrolle | Content-Freigabe, Activity-Monitoring |
| 🏢 **Enterprise Admin** | Unternehmens-Admin mit Bulk-Features | Bulk-Import, SSO-Config, Analytics |
| 🔍 **Auditor** | Compliance-Auditor | Audit-Logs, Export, Compliance-Reports |
| 📚 **Librarian** | Content-Kurator | Content-Moderation, Kategorien |
| 🎓 **Course Manager** | Kurs-Manager ohne Admin-Rechte | Course CRUD, Publishing |

**Feature-Zuweisung:**

Custom-Rollen können **System-Features** (25 Features) individuell zugewiesen bekommen:

```typescript
// Beispiel: Parent-Rolle erstellen
const parentRole = {
  role_name: 'parent',
  display_name: 'Parent',
  description: 'Elternkonto mit Kinderkontrolle',
  is_custom: true,
  created_by: owner_admin_id,

  // Zugewiesene Features:
  features: [
    'parental_controls',    // Kinderkontrolle
    'content_approval',     // Content-Freigabe
    'screen_time_mgmt',     // Bildschirmzeit
    'activity_reports'      // Activity-Reports
  ]
}
```

#### Admin-Panel: Role Management

**Endpoints (TODO):**
```
GET    /api/v1/admin/roles              # List all roles
POST   /api/v1/admin/roles              # Create custom role (Owner-Admin only)
PUT    /api/v1/admin/roles/{role_id}    # Update role (Owner-Admin only)
DELETE /api/v1/admin/roles/{role_id}    # Delete custom role (Owner-Admin only)

GET    /api/v1/admin/roles/{role_id}/permissions    # Get role permissions
POST   /api/v1/admin/roles/{role_id}/permissions    # Assign permissions

GET    /api/v1/admin/roles/templates    # Get role templates
POST   /api/v1/admin/roles/from-template # Create role from template
```

**Frontend-Komponenten (TODO):**
```
frontend/src/pages/admin/RoleManagement.vue
frontend/src/components/admin/roles/
├── RoleList.vue
├── RoleForm.vue
├── RolePermissionsMatrix.vue
├── RoleTemplateSelector.vue
└── RoleDeleteConfirm.vue
```

#### Permission-Middleware (Erweiterung)

**Backend-Check:**
```python
# backend/app/middleware/auth.py
@require_permission('manage_roles')  # ← Nur Owner-Admin
def create_custom_role():
    """Create custom role with feature assignments"""
    pass
```

**Frontend-Check:**
```typescript
// Frontend Permission Guard
const canManageRoles = computed(() => {
  return authStore.user?.is_owner === true
})
```

#### Aktueller Status

| Komponente | Status |
|------------|--------|
| Owner-Admin (users.is_owner) | ✅ Implementiert (Migration 067) |
| Unique Constraint (nur 1 Owner) | ✅ Implementiert (idx_single_owner) |
| Setup Wizard Owner Creation | ✅ Implementiert (admin_setup.py) |
| role_feature_assignments Table | ✅ Implementiert (Migration 068) |
| Custom Roles (roles.is_custom) | ✅ Schema vorhanden |
| Backend API (admin/roles.py) | 🟡 TODO |
| Frontend Admin-Panel | 🟡 TODO |
| Permission Middleware | 🟡 TODO |

**Nächste Schritte:**
1. Backend API für Rollen-Management implementieren
2. Frontend Admin-Panel für Custom-Rollen erstellen
3. Permission Middleware erweitern
4. Unit Tests für RBAC 2.0 schreiben

---

## 6. Ressourcen-Besitzmodell

### 🏢 Ownership Hierarchy

```plantuml
@startuml
package "Ownership Model" {
  class Resource {
    +resource_id: UUID
    +owner_id: UUID
    +owner_type: String
    +org_id: UUID (nullable)
    --
    +checkAccess(user): Boolean
  }
  
  class User {
    +user_id: UUID
    +role_id: Integer
    +org_id: UUID (nullable)
  }
  
  class Organization {
    +org_id: UUID
    +type: String
  }
  
  Resource "n" --> "1" User : "owned by"
  Resource "n" --> "0..1" Organization : "belongs to"
  User "n" --> "0..1" Organization : "member of"
}

note right of Resource
  Ownership Rules:
  - Creator owns: eigene Kurse
  - Premium owns: eigene Kurse
  - Teacher owns: Klassen-Kurse
  - School owns: alle Org-Ressourcen
  - Admin owns: system-wide
end note
@enduml
```

---

## 7. Endpunkt-Schutz

### 🔐 API Endpoint Security

```plantuml
@startuml
@startuml
map "POST /api/v1/courses" {
  requires_auth => true
  allowed_roles => ["creator", "teacher", "school_admin"]
  requires_ownership => false
  rate_limit => 10/min
}

map "PATCH /api/v1/courses/{id}" {
  requires_auth => true
  allowed_roles => ["creator", "teacher", "school_admin", "admin"]
  requires_ownership => true
  rate_limit => 20/min
}

map "POST /api/v1/ki/generate" {
  requires_auth => true
  allowed_roles => ["premium", "creator", "teacher"]
  requires_ownership => false
  rate_limit => 2/min
  token_check => true
}

map "GET /api/v1/admin/users" {
  requires_auth => true
  allowed_roles => ["admin"]
  requires_ownership => false
  rate_limit => 100/min
}

note right
  Alle Endpoints sind
  geschützt durch:
  - Authentication
  - Role Check
  - Ownership Check
  - Rate Limiting
end note
@enduml
@enduml
```

---

## 8. Input-Sicherheit

### 🛡️ Input Validation Pipeline

```plantuml
@startuml
|Client|
start
:Submit Form Data;

|API Gateway|
:Receive Request;

|Input Validator|
:1. Sanitisierung;
note right
  - HTML Strip
  - SQL Escape
  - Script Remove
end note

if (Contains Malicious Code?) then (yes)
  :400 Bad Request;
  stop
endif

:2. Schema Validierung;
note right
  - Type Check
  - Format Check
  - Required Fields
end note

if (Schema Valid?) then (no)
  :400 Validation Error;
  stop
endif

:3. Length Limits;
if (Within Limits?) then (no)
  :413 Payload Too Large;
  stop
endif

:4. Special Checks;
fork
  :Theorieblatt: HTML Strip;
fork again
  :Methoden: JSON Validate;
fork again
  :Email: Regex Check;
end fork

|API Logic|
:Process Validated Input;
stop
@enduml
```

---

### 🔍 Validation Rules

| Input Type | Validation |
|------------|-----------|
| 📧 **Email** | Regex + DNS Check |
| 🔑 **Password** | Min 8, Upper, Lower, Number |
| 📝 **Theorieblatt** | HTML Sanitizer, MaxLength |
| 🎯 **Methoden** | JSON Schema Validation |
| 📁 **Filename** | Path Traversal Check |
| 🌐 **URL** | Whitelist + SSRF Check |

---

## 9. Dateiupload-Sicherheit

### 📤 File Upload Security Flow

```plantuml
@startuml
actor User
participant "Upload API" as api
participant "File Scanner" as scanner
participant "Storage" as storage
database "Database" as db

User -> api: Upload File
activate api

api -> api: Check File Size
alt Size > 50MB
  api --> User: 413 Too Large
  deactivate api
  stop
end

api -> api: Check MIME Type
alt Invalid Type
  api --> User: 400 Invalid File Type
  deactivate api
  stop
end

api -> scanner: Scan File (ClamAV)
activate scanner
scanner -> scanner: Virus Scan
scanner -> scanner: Malware Check

alt Threat Found
  scanner --> api: Threat Detected
  api --> User: 400 Malicious File
  deactivate scanner
  deactivate api
  stop
end

scanner --> api: Clean
deactivate scanner

api -> storage: Store in Quarantine
storage --> api: temp_path

api -> api: Generate Hash
api -> db: Save Metadata
db --> api: file_id

api --> User: {file_id, status: "processing"}
deactivate api

... Background Processing ...

api -> api: Parse Content
api -> storage: Move to Safe Storage
api -> db: Update status: "ready"
@enduml
```

---

### 🛡️ Upload Security Measures

| Maßnahme | Implementation |
|----------|---------------|
| 🦠 **Virenscan** | ClamAV Integration |
| 📄 **MIME Check** | Magic Bytes Validation |
| 📏 **Size Limit** | 50MB per File |
| 📦 **PDF Sandbox** | Isolated Processing |
| 🚫 **No Executables** | Extension Blacklist |
| 🔒 **Safe Storage** | Isolated Directory |
| 🤖 **KI Filtration** | Before User Access |

---

## 10. KI-Sicherheit

### 🤖 KI Security Architecture

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

Container_Boundary(ki_security, "KI Security Layer") {
    Component(rate_limiter, "Rate Limiter", "Redis", "Per-User/Role Limits")
    Component(token_manager, "Token Manager", "PostgreSQL", "Token Pool Management")
    Component(abuse_detector, "Abuse Detector", "ML", "Anomaly Detection")
    Component(content_filter, "Content Filter", "Rules", "Harmful Content Check")
    Component(logger, "KI Logger", "PostgreSQL", "ki_requests Table")
}

Component(ki_api, "KI API", "Anthropic/OpenAI")

Rel(rate_limiter, token_manager, "Check Tokens")
Rel(token_manager, abuse_detector, "Monitor")
Rel(abuse_detector, content_filter, "Validate")
Rel(content_filter, ki_api, "Forward Request")
Rel(ki_api, logger, "Log Request/Response")

note right of abuse_detector
  Erkennt:
  - Extreme lange Prompts
  - Mass Generation
  - Harmful Content
  - Negative Prompting
  - Data Exfiltration
end note
@enduml
```

---

### 📊 KI Rate Limits pro Rolle

```plantuml
@startuml
card "Free User" {
  :❌ Keine KI-Features;
}

card "Premium User" {
  :✅ KI-Features;
  :Token Limit: 10,000/Monat;
  :Rate Limit: 2 req/min;
}

card "Creator" {
  :✅ Erweiterte KI-Features;
  :Token Limit: 50,000/Monat;
  :Rate Limit: 5 req/min;
}

card "School/Company" {
  :✅ KI-Features (Pool);
  :Shared Token Pool;
  :Rate Limit: 10 req/min;
}

card "Admin" {
  :✅ Unlimited KI;
  :System-Level Access;
  :Rate Limit: 20 req/min;
}

note bottom
  Token-basiertes
  Fair-Use System
end note
@enduml
```

---

### 🚨 KI Abuse Detection

```plantuml
@startuml
|User Request|
start
:KI Request;

|Abuse Detector|
:Check Request Pattern;

fork
  :Prompt Length Check;
  if (> 10,000 chars?) then (yes)
    :⚠️ Alert: Extreme Length;
  endif
fork again
  :Frequency Check;
  if (> 10 req/min?) then (yes)
    :⚠️ Alert: Mass Generation;
  endif
fork again
  :Content Check;
  if (Harmful Content?) then (yes)
    :🚫 Block Request;
    stop
  endif
fork again
  :Pattern Analysis;
  if (Data Exfiltration?) then (yes)
    :🚫 Block + Log;
    stop
  endif
end fork

if (Abuse Detected?) then (yes)
  |Admin Alert|
  :Send Alert;
  :Throttle User;
  :Log Incident;
endif

:Allow Request;
stop
@enduml
```

---

### 📝 KI Request Logging

Jede KI-Anfrage wird in `ki_requests` gespeichert:

```sql
CREATE TABLE ki_requests (
    ki_request_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    role_id INTEGER NOT NULL,
    type VARCHAR(100),  -- 'module_gen', 'translation', etc.
    input_reference TEXT,  -- Hash of input
    output_reference TEXT,  -- Hash of output
    token_used INTEGER,
    model_used VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP,
    
    -- Security Fields
    request_ip INET,
    user_agent TEXT,
    abuse_score INTEGER DEFAULT 0
);
```

---

## 11. Organisationen-Sicherheit

### 🏢 Organization Data Isolation

```plantuml
@startuml
package "Organization Security" {
  rectangle "School A" #LightBlue {
    [Users A]
    [Courses A]
    [Data A]
  }
  
  rectangle "School B" #LightGreen {
    [Users B]
    [Courses B]
    [Data B]
  }
  
  rectangle "Security Layer" #LightGray {
    [Org Filter]
    [Access Control]
    [Domain Verification]
  }
  
  [Users A] -down-> [Org Filter]
  [Users B] -down-> [Org Filter]
  
  [Org Filter] -down-> [Access Control]
  [Access Control] -down-> [Domain Verification]
}

note right of "Security Layer"
  Isolation Rules:
  - Users only see own org
  - Domain verification required
  - Separate token pools
  - No cross-org data access
end note

note left of "School A"
  school.example.edu
  - 500 Students
  - 20 Teachers
  - Token Pool: 100k
end note
@enduml
```

---

### 🔒 Organization Security Features

| Feature | Implementation |
|---------|---------------|
| 🔐 **Domain Verification** | CNAME Record Check |
| 👥 **User Isolation** | org_id Filter on ALL queries |
| 💰 **Token Pool** | Shared org_id pool |
| 🎓 **Teacher Rights** | Only within org |
| 📊 **Data Isolation** | Row-Level Security |
| 🚫 **Cross-Org Access** | Blocked by Middleware |

---

## 12. Creator-Schutz

### ✨ Creator Content Protection

```plantuml
@startuml
package "Creator Protection" {
  component "Content Security" {
    [Anti-Copy]
    [Watermark]
    [Version Control]
    [Access Control]
  }
  
  component "Export Control" {
    [Permission Check]
    [Watermark Injection]
    [Download Tracking]
  }
  
  component "Anti-Scraping" {
    [Rate Limiting]
    [Bot Detection]
    [IP Tracking]
  }
}

actor "Legitimate User" as user
actor "Scraper Bot" as bot

user --> [Access Control] : "View Course"
[Access Control] --> [Version Control] : "Track Access"

bot --> [Anti-Scraping] : "Mass Requests"
[Anti-Scraping] --> [Bot Detection] : "Block"

note right of "Content Security"
  Creator-Kurse sind geschützt:
  - Kein unauth. Export
  - Wasserzeichen
  - Versionskontrolle
  - Zugriffslogs
end note
@enduml
```

---

## 13. Community-Sicherheit

### 👥 Community Moderation System

```plantuml
@startuml
|User|
start
:Upload Community Course;

|Auto-Moderation|
:KI Content Scan;

fork
  :Toxicity Check;
fork again
  :Copyright Check;
fork again
  :Quality Check;
end fork

if (Issues Found?) then (yes)
  :🚧 Quarantine;
  |Moderator Queue|
  :Add to Review Queue;
  
  |Human Moderator|
  :Review Content;
  
  if (Approve?) then (yes)
    :✅ Publish;
  else (no)
    :❌ Reject;
    :Notify User;
  endif
else (no)
  :✅ Auto-Approve;
  :Publish to Community;
endif

stop

note right
  Multi-Layer Moderation:
  1. Automated KI Scan
  2. Risk Scoring
  3. Human Review (if needed)
end note
@enduml
```

---

## 14. LiveRoom-Sicherheit

### 🎥 LiveRoom Security Model

```plantuml
@startuml
package "LiveRoom Security" {
  component "Access Control" {
    [Room Owner]
    [Moderator]
    [Presenter]
    [Participant]
  }
  
  component "WebRTC Security" {
    [DTLS Encryption]
    [SRTP Media]
    [Peer Validation]
  }
  
  component "Action Control" {
    [Kick/Ban]
    [Mute Control]
    [Screen Share Control]
    [Recording Rights]
  }
}

[Room Owner] -down-> [Moderator] : "assign"
[Moderator] -down-> [Kick/Ban] : "execute"
[Presenter] -down-> [Screen Share Control] : "use"
[Participant] -down-> [DTLS Encryption] : "connect via"

note bottom
  Role-Based Permissions:
  - Owner: Full Control
  - Moderator: Kick/Mute
  - Presenter: Share Screen
  - Participant: View Only
end note
@enduml
```

---

## 15. Logging & Monitoring

### 📝 Logging Architecture

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Container_Boundary(logging, "Logging System") {
    Container(system_log, "System Log", "PostgreSQL", "Auth, Errors, Changes")
    Container(audit_log, "Audit Log", "PostgreSQL", "Business Events")
    Container(security_log, "Security Log", "PostgreSQL", "Security Events")
    Container(ki_log, "KI Log", "PostgreSQL", "ki_requests Table")
}

Container_Boundary(monitoring, "Monitoring") {
    Container(alerting, "Alerting", "Email/Slack", "Real-time Alerts")
    Container(dashboard, "Admin Dashboard", "Vue.js", "Visualization")
    Container(analytics, "Analytics", "Python", "Pattern Detection")
}

Rel(system_log, dashboard, "Display")
Rel(audit_log, dashboard, "Display")
Rel(security_log, alerting, "Alert on Events")
Rel(ki_log, analytics, "Analyze Usage")

@enduml
```

---

### 📊 Log Categories

| Log Type | Events | Retention |
|----------|--------|-----------|
| 🔐 **System Log** | Logins, Errors, Config Changes | 90 days |
| 📝 **Audit Log** | Courses, Exams, LiveRooms | 1 year |
| 🚨 **Security Log** | Failed Logins, Abuse, Blocks | 2 years |
| 🤖 **KI Log** | All KI Requests | 1 year |

---

## 16. Rate Limits

### ⏱️ Rate Limiting Strategy

```plantuml
@startuml
package "Rate Limiting (Redis)" {
  map "Auth Endpoints" {
    /auth/login => 5/min
    /auth/register => 3/min
    /auth/refresh => 10/min
  }
  
  map "KI Endpoints" {
    /ki/generate => 2/min (premium)
    /ki/generate => 5/min (creator)
    /ki/analyze => 3/min
  }
  
  map "Content Endpoints" {
    POST /courses => 10/min
    PATCH /courses => 20/min
    POST /methods => 15/min
  }
  
  map "Upload Endpoints" {
    POST /upload => 5/10min
    POST /media => 10/hour
  }
}

note right
  Redis-based counters
  - Per User
  - Per IP
  - Sliding Window
end note
@enduml
```

---

## 17. Schutz vor bekannten Angriffen

### 🛡️ Attack Prevention Matrix

```plantuml
@startuml
@startmindmap
* Security Defenses
** SQL Injection
*** Parameterized Queries (psycopg3)
*** Prepared Statements
*** Input Validation
** XSS
*** HTML Sanitizer
*** Content-Security-Policy
*** Output Encoding
** CSRF
*** JWT Tokens
*** SameSite Cookies
*** CORS Policy
** SSRF
*** URL Whitelist
*** No Direct External Requests
*** Internal Network Isolation
** DOS
*** Rate Limiting
*** IP Blocking
*** CloudFlare
** Brute Force
*** Login Throttling
*** Account Lockout
*** CAPTCHA
** Session Hijacking
*** Token Rotation
*** Device Binding
*** HTTPS Only
@endmindmap
@enduml
```

---

### 🔒 Defense-in-Depth

```plantuml
@startuml
rectangle "Application Layer" #LightBlue {
  [Input Validation]
  [Output Encoding]
  [CSRF Protection]
}

rectangle "Authentication Layer" #LightGreen {
  [JWT Tokens]
  [Session Management]
  [MFA (Optional)]
}

rectangle "Network Layer" #LightYellow {
  [Rate Limiting]
  [IP Filtering]
  [DDoS Protection]
}

rectangle "Database Layer" #LightPink {
  [ORM Protection]
  [Encryption at Rest]
  [Access Control]
}

[Application Layer] -down-> [Authentication Layer]
[Authentication Layer] -down-> [Network Layer]
[Network Layer] -down-> [Database Layer]

note right
  Multiple Security Layers
  - Defense-in-Depth
  - Redundant Controls
  - Fail-Secure
end note
@enduml
```

---

## 18. Backups & Recovery

### 💾 Backup Strategy

```plantuml
@startuml
|Daily|
start
:Full Database Backup;
:Encrypt Backup;
:Upload to S3;

|Weekly|
:Full System Snapshot;
:Test Recovery;

|Monthly|
:Recovery Drill;
:Update DR Plan;

|Critical Updates|
:Pre-Update Snapshot;
:Deploy Update;
:Verify System;

if (Issues?) then (yes)
  :Rollback;
else (no)
  :Delete Old Snapshot;
endif

stop
@enduml
```

---

## 19. Zusammenfassung

### ✅ LSX Security Features

| Kategorie | Features |
|-----------|----------|
| 🔐 **Auth** | JWT, HTTP-only Cookies, Token Rotation |
| 👥 **Authorization** | RBAC, Ownership, Permissions |
| 🛡️ **Input Security** | Sanitization, Validation, Length Limits |
| 📤 **File Upload** | Virus Scan, MIME Check, Sandboxing |
| 🤖 **KI Security** | Rate Limits, Abuse Detection, Logging |
| 🏢 **Org Security** | Data Isolation, Domain Verification |
| ✨ **Creator Protection** | Anti-Copy, Watermarks, Version Control |
| 👥 **Community** | Auto-Moderation, Human Review |
| 🎥 **LiveRoom** | WebRTC Encryption, Role-based Access |
| 📝 **Logging** | System, Audit, Security, KI Logs |
| ⏱️ **Rate Limiting** | Redis-based, Per-Endpoint |
| 🛡️ **Attack Prevention** | SQL, XSS, CSRF, SSRF, DOS |

---

### 🎯 Security Architecture Overview

```
┌─────────────────────────────────────┐
│  🔒 Zero-Trust Architecture          │
│  ─────────────────────────────────   │
│  ✅ JWT Authentication                │
│  ✅ RBAC Authorization                │
│  ✅ Input Validation                  │
│  ✅ Rate Limiting                     │
│  ✅ Audit Logging                     │
│  ✅ Abuse Detection                   │
│  ✅ Data Isolation                    │
│  ✅ Encryption (Transit & Rest)       │
└─────────────────────────────────────┘
```

> **LSX erfüllt alle modernen IT-Sicherheitsanforderungen und ist DSGVO-konform.**

---

## 📌 Dokument abgeschlossen

**Version:** 1.0  
**Status:** Final  
**Letzte Aktualisierung:** November 2024

---

> 💡 **Hinweis:** Dieses Dokument ist Teil der LSX-Systemdokumentation und beschreibt die vollständige Sicherheitsarchitektur mit Zero-Trust-Ansatz, RBAC, KI-Schutz und umfassendem Monitoring.