# 02 – API-Spezifikation (GBA Edition)

**Version:** 2.0 (Group-Based Architecture)
**Stand:** 2026-01-25
**Status:** Production Ready

---

## Überblick

Dieses Dokument definiert die REST-API des LSX Lernsystems mit **Group-Based Architecture (GBA)** für flexible Zugriffskontrolle.

Die API ist **REST-basiert** (JSON), folgt klaren Namenskonventionen und unterstützt:

- 👥 **Benutzerverwaltung & Authentifizierung**
- 🔐 **Gruppen-basierte Zugriffskontrolle (GBA)**
- 📚 **Kurssystem**
- 📖 **Lernmodule & Lernmethoden (12 LMs)**
- 📝 **Prüfungssystem**
- 🤖 **KI-Pipeline**
- 🌍 **Übersetzungssystem**
- 📊 **Dashboard & Widgets**
- 🎥 **LiveRoom (WebRTC)**
- 💰 **Token & Billing**
- 👥 **Community & Social Network**

> Alle Endpunkte sind **versioniert** (v1) und folgen **GBA Berechtigungsmodell**.

---

## 1. API-Standards

### 1.1 📋 Format-Konventionen

| Standard | Wert |
|----------|------|
| 🌐 **Protokoll** | REST JSON |
| 📝 **Encoding** | UTF-8 |
| 🔤 **Naming** | snake_case |
| 🔧 **Partial Update** | PATCH |
| ➕ **Aktionen** | POST |
| 👁️ **Lesezugriffe** | GET |
| 🗑️ **Löschen** | DELETE |

---

### 1.2 🔐 Authentifizierung & JWT-Token

**JWT-basierte Authentifizierung mit Access & Refresh Token**

#### 📨 Request Header

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 🔑 Token-Struktur (JWT Payload)

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "groups": [
    {
      "id": 1,
      "name": "system-admin",
      "slug": "system_admin",
      "type": "system",
      "permissions": ["admin:system", "admin:organisations", "manage:users", "manage:groups"]
    },
    {
      "id": 5,
      "name": "teacher",
      "slug": "teacher",
      "type": "system",
      "permissions": ["manage:courses", "manage:lessons", "view:analytics"]
    }
  ],
  "exp": 1234567890,
  "iat": 1234567800
}
```

#### 🎫 Token-Typen

| Token | Lebensdauer | Verwendung |
|-------|-------------|-----------|
| 🎫 **Access Token** | 15 Minuten | API-Requests |
| 🔄 **Refresh Token** | 7 Tage | Token-Erneuerung |

---

### 1.3 ❌ Fehlerformat

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "User does not have required permission",
    "details": {
      "required_permission": "admin:system",
      "user_permissions": ["manage:courses", "view:analytics"]
    }
  }
}
```

#### 🚨 HTTP Status Codes

| Code | Bedeutung | Verwendung |
|------|-----------|-----------|
| 200 | ✅ OK | Erfolg |
| 201 | ✅ Created | Ressource erstellt |
| 400 | ❌ Bad Request | Ungültige Anfrage |
| 401 | 🔒 Unauthorized | Nicht authentifiziert |
| 403 | 🚫 Forbidden | Keine Berechtigung (GBA-Check fehlgeschlagen) |
| 404 | 🔍 Not Found | Ressource nicht gefunden |
| 429 | ⏱️ Too Many Requests | Rate Limit überschritten |
| 500 | 💥 Internal Server Error | Server-Fehler |

---

