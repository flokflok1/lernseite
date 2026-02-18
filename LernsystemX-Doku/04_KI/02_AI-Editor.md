# 36 – AI Editor

**Version:** 1.0
**Stand:** Dezember 2024

---

## Überblick

Das **AI Editor** ist ein Desktop-basiertes Werkzeug im Admin-Bereich, das Content-Creatoren und Administratoren ermöglicht, KI-gestützt Kursinhalte zu erstellen, zu bearbeiten und zu verwalten.

### Kernziele

- **Chat-basierte Interaktion** – Natürliche Konversation mit der KI zur Content-Erstellung
- **Kontextbewusstsein** – KI kennt ausgewählten Kurs, Kapitel und Dateien
- **Split-View Layout** – Übersichtliche Trennung von Navigation und Chat
- **Session-Management** – Fortschritt wird gespeichert und kann fortgesetzt werden
- **Action Buttons** – Schnellzugriff auf häufige Aktionen

---

## Systemarchitektur

### Desktop-Window-Konzept

Das AI Editor ist als **Desktop-Window** im LSX-Admin-System implementiert. Es öffnet sich als schwebendes Fenster mit:

- Minimieren/Schließen-Buttons
- Verschiebbar per Drag & Drop
- Feste Größe (800x600px Standard)

### Split-View Layout

```
┌─────────────────────────────────────────────────────────────┐
│  AI Editor                           [_] [X]      │
├─────────────────────┬───────────────────────────────────────┤
│                     │  Kontext-Leiste                       │
│  Kurs-Auswahl       │  [Kurs] [Kapitel] [3 Dateien]         │
│  ┌───────────────┐  ├───────────────────────────────────────┤
│  │ Dropdown      │  │                                       │
│  └───────────────┘  │  Chat-Bereich                         │
│                     │                                       │
│  [Kapitel] [Dateien]│  ┌─────────────────────────────────┐  │
│                     │  │ KI: Wie kann ich helfen?        │  │
│  □ Kapitel 1        │  └─────────────────────────────────┘  │
│  □ Kapitel 2        │                                       │
│  ☑ Kapitel 3        │  ┌─────────────────────────────────┐  │
│                     │  │ User: Erstelle ein Quiz...      │  │
│                     │  └─────────────────────────────────┘  │
│                     │                                       │
│                     ├───────────────────────────────────────┤
│                     │  [Eingabefeld...]          [Senden]   │
│                     ├───────────────────────────────────────┤
│                     │  [Kapitel] [Quiz] [Zusammenfassung]   │
│                     │  Action Buttons                       │
└─────────────────────┴───────────────────────────────────────┘
```

---

## Frontend-Komponente

### Datei

`frontend/src/presentation/components/panel/editor/ai/AIEditorContainer.vue`

### Props

```typescript
interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}
```

### State-Management

```typescript
// Session-State
const session = ref<{
  id: string
  mode: 'new_chapters' | 'edit_existing'
  context: {
    course_id?: string
    chapter_ids: string[]
    file_ids: string[]
  }
} | null>(null)

// Chat-State
const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const isLoading = ref(false)

// Selection-State
const selectedCourseId = ref<string | null>(null)
const selectedChapterId = ref<string | null>(null)
const selectedFileIds = ref<string[]>([])
```

### Wichtige Funktionen

| Funktion | Beschreibung |
|----------|--------------|
| `loadCourses()` | Lädt alle Kurse vom Backend |
| `loadChapters(courseId)` | Lädt Kapitel eines Kurses |
| `loadFiles(courseId)` | Lädt Dateien eines Kurses |
| `sendMessage()` | Sendet Nachricht an KI-Backend |
| `callChatApi(prompt)` | API-Call zum Chat-Endpoint |
| `executeAction(action)` | Führt Action-Button aus |

---

## Backend-API

### Endpoints

#### POST `/api/v1/admin/ai-editor/chat`

Chat-Nachricht an die KI senden.

**Request:**
```json
{
  "message": "Erstelle ein Quiz zum Thema Netzwerke",
  "course_id": "uuid-string",
  "context": {
    "mode": "new_chapters",
    "chapter_id": "uuid-string",
    "file_ids": ["uuid-1", "uuid-2"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Ich erstelle ein Quiz mit 10 Fragen...",
    "actions": [
      {
        "id": "create_quiz",
        "label": "Quiz erstellen",
        "type": "primary"
      },
      {
        "id": "modify",
        "label": "Anpassen",
        "type": "secondary"
      }
    ],
    "context_used": {
      "course_title": "CompTIA Network+",
      "chapters_count": 3,
      "files_count": 2
    }
  }
}
```

### Backend-Datei

`backend/app/api/admin_ai_editor.py`

### Interne Funktionen

| Funktion | Beschreibung |
|----------|--------------|
| `_analyze_chat_intent(message)` | Erkennt Absicht der Nachricht |
| `_build_chat_context(course_id, context)` | Baut Kontext für KI |
| `_get_info_response(intent, context)` | Generiert Info-Antworten |
| `_get_fallback_response(intent)` | Fallback wenn KI nicht verfügbar |
| `_generate_chat_actions(intent)` | Erstellt passende Action-Buttons |

