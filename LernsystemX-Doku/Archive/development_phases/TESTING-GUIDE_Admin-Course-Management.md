# TESTING-GUIDE: Admin-Kursverwaltung (Backend)

**Phase:** B24-02
**Datum:** 2025-11-20
**Zielgruppe:** Entwickler, QA-Team, System-Administrator

---

## 1. ÜBERSICHT

Dieses Dokument enthält manuelle Testszenarien für die Admin-Kursverwaltungs-API. Alle Tests verwenden **cURL** und können in einer **Bash/PowerShell/cmd** ausgeführt werden.

### Voraussetzungen

1. **Backend läuft** auf `http://localhost:5000`
2. **Admin-User existiert** in der Datenbank
3. **JWT-Token** für Admin-User verfügbar

---

## 2. AUTHENTICATION

### 2.1 Login als Admin

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@lernsystem.de",
    "password": "IhrAdminPasswort"
  }'
```

**Erwartete Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJI...",
    "refresh_token": "eyJhbGciOiJI...",
    "user": {
      "user_id": "e4ac9965-e3d2-42b9-9703-3f1c0f4adedc",
      "email": "admin@lernsystem.de",
      "role": "admin",
      ...
    }
  }
}
```

**✅ Erfolgskriterium:** `access_token` erhalten

**Für alle folgenden Tests:**
```bash
export TOKEN="eyJhbGciOiJI..."  # Ihr access_token hier
```

---

## 3. GET /api/v1/admin/courses - KURSLISTE

### 3.1 Test: Liste aller Kurse (Standard)

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses" \
  -H "Authorization: Bearer $TOKEN"
```

**Erwartete Response:**
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
      ...
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

**✅ Erfolgskriterium:**
- HTTP 200
- `courses` ist Array
- `pagination.total` >= 0

---

### 3.2 Test: Filter nach Status (published)

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses?status=published" \
  -H "Authorization: Bearer $TOKEN"
```

**✅ Erfolgskriterium:**
- Alle Kurse haben `"status": "published"`

---

### 3.3 Test: Filter nach Status (draft)

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses?status=draft" \
  -H "Authorization: Bearer $TOKEN"
```

**✅ Erfolgskriterium:**
- Alle Kurse haben `"status": "draft"`

---

### 3.4 Test: Filter nach Status (archived)

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses?status=archived" \
  -H "Authorization: Bearer $TOKEN"
```

**✅ Erfolgskriterium:**
- Alle Kurse haben `"status": "archived"`

---

### 3.5 Test: Suche nach Titel

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses?search=Python" \
  -H "Authorization: Bearer $TOKEN"
```

**✅ Erfolgskriterium:**
- Alle Kurse enthalten "Python" in `title` oder `description` (case-insensitive)

---

### 3.6 Test: Filter nach Creator

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses?creator_id=5" \
  -H "Authorization: Bearer $TOKEN"
```

**✅ Erfolgskriterium:**
- Alle Kurse haben `"creator_id": 5`

---

### 3.7 Test: Pagination (Seite 2)

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses?page=2&per_page=10" \
  -H "Authorization: Bearer $TOKEN"
```

**✅ Erfolgskriterium:**
- HTTP 200
- `pagination.page === 2`
- `pagination.per_page === 10`
- `courses.length <= 10`

---

### 3.8 Test: Sortierung (title ASC)

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses?sort=title&order=asc" \
  -H "Authorization: Bearer $TOKEN"
```

**✅ Erfolgskriterium:**
- Kurse sind alphabetisch nach `title` sortiert (A-Z)

---

### 3.9 Test: Keine Permission (Premium-User)

```bash
# Login als Premium-User
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "premium@lernsystem.de",
    "password": "premiumpassword"
  }'

# Premium-Token verwenden
export PREMIUM_TOKEN="..."

curl -X GET "http://localhost:5000/api/v1/admin/courses" \
  -H "Authorization: Bearer $PREMIUM_TOKEN"
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Forbidden",
  "message": "Missing required permission: admin:course:read"
}
```

**✅ Erfolgskriterium:**
- HTTP 403
- `error === "Forbidden"`

---

## 4. GET /api/v1/admin/courses/<course_id> - KURSDETAILS

### 4.1 Test: Existierender Kurs

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses/1" \
  -H "Authorization: Bearer $TOKEN"
