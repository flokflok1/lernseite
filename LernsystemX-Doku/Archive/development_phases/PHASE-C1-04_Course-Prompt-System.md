# Phase C1.4 - Kurs-spezifisches Prompt-System

**Status:** ✅ Vollständig implementiert
**Datum:** 2025-01-23
**Version:** 1.0

## Überblick

Phase C1.4 implementiert ein **kurs-spezifisches Prompt-System** für das LernsystemX Admin-System. Administratoren können KI-Prompts pro Kurs anpassen, um die Qualität und Konsistenz der AI-generierten Inhalte zu verbessern.

**Kernfunktionalität:**
- Kurs-spezifische Prompts für verschiedene Scopes (Modul-Generierung, Prüfungs-Generierung, etc.)
- **Prompt-Resolution Chain**: Course-specific → Global → Hardcoded Fallback
- Verwaltung über Admin-API
- Vollständige Integration mit bestehender KI-Pipeline

## Architektur-Übersicht

### Resolution Chain (Prompt-Resolver)

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Generation Request                       │
│                   (z.B. Exam generieren)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PromptResolver.resolve()                      │
│                  (course_id, scope, language)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ STEP 1:         │ │ STEP 2:         │ │ STEP 3:         │
│ Course-Specific │ │ Global Prompt   │ │ Hardcoded       │
│ Prompt (DB)     │ │ (Registry)      │ │ Fallback        │
│                 │ │                 │ │                 │
│ course_prompts  │ │ PROMPT_REGISTRY │ │ HARDCODED_      │
│ table           │ │ (in-memory)     │ │ FALLBACKS       │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │ Exists?           │ Exists?           │ Always
         └────YES────────────┼───────NO──────────┤
                  ▼          │                   │
           ┌────────────┐    │                   │
           │ Use Course │    │                   │
           │ Prompt     │    │                   │
           └────────────┘    │                   │
                  │          │                   │
                  │         NO                  YES
                  │          │                   │
                  │    ┌────────────┐     ┌─────────────┐
                  │    │ Use Global │     │ Use Fallback│
                  │    │ Prompt     │     │ Prompt      │
                  │    └────────────┘     └─────────────┘
                  │          │                   │
                  └──────────┴───────────────────┘
                             │
                             ▼
                  ┌────────────────────────┐
                  │ Resolved Prompt        │
                  │ + Source Label         │
                  │ (für Audit Log)        │
                  └────────────────────────┘
```

### Datenfluss: Exam-Generierung mit Prompt-Resolution

```
[Frontend] AdminExamManagerWindow.vue
    ↓ generateExam()
    ↓ adminGenerateExam(courseId, generateRequest)
    ↓
[API] POST /api/v1/admin/courses/{course_id}/exams/generate
    ↓
[Backend] admin_courses.py → admin_generate_exam()
    ↓
    1. Validate ExamGenerateRequest (Pydantic)
    2. Create placeholder exam (ExamRepository.create_exam)
    3. Create AI job (AIJobService.create_job)
    ↓
    4. 🆕 Resolve Prompt (PromptResolver.resolve)
       ↓
       ├─ Try course-specific prompt (course_prompts table)
       ├─ Fallback to global prompt (PROMPT_REGISTRY)
       └─ Fallback to hardcoded default
    ↓
    5. Render prompt with context ({{course_title}}, {{exam_title}}, etc.)
    6. Update AI job with rendered messages
    7. Start AI generation (AIJobService.update_job_status → 'queued')
    8. Audit log (admin.exams.generate, severity=high)
    ↓
