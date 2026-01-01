# Phase B24-04: Admin Lesson System (Backend-only)

**Version:** 1.0
**Status:** Implemented
**Date:** 2025-11-20
**Phase:** Backend Development - Admin Lesson Management

---

## Überblick

Phase B24-04 erweitert das Admin-System um **vollständige Lesson-Management-Funktionalität** als logische Fortsetzung der Course → Module → Lesson Hierarchie (aufbauend auf Phase B24-03).

**Scope:** Backend-only (keine Frontend-Änderungen in dieser Phase)

### Zielsetzung

- ✅ **Lesson CRUD**: Komplette Verwaltung von Lessons innerhalb von Modulen
- ✅ **Reorder-Funktionalität**: Drag & Drop-fähige Lesson-Sortierung
- ✅ **Permissions**: Granulare RBAC-Berechtigungen für Lesson-Operationen
- ✅ **Audit Logging**: Vollständige Protokollierung aller Admin-Aktionen
- ✅ **Bestehende Infrastruktur**: Nutzung vorhandener Lessons-Tabelle und LessonRepository

---

## Architektur

### Datenmodell

#### Bestehende Lessons-Tabelle (Migration 010)

Die `lessons` Tabelle existiert bereits mit folgendem Schema:

```sql
CREATE TABLE lessons (
    lesson_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID REFERENCES modules(module_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255),
    lesson_type VARCHAR(50) NOT NULL,
    content JSONB,
    duration_minutes INTEGER,
    order_index INTEGER NOT NULL,
    published BOOLEAN DEFAULT FALSE,
    free_preview BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_lesson_type CHECK (lesson_type IN ('text', 'video', 'quiz', 'interactive', 'assignment', 'discussion')),
    UNIQUE (module_id, order_index)
);
```

**Wichtige Felder:**
- `lesson_type`: Enum mit 6 Typen (text, video, quiz, interactive, assignment, discussion)
- `content`: JSONB für flexible Content-Struktur
- `order_index`: Sortierung innerhalb des Moduls (eindeutig pro Modul)
- `published`: Veröffentlichungsstatus
- `free_preview`: Markierung für kostenlose Vorschau-Lessons

**Unterschiede zur User-Anforderung:**
- ❌ Kein `description` Feld (kann bei Bedarf nachträglich hinzugefügt werden)
- ❌ Kein `is_mandatory` Feld (kann bei Bedarf nachträglich hinzugefügt werden)
- ✅ Nutzt `lesson_type` statt `content_type`
- ✅ Nutzt `published` (boolean) statt `status` (enum)

---

## API-Endpunkte

### 1. GET `/api/v1/admin/modules/<module_id>/lessons`

**Beschreibung:** Liste aller Lessons eines Moduls

**Berechtigung:** `ADMIN_LESSON_READ`

**Path Parameter:**
- `module_id` (integer) - Module ID

**Response (200 OK):**
```json
{
  "success": true,
  "lessons": [
    {
      "lesson_id": "550e8400-e29b-41d4-a716-446655440000",
      "module_id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Einführung in Python",
      "lesson_type": "video",
      "content": {
        "video_url": "https://...",
        "transcript": "..."
      },
      "duration_minutes": 15,
      "order_index": 1,
      "published": true,
      "free_preview": false,
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-11-19T10:00:00Z"
    }
  ]
}
```

**Fehlercodes:**
- `404 Not Found` - Module nicht gefunden
- `403 Forbidden` - Fehlende ADMIN_LESSON_READ Berechtigung

**Beispiel:**
```bash
curl -X GET "http://localhost:5000/api/v1/admin/modules/1/lessons" \
  -H "Authorization: Bearer <admin_token>"
```

---

### 2. POST `/api/v1/admin/modules/<module_id>/lessons`

**Beschreibung:** Neue Lesson erstellen

**Berechtigung:** `ADMIN_LESSON_WRITE`

**Path Parameter:**
- `module_id` (integer) - Module ID

**Request Body:**
```json
{
  "title": "Einführung in Python",
  "lesson_type": "video",
  "content": {
    "video_url": "https://...",
    "transcript": "..."
  },
  "duration_minutes": 15,
  "published": false,
  "free_preview": false
}
```