```

**Erwartete Response:**
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

**✅ Erfolgskriterium:**
- HTTP 200
- `course.course_id === 1`
- `creator_name` vorhanden
- `module_count` und `enrollment_count` vorhanden

---

### 4.2 Test: Nicht-existierender Kurs

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses/99999" \
  -H "Authorization: Bearer $TOKEN"
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Course not found"
}
```

**✅ Erfolgskriterium:**
- HTTP 404
- `error === "Course not found"`

---

## 5. POST /api/v1/admin/courses - KURS ERSTELLEN

### 5.1 Test: Gültiger Kurs (Minimal)

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Admin Test Course",
    "description": "Created by admin for testing",
    "creator_id": 5,
    "level": "beginner",
    "language": "de"
  }'
```

**Erwartete Response:**
```json
{
  "success": true,
  "message": "Course created successfully",
  "course": {
    "course_id": 123,
    "title": "Admin Test Course",
    "description": "Created by admin for testing",
    "creator_id": 5,
    "level": "beginner",
    "language": "de",
    "price": 0.00,
    "is_public": false,
    "is_published": false,
    ...
  }
}
```

**✅ Erfolgskriterium:**
- HTTP 201
- `course.course_id` vorhanden (neu erstellt)
- `course.is_published === false` (Draft)

**Audit-Log prüfen:**
```sql
SELECT * FROM audit_logs
WHERE action = 'admin.courses.create'
ORDER BY created_at DESC
LIMIT 1;
```

---

### 5.2 Test: Gültiger Kurs (Komplett)

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Python Programming",
    "description": "Master Python with advanced concepts",
    "creator_id": 5,
    "organisation_id": null,
    "category": "programming",
    "level": "advanced",
    "language": "en",
    "price": 99.99,
    "is_public": true,
    "thumbnail_url": "https://example.com/thumb.jpg",
    "preview_video_url": "https://vimeo.com/123456",
    "tags": ["python", "advanced", "oop"]
  }'
```

**✅ Erfolgskriterium:**
- HTTP 201
- Alle Felder korrekt gesetzt

---

### 5.3 Test: Ungültiger Titel (zu kurz)

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AB",
    "creator_id": 5
  }'
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Validation error",
  "details": [
    {
      "type": "string_too_short",
      "loc": ["title"],
      "msg": "String should have at least 3 characters",
      ...
    }
  ]
}
```

**✅ Erfolgskriterium:**
- HTTP 400
- `error === "Validation error"`

---

### 5.4 Test: Ungültiger Level

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Course",
    "creator_id": 5,
    "level": "super_expert"
  }'
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Validation error",
  "details": [
    {
      "type": "value_error",
      "loc": ["level"],
      "msg": "Value error, Level must be one of: beginner, intermediate, advanced, expert",
      ...
    }
  ]
}
```

**✅ Erfolgskriterium:**
- HTTP 400
- Validation error für `level`

---

### 5.5 Test: Fehlender creator_id

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Course"
  }'
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Validation error",
  "details": [
    {
      "type": "missing",
      "loc": ["creator_id"],
      "msg": "Field required",
      ...
    }
  ]
}
```

**✅ Erfolgskriterium:**
- HTTP 400
- `creator_id` als required markiert

---

## 6. PATCH /api/v1/admin/courses/<course_id> - KURS AKTUALISIEREN

### 6.1 Test: Titel ändern

```bash
curl -X PATCH "http://localhost:5000/api/v1/admin/courses/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Grundlagen - Aktualisiert 2025"
  }'
```

**Erwartete Response:**
```json
{
  "success": true,
  "message": "Course updated successfully",
  "course": {
    "course_id": 1,
    "title": "Python Grundlagen - Aktualisiert 2025",
    ...
  }
}
```

**✅ Erfolgskriterium:**
- HTTP 200
- `course.title` ist aktualisiert
- `course.updated_at` ist aktualisiert

**Audit-Log prüfen:**
```sql
SELECT * FROM audit_logs
WHERE action = 'admin.courses.update'
  AND resource_id = '1'
ORDER BY created_at DESC
LIMIT 1;
```

---

### 6.2 Test: Mehrere Felder ändern

```bash
curl -X PATCH "http://localhost:5000/api/v1/admin/courses/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Neue Beschreibung mit mehr Details",
    "price": 59.99,
    "level": "intermediate",
    "tags": ["python", "intermediate", "2025"]
  }'
