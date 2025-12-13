# Phase B24-05: AI Course Generator System

**Version:** 1.0
**Status:** Implemented
**Date:** 2025-11-20
**Phase:** Backend Development - AI-Powered Course Generation

---

## Überblick

Phase B24-05 implementiert ein vollständiges **KI-Job-System für automatische Kursgenerierung** aus PDF-Dateien mit Live-Progress-Tracking, Multi-Provider AI-Integration und strukturierter Course/Module/Lesson-Erstellung.

**Scope:** Backend-only (keine Frontend-Änderungen in dieser Phase)

### Zielsetzung

- ✅ **AI Job Management**: Job-System für asynchrone AI-Operationen
- ✅ **PDF → Course**: Automatische Kurserstellung aus PDF-Dokumenten
- ✅ **Live Progress**: Echtzeit-Fortschrittsanzeige (0-100%)
- ✅ **Multi-Provider AI**: OpenAI, Anthropic, Google, Cohere, HuggingFace
- ✅ **Module/Lesson Generation**: Strukturierte Content-Hierarchie
- ✅ **Finalize Workflow**: Zwei-Schritt-Prozess (Generate → Review → Finalize)
- ✅ **Permissions & Audit**: Granulare RBAC + vollständiges Logging

---

## Architektur

### System-Komponenten

```
┌─────────────────────────────────────────────────────────────┐
│                        Admin API                             │
│  POST /api/v1/admin/ai/jobs         (Create AI Job)        │
│  GET  /api/v1/admin/ai/jobs/<id>    (Get Status)           │
│  POST /api/v1/admin/ai/jobs/<id>/cancel                     │
│  POST /api/v1/admin/ai/jobs/<id>/finalize                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AIJobService                              │
│  • create_job()      • update_status()                      │
│  • update_progress() • fail_job()                           │
│  • complete_job()    • cancel_job()                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  AICourseGenerator (Worker)                  │
│  1. Extract PDF Text                                         │
│  2. AI: Generate Title                                       │
│  3. AI: Suggest Category                                     │
│  4. AI: Create Description                                   │
│  5. AI: Generate Modules (3-6)                              │
│  6. AI: Generate Lessons per Module (3-5)                   │
│  7. Save to output_data (JSONB)                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      AIAdapter                               │
│  Multi-Provider: OpenAI | Anthropic | Google | Cohere | HF │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   AIJobRepository                            │
│            PostgreSQL: ai_jobs table                         │
└─────────────────────────────────────────────────────────────┘
```

### Workflow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ PENDING  │────▶│PROCESSING│────▶│COMPLETED │────▶│FINALIZED │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                       │                 │
                       │                 │
                       ▼                 ▼
                 ┌──────────┐     ┌──────────┐
                 │  FAILED  │     │CANCELLED │
                 └──────────┘     └──────────┘