**Validierung:**
- `title` (required, min 3 characters)
- `lesson_type` (required, enum: text|video|quiz|interactive|assignment|discussion)
- `content` (optional, JSONB)
- `duration_minutes` (optional, integer, default: 0)
- `published` (optional, boolean, default: false)
- `free_preview` (optional, boolean, default: false)
- `order_index` wird automatisch vergeben (nächster freier Index)

**Response (201 Created):**
```json
{
  "success": true,
  "lesson": {
    "lesson_id": "550e8400-e29b-41d4-a716-446655440000",
    "module_id": 1,
    "title": "Einführung in Python",
    "lesson_type": "video",
    "content": {...},
    "duration_minutes": 15,
    "order_index": 3,
    "published": false,
    "free_preview": false,
    "created_at": "2025-11-20T10:00:00Z",
    "updated_at": "2025-11-20T10:00:00Z"
  }
}
```

**Fehlercodes:**
- `404 Not Found` - Module nicht gefunden
- `400 Bad Request` - Validierungsfehler (fehlender Titel oder ungültiger lesson_type)
- `403 Forbidden` - Fehlende ADMIN_LESSON_WRITE Berechtigung

**Beispiel:**
```bash
curl -X POST "http://localhost:5000/api/v1/admin/modules/1/lessons" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "lesson_type": "video",
    "content": {"video_url": "https://example.com/video.mp4"},
    "duration_minutes": 20,
    "published": true
  }'
```

---

### 3. PATCH `/api/v1/admin/lessons/<lesson_id>`

**Beschreibung:** Lesson aktualisieren

**Berechtigung:** `ADMIN_LESSON_WRITE`

**Path Parameter:**
- `lesson_id` (UUID string) - Lesson UUID

**Request Body (alle Felder optional):**
```json
{
  "title": "Updated title",
  "lesson_type": "video",
  "content": {...},
  "duration_minutes": 20,
  "published": true,
  "free_preview": false
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "lesson": {
    "lesson_id": "550e8400-e29b-41d4-a716-446655440000",
    "module_id": 1,
    "title": "Updated title",
    ...
  }
}
```

**Fehlercodes:**
- `404 Not Found` - Lesson nicht gefunden
- `400 Bad Request` - Ungültiger lesson_type
- `403 Forbidden` - Fehlende ADMIN_LESSON_WRITE Berechtigung

**Beispiel:**
```bash
curl -X PATCH "http://localhost:5000/api/v1/admin/lessons/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics - Updated",
    "published": true
  }'
```

---

### 4. DELETE `/api/v1/admin/lessons/<lesson_id>`

**Beschreibung:** Lesson löschen (Hard Delete mit CASCADE)

**Berechtigung:** `ADMIN_LESSON_DELETE`

**Path Parameter:**
- `lesson_id` (UUID string) - Lesson UUID

**Request Body (optional):**
```json
{
  "reason": "Outdated content"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Lesson deleted successfully"
}
```

**Fehlercodes:**
- `404 Not Found` - Lesson nicht gefunden
- `403 Forbidden` - Fehlende ADMIN_LESSON_DELETE Berechtigung

**Hinweis:** Löschen erfolgt als Hard Delete. Alle zugehörigen lesson_completions werden durch CASCADE automatisch gelöscht.

**Beispiel:**
```bash
curl -X DELETE "http://localhost:5000/api/v1/admin/lessons/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Duplicate content"}'
```

---

### 5. POST `/api/v1/admin/modules/<module_id>/lessons/reorder`

**Beschreibung:** Lessons neu sortieren

**Berechtigung:** `ADMIN_LESSON_WRITE`

**Path Parameter:**
- `module_id` (integer) - Module ID

**Request Body:**
```json
{
  "lesson_ids": [
    "550e8400-e29b-41d4-a716-446655440003",
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Validierung:**
- `lesson_ids` muss ein nicht-leeres Array sein
- Reihenfolge bestimmt neuen order_index (1-basiert)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Lessons reordered successfully"
}
```