### 1.4 ✅ Erfolgformat

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Example",
    "created_at": "2024-11-14T10:30:00Z"
  },
  "meta": {
    "timestamp": "2024-11-14T10:30:00Z"
  }
}
```

---

## 2. Auth & Benutzer

### 2.1 ➕ POST `/api/v1/auth/register`

**Registriert einen neuen Benutzer**

#### Request Body

```json
{
  "email": "test@example.com",
  "password": "SecurePass123!",
  "firstname": "John",
  "lastname": "Doe",
  "language": "de"
}
```

#### Response (201 Created)

```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "test@example.com",
    "groups": [
      {
        "id": 3,
        "name": "student",
        "slug": "student",
        "permissions": ["view:courses", "enroll:courses"]
      }
    ]
  }
}
```

---

### 2.2 🔑 POST `/api/v1/auth/login`

**Authentifiziert einen Benutzer und gibt GBA-Token zurück**

#### Request Body

```json
{
  "email": "test@example.com",
  "password": "SecurePass123!"
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "user_id": "uuid",
      "email": "test@example.com",
      "firstname": "John",
      "lastname": "Doe",
      "groups": [
        {
          "id": 3,
          "name": "student",
          "slug": "student",
          "type": "system",
          "permissions": ["view:courses", "enroll:courses"]
        }
      ]
    }
  }
}
```

---

### 2.3 👤 GET `/api/v1/users/me`

**Gibt das eigene Profil mit aktuellen Gruppen und Berechtigungen zurück**

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "test@example.com",
    "firstname": "John",
    "lastname": "Doe",
    "language": "de",
    "groups": [
      {
        "id": 3,
        "name": "student",
        "slug": "student",
        "permissions": ["view:courses", "enroll:courses"]
      }
    ],
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

---

### 2.4 🔄 POST `/api/v1/auth/refresh`

**Erneuert Access Token**

#### Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "access_token": "new_access_token..."
  }
}
```

---

### 2.5 🚪 POST `/api/v1/auth/logout`

**Invalidiert Token**

---

### 2.6 🎨 User Profile – Theme Preference

#### 👁️ GET `/api/v1/profile/theme`

**Gibt die aktuelle Theme-Einstellung zurück**

#### 🎨 PATCH `/api/v1/profile/theme`

**Aktualisiert die Theme-Einstellung**

---

## 3. Gruppen-Management (GBA)

### 🔑 Group-Based Architecture (GBA) – Berechtigungsmodell

**Endpunkte für Group-Management (Admin-Panel)**

| Endpunkt | Methode | Beschreibung | Auth |
|----------|---------|-------------|------|
| `/api/v1/admin/groups` | GET | Liste aller Gruppen mit Statistiken | `admin:system` |
| `/api/v1/admin/groups/{id}` | GET | Details einer Gruppe + Permissions | `admin:system` |
| `/api/v1/admin/groups` | POST | Neue Gruppe erstellen | `admin:system` |
| `/api/v1/admin/groups/{id}` | PUT | Gruppe aktualisieren | `admin:system` |
| `/api/v1/admin/groups/{id}` | DELETE | Gruppe löschen | `admin:system` |
| `/api/v1/admin/groups/{id}/members` | GET | Mitglieder einer Gruppe | `admin:system` |
| `/api/v1/admin/groups/{id}/members` | POST | Benutzer zur Gruppe hinzufügen | `admin:system` |
| `/api/v1/admin/groups/{id}/members/{user_id}` | DELETE | Benutzer aus Gruppe entfernen | `admin:system` |
| `/api/v1/admin/groups/{id}/permissions` | GET | Berechtigungen der Gruppe | `admin:system` |
| `/api/v1/admin/groups/{id}/permissions` | POST | Permissions zuweisen | `admin:system` |

---

### 3.1 📋 GET `/api/v1/admin/groups`

**Liste aller Gruppen mit Filterung und Statistiken**

**Auth:** `@require_permission('admin:system')`

#### Query Parameter