[Response] { success: true, job_id: "...", exam_id: "..." }
```

## Implementierte Features

### ✅ Backend (100%)

#### 1. Datenbank-Schema (`backend/migrations/047_course_prompts.sql`)

**Tabelle: `course_prompts`**
```sql
CREATE TABLE course_prompts (
    course_prompt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(course_id) ON DELETE CASCADE,
    scope TEXT CHECK (scope IN (
        'course_generation',
        'module_generation',
        'exam_generation',
        'lesson_generation',
        'quiz_generation'
    )),
    language TEXT,
    prompt_system TEXT,
    prompt_user_template TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_course_prompts_course_scope_lang
        UNIQUE (course_id, scope, language)
);
```

**Indexes:**
- `idx_course_prompts_course_scope` - Fast lookup by course + scope
- `idx_course_prompts_scope` - Analytics queries
- `idx_course_prompts_audit` - Audit trail queries

**Trigger:**
- `trigger_course_prompts_updated_at` - Auto-update `updated_at`

#### 2. Pydantic Models (`backend/app/models/course_prompt.py`)

**Enums:**
- `PromptScope` - course_generation, module_generation, exam_generation, lesson_generation, quiz_generation

**Models:**
- `CoursePromptCreateRequest` - Erstellen eines Prompts
- `CoursePromptUpdateRequest` - Aktualisieren (partial update)
- `CoursePromptResponse` - Response mit allen DB-Feldern
- `CoursePromptResolveRequest` - Prompt auflösen (für Testing/Preview)
- `CoursePromptResolveResponse` - Resolved prompt mit Source-Label
- `BulkResetRequest` - Bulk-Reset zu Global Defaults

**Validierungen:**
- Language Code: 2-5 alphabetic characters (z.B. 'de', 'en-us')
- Prompt System/User Template: Nicht leer (NULL ist ok)
- Metadata: Valid JSON

#### 3. Repository (`backend/app/repositories/course_prompt_repository.py`)

**CRUD-Operationen:**
```python
# Read
find_by_id(course_prompt_id) -> Optional[Dict]
find_by_course(course_id, include_inactive=False) -> List[Dict]
find_by_course_and_scope(course_id, scope, language=None) -> Optional[Dict]  # 🔑 Key method
find_by_scope(scope, include_inactive=False) -> List[Dict]

# Create
create(course_id, scope, created_by, ...) -> Optional[Dict]

# Update
update(course_prompt_id, ...) -> Optional[Dict]
upsert(course_id, scope, language, ...) -> Optional[Dict]  # 🔑 Key method

# Delete
delete(course_prompt_id) -> bool
soft_delete(course_prompt_id) -> bool
delete_by_course_and_scope(course_id, scope, language=None) -> bool
delete_by_course(course_id) -> int

# Bulk
bulk_reset_by_course(course_id, scopes=None) -> int

# Statistics
count_by_course(course_id) -> int
count_by_scope(scope) -> int
```

**Besonderheiten:**
- Unique constraint auf (course_id, scope, language)
- JSONB-Felder für metadata (flexible Erweiterung)
- Cascading delete (Kurs gelöscht → Prompts gelöscht)

#### 4. Prompt-Resolver Service (`backend/app/services/prompt_resolver.py`)

**Hauptfunktion:**
```python
PromptResolver.resolve(
    course_id: str,
    scope: str,
    language: Optional[str] = None,
    fallback_to_global: bool = True,
    fallback_to_hardcoded: bool = True
) -> Dict[str, Any]
```

**Resolution Chain:**
1. **Course-Specific Prompt** (DB: course_prompts table)
   - Lookup: `CoursePromptRepository.find_by_course_and_scope()`
   - Returns: `{"source": "course_specific", ...}`

2. **Global Prompt** (In-Memory: PROMPT_REGISTRY)
   - Mapping: `SCOPE_TO_GLOBAL_CODE_MAP` (z.B. exam_generation → quiz_generator)
   - Returns: `{"source": "global", ...}`

3. **Hardcoded Fallback** (Code: HARDCODED_FALLBACKS)
   - Basic default prompts für alle Scopes
   - Returns: `{"source": "hardcoded_fallback", ...}`

**Convenience-Methoden:**
```python
# Resolve + Render in einem Schritt
PromptResolver.resolve_and_render(
    course_id, scope, context, language
) -> List[Dict[str, str]]  # Ready for AI API