Status Flow:
1. PENDING    → Job created, waiting to start
2. PROCESSING → AI worker active, progress 0-100%
3. COMPLETED  → AI finished, output_data ready
4. CANCELLED  → Manually stopped by admin
5. FAILED     → Error occurred, error_message set
```

---

## Datenmodell

### Tabelle: ai_jobs (Migration 046)

```sql
CREATE TABLE ai_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    course_id UUID NULL REFERENCES courses(course_id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    progress INT DEFAULT 0,
    input_file VARCHAR(255),
    input_prompt TEXT,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_ai_job_type CHECK (type IN (
        'course_from_pdf',
        'module_autogen',
        'lesson_autogen'
    )),

    CONSTRAINT chk_ai_job_status CHECK (status IN (
        'pending',
        'processing',
        'completed',
        'failed',
        'cancelled'
    )),

    CONSTRAINT chk_progress_range CHECK (progress >= 0 AND progress <= 100)
);
```

**Felderbeschreibung:**

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Job-ID (Primary Key) |
| `user_id` | UUID | User der den Job erstellt hat |
| `course_id` | UUID | Verknüpfter Kurs (nach Finalize) |
| `type` | VARCHAR(50) | Job-Typ (course_from_pdf, module_autogen, lesson_autogen) |
| `status` | VARCHAR(30) | Job-Status (pending, processing, completed, failed, cancelled) |
| `progress` | INT | Fortschritt 0-100% |
| `input_file` | VARCHAR(255) | PDF-Dateiname oder Pfad |
| `input_prompt` | TEXT | Optionale User-Anweisung für AI |
| `output_data` | JSONB | Generierte Kurs-Struktur (JSON) |
| `error_message` | TEXT | Fehlermeldung bei Status=failed |
| `created_at` | TIMESTAMPTZ | Erstellungszeitpunkt |
| `updated_at` | TIMESTAMPTZ | Letztes Update (Auto-Trigger) |

### Output Data Schema (JSONB)

```json
{
  "course": {
    "title": "Python Grundlagen für Anfänger",
    "description": "Lerne Python von Grund auf...",
    "category": "programming",
    "level": "beginner",
    "language": "de"
  },
  "modules": [
    {
      "title": "Modul 1: Einführung",
      "description": "Grundlagen und Setup",
      "duration_minutes": 45,
      "order_index": 1,
      "lessons": [
        {
          "title": "Lektion 1: Was ist Python?",
          "lesson_type": "text",
          "duration_minutes": 15,
          "order_index": 1
        },
        {
          "title": "Lektion 2: Installation",
          "lesson_type": "video",
          "duration_minutes": 20,
          "order_index": 2
        },
        {
          "title": "Lektion 3: Erstes Programm",
          "lesson_type": "interactive",
          "duration_minutes": 10,
          "order_index": 3
        }
      ]
    },
    {
      "title": "Modul 2: Variablen & Datentypen",
      "description": "Grundlegende Konzepte",
      "duration_minutes": 60,
      "order_index": 2,
      "lessons": [...]
    }
  ]
}
```

---

## API-Endpunkte

### 1. POST `/api/v1/admin/ai/jobs`

**Beschreibung:** Erstellt neuen AI Job und startet Worker

**Berechtigung:** `ADMIN_AI_JOBS_WRITE`

**Request Body:**
```json
{
  "type": "course_from_pdf",
  "file_name": "python_basics.pdf",
  "prompt": "Erstelle einen Anfängerkurs für Python mit Fokus auf Praxis",
  "course_id": null
}
```

**Validierung:**
- `type` (required): Enum: `course_from_pdf` | `module_autogen` | `lesson_autogen`
- `file_name` (optional, max 255 chars): PDF-Dateiname
- `prompt` (optional, max 5000 chars): User-Anweisung
- `course_id` (optional, UUID): Für module/lesson generation

**Response (201 Created):**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Fehlercodes:**
- `400 Bad Request` - Validierungsfehler (ungültiger type)
- `403 Forbidden` - Fehlende ADMIN_AI_JOBS_WRITE Berechtigung

**Beispiel:**
```bash
curl -X POST "http://localhost:5000/api/v1/admin/ai/jobs" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "course_from_pdf",
    "file_name": "python_basics.pdf",
    "prompt": "Erstelle einen Python Anfängerkurs"
  }'
