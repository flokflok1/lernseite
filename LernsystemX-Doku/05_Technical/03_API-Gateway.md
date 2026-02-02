# 03 – API-Gateway (GBA Edition)

**Version:** 2.0 (Group-Based Architecture)
**Stand:** 2026-01-25
**Status:** Production Ready

Das Dokument beschreibt das **API-Gateway-System** des LSX Lernsystems als zentrale Sicherheitsschicht.

Das API-Gateway ist der Single Entry Point für alle Clients und implementiert **Group-Based Authorization (GBA)** für alle geschützten Endpoints.

---

## Überblick

Das API-Gateway erfüllt folgende Funktionen:

- 🔐 **GBA Authorization** - Group-basierte Berechtigungsprüfung für jeden Request
- 🎯 **Routing** - Weiterleitung zu Backend-Services
- 🔑 **JWT-Validierung** - Token-Parsing und Signatur-Verifizierung
- ⏱️ **Rate Limiting** - Schutz vor Überlastung
- 📊 **Monitoring** - Zentrale Logging- und Tracking-Infrastruktur
- 🌍 **Multi-Tenant** - Organisations-Isolation und -Routing
- 🔌 **WebSocket** - LiveRoom und Real-Time Services
- 🛡️ **Security** - WAF, DDoS-Schutz, Request Validation

---

## Architektur

```
[Clients: Web/Mobile/Desktop]
           ↓
[API Gateway (Traefik/Kong/nginx)]
    ├─ JWT Validation
    ├─ GBA Permission Check (groups[] + permissions)
    ├─ Rate Limiting
    └─ Request Routing
           ↓
[Backend Services]
    ├─ /api/v1/auth/*
    ├─ /api/v1/courses/*
    ├─ /api/v1/admin/*
    └─ /api/v1/learning-methods/*
           ↓
[Databases, Cache, Workers]
```

---

## Routing-Struktur

LSX nutzt folgende API-Routes (alle mit v1-Versionierung):

| Route | Service | Beschreibung |
|-------|---------|--------------|
| `/api/v1/auth/*` | Auth Service | Login, Register, Token Refresh |
| `/api/v1/users/*` | User Service | Benutzerverwaltung |
| `/api/v1/courses/*` | Course Service | Kurse, Kapitel, Lektionen |
| `/api/v1/admin-panel/*` | Admin Service | System Administration (GBA) |
| `/api/v1/course_editor/*` | Editor Service | Content Authoring |
| `/api/v1/learning_methods/*` | Methods Service | LM00-LM11 Execution |
| `/api/v1/community/*` | Community Service | Social Network |
| `/api/v1/liveroom/*` | LiveRoom Service | WebRTC + Whiteboard |
| `/api/v1/compliance/*` | Compliance Service | GDPR, DSA, NetzDG |
| `/api/v1/moderation/*` | Moderation Service | Content Review & DRM |
| `/api/v1/payments/*` | Payment Service | Token Billing |
| `/api/v1/analytics/*` | Analytics Service | Dashboards & Metrics |

**Wichtig:** Alle Routes werden durch das Gateway geleitet und müssen die JWT-Validierung + GBA-Prüfung bestehen.

---

## API-Versionierung

LSX nutzt **URL-basierte Versionierung**:

- `/api/v1/*` - Stabile Version (langfristig kompatibel)
- `/api/v2/*` - Neue Versionen mit Breaking Changes (optional)

**Regeln:**
- v1 bleibt kompatibel mit existierenden Clients
- v2 wird parallel eingeführt bei Breaking Changes
- Deprecation-Hinweise im Response-Header

---

## GBA-Authentifizierung im Gateway

Jeder Request durchläuft folgendes Flow:

```
1. Header Validation
   ↓
2. JWT Token Extraction & Validation
   ├─ Signatur-Verifizierung
   ├─ Ablaufzeit-Prüfung
   └─ groups[] Array Extraktion
   ↓
3. GBA Permission Check
   ├─ Permission Code aus Endpoint
   ├─ User's effective permissions ermitteln
   └─ Zugriff erlaubt/verweigert?
   ↓
4. Organisation Routing (Multi-Tenant)
   ├─ X-LSX-Org-ID aus JWT
   └─ Resource-Isolation prüfen
   ↓
5. Request Forwarding oder 403 Forbidden
```

### Header-Anforderungen

```
Authorization: Bearer <jwt>              # REQUIRED - Access Token
X-LSX-Client: web|mobile|admin          # REQUIRED - Client Type
X-LSX-Org-ID: <org-uuid>                # OPTIONAL - Auto-erkannt aus JWT
X-LSX-Request-ID: <tracking-id>         # AUTO - Gesetzt vom Gateway
```

