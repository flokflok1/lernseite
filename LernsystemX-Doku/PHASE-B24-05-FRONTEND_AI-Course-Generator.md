# Phase B24-05: AI Course Generator - Frontend Implementation

**Version:** 1.0
**Status:** Implemented
**Date:** 2025-11-20
**Phase:** Frontend Development - AI-Powered Course Generation UI

---

## Überblick

Phase B24-05 Frontend implementiert die vollständige Benutzeroberfläche für den **KI-Kursgenerator**. Admins können PDFs hochladen, den AI-Job in Echtzeit verfolgen, und mit einem Klick vollständige Kurse erstellen.

### Zielsetzung

- ✅ **Upload-UI**: PDF-Upload mit Drag & Drop
- ✅ **Live Progress**: Echtzeit-Fortschrittsanzeige (Polling)
- ✅ **Job Viewer**: Strukturierter Output-Viewer für AI-generierte Kurse
- ✅ **One-Click-Finalize**: Kurs, Module, Lessons mit einem Klick erstellen
- ✅ **Responsive Design**: Mobile-First, nur CSS-Variablen
- ✅ **TypeScript**: Vollständig typsicher

---

## Implementierte Komponenten

### 1. API Layer (`admin.api.ts`)

**Neue Exports:**
```typescript
// Types
export type AIJobStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
export type AIJobType = 'course_from_pdf' | 'module_autogen' | 'lesson_autogen'
export interface AIJob { ... }
export interface AICourseDraft { ... }

// API Functions
export const adminStartAIJob = async (data: FormData): Promise<AIJob>
export const adminGetAIJob = async (jobId: string): Promise<AIJob>
export const adminCancelAIJob = async (jobId: string): Promise<void>
export const adminFinalizeAIJob = async (jobId: string, options?: AIJobFinalizeRequest): Promise<AIJobFinalizeResponse>
```

**Endpoint-Mapping:**
- `POST /admin/ai/jobs` → `adminStartAIJob()`
- `GET /admin/ai/jobs/<id>` → `adminGetAIJob()`
- `POST /admin/ai/jobs/<id>/cancel` → `adminCancelAIJob()`
- `POST /admin/ai/jobs/<id>/finalize` → `adminFinalizeAIJob()`

---

### 2. Store Layer (`admin.store.ts`)

**Neue State:**
```typescript
const aiJobs = ref<Map<string, AIJob>>(new Map())
const currentAIJob = ref<AIJob | null>(null)
const aiJobPollingInterval = ref<number | null>(null)
const aiJobLoading = ref(false)
const aiJobError = ref<string | null>(null)
```

**Neue Actions:**
```typescript
// Job Management
startAIJob(file: File, prompt?: string): Promise<AIJob>
pollAIJob(jobId: string): Promise<AIJob>
getAIJob(jobId: string): Promise<AIJob>
cancelAIJob(jobId: string): Promise<void>
finalizeAIJob(jobId: string, options?: AIJobFinalizeRequest): Promise<number>
clearCurrentAIJob(): void

// Polling Control
startAIJobPolling(jobId: string): void
stopAIJobPolling(): void
```

**Polling Logic:**
- Interval: 1500ms (1.5 Sekunden)
- Auto-Stop: Bei `completed`, `failed`, `cancelled`
- Error Handling: Automatischer Polling-Stop bei Fehler

---

### 3. UI Komponenten

#### 3.1 AICourseCreatorModal.vue

**Features:**
- PDF Drag & Drop Upload
- Dateivalidierung (max 50MB, nur PDF)
- Optionales Prompt-Feld
- Live-Upload-Status
- File-Size-Formatter

**Props:**
```typescript
interface Props {
  isOpen: boolean
}
```

**Emits:**
```typescript
interface Emits {
  (e: 'close'): void
  (e: 'jobStarted', jobId: string): void
}
```

**Styling:**
- Nur CSS-Variablen
- `z-index: 9999`
- Backdrop: `bg-[var(--color-overlay)]`
- Responsive Layout

---

#### 3.2 AIJobProgressModal.vue

**Features:**
- Live Progress Bar (0-100%)
- Status-Badge (pending/processing/completed/failed/cancelled)
- Output-Vorschau:
  - Kurstitel & Beschreibung
  - Kategorie, Level, Sprache
  - Module (Anzahl, Titel, Beschreibung, Duration)
  - Lektionen pro Modul