```

**Hintergrund-Prozess:**
- Job wird mit `status=pending` erstellt
- Worker startet in separatem Thread
- Worker durchläuft 7 Schritte (PDF → Titel → Kategorie → Beschreibung → Module → Lessons)
- Progress wird von 0% → 100% aktualisiert
- Bei Erfolg: `status=completed`, `output_data` gefüllt
- Bei Fehler: `status=failed`, `error_message` gesetzt

---

### 2. GET `/api/v1/admin/ai/jobs/<job_id>`

**Beschreibung:** Holt Job-Status und Output-Daten

**Berechtigung:** `ADMIN_AI_JOBS_READ`

**Path Parameter:**
- `job_id` (UUID) - Job-ID

**Response (200 OK):**
```json
{
  "success": true,
  "job": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user-uuid",
    "course_id": null,
    "type": "course_from_pdf",
    "status": "processing",
    "progress": 65,
    "input_file": "python_basics.pdf",
    "input_prompt": "Erstelle einen Python Anfängerkurs",
    "output_data": null,
    "error_message": null,
    "created_at": "2025-11-20T10:00:00Z",
    "updated_at": "2025-11-20T10:05:23Z",
    "user_email": "admin@lernsystem.com",
    "course_title": null
  }
}
```

**Status-Werte:**
- `pending` - Job wartet auf Start
- `processing` - AI arbeitet, siehe `progress` (0-100%)
- `completed` - Fertig, `output_data` verfügbar
- `failed` - Fehler, siehe `error_message`
- `cancelled` - Abgebrochen

**Fehlercodes:**
- `404 Not Found` - Job nicht gefunden
- `403 Forbidden` - Fehlende ADMIN_AI_JOBS_READ Berechtigung

**Beispiel:**
```bash
curl "http://localhost:5000/api/v1/admin/ai/jobs/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <admin_token>"
```

---

### 3. POST `/api/v1/admin/ai/jobs/<job_id>/cancel`

**Beschreibung:** Bricht laufenden Job ab

**Berechtigung:** `ADMIN_AI_JOBS_EXECUTE`

**Path Parameter:**
- `job_id` (UUID) - Job-ID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Job cancelled successfully"
}
```

**Hinweise:**
- Nur möglich bei `status=pending` oder `status=processing`
- Bei `completed`/`failed`/`cancelled` → 404 Error
- Setzt `status=cancelled` und `updated_at=NOW()`

**Fehlercodes:**
- `404 Not Found` - Job nicht gefunden oder bereits abgeschlossen
- `403 Forbidden` - Fehlende ADMIN_AI_JOBS_EXECUTE Berechtigung

**Beispiel:**
```bash
curl -X POST "http://localhost:5000/api/v1/admin/ai/jobs/550e8400-e29b-41d4-a716-446655440000/cancel" \
  -H "Authorization: Bearer <admin_token>"
```

---

### 4. POST `/api/v1/admin/ai/jobs/<job_id>/finalize`

**Beschreibung:** Erstellt echten Kurs/Module/Lessons aus AI-Output

**Berechtigung:** `ADMIN_AI_JOBS_EXECUTE`

**Path Parameter:**
- `job_id` (UUID) - Job-ID

**Request Body:**
```json
{
  "create_course": true,
  "create_modules": true,
  "create_lessons": true,
  "override_existing": false
}
```

**Validierung:**
- Job muss `status=completed` haben
- `output_data` muss vorhanden sein
- `create_course` muss `true` sein (Pflicht)

**Response (200 OK):**
```json
{
  "success": true,
  "course_id": "new-course-uuid",
  "modules_created": 4,
  "lessons_created": 18
}
```

**Workflow:**
1. Prüft Job-Status (`completed`)
2. Liest `output_data` aus Job
3. Erstellt Kurs via `CourseRepository.admin_create_course()`
4. Erstellt Module via `ModuleRepository.create()` (für jedes Modul in output_data)
5. Erstellt Lessons via `LessonRepository.create()` (für jede Lesson in jedem Modul)
6. Verknüpft `course_id` mit Job via `AIJobService.attach_course()`
7. Audit-Log mit `severity=high`

**Fehlercodes:**
- `404 Not Found` - Job nicht gefunden
- `400 Bad Request` - Job nicht completed oder kein output_data
- `403 Forbidden` - Fehlende ADMIN_AI_JOBS_EXECUTE Berechtigung

**Beispiel:**
```bash
curl -X POST "http://localhost:5000/api/v1/admin/ai/jobs/550e8400-e29b-41d4-a716-446655440000/finalize" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "create_course": true,
    "create_modules": true,
    "create_lessons": true
  }'
```

---