```

**✅ Erfolgskriterium:**
- HTTP 200
- Alle Felder aktualisiert

---

### 6.3 Test: Nicht-existierender Kurs

```bash
curl -X PATCH "http://localhost:5000/api/v1/admin/courses/99999" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test"
  }'
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Course not found"
}
```

**✅ Erfolgskriterium:**
- HTTP 404

---

### 6.4 Test: Ungültige Daten (Level)

```bash
curl -X PATCH "http://localhost:5000/api/v1/admin/courses/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "mega_expert"
  }'
```

**✅ Erfolgskriterium:**
- HTTP 400
- Validation error

---

## 7. POST /api/v1/admin/courses/<course_id>/status - STATUS ÄNDERN

### 7.1 Test: Kurs veröffentlichen

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "publish",
    "reason": "Quality approved by admin"
  }'
```

**Erwartete Response:**
```json
{
  "success": true,
  "message": "Course published successfully",
  "status": "published"
}
```

**✅ Erfolgskriterium:**
- HTTP 200
- `status === "published"`

**DB prüfen:**
```sql
SELECT is_published, published_at, archived_at
FROM courses
WHERE course_id = 1;
-- is_published = TRUE
-- published_at = NOW()
-- archived_at = NULL
```

**Audit-Log prüfen:**
```sql
SELECT * FROM audit_logs
WHERE action = 'admin.courses.publish'
  AND resource_id = '1'
ORDER BY created_at DESC
LIMIT 1;
-- severity = 'high'
```

---

### 7.2 Test: Veröffentlichung zurückziehen

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "unpublish",
    "reason": "Content needs revision"
  }'
```

**Erwartete Response:**
```json
{
  "success": true,
  "message": "Course unpublished successfully",
  "status": "draft"
}
```

**✅ Erfolgskriterium:**
- HTTP 200
- `status === "draft"`

**DB prüfen:**
```sql
SELECT is_published, archived_at
FROM courses
WHERE course_id = 1;
-- is_published = FALSE
-- archived_at = NULL
```

---

### 7.3 Test: Kurs archivieren

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "archive",
    "reason": "Course outdated - replaced by new version"
  }'
```

**Erwartete Response:**
```json
{
  "success": true,
  "message": "Course archived successfully",
  "status": "archived"
}
```

**✅ Erfolgskriterium:**
- HTTP 200
- `status === "archived"`

**DB prüfen:**
```sql
SELECT is_published, archived_at
FROM courses
WHERE course_id = 1;
-- is_published = FALSE
-- archived_at = NOW()
```

---

### 7.4 Test: Archivierung aufheben

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "unarchive",
    "reason": "Course content still relevant"
  }'
```

**Erwartete Response:**
```json
{
  "success": true,
  "message": "Course unarchived successfully",
  "status": "draft"
}
```

**✅ Erfolgskriterium:**
- HTTP 200
- `status === "draft"`

**DB prüfen:**
```sql
SELECT archived_at
FROM courses
WHERE course_id = 1;
-- archived_at = NULL
```

---

### 7.5 Test: Ungültige Action

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "super_publish"
  }'
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Validation error",
  "details": [
    {
      "type": "value_error",
      "loc": ["action"],
      "msg": "Value error, Action must be one of: publish, unpublish, archive, unarchive",
      ...
    }
  ]
}
```

**✅ Erfolgskriterium:**
- HTTP 400
- Validation error

---

## 8. DELETE /api/v1/admin/courses/<course_id> - KURS ARCHIVIEREN

### 8.1 Test: Kurs archivieren (Soft Delete)

```bash
curl -X DELETE "http://localhost:5000/api/v1/admin/courses/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Copyright violation reported"
  }'
```

**Erwartete Response:**
```json
{
  "success": true,
  "message": "Course archived successfully"
}
```

**✅ Erfolgskriterium:**
- HTTP 200
- Kurs ist archiviert (nicht gelöscht!)

**DB prüfen:**
```sql
SELECT * FROM courses WHERE course_id = 1;
-- Kurs existiert noch!
-- archived_at = NOW()
-- is_published = FALSE
```

**Audit-Log prüfen:**
```sql
SELECT * FROM audit_logs
WHERE action = 'admin.courses.delete'
  AND resource_id = '1'
ORDER BY created_at DESC
LIMIT 1;
-- severity = 'critical'
```

---

### 8.2 Test: Nicht-existierender Kurs

```bash
curl -X DELETE "http://localhost:5000/api/v1/admin/courses/99999" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Test"
  }'
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Course not found"
}
```

**✅ Erfolgskriterium:**
- HTTP 404

---

## 9. AUDIT-LOG-VERIFIKATION