| Parameter | Typ | Beschreibung |
|-----------|-----|-------------|
| `type` | string | Filter: system, organization, custom |
| `search` | string | Suche in group_name oder description |
| `include_members` | boolean | Mitgliederzahlen mit ausgeben |
| `include_permissions` | boolean | Permission-Assignments mit ausgeben |

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "groups": [
      {
        "id": 1,
        "name": "system-admin",
        "slug": "system_admin",
        "description": "System administrator with full access",
        "group_type": "system",
        "frontend_role": "Admin",
        "is_active": true,
        "created_at": "2025-01-10T10:00:00Z",
        "member_count": 2,
        "permission_count": 50
      },
      {
        "id": 2,
        "name": "teacher",
        "slug": "teacher",
        "description": "Teachers can manage courses and view analytics",
        "group_type": "system",
        "frontend_role": "Teacher",
        "is_active": true,
        "created_at": "2025-01-10T10:00:00Z",
        "member_count": 25,
        "permission_count": 15
      },
      {
        "id": 3,
        "name": "student",
        "slug": "student",
        "description": "Students can view and enroll in courses",
        "group_type": "system",
        "frontend_role": "Student",
        "is_active": true,
        "created_at": "2025-01-10T10:00:00Z",
        "member_count": 5000,
        "permission_count": 5
      }
    ],
    "total": 3
  }
}
```

---

### 3.2 👁️ GET `/api/v1/admin/groups/{group_id}`

**Details einer Gruppe mit allen Permissions und Mitgliedern**

**Auth:** `@require_permission('admin:system')`

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "teacher",
    "slug": "teacher",
    "description": "Teachers can manage courses and view analytics",
    "group_type": "system",
    "frontend_role": "Teacher",
    "is_active": true,
    "created_at": "2025-01-10T10:00:00Z",
    "permissions": [
      {
        "id": 10,
        "permission_code": "manage:courses",
        "description": "Create, edit, and delete courses",
        "resource": "courses",
        "action": "manage"
      },
      {
        "id": 11,
        "permission_code": "manage:lessons",
        "description": "Create, edit, and delete lessons",
        "resource": "lessons",
        "action": "manage"
      },
      {
        "id": 20,
        "permission_code": "view:analytics",
        "description": "View course and user analytics",
        "resource": "analytics",
        "action": "read"
      }
    ],
    "member_count": 25,
    "created_by": "system"
  }
}
```

---

### 3.3 ➕ POST `/api/v1/admin/groups`

**Neue Gruppe erstellen**

**Auth:** `@require_permission('admin:system')`

#### Request Body

```json
{
  "name": "content-curator",
  "slug": "content_curator",
  "description": "Curates and approves user-generated content",
  "group_type": "custom",
  "frontend_role": "ContentCurator",
  "is_active": true
}
```

#### Response (201 Created)

```json
{
  "success": true,
  "data": {
    "id": 10,
    "name": "content-curator",
    "slug": "content_curator",
    "description": "Curates and approves user-generated content",
    "group_type": "custom",
    "frontend_role": "ContentCurator",
    "is_active": true,
    "created_at": "2025-01-12T15:00:00Z"
  }
}
```

---

### 3.4 🔐 POST `/api/v1/admin/groups/{group_id}/permissions`

**Permissions zu Gruppe zuweisen**

**Auth:** `@require_permission('admin:system')`

#### Request Body

```json
{
  "permission_ids": [10, 11, 20],
  "replace": false
}
```

**Parameter:**
- `permission_ids`: Liste von Permission-IDs aus `core.permissions`
- `replace`: `true` = Alle bisherigen Permissions ersetzen, `false` = Hinzufügen

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "permissions_assigned": 3,
    "total_permissions": 8,
    "group_id": 10
  }
}
```

---

### 3.5 👥 POST `/api/v1/admin/groups/{group_id}/members`

**Benutzer zur Gruppe hinzufügen**

**Auth:** `@require_permission('admin:system')`

#### Request Body

```json
{
  "user_ids": ["uuid-1", "uuid-2"],
  "member_role": "member"
}
```

**Parameter:**
- `user_ids`: Liste von Benutzer-IDs
- `member_role`: owner, moderator, oder member

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "added_count": 2,
    "group_id": 10,
    "total_members": 25
  }
}
```

---

### 3.6 🗑️ DELETE `/api/v1/admin/groups/{group_id}/members/{user_id}`

**Benutzer aus Gruppe entfernen**

**Auth:** `@require_permission('admin:system')`

---

## 4. Permissions (GBA Berechtigungen)

### 🔐 Permission-Codes

**Verfügbare Permission-Codes** (Beispiele):

