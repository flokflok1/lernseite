# 3D Avatar & Feedback System

**Version:** 1.0
**Datum:** 2024-12
**Status:** Implementiert

---

## Übersicht

Das 3D Avatar & Feedback System erweitert den bestehenden TutorCompanion um:
1. **VRM Avatar Support** - Ready Player Me kompatible 3D-Avatare
2. **Lip-Sync** - Echtzeit-Lippensynchronisation mit Audio-Analyse
3. **Whiteboard/Classroom Modus** - Avatar steht vor Tafel wie ein echter Lehrer
4. **Feedback Button** - Separates Fenster für Nutzer-Fragen und Feedback
5. **KI-Zusammenfassung** - Automatische Analyse und Zusammenfassung von Feedback

---

## Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vue.js)                         │
├─────────────────────────────────────────────────────────────────┤
│  AvatarContainer.vue                                             │
│  ├── Avatar3D.vue (Three.js + VRM)                              │
│  │   ├── Robot Avatar (eingebaut)                               │
│  │   ├── VRM Avatar (Ready Player Me)                           │
│  │   └── Whiteboard Scene                                        │
│  ├── FeedbackWindow.vue                                          │
│  └── Chat Interface                                              │
├─────────────────────────────────────────────────────────────────┤
│  Stores:                                                         │
│  ├── avatar.store.ts (VRM, Lip-Sync, Erscheinung)               │
│  └── tutor.store.ts (Chat, Persönlichkeit, TTS)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   API Endpoints   │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                        Backend (Flask)                           │
├─────────────────────────────────────────────────────────────────┤
│  /api/v1/feedback/*                                              │
│  ├── POST /submit - Feedback einreichen                         │
│  ├── GET /my - Eigene Feedbacks abrufen                         │
│  ├── GET / - Alle Feedbacks (Admin)                             │
│  ├── GET /<id> - Details (Admin)                                │
│  ├── PATCH /<id>/status - Status ändern                         │
│  ├── POST /<id>/respond - Antworten                             │
│  └── POST /generate-summary - KI-Zusammenfassung                │
├─────────────────────────────────────────────────────────────────┤
│  Services:                                                       │
│  ├── FeedbackService - Geschäftslogik                           │
│  └── FeedbackRepository - Datenbank                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │    PostgreSQL     │
                    │  Migration 067    │
                    └───────────────────┘
```

---

## Features

### 1. 3D Avatar Stile

| Stil | Beschreibung | Technologie |
|------|--------------|-------------|
| **Robot** | Klassischer lilaner Lernroboter "Lumi" | Three.js Geometrie |
| **Human** | Realistische menschliche Avatare | VRM (Ready Player Me) |
| **Anime** | Anime-Stil Tutoren | VRM (VRoid) |
| **Custom** | Eigene VRM-Dateien | VRM Upload |

### 2. Avatar Modi

```
┌─────────────────────────────────────────────────────────────────┐
│ FLOATING (Standard)                                              │
│ - Kleiner Avatar (120x120px)                                    │
│ - Schwebt unten rechts/links                                     │
│ - Klick öffnet Chat                                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ EXPANDED                                                         │
│ - Größerer Avatar (300x300px)                                   │
│ - Auto-Expand beim Sprechen (optional)                          │
│ - Mehr Details sichtbar                                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CLASSROOM/WHITEBOARD                                             │
│ - Avatar steht vor Whiteboard                                   │
│ - Tafel zeigt aktuellen Inhalt                                  │
│ - "Lehrer vor der Klasse" Feeling                               │
│ - Zeige-Animation auf wichtige Stellen                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Lip-Sync System

```typescript
// Audio-Analyse für Lip-Sync
const updateLipSync = () => {
  analyser.getByteFrequencyData(dataArray)

  // Durchschnittsvolumen berechnen
  const avgVolume = sum / dataArray.length / 255

  // Auf Mund-Animation anwenden
  lipSyncData = {
    mouthOpen: avgVolume * 0.8,    // Wie weit Mund offen
    mouthWide: avgVolume * 0.3,    // Wie breit
    viseme: avgVolume > 0.1 ? 'aa' : 'sil',
    volume: avgVolume
  }
}
```

### 4. Feedback-Kategorien

| Kategorie | Icon | Beschreibung |
|-----------|------|--------------|
| Frage | ❓ | Allgemeine Fragen zum System |
| Problem/Bug | 🐛 | Technische Probleme melden |
| Vorschlag | 💡 | Verbesserungsvorschläge |
| Lob | ⭐ | Positives Feedback |
| Sonstiges | 📝 | Alles andere |

---

## Datenbank (Migration 067)

### Tabellen

```sql
-- Haupttabelle für Feedback
CREATE TABLE user_feedback (
    feedback_id UUID PRIMARY KEY,
    user_id UUID,                    -- Optional für anonym
    is_anonymous BOOLEAN,
    email VARCHAR(255),

    feedback_type VARCHAR(20),       -- question, bug, suggestion, praise, other
    title VARCHAR(255),
    message TEXT NOT NULL,

    -- Kontext
    context_course_id UUID,
    context_lesson_id UUID,
    context_page VARCHAR(100),
    context_url TEXT,

    -- Status
    status VARCHAR(20),              -- new, read, in_progress, resolved, closed
    priority VARCHAR(10),            -- low, normal, high, urgent

    -- KI-Analyse
    ai_summary TEXT,
    ai_category VARCHAR(50),
    ai_sentiment VARCHAR(20),        -- positive, neutral, negative, mixed
    ai_tags TEXT[],

    -- Admin-Antwort
    admin_response TEXT,
    admin_responded_at TIMESTAMPTZ
);

-- Batch-Zusammenfassungen für Admin-Dashboard
CREATE TABLE feedback_summary_batches (
    batch_id UUID PRIMARY KEY,
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,

    total_feedbacks INTEGER,
    ai_executive_summary TEXT,
    ai_key_themes JSONB,
    ai_action_items JSONB
);
```

---

## API Endpoints

### Public (ohne Auth)

```
POST /api/v1/feedback/submit
  Request: {
    type: "question" | "bug" | "suggestion" | "praise" | "other",
    message: string,
    title?: string,
    email?: string,
    is_anonymous?: boolean,
    context?: {
      course_id?: string,
      lesson_id?: string,
      page_context?: string,
      url?: string
    }
  }
  Response: { feedback_id: string }
```

### Authenticated

```
GET /api/v1/feedback/my
  Response: { feedbacks: FeedbackItem[] }
```

### Admin Only

```
GET  /api/v1/feedback                    - Liste mit Filtern
GET  /api/v1/feedback/<id>               - Details
PATCH /api/v1/feedback/<id>/status       - Status ändern
PATCH /api/v1/feedback/<id>/priority     - Priorität ändern
POST /api/v1/feedback/<id>/respond       - Antworten
POST /api/v1/feedback/<id>/notes         - Interne Notiz
GET  /api/v1/feedback/dashboard          - Dashboard Stats
POST /api/v1/feedback/generate-summary   - KI-Zusammenfassung erstellen
GET  /api/v1/feedback/summaries          - Zusammenfassungen abrufen
```

---

## Frontend-Komponenten

### AvatarContainer.vue

Hauptkomponente die alles zusammenfasst:

```vue
<template>
  <div v-if="tutorStore.settings.enabled">
    <!-- Floating Avatar -->
    <div :class="positionClasses">
      <Avatar3D :mode="currentMode" />

      <!-- Action Buttons neben Avatar -->
      <div class="action-buttons">
        <button @click="openFeedback">Feedback</button>
        <button @click="toggleExpand">Expand</button>
        <button @click="showSettings">Settings</button>
      </div>
    </div>

    <!-- Chat Window -->
    <ChatWindow v-if="showChat" />

    <!-- Feedback Window -->
    <FeedbackWindow v-if="showFeedback" />

    <!-- Settings Panel -->
    <SettingsPanel v-if="showSettings" />
  </div>
</template>
```

### Avatar3D.vue

3D-Rendering mit Three.js:

```typescript
// VRM laden (Ready Player Me)
const loadVRMAvatar = async (url: string) => {
  const loader = new GLTFLoader()
  loader.register((parser) => new VRMLoaderPlugin(parser))

  const gltf = await loader.loadAsync(url)
  vrmAvatar = gltf.userData.vrm as VRM

  // Lip-Sync auf VRM anwenden
  vrmAvatar.expressionManager?.setValue('aa', lipSync.mouthOpen)
}

// Whiteboard erstellen
const createWhiteboard = () => {
  // Canvas für dynamischen Inhalt
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')

  // Text auf Whiteboard schreiben
  ctx.fillText(content, canvas.width / 2, 80)

  // Als Textur verwenden
  whiteboardTexture = new THREE.CanvasTexture(canvas)
}
```

---

## KI-Feedback-Analyse

### Einzelanalyse

```python
def analyze_feedback_with_ai(feedback_id: str):
    """
    Analysiert einzelnes Feedback:
    - Zusammenfassung
    - Kategorie (technisch, inhaltlich, usability, etc.)
    - Sentiment (positiv, neutral, negativ)
    - Tags/Keywords
    """
    prompt = f"""
    Analysiere das Feedback:
    Typ: {feedback['feedback_type']}
    Nachricht: {feedback['message']}

    Extrahiere:
    1. Kurze Zusammenfassung
    2. Kategorie
    3. Stimmung
    4. 3-5 relevante Tags
    """
```

### Batch-Zusammenfassung

```python
def generate_summary_batch(period_start, period_end):
    """
    Erstellt Executive Summary für Zeitraum:
    - Wichtigste Punkte
    - Top 5 Themen/Trends
    - Priorisierte Handlungsempfehlungen
    - Sentiment-Verteilung
    """
```

---

## Verwendung

### Im Layout einbinden

```vue
<!-- App.vue oder MainLayout.vue -->
<template>
  <div>
    <router-view />

    <!-- Avatar global einbinden -->
    <AvatarContainer
      :course-id="currentCourseId"
      :lesson-id="currentLessonId"
      :course-name="currentCourseName"
    />
  </div>
</template>
```

### Avatar-Einstellungen

Im Settings-Panel können Nutzer konfigurieren:

- **Avatar-Stil**: Robot, Human, Anime, Custom VRM
- **Persönlichkeit**: Freundlich, Streng, Humorvoll, Geduldig
- **Position**: Links oder Rechts
- **Sprachausgabe**: An/Aus, Automatisch vorlesen
- **Lip-Sync**: An/Aus
- **Auto-Expand**: Beim Sprechen vergrößern
- **Whiteboard**: In Kursen Whiteboard-Modus aktivieren

---

## Dateien

### Backend

```
backend/
├── database/
│   └── 067_feedback_system.sql
├── app/
│   ├── api/
│   │   └── feedback.py
│   ├── services/
│   │   └── feedback_service.py
│   └── repositories/
│       └── feedback_repository.py
```

### Frontend

```
frontend/src/
├── api/
│   └── feedback.api.ts
├── store/
│   └── avatar.store.ts
└── components/tutor/
    ├── AvatarContainer.vue    # Hauptcontainer
    ├── Avatar3D.vue           # 3D-Rendering
    ├── FeedbackWindow.vue     # Feedback-Formular
    └── TutorCompanion.vue     # Legacy (wird ersetzt)
```

---

## Token-Nutzung

| Operation | Tokens (ca.) |
|-----------|-------------|
| Einzelanalyse | 200-500 |
| Batch-Summary (50 Feedbacks) | 1000-2000 |
| Feedback mit TTS | +100-500 |

---

## Nächste Schritte

1. **VRM-Bibliothek**: Sammlung von vorgefertigten Avataren
2. **Avatar-Editor**: Eigene Avatare im Browser erstellen
3. **Animationen**: Mixamo-Integration für mehr Gesten
4. **Email-Benachrichtigung**: Bei Admin-Antwort auf Feedback
5. **Spracheingabe**: Direkt mit Avatar sprechen (STT)
