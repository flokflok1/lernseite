# 42 – Kurs-Lektions-Struktur

**Version:** 1.0
**Stand:** Dezember 2024

---

## Überblick

Die **Kurs-Lektions-Struktur** definiert die vollständige Hierarchie von Lerninhalten im LSX-System. Sie verbindet das flexible Kategorie-System mit Kursen, Kapiteln, Lektionen und den 19 Content-Lernmethoden sowie System-Features.

### Kernkonzepte

| Ebene | Beschreibung | Enthält |
|-------|--------------|---------|
| **Kategorie** | Flexibles Hierarchie-System (1-20 Ebenen) | Kurse |
| **Kurs** | Lerneinheit mit Metadaten | Kapitel |
| **Kapitel** | Thematische Gruppierung | Lektionen + Theorieblatt |
| **Lektion** | Einzelne Lerneinheit | Aufgaben + System-Features |

### Begriffszuordnung: UI vs. System

| UI (Frontend) | System (Backend) | Beschreibung |
|---------------|------------------|--------------|
| **Aufgabe** | `learning_method_instance` | Was der Lerner sieht und bearbeitet |
| Aufgaben-Typ | `method_type` (LM00-LM25) | Die 19 Content-Lernmethoden |

> **Wichtig:** Im Frontend/UI heißt es immer **"Aufgabe"** (benutzerfreundlich).
> Im Backend/System heißt es **"LM"** oder **"learning_method_instance"** (technisch).

---

## 1. Gesamtstruktur

### 1.1 Hierarchie-Diagramm

```
📁 Kategorie (flexibel, bis 20 Ebenen)
│   └── z.B. IT → Netzwerk → Cisco → CCNA
│
└── 📚 Kurs
    ├── Metadaten (Titel, Beschreibung, Sprache, etc.)
    ├── Kurs-Einstellungen
    │   └── Aktivierte System-Features (kurs-weit)
    │
    └── 📖 Kapitel (1-n)
        │
        ├── 📑 Tab: Theorieblätter
        │   └── Kapitel-Zusammenfassung (Theorie für gesamtes Kapitel)
        │
        └── 📝 Tab: Lektionen (1-n)
            │
            └── Lektion
                ├── Lektions-Theorieblatt (optional)
                ├── Lernmethoden (LM00-LM25, 19 Content-LMs)
                └── System-Features (Taschenrechner, Tutor, etc.)
```

### 1.2 UI-Struktur (basierend auf Screenshots)

