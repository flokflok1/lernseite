# Kurs Studio - Komplettes Re-Design (ISO/IEC 26515)

**Datum:** 2025-01-07
**Status:** KONZEPT
**Priorität:** 🔥 KRITISCH - Hauptproblem identifiziert

---

## Problem-Analyse

### Aktueller Zustand (CHAOS)

**AI Studio (8.520 LOC total):**
```
components/admin/ai-operations/studio/
├── AiStudioMain.vue (1270 LOC)           ← DUPLIKAT?
├── views/AiStudioProWindow.vue (1267 LOC) ← DUPLIKAT?
└── tabs/ (13 Tabs, 6.983 LOC)
    ├── KursBuilderTab.vue (608)          ← Zu groß
    ├── AnalyticsTab.vue (560)            ← Zu groß
    ├── GlobalSettingsTab.vue (555)       ← Zu groß
    ├── SystemFeaturesTab.vue (502)       ← Zu groß
    └── ... 9 weitere Tabs
```

**Probleme:**
1. ❌ 2 "Main" Komponenten - unklar welche aktiv
2. ❌ Keine klare mentale Struktur
3. ❌ Tabs sind zu groß (4x >500 LOC)
4. ❌ "AI Studio" vs "Kurs Studio" - falscher Fokus
5. ❌ Verstreute Editor außerhalb (CourseEditor, ChapterEditor...)
6. ❌ Keine psychologische Gruppierung

---

## Vision: "Kurs Studio" (ISO-konform)

### Konzept

**Ein zentraler Workspace für ALLES rund um Kurse:**
- 🎯 Kurs-zentrisch (nicht AI-zentrisch)
- 🧠 Psychologisch gruppiert nach Aufgaben
- ⚡ KI als Werkzeug (nicht als Hauptfokus)
- 📝 Manuell + KI-gestützt in einem Interface
- 🎨 Konsistente UX

---

## ISO-konforme Struktur

### Mentales Modell (User-Perspektive)

```
Kurs Studio
│
├── 📝 ERSTELLEN                    ← Was will ich machen?
│   ├── Kurs aufbauen
│   ├── Kapitel hinzufügen
│   ├── Lektionen erstellen
│   └── Lernmethoden definieren
│
├── ✏️ BEARBEITEN                   ← Inhalte verfeinern
│   ├── Kurs-Metadaten
│   ├── Kapitel-Struktur
│   ├── Lektions-Inhalte
│   └── Methoden-Konfiguration
│
├── 👁️ VORSCHAU                    ← Wie sieht's aus?
│   ├── Kurs-Übersicht
│   ├── Kapitel-Ansicht
│   ├── Lektions-Player
│   └── Methoden-Preview
│
├── 🤖 KI-ASSISTENZ                ← KI als Helfer
│   ├── Chat-Assistent
│   ├── Content-Generation
│   ├── Tutor-Preview
│   └── Exam-Generator
│
├── 📊 ANALYSE                     ← Wie läuft's?
│   ├── Nutzungs-Statistiken
│   ├── KI-Kosten
│   ├── Qualitäts-Metriken
│   └── Performance
│
└── ⚙️ KONFIGURATION              ← Einstellungen
    ├── KI-Modelle
    ├── Prompts
    ├── System-Features
    └── Global Settings
```

---

## Technische Architektur

### Neue Struktur (ISO-konform)