**Fehlercodes:**
- `404 Not Found` - Module nicht gefunden
- `400 Bad Request` - Ungültiges oder leeres lesson_ids Array
- `403 Forbidden` - Fehlende ADMIN_LESSON_WRITE Berechtigung

**Beispiel:**
```bash
curl -X POST "http://localhost:5000/api/v1/admin/modules/1/lessons/reorder" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_ids": [
      "550e8400-e29b-41d4-a716-446655440003",
      "550e8400-e29b-41d4-a716-446655440001",
      "550e8400-e29b-41d4-a716-446655440002"
    ]
  }'
```

---

## Berechtigungen (RBAC)

### Neue Permissions (Phase B24-04)

```python
class Permissions:
    # Admin Lesson Management
    ADMIN_LESSON_READ = 'admin:lesson:read'      # List und View Lessons
    ADMIN_LESSON_WRITE = 'admin:lesson:write'    # Create, Update, Reorder
    ADMIN_LESSON_DELETE = 'admin:lesson:delete'  # Delete Lessons
```

### Rollen-Zuordnung

| Role | ADMIN_LESSON_READ | ADMIN_LESSON_WRITE | ADMIN_LESSON_DELETE |
|------|-------------------|--------------------|--------------------|
| `admin` | ✅ | ✅ | ✅ |
| `superadmin` | ✅ (via *) | ✅ (via *) | ✅ (via *) |
| `moderator` | ❌ | ❌ | ❌ |
| `support` | ❌ | ❌ | ❌ |
| `creator` | ❌ | ❌ | ❌ |

**Hinweis:** Nur `admin` und `superadmin` haben Zugriff auf Admin Lesson Management Endpoints.

---

## Repository (LessonRepository)

### Wichtige Anpassungen

Die bestehende `LessonRepository` wurde angepasst, um mit dem tatsächlichen Schema der `lessons`-Tabelle zu arbeiten:

**Alte Feldnamen (inkorrekt):**
- `content_type`, `content_url`, `content_text`, `quiz_data`, `is_preview`

**Neue Feldnamen (korrekt, Migration 010):**
- `lesson_type`, `content` (JSONB), `published`, `free_preview`

### Key Methods

```python
class LessonRepository(BaseRepository):
    @classmethod
    def create(cls, lesson_data: Dict[str, Any]) -> Dict[str, Any]:
        """Erstellt neue Lesson mit auto-assigned order_index"""

    @classmethod
    def find_by_id(cls, lesson_id: str) -> Optional[Dict[str, Any]]:
        """Findet Lesson by UUID"""

    @classmethod
    def find_by_module(cls, module_id: int) -> List[Dict[str, Any]]:
        """Alle Lessons eines Moduls, sortiert nach order_index"""

    @classmethod
    def update(cls, lesson_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Aktualisiert Lesson (setzt updated_at automatisch)"""

    @classmethod
    def delete(cls, lesson_id: str) -> bool:
        """Löscht Lesson (Hard Delete, CASCADE zu lesson_completions)"""

    @classmethod
    def reorder(cls, module_id: int, lesson_orders: List[Dict[str, int]]) -> bool:
        """Sortiert Lessons neu (aktualisiert order_index)"""
```

---

## Audit Logging

### Protokollierte Aktionen

Alle Admin-Lesson-Operationen werden über den `AuditService` protokolliert:

| Aktion | Kategorie | Severity | Details |
|--------|-----------|----------|---------|
| `admin.lessons.list` | `module` | `info` | `lesson_count`, `module_title` |
| `admin.lessons.create` | `lesson` | `info` | `module_id`, `lesson_title`, `lesson_type`, `module_title` |
| `admin.lessons.update` | `lesson` | `info` | `lesson_title`, `module_id`, `changes` |
| `admin.lessons.delete` | `lesson` | `high` | `reason`, `lesson_title`, `module_id` |
| `admin.lessons.reorder` | `module` | `info` | `module_title`, `new_order` |