### JWT Token Struktur (mit GBA)

```json
{
  "sub": "user-uuid",
  "user_id": "user-uuid",
  "email": "user@example.com",
  "name": "Full Name",
  "organisation_id": "org-uuid",
  "iat": 1704067200,
  "exp": 1704153600,

  "groups": [
    {
      "id": 1,
      "name": "system-admin",
      "slug": "system_admin",
      "type": "system",
      "permissions": [
        "admin:system",
        "admin:organisations",
        "manage:*"
      ]
    },
    {
      "id": 52,
      "name": "course-creators",
      "slug": "course_creators",
      "type": "organisation",
      "permissions": [
        "manage:courses",
        "manage:content",
        "view:analytics"
      ]
    }
  ]
}
```

### Token-Validierung im Gateway

Das Gateway prüft:

1. **Signatur** - JWT korrekt signiert mit SECRET_KEY?
2. **Ablaufzeit** - `exp` claim noch gültig?
3. **groups[] Array** - Vorhanden und nicht leer?
4. **Berechtigungen** - User hat Permissions für den angeforderten Endpoint?
5. **Organisation** - Resource gehört zur User's Organisation?

**Fehler-Response bei fehlender Authentifizierung:**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing or invalid JWT token"
  }
}
```
**Status:** 401 Unauthorized

---

## GBA-Autorisierung (Permission Checking)

### Permission Decorator Pattern

Der Backend nutzt **Permission Decorators** zur Endpoint-Absicherung:

```python
# Python Flask Example

@bp.route('/api/v1/admin-panel/users', methods=['GET'])
@require_permission('admin:system')
def list_all_users():
    """
    Nur Benutzer mit admin:system Permission dürfen zugreifen.
    Der Decorator prüft automatisch:
    1. JWT vorhanden?
    2. groups[] vorhanden?
    3. Eine der User-Gruppen hat 'admin:system' permission?
    """
    return get_users()

@bp.route('/api/v1/courses', methods=['POST'])
@require_permission('manage:courses')
def create_course():
    """Erfordert manage:courses Permission"""
    return create_new_course()

@bp.route('/api/v1/admin-panel/courses/<course_id>', methods=['DELETE'])
@require_permission('admin:system', 'manage:courses')  # ANY
def delete_course(course_id):
    """Erfordert admin:system ODER manage:courses"""
    return delete_course_by_id(course_id)
```

### Permission Codes (Master List)

| Code | Bedeutung | Gruppen |
|------|-----------|---------|
| `admin:system` | System-Admin (alles) | system-admin |
| `admin:organisations` | Organisationen verwalten | system-admin, org-admin |
| `manage:courses` | Kurse erstellen/ändern | course-creators, teachers |
| `manage:content` | Content-Authoring | course-creators, teachers |
| `manage:users` | Benutzer verwalten | org-admin, support |
| `manage:groups` | Gruppen verwalten | system-admin, org-admin |
| `view:analytics` | Analytics/Reports anschauen | org-admin, teachers, analytics-viewers |
| `view:moderation` | Moderation-Panel | moderators, system-admin |
| `manage:compliance` | Compliance-Tools | compliance-officers, system-admin |

### Autorisierungsprozess im Gateway

```
User Request: GET /api/v1/admin-panel/users
    ↓
Gateway: JWT validieren
    ↓
Backend: Decorator @require_permission('admin:system') prüft:
    1. Extract user.groups[] aus JWT
    2. Für jede Gruppe: Hat sie 'admin:system'?
    3. NICHT gefunden? → 403 Forbidden
    4. GEFUNDEN? → Request durchlassen
    ↓
Response: 200 OK (mit Daten) oder 403 Forbidden
```

**Fehler-Response bei mangelnden Berechtigungen:**
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to access this resource",
    "required_permission": "admin:system",
    "your_permissions": ["manage:courses", "view:analytics"]
  }
}
```
**Status:** 403 Forbidden

---

## Rate Limiting

### Limit-Tiers

| Route | Public User | Premium | Org Admin |
|-------|------------|---------|-----------|
| `/api/v1/auth/*` | 5/min | 10/min | 10/min |
| `/api/v1/courses/*` | 30/min | 60/min | 120/min |
| `/api/v1/learning_methods/*` | 60/min | 200/min | 500/min |
| `/api/v1/admin-panel/*` | N/A | N/A | 100/min |
| `/api/v1/moderation/*` | N/A | N/A | 200/min |

**Anpassbar pro Organisation** (über Subscription).

