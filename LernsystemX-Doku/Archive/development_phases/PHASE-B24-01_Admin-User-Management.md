# Phase B24-01: Admin User Management - Technische Dokumentation

**Version:** 1.0.0
**Datum:** 2025-11-19
**Status:** Implementiert (Backend), Ausstehend (Frontend)
**Compliance:** ISO/IEC 25010, ISO/IEC/IEEE 26514, ISO/IEC/IEEE 12207, OWASP ASVS 4.0

---

## Inhaltsverzeichnis

1. [Übersicht](#1-übersicht)
2. [Technische Beschreibung](#2-technische-beschreibung)
3. [API-Spezifikation](#3-api-spezifikation)
4. [Backend-Architektur](#4-backend-architektur)
5. [Frontend-Architektur](#5-frontend-architektur)
6. [Datenbank-Änderungen](#6-datenbank-änderungen)
7. [Sicherheitsaspekte](#7-sicherheitsaspekte)
8. [Changelog](#8-changelog)
9. [Edge Cases & Erweiterbarkeit](#9-edge-cases--erweiterbarkeit)
10. [Datenfluss-Diagramme](#10-datenfluss-diagramme)

---

## 1. Übersicht

### 1.1 Zweck

Phase B24-01 implementiert das **Admin User Management System**, das Administratoren die vollständige Kontrolle über Benutzerkonten ermöglicht. Das System umfasst:

- Benutzerverwaltung (Anzeigen, Suchen, Filtern)
- Rollenverwaltung (Rollenwechsel)
- Benutzersperren (Temporär/Permanent)
- Token-Gewährung
- Benutzerlöschung (Soft/Hard Delete)
- Creator-Verifizierung

### 1.2 Betroffene Subsysteme

- **Authentication & Authorization** (RBAC)
- **Audit Logging** (ISO 27001:2013)
- **User Management** (CRUD)
- **Token Management** (Wallet System)
- **API Gateway** (Routing, Rate Limiting)

### 1.3 Abhängigkeiten

- `app.middleware.auth` - JWT-Token-Validierung
- `app.security.permissions` - RBAC Permission System
- `app.services.audit_service` - Audit Logging
- `app.repositories.user_repository` - User Data Access
- `app.repositories.token_repository` - Token Operations
- `app.models.admin` - Pydantic Validation Models

---

## 2. Technische Beschreibung

### 2.1 Kontext

Das Admin User Management System ist Teil der **Admin-Panel-Architektur (Phase B24)** und ermöglicht granulare Verwaltung aller Benutzerkonten im System. Es implementiert die in **Dokument 24_Admin-System.md** spezifizierten Anforderungen.

### 2.2 Architektur-Pattern

```
┌─────────────┐
│   Client    │
│  (Frontend) │
└──────┬──────┘
       │ HTTP Request (JWT)
       ▼
┌─────────────────────┐
│   API Gateway       │
│  /api/v1/admin/*    │
└──────┬──────────────┘
       │ @token_required
       │ @require_permission(ADMIN_USER_WRITE)
       ▼
┌─────────────────────┐
│  admin_users.py     │  ◄── Blueprint (Route Handler)
│  (Routes/Endpoints) │
└──────┬──────────────┘
       │ Business Logic Delegation
       ▼
┌─────────────────────┐
│  UserRepository     │  ◄── Data Access Layer
│  TokenRepository    │
└──────┬──────────────┘
       │ SQL Queries (Parameterized)
       ▼
┌─────────────────────┐
│   PostgreSQL DB     │
│  users, audit_logs  │
│  token_wallets      │
└─────────────────────┘
```

### 2.3 Datenfluss

1. **Request**: Client sendet HTTP-Request mit JWT-Token
2. **Authentication**: Middleware validiert JWT und extrahiert User-Daten
3. **Authorization**: Permission Decorator prüft RBAC (z.B. `ADMIN_USER_WRITE`)
4. **Validation**: Pydantic validiert Request Body
5. **Business Logic**: Route-Handler ruft Repository-Methoden auf
6. **Audit Logging**: Alle Aktionen werden in `audit_logs` geschrieben
7. **Response**: JSON-Response mit Erfolg/Fehler

---

## 3. API-Spezifikation

### 3.1 Basis-URL

```
/api/v1/admin/users
```

### 3.2 Authentifizierung

Alle Endpoints erfordern:
- JWT-Token im `Authorization: Bearer <token>` Header
- Admin-Rolle (`role = 'admin'`)
- Spezifische Permissions (RBAC)

### 3.3 Endpoints

#### 3.3.1 GET /api/v1/admin/users

**Beschreibung:** Liste aller Benutzer mit Pagination und Filtern

**Permissions:** `ADMIN_USER_READ`

**Query Parameters:**

| Parameter | Typ     | Pflicht | Default | Beschreibung                                    |
|-----------|---------|---------|---------|------------------------------------------------|
| page      | integer | Nein    | 1       | Seitennummer (1-indexed)                       |
| per_page  | integer | Nein    | 50      | Anzahl Einträge pro Seite (Max: 100)          |
| role      | string  | Nein    | -       | Filtern nach Rolle (free, premium, admin, ...) |
| search    | string  | Nein    | -       | Suche in Email/Name                            |
| status    | string  | Nein    | active  | Filter Status (active, suspended, banned)      |
| sort      | string  | Nein    | created_at | Sortierfeld (created_at, last_login, email)|
| order     | string  | Nein    | desc    | Sortierung (asc, desc)                         |

**Response 200 OK:**

```json
{
  "success": true,
  "users": [
    {
      "user_id": "uuid",
      "email": "user@example.com",
      "firstname": "John",
      "lastname": "Doe",
      "role": "premium",
      "status": "active",
      "created_at": "2025-01-15T10:00:00Z",
      "last_login": "2025-11-19T10:00:00Z",
      "email_verified": true,
      "organisation_id": null
    }
  ],
  "pagination": {
    "total": 1234,
    "page": 1,
    "per_page": 50,
    "total_pages": 25
  }
}
```

**Fehlercodes:**
- `401 Unauthorized` - Kein/ungültiger JWT-Token
- `403 Forbidden` - Fehlende Permission `ADMIN_USER_READ`
- `400 Bad Request` - Ungültige Query-Parameter

**Audit Log:** `admin.users.list` (Severity: `info`)

---

#### 3.3.2 GET /api/v1/admin/users/{user_id}

**Beschreibung:** Detaillierte Benutzerinformationen abrufen

**Permissions:** `ADMIN_USER_READ`

**Path Parameters:**

| Parameter | Typ    | Pflicht | Beschreibung |
|-----------|--------|---------|--------------|
| user_id   | UUID   | Ja      | Benutzer-ID  |

**Response 200 OK:**

```json
{
  "success": true,
  "user": {
    "user_id": "uuid",
    "email": "user@example.com",
    "firstname": "John",
    "lastname": "Doe",
    "role": "premium",
    "status": "active",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-11-19T10:00:00Z",
    "last_login": "2025-11-19T10:00:00Z",
    "last_login_ip": "192.168.1.1",
    "email_verified": true,
    "two_factor_enabled": false,
    "organisation_id": null,
    "subscription": {
      "plan": "premium",
      "status": "active",
      "expires_at": "2025-12-19T10:00:00Z",
      "auto_renew": true
    },
    "tokens": {
      "balance": 5000,
      "total_used": 2500,
      "total_granted": 1000,
      "total_purchased": 6500
    },
    "courses_created": 12,
    "courses_enrolled": 45,
    "login_history": [
      {
        "login_time": "2025-11-19T10:00:00Z",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "success": true
      }
    ],
    "ban_history": []
  }
}
```

**Fehlercodes:**
- `404 Not Found` - Benutzer nicht gefunden
- `401 Unauthorized` - Kein/ungültiger JWT-Token
- `403 Forbidden` - Fehlende Permission

**Audit Log:** `admin.users.view` (Severity: `info`)

---

#### 3.3.3 PUT /api/v1/admin/users/{user_id}/role

**Beschreibung:** Benutzerrolle ändern

**Permissions:** `ADMIN_USER_WRITE`

**Path Parameters:**

| Parameter | Typ  | Pflicht | Beschreibung |
|-----------|------|---------|--------------|
| user_id   | UUID | Ja      | Benutzer-ID  |

**Request Body:**

```json
{
  "role": "premium",
  "reason": "Upgrade requested by support"
}
```

**Validierung:**
- `role`: Enum (free, premium, creator, teacher, school, company, support, moderator, admin)
- `reason`: String, min_length=10, max_length=500

**Response 200 OK:**

```json
{
  "success": true,
  "message": "User role changed to premium"
}
```

**Business Rules:**
- Admin kann eigene Rolle NICHT ändern
- Rolle muss im System existieren

**Fehlercodes:**
- `400 Bad Request` - Ungültige Rolle oder fehlende Begründung
- `403 Forbidden` - Versuch, eigene Rolle zu ändern
- `404 Not Found` - Benutzer nicht gefunden

**Audit Log:** `admin.users.change_role` (Severity: `high`)

---

#### 3.3.4 POST /api/v1/admin/users/{user_id}/ban

**Beschreibung:** Benutzer sperren (temporär oder permanent)

**Permissions:** `ADMIN_USER_WRITE`

**Request Body:**

```json
{
  "reason": "Violation of community guidelines",
  "duration_days": 30,
  "permanent": false,
  "notify_user": true
}
```

**Validierung:**
- `reason`: String, min_length=10, max_length=1000
- `duration_days`: Optional, Integer, 1-365 (nur bei permanent=false)
- `permanent`: Boolean, default=false
- `notify_user`: Boolean, default=true
- **Constraint:** `duration_days` und `permanent` schließen sich aus

**Response 200 OK:**

```json
{
  "success": true,
  "message": "User banned successfully",
  "banned_until": "2025-12-19T10:00:00Z"
}
```

**Business Rules:**
- Admin kann sich selbst NICHT bannen
- Admin kann andere Admins NICHT bannen
- Permanente Bans haben kein Enddatum

**Fehlercodes:**
- `400 Bad Request` - Validierungsfehler
- `403 Forbidden` - Versuch, sich selbst oder anderen Admin zu bannen
- `404 Not Found` - Benutzer nicht gefunden

**Audit Log:** `admin.users.ban` (Severity: `critical`)

---

#### 3.3.5 POST /api/v1/admin/users/{user_id}/unban

**Beschreibung:** Benutzersperre aufheben

**Permissions:** `ADMIN_USER_WRITE`

**Request Body:**

```json
{
  "reason": "Appeal approved"
}
```

**Response 200 OK:**

```json
{
  "success": true,
  "message": "User unbanned successfully"
}
```

**Audit Log:** `admin.users.unban` (Severity: `high`)

---

#### 3.3.6 POST /api/v1/admin/users/{user_id}/tokens/grant

**Beschreibung:** Tokens an Benutzer gewähren

**Permissions:** `ADMIN_USER_WRITE`

**Request Body:**

```json
{
  "amount": 5000,
  "reason": "Goodwill gesture for reported bug"
}
```

**Validierung:**
- `amount`: Integer, 1-1,000,000
- `reason`: String, min_length=10, max_length=500

**Response 200 OK:**

```json
{
  "success": true,
  "message": "5000 tokens granted",
  "new_balance": 10500
}
```

**Business Rules:**
- Automatische Wallet-Erstellung, falls nicht vorhanden
- Transaktion wird in `token_transactions` gespeichert

**Audit Log:** `admin.users.grant_tokens` (Severity: `medium`)

---

#### 3.3.7 DELETE /api/v1/admin/users/{user_id}

**Beschreibung:** Benutzer löschen (Soft/Hard Delete)

**Permissions:** `ADMIN_USER_DELETE`

**Request Body:**

```json
{
  "reason": "GDPR deletion request",
  "hard_delete": false
}
```

**Validierung:**
- `reason`: String
- `hard_delete`: Boolean, default=false

**Response 200 OK:**

```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

**Business Rules:**
- Admin kann sich selbst NICHT löschen
- Admin kann andere Admins NICHT löschen (außer bei hard_delete=true)
- Soft Delete: Status = 'deleted', deleted_at = NOW()
- Hard Delete: Permanente Löschung aus DB (CASCADE)

**Fehlercodes:**
- `403 Forbidden` - Versuch, sich selbst oder anderen Admin zu löschen
- `404 Not Found` - Benutzer nicht gefunden

**Audit Log:** `admin.users.delete` (Severity: `critical`)

---

#### 3.3.8 POST /api/v1/admin/users/{user_id}/verify-creator

**Beschreibung:** Creator als verifiziert markieren

**Permissions:** `ADMIN_USER_WRITE`

**Request Body:**

```json
{
  "verified": true,
  "reason": "Quality content creator"
}
```

**Response 200 OK:**

```json
{
  "success": true,
  "message": "Creator verified successfully"
}
```

**Business Rules:**
- Nur Benutzer mit Rolle 'creator' können verifiziert werden

**Fehlercodes:**
- `400 Bad Request` - Benutzer ist kein Creator
- `404 Not Found` - Benutzer nicht gefunden

**Audit Log:** `admin.users.verify_creator` (Severity: `medium`)

---

## 4. Backend-Architektur

### 4.1 Dateistruktur

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py                 # Blueprint-Registrierung (GEÄNDERT)
│   │   └── admin_users.py              # Admin User Management Routes (NEU)
│   ├── models/
│   │   └── admin.py                    # Pydantic Models (NEU)
│   ├── repositories/
│   │   ├── user_repository.py          # User Data Access (ERWEITERT)
│   │   └── token_repository.py         # Token Operations (ERWEITERT)
│   ├── services/
│   │   └── audit_service.py            # Audit Logging (ERWEITERT)
│   └── security/
│       └── permissions.py              # RBAC Permissions (VORHANDEN)
└── migrations/
    └── 043_extend_audit_logs.sql       # Audit Logs Extension (NEU)
```

### 4.2 Blueprint-Registrierung

**Datei:** `app/api/__init__.py`

```python
from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import routes after blueprint creation
from app.api import admin_users  # NEU: Admin User Management

__all__ = ['api_v1']
```

### 4.3 Route-Handler

**Datei:** `app/api/admin_users.py` (707 Zeilen)

**Aufbau:**
- Imports (auth, permissions, models, repositories, services)
- 8 Route-Handler-Funktionen
- Validierung mit Pydantic
- Repository-Delegation
- Audit Logging
- Error Handling

**Middleware-Stack pro Request:**
```
@api_v1.route('/admin/users/<user_id>/ban', methods=['POST'])
@token_required                        # JWT-Validierung
@require_permission(ADMIN_USER_WRITE)  # RBAC Permission
def admin_ban_user(user_id: str):
    # 1. Get current user
    current_user = get_current_user()

    # 2. Validate request body
    ban_request = BanUserRequest(**data)

    # 3. Business logic checks
    # 4. Repository call
    # 5. Audit logging
    # 6. Response
```

### 4.4 Pydantic Models

**Datei:** `app/models/admin.py` (215 Zeilen)

**Enums:**
- `UserRole` - 9 Rollen (free, premium, creator, teacher, school, company, support, moderator, admin)
- `UserStatus` - 4 Status (active, suspended, banned, deleted)

**Request Models:**
- `RoleChangeRequest` - Rollenwechsel
- `BanUserRequest` - Benutzersperre (mit Custom Validator für duration/permanent)
- `GrantTokensRequest` - Token-Gewährung
- `ModerateContentRequest` - Content-Moderation (Phase 2)

**Response Models:**
- `UserListItem` - User in Liste
- `UserListResponse` - Paginierte User-Liste
- `SubscriptionInfo` - Abo-Informationen
- `TokenInfo` - Token-Wallet-Info
- `UserDetailResponse` - Detaillierte User-Info
- `AdminActionResponse` - Generische Action Response
- `AuditLogEntry` - Audit Log Eintrag
- `AuditLogListResponse` - Audit Log Liste
- `SystemStats` - System-Statistiken
- `DashboardStats` - Dashboard-Daten

### 4.5 Repository-Methoden

**Datei:** `app/repositories/user_repository.py` (ERWEITERT: +445 Zeilen)

**Neue Admin-Methoden:**

```python
@classmethod
def admin_list_users(
    cls,
    page: int = 1,
    per_page: int = 50,
    role: Optional[str] = None,
    search: Optional[str] = None,
    status: str = 'active',
    sort: str = 'created_at',
    order: str = 'desc'
) -> Dict:
    """
    Liste alle Benutzer mit Pagination und Filtern

    Returns:
        Dict mit 'users' und 'pagination'
    """

@classmethod
def admin_get_user_details(cls, user_id: str) -> Optional[Dict]:
    """
    Hole detaillierte User-Informationen inkl.:
    - Subscription
    - Token Wallet
    - Course Counts
    - Login History (letzte 10)
    - Ban History (letzte 5)
    """

@classmethod
def admin_change_role(cls, user_id: str, new_role: str, changed_by: str) -> bool:
    """Ändere Benutzerrolle"""

@classmethod
def admin_ban_user(
    cls,
    user_id: str,
    reason: str,
    banned_until: Optional[datetime],
    banned_by: str
) -> bool:
    """Sperre Benutzer (temporär oder permanent)"""

@classmethod
def admin_unban_user(cls, user_id: str, unbanned_by: str) -> bool:
    """Hebe Benutzersperre auf"""

@classmethod
def admin_delete_user(
    cls,
    user_id: str,
    reason: str,
    deleted_by: str,
    hard_delete: bool = False
) -> bool:
    """Lösche Benutzer (Soft/Hard Delete)"""

@classmethod
def admin_verify_creator(
    cls,
    user_id: str,
    verified: bool,
    verified_by: str
) -> bool:
    """Verifiziere Creator"""
```

**Datei:** `app/repositories/token_repository.py` (ERWEITERT: +64 Zeilen)

```python
@classmethod
def admin_grant_tokens(
    cls,
    user_id: str,
    amount: int,
    reason: str,
    granted_by: str
) -> Optional[int]:
    """
    Gewähre Tokens an Benutzer (Admin-Only)

    - Erstellt Wallet falls notwendig
    - Nutzt change_balance() für transaktionale Sicherheit
    - Speichert Transaktion
    - Gibt neuen Balance zurück
    """
```

### 4.6 Audit Service

**Datei:** `app/services/audit_service.py` (ERWEITERT: +58 Zeilen)

**Neue Methode:**

```python
@staticmethod
def log_action(
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    severity: str = 'info'
):
    """
    Convenience-Wrapper für Admin-Aktionen

    Maps severity levels:
    - info -> Severity.INFO
    - warning/medium -> Severity.WARNING
    - high -> Severity.ERROR
    - critical -> Severity.CRITICAL

    Auto-bestimmt event_category basierend auf action:
    - admin.* -> ADMIN_ACTION
    - delete/update/create -> DATA_MODIFICATION
    - view/list/read -> DATA_ACCESS
    """
```

**Bestehende Methoden:**
- `log_event()` - Hauptmethode für alle Audit Logs
- `log_login_success()`, `log_login_failed()`, `log_logout()` - Auth Events
- `log_permission_denied()` - Authorization
- `log_2fa_enabled()`, `log_2fa_disabled()` - 2FA
- `get_user_audit_logs()`, `get_failed_login_attempts()` - Query Methods

---

## 5. Frontend-Architektur

### 5.1 Status

**⚠️ NICHT IMPLEMENTIERT**

Frontend-Implementation ist Teil der ausstehenden Aufgaben.

### 5.2 Geplante Struktur

```
frontend/
├── src/
│   ├── pages/
│   │   └── admin/
│   │       ├── AdminUsersPage.vue      # User Management Dashboard
│   │       ├── AdminUserDetailPage.vue # User Detail View
│   │       └── AdminLayout.vue         # Admin Layout (vorhanden)
│   ├── components/
│   │   └── admin/
│   │       ├── UserListTable.vue       # User Table Component
│   │       ├── UserDetailCard.vue      # User Info Card
│   │       ├── UserActionsMenu.vue     # Action Buttons/Menu
│   │       ├── BanUserModal.vue        # Ban Dialog
│   │       ├── GrantTokensModal.vue    # Grant Tokens Dialog
│   │       └── RoleChangeModal.vue     # Role Change Dialog
│   ├── stores/
│   │   └── adminUsers.js               # Pinia Store (Admin Users)
│   └── services/
│       └── api/
│           └── adminApi.js             # Admin API Service
```

### 5.3 Geplante Features

- **User List View** mit Pagination, Filterung, Suche
- **User Detail View** mit Tabs (Info, Subscription, Tokens, Courses, History)
- **Action Modals** für Ban, Unban, Role Change, Token Grant
- **Permissions-basierte UI** (Buttons nur sichtbar mit entsprechenden Permissions)
- **Real-time Updates** bei Status-Änderungen

---

## 6. Datenbank-Änderungen

### 6.1 Migration: 043_extend_audit_logs.sql

**Datum:** 2025-11-19
**Zweck:** Erweitere `audit_logs` Tabelle für umfassendes Admin Audit Logging

**Neue Spalten:**

| Spalte          | Typ          | Nullable | Default | Beschreibung                              |
|-----------------|--------------|----------|---------|-------------------------------------------|
| event_category  | VARCHAR(50)  | Yes      | -       | Event-Kategorie (auth, admin, data, ...)  |
| user_email      | VARCHAR(255) | Yes      | -       | User Email (bei fehlgeschlagenen Logins)  |
| user_role       | VARCHAR(50)  | Yes      | -       | User-Rolle zum Zeitpunkt der Aktion      |
| session_id      | VARCHAR(255) | Yes      | -       | Session/JWT ID                            |
| description     | TEXT         | Yes      | -       | Human-readable Beschreibung               |
| success         | BOOLEAN      | No       | TRUE    | Ob Aktion erfolgreich war                 |
| error_message   | TEXT         | Yes      | -       | Fehlermeldung bei Fehlschlag              |

**Gelöschte Constraints:**
- `chk_audit_action` - Constraint entfernt, um beliebige Actions zu erlauben (z.B. `admin.users.ban`)

**Neue Indizes:**

```sql
CREATE INDEX idx_audit_logs_event_category
  ON audit_logs(event_category, created_at DESC);

CREATE INDEX idx_audit_logs_user_email
  ON audit_logs(user_email, created_at DESC)
  WHERE user_email IS NOT NULL;

CREATE INDEX idx_audit_logs_session
  ON audit_logs(session_id)
  WHERE session_id IS NOT NULL;

CREATE INDEX idx_audit_logs_success
  ON audit_logs(success, created_at DESC)
  WHERE success = FALSE;
```

**Ausführung:**

```bash
python backend/run_migration_043.py
```

**Rollback:**

```sql
-- Kein Rollback vorgesehen, da nur Spalten hinzugefügt wurden
-- Bei Bedarf: DROP COLUMN für jede neue Spalte
```

### 6.2 Bestehende Tabellen (Genutzt)

**Tabelle: users**

Relevante Spalten für Admin Operations:
- `user_id` (UUID, PK)
- `email` (VARCHAR, UNIQUE)
- `role_id` (INT, FK → roles)
- `status` (VARCHAR: active, suspended, banned, deleted)
- `banned_until` (TIMESTAMPTZ, Nullable)
- `creator_verified` (BOOLEAN)
- `creator_verified_at` (TIMESTAMPTZ, Nullable)
- `deleted_at` (TIMESTAMPTZ, Nullable)

**Tabelle: token_wallets**

- `wallet_id` (SERIAL, PK)
- `user_id` (UUID, FK → users)
- `balance` (INT)
- `total_granted` (INT)
- `total_purchased` (INT)
- `total_used` (INT)

**Tabelle: token_transactions**

- `transaction_id` (BIGSERIAL, PK)
- `wallet_id` (INT, FK → token_wallets)
- `user_id` (UUID, FK → users)
- `type` (VARCHAR: grant, consumption, purchase)
- `amount` (INT)
- `balance_after` (INT)
- `description` (TEXT)

**Tabelle: subscriptions**

- `subscription_id` (BIGSERIAL, PK)
- `user_id` (UUID, FK → users)
- `plan_id` (UUID, FK → subscription_plans)
- `status` (VARCHAR: active, cancelled, expired)
- `end_date` (TIMESTAMPTZ)
- `auto_renew` (BOOLEAN)

---

## 7. Sicherheitsaspekte

### 7.1 ISO 27001:2013 & OWASP ASVS 4.0 Compliance

#### 7.1.1 Authentication (ASVS V2)

✅ **V2.1.1:** JWT-basierte Authentifizierung
✅ **V2.1.3:** Token Expiry (1 Stunde Access Token, 30 Tage Refresh Token)
✅ **V2.1.11:** JWT-Token Blacklist in Redis

**Implementation:**
```python
@token_required  # Middleware validiert JWT
def admin_list_users():
    current_user = get_current_user()  # Extrahiert User aus g.current_user
```

#### 7.1.2 Authorization (ASVS V4)

✅ **V4.1.1:** RBAC-basierte Zugriffskontrolle
✅ **V4.1.2:** Permission-basierte Endpunkte
✅ **V4.1.3:** Least Privilege Prinzip
✅ **V4.1.5:** Deny by Default

**Permissions:**

| Permission           | Beschreibung                              |
|----------------------|-------------------------------------------|
| ADMIN_USER_READ      | Benutzer anzeigen                         |
| ADMIN_USER_WRITE     | Benutzer ändern (Rolle, Ban, Tokens)      |
| ADMIN_USER_DELETE    | Benutzer löschen                          |

**Implementation:**
```python
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_ban_user(user_id: str):
    # Nur Admins mit ADMIN_USER_WRITE Permission
```

**Business Rule Enforcement:**
```python
# Admin kann sich selbst nicht bannen
if user_id == current_user['user_id']:
    return jsonify({'error': 'Forbidden'}), 403

# Admin kann andere Admins nicht bannen
if target_user.get('role') == 'admin':
    return jsonify({'error': 'Cannot ban admin users'}), 403
```

#### 7.1.3 Input Validation (ASVS V5)

✅ **V5.1.1:** Whitelist-basierte Input-Validierung
✅ **V5.1.3:** Type Enforcement
✅ **V5.1.4:** Length Constraints
✅ **V5.1.5:** Custom Validators

**Pydantic Validation:**

```python
class BanUserRequest(BaseModel):
    reason: str = Field(..., min_length=10, max_length=1000)
    duration_days: Optional[int] = Field(None, ge=1, le=365)
    permanent: bool = Field(default=False)

    @validator('duration_days')
    def validate_duration(cls, v, values):
        # Custom Logic: permanent und duration schließen sich aus
        if values.get('permanent') and v is not None:
            raise ValueError('Cannot set duration_days for permanent bans')
        return v
```

**SQL Injection Prevention:**
```python
# Parameterisierte Queries (psycopg)
query = "SELECT * FROM users WHERE user_id = %s"
result = fetch_one(query, (user_id,))  # ✅ Sicher

# NIEMALS:
query = f"SELECT * FROM users WHERE user_id = '{user_id}'"  # ❌ Unsicher
```

#### 7.1.4 Audit Logging (ISO 27001 A.12.4.1)

✅ **A.12.4.1:** Event Logging
✅ **A.12.4.2:** Protection of Log Information
✅ **A.12.4.3:** Administrator and Operator Logs
✅ **A.12.4.4:** Clock Synchronisation

**Logged Events:**
- Alle Admin-Aktionen (Ban, Unban, Role Change, Token Grant, Delete)
- User-ID, Action, Resource, Timestamp
- Request-Context (IP, User Agent, Session)
- Success/Failure Status
- Details (Begründungen, Beträge, etc.)

**Severity Levels:**
- `info` - Normale Operationen (List, View)
- `warning` - Potenzielle Sicherheitsprobleme
- `high` - Wichtige Änderungen (Role Change, Unban)
- `critical` - Kritische Aktionen (Ban, Delete)

**Log-Schutz:**
- Sensible Daten (Passwörter, Tokens) werden automatisch gesanitized
- Audit Logs sind append-only
- Nur Admins mit ADMIN_AUDIT_READ können Logs lesen

#### 7.1.5 Rate Limiting (OWASP API Security Top 10)

✅ **API4:2023 Unrestricted Resource Consumption**

**Configured Limits:**
- Admin APIs: 200 Requests / Minute
- Granulare Limits pro Endpoint möglich

```python
# In API Gateway Middleware
RATE_LIMITS = {
    '/api/v1/admin/*': '200 per minute'
}
```

#### 7.1.6 Data Protection (GDPR Art. 32)

✅ **Art. 32(1)(a):** Pseudonymisation
✅ **Art. 32(1)(b):** Confidentiality
✅ **Art. 32(1)(c):** Integrity
✅ **Art. 32(1)(d):** Availability

**Maßnahmen:**
- UUIDs statt sequenzielle IDs
- Passwort-Hashes niemals in Responses
- Soft Delete für GDPR-Konformität
- Hard Delete nur nach expliziter Anfrage

**Sensitive Data Handling:**
```python
# Passwort-Hash wird automatisch entfernt
if user:
    user.pop('password_hash', None)
```

### 7.2 Sicherheitsrisiken & Mitigations

| Risiko                      | Severity | Mitigation                                     |
|-----------------------------|----------|------------------------------------------------|
| Privilege Escalation        | Critical | RBAC + Business Rules (kein Self-Modify)       |
| Mass Assignment             | High     | Pydantic whitelisting, keine direkten Updates  |
| Broken Authentication       | Critical | JWT + Token Blacklist + Expiry                 |
| SQL Injection               | Critical | Parameterisierte Queries (psycopg)             |
| IDOR                        | High     | Permission Checks + User ID Validation         |
| Mass Enumeration            | Medium   | Rate Limiting                                  |
| Audit Log Tampering         | High     | Append-only Logs, Admin-only Access            |

---

## 8. Changelog

### 8.1 Neue Dateien

| Datei                                | Zeilen | Beschreibung                                |
|--------------------------------------|--------|---------------------------------------------|
| `app/api/admin_users.py`             | 707    | Admin User Management Routes (8 Endpoints)  |
| `app/models/admin.py`                | 215    | Pydantic Validation Models                  |
| `migrations/043_extend_audit_logs.sql` | 115  | Audit Logs Tabellen-Erweiterung            |
| `run_migration_043.py`               | 54     | Migration Runner Script                     |
| `check_audit_logs_columns.py`        | 20     | DB Schema Verifikation Script               |

**Gesamt:** 5 neue Dateien, 1111 Zeilen Code

### 8.2 Geänderte Dateien

| Datei                                | Änderung | Zeilen | Beschreibung                                |
|--------------------------------------|----------|--------|---------------------------------------------|
| `app/api/__init__.py`                | +1 Zeile | 48     | Blueprint-Import für admin_users            |
| `app/services/audit_service.py`      | +58      | 488    | log_action() Methode für Admin-Aktionen     |
| `app/repositories/user_repository.py`| +445     | 952    | 7 neue Admin-Methoden                       |
| `app/repositories/token_repository.py`| +64     | 516    | admin_grant_tokens() Methode                |

**Gesamt:** 4 geänderte Dateien, +568 Zeilen Code

### 8.3 Breaking Changes

**Keine Breaking Changes.**

Alle Änderungen sind rückwärtskompatibel:
- Neue Endpoints unter `/api/v1/admin/users/*`
- Neue Spalten in `audit_logs` (nullable)
- Neue Methoden in bestehenden Repositories
- Keine Änderungen an bestehenden APIs

### 8.4 Migrationsschritte

1. **Datenbank-Migration ausführen:**
   ```bash
   cd backend
   python run_migration_043.py
   ```

2. **Backend neu starten:**
   ```bash
   # Bestehende Prozesse beenden
   # Neu starten
   python run.py
   ```

3. **Verifizierung:**
   ```bash
   # Prüfe ob Routen registriert sind
   curl http://localhost:5000/api/v1/admin/users
   # Erwarteter Response: 401 Unauthorized (ohne Token)
   ```

4. **Frontend-Integration (ausstehend):**
   - Admin User Management Pages implementieren
   - Pinia Store erstellen
   - API Service integrieren

---

## 9. Edge Cases & Erweiterbarkeit

### 9.1 Edge Cases

#### 9.1.1 Gleichzeitige Modifikationen

**Problem:** Zwei Admins ändern gleichzeitig denselben User

**Lösung:** PostgreSQL Row-Level Locking
```sql
-- In Repository-Methoden:
SELECT * FROM users WHERE user_id = %s FOR UPDATE
```

**Status:** ❌ Nicht implementiert (Optimistic Locking ausreichend für Phase 1)

#### 9.1.2 Banned Admin versucht Login

**Problem:** Gesperrter Admin versucht sich einzuloggen

**Lösung:** Status-Prüfung in `authenticate()` Methode
```python
if user.get('status') != 'active':
    return None  # Login abgelehnt
```

**Status:** ✅ Implementiert in `user_repository.py:172`

#### 9.1.3 Token Grant an gelöschten User

**Problem:** Admin gewährt Tokens an soft-deleted User

**Lösung:** Status-Prüfung vor Grant
```python
target_user = UserRepository.find_by_id(user_id)
if not target_user or target_user['status'] == 'deleted':
    return 404
```

**Status:** ⚠️ Teilweise implementiert (find_by_id prüft nicht deleted_at)

**Empfehlung:** Filter in `find_by_id()` für deleted_at hinzufügen

#### 9.1.4 Creator-Verifizierung für Nicht-Creator

**Problem:** Admin versucht Non-Creator zu verifizieren

**Lösung:** Rolle-Prüfung vor Verifikation
```python
if target_user.get('role') != 'creator':
    return jsonify({'error': 'User is not a creator'}), 400
```

**Status:** ✅ Implementiert in `admin_users.py:664`

#### 9.1.5 Ban-Expire Automatisierung

**Problem:** Temporäre Bans müssen manuell aufgehoben werden

**Lösung:** Cronjob/Celery Task zum Auto-Unban
```python
# Celery Task (täglich)
@celery.task
def auto_unban_expired_users():
    query = """
        UPDATE users
        SET status = 'active', banned_until = NULL
        WHERE status = 'banned'
          AND banned_until < NOW()
    """
    execute_query(query)
```

**Status:** ❌ Nicht implementiert

**Empfehlung:** Als Celery Periodic Task in Phase 3 implementieren

### 9.2 Limitierungen

| Limitierung                        | Beschreibung                                          | Workaround                          |
|------------------------------------|-------------------------------------------------------|-------------------------------------|
| Keine Bulk-Operationen             | Keine Multi-User-Aktionen (Bulk Ban, Bulk Delete)    | Mehrfache API-Calls vom Frontend    |
| Keine User-Impersonation           | Admin kann nicht als User einloggen                   | Separate Feature in Phase 2         |
| Keine Email-Benachrichtigung       | Banned/Unbanned User werden nicht per Email informiert| Email-Service in Phase 3            |
| Keine Advanced Filters             | Nur basic Filterung (Role, Status, Search)            | Elasticsearch in Phase 4            |
| Keine Soft-Delete Wiederherstellung| Soft-deleted User können nicht reaktiviert werden     | Separate Restore-Endpoint           |

### 9.3 Empfehlungen für zukünftige Erweiterungen

#### Phase 2: Content Moderation & Feature Flags

- **User Export:** CSV/Excel Export von Userlisten
- **Bulk Actions:** Multi-User-Operationen (Bulk Ban, Bulk Role Change)
- **Email Notifications:** Benachrichtigung bei Ban/Unban
- **Activity Timeline:** Erweiterte User-Activity-Logs

#### Phase 3: Finance & Billing

- **Payment History:** Integration mit Billing-System
- **Refund Management:** Automatische Rückerstattung bei Bans
- **Revenue Reports:** Pro-User-Umsatzberichte

#### Phase 4: Advanced Features

- **User Impersonation:** Admin-Login als User (mit Audit Log)
- **Advanced Search:** Elasticsearch-basierte Suche
- **User Segmentation:** Cohort-Analysen, User-Gruppen
- **Automated Actions:** Rules-Engine für automatische Bans bei Verstößen

---

## 10. Datenfluss-Diagramme

### 10.1 User Ban Flow (PlantUML)

```plantuml
@startuml Admin User Ban Flow

actor Admin
participant "Frontend" as FE
participant "API Gateway" as GW
participant "admin_users.py" as Route
participant "UserRepository" as UserRepo
participant "AuditService" as Audit
database "PostgreSQL" as DB

Admin -> FE: Click "Ban User"
FE -> FE: Show Ban Modal
Admin -> FE: Enter Reason, Duration
FE -> GW: POST /api/v1/admin/users/{id}/ban\nAuthorization: Bearer {token}

GW -> GW: Validate JWT
GW -> Route: Forward Request

Route -> Route: @token_required\nExtract current_user
Route -> Route: @require_permission\n(ADMIN_USER_WRITE)

Route -> Route: Validate BanUserRequest\n(Pydantic)

Route -> Route: Check: user_id != current_user
Route -> UserRepo: find_by_id(user_id)
UserRepo -> DB: SELECT * FROM users\nWHERE user_id = ?
DB --> UserRepo: User Data
UserRepo --> Route: target_user

Route -> Route: Check: target_user.role != 'admin'
Route -> Route: Calculate banned_until\n(NOW + duration_days)

Route -> UserRepo: admin_ban_user(\n  user_id,\n  reason,\n  banned_until,\n  banned_by\n)

UserRepo -> DB: UPDATE users\nSET status='banned',\nbanned_until=?, updated_at=NOW()\nWHERE user_id=?
DB --> UserRepo: Success

UserRepo --> Route: True

Route -> Audit: log_action(\n  user_id=current_user,\n  action='admin.users.ban',\n  resource_type='user',\n  resource_id=user_id,\n  details={'reason', 'duration'},\n  severity='critical'\n)

Audit -> DB: INSERT INTO audit_logs\n(event_type, action, user_id, ...)
DB --> Audit: log_id

Audit --> Route: log_id

Route -> GW: JSON Response:\n{\n  "success": true,\n  "banned_until": "..."\n}

GW -> FE: 200 OK
FE -> Admin: Show Success Message

@enduml
```

### 10.2 Permission Check Flow

```
┌─────────────┐
│   Request   │
│  (JWT Token)│
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  @token_required     │ ◄── Middleware
│  - Decode JWT        │
│  - Check Blacklist   │
│  - Extract user_data │
│  - Set g.current_user│
└──────┬───────────────┘
       │ Success
       ▼
┌──────────────────────────────┐
│  @require_permission(...)    │ ◄── Decorator
│  - Get current_user from g   │
│  - Check user.permissions    │
│  - Compare with required     │
└──────┬───────────────────────┘
       │ Has Permission
       ▼
┌──────────────────┐
│  Route Handler   │
│  - Business Logic│
│  - Repository    │
│  - Audit Log     │
└──────────────────┘
```

### 10.3 Audit Log Data Flow

```
┌──────────────────┐
│  Admin Action    │
│  (Ban, Delete, ...)│
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│  Route Handler               │
│  - Perform Action            │
│  - Call Repository Method    │
└────────┬─────────────────────┘
         │ After Success
         ▼
┌──────────────────────────────┐
│  AuditService.log_action()   │
│  - user_id (Admin)           │
│  - action (admin.users.ban)  │
│  - resource_type (user)      │
│  - resource_id (target_user) │
│  - details (reason, etc.)    │
│  - severity (critical)       │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  AuditService.log_event()    │
│  - Map severity              │
│  - Determine event_category  │
│  - Auto-detect IP, User Agent│
│  - Sanitize metadata         │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  INSERT INTO audit_logs      │
│  - event_type                │
│  - event_category            │
│  - user_id                   │
│  - user_email                │
│  - user_role                 │
│  - session_id                │
│  - ip_address                │
│  - user_agent                │
│  - resource_type             │
│  - resource_id               │
│  - action                    │
│  - description               │
│  - metadata (JSON)           │
│  - success                   │
│  - severity                  │
│  - created_at                │
└──────────────────────────────┘
```

---

## 11. Zusammenfassung

### 11.1 Implementierungsstatus

| Komponente               | Status | Beschreibung                                    |
|--------------------------|--------|-------------------------------------------------|
| Backend API              | ✅     | 8 Endpoints implementiert und registriert      |
| Pydantic Models          | ✅     | Vollständige Request/Response Validierung       |
| Repository Layer         | ✅     | 7 User + 1 Token Admin-Methoden                |
| Audit Logging            | ✅     | Erweitert mit log_action() Methode              |
| Database Migration       | ✅     | audit_logs Tabelle erweitert                    |
| Security (RBAC)          | ✅     | Permission-basiert, Self-Modify-Protection      |
| Frontend Implementation  | ❌     | Ausstehend                                      |
| Email Notifications      | ❌     | Ausstehend (Phase 3)                            |
| Bulk Operations          | ❌     | Ausstehend (Phase 2)                            |

### 11.2 Code-Statistiken

- **Neue Dateien:** 5 (1111 Zeilen)
- **Geänderte Dateien:** 4 (+568 Zeilen)
- **Gesamt:** 1679 Zeilen neuer/geänderter Code
- **Tests:** 0 (Unit-Tests ausstehend)
- **Dokumentation:** 1 (dieses Dokument)

### 11.3 Nächste Schritte

1. **Frontend Implementation:**
   - AdminUsersPage.vue erstellen
   - Pinia Store (adminUsers.js) implementieren
   - Admin API Service integrieren
   - UI-Komponenten für User-Aktionen

2. **Testing:**
   - Unit-Tests für Repository-Methoden
   - Integration-Tests für API-Endpoints
   - E2E-Tests für Admin User Flows

3. **Optimierungen:**
   - Celery Task für Auto-Unban
   - Email-Benachrichtigungen
   - Erweiterte Filter & Suche
   - Bulk-Operationen

4. **Dokumentation:**
   - API-Dokumentation in Swagger/OpenAPI
   - Benutzerhandbuch für Admins
   - Runbook für Operations

---

**Ende der Dokumentation**

*Erstellt von: Claude Code*
*Letzte Aktualisierung: 2025-11-19*
*Compliance: ISO/IEC 25010, ISO/IEC/IEEE 26514, OWASP ASVS 4.0*