```
components/admin/kurs-studio/              ← Umbenennen!
│
├── KursStudioWorkspace.vue (200 LOC)      ← Haupt-Orchestrator
│
├── views/                                  ← Top-Level Views
│   ├── KursStudioWindow.vue (150 LOC)     ← Window-Wrapper
│   └── KursStudioPage.vue (150 LOC)       ← Standalone-Page
│
├── layout/                                 ← Layout-Komponenten
│   ├── StudioSidebar.vue (200 LOC)        ← Navigation
│   ├── StudioHeader.vue (100 LOC)         ← Context-Anzeige
│   ├── StudioFooter.vue (80 LOC)          ← Status-Bar
│   └── StudioTabBar.vue (150 LOC)         ← Tab-Verwaltung
│
├── erstellen/                              ← ERSTELLEN-Bereich
│   ├── KursBuilderView.vue (300 LOC)      ← Haupt-View
│   ├── panels/
│   │   ├── StructurePanel.vue (200 LOC)   ← Struktur-Baum
│   │   ├── MaterialsPanel.vue (200 LOC)   ← Upload/Dateien
│   │   └── WorkflowPanel.vue (250 LOC)    ← Workflow-Steuerung
│   └── composables/
│       └── useKursBuilder.ts (200 LOC)    ← Shared Logic
│
├── bearbeiten/                             ← BEARBEITEN-Bereich
│   ├── KursEditorView.vue (250 LOC)       ← Orchestrator
│   ├── editors/
│   │   ├── CourseMetaEditor.vue (200 LOC)
│   │   ├── ChapterEditor.vue (300 LOC)
│   │   ├── LessonEditor.vue (300 LOC)
│   │   └── MethodEditor.vue (250 LOC)
│   └── composables/
│       ├── useCourseEditor.ts (150 LOC)
│       ├── useChapterEditor.ts (150 LOC)
│       └── useLessonEditor.ts (150 LOC)
│
├── vorschau/                               ← VORSCHAU-Bereich
│   ├── PreviewView.vue (200 LOC)          ← Orchestrator
│   ├── previews/
│   │   ├── CoursePreview.vue (200 LOC)
│   │   ├── ChapterPreview.vue (250 LOC)
│   │   ├── LessonPreview.vue (250 LOC)
│   │   └── MethodPreview.vue (200 LOC)
│   └── composables/
│       └── usePreview.ts (150 LOC)
│
├── ki-assistenz/                           ← KI-ASSISTENZ-Bereich
│   ├── AIAssistantView.vue (250 LOC)      ← Chat-Interface
│   ├── panels/
│   │   ├── ChatPanel.vue (200 LOC)        ← Chat
│   │   ├── GenerationPanel.vue (200 LOC)  ← Content-Gen
│   │   ├── TutorPanel.vue (200 LOC)       ← Tutor-Preview
│   │   └── ExamPanel.vue (200 LOC)        ← Exam-Gen
│   └── composables/
│       ├── useAIChat.ts (200 LOC)
│       └── useContentGeneration.ts (200 LOC)
│
├── analyse/                                ← ANALYSE-Bereich
│   ├── AnalyticsView.vue (250 LOC)        ← Dashboard
│   ├── widgets/
│   │   ├── UsageStats.vue (150 LOC)
│   │   ├── CostAnalysis.vue (150 LOC)
│   │   ├── QualityMetrics.vue (150 LOC)
│   │   └── PerformanceChart.vue (150 LOC)
│   └── composables/
│       └── useAnalytics.ts (150 LOC)
│
├── konfiguration/                          ← KONFIGURATION-Bereich
│   ├── ConfigurationView.vue (200 LOC)    ← Settings
│   ├── panels/
│   │   ├── ModelsPanel.vue (200 LOC)      ← KI-Modelle
│   │   ├── PromptsPanel.vue (200 LOC)     ← Prompts
│   │   ├── FeaturesPanel.vue (200 LOC)    ← System-Features
│   │   └── GlobalPanel.vue (200 LOC)      ← Global Settings
│   └── composables/
│       └── useConfiguration.ts (150 LOC)
│
├── shared/                                 ← Shared Components
│   ├── StudioCard.vue (100 LOC)
│   ├── StudioButton.vue (80 LOC)
│   ├── StudioModal.vue (150 LOC)
│   └── StudioTooltip.vue (80 LOC)
│
└── composables/                            ← Shared Composables
    ├── useStudioNavigation.ts (150 LOC)   ← Navigation
    ├── useStudioState.ts (200 LOC)        ← Global State
    ├── useStudioContext.ts (150 LOC)      ← Context (Kurs/Kapitel)
    └── useStudioHotkeys.ts (100 LOC)      ← Keyboard Shortcuts
```

---

## Migration Strategy

### Phase 1: Struktur aufbauen (1 Session)
1. Ordner-Struktur erstellen
2. KursStudioWorkspace.vue (Haupt-Orchestrator)
3. Layout-Komponenten (Sidebar, Header, Footer)
4. Routing einrichten

### Phase 2: ERSTELLEN-Bereich migrieren (2 Sessions)
1. KursBuilderTab.vue (608 LOC) aufteilen
2. Panels extrahieren (Structure, Materials, Workflow)
3. Composables erstellen
4. Integration testen

### Phase 3: BEARBEITEN-Bereich konsolidieren (2 Sessions)
1. Bestehende Editor zusammenführen
2. Einheitliches Editor-Interface
3. Shared Editor-Logic → Composables
4. Konsistente UX

### Phase 4: VORSCHAU-Bereich aufbauen (1 Session)
1. Preview-Komponenten konsolidieren
2. Einheitliches Preview-Interface
3. Preview-Composables

### Phase 5: KI-ASSISTENZ integrieren (2 Sessions)
1. Chat-Interface modernisieren
2. Generation-Workflows vereinfachen
3. Tutor/Exam-Preview einbinden
4. AI-Composables

### Phase 6: ANALYSE & KONFIGURATION (1 Session)
1. Analytics zusammenführen
2. Settings konsolidieren
3. Models/Prompts/Features-Panels
4. Analytics-Composables

### Phase 7: Cleanup & Polish (1 Session)
1. Alte Studio-Dateien löschen
2. Imports aktualisieren
3. Build-Tests
4. Dokumentation

**TOTAL: 10 Sessions (~20h)**

---

## Naming Convention