### 9.1 Alle Admin-Kurs-Aktionen prüfen

```sql
SELECT
  log_id,
  action,
  resource_id,
  severity,
  user_email,
  metadata,
  created_at
FROM audit_logs
WHERE action LIKE 'admin.courses.%'
ORDER BY created_at DESC
LIMIT 20;
```

**✅ Erfolgskriterium:**
- Alle Aktionen sind geloggt
- `user_email` ist Admin-Email
- `metadata` enthält relevante Details (z.B. `title`, `creator_id`)

---

### 9.2 High-Severity-Aktionen prüfen

```sql
SELECT
  action,
  resource_id,
  severity,
  metadata->>'reason' AS reason,
  created_at
FROM audit_logs
WHERE action IN ('admin.courses.create', 'admin.courses.publish', 'admin.courses.delete')
  AND severity IN ('high', 'critical')
ORDER BY created_at DESC;
```

**✅ Erfolgskriterium:**
- `admin.courses.create` → severity = 'high'
- `admin.courses.publish` → severity = 'high'
- `admin.courses.delete` → severity = 'critical'

---

## 10. PERFORMANCE-TESTS

### 10.1 Test: Große Kursliste (1000+ Kurse)

```bash
time curl -X GET "http://localhost:5000/api/v1/admin/courses?per_page=100" \
  -H "Authorization: Bearer $TOKEN"
```

**✅ Erfolgskriterium:**
- Response-Zeit < 500ms (abhängig von DB-Performance)
- HTTP 200
- Keine Timeout-Fehler

---

### 10.2 Test: Komplexe Filter-Kombination

```bash
time curl -X GET "http://localhost:5000/api/v1/admin/courses?status=published&search=Python&level=beginner&sort=enrollment_count&order=desc" \
  -H "Authorization: Bearer $TOKEN"
```

**✅ Erfolgskriterium:**
- Response-Zeit < 1000ms
- HTTP 200
- Korrekte Filter-Anwendung

---

## 11. ERROR-HANDLING-TESTS

### 11.1 Test: Ungültiges JSON

```bash
curl -X POST "http://localhost:5000/api/v1/admin/courses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", invalid_json'
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Invalid JSON",
  ...
}
```

**✅ Erfolgskriterium:**
- HTTP 400
- Error-Message vorhanden

---

### 11.2 Test: Fehlender Authorization-Header

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses"
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Authentication is required to access this resource"
}
```

**✅ Erfolgskriterium:**
- HTTP 401

---

### 11.3 Test: Ungültiger JWT-Token

```bash
curl -X GET "http://localhost:5000/api/v1/admin/courses" \
  -H "Authorization: Bearer invalid_token_xyz"
```

**Erwartete Response:**
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Invalid token"
}
```

**✅ Erfolgskriterium:**
- HTTP 401

---

## 12. ZUSAMMENFASSUNG

### Test-Checklist

**Basic Tests:**
- ✅ GET /api/v1/admin/courses (Liste)
- ✅ GET /api/v1/admin/courses/<id> (Details)
- ✅ POST /api/v1/admin/courses (Erstellen)
- ✅ PATCH /api/v1/admin/courses/<id> (Aktualisieren)
- ✅ POST /api/v1/admin/courses/<id>/status (Status ändern)
- ✅ DELETE /api/v1/admin/courses/<id> (Archivieren)

**Filter & Search:**
- ✅ Status-Filter (draft, published, archived, all)
- ✅ Search (Titel/Beschreibung)
- ✅ Creator-Filter
- ✅ Pagination
- ✅ Sortierung

**Validation:**
- ✅ Titel zu kurz
- ✅ Ungültiger Level
- ✅ Fehlende Pflichtfelder
- ✅ Ungültiges JSON

**Authorization:**
- ✅ Admin hat Zugriff
- ✅ Premium-User hat keinen Zugriff
- ✅ Ungültiger Token
- ✅ Fehlender Token

**Audit-Logging:**
- ✅ Alle Aktionen geloggt
- ✅ Severity-Level korrekt
- ✅ Metadata vorhanden

**Performance:**
- ✅ Große Listen (100+ Items)
- ✅ Komplexe Filter

**Error-Handling:**
- ✅ 404 (Not Found)
- ✅ 400 (Bad Request)
- ✅ 401 (Unauthorized)
- ✅ 403 (Forbidden)

---

**TESTING-GUIDE KOMPLETT** ✅

Bei Problemen: Logs prüfen (`backend/logs/`) und DB-Zustand verifizieren.
