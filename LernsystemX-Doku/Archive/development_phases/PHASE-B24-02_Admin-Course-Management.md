# PHASE B24-02: Admin-Kursverwaltung (Backend)

**Status:** ✅ Abgeschlossen
**Datum:** 2025-11-20
**Autor:** Claude Code (Anthropic)
**Compliance:** ISO 27001:2013, ISO 9001:2015

---

## 1. ÜBERSICHT

Diese Phase implementiert die Backend-Funktionalität für die Admin-Kursverwaltung. Administratoren können nun alle Kurse im System zentral verwalten, überwachen und moderieren.

### Ziele

- ✅ Zentrale Kursverwaltung für Administratoren
- ✅ Erweiterte Filter- und Suchfunktionen
- ✅ Kursstatusänderungen (Veröffentlichen, Archivieren)
- ✅ Vollständige Audit-Logging-Integration
- ✅ RBAC-konforme Berechtigungsprüfungen

### Scope

**IN SCOPE:**
- Admin API-Endpunkte für Kursverwaltung
- Repository-Methoden für Admin-Operationen
- Pydantic-Modelle für Validierung
- Permissions-System-Erweiterung
- Audit-Logging für alle Aktionen

**OUT OF SCOPE:**
- Frontend-Implementierung (separate Phase)
- Modul-/Lesson-Content-Verwaltung (spätere Phase)
- 5-stufiges Kategoriesystem (spätere Phase)
- Demo-Daten-Seeding
- SQL-Migrationen (existierende DB-Struktur wird verwendet)

---

## 2. ARCHITEKTUR & ENTSCHEIDUNGEN

### 2.1 Vorgefundene Struktur

**Existierende Komponenten:**
- `CourseRepository` mit CRUD-Methoden (psycopg ohne ORM)
- `AuditService` für Security-Event-Logging
- `Permissions`-System mit RBAC-Matrix
- `admin_users.py` als Referenz-Implementierung (Phase B24)
- API Gateway mit Blueprint-Routing
- Pydantic-Modelle für Request/Response-Validierung

**DB-Struktur (courses-Tabelle):**
```sql
- course_id (PK)
- title, description
- creator_user_id (FK zu users)
- organisation_id (FK zu organisations, nullable)
- category, level, language
- price, is_public
- is_published (BOOLEAN) + published_at (TIMESTAMP)
- archived_at (TIMESTAMP) -- Soft Delete
- thumbnail_url, preview_video_url, tags (ARRAY)
- created_at, updated_at
```

### 2.2 Status-Feld-Konflikt (Doku vs. Realität)

**Problem:**
- Dokumentation (`04_Kurs-Architektur.md`) erwähnt `status` ENUM-Feld
- Existierende DB verwendet `is_published` (BOOL) + `archived_at` (TIMESTAMP)

**Lösung (Minimalinvasiv):**
- Verwende **virtuelle Status-Logik** in SQL-Queries:
  ```sql
  CASE
    WHEN archived_at IS NOT NULL THEN 'archived'
    WHEN is_published = TRUE THEN 'published'
    ELSE 'draft'
  END AS status
  ```
- Keine Schema-Änderungen erforderlich
- API gibt `status` als berechnetes Feld zurück
- Kompatibel mit existierendem Code

### 2.3 Implementierungsplan

1. **API-Endpunkte** (`admin_courses.py`):
   - GET `/api/v1/admin/courses` - Liste mit Filtern
   - GET `/api/v1/admin/courses/<id>` - Details
   - POST `/api/v1/admin/courses` - Erstellen
   - PATCH `/api/v1/admin/courses/<id>` - Metadaten ändern
   - POST `/api/v1/admin/courses/<id>/status` - Status ändern
   - DELETE `/api/v1/admin/courses/<id>` - Archivieren

2. **Repository-Methoden** (`course_repository.py`):
   - `admin_list_courses(...)` - Pagination + Filter
   - `admin_get_course_by_id(...)` - Details ohne Cache
   - `admin_create_course(...)` - Kurs im Namen eines Creators erstellen
   - `admin_update_course(...)` - Metadaten aktualisieren

3. **Pydantic-Modelle** (`admin_course.py`):
   - `AdminCourseListItem` - List-Response
   - `AdminCourseDetail` - Detail-Response
   - `AdminCourseCreateRequest` - Create-Request
   - `AdminCourseUpdateRequest` - Update-Request
   - `AdminCourseStatusUpdateRequest` - Status-Change-Request