- Aktionen:
  - Job abbrechen (pending/processing)
  - Kurs erstellen (completed)
  - Modal schließen

**Props:**
```typescript
interface Props {
  isOpen: boolean
  jobId?: string | null
}
```

**Workflow:**
1. Job laden bei `isOpen = true`
2. Polling automatisch starten (pending/processing)
3. Output-Preview anzeigen (completed)
4. Finalize → Redirect zu `/admin/courses/<id>`

---

#### 3.3 AIJobStatusBadge.vue

**Features:**
- Farbcodierte Status-Badges
- Lokalisierte Labels (Deutsch)

**Status-Mapping:**
```typescript
pending    → Grau:  "Wartend"
processing → Blau:  "In Bearbeitung"
completed  → Grün:  "Abgeschlossen"
failed     → Rot:   "Fehlgeschlagen"
cancelled  → Grau:  "Abgebrochen"
```

---

### 4. Page Integration

#### AdminCoursesPage.vue

**Änderungen:**
- Neuer Button: `+ KI-Kurs aus PDF` (Purple Gradient)
- Import von `AICourseCreatorModal` & `AIJobProgressModal`
- Event Handler: `handleAIJobStarted(jobId: string)`
- State: `showAICreatorModal`, `showAIProgressModal`, `currentAIJobId`

**UI-Flow:**
```
Button Click
  → AICourseCreatorModal öffnen
  → PDF hochladen + Prompt
  → Job gestartet → AIJobProgressModal öffnen
  → Polling startet automatisch
  → Output-Preview anzeigen
  → "Kurs erstellen" klicken
  → Redirect zu /admin/courses/<id>
```

---

## Technische Details

### CSS-Variablen (Theme-Support)

Alle Komponenten nutzen **ausschließlich CSS-Variablen**:

```css
--color-surface       /* Modal Background */
--color-background    /* Input Background */
--color-border        /* Borders */
--color-text-primary  /* Primary Text */
--color-text-secondary /* Secondary Text */
--color-primary       /* Primary Button */
--color-overlay       /* Modal Backdrop */
```

**Keine `dark:` Klassen, keine festen Farben!**

---

### Polling-Implementierung

```typescript
// Start Polling (1500ms)
startAIJobPolling(jobId: string): void {
  stopAIJobPolling() // Clear existing

  aiJobPollingInterval.value = window.setInterval(async () => {
    try {
      await pollAIJob(jobId)
    } catch (err) {
      console.error('Polling error:', err)
      stopAIJobPolling()
    }
  }, 1500)
}

// Stop Polling
stopAIJobPolling(): void {
  if (aiJobPollingInterval.value !== null) {
    clearInterval(aiJobPollingInterval.value)
    aiJobPollingInterval.value = null
  }
}
```

**Auto-Stop-Bedingungen:**
```typescript
if (['completed', 'failed', 'cancelled'].includes(job.status)) {
  stopAIJobPolling()
}
```

---

### File Upload

**Validation:**
```typescript
// Type Check
if (file.type !== 'application/pdf') {
  fileError.value = 'Nur PDF-Dateien sind erlaubt'
  return
}

// Size Check (50MB)
if (file.size > 50 * 1024 * 1024) {
  fileError.value = 'Datei ist zu groß (max. 50 MB)'
  return
}
```

**FormData Submission:**
```typescript
const formData = new FormData()
formData.append('type', 'course_from_pdf')
formData.append('file', file)
if (prompt) formData.append('prompt', prompt)

const job = await adminApi.adminStartAIJob(formData)
```

---

## Code-Statistiken

### Dateien Erstellt/Erweitert

| Datei | Zeilen | Status |
|-------|--------|--------|
| `admin.api.ts` | +145 | Erweitert |
| `admin.store.ts` | +207 | Erweitert |
| `AICourseCreatorModal.vue` | 300 | Neu |
| `AIJobProgressModal.vue` | 290 | Neu |
| `AIJobStatusBadge.vue` | 35 | Neu |
| `AdminCoursesPage.vue` | +25 | Erweitert |

**Total:** ~1.000 LOC (ohne Dokumentation)

---

## Testing

### Manuelle Tests

1. **Upload-Modal öffnen:**
   ```
   /admin/courses → "+ KI-Kurs aus PDF" Button
   ```

2. **PDF hochladen:**
   - Drag & Drop testen
   - Dateiauswahl testen
   - Validierung testen (nicht-PDF, > 50MB)