**Beispiel Audit-Log-Eintrag:**
```json
{
  "user_id": "admin-uuid",
  "action": "admin.lessons.create",
  "resource_type": "lesson",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "details": {
    "module_id": 1,
    "lesson_title": "Python Basics",
    "lesson_type": "video",
    "module_title": "Einführung"
  },
  "severity": "info",
  "timestamp": "2025-11-20T10:00:00Z"
}
```

---

## Implementierte Dateien

### Backend Code Changes

**1. Permissions (`backend/app/security/permissions.py`)**
```python
# Neue Permissions hinzugefügt
ADMIN_LESSON_READ = 'admin:lesson:read'
ADMIN_LESSON_WRITE = 'admin:lesson:write'
ADMIN_LESSON_DELETE = 'admin:lesson:delete'

# Rollen-Matrix erweitert
'admin': {
    ...
    Permissions.ADMIN_LESSON_READ,
    Permissions.ADMIN_LESSON_WRITE,
    Permissions.ADMIN_LESSON_DELETE,
}
```

**2. API Endpoints (`backend/app/api/admin_courses.py`)**
```python
# Import LessonRepository hinzugefügt
from app.repositories.lesson_repository import LessonRepository

# 5 neue Endpunkte implementiert
@api_v1.route('/admin/modules/<int:module_id>/lessons', methods=['GET'])
@api_v1.route('/admin/modules/<int:module_id>/lessons', methods=['POST'])
@api_v1.route('/admin/lessons/<lesson_id>', methods=['PATCH'])
@api_v1.route('/admin/lessons/<lesson_id>', methods=['DELETE'])
@api_v1.route('/admin/modules/<int:module_id>/lessons/reorder', methods=['POST'])
```

**3. Repository Fix (`backend/app/repositories/lesson_repository.py`)**
- Schema-Anpassung: `content_type` → `lesson_type`
- Schema-Anpassung: `is_preview` → `free_preview`
- Schema-Anpassung: Entfernt `content_url`, `content_text`, `quiz_data` → vereinheitlicht zu `content` (JSONB)

---

## Testing

### Manuelle Tests (cURL)

**Voraussetzung:** Admin-JWT-Token holen:
```bash
# Login als Admin
curl -X POST "http://localhost:5000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@lernsystem.com", "password": "AdminPass123!"}' \
  | jq -r '.data.access_token'
```

**Test 1: Lessons auflisten**
```bash
curl -X GET "http://localhost:5000/api/v1/admin/modules/1/lessons" \
  -H "Authorization: Bearer <admin_token>"
```

**Test 2: Lesson erstellen**
```bash
curl -X POST "http://localhost:5000/api/v1/admin/modules/1/lessons" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Lesson",
    "lesson_type": "text",
    "content": {"text": "This is a test lesson"},
    "duration_minutes": 10,
    "published": false
  }'
```

**Test 3: Lesson aktualisieren**
```bash
curl -X PATCH "http://localhost:5000/api/v1/admin/lessons/<lesson_uuid>" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Test Lesson",
    "published": true
  }'
```

**Test 4: Lessons neu sortieren**
```bash
curl -X POST "http://localhost:5000/api/v1/admin/modules/1/lessons/reorder" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_ids": ["uuid3", "uuid1", "uuid2"]
  }'
```

**Test 5: Lesson löschen**
```bash
curl -X DELETE "http://localhost:5000/api/v1/admin/lessons/<lesson_uuid>" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Test cleanup"
  }'
```

---

## Known Limitations

### 1. Schema-Unterschiede zur Anforderung

**Fehlende Felder (können bei Bedarf nachgerüstet werden):**
- ❌ `description` (TEXT) - Aktuell nicht in lessons-Tabelle
- ❌ `is_mandatory` (BOOLEAN) - Aktuell nicht in lessons-Tabelle

**Unterschiedliche Felder:**
- ℹ️ `lesson_type` statt `content_type` (funktional identisch)
- ℹ️ `published` (boolean) statt `status` (enum: draft/published/archived)

**Empfehlung:** Falls `description` und `is_mandatory` benötigt werden, sollte eine neue Migration (046) erstellt werden:
```sql
ALTER TABLE lessons
  ADD COLUMN description TEXT,
  ADD COLUMN is_mandatory BOOLEAN DEFAULT TRUE;
```