## AI Worker (AICourseGenerator)

### Workflow-Schritte

```python
1. Extract PDF Text (Progress: 10%)
   └─ Placeholder: PyPDF2/pdfplumber (TODO)

2. Generate Course Title (Progress: 30%)
   └─ AI Prompt: "Generate concise course title (max 100 chars)"
   └─ Fallback: "AI-Generated Course"

3. Suggest Category (Progress: 40%)
   └─ AI Prompt: "Suggest category from: programming, business, design, ..."
   └─ Fallback: "other"

4. Create Description (Progress: 50%)
   └─ AI Prompt: "Create compelling description (2-3 sentences, max 300 chars)"
   └─ Fallback: "Lerne alles über {title}..."

5. Generate Module Structure (Progress: 70%)
   └─ AI Prompt: "Create logical module structure (3-6 modules) as JSON"
   └─ Fallback: 3 Standard-Module

6. Generate Lessons per Module (Progress: 90%)
   └─ AI Prompt: "Create 3-5 lessons for module as JSON"
   └─ Fallback: 3 Standard-Lessons

7. Save Output & Complete (Progress: 100%)
   └─ output_data = {course: {...}, modules: [...]}
   └─ Status = completed
```

### AI-Prompts

**Titel-Generierung:**
```
Analyze this educational content and generate a concise, descriptive
course title (max 100 characters).

Content summary:
{pdf_text[:1000]}

User instruction: {user_prompt}

Respond with ONLY the course title, nothing else.
```

**Kategorie-Vorschlag:**
```
Based on this course title and content, suggest the most appropriate
category from this list:
- programming, business, design, marketing, languages, science,
  mathematics, health, personal-development, other

Course title: {course_title}
Content: {pdf_text[:500]}

Respond with ONLY the category name (lowercase, hyphenated).
```

**Modul-Struktur:**
```
Analyze this course content and create a logical module structure (3-6 modules).

Course: {course_title}
Content: {pdf_text[:2000]}

Return a JSON array of modules with this format:
[
  {"title": "Module 1: Introduction", "description": "Overview and basics", "duration_minutes": 45},
  {"title": "Module 2: Core Concepts", "description": "Main topics", "duration_minutes": 60}
]

Respond with ONLY valid JSON, nothing else.
```

**Lesson-Generierung:**
```
Create 3-5 lessons for this module:

Module: {module['title']}
Description: {module['description']}
Context: {pdf_text[:1000]}

Return a JSON array of lessons with this format:
[
  {"title": "Lesson 1: Introduction", "lesson_type": "text", "duration_minutes": 15},
  {"title": "Lesson 2: Practice", "lesson_type": "quiz", "duration_minutes": 20}
]

Valid lesson_types: text, video, quiz, interactive, assignment, discussion
Respond with ONLY valid JSON, nothing else.
```

### Fallback-Mechanismen

**Bei AI-Fehler (Timeout, Quota, Parse-Error):**

```python
# Fallback Module Structure
[
  {'title': 'Modul 1: Einführung', 'description': 'Grundlagen und Überblick', 'duration_minutes': 45},
  {'title': 'Modul 2: Hauptthemen', 'description': 'Kernkonzepte', 'duration_minutes': 60},
  {'title': 'Modul 3: Praxis', 'description': 'Übungen und Anwendungen', 'duration_minutes': 60}
]

# Fallback Lesson Structure
[
  {'title': 'Lektion 1: Einführung', 'lesson_type': 'text', 'duration_minutes': 15},
  {'title': 'Lektion 2: Konzepte', 'lesson_type': 'text', 'duration_minutes': 20},
  {'title': 'Lektion 3: Quiz', 'lesson_type': 'quiz', 'duration_minutes': 10}
]
```

### Error Handling

```python
try:
    # AI Generation Steps
    ...
except AIProviderError as e:
    AIJobService.fail_job(job_id, f'AI provider error: {str(e)}')
except AITimeoutError as e:
    AIJobService.fail_job(job_id, f'AI timeout: {str(e)}')
except Exception as e:
    AIJobService.fail_job(job_id, f'Unexpected error: {str(e)}')
```

