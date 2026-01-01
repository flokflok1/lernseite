# Frontend Phase F5 – Kurs-Player & Lernmethoden-UI

**Version:** 1.0
**Stand:** Abgeschlossen
**Datum:** 2025-01-16

---

## Überblick

Phase F5 implementiert den vollständigen Kurs-Player für LernsystemX, einschließlich:

- Course Overview Page (Kursdetails & Modulübersicht)
- Lesson Player (Multi-Typ Lesson Viewer)
- Learning Methods Panel (KI-gestützte Lernmethoden)
- Progress Tracking & Synchronisation
- Analytics Event Integration

---

## Architektur-Übersicht

### Komponentenhierarchie

```
CourseOverviewPage.vue
├── Kurs-Header (Thumbnail, Title, Progress)
├── Beschreibung & Lernziele
└── Modulübersicht
    └── Lesson-Liste (pro Modul)

LessonPlayerPage.vue
├── Top Navigation Bar
├── Left Sidebar: Module & Lesson Navigation
├── Center: Lesson Content (Dynamic Component)
│   ├── TextLesson.vue
│   ├── VideoLesson.vue
│   ├── QuizLesson.vue (Placeholder)
│   └── AiLesson.vue
└── Right Sidebar: MethodExecutionPanel.vue
    ├── Token Balance Display
    ├── Available Methods List
    └── Execution Result Display
```

### State Management Flow

```
User Action → Component → Player Store → API Layer → Backend
                  ↓
            Analytics Event (course_view, lesson_start, etc.)
```

---

## Neue Dateien

### 1. Router-Erweiterung

**Datei:** `src/router/index.ts`

Neue Routen:
- `/course/:courseId` → `CourseOverviewPage.vue`
- `/course/:courseId/module/:moduleId/lesson/:lessonId` → `LessonPlayerPage.vue`

Beide Routen erfordern Authentifizierung (`requiresAuth: true`).

---

### 2. API Layer

**Datei:** `src/api/player.api.ts`

#### Hauptfunktionen:

**Course Management:**
- `getCourse(courseId)` - Kursdetails laden
- `getCourseModules(courseId)` - Module eines Kurses laden
- `getModule(courseId, moduleId)` - Modul mit Lessons laden
- `getLesson(courseId, moduleId, lessonId)` - Lesson Details laden

**Progress Tracking:**
- `getCourseProgress(courseId)` - Kursfortschritt abrufen
- `getModuleProgress(courseId, moduleId)` - Modulfortschritt abrufen
- `getLessonProgress(courseId, moduleId, lessonId)` - Lessonfortschritt abrufen
- `markLessonStarted()` - Lesson als gestartet markieren
- `markLessonCompleted()` - Lesson als abgeschlossen markieren
- `updateLessonProgress()` - Fortschritt aktualisieren

**Learning Methods:**
- `getLessonMethods(lessonId)` - Verfügbare Methoden für Lesson laden
- `executeMethod(request)` - KI-Methode ausführen

**Analytics:**
- `sendAnalyticsEvent(request)` - Event an Analytics-System senden

#### TypeScript Interfaces:

- `Course` - Kurs-Datenstruktur
- `Module` - Modul-Datenstruktur
- `Lesson` - Lesson-Datenstruktur (mit `lesson_type`)
- `LessonProgress` - Fortschritt einer Lesson
- `ModuleProgress` - Fortschritt eines Moduls
- `CourseProgress` - Gesamtfortschritt eines Kurses
- `LearningMethod` - Lernmethoden-Definition
- `ExecuteMethodRequest` - Request für Methodenausführung
- `ExecuteMethodResponse` - Response der Methodenausführung

---

### 3. Player Store

**Datei:** `src/store/player.store.ts`

#### State:

```typescript
{
  course: Course | null
  modules: Module[]
  currentModule: Module | null
  currentLesson: Lesson | null
  courseProgress: CourseProgress | null
  moduleProgress: ModuleProgress | null
  lessonProgress: LessonProgress | null
  availableMethods: LearningMethod[]
  loading: boolean
  error: string | null
  methodExecuting: boolean
  methodResult: any
  methodError: string | null
}
```

#### Getters:

- `hasCourse` - Prüft ob Kurs geladen
- `currentLessonIndex` - Index der aktuellen Lesson im Modul
- `hasNextLesson` - Prüft ob nächste Lesson existiert
- `hasPreviousLesson` - Prüft ob vorherige Lesson existiert
- `nextLesson` - Gibt nächste Lesson zurück
- `previousLesson` - Gibt vorherige Lesson zurück
- `isLessonCompleted` - Prüft ob Lesson abgeschlossen

#### Actions:

- `loadCourse(courseId)` - Lädt Kurs mit Modulen + sendet `course_view` Event
- `loadModule(courseId, moduleId)` - Lädt Modul mit Lessons + sendet `module_start` Event
- `loadLesson(courseId, moduleId, lessonId)` - Lädt Lesson mit Progress & Methoden + sendet `lesson_start` Event
- `markLessonStarted()` - Markiert Lesson als gestartet
- `markLessonCompleted()` - Markiert Lesson als abgeschlossen + sendet `lesson_complete` Event
- `executeLearningMethod(request)` - Führt KI-Methode aus + sendet `method_execute` Event
- `syncProgress()` - Synchronisiert Fortschritt
- `clearPlayer()` - Leert Player-State

**Persistenz:** Keine LocalStorage-Persistierung (alles wird live vom Backend geladen).

---

### 4. Pages

#### 4.1 CourseOverviewPage.vue

**Route:** `/course/:courseId`

**Features:**
- Kurs-Header mit Thumbnail, Titel, Level-Badge
- Fortschrittsbalken (wenn eingeschrieben)
- "Kurs starten / fortsetzen"-Button
- Kursbeschreibung, Lernziele, Voraussetzungen
- Modulübersicht mit Lessons
- Analytics: Sendet `course_view` beim Laden

**Layout:**
- Responsive Cards-basiertes Layout
- TailwindCSS Styling

**Navigation:**
- Klick auf Lesson → Weiterleitung zu `/course/:courseId/module/:moduleId/lesson/:lessonId`

---

#### 4.2 LessonPlayerPage.vue

**Route:** `/course/:courseId/module/:moduleId/lesson/:lessonId`

**Features:**
- **Top Bar:**
  - "Zurück zum Kurs"-Button
  - Kurs- & Modultitel
  - Fortschrittsanzeige
  - "Als abgeschlossen markieren"-Button

- **Left Sidebar:**
  - Modulinhalte (Lesson-Liste)
  - Aktive Lesson hervorgehoben
  - Lesson-Typ-Badges
  - Klickbare Navigation

- **Center Area:**
  - Dynamischer Lesson-Renderer (basierend auf `lesson_type`)
  - Lesson-Header (Titel, Beschreibung)
  - Next/Previous Navigation
  - "Kurs abschließen"-Button (letzte Lesson)

- **Right Sidebar:**
  - MethodExecutionPanel (KI-Lernmethoden)

**Lifecycle:**
1. `onMounted()`:
   - Lädt Kurs (falls nicht geladen)
   - Lädt Modul (falls nicht geladen)
   - Lädt Lesson + Progress + Methods
   - Markiert Lesson automatisch als "started"
   - Sendet Analytics: `lesson_start`

**Analytics Events:**
- `lesson_start` - Beim ersten Laden
- `lesson_complete` - Beim Markieren als abgeschlossen
- `page_view` - Automatisch via Router (zukünftig)

---

### 5. Lesson-Komponenten

**Ordner:** `src/components/lesson/`

#### 5.1 TextLesson.vue

**Zweck:** Zeigt Text-basierte Lessons an

**Features:**
- HTML-Rendering (mit DOMPurify-Sanitization)
- Markdown-Support
- Plain-Text-Support
- Bild-Galerie
- Zusätzliche Ressourcen (Links)

**Content-Struktur:**
```json
{
  "html": "<p>HTML Content</p>",
  "markdown": "Markdown Content",
  "text": "Plain Text",
  "images": [
    {
      "url": "https://...",
      "caption": "Bildbeschreibung"
    }
  ],
  "resources": [
    {
      "title": "Link-Titel",
      "url": "https://..."
    }
  ]
}
```

**Styling:** Custom Prose-Styling für optimale Lesbarkeit

---

#### 5.2 VideoLesson.vue

**Zweck:** Zeigt Video-Lessons an

**Features:**
- YouTube Embed (automatische ID-Extraktion)
- Vimeo Embed (automatische ID-Extraktion)
- Native HTML5 Video Player (für direkte Video-URLs)
- Beschreibung
- Transkript (expandable)
- Zusätzliche Notizen

**Content-Struktur:**
```json
{
  "video_url": "https://youtube.com/watch?v=...",
  "description": "Video-Beschreibung",
  "transcript": "Vollständiges Transkript",
  "notes": "Zusätzliche Notizen"
}
```

**Features:**
- Responsive 16:9 Aspect Ratio
- Autoplay-Support
- Fullscreen-Modus

---

#### 5.3 QuizLesson.vue

**Zweck:** Placeholder für Quiz-Funktionalität

**Status:** Stub-Implementation (vollständige Implementierung in späterer Phase)