**Fehler bei Überschreitung:**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retry_after": 60
  }
}
```
**Status:** 429 Too Many Requests

---

## Multi-Tenant Routing (Organisationen)

Das Gateway erkennt Organisationen über:

### Domain-basiert
```
schule-123.lernsystemx.com     → org_id = "xyz-123"
firma-training.lernsystemx.com → org_id = "xyz-456"
academy.lernsystemx.com         → Org Auto-Erkennung via JWT
```

### JWT-basiert (X-LSX-Org-ID)
```
Authorization: Bearer <jwt>
  ↓
JWT decode: organisation_id = "xyz-123"
  ↓
Gateway setzt: X-LSX-Org-ID: xyz-123
  ↓
Backend nutzt X-LSX-Org-ID für Resource-Filtering
```

### Tenant-Isolation Rules

- ✅ User kann nur auf Ressourcen seiner Organisation zugreifen
- ✅ System-Admin (`admin:system`) kann alle Organisationen sehen
- ❌ Cross-Tenant Zugriffe sind NICHT erlaubt (selbst mit Token)
- ✅ Jede Org hat eigene Kurse, Benutzer, Liveroom-Instanzen
- ✅ Jede Org hat separate Token-Wallets & Subscriptions

---

## CORS-Konfiguration

Nur explizit erlaubte Domains akzeptiert:

```
*.lernsystemx.com
*.schule-domain.de
*.firma-domain.com
localhost:3000 (Development)
```

**Erlaubte HTTP-Methoden:**
```
GET, POST, PUT, PATCH, DELETE, OPTIONS
```

**Erlaubte Header:**
```
Authorization
Content-Type
X-LSX-Client
X-LSX-Org-ID
X-LSX-Request-ID
Accept-Language
```

**Deny-by-Default:** Requests von nicht-erlaubten Origins erhalten 403.

---

## WebSocket Routing (LiveRoom)

Für Real-Time Communication (WebRTC, Whiteboard, Chat):

```
ws://api.lernsystemx.com/api/v1/liveroom/ws
wss://api.lernsystemx.com/api/v1/liveroom/ws (SSL)
```

### WebSocket Authentifizierung

```javascript
// Client sendet JWT im Query-Parameter oder Header
const ws = new WebSocket(
  'wss://api.lernsystemx.com/api/v1/liveroom/ws?token=' + jwtToken
);

// Oder Header-basiert (je nach Implementierung):
ws.setRequestHeader('Authorization', 'Bearer ' + jwtToken);
```

### Gateway prüft WebSocket-Requests auf:

- ✅ Gültiges JWT vorhanden?
- ✅ User in der Liveroom-Gruppe eingetragen?
- ✅ Liveroom selbst existiert?
- ✅ Rate Limits für WebSocket-Events einhalten

**Fehler:** 403 Forbidden (WebSocket wird abgelehnt)

---

## Request-Validierung

Alle eingehenden Requests werden validiert:

```
1. HTTP-Methode erlaubt?
   GET, POST, PUT, PATCH, DELETE, OPTIONS
   ↓
2. Content-Type gültig?
   application/json, application/x-www-form-urlencoded
   ↓
3. Body-Größe OK?
   Max 20MB pro Request
   ↓
4. JSON-Format korrekt?
   ↓
5. Rate Limit nicht überschritten?
   ↓
6. JWT vorhanden & gültig?
   ↓
7. GBA Permission vorhanden?
   ↓