---

## Berechtigungen (RBAC)

### Neue Permissions (Phase B24-05)

```python
class Permissions:
    # Admin AI Job Management
    ADMIN_AI_JOBS_READ = 'admin:ai:jobs:read'      # List und View Jobs
    ADMIN_AI_JOBS_WRITE = 'admin:ai:jobs:write'    # Create Jobs
    ADMIN_AI_JOBS_EXECUTE = 'admin:ai:jobs:execute' # Cancel & Finalize
```

### Rollen-Zuordnung

| Role | ADMIN_AI_JOBS_READ | ADMIN_AI_JOBS_WRITE | ADMIN_AI_JOBS_EXECUTE |
|------|-------------------|--------------------|-----------------------|
| `admin` | ✅ | ✅ | ✅ |
| `superadmin` | ✅ (via *) | ✅ (via *) | ✅ (via *) |
| `moderator` | ❌ | ❌ | ❌ |
| `creator` | ❌ | ❌ | ❌ |

**Hinweis:** Nur `admin` und `superadmin` haben Zugriff auf AI Job Management.

---

## Services & Repositories

### AIJobService

**Zweck:** Business Logic für AI Jobs

**Key Methods:**
```python
class AIJobService:
    # Job Creation
    @staticmethod
    def create_job(user_id, job_type, input_file, input_prompt, course_id) -> Dict

    # Status Management
    @staticmethod
    def update_status(job_id, status) -> Dict
    @staticmethod
    def update_progress(job_id, progress) -> Dict
    @staticmethod
    def start_processing(job_id) -> Dict

    # Output Management
    @staticmethod
    def update_output(job_id, output_data) -> Dict
    @staticmethod
    def attach_course(job_id, course_id) -> Dict

    # Error & Cancel
    @staticmethod
    def fail_job(job_id, error_message) -> Dict
    @staticmethod
    def cancel_job(job_id) -> Dict
    @staticmethod
    def complete_job(job_id, output_data) -> Dict

    # Query
    @staticmethod
    def get_job(job_id) -> Dict
    @staticmethod
    def get_user_jobs(user_id, limit=50) -> List[Dict]
    @staticmethod
    def get_job_stats(user_id) -> Dict
```

### AIJobRepository

**Zweck:** Data Access Layer für ai_jobs Tabelle

**Key Methods:**
```python
class AIJobRepository:
    @classmethod
    def create(cls, job_data) -> Dict
    @classmethod
    def find_by_id(cls, job_id) -> Optional[Dict]
    @classmethod
    def find_by_user(cls, user_id, limit=50) -> List[Dict]
    @classmethod
    def find_by_status(cls, status, limit=100) -> List[Dict]

    @classmethod
    def update_status(cls, job_id, status) -> Optional[Dict]
    @classmethod
    def update_progress(cls, job_id, progress) -> Optional[Dict]
    @classmethod
    def update_output(cls, job_id, output_data) -> Optional[Dict]
    @classmethod
    def attach_course(cls, job_id, course_id) -> Optional[Dict]

    @classmethod
    def fail_job(cls, job_id, error_message) -> Optional[Dict]
    @classmethod
    def cancel_job(cls, job_id) -> Optional[Dict]
    @classmethod
    def complete_job(cls, job_id, output_data) -> Optional[Dict]

    @classmethod
    def delete(cls, job_id) -> bool
    @classmethod
    def get_stats_by_user(cls, user_id) -> Dict
    @classmethod
    def get_recent_jobs(cls, limit=20) -> List[Dict]
```

---

## Audit Logging

### Protokollierte Aktionen