# Check if course has custom prompt
PromptResolver.has_course_specific_prompt(
    course_id, scope, language
) -> bool
```

**Hardcoded Fallbacks:**
- `course_generation` - Generic course outline generator
- `module_generation` - Generic module content generator
- `exam_generation` - Generic exam creator
- `lesson_generation` - Generic lesson content generator
- `quiz_generation` - Generic quiz question generator

#### 5. Admin API Endpoints (`backend/app/api/admin_courses.py`)

**Prompt-Verwaltung:**

```python
# Liste aller Prompts eines Kurses
GET /api/v1/admin/courses/{course_id}/prompts
→ Response: { success: true, prompts: [...] }

# Einzelnen Prompt abrufen
GET /api/v1/admin/courses/{course_id}/prompts/{scope}?language=de
→ Response: {
    success: true,
    prompt: {...} | null,  # Course-specific if exists
    resolved: {...},       # Resolved prompt (global or fallback)
    source: "course_specific" | "global" | "hardcoded_fallback"
  }

# Prompt erstellen/aktualisieren (UPSERT)
PUT /api/v1/admin/courses/{course_id}/prompts/{scope}
Body: {
  language: "de",
  prompt_system: "Du bist ein Experte...",
  prompt_user_template: "Erstelle ein Modul über {{topic}}",
  metadata: {"temperature": 0.7},
  is_active: true
}
→ Response: { success: true, prompt: {...}, created: true/false }

# Prompt löschen (Reset zu Global)
DELETE /api/v1/admin/courses/{course_id}/prompts/{scope}?language=de
→ Response: { success: true, message: "Prompt reset to global default" }

# Bulk-Reset aller Prompts
POST /api/v1/admin/courses/{course_id}/prompts/reset
Body: {
  scopes: ["module_generation", "exam_generation"],  // optional (all if null)
  confirm: true  // required
}
→ Response: { success: true, message: "2 prompt(s) reset to global defaults" }

# Prompt auflösen (Testing/Preview)
POST /api/v1/admin/courses/{course_id}/prompts/resolve
Body: {
  scope: "module_generation",
  language: "de"
}
→ Response: {
    success: true,
    resolved: {
      source: "...",
      scope: "...",
      prompt_system: "...",
      prompt_user_template: "...",
      metadata: {...}
    }
  }
```

**Permissions:**
- `ADMIN_COURSE_READ` - Prompts anzeigen
- `ADMIN_COURSE_WRITE` - Prompts erstellen/bearbeiten/löschen

**Audit Logging:**
- Alle Operationen werden in `audit_logs` protokolliert
- Severity: high (Bulk-Reset), medium (Create/Update/Delete)

#### 6. KI-Integration (`admin_courses.py` → `admin_generate_exam()`)

**Aktualisierte Exam-Generierung:**
```python
# Resolve prompt for exam generation (Phase C1.4)
resolved_prompt = PromptResolver.resolve(
    course_id=course_id,
    scope='exam_generation',
    language=course.get('language', 'de')
)

# Build context for prompt rendering
context = {
    'course_title': course['title'],
    'exam_title': generate_request.title,
    'exam_standard': generate_request.exam_standard.value,
    'difficulty': generate_request.difficulty or 'intermediate',
    'question_count': sum(generate_request.question_distribution.values()),
    'duration_minutes': generate_request.duration_minutes,
    'passing_score': generate_request.passing_score
}

# Render prompt with context
rendered_messages = PromptResolver.resolve_and_render(
    course_id=course_id,
    scope='exam_generation',
    context=context,
    language=course.get('language', 'de')
)