**Kurs-Übersicht** (`/course/{course_id}`)
```
┌─────────────────────────────────────────────────────────────────────┐
│                     Deine Lernreise                                 │
│     🧑‍🎓 ──── 🔒2 ──── 🔒3 ──── 🔒4 ──── 🔒5 ──── 🚩           │
│                  (Fortschritts-Pfad)                                │
├─────────────────────────────────────────────────────────────────────┤
│  📖 Kapitel                                                         │
│  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐ │
│  │ 1  IT1: Beschaff. │ │ 2  IT4: Netzwerk  │ │ 3  IT3: SQL       │ │
│  │    & Kalkulation  │ │    & Sicherheit   │ │    & Datenbanken  │ │
│  │    4 Lektionen    │ │    8 Lektionen    │ │    4 Lektionen    │ │
│  │ ▶ IN BEARBEITUNG │ │ 🔒 GESPERRT       │ │ 🔒 GESPERRT       │ │
│  └───────────────────┘ └───────────────────┘ └───────────────────┘ │
│  ┌───────────────────┐ ┌───────────────────┐                       │
│  │ 4  IT2: Program-  │ │ 5  Prüfungs-      │                       │
│  │    mierung        │ │    Simulation     │                       │
│  └───────────────────┘ └───────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Kapitel-Ansicht** (`/course/{course_id}/chapter/{chapter_id}`)
```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Zuruck zum Kurs           IT1: Beschaffung & Kalkulation         │
│                              AP1 Pruefungsvorbereitung              │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  [📖 Theorie]  [📚 Lektionen (4)]                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Lektionen in diesem Kapitel                        0/4 abgeschl.   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ ● 1  Bezugskalkulation         [Interaktiv]            ▶ │    │
│  ├────────────────────────────────────────────────────────────┤    │
│  │ ○ 2  Verkaufskalkulation       [Interaktiv]            ▶ │    │
│  ├────────────────────────────────────────────────────────────┤    │
│  │ ○ 3  Handelskalkulation        [Interaktiv]            ▶ │    │
│  ├────────────────────────────────────────────────────────────┤    │
│  │ ○ 4  Organisationsformen       [Text]                  ▶ │    │
│  └────────────────────────────────────────────────────────────┘    │
│                      [▶ Lernen starten]                             │
└─────────────────────────────────────────────────────────────────────┘
```

**Lektions-Ansicht** (Modal/Overlay)
```
┌─────────────────────────────────────────────────────────────────────┐
│  Lektion 1/4   Bezugskalkulation                              ✕    │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  [📖 Lektion]                    [🤖 Tutor-Erklärung]       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Modus wählen:                                                      │
│  ┌─────────────┐ ┌────────────────┐ ┌────────────────┐            │
│  │ 📖 Das      │ │ ⚡ Speed-      │ │ 📝 Prüfungs-   │            │
│  │   Muster    │ │   Training     │ │   modus        │            │
│  └─────────────┘ └────────────────┘ └────────────────┘            │
│  Schritt-für-Schritt-Erklärung mit ausführlichen Lösungswegen      │
│                                                                     │
│  📊 Aufgaben - Interaktive Übungen zur Lektion                     │
│  (technisch: learning_method_instances)                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Token-Guthaben ████████████████████████████░░░░  8.543    │   │
│  │                                                             │   │
│  │         0              │           0                        │   │
│  │      Generiert         │         Gelöst                     │   │
│  │                                                             │   │
│  │  [📂 Gespeicherte laden]                                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│        [✓ Als abgeschlossen markieren]    [Nächste →]             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Kapitel-Struktur

### 2.1 Kapitel-Tabs

Jedes Kapitel hat zwei Haupt-Tabs:

| Tab | Inhalt | Beschreibung |
|-----|--------|--------------|
| **Lektionen** | Liste aller Lektionen | Interaktive Lerneinheiten mit Aufgaben |
| **Theorieblätter** | Kapitel-Zusammenfassung | Kompakte Theorie für das gesamte Kapitel |

### 2.2 Kapitel-Theorieblatt

Das **Kapitel-Theorieblatt** fasst den gesamten Inhalt eines Kapitels zusammen:

```typescript
interface ChapterTheory {
  chapter_id: string
  title: string
  content_html: string         // Formatierter Inhalt
  content_markdown: string     // Markdown-Quelle
  key_concepts: string[]       // Schlüsselbegriffe
  summary: string              // Kurze Zusammenfassung
  generated_at: Date           // KI-Generierungszeitpunkt
  audio_url?: string           // TTS-Audio (optional)
}
```

**KI-Generierung:**
- Automatisch aus allen Lektionen des Kapitels generiert
- Konsolidiert Schlüsselbegriffe
- Optional mit TTS-Audio

---

## 3. Lektions-Struktur

### 3.1 Lektions-Komponenten

Eine **Lektion** enthält drei Hauptbereiche:

```
┌─────────────────────────────────────────────────────────────┐
│  📝 Lektion: Subnetting-Grundlagen                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📑 Theorieblatt (optional)                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Einführung in Subnetting...                         │   │
│  │ [Audio abspielen 🔊]                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  📊 Aufgaben (UI) = LM-Instanzen (System)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ▸ Aufgabe 1: Schritt-für-Schritt     (LM01)        │   │
│  │ ▸ Aufgabe 2: Subnetting-Rechnung     (LM12)        │   │
│  │ ▸ Aufgabe 3: Verständnistest         (LM22)        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  🔧 System-Features                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [🧮 Taschenrechner]  [📖 Formelsammlung]           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Lektions-Datenmodell

```typescript
interface Lesson {
  lesson_id: string
  chapter_id: string
  title: string
  description?: string
  order_index: number

  // Theorieblatt
  theory?: LessonTheory

  // Aufgaben (UI) = LM-Instanzen (System)
  tasks: LearningMethodInstance[]  // UI: "Aufgaben"

  // System-Features
  enabled_features: SystemFeature[]

  // Metadaten
  estimated_duration: number  // Minuten
  difficulty: 1 | 2 | 3
  created_at: Date
  updated_at: Date
}

interface LessonTheory {
  lesson_id: string
  title: string
  content_html: string
  content_markdown: string
  audio_url?: string
  whiteboard_data?: object  // Für Whiteboard-Darstellung
}
```

---

## 4. Lernmethoden (19 Content-LMs)

### 4.1 Übersicht der Content-Lernmethoden

Die 19 Content-Lernmethoden sind in 3 Gruppen organisiert:

| Gruppe | Name | LM-IDs | Fokus |
|--------|------|--------|-------|
| **A** | Erklärend | LM00-LM03, LM06 | Verständnis aufbauen |
| **B** | Praxis | LM08, LM12-LM15, LM17 | Anwenden & Üben |
| **C** | Prüfung | LM18-LM25 | Prüfungsvorbereitung |

### 4.2 Gruppe A – Erklärende Methoden (5)

| ID | Name | Beschreibung |
|----|------|--------------|
| LM00 | Tiefgehende Erklärung | Ausführliche, KI-generierte Erklärungen |
| LM01 | Schritt-für-Schritt | Sequentielle Anleitung mit Zwischenschritten |
| LM02 | Interaktive Theorie | Theorie mit eingebetteten Interaktionen |
| LM03 | Diagramm/Visualisierung | Grafische Darstellungen und Flowcharts |
| LM06 | Beispiel-Szenario | Praxisnahe Beispiele und Use-Cases |

### 4.3 Gruppe B – Praxis-Methoden (6)

| ID | Name | Beschreibung |
|----|------|--------------|
| LM08 | Whiteboard-Aufgabe | Freihand-Zeichnen und Diagramme |
| LM12 | Mathe-Interaktiv | Berechnungen mit Taschenrechner-Integration |
| LM13 | Flashcards | Karteikarten zum Lernen |
| LM14 | Drag & Drop | Zuordnungs-Aufgaben |
| LM15 | Lückentext | Texte mit Lücken ausfüllen |
| LM17 | Hands-on Lab | Praktische Übungen (IT-Sandbox) |

### 4.4 Gruppe C – Prüfungs-Methoden (8)

| ID | Name | Beschreibung |
|----|------|--------------|
| LM18 | Freitext-Langantwort | Ausführliche schriftliche Antworten |
| LM19 | IHK-Stil Aufgaben | Prüfungsaufgaben im IHK-Format |
| LM20 | Multi-Step Praxisprüfung | Mehrstufige praktische Prüfungen |
| LM21 | Zeitlimit-Training | Übungen unter Zeitdruck |
| LM22 | Prüfungs-Quiz | Multiple-Choice Fragen |
| LM23 | Verständnis-Checks | Kurze Verständnisfragen |
| LM24 | Mündliche Erklärung | Sprachaufnahme zur Erklärung |
| LM25 | Kapitel-Endprüfung | Abschlussprüfung pro Kapitel |

---

## 5. System-Features

### 5.1 Übersicht

**System-Features** sind modulare Funktionen, die pro Kurs oder Lektion aktiviert werden können. Sie ergänzen die Content-Lernmethoden.

| Feature-ID | Name | Beschreibung | Icon |
|------------|------|--------------|------|
| SF_CALC | Taschenrechner | OnScreenCalculator für Mathe-Aufgaben | 🧮 |
| SF_FORMULA | Formelsammlung | Bibliothek mit Formeln | 📖 |
| SF_TUTOR | KI-Tutor | 3D-Avatar mit Chat-Funktion | 🤖 |
| SF_WHITEBOARD | Whiteboard | Freihand-Zeichenfläche | 🎨 |
| SF_SANDBOX | IT-Sandbox | Virtuelle Umgebung für IT-Labs | 💻 |
| SF_TIMER | Prüfungstimer | Countdown für Zeitlimit-Aufgaben | ⏱️ |
| SF_NOTES | Notizen | Persönliche Notizen zur Lektion | 📝 |
| SF_BOOKMARKS | Lesezeichen | Wichtige Stellen markieren | 🔖 |

### 5.2 Feature-Aktivierung (3 Quellen)

System-Features sind **standardmäßig immer verfügbar** und können aus 3 Quellen gesteuert werden:

```
┌─────────────────────────────────────────────────────────────┐
│  Feature-Quellen (Priorität)                                │
├─────────────────────────────────────────────────────────────┤
│  1. LM-basiert (Standard)     → Immer verfügbar via Mapping │
│  2. User/Admin (Optional)     → Kann ein-/ausschalten       │
│  3. KI-Empfehlung (Optional)  → Kann vorschlagen/aktivieren │
└─────────────────────────────────────────────────────────────┘
```

**Beispiel:**
```
Lektion enthält Aufgabe mit LM12 (Mathe-Interaktiv)
  → SF_CALC ist verfügbar (LM-Mapping)
  → User kann SF_CALC ausblenden (Präferenz)
  → KI kann SF_CALC hervorheben wenn nötig