| Aktion | Kategorie | Severity | Details |
|--------|-----------|----------|---------|
| `admin.ai.job.create` | `ai_job` | `info` | `type`, `file_name` |
| `admin.ai.job.cancel` | `ai_job` | `medium` | `job_id` |
| `admin.ai.job.finalize` | `ai_job` | `high` | `course_id`, `modules_created`, `lessons_created` |

**Beispiel Audit-Log (Finalize):**
```json
{
  "user_id": "admin-uuid",
  "action": "admin.ai.job.finalize",
  "resource_type": "ai_job",
  "resource_id": "job-uuid",
  "details": {
    "course_id": "course-uuid",
    "modules_created": 4,
    "lessons_created": 18
  },
  "severity": "high",
  "timestamp": "2025-11-20T10:30:00Z"
}
```

---

## Testing

### Manueller Test-Workflow

**Schritt 1: AI Job erstellen**
```bash
curl -X POST "http://localhost:5000/api/v1/admin/ai/jobs" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "type": "course_from_pdf",
    "file_name": "python_intro.pdf",
    "prompt": "Erstelle einen 4-stündigen Python Kurs für absolute Anfänger"
  }'

# Response:
# {"success": true, "job_id": "550e8400-e29b-41d4-a716-446655440000"}
```

**Schritt 2: Status prüfen (mehrmals)**
```bash
# Nach 10 Sekunden
curl "http://localhost:5000/api/v1/admin/ai/jobs/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJ..."

# Response: {"success": true, "job": {"status": "processing", "progress": 30, ...}}

# Nach 30 Sekunden
curl "http://localhost:5000/api/v1/admin/ai/jobs/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJ..."

# Response: {"success": true, "job": {"status": "processing", "progress": 70, ...}}

# Nach 60 Sekunden
curl "http://localhost:5000/api/v1/admin/ai/jobs/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJ..."

# Response: {"success": true, "job": {"status": "completed", "progress": 100, "output_data": {...}}}
```

**Schritt 3: Output-Data inspizieren**
```bash
curl "http://localhost:5000/api/v1/admin/ai/jobs/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJ..." | jq '.job.output_data'

# Response:
# {
#   "course": {
#     "title": "Python Programmierung für Anfänger",
#     "description": "Lerne Python von Grund auf...",
#     "category": "programming",
#     ...
#   },
#   "modules": [
#     {
#       "title": "Modul 1: Einführung",
#       "lessons": [...]
#     }
#   ]
# }
```

**Schritt 4: Kurs finalisieren**
```bash
curl -X POST "http://localhost:5000/api/v1/admin/ai/jobs/550e8400-e29b-41d4-a716-446655440000/finalize" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "create_course": true,
    "create_modules": true,
    "create_lessons": true
  }'

# Response:
# {
#   "success": true,
#   "course_id": "new-course-uuid",
#   "modules_created": 4,
#   "lessons_created": 17
# }
```

**Schritt 5: Kurs verifizieren**
```bash
curl "http://localhost:5000/api/v1/admin/courses/new-course-uuid" \
  -H "Authorization: Bearer eyJ..."
```

### Fehlerfall-Tests

**Test 1: Ungültiger Job-Typ**
```bash
curl -X POST "http://localhost:5000/api/v1/admin/ai/jobs" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"type": "invalid_type"}'

# Expected: 400 Bad Request
# {"success": false, "error": "Validation error", "details": [...]}
```

**Test 2: Job abbrechen**
```bash
# Job erstellen
curl -X POST "http://localhost:5000/api/v1/admin/ai/jobs" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"type": "course_from_pdf", "file_name": "test.pdf"}'

# Response: {"job_id": "job-uuid"}

# Sofort abbrechen
curl -X POST "http://localhost:5000/api/v1/admin/ai/jobs/job-uuid/cancel" \
  -H "Authorization: Bearer eyJ..."

# Expected: 200 OK
# {"success": true, "message": "Job cancelled successfully"}
```