# Update AI job with resolved prompt info
AIJobRepository.update(job['id'], {
    'exam_id': exam['exam_id'],
    'input_prompt': f"[{resolved_prompt['source'].upper()}] Generate exam",
    'settings': {
        'prompt_source': resolved_prompt['source'],
        'rendered_messages': rendered_messages,
        'context': context
    }
})
```

**Fallback-Handling:**
- Wenn Prompt-Resolution fehlschlägt, wird eine Exception geloggt
- Der AI-Job wird trotzdem gestartet (mit basic prompt)
- Audit-Log enthält Source-Information (COURSE_SPECIFIC, GLOBAL, HARDCODED_FALLBACK)

### ✅ Frontend (100%)

#### 1. API Client (`frontend/src/api/admin.api.ts`)

**TypeScript Interfaces:**
```typescript
type PromptScope =
  | 'course_generation'
  | 'module_generation'
  | 'exam_generation'
  | 'lesson_generation'
  | 'quiz_generation'

interface CoursePrompt { ... }
interface CoursePromptUpdateRequest { ... }
interface CoursePromptResolveResponse { ... }
```

**API Funktionen:**
```typescript
adminListCoursePrompts(courseId: string, includeInactive?: boolean): Promise<CoursePrompt[]>
adminGetCoursePrompt(courseId: string, scope: PromptScope, language?: string): Promise<{...}>
adminUpsertCoursePrompt(courseId: string, scope: PromptScope, data: CoursePromptUpdateRequest): Promise<{...}>
adminDeleteCoursePrompt(courseId: string, scope: PromptScope, language?: string): Promise<void>
adminBulkResetCoursePrompts(courseId: string, scopes?: PromptScope[]): Promise<{message: string}>
adminResolveCoursePrompt(courseId: string, scope: PromptScope, language?: string): Promise<CoursePromptResolveResponse>
```

#### 2. UI Integration (Vorbereitet, nicht implementiert)

**Geplante Integration:**
- Neuer Tab "Prompts" in `AdminCourseDetailWindow.vue`
- Prompt-Editor pro Scope mit Live-Preview
- Source-Badge (Course-Specific, Global, Fallback)
- Reset-zu-Global-Button
- Bulk-Reset-Funktion

**Hinweis:** Frontend-UI wird in Phase C1.5 (Polishing) implementiert.

## Architektur-Details

### Prompt-Struktur

**Prompt-Template Felder:**
```json
{
  "prompt_system": "Du bist ein erfahrener IHK-Ausbilder für Fachinformatiker Systemintegration.",
  "prompt_user_template": "Erstelle eine Prüfung für den Kurs {{course_title}}.\n\nPrüfungstitel: {{exam_title}}\nStandard: {{exam_standard}}\nSchwierigkeit: {{difficulty}}\nFragenanzahl: {{question_count}}\n\nDie Prüfung soll dem Standard {{exam_standard}} entsprechen und {{question_count}} Fragen enthalten.",
  "metadata": {
    "temperature": 0.5,
    "max_tokens": 6000,
    "tags": ["ihk", "fisi", "ap1"]
  }
}
```

**Context-Variablen (Beispiel Exam-Generierung):**
- `{{course_title}}` - Kurstitel
- `{{exam_title}}` - Prüfungstitel
- `{{exam_standard}}` - IHK FISI AP1, CompTIA A+, etc.
- `{{difficulty}}` - beginner, intermediate, advanced, expert
- `{{question_count}}` - Anzahl der Fragen
- `{{duration_minutes}}` - Prüfungsdauer
- `{{passing_score}}` - Bestehen-Schwelle (%)

**Rendering:**
```python
# Simple template rendering
rendered = prompt_user_template.replace("{{course_title}}", "IHK FISI AP1")
rendered = rendered.replace("{{exam_title}}", "Abschlussprüfung Teil 1")
# ... etc.
```

### Scope-zu-Global-Mapping

```python
SCOPE_TO_GLOBAL_CODE_MAP = {
    'course_generation': None,              # No global prompt (custom only)
    'module_generation': None,              # No global prompt (custom only)
    'exam_generation': 'quiz_generator',    # Maps to quiz_generator
    'lesson_generation': 'explain_concept', # Maps to explain_concept
    'quiz_generation': 'quiz_generator'     # Maps to quiz_generator
}
```

**Hinweis:** `course_generation` und `module_generation` haben KEINE globalen Prompts, da diese Operationen sehr kurs-spezifisch sind. Sie fallen direkt auf hardcoded fallbacks zurück.

### Datenbank-Schema-Details

**UNIQUE Constraint:**
```sql
CONSTRAINT uq_course_prompts_course_scope_lang
    UNIQUE (course_id, scope, language)