### 2. Keine Soft Delete

Lessons werden als **Hard Delete** gelöscht (mit CASCADE zu `lesson_completions`).

**Alternative für Soft Delete:**
- Nutze `published = false` + `archived_at TIMESTAMPTZ` Feld
- Oder implementiere separates `status` Enum mit `archived` Zustand

### 3. Frontend Integration

Phase B24-04 ist **Backend-only**. Für vollständige Lesson-Management-UI sind zusätzliche Frontend-Änderungen erforderlich:
- Lesson-Tab in AdminCourseDetailPage
- Lesson Editor Modal
- Lesson Drag & Drop Reordering

---

## Zusammenfassung

### ✅ Erfolgreich Implementiert

| Feature | Status |
|---------|--------|
| **5 API Endpoints** | ✅ Vollständig implementiert |
| **RBAC Permissions** | ✅ 3 neue Permissions, Admin-Rolle erweitert |
| **Audit Logging** | ✅ Alle 5 Aktionen protokolliert |
| **LessonRepository** | ✅ Schema-korrekt angepasst |
| **Validation** | ✅ Titel & lesson_type Validierung |
| **Auto Order Index** | ✅ Automatische Zuweisung bei CREATE |
| **Reorder Support** | ✅ Bulk reorder mit order_index Update |
| **Hard Delete** | ✅ Mit CASCADE zu lesson_completions |

### 📊 Statistik

- **Lines of Code:** ~420 Zeilen (admin_courses.py)
- **API Endpoints:** 5 neue Endpunkte
- **Permissions:** 3 neue Permissions
- **Repositories:** 1 angepasst (LessonRepository)
- **Migrations:** 0 (nutzt bestehende Migration 010)
- **Documentation:** Vollständig (diese Datei)

---

## Nächste Schritte (Optional)

### Frontend Integration (zukünftige Phase)

Für vollständiges Admin Lesson Management sollte das Frontend erweitert werden:

1. **AdminCourseDetailPage.vue erweitern:**
   - Neuer Tab "Lessons" (neben Module & Einstellungen)
   - Lesson-Liste mit Drag & Drop Reordering
   - Create/Edit Lesson Modal
   - Delete Confirmation

2. **admin.api.ts erweitern:**
   ```typescript
   // Lesson Management
   adminListLessons(moduleId: number): Promise<ApiResponse<Lesson[]>>
   adminCreateLesson(moduleId: number, data: LessonCreateRequest): Promise<ApiResponse<Lesson>>
   adminUpdateLesson(lessonId: string, data: LessonUpdateRequest): Promise<ApiResponse<Lesson>>
   adminDeleteLesson(lessonId: string, reason?: string): Promise<ApiResponse<void>>
   adminReorderLessons(moduleId: number, lessonIds: string[]): Promise<ApiResponse<void>>
   ```

3. **admin.store.ts erweitern:**
   - Lesson-State Management
   - Optimistic UI Updates
   - Error Handling

### Schema Erweiterungen (Optional)

Falls benötigt, Migration 046 erstellen:
```sql
-- Migration 046: Extend lessons table
ALTER TABLE lessons
  ADD COLUMN description TEXT,
  ADD COLUMN is_mandatory BOOLEAN DEFAULT TRUE,
  ADD COLUMN archived_at TIMESTAMPTZ;

-- Soft Delete Support
CREATE INDEX idx_lessons_archived ON lessons(archived_at) WHERE archived_at IS NULL;
```

---

## Dokumentation References

- **Phase B24-02:** Admin Course Management (Courses)
- **Phase B24-03:** Admin Module Management (Modules + Categories)
- **Phase B24-04:** Admin Lesson Management (Lessons) ← Diese Phase
- **Migration 010:** lessons + lesson_completions Tabellen
- **Dok 04:** Kurs-Architektur (Hierarchie Course → Module → Lesson)
- **Dok 18:** Editor-System (Lesson Content Types)
- **Dok 24:** Admin-System (Überblick Admin-Funktionalität)

---

**Ende der Dokumentation Phase B24-04**