3. **Job starten:**
   - Mit Prompt
   - Ohne Prompt
   - Progress-Modal sollte öffnen

4. **Polling testen:**
   - Backend manuell auf `processing` setzen
   - Progress sollte sich aktualisieren (alle 1.5s)
   - Bei `completed`: Output-Preview anzeigen

5. **Finalisierung testen:**
   - "Kurs erstellen" klicken
   - Sollte redirecten zu `/admin/courses/<id>`
   - Kurs sollte in DB existieren

6. **Job abbrechen testen:**
   - "Abbrechen" klicken (während processing)
   - Status sollte auf `cancelled` wechseln
   - Polling sollte stoppen

---

## API-Antwort-Beispiel

### GET /admin/ai/jobs/<id>

```json
{
  "success": true,
  "job": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "e4ac9965-e3d2-42b9-9703-3f1c0f4adedc",
    "type": "course_from_pdf",
    "status": "completed",
    "progress": 100,
    "input_file": "python_basics.pdf",
    "input_prompt": "Erstelle einen Anfängerkurs",
    "output_data": {
      "course": {
        "title": "Python Grundlagen",
        "description": "Einführung in Python...",
        "category": "programming",
        "level": "beginner",
        "language": "de"
      },
      "modules": [
        {
          "title": "Modul 1: Einführung",
          "description": "Grundlagen...",
          "duration_minutes": 45,
          "order_index": 1,
          "lessons": [
            {
              "title": "Lektion 1: Was ist Python?",
              "lesson_type": "text",
              "duration_minutes": 15,
              "order_index": 1
            }
          ]
        }
      ]
    },
    "created_at": "2025-11-20T10:30:00Z",
    "updated_at": "2025-11-20T10:35:00Z"
  }
}
```

---

## Bekannte Einschränkungen

1. **Kein WebSocket**: Polling (1.5s) statt Echtzeit-Push
2. **Keine Job-Liste**: Nur aktueller Job sichtbar (AdminAIJobsPage.vue fehlt noch)
3. **Keine Retry-Logic**: Bei fehlgeschlagenen Jobs muss neu hochgeladen werden
4. **Keine Edit-Funktion**: Output kann nicht vor Finalisierung bearbeitet werden

---

## Future Roadmap

### Phase B24-06 (geplant):
- **AdminAIJobsPage.vue**: Übersicht aller AI-Jobs
- **Job-Reopen**: Alte Jobs wieder öffnen
- **WebSocket**: Echtzeit-Updates statt Polling
- **Edit-Output**: Output vor Finalisierung bearbeiten
- **Retry Failed Jobs**: Fehlgeschlagene Jobs neu starten

### Phase B24-07 (geplant):
- **AI-Feedback-Loop**: "Ist der Kurs so okay?" → KI verbessert
- **Iterative Generation**: Schritt-für-Schritt mit User-Input
- **Multi-Language**: PDF in beliebiger Sprache → Kurs in Zielsprache

---

## Deployment-Checkliste

- [x] API-Endpoints getestet
- [x] Store-Actions getestet
- [x] UI-Komponenten erstellt
- [x] CSS-Variablen verwendet (kein Tailwind dark:)
- [x] TypeScript typsicher
- [x] Polling implementiert
- [x] Error Handling implementiert
- [ ] E2E-Tests geschrieben
- [ ] Migration 046 angewendet
- [ ] Backend AI-Worker getestet

---

## Zusammenfassung

**Phase B24-05 Frontend ist vollständig implementiert!**

Die Benutzeroberfläche ermöglicht Admins:
1. PDFs hochzuladen mit Drag & Drop
2. Optional Prompt-Anweisungen zu geben
3. Job-Progress in Echtzeit zu verfolgen (Polling)
4. AI-generierte Kursstruktur zu reviewen
5. Mit einem Klick vollständige Kurse zu erstellen

**Architektur:**
- Saubere Trennung: API → Store → Components
- TypeScript überall
- Nur CSS-Variablen (Theme-Support)
- Polling mit Auto-Stop
- Responsive & Mobile-First

**Nächste Schritte:**
- Migration 046 anwenden
- Backend AI-Worker testen
- AdminAIJobsPage.vue implementieren (Job-Liste)
- WebSocket für Echtzeit-Updates erwägen

---

**Phase B24-05 Frontend: ✅ COMPLETE**