### Intent-Erkennung

```python
INTENT_KEYWORDS = {
    'create_chapter': ['kapitel erstellen', 'neues kapitel', 'chapter'],
    'create_quiz': ['quiz', 'fragen', 'test erstellen'],
    'create_summary': ['zusammenfassung', 'summary', 'zusammenfassen'],
    'explain': ['erkläre', 'was ist', 'wie funktioniert'],
    'edit': ['bearbeiten', 'ändern', 'anpassen'],
    'info': ['info', 'status', 'übersicht']
}
```

---

## Session-Management

### Session-Modi

| Modus | Beschreibung |
|-------|--------------|
| `new_chapters` | Neue Kapitel für einen Kurs erstellen |
| `edit_existing` | Bestehende Kapitel bearbeiten |

### Session-Persistenz

Sessions werden im LocalStorage gespeichert:

```typescript
// Speichern
localStorage.setItem('ai_editor_session', JSON.stringify(session.value))

// Laden
const saved = localStorage.getItem('ai_editor_session')
if (saved) session.value = JSON.parse(saved)
```

---

## Action Buttons

Dynamisch generierte Buttons basierend auf Chat-Kontext:

### Standard-Actions

| Action | Label | Beschreibung |
|--------|-------|--------------|
| `create_chapter` | Kapitel erstellen | Öffnet Kapitel-Generator |
| `create_quiz` | Quiz erstellen | Startet Quiz-Erstellung |
| `create_summary` | Zusammenfassung | Generiert Zusammenfassung |
| `view_chapters` | Kapitel anzeigen | Zeigt vorhandene Kapitel |

### Action-Handling

```typescript
function executeAction(action: ChatAction) {
  switch (action.id) {
    case 'create_chapter':
      // Öffnet Kapitel-Generator-Window
      windowStore.openWindow({
        type: 'admin-ai-kapitel-generator',
        title: 'KI-Kapitel-Generator',
        payload: { courseId: selectedCourseId.value }
      })
      break
    // ... weitere Actions
  }
}
```

---

## Kontext-System

### Kontext-Leiste

Die Kontext-Leiste zeigt der KI und dem User den aktuellen Arbeitskontext:

```vue
<div class="context-bar">
  <span v-if="selectedCourse">{{ selectedCourse.title }}</span>
  <span v-if="selectedChapterId">Kapitel ausgewählt</span>
  <span v-if="selectedFileIds.length">{{ selectedFileIds.length }} Dateien</span>
</div>
```

### Kontext an KI übergeben

```typescript
const context = {
  mode: session.value?.mode || 'new_chapters',
  chapter_id: selectedChapterId.value,
  file_ids: selectedFileIds.value
}
```

---

## Styling

### CSS-Variablen

```css
/* Verwendet Theme-Variablen */
--color-surface
--color-border
--color-text-primary
--color-text-secondary
--color-primary
--color-bg
```

### Responsive Split-View

```css
.ai-editor-split-view {
  display: flex;
  height: 100%;
}

.ai-editor-sidebar {
  width: 280px;
  border-right: 1px solid var(--color-border);
}

.ai-editor-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
```

---

## Integration mit anderen Systemen

### Window Store

```typescript
import { useWindowStore } from '@/store/window.store'

// Fenster öffnen
windowStore.openWindow({
  type: 'admin-ai-editor',
  title: 'AI Editor',
  icon: '🤖',
  payload: { courseId, courseTitle }
})
```

### Kurs-System

- Lädt Kurse über `/api/v1/admin/courses`
- Lädt Kapitel über `/api/v1/admin/courses/{id}/chapters`
- Lädt Dateien über `/api/v1/admin/courses/{id}/files`

### KI-Pipeline

- Nutzt Anthropic Claude für Chat-Responses
- Token-Tracking über `ki_requests` Tabelle
- Fallback-Responses wenn KI nicht verfügbar

---

## Fehlerbehandlung

### API-Fehler

```typescript
try {
  const response = await callChatApi(prompt)
  // Handle success
} catch (error) {
  addFallbackResponse()
  console.error('Chat API error:', error)
}
```

### Fallback-Responses

Wenn die KI nicht verfügbar ist:

```typescript
function addFallbackResponse() {
  messages.value.push({
    id: generateId(),
    role: 'assistant',
    content: 'Die KI ist momentan nicht verfügbar. Versuche es später erneut.',
    timestamp: new Date()
  })
}
```

---

## Erweiterungsmöglichkeiten

### Geplante Features

- [ ] **Streaming-Responses** – Token-by-Token Anzeige
- [ ] **File-Upload** – Dateien direkt im Chat hochladen
- [ ] **Vorlagen-System** – Gespeicherte Prompt-Vorlagen
- [ ] **Multi-Kapitel-Generierung** – Mehrere Kapitel gleichzeitig
- [ ] **Version-History** – Änderungsverlauf für generierte Inhalte
- [ ] **Collaboration** – Mehrere User arbeiten an Session

---

## Changelog

| Version | Datum | Änderungen |
|---------|-------|------------|
| 1.0 | Dez 2024 | Initiale Version mit Split-View, Chat, Actions |