```

### 5.3 LM → Feature Mapping

| LM-Typ | Name | Aktivierte Features |
|--------|------|---------------------|
| **LM12** | Mathe-Interaktiv | `SF_CALC`, `SF_FORMULA` |
| **LM08** | Whiteboard-Aufgabe | `SF_WHITEBOARD` |
| **LM17** | Hands-on Lab | `SF_SANDBOX` |
| **LM21** | Zeitlimit-Training | `SF_TIMER` |
| **LM19** | IHK-Stil Aufgaben | `SF_CALC`, `SF_TIMER` |
| **LM20** | Multi-Step Praxisprüfung | `SF_CALC`, `SF_TIMER`, `SF_NOTES` |
| **LM04** | Sokratischer Dialog | `SF_TUTOR` |
| *Alle LMs* | - | `SF_NOTES`, `SF_BOOKMARKS` (Standard) |

```typescript
// LM → Feature Mapping (Backend-Konfiguration)
const LM_FEATURE_MAP: Record<number, string[]> = {
  4:  ['SF_TUTOR'],                           // Sokratischer Dialog
  8:  ['SF_WHITEBOARD'],                      // Whiteboard-Aufgabe
  12: ['SF_CALC', 'SF_FORMULA'],              // Mathe-Interaktiv
  17: ['SF_SANDBOX'],                         // Hands-on Lab
  19: ['SF_CALC', 'SF_TIMER'],                // IHK-Stil
  20: ['SF_CALC', 'SF_TIMER', 'SF_NOTES'],    // Multi-Step Praxis
  21: ['SF_TIMER'],                           // Zeitlimit-Training
}

// Standard-Features für alle Lektionen
const DEFAULT_FEATURES = ['SF_NOTES', 'SF_BOOKMARKS']
```

### 5.4 Feature-Auflösung (3 Quellen)

```typescript
interface FeatureState {
  feature_id: string
  available: boolean      // Via LM-Mapping verfügbar
  visible: boolean        // User-Präferenz (ein-/ausgeblendet)
  highlighted: boolean    // KI-Empfehlung (hervorgehoben)
  pinned: boolean         // User hat angepinnt
}