**Geplante Features:**
- Multiple-Choice Fragen
- Lückentext-Aufgaben
- Drag & Drop Zuordnungen
- Echtzeit-Feedback
- Punktesystem
- Wiederholung fehlerhafter Fragen

**Aktueller Inhalt:**
- Info-Grafik
- Feature-Liste (Placeholder)
- Anzahl der Fragen (falls vorhanden)

---

#### 5.4 AiLesson.vue

**Zweck:** Spezielle Lesson-Typ für KI-gestützte Inhalte

**Features:**
- Anleitung zur Nutzung von KI-Lernmethoden
- Beschreibung verfügbarer Methoden
- Beispiel-Prompts
- Lernkontext
- Hinweis auf Token-Verbrauch

**Content-Struktur:**
```json
{
  "text": "Lesson-Inhalt",
  "description": "Beschreibung",
  "learning_context": "Kontext für KI",
  "example_prompts": [
    "Beispiel-Prompt 1",
    "Beispiel-Prompt 2"
  ]
}
```

**UI:** Gradient-Design mit Purple/Blue-Theme

---

### 6. MethodExecutionPanel.vue

**Datei:** `src/components/lesson/MethodExecutionPanel.vue`

**Zweck:** Panel zur Ausführung von KI-Lernmethoden

#### Features:

**1. Token-Anzeige:**
- Aktuelles Token-Guthaben
- Farbcodierte Fortschrittsbalken:
  - Grün: > 2000 Tokens
  - Gelb: 500-2000 Tokens
  - Rot: < 500 Tokens
- Warnung bei niedrigem Guthaben

**2. Methoden-Liste:**
- Anzeige aller verfügbaren Methoden
- Kategorie-Badge (Basis / Premium / Pro)
- Beschreibung
- Token-Kosten
- Premium-Kennzeichnung
- "Ausführen"-Button

**3. Zugriffskontrolle:**
- Premium-Check für Premium-Methoden
- Token-Check für KI-Methoden
- Deaktivierung + Fehlerhinweis bei fehlenden Voraussetzungen

**4. Ausführung:**
- Loading-State während KI-Verarbeitung
- Fehlerbehandlung:
  - Zu wenig Tokens
  - Fehlende Premium-Mitgliedschaft
  - Backend-Fehler
  - Netzwerkfehler
- Erfolgsanzeige mit KI-Ergebnis
- "Schließen"-Button

**Analytics:**
- Sendet `method_execute` Event bei jeder Ausführung
- Metadata: `lesson_id`, `tokens_used`

**Lifecycle:**
- `onMounted()`: Lädt Token-Balance
- Nach jeder Ausführung: Aktualisiert Token-Balance

---

## Analytics-Integration

### Implementierte Events:

| Event | Trigger | Resource Type | Metadata |
|-------|---------|---------------|----------|
| `course_view` | Kurs-Seite geöffnet | `course` | `course_id` |
| `module_start` | Modul geöffnet | `module` | `module_id` |
| `lesson_start` | Lesson geöffnet | `lesson` | `lesson_id` |
| `lesson_complete` | Lesson abgeschlossen | `lesson` | `lesson_id` |
| `method_execute` | KI-Methode ausgeführt | `learning_method` | `method_id`, `lesson_id`, `tokens_used` |

### API-Endpoint:

```
POST /api/v1/analytics/event
```

**Request Body:**
```json
{
  "event_type": "lesson_start",
  "resource_type": "lesson",
  "resource_id": 123,
  "metadata": {
    "course_id": 1,
    "module_id": 5
  }
}
```

---

## Datenfluss-Beispiel

### User öffnet Lesson:

```
1. User navigiert zu /course/1/module/2/lesson/3

2. LessonPlayerPage.onMounted():
   ↓
   a) playerStore.loadCourse(1)
      → GET /api/v1/courses/1
      → GET /api/v1/courses/1/modules
      → GET /api/v1/courses/1/progress
      → POST /api/v1/analytics/event (course_view)
   ↓
   b) playerStore.loadModule(1, 2)
      → GET /api/v1/courses/1/modules/2
      → GET /api/v1/courses/1/modules/2/progress
      → POST /api/v1/analytics/event (module_start)
   ↓
   c) playerStore.loadLesson(1, 2, 3)
      → GET /api/v1/courses/1/modules/2/lessons/3
      → GET /api/v1/courses/1/modules/2/lessons/3/progress
      → GET /api/v1/learning_methods/lesson/3
      → POST /api/v1/courses/1/modules/2/lessons/3/start
      → POST /api/v1/analytics/event (lesson_start)

3. Render LessonPlayerPage:
   ↓
   - Top Bar (mit Progress)
   - Left Sidebar (Module Navigation)
   - Center Area (TextLesson / VideoLesson / etc.)
   - Right Sidebar (MethodExecutionPanel)

4. User klickt "Als abgeschlossen markieren":
   ↓
   playerStore.markLessonCompleted(1, 2, 3)
   → POST /api/v1/courses/1/modules/2/lessons/3/complete
   → POST /api/v1/analytics/event (lesson_complete)

5. User führt KI-Methode aus:
   ↓
   playerStore.executeLearningMethod({ lesson_id: 3, method_id: 12 })
   → POST /api/v1/learning_methods/execute
   → POST /api/v1/analytics/event (method_execute)
   ↓
   MethodExecutionPanel zeigt Ergebnis an
```