| Permission Code | Beschreibung | Ressource |
|-----------------|-------------|-----------|
| `admin:system` | Full system admin access | system |
| `admin:organisations` | Manage all organizations | organisations |
| `manage:users` | Create/update/delete users | users |
| `manage:groups` | Create/update/delete groups | groups |
| `manage:courses` | Create/edit/delete courses | courses |
| `manage:lessons` | Create/edit/delete lessons | lessons |
| `view:analytics` | View analytics dashboards | analytics |
| `manage:billing` | Manage billing and tokens | billing |
| `moderate:content` | Moderate user-generated content | content |

---

### 4.1 📋 GET `/api/v1/admin/permissions`

**Liste aller verfügbaren Permissions**

**Auth:** `@require_permission('admin:system')`

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "permissions": [
      {
        "id": 1,
        "permission_code": "admin:system",
        "description": "Full system access",
        "resource": "system",
        "action": "admin"
      },
      {
        "id": 10,
        "permission_code": "manage:courses",
        "description": "Create, edit, and delete courses",
        "resource": "courses",
        "action": "manage"
      }
    ]
  }
}
```

---

## 5. Berechtigungsprüfung (API-Implementierung)

### 🔒 Permission-Decorators

**Backend-API nutzt Permission-Decorators zur Autorisierung:**

```python
# Beispiele:
@bp.route('/admin/users', methods=['GET'])
@require_permission('admin:system')
def get_users():
    """Only users with 'admin:system' permission"""
    pass

@bp.route('/courses', methods=['POST'])
@require_permission('manage:courses')
def create_course():
    """Only users with 'manage:courses' permission"""
    pass

@bp.route('/analytics', methods=['GET'])
@require_permission('view:analytics')
def view_analytics():
    """Only users with 'view:analytics' permission"""
    pass