**Test 3: Finalize ohne completed Status**
```bash
# Job erstellen (läuft noch)
curl -X POST "http://localhost:5000/api/v1/admin/ai/jobs" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"type": "course_from_pdf", "file_name": "test.pdf"}'

# Sofort finalisieren (sollte fehlschlagen)
curl -X POST "http://localhost:5000/api/v1/admin/ai/jobs/job-uuid/finalize" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"create_course": true}'

# Expected: 400 Bad Request
# {"success": false, "error": "Job must be completed (current status: processing)"}
```

---

## Known Limitations

### 1. PDF-Parsing nicht implementiert

**Aktuell:** Placeholder-Funktion gibt statischen Text zurück
```python
def _extract_pdf_text(self, file_path):
    return "Sample course content from PDF about Python programming basics."
```

**TODO:** Implementierung mit:
- **PyPDF2**: Text-basierte PDFs
- **pdfplumber**: Bessere Formatierung
- **Tesseract OCR**: Gescannte PDFs
- **Strukturerkennung**: Kapitel/Überschriften erkennen

### 2. Kein File-Upload

**Aktuell:** User gibt nur `file_name` als String an

**TODO:** Multipart-Upload implementieren:
```python
@api_v1.route('/admin/ai/upload-pdf', methods=['POST'])
def upload_pdf():
    file = request.files['pdf']
    # Speichern, Validieren (max 50MB, nur PDF)
    # Rückgabe: file_path für Job
```

### 3. Synchrone Ausführung in Thread

**Aktuell:** Worker läuft in `threading.Thread` (daemon)

**Problem:**
- Bei Server-Neustart gehen Jobs verloren
- Keine Retry-Logik
- Keine Job-Queue

**TODO:** Migration zu Celery/RQ:
```python
@celery.task
def run_ai_course_generation_task(job_id):
    generator = AICourseGenerator(job_id)
    return generator.run()
```

### 4. Basis AI-Prompts

**Aktuell:** Einfache Prompts ohne Few-Shot Examples

**TODO:**
- Few-Shot Learning mit Beispielen
- Structured Output (JSON Schema Validation)
- Chain-of-Thought Prompting
- Prompt-Templates aus Datenbank

### 5. Keine Job-Queue

**Aktuell:** Alle Jobs starten sofort

**TODO:**
- Max concurrent jobs (z.B. 5 gleichzeitig)
- Priority Queue (Premium-User zuerst)
- Rate Limiting (max 10 Jobs/Stunde pro User)

---

## Zukünftige Erweiterungen

### Phase 2: Module-Autogen

```python
# Job-Type: module_autogen
# Generiert zusätzliche Module für bestehenden Kurs

POST /api/v1/admin/ai/jobs
{
  "type": "module_autogen",
  "course_id": "existing-course-uuid",
  "prompt": "Erstelle 2 fortgeschrittene Module über Async/Await"
}
```

### Phase 3: Lesson-Autogen

```python
# Job-Type: lesson_autogen
# Generiert zusätzliche Lessons für bestehendes Modul

POST /api/v1/admin/ai/jobs
{
  "type": "lesson_autogen",
  "course_id": "course-uuid",
  "module_id": "module-uuid",
  "prompt": "Erstelle 3 interaktive Lessons über List Comprehensions"
}
```

### Phase 4: Content-Enrichment

- **Video-URLs generieren**: AI schlägt passende YouTube-Videos vor
- **Quiz-Fragen**: Automatische Multiple-Choice Generierung
- **Code-Beispiele**: Syntax-highlighted Code-Snippets
- **Übungen**: Programmieraufgaben mit Musterlösungen

### Phase 5: Multi-Language Support

```python
# AI übersetzt generierten Kurs automatisch
POST /api/v1/admin/ai/jobs/<job_id>/translate
{
  "target_languages": ["en", "es", "fr"]
}
# Erstellt 3 Kurskopien in anderen Sprachen
```

---

## Zusammenfassung

### ✅ Erfolgreich Implementiert