function getFeatureStates(
  lesson: Lesson,
  userId: string,
  kiSession?: KiSession
): FeatureState[] {

  // 1. LM-basiert: Welche Features sind verfügbar?
  const available = new Set<string>(DEFAULT_FEATURES)
  for (const task of lesson.tasks) {
    const lmFeatures = LM_FEATURE_MAP[task.method_type] || []
    lmFeatures.forEach(f => available.add(f))
  }

  // 2. User-Präferenzen laden
  const userPrefs = getUserFeaturePreferences(userId)

  // 3. KI-Empfehlungen (falls vorhanden)
  const kiRecs = kiSession?.recommended_features || []
  const kiHighlight = kiSession?.highlight_feature

  // Kombinieren
  return Array.from(available).map(featureId => ({
    feature_id: featureId,
    available: true,
    visible: userPrefs[featureId]?.is_visible ?? true,
    highlighted: featureId === kiHighlight,
    pinned: userPrefs[featureId]?.is_pinned ?? false
  }))
}

// Beispiel-Ergebnis:
// [
//   { feature_id: "SF_CALC", available: true, visible: true, highlighted: true, pinned: false },
//   { feature_id: "SF_FORMULA", available: true, visible: false, highlighted: false, pinned: false },
//   { feature_id: "SF_NOTES", available: true, visible: true, highlighted: false, pinned: true }
// ]
```

### 5.5 Feature-Anzeige im Frontend

```typescript
// Features werden nach Status sortiert angezeigt:
// 1. Angepinnt (pinned) - immer oben
// 2. KI-hervorgehoben (highlighted) - mit Glow-Effekt
// 3. Sichtbar (visible) - normal angezeigt
// 4. Ausgeblendet (visible=false) - im "Mehr"-Menü

interface FeatureBarProps {
  features: FeatureState[]
  onToggleVisibility: (featureId: string) => void
  onTogglePin: (featureId: string) => void
}
```

### 5.6 MathToolkit als System-Feature (SF_CALC)

Der **Taschenrechner** (SF_CALC) nutzt das MathToolkit-Backend:

```typescript
// Wenn SF_CALC aktiviert ist:
// 1. OnScreenCalculator wird in der Lektion angezeigt
// 2. Bei Mathe-Lektionen (LM12) automatisch aktiviert
// 3. Backend-Session für Verlauf und Fortschritt

interface MathToolkitIntegration {
  session_id: string
  lesson_id: string
  enabled_features: {
    calculator: boolean      // OnScreenCalculator
    memory: boolean          // M+, M-, MR, MC
    history: boolean         // Verlauf speichern
    formulas: boolean        // Formelsammlung
    patterns: boolean        // Rechenweg-Muster
  }
}
```

---

## 6. Datenbank-Schema

### 6.1 Relevante Tabellen

```sql
-- Kurse
CREATE TABLE courses (
  course_id UUID PRIMARY KEY,
  category_id INTEGER REFERENCES course_categories(category_id),
  title VARCHAR(255) NOT NULL,
  -- ... weitere Felder
);

-- Kapitel
CREATE TABLE chapters (
  chapter_id UUID PRIMARY KEY,
  course_id UUID REFERENCES courses(course_id),
  title VARCHAR(255) NOT NULL,
  order_index INTEGER DEFAULT 0,
  -- Kapitel-Theorieblatt
  theory_content TEXT,
  theory_audio_url VARCHAR(500)
);

-- Lektionen
CREATE TABLE lessons (
  lesson_id UUID PRIMARY KEY,
  chapter_id UUID REFERENCES chapters(chapter_id),
  title VARCHAR(255) NOT NULL,
  order_index INTEGER DEFAULT 0,
  estimated_duration INTEGER,
  difficulty INTEGER DEFAULT 1
);