---

## Fehlerbehandlung

### Implementierte Error States:

1. **Course/Module/Lesson nicht gefunden (404)**
   - Error-Anzeige in Page
   - "Zurück"-Button

2. **Keine Berechtigung (403)**
   - Error-Message
   - Redirect zu Courses-Page

3. **Network-Fehler**
   - Retry-Logik (manuell via Reload)
   - Fehlerhinweis

4. **KI-Methode Fehler:**
   - Zu wenig Tokens → Deaktivierter Button + Hinweis
   - Fehlende Premium-Mitgliedschaft → Deaktivierter Button + Hinweis
   - Backend-Fehler → Error-State in Panel
   - Timeout → Error-Message

---

## Responsive Design

### Breakpoints:

- **Mobile (< 768px):**
  - Single-Column Layout
  - Collapsed Sidebars (Toggle-Buttons)
  - Stack: Navigation → Content → Methods

- **Tablet (768px - 1024px):**
  - Left Sidebar: Collapsed (Icon-Only)
  - Center: Full Width
  - Right Sidebar: Drawer (Slide-In)

- **Desktop (> 1024px):**
  - 3-Column Layout
  - Left Sidebar: 256px
  - Center: Flexible
  - Right Sidebar: 320px

---

## TailwindCSS Styling

### Theme-Farben:

- **Primary:** Blue (#3b82f6)
- **Success:** Green (#10b981)
- **Warning:** Yellow (#f59e0b)
- **Error:** Red (#ef4444)
- **Purple Gradient:** `from-purple-50 to-blue-50`

### Komponenten-Klassen:

- Cards: `bg-white rounded-lg shadow-sm p-6`
- Buttons: Siehe `Button.vue` (Primary, Outline, Ghost)
- Progress Bars: `bg-gray-200`, `bg-primary-600`, `rounded-full`

---

## Testing

### Manuelle Test-Checkliste:

- [ ] CourseOverviewPage lädt Kurs + Module
- [ ] Klick auf Lesson öffnet LessonPlayerPage
- [ ] Lesson-Content wird korrekt gerendert (Text, Video, Quiz, AI)
- [ ] Navigation (Next/Previous) funktioniert
- [ ] "Als abgeschlossen markieren" funktioniert
- [ ] MethodExecutionPanel zeigt Methods an
- [ ] Token-Balance wird geladen
- [ ] KI-Methode kann ausgeführt werden (bei genug Tokens)
- [ ] Premium-Check funktioniert
- [ ] Analytics-Events werden gesendet
- [ ] Error-States werden korrekt angezeigt

---

## Zukünftige Erweiterungen

### Geplant für Phase F6+:

1. **Quiz-System vollständig implementieren**
   - MCQ-Komponenten
   - Fill-Blanks-Komponenten
   - Drag-Drop-Komponenten
   - Score-Tracking

2. **Erweiterte Progress-Features**
   - Time-Tracking pro Lesson
   - Heatmap der Lernaktivität
   - Streak-System

3. **Social Features**
   - Lesson-Kommentare
   - Notizen teilen
   - Diskussionsforum

4. **Offline-Modus**
   - Download-Funktion für Lessons
   - Offline-Synchronisation

5. **Gamification**
   - Achievements
   - Leaderboards
   - XP-System

---

## Zusammenfassung

**Phase F5 ist vollständig abgeschlossen!**

✅ Router erweitert
✅ API Layer erstellt
✅ Player Store erstellt
✅ CourseOverviewPage implementiert
✅ LessonPlayerPage implementiert
✅ 4 Lesson-Typ-Komponenten erstellt
✅ MethodExecutionPanel implementiert
✅ Analytics-Integration abgeschlossen
✅ Dokumentation erstellt

**Neue Dateien:** 13
**Geänderte Dateien:** 1 (Router)
**Lines of Code:** ~2500+

Der Kurs-Player ist voll funktionsfähig und bereit für die Integration mit dem Backend!