| Feature | Status |
|---------|--------|
| **AI Job System** | ✅ Vollständig mit CRUD |
| **4 API Endpoints** | ✅ Create, Get, Cancel, Finalize |
| **Live Progress** | ✅ 0-100% Tracking |
| **Multi-Provider AI** | ✅ OpenAI, Anthropic, Google, Cohere, HF |
| **7-Step Workflow** | ✅ PDF → Titel → Kategorie → Beschreibung → Module → Lessons |
| **JSONB Output** | ✅ Strukturierte Course-Daten |
| **Fallback-Mechanismen** | ✅ Bei AI-Fehlern |
| **RBAC Permissions** | ✅ 3 neue Permissions |
| **Audit Logging** | ✅ Alle Operationen protokolliert |
| **Repository Pattern** | ✅ Saubere Datenzugriffe |
| **Pydantic Validation** | ✅ Request/Response Models |
| **Migration 046** | ✅ ai_jobs Tabelle mit Constraints |

### 📊 Statistik

| Metrik | Wert |
|--------|------|
| **Dateien erstellt** | 7 (Migration, Repo, Service, Worker, Models, __init__, Endpoints) |
| **Dateien erweitert** | 2 (permissions.py, admin_courses.py) |
| **Lines of Code** | ~1.500 Zeilen |
| **API Endpoints** | 4 neue Admin-Endpoints |
| **Permissions** | 3 neue Permissions (READ, WRITE, EXECUTE) |
| **Database Tables** | 1 neue Tabelle (ai_jobs) |
| **Job Types** | 3 (course_from_pdf, module_autogen, lesson_autogen) |
| **Job Statuses** | 5 (pending, processing, completed, failed, cancelled) |
| **AI Providers** | 5 (via AIAdapter) |

### 🎯 Acceptance Criteria

| Kriterium | Status |
|-----------|--------|
| AI Job erstellen | ✅ POST /api/v1/admin/ai/jobs |
| Job-Status abrufen | ✅ GET /api/v1/admin/ai/jobs/<id> |
| Job abbrechen | ✅ POST /api/v1/admin/ai/jobs/<id>/cancel |
| Kurs finalisieren | ✅ POST /api/v1/admin/ai/jobs/<id>/finalize |
| Live Progress 0-100% | ✅ progress Feld |
| JSONB Output-Speicherung | ✅ output_data JSONB |
| Multi-Provider AI | ✅ AIAdapter |
| RBAC Permissions | ✅ 3 Permissions |
| Audit Logging | ✅ Alle Operationen |
| Keine Duplikat-Dateien | ✅ Keine .old/.bak |
| Keine Demo-Daten | ✅ Keine Seeds |
| Backend-only | ✅ Kein Frontend-Code |

---

## Dateistruktur

### Neue Dateien (7)

```
backend/
├── migrations/
│   └── 046_ai_jobs.sql                          # Migration für ai_jobs Tabelle
├── app/
│   ├── ai/
│   │   ├── __init__.py                          # AI Module Exports
│   │   └── ai_course_generator.py               # Worker (540 Zeilen)
│   ├── models/
│   │   └── admin_ai.py                          # Pydantic Models (80 Zeilen)
│   ├── repositories/
│   │   └── ai_job_repository.py                 # Repository (380 Zeilen)
│   └── services/
│       └── ai_job_service.py                    # Service Layer (280 Zeilen)
```

### Erweiterte Dateien (2)

```
backend/app/
├── security/
│   └── permissions.py                           # + 3 Permissions, + admin-Rolle
└── api/
    └── admin_courses.py                         # + 4 Endpoints (~330 Zeilen)
```

---

**Ende der Dokumentation Phase B24-05**

---

**Nächste Schritte:**
1. ✅ Migration 046 ausführen: `psql < backend/migrations/046_ai_jobs.sql`
2. ✅ Backend-Neustart (bereits laufend)
3. ⏳ Frontend UI für AI Jobs (zukünftige Phase)
4. ⏳ PDF-Upload Endpoint implementieren
5. ⏳ Celery-Worker-Migration für Production