-- Lektions-Theorieblätter
CREATE TABLE lesson_theory (
  theory_id UUID PRIMARY KEY,
  lesson_id UUID REFERENCES lessons(lesson_id),
  content_html TEXT,
  content_markdown TEXT,
  audio_url VARCHAR(500),
  whiteboard_data JSONB
);

-- Lernmethoden-Instanzen
CREATE TABLE learning_method_instances (
  instance_id UUID PRIMARY KEY,
  lesson_id UUID REFERENCES lessons(lesson_id),
  method_type INTEGER CHECK (method_type BETWEEN 0 AND 32),
  content_data JSONB,
  order_index INTEGER DEFAULT 0
);

-- System-Features Registry
CREATE TABLE system_features (
  feature_id VARCHAR(20) PRIMARY KEY,  -- z.B. 'SF_CALC'
  name VARCHAR(100) NOT NULL,
  description TEXT,
  icon VARCHAR(10),
  is_default BOOLEAN DEFAULT FALSE     -- Standard für alle Lektionen?
);

-- LM → Feature Mapping (welcher LM-Typ aktiviert welche Features)
CREATE TABLE lm_feature_mapping (
  method_type INTEGER NOT NULL,        -- LM00-LM32
  feature_id VARCHAR(20) NOT NULL REFERENCES system_features(feature_id),
  PRIMARY KEY (method_type, feature_id)
);

-- Beispiel-Daten:
INSERT INTO system_features VALUES
  ('SF_CALC', 'Taschenrechner', 'OnScreenCalculator für Mathe', '🧮', FALSE),
  ('SF_FORMULA', 'Formelsammlung', 'Bibliothek mit Formeln', '📖', FALSE),
  ('SF_TUTOR', 'KI-Tutor', '3D-Avatar mit Chat', '🤖', FALSE),
  ('SF_WHITEBOARD', 'Whiteboard', 'Freihand-Zeichenfläche', '🎨', FALSE),
  ('SF_SANDBOX', 'IT-Sandbox', 'Virtuelle Umgebung', '💻', FALSE),
  ('SF_TIMER', 'Prüfungstimer', 'Countdown', '⏱️', FALSE),
  ('SF_NOTES', 'Notizen', 'Persönliche Notizen', '📝', TRUE),
  ('SF_BOOKMARKS', 'Lesezeichen', 'Markierungen', '🔖', TRUE);

INSERT INTO lm_feature_mapping VALUES
  (12, 'SF_CALC'), (12, 'SF_FORMULA'),  -- LM12: Mathe-Interaktiv
  (8, 'SF_WHITEBOARD'),                  -- LM08: Whiteboard
  (17, 'SF_SANDBOX'),                    -- LM17: Hands-on Lab
  (21, 'SF_TIMER'),                      -- LM21: Zeitlimit
  (19, 'SF_CALC'), (19, 'SF_TIMER'),     -- LM19: IHK-Stil
  (20, 'SF_CALC'), (20, 'SF_TIMER'),     -- LM20: Multi-Step
  (4, 'SF_TUTOR');                       -- LM04: Sokratisch

-- User-Präferenzen für Features (optional, überschreibt LM-Mapping)
CREATE TABLE user_feature_preferences (
  user_id UUID REFERENCES users(user_id),
  feature_id VARCHAR(20) REFERENCES system_features(feature_id),
  is_visible BOOLEAN DEFAULT TRUE,       -- User hat Feature ein-/ausgeblendet
  is_pinned BOOLEAN DEFAULT FALSE,       -- User hat Feature angepinnt
  PRIMARY KEY (user_id, feature_id)
);