4. **Permissions** (`permissions.py`):
   - `ADMIN_COURSE_READ` - Lesen/Anzeigen
   - `ADMIN_COURSE_WRITE` - Erstellen/Ändern/Veröffentlichen
   - `ADMIN_COURSE_DELETE` - Archivieren/Löschen

5. **Audit-Logging** (Integration):
   - Alle Admin-Aktionen loggen via `AuditService.log_action()`
   - Severity-Level: info, medium, high, critical

---

## 3. IMPLEMENTIERTE ENDPUNKTE

### 3.1 GET `/api/v1/admin/courses`

**Zweck:** Liste aller Kurse mit erweiterten Filtern

**Query-Parameter:**
- `page` (default: 1)
- `per_page` (default: 50, max: 100)
- `status` (all, draft, published, archived)
- `search` (Titel/Beschreibung)
- `creator_id` (Filter nach Creator)
- `organisation_id` (Filter nach Organisation)
- `category`, `level`, `language`
- `sort` (created_at, updated_at, title, enrollment_count)
- `order` (asc, desc)

**Response:**
```json
{
  "success": true,
  "courses": [
    {
      "course_id": 1,
      "title": "Python Grundlagen",
      "creator_id": 5,
      "creator_name": "Max Mustermann",
      "organisation_id": null,
      "status": "published",
      "is_public": true,
      "enrollment_count": 150,
      "module_count": 8,
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-11-19T10:00:00Z",
      "published_at": "2025-01-20T10:00:00Z"
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

**Permissions:** `ADMIN_COURSE_READ`

**Audit-Log:** `admin.courses.list`

---

### 3.2 GET `/api/v1/admin/courses/<course_id>`

**Zweck:** Detaillierte Kurs-Informationen

**Response:**
```json
{
  "success": true,
  "course": {
    "course_id": 1,
    "title": "Python Grundlagen",
    "description": "Lerne Python von Grund auf",
    "creator_id": 5,
    "creator_name": "Max Mustermann",
    "creator_email": "max@example.com",
    "organisation_id": null,
    "organisation_name": null,
    "category": "programming",
    "level": "beginner",
    "language": "de",
    "price": 49.99,
    "is_public": true,
    "status": "published",
    "thumbnail_url": "https://...",
    "tags": ["python", "beginner", "programming"],
    "module_count": 8,
    "enrollment_count": 150,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-11-19T10:00:00Z",
    "published_at": "2025-01-20T10:00:00Z",
    "archived_at": null
  }
}
```

**Permissions:** `ADMIN_COURSE_READ`

**Audit-Log:** `admin.courses.view`

---

### 3.3 POST `/api/v1/admin/courses`

**Zweck:** Neuen Kurs erstellen (im Namen eines Creators)

**Request Body:**
```json
{
  "title": "Python Grundlagen",
  "description": "Lerne Python von Grund auf",
  "creator_id": 5,
  "organisation_id": null,
  "category": "programming",
  "level": "beginner",
  "language": "de",
  "price": 49.99,
  "is_public": false,
  "tags": ["python", "beginner"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Course created successfully",
  "course": {
    "course_id": 123,
    "title": "Python Grundlagen",
    ...
  }
}
```

**Permissions:** `ADMIN_COURSE_WRITE`

**Audit-Log:** `admin.courses.create` (Severity: high)

---

### 3.4 PATCH `/api/v1/admin/courses/<course_id>`

**Zweck:** Kurs-Metadaten aktualisieren

**Request Body (alle Felder optional):**
```json
{
  "title": "Python Grundlagen - Aktualisiert",
  "description": "Neue Beschreibung",
  "category": "programming",
  "level": "intermediate",
  "language": "en",
  "price": 59.99,
  "is_public": true,
  "thumbnail_url": "https://...",
  "tags": ["python", "intermediate"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Course updated successfully",
  "course": {...}
}
```

**Permissions:** `ADMIN_COURSE_WRITE`

**Audit-Log:** `admin.courses.update` (Severity: medium)

---

### 3.5 POST `/api/v1/admin/courses/<course_id>/status`

**Zweck:** Kurs-Status ändern

**Request Body:**
```json
{
  "action": "publish",
  "reason": "Quality approved by admin"
}
```

**Aktionen:**
- `publish` - Kurs veröffentlichen (`is_published=TRUE`, `published_at=NOW()`)
- `unpublish` - Veröffentlichung zurückziehen (`is_published=FALSE`)
- `archive` - Kurs archivieren (`archived_at=NOW()`, `is_published=FALSE`)
- `unarchive` - Archivierung aufheben (`archived_at=NULL`)

**Response:**
```json
{
  "success": true,
  "message": "Course published successfully",
  "status": "published"
}
```

**Permissions:** `ADMIN_COURSE_WRITE`

**Audit-Log:** `admin.courses.publish/unpublish/archive/unarchive` (Severity: high)

---

### 3.6 DELETE `/api/v1/admin/courses/<course_id>`

**Zweck:** Kurs archivieren (Soft Delete)

**Request Body:**
```json
{
  "reason": "Copyright violation reported"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Course archived successfully"
}
```

**Hinweis:** Dies ist ein **Soft Delete** (setzt `archived_at`). Kein Hard Delete!

**Permissions:** `ADMIN_COURSE_DELETE`

**Audit-Log:** `admin.courses.delete` (Severity: critical)

---

## 4. CODE-ÄNDERUNGEN (High Level)

### 4.1 Neue Dateien

| Datei | Zeilen | Zweck |
|-------|--------|-------|
| `backend/app/api/admin_courses.py` | 485 | Admin-Kurs-API-Endpunkte |
| `backend/app/models/admin_course.py` | 201 | Pydantic-Modelle für Validierung |
| `LernsystemX-Doku/PHASE-B24-02_Admin-Course-Management.md` | Dieses Dokument | Phase-Dokumentation |
| `LernsystemX-Doku/TESTING-GUIDE_Admin-Course-Management.md` | Siehe unten | Manuelles Test-Guide |

### 4.2 Geänderte Dateien

**`backend/app/repositories/course_repository.py`** (+293 Zeilen)
- Neue Methoden:
  - `admin_list_courses(...)` - Erweiterte Listenabfrage mit Filtern
  - `admin_get_course_by_id(...)` - Admin-Detail-Ansicht (ohne Cache)
  - `admin_create_course(...)` - Kurs erstellen im Namen eines Creators
  - `admin_update_course(...)` - Kurs-Metadaten aktualisieren

**`backend/app/security/permissions.py`** (+9 Zeilen)
- Neue Permissions:
  - `ADMIN_COURSE_READ = 'admin:course:read'`
  - `ADMIN_COURSE_WRITE = 'admin:course:write'`
  - `ADMIN_COURSE_DELETE = 'admin:course:delete'`
- Permissions zu `admin`-Rolle hinzugefügt

**`backend/app/api/__init__.py`** (+1 Zeile)
- Import: `from app.api import admin_courses`

### 4.3 Keine Änderungen

- ❌ Keine SQL-Migrationen erstellt (044+)
- ❌ Keine Tabellen-/Spalten-Änderungen
- ❌ Keine Demo-Daten-Seeds
- ❌ Keine Entfernung/Refactoring existierender Endpunkte
- ❌ Keine .old/.bak/.tmp/.copy-Dateien
- ❌ Keine Frontend-Änderungen

---

## 5. ARCHITEKTUR-PATTERNS

### 5.1 Repository Pattern

**Alle DB-Operationen in Repository-Schicht:**
```python
# Admin-spezifische Methoden in CourseRepository
@classmethod
def admin_list_courses(cls, page, per_page, status, search, ...):
    # Parametrisierte Queries, keine String-Interpolation
    # Virtuelle Status-Logik in SQL
    # Pagination + Filter-Logik
    pass
```

**Vorteile:**
- Trennung von Business-Logik und Datenzugriff
- Wiederverwendbarkeit
- Testbarkeit

### 5.2 Pydantic-Validierung

**Request/Response-Validierung:**
```python
class AdminCourseCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    creator_id: int = Field(...)
    level: str = Field(default="beginner")

    @field_validator('level')
    @classmethod
    def validate_level(cls, v: str) -> str:
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if v not in valid_levels:
            raise ValueError(...)
        return v
```

**Vorteile:**
- Automatische Validierung vor DB-Zugriff
- Konsistente Fehlerbehandlung
- Type Safety

### 5.3 Decorator-basierte Permissions

**RBAC-Enforcement:**
```python
@api_v1.route('/admin/courses', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_list_courses():
    # ...
```

**Funktionsweise:**
- `@require_permission` prüft `g.current_user['role']` gegen `ROLE_PERMISSIONS`
- Automatische 403-Response bei fehlender Permission
- Integration mit `@token_required` (JWT)

### 5.4 Audit-Logging Pattern

**Alle Admin-Aktionen loggen:**
```python
AuditService.log_action(
    user_id=g.current_user['user_id'],
    action='admin.courses.create',
    resource_type='course',
    resource_id=str(course_id),
    details={'title': title, 'creator_id': creator_id},
    severity='high'
)
```

**Logged in:**
- `audit_logs` Tabelle (PostgreSQL)
- Felder: user_id, action, resource_type, resource_id, details (JSONB), severity, timestamp, IP, User-Agent

---

## 6. SICHERHEIT & COMPLIANCE

### 6.1 RBAC (Role-Based Access Control)

**Permissions-Matrix:**

| Permission | Free | Premium | Creator | Teacher | School | Company | Moderator | Support | **Admin** | Superadmin |
|------------|------|---------|---------|---------|--------|---------|-----------|---------|-----------|------------|
| `ADMIN_COURSE_READ` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** | ✅ |
| `ADMIN_COURSE_WRITE` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** | ✅ |
| `ADMIN_COURSE_DELETE` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** | ✅ |

### 6.2 Audit-Logging (ISO 27001:2013)

**Alle Admin-Aktionen werden geloggt:**
- `admin.courses.list` (Severity: info)
- `admin.courses.view` (Severity: info)
- `admin.courses.create` (Severity: high)
- `admin.courses.update` (Severity: medium)
- `admin.courses.publish/unpublish/archive/unarchive` (Severity: high)
- `admin.courses.delete` (Severity: critical)

**Log-Inhalte:**
- Wer? (user_id, user_email, user_role)
- Was? (action, resource_type, resource_id)
- Wann? (timestamp)
- Wo? (IP-Adresse, User-Agent, Session-ID)
- Details? (JSONB mit kontextspezifischen Infos)

### 6.3 Input-Validierung

**Pydantic-Validierung verhindert:**
- SQL-Injection (parametrisierte Queries)
- XSS (keine HTML-Injektion in title/description)
- Invalid Enums (level, language, action)
- Invalid Data Types (price, creator_id, etc.)

**Zusätzliche Checks:**
- Min/Max-Length für Strings
- Positive Zahlen für price
- Gültige ISO-639-1-Language-Codes

### 6.4 Cache-Invalidierung

**Nach Änderungen:**
```python
if result:
    CacheService.invalidate_course_cache(course_id)
```

**Verhindert:**
- Stale Data in Redis-Cache
- Inkonsistente API-Responses

---

## 7. TESTING-GUIDE (Manuell)

Siehe separate Datei: `TESTING-GUIDE_Admin-Course-Management.md`

**Enthält:**
- cURL-Beispiele für alle Endpunkte
- Testszenarien (Happy Path, Error Cases)
- Erwartete Responses
- Audit-Log-Verifikation

---

## 8. BEKANNTE LIMITIERUNGEN & NÄCHSTE PHASEN

### 8.1 Limitierungen (Out of Scope)

| Limitation | Grund | Spätere Phase |
|------------|-------|---------------|
| Keine Modul-/Lesson-Content-Verwaltung | Scope-Begrenzung | Phase B24-03 |
| Keine 5-stufigen Kategorien | DB-Schema nicht vorhanden | Phase B24-04 |
| Keine automatischen Tests | Fokus auf Implementierung | Phase B24-05 |
| Kein Frontend | Backend-only Phase | Phase B24-06 |
| Keine Bulk-Operationen | Nicht angefordert | Phase B24-07 |
| Keine Course-History/Versioning | Nicht angefordert | Phase B24-08 |

### 8.2 Nächste Phasen

**Phase B24-03: Admin-Modul-/Lesson-Verwaltung**
- Admin-Endpunkte für Modul-/Lesson-Content
- Content-Moderation (Text, Video, Quiz)
- Learning-Method-Instance-Verwaltung

**Phase B24-04: Erweiterte Kurs-Features**
- 5-stufiges Kategoriesystem
- Kurs-Duplikation
- Kurs-Templates

**Phase B24-05: Testing & Quality Assurance**
- Unit-Tests (pytest)
- Integration-Tests
- Performance-Tests

**Phase B24-06: Frontend-Integration**
- Vue.js Admin-Dashboard für Kursverwaltung
- Filterbare Kurs-Liste
- Kurs-Editor-Modal

---

## 9. DEPLOYMENT-HINWEISE

### 9.1 Voraussetzungen

**Keine Schema-Änderungen erforderlich!**
- Existierende DB-Struktur wird verwendet
- Keine SQL-Migrationen notwendig

**Python-Dependencies:**
- Keine neuen Dependencies hinzugefügt
- Existierende `requirements.txt` ausreichend

### 9.2 Deployment-Schritte

1. **Backend-Update:**
   ```bash
   cd backend
   git pull origin main
   # Kein pip install notwendig
   # Kein DB-Migrate notwendig
   ```

2. **Server-Restart:**
   ```bash
   # Development
   python run.py

   # Production (Gunicorn)
   gunicorn -w 1 -b 0.0.0.0:5000 --worker-class eventlet run:app
   ```

3. **Verifizierung:**
   ```bash
   curl http://localhost:5000/health
   # {"status": "healthy", ...}
   ```

### 9.3 Rollback-Plan

**Bei Problemen:**
1. Backend auf vorherige Version zurücksetzen
2. Server neu starten
3. Keine DB-Rollbacks notwendig (keine Schema-Änderungen)

**Audit-Logs bleiben erhalten:**
- Alle Admin-Aktionen vor dem Rollback sind weiterhin in `audit_logs` vorhanden

---

## 10. COMPLIANCE & STANDARDS

### 10.1 ISO 27001:2013 (Security)

✅ **A.9 - Access Control:**
- RBAC mit Permissions-System
- Decorator-basierte Authorization
- Least-Privilege-Prinzip

✅ **A.12 - Audit Logging:**
- Alle Admin-Aktionen in `audit_logs`
- Severity-Level (info, medium, high, critical)
- Immutable Log-Einträge

✅ **A.14 - Input Validation:**
- Pydantic-Validierung für alle Requests
- Parametrisierte SQL-Queries (keine Injection)
- Type Safety

### 10.2 ISO 9001:2015 (Quality)

✅ **7.1.5 - Monitoring Resources:**
- Umfassendes Audit-Logging
- Performance-Metriken via API Gateway

✅ **8.1 - Operational Planning:**
- Dokumentierte Architektur
- Code-Kommentare mit Docstrings
- Strukturierter Implementierungsplan

### 10.3 GDPR/DSGVO

✅ **Art. 30 - Records of Processing:**
- Audit-Logs für alle Datenverarbeitungen
- User-ID, Timestamp, Action-Type

✅ **Art. 32 - Security of Processing:**
- RBAC für Datenzugriff
- Audit-Trail für Compliance-Nachweis

---

## 11. FAZIT

### 11.1 Erreichte Ziele

✅ **Funktional:**
- 6 Admin-Endpunkte implementiert
- Erweiterte Filter-/Suchfunktionalität
- Status-Management (publish, archive, etc.)

✅ **Qualität:**
- Konsistente Code-Struktur (Pattern von admin_users.py)
- Vollständige Audit-Logging-Integration
- RBAC-konforme Permissions

✅ **Dokumentation:**
- Phase-Dokumentation (dieses Dokument)
- Testing-Guide (separates Dokument)
- Inline-Code-Kommentare (Docstrings)

### 11.2 Technische Highlights

- **Virtuelle Status-Logik** vermeidet DB-Schema-Änderungen
- **Repository-Pattern** für saubere Architektur
- **Pydantic-Validierung** für Type Safety
- **Decorator-based RBAC** für Security
- **Comprehensive Audit-Logging** für Compliance

### 11.3 Metrics

| Metric | Wert |
|--------|------|
| Neue API-Endpunkte | 6 |
| Neue Code-Zeilen | ~980 |
| Geänderte Dateien | 4 |
| Neue Permissions | 3 |
| DB-Schema-Änderungen | 0 |
| SQL-Migrationen | 0 |

---

**PHASE B24-02 - ERFOLGREICH ABGESCHLOSSEN** ✅

**Nächste Empfohlene Phase:** B24-06 (Frontend-Integration) oder B24-03 (Modul-/Lesson-Verwaltung)