```

**Berechtigungsprüfung erfolgt:**
1. Benutzer sendet JWT Token mit `groups` Claim
2. Decorator extrahiert erforderliche Permission aus Decorator-Parameter
3. Decorator prüft: Hat die Gruppe diese Permission? → `core.role_permissions`
4. Falls JA: Request wird verarbeitet (200/201/204)
5. Falls NEIN: 403 Forbidden wird zurückgegeben

---

## 6. Kurs-System

### 📚 Kurs-Management

| Endpunkt | Methode | Beschreibung | Auth |
|----------|---------|-------------|------|
| `/api/v1/courses` | GET | Liste aller Kurse | optional |
| `/api/v1/courses/{course_id}` | GET | Kurs-Details | optional |
| `/api/v1/courses` | POST | Kurs erstellen | `manage:courses` |
| `/api/v1/courses/{course_id}` | PATCH | Kurs aktualisieren | `manage:courses` |
| `/api/v1/courses/{course_id}/publish` | POST | Kurs veröffentlichen | `manage:courses` |

---

### 6.1 📋 GET `/api/v1/courses`

**Liste aller Kurse mit Filterung**

#### Query Parameter

| Parameter | Typ | Beschreibung |
|-----------|-----|-------------|
| `category` | integer | Kategorie-ID |
| `language` | string | de, en, pl, ... |
| `level` | string | beginner, intermediate, advanced |
| `page` | integer | Seite (Default: 1) |
| `limit` | integer | Ergebnisse pro Seite (Default: 20) |

#### Response (200 OK)

```json
{
  "success": true,
  "data": [
    {
      "course_id": "uuid",
      "title": "Network+ Komplettkurs",
      "description": "Vollständiger Kurs für CompTIA Network+",
      "level": "intermediate",
      "price": 39.99,
      "published": true
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "limit": 20
  }
}
```

---

### 6.2 ➕ POST `/api/v1/courses`

**Neuen Kurs erstellen**

**Auth:** `@require_permission('manage:courses')`

#### Request Body

```json
{
  "title": "Network+ Komplettkurs",
  "description": "Vollständiger Vorbereitungskurs",
  "category_id": 12,
  "level": "intermediate",
  "price": 39.99,
  "language_default": "de"
}
```

#### Response (201 Created)

```json
{
  "success": true,
  "data": {
    "course_id": "uuid",
    "title": "Network+ Komplettkurs",
    "published": false,
    "created_at": "2024-11-14T10:30:00Z"
  }
}
```

---

## 7. Lernmodule

### 📖 Modul-Management

| Endpunkt | Methode | Beschreibung | Auth |
|----------|---------|-------------|------|
| `/api/v1/modules/{course_id}` | GET | Module eines Kurses | optional |
| `/api/v1/modules` | POST | Modul erstellen | `manage:courses` |
| `/api/v1/modules/{module_id}` | PATCH | Modul aktualisieren | `manage:courses` |
| `/api/v1/modules/{module_id}` | DELETE | Modul löschen | `manage:courses` |

---

## 8. Lernmethoden (LM00-LM11)

### 🎯 Methoden-Management

**12 Content-Lernmethoden** in 3 Gruppen:

| Gruppe | IDs | Lernmethoden |
|--------|-----|--------------|
| **A** | LM00-LM04 | Erklärend: Text, Video, Interaktiv, KI, Oral |
| **B** | LM05-LM08 | Praxis: Übungen, Code, Whiteboard, Quiz |
| **C** | LM09-LM11 | Prüfung: Exam, Case Study, Peer Review |

#### 6.1 📋 GET `/api/v1/methods/{module_id}`

**Alle Lernmethoden eines Moduls**

---

#### 6.2 ➕ POST `/api/v1/methods`

**Neue Lernmethode erstellen** (LM00-LM11)

**Auth:** `@require_permission('manage:courses')`

#### Request Body

```json
{
  "module_id": "uuid",
  "method_type": 0,
  "title": "Einführung in Netzwerke",
  "description": "Text-basierte Erklärung der Netzwerk-Grundlagen"
}
```

**Constraint:**
- `method_type`: 0-11 (NICHT 12-32!)
- `group_code`: A, B, oder C

---

## 9. Prüfungen

### 📝 Prüfungs-Management

| Endpunkt | Methode | Beschreibung | Auth |
|----------|---------|-------------|------|
| `/api/v1/exams/{course_id}` | GET | Prüfungen eines Kurses | optional |
| `/api/v1/exams` | POST | Neue Prüfung erstellen | `manage:courses` |
| `/api/v1/exam/{exam_id}` | GET | Prüfungsdetails | authenticated |
| `/api/v1/exam/{exam_id}/submit` | POST | Prüfung abgeben | authenticated |

---

## 10. KI-Pipeline

### 🤖 KI-Funktionen

| Endpunkt | Methode | Beschreibung | Auth |
|----------|---------|-------------|------|
| `/api/v1/ki/import` | POST | Datei hochladen | `manage:courses` |
| `/api/v1/ki/generate/modules` | POST | Module generieren | `manage:courses` |
| `/api/v1/ki/generate/methods` | POST | Lernmethoden generieren | `manage:courses` |
| `/api/v1/ki/translate` | POST | Inhalte übersetzen | authenticated |

---

## 11. Dashboard & Widgets

### 📊 Dashboard-Management

| Endpunkt | Methode | Beschreibung | Auth |
|----------|---------|-------------|------|
| `/api/v1/dashboard` | GET | Dashboard laden | authenticated |
| `/api/v1/dashboard/save` | POST | Layout speichern | authenticated |
| `/api/v1/widgets` | GET | Verfügbare Widgets | authenticated |

---

## 12. LiveRoom

### 🎥 LiveRoom-API

| Endpunkt | Methode | Beschreibung | Auth |
|----------|---------|-------------|------|
| `/api/v1/liveroom/create` | POST | LiveRoom erstellen | authenticated |
| `/api/v1/liveroom/{room_id}` | GET | LiveRoom-Details | authenticated |
| `/api/v1/liveroom/{room_id}/join` | POST | LiveRoom beitreten | authenticated |
| `/api/v1/liveroom/{room_id}/leave` | POST | LiveRoom verlassen | authenticated |

---

## 13. Token-System

### 💰 Token-Management

| Endpunkt | Methode | Beschreibung | Auth |
|----------|---------|-------------|------|
| `/api/v1/tokens` | GET | Token-Status | authenticated |
| `/api/v1/tokens/buy` | POST | Token kaufen | authenticated |
| `/api/v1/tokens/history` | GET | Verbrauchs-Historie | authenticated |

---

## 14. Community & Gruppen

### 👥 Gruppen-Management (Social Network)

**Unterschied:** `core.groups` (GBA/Zugriffskontrolle) vs `community.groups` (Social Network)

| Endpunkt | Methode | Beschreibung | Auth |
|----------|---------|-------------|------|
| `/api/v1/groups/create` | POST | Gruppe erstellen | authenticated |
| `/api/v1/groups/{group_id}` | GET | Gruppen-Details | authenticated |
| `/api/v1/groups/{group_id}/join` | POST | Gruppe beitreten | authenticated |
| `/api/v1/groups/{group_id}/posts` | GET | Posts in Gruppe | authenticated |

---

## 15. Suche

### 🔍 Such-API

| Endpunkt | Methode | Beschreibung | Auth |
|----------|---------|-------------|------|
| `/api/v1/search` | GET | Globale Suche | optional |

---

## 16. Sicherheit

### 🔒 Sicherheitsmaßnahmen

```
API Request
    ↓
1. Rate Limit Check
    ↓
2. Authentication (JWT Token)
    ├─ Valid Token? → Extract user_id + groups
    └─ Invalid? → 401 Unauthorized
    ↓
3. Authorization (GBA Permission Check)
    ├─ User's groups have required permission?
    ├─ YES → Continue to step 4
    └─ NO → 403 Forbidden
    ↓
4. Input Validation (Pydantic)
    ├─ Valid input?
    ├─ YES → Process Request
    └─ NO → 400 Bad Request
    ↓
5. Return Response
```

---

### 🛡️ Security Features

| Feature | Beschreibung |
|---------|-------------|
| 🔐 **GBA Authorization** | Group-based permission checks at every endpoint |
| ⏱️ **Rate Limiting** | 100 Requests/Minute pro User |
| 📝 **IP-Logging** | Für Admin-Zugriffe |
| 🚨 **Abuse-Detection** | KI-Endpunkte überwacht |
| 🔑 **JWT-Validation** | Token-Integrität und Ablauf |
| 🛡️ **Input Validation** | Pydantic Models |
| 🔒 **HTTPS Only** | TLS 1.3 |
| 🎫 **CSRF Protection** | Token-basiert |

---

### ⏱️ Rate Limits

| Endpunkt-Typ | Limit | Zeitfenster |
|--------------|-------|-------------|
| 🔓 **Public** | 60 | 1 Minute |
| 🔐 **Authenticated** | 120 | 1 Minute |
| 🤖 **KI-Endpoints** | 10 | 1 Minute |
| 📤 **Upload** | 5 | 1 Minute |

---

## 17. GBA Berechtigungsmodell – Zusammenfassung

### 🔑 Core Concepts

**Gruppen (Groups)** sind zentrale Organisationseinheit:
- Benutzer gehören zu einer oder mehreren **Gruppen** (core.users_groups)
- Jede Gruppe hat **Berechtigungen** (core.permissions via core.role_permissions)
- Berechtigungen steuern **API-Zugriff** via @require_permission() Decorators

### 📋 Berechtigungsprüfung im Detail

```
1. Client sendet API-Request mit JWT Token
2. JWT Token enthält: user_id + groups[]
3. Backend Decorator (@require_permission('manage:courses'))
4. SQL Query: SELECT * FROM core.permissions
   WHERE permission_code = 'manage:courses'
   AND group_id IN (user.groups)
5. Falls Permission gefunden: 200 OK
   Falls nicht: 403 Forbidden
```

---

## 18. Zusammenfassung

### ✅ Die LSX-API (GBA Edition)

| Feature | Status |
|---------|--------|
| 📚 **Alle Funktionen abgedeckt** | ✅ |
| 🧩 **GBA-basierte Autorisierung** | ✅ |
| 📦 **Versioniert (v1)** | ✅ |
| 🔒 **Sicher** | ✅ |
| 🔄 **Erweiterbar** | ✅ |
| 🤖 **KI-optimiert** | ✅ |
| 👥 **Gruppen-basiert (GBA)** | ✅ |
| 📊 **RESTful** | ✅ |

---

**Version:** 2.0 (GBA Edition)
**Status:** Production
**Letztes Update:** 2026-01-25