-- KI-Feature-Empfehlungen (temporär, pro Session)
CREATE TABLE ki_feature_recommendations (
  session_id UUID PRIMARY KEY,
  lesson_id UUID REFERENCES lessons(lesson_id),
  user_id UUID REFERENCES users(user_id),
  recommended_features JSONB,            -- ["SF_CALC", "SF_FORMULA"]
  highlight_feature VARCHAR(20),         -- Aktuell hervorgehobenes Feature
  reason TEXT,                           -- KI-Begründung
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP                   -- Auto-Cleanup
)
```

---

## 7. Frontend-Komponenten

### 7.1 Übersicht

```
frontend/src/
├── pages/
│   ├── CoursePage.vue            # Kurs-Übersicht
│   ├── ChapterPage.vue           # Kapitel mit Tabs
│   └── LessonPage.vue            # Lektions-Player
│
├── components/
│   ├── chapter/
│   │   ├── ChapterTabs.vue       # Lektionen/Theorieblätter Tabs
│   │   ├── LessonList.vue        # Liste der Lektionen
│   │   └── ChapterTheory.vue     # Kapitel-Theorieblatt
│   │
│   ├── lesson/
│   │   ├── LessonPlayer.vue      # Haupt-Lektions-Container
│   │   ├── LessonTheory.vue      # Lektions-Theorieblatt
│   │   ├── LearningMethodPanel.vue # LM-Anzeige
│   │   └── SystemFeaturesBar.vue # Feature-Buttons
│   │
│   └── tutor/
│       └── OnScreenCalculator.vue # Taschenrechner
```

### 7.2 LessonPlayer mit System-Features

```vue
<template>
  <div class="lesson-player">
    <!-- Theorieblatt (falls vorhanden) -->
    <LessonTheory v-if="lesson.theory" :theory="lesson.theory" />

    <!-- Lernmethoden -->
    <LearningMethodPanel
      v-for="lm in lesson.learning_methods"
      :key="lm.instance_id"
      :method="lm"
    />

    <!-- System-Features Bar -->
    <SystemFeaturesBar :features="enabledFeatures">
      <!-- Taschenrechner -->
      <OnScreenCalculator
        v-if="hasFeature('SF_CALC')"
        :show-memory="true"
        :show-history="true"
        :session-id="mathSession?.session_id"
        :save-to-backend="true"
      />

      <!-- Formelsammlung -->
      <FormulaLibrary v-if="hasFeature('SF_FORMULA')" />

      <!-- KI-Tutor -->
      <TutorCompanion v-if="hasFeature('SF_TUTOR')" />
    </SystemFeaturesBar>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useLessonStore } from '@/store/lesson.store'

const lessonStore = useLessonStore()
const lesson = computed(() => lessonStore.currentLesson)
const enabledFeatures = computed(() => lessonStore.enabledFeatures)

function hasFeature(featureId: string): boolean {
  return enabledFeatures.value.includes(featureId)
}
</script>
```

---

## 8. API-Endpunkte

### 8.1 Kapitel-API

```python
# Kapitel mit Lektionen laden
GET /api/v1/courses/{course_id}/chapters/{chapter_id}
Response: {
  "chapter": { ... },
  "lessons": [ ... ],
  "theory": { ... }  # Kapitel-Theorieblatt
}

# Kapitel-Theorieblatt
GET /api/v1/chapters/{chapter_id}/theory
POST /api/v1/chapters/{chapter_id}/theory/generate  # KI-Generierung
```

### 8.2 Lektions-API

```python
# Lektion mit allen Inhalten laden
GET /api/v1/lessons/{lesson_id}
Response: {
  "lesson": { ... },
  "theory": { ... },           # Lektions-Theorieblatt
  "learning_methods": [ ... ], # Content-LMs
  "enabled_features": [ ... ]  # System-Features
}