### Aktuell (Chaos):
```
AiStudioMain.vue
AiStudioProWindow.vue
KursBuilderTab.vue
```

### Neu (ISO-konform):
```
KursStudioWorkspace.vue          ← Hauptkomponente
KursStudioWindow.vue             ← Window-Wrapper
erstellen/KursBuilderView.vue    ← View-Komponente
erstellen/panels/StructurePanel.vue ← Sub-Panel
```

**Pattern:**
- **Workspace** = Haupt-Orchestrator
- **View** = Top-Level Bereichs-Komponente
- **Panel** = Sub-Komponente eines Views
- **Editor/Preview** = Spezifische Funktionen
- **Composable** = Shared Logic

---

## User Experience Flow

### Typischer Workflow:

```
1. User öffnet "Kurs Studio"
   → KursStudioWorkspace.vue lädt

2. Sidebar zeigt 6 Haupt-Bereiche
   → Erstellen | Bearbeiten | Vorschau | KI | Analyse | Config

3. User wählt "ERSTELLEN"
   → erstellen/KursBuilderView.vue lädt
   → Panels: Structure | Materials | Workflow

4. User lädt PDF hoch (Materials Panel)
   → Automatisch zu "KI-ASSISTENZ" wechseln
   → Generation starten

5. Nach Generation → "VORSCHAU"
   → vorschau/PreviewView.vue
   → Kurs-Preview anzeigen

6. User findet Fehler → "BEARBEITEN"
   → bearbeiten/KursEditorView.vue
   → Kapitel bearbeiten

7. User prüft Kosten → "ANALYSE"
   → analyse/AnalyticsView.vue
   → KI-Kosten Dashboard

8. User speichert & schließt
   → Zurück zu Admin-Dashboard
```

**UX-Prinzipien:**
- ✅ Klare mentale Modelle (was vs. wie)
- ✅ Konsistente Navigation
- ✅ Kontextuelle Hilfe (KI als Assistent)
- ✅ Vorhersagbare Workflows
- ✅ Keyboard Shortcuts

---

## Code-Metriken (Ziel)

| Komponente | Max LOC | Aktuell | Ziel |
|------------|---------|---------|------|
| Workspace | 200 | 1270 | 200 |
| View | 300 | 608 | 250 |
| Panel | 200 | - | 200 |
| Editor | 300 | 1026 | 300 |
| Composable | 200 | - | 150 |

**Gesamt-Reduktion:**
- Vorher: 8.520 LOC (Studio) + ~6.000 (externe Editoren) = **14.520 LOC**
- Nachher: ~8.000 LOC (alles integriert) = **-45% LOC**

---

## Breaking Changes

### Was ändert sich:

1. **Import-Pfade:**
   ```typescript
   // ALT:
   import AiStudioMain from '@/components/admin/ai-operations/studio/AiStudioMain.vue'

   // NEU:
   import { KursStudioWorkspace } from '@/components/admin/kurs-studio'
   ```

2. **Routing:**
   ```typescript
   // ALT:
   /admin/ki-studio

   // NEU:
   /admin/kurs-studio
   ```

3. **Window-Types:**
   ```typescript
   // ALT:
   'admin-ai-studio'

   // NEU:
   'admin-kurs-studio'
   ```

### Backward Compatibility:

```typescript
// Deprecated (6 Monate Support):
export { KursStudioWorkspace as AiStudioMain }
```

---

## Vorteile des Re-Designs

### Für User:
- ✅ Intuitivere Navigation (mentale Modelle)
- ✅ Schnellere Workflows (weniger Klicks)
- ✅ Konsistente UX überall
- ✅ KI als Helfer (nicht als Hauptfokus)
- ✅ Alles in einem Workspace

### Für Entwickler:
- ✅ Klare Struktur (ISO-konform)
- ✅ Wartbare Komponenten (<300 LOC)
- ✅ Wiederverwendbare Composables
- ✅ Testbare Module
- ✅ Dokumentierte Architektur

### Für das Projekt:
- ✅ Reduzierte Komplexität (-45% LOC)
- ✅ Bessere Skalierbarkeit
- ✅ Einfachere Erweiterungen
- ✅ Professionelleres Produkt

---

## Nächste Schritte

1. **User Approval** - Konzept bestätigen
2. **Phase 1 Start** - Struktur aufbauen
3. **Iteratives Refactoring** - Bereich für Bereich
4. **Continuous Testing** - Nach jeder Phase

---

## Fragen zur Klärung

1. **Name:** "Kurs Studio" oder "Course Studio"?
2. **Bereiche:** Sind die 6 Bereiche passend?
3. **Priorität:** Welcher Bereich zuerst? (Empfehlung: ERSTELLEN)
4. **Timeline:** 10 Sessions = ~2 Wochen OK?

---

**Status:** ✅ KONZEPT BEREIT
**Nächster Schritt:** User Approval + Phase 1 Start