```

**Interpretation:**
- Ein Kurs kann **maximal einen Prompt** pro (scope, language) haben
- Beispiel: Kurs "IHK FISI" kann haben:
  - `exam_generation` + `de` → Ein Prompt
  - `exam_generation` + `en` → Ein anderer Prompt
  - `module_generation` + `de` → Ein weiterer Prompt

**NULL Language:**
- `language = NULL` bedeutet "Standard-Sprache" (typischerweise aus Kurs-Metadaten)
- UNIQUE-Check erlaubt: (course_id=1, scope='exam_generation', language=NULL) nur einmal

## Testing

### Backend-Tests (Empfohlen)

```bash
cd backend
pytest tests/test_course_prompts.py -v
```

**Test-Szenarien:**
1. Prompt erstellen (Kurs-spezifisch)
2. Prompt abrufen (UPSERT-Logik)
3. Prompt aktualisieren (Partial Update)
4. Prompt löschen (Reset zu Global)
5. Bulk-Reset (Alle Scopes)
6. Prompt-Resolution (Course → Global → Fallback)
7. Context-Rendering ({{variable}} replacement)

### Manuelle API-Tests (curl)

```bash
# 1. Liste alle Prompts eines Kurses
curl -X GET "http://localhost:5000/api/v1/admin/courses/{course_id}/prompts" \
  -H "Authorization: Bearer $TOKEN"

# 2. Prompt für Exam-Generierung abrufen
curl -X GET "http://localhost:5000/api/v1/admin/courses/{course_id}/prompts/exam_generation?language=de" \
  -H "Authorization: Bearer $TOKEN"

# 3. Kurs-spezifischen Prompt erstellen
curl -X PUT "http://localhost:5000/api/v1/admin/courses/{course_id}/prompts/exam_generation" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "de",
    "prompt_system": "Du bist ein IHK-Ausbilder...",
    "prompt_user_template": "Erstelle eine Prüfung über {{topic}}",
    "metadata": {"temperature": 0.5}
  }'

# 4. Prompt auflösen (Testing)
curl -X POST "http://localhost:5000/api/v1/admin/courses/{course_id}/prompts/resolve" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "exam_generation",
    "language": "de"
  }'

# 5. Prompt löschen (Reset zu Global)
curl -X DELETE "http://localhost:5000/api/v1/admin/courses/{course_id}/prompts/exam_generation?language=de" \
  -H "Authorization: Bearer $TOKEN"

# 6. Bulk-Reset aller Prompts
curl -X POST "http://localhost:5000/api/v1/admin/courses/{course_id}/prompts/reset" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scopes": null,
    "confirm": true
  }'