# Lektions-Features aktualisieren (Admin)
PATCH /api/v1/admin/lessons/{lesson_id}/features
{
  "calc_override": true,
  "formula_override": true
}
```

### 8.3 System-Features API (LM-basiert)

```python
# === Alle System-Features abrufen ===
GET /api/v1/system-features
Response: {
  "features": [
    { "feature_id": "SF_CALC", "name": "Taschenrechner", "icon": "🧮", "is_default": false },
    { "feature_id": "SF_NOTES", "name": "Notizen", "icon": "📝", "is_default": true },
    ...
  ]
}

# === LM → Feature Mapping abrufen (Admin) ===
GET /api/v1/admin/lm-feature-mapping
Response: {
  "mapping": {
    "12": ["SF_CALC", "SF_FORMULA"],
    "8": ["SF_WHITEBOARD"],
    ...
  }
}

# === LM → Feature Mapping aktualisieren (Admin) ===
PATCH /api/v1/admin/lm-feature-mapping/{method_type}
{
  "features": ["SF_CALC", "SF_FORMULA", "SF_TIMER"]
}

# === Effektive Features für Lektion (automatisch berechnet) ===
GET /api/v1/lessons/{lesson_id}/features
Response: {
  "features": ["SF_CALC", "SF_FORMULA", "SF_TIMER", "SF_NOTES", "SF_BOOKMARKS"],
  "by_task": [
    { "task_id": "...", "method_type": 12, "provides": ["SF_CALC", "SF_FORMULA"] },
    { "task_id": "...", "method_type": 21, "provides": ["SF_TIMER"] }
  ],
  "defaults": ["SF_NOTES", "SF_BOOKMARKS"]
}
```

---

## 9. Zusammenfassung

### Hierarchie

```
Kategorien (1-20 Ebenen)
└── Kurse
    └── Kapitel (mehrere pro Kurs)
        ├── Tab: Theorieblätter (Kapitel-Zusammenfassung)
        └── Tab: Lektionen (mehrere pro Kapitel)
            ├── Tab: Lektion (Lerninhalt)
            │   ├── Lektions-Theorieblatt
            │   ├── Aufgaben (UI) = LM-Instanzen (System)
            │   └── System-Features (automatisch via LM)
            └── Tab: Tutor-Erklärung
```

### Feature-Aktivierung (3 Quellen)

```
┌─────────────────────────────────────────────────────────────┐
│  1. LM-Mapping (Standard)   → Features immer verfügbar      │
│  2. User-Präferenz          → Ein-/Ausblenden, Anpinnen     │
│  3. KI-Empfehlung           → Hervorheben, Vorschlagen      │
└─────────────────────────────────────────────────────────────┘

LM → Feature Mapping:
  LM12 (Mathe)       → 🧮 SF_CALC, 📖 SF_FORMULA
  LM08 (Whiteboard)  → 🎨 SF_WHITEBOARD
  LM17 (Hands-on)    → 💻 SF_SANDBOX
  LM21 (Zeitlimit)   → ⏱️ SF_TIMER
  Alle               → 📝 SF_NOTES, 🔖 SF_BOOKMARKS
```

### Aufgaben (UI) vs. LM (System) vs. System-Features

| Aspekt | Aufgaben / LM | System-Features (SF) |
|--------|---------------|----------------------|
| **UI-Begriff** | Aufgabe | Feature |
| **System-Begriff** | `learning_method_instance` | `system_feature` |
| **Zweck** | Lerninhalt bearbeiten | Hilfswerkzeuge |
| **Typen** | 19 LMs (LM00-LM25) | 8+ Features |
| **Instanzen** | Pro Lektion mehrere | Pro Lektion automatisch |
| **Content** | Enthalten Lerninhalt | Kein eigener Content |
| **Aktivierung** | Vom Admin erstellt | **Automatisch via LM-Typ** |

---

**Dokument erstellt:** Dezember 2024
**Autor:** Claude (KI-Assistent)
**Referenzen:**
- 02_Lernmethoden.md
- 04_Kurs-Architektur.md
- 12_Kurs-Kategorisierung-Flexibles-System.md