8. Weiterleitung zum Backend-Service
```

**Typische Fehler:**
- 400 Bad Request - Format/Validierungsfehler
- 401 Unauthorized - Kein gültiges JWT
- 403 Forbidden - Permission nicht vorhanden
- 413 Payload Too Large - Body zu groß
- 429 Too Many Requests - Rate Limit überschritten

---

## Gateway-Logging & Monitoring

### Request Tracking

Jeder Request erhält eine **eindeutige Tracking-ID**:

```
X-LSX-Request-ID: <uuid>
```

Diese wird in allen Logs verwendet für End-to-End Tracing.

### Zentrale Logs enthalten:

```json
{
  "timestamp": "2026-01-25T14:30:00Z",
  "request_id": "uuid-1234",
  "method": "GET",
  "path": "/api/v1/courses",
  "user_id": "user-uuid",
  "organisation_id": "org-uuid",
  "status_code": 200,
  "response_time_ms": 245,
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "groups": ["teachers", "course-creators"],
  "permissions_checked": ["manage:courses"],
  "permission_result": "granted"
}
```

### Monitoring-Dashboards

- 📊 Request-Rate pro Endpoint
- ⏱️ Response-Times (p50, p95, p99)
- 🔴 Error Rates (4xx, 5xx)
- 🔐 Failed Authorization Attempts
- 🌍 Request Distribution by Org
- 🛑 Rate Limit Hits

---

## Fehlerbehandlung

### Standard HTTP-Codes

| Code | Bedeutung | Beispiel |
|------|-----------|----------|
| 200 | OK | Erfolgreich abgearbeitet |
| 201 | Created | Ressource erstellt |
| 204 | No Content | OK, kein Body |
| 400 | Bad Request | Ungültige Eingabe |
| 401 | Unauthorized | Kein JWT / JWT ungültig |
| 403 | Forbidden | Permission nicht vorhanden |
| 404 | Not Found | Ressource nicht gefunden |
| 409 | Conflict | Datenproblem (z.B. duplicate) |
| 429 | Too Many Requests | Rate Limit überschritten |
| 500 | Internal Server Error | Backend-Fehler |
| 502 | Bad Gateway | Backend nicht erreichbar |
| 503 | Service Unavailable | Gateway in Wartung |

### Einheitliche Error Response

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You don't have permission to perform this action",
    "details": {
      "required_permission": "admin:system",
      "your_groups": ["teachers", "students"]
    }
  },
  "request_id": "uuid-1234"
}
```

---

## Sicherheitsmechanismen

Das Gateway implementiert mehrschichtige Sicherheit:

### 🔐 GBA-basierte Autorisierung
- Alle Endpoints prüfen Benutzer-Berechtigungen über groups[]
- Permission-Decorator auf jedem geschützten Endpoint
- Fine-grained Permission Codes (admin:system, manage:courses, etc.)
- Fail-Secure: Bei fehlender Permission → 403

### 🛡️ Web Application Firewall (WAF)
- SQL Injection Detection & Prevention
- XSS Prevention
- Header Validation
- Payload Inspection

### 🚨 DDoS-Schutz
- Rate Limiting pro User / IP
- Connection Limits
- Request Size Limits
- Slowloris Protection

### 🌍 Geo-Blocking
- Erlaubte Länder pro Org konfigurierbar
- IP-Geolocation Check
- Verdächtige Länder blocken

### 🤖 Bot Detection
- User-Agent Analysis
- Behavioral Pattern Detection
- CAPTCHA Integration (optional)

### 📋 Header Whitelisting
- Nur bekannte Header akzeptiert
- Custom LSX Headers validiert
- Authorization Header mandatory für protected endpoints

### 🔑 JWT Sicherheit
- HS256 oder RS256 Signing
- Secret Key Rotation
- Token Expiration (kurz für Access, lang für Refresh)
- Blacklist für widerrufene Tokens

---

## API-Gateway Deployment

### Empfohlene Tools

**Traefik oder Kong** - beide unterstützen:

- ✅ Automatische SSL-Zertifikate (Let's Encrypt)
- ✅ Load Balancing (Round-Robin, Least Conn)
- ✅ Canary Releases (Schrittweise Rollouts)
- ✅ Rate Limiting & Quota Management
- ✅ Header Injection & Rewriting
- ✅ URL Rewrites & Redirects
- ✅ Multi-Tenant Domain Routing
- ✅ WebSocket Proxy
- ✅ Built-in WAF
- ✅ Health Checks & Auto-Recovery

### Docker Deployment

```yaml
version: '3.8'
services:
  gateway:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./traefik.yml:/traefik.yml:ro
    environment:
      - LE_EMAIL=admin@lernsystemx.com
      - DOMAIN=api.lernsystemx.com
```

---

## Zusammenfassung

Das LSX API-Gateway ist:

- 🔐 **Sicher** - GBA-basierte Autorisierung auf jedem Request
- 📈 **Skalierbar** - Load Balanced, Multi-Instance
- 🎯 **Zentralisiert** - Single Entry Point für alle Clients
- 🏗️ **Modular** - Service-agnostisch, flexibel erweiterbar
- 🌍 **Mandantenfähig** - Vollständige Organisation-Isolation
- 🚀 **Performance-optimiert** - Caching, Compression, Connection Pooling
- 🛡️ **Compliance-ready** - WAF, Rate Limits, Audit Logging
- 🔄 **Zukunftssicher** - API v1/v2 Unterstützung, Progressive Upgrades

Es bildet die **kritische Sicherheits- und Routing-Infrastruktur** für alle Verbindungen zwischen Clients, Backend-Services, und externen Systems.

---

**Stand:** 2026-01-25 | **Version:** 2.0 (GBA) | **Status:** Production Ready