```

## Bekannte Einschränkungen

1. **Frontend-UI:**
   - Keine grafische Oberfläche zur Prompt-Verwaltung
   - API ist vollständig implementiert, UI fehlt noch
   - Wird in Phase C1.5 (Polishing) nachgeholt

2. **Prompt-Validation:**
   - Keine Syntax-Validierung für {{variable}} Placeholders
   - Keine Warnung bei unbekannten Variablen
   - Keine Template-Vorschau mit Sample-Daten

3. **Multi-Language Support:**
   - Language-Fallback noch nicht implementiert (de → en → default)
   - Aktuell: Exakte Übereinstimmung erforderlich

4. **Versionierung:**
   - Keine Prompt-Versionen (History)
   - Änderungen überschreiben alten Prompt

## Zukünftige Erweiterungen (C1.5+)

- [ ] Frontend UI für Prompt-Manager Tab
- [ ] Prompt-Template-Validator ({{variable}} Syntax-Check)
- [ ] Prompt-Preview mit Sample-Daten
- [ ] Prompt-Versionshistorie (Rollback-Funktion)
- [ ] Prompt-Templates (Vorlagen für IHK, CompTIA, etc.)
- [ ] Multi-Language Fallback-Chain (de → en → default)
- [ ] Prompt-Import/Export (JSON)
- [ ] Prompt-Statistiken (Nutzungshäufigkeit, Token-Verbrauch)
- [ ] A/B-Testing für Prompts

## Erfolgskriterien ✅

- [x] Backend DB-Schema vollständig implementiert
- [x] Pydantic Models mit Validierung
- [x] Repository mit CRUD-Operationen
- [x] Prompt-Resolver Service mit Resolution Chain
- [x] Admin API vollständig implementiert (6 Endpoints)
- [x] Frontend API Client vollständig implementiert
- [x] KI-Integration aktualisiert (Exam Generator)
- [x] Audit Logging für alle Operationen
- [x] Error Handling mit Fallbacks
- [x] Dokumentation vollständig

## Nutzung im Produktivbetrieb

### Admin-Workflow: Kurs-spezifischen Prompt erstellen

1. **Kurs auswählen:**
   - Admin öffnet Kurs-Details im Admin-Panel

2. **Prompt anpassen:**
   - PUT `/api/v1/admin/courses/{course_id}/prompts/exam_generation`
   - Setzt kurs-spezifische System- und User-Prompts

3. **Testen:**
   - POST `/api/v1/admin/courses/{course_id}/prompts/resolve`
   - Prüft, ob Prompt korrekt aufgelöst wird

4. **Exam generieren:**
   - POST `/api/v1/admin/courses/{course_id}/exams/generate`
   - Nutzt automatisch den kurs-spezifischen Prompt

5. **Zurücksetzen (falls nötig):**
   - DELETE `/api/v1/admin/courses/{course_id}/prompts/exam_generation`
   - Kurs nutzt wieder global defaults

### Entwickler-Workflow: Neuen Scope hinzufügen

1. **Enum erweitern:**
   ```python
   # backend/app/models/course_prompt.py
   class PromptScope(str, Enum):
       ...
       NEW_SCOPE = "new_scope"
   ```

2. **Hardcoded Fallback definieren:**
   ```python
   # backend/app/services/prompt_resolver.py
   HARDCODED_FALLBACKS = {
       ...
       'new_scope': {
           'prompt_system': "...",
           'prompt_user_template': "...",
           'metadata': {...}
       }
   }
   ```

3. **Mapping hinzufügen (optional):**
   ```python
   # backend/app/services/prompt_resolver.py
   SCOPE_TO_GLOBAL_CODE_MAP = {
       ...
       'new_scope': 'global_prompt_code'  # oder None
   }
   ```

4. **Frontend-Type aktualisieren:**
   ```typescript
   // frontend/src/api/admin.api.ts
   export type PromptScope =
     | ...
     | 'new_scope'
   ```

## Änderungshistorie

| Datum | Version | Änderung |
|-------|---------|----------|
| 2025-01-23 | 1.0 | Initial Release - Vollständige C1.4 Implementierung |

---

**Entwickler-Notizen:**

Diese Phase C1.4 erweitert das bestehende Prompt-System (Phase 24) um kurs-spezifische Overrides. Die Resolution-Chain stellt sicher, dass immer ein Prompt verfügbar ist (3-stufig: Course → Global → Fallback), während Admins volle Kontrolle über kurs-spezifische Anpassungen haben.

Das Design folgt dem "Convention over Configuration" Prinzip: Standardmäßig nutzen alle Kurse globale Prompts, aber Admins können gezielt Prompts für spezielle Kurse (z.B. IHK FISI) anpassen.

**Integration mit bestehenden Systemen:**
- ✅ Nutzt bestehendes Prompt-System (PROMPT_REGISTRY)
- ✅ Integriert mit AI-Job-System (Phase C1.3)
- ✅ Audit-Logging (Phase 06)
- ✅ Permissions-System (RBAC)
- ✅ Repository-Pattern (kein ORM)
