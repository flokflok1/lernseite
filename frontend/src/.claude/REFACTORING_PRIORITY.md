# Frontend Refactoring Priority List 🚨

**Datum:** 2025-01-07
**Status:** 49 Dateien über 500 Zeilen (G05-Verstoß!)

---

## Executive Summary

| Kategorie | Anzahl >500 LOC | Worst Offender | Max LOC |
|-----------|-----------------|----------------|---------|
| Pages | 12 | ChapterDetailPage.vue | 2315 (462%) |
| Components/User | 18 | LessonTutorPlayer.vue | 1692 (338%) |
| Components/Admin | 30 | LessonExplanationView.vue | 1322 (264%) |
| Store | 5 | admin.store.ts | 1353 (271%) |
| API/Composables | 3 | api/admin/types.ts | 1121 (224%) |
| **TOTAL** | **68 Dateien** | | |

---

## Top 20 Kritische Dateien (Priorität 1)

### 🔥 EXTREME (>1500 Zeilen)

| Rang | Datei | LOC | Über Limit | Priorität |
|------|-------|-----|-----------|-----------|
| 1 | **pages/ChapterDetailPage.vue** | 2315 | +1815 | 🔥🔥🔥 |
| 2 | **components/user/tutor/LessonTutorPlayer.vue** | 1692 | +1192 | 🔥🔥🔥 |
| 3 | **components/user/lessons/MethodExecutionPanel.vue** | 1601 | +1101 | 🔥🔥🔥 |

### 🚨 KRITISCH (1000-1500 Zeilen)

| Rang | Datei | LOC | Über Limit | Priorität |
|------|-------|-----|-----------|-----------|
| 4 | store/admin.store.ts | 1353 | +853 | 🚨🚨 |
| 5 | components/admin/ai-operations/authoring/tutor/LessonExplanationView.vue | 1322 | +822 | 🚨🚨 |
| 6 | pages/admin/AdminCourseDetailPage.vue | 1319 | +819 | 🚨🚨 |
| 7 | components/admin/ai-operations/studio/AiStudioMain.vue | 1270 | +770 | 🚨🚨 |
| 8 | components/admin/ai-operations/studio/views/AiStudioProWindow.vue | 1267 | +767 | 🚨🚨 |
| 9 | components/user/tutor/RealisticTeacher3D.vue | 1173 | +673 | 🚨🚨 |
| 10 | api/admin/types.ts | 1121 | +621 | 🚨🚨 |
| 11 | components/admin/content-management/learning-methods/LearningMethodEditor.vue | 1054 | +554 | 🚨 |
| 12 | components/admin/content-management/learning-methods/views/LearningMethodEditorWindow.vue | 1051 | +551 | 🚨 |
| 13 | components/admin/content-management/chapters/ChapterEditor.vue | 1026 | +526 | 🚨 |
| 14 | components/admin/content-management/chapters/views/KapitelEditorWindow.vue | 1022 | +522 | 🚨 |

### ⚠️ HOCH (800-1000 Zeilen)

| Rang | Datei | LOC | Über Limit | Priorität |
|------|-------|-----|-----------|-----------|
| 15 | pages/CourseOverviewPage.vue | 951 | +451 | ⚠️ |
| 16 | components/admin/ai-operations/authoring/tutor/ChapterTheoryView.vue | 945 | +445 | ⚠️ |
| 17 | components/admin/content-management/lessons/views/LessonPreviewWindow.vue | 879 | +379 | ⚠️ |
| 18 | pages/dashboard/DashboardPage.vue | 877 | +377 | ⚠️ |
| 19 | components/admin/content-management/lessons/LessonPreview.vue | 876 | +376 | ⚠️ |
| 20 | pages/admin/AdminAISettingsPage.vue | 856 | +356 | ⚠️ |

---

## Refactoring-Strategie nach Bereich

### 1. PAGES (12 Dateien)

**Problem:** Routing-Pages zu groß → sollten nur Orchestrierung sein!

**ChapterDetailPage.vue (2315 LOC)** 🔥🔥🔥
```
Aktuell: Monolith mit allem (Theory, Progress, Lessons, UI)
Ziel:
pages/ChapterDetailPage.vue          (150 LOC) ← Orchestrierung
└── components/user/chapters/
    ├── ChapterHeader.vue            (100 LOC)
    ├── ChapterTheorySection.vue     (200 LOC) ← Existiert (818 LOC!)
    ├── ChapterProgressBar.vue       (80 LOC)
    ├── LessonList.vue               (150 LOC)
    └── ChapterActions.vue           (100 LOC)
```

**AdminCourseDetailPage.vue (1319 LOC)** 🚨
```
Ziel:
pages/admin/AdminCourseDetailPage.vue  (150 LOC)
└── components/admin/content-management/courses/
    ├── CourseHeader.vue               (100 LOC)
    ├── CourseMetadata.vue             (120 LOC)
    ├── ChapterList.vue                (200 LOC)
    ├── CourseStats.vue                (150 LOC)
    └── CourseActions.vue              (100 LOC)
```

**Weitere Pages >500:**
- CourseOverviewPage.vue (951)
- DashboardPage.vue (877)
- AdminAISettingsPage.vue (856)
- ExamSimulationPage.vue (808)
- AdminPromptsPage.vue (768)
- LessonPlayerPage.vue (637)
- AdminTranslationsPage.vue (616)
- AdminCoursesPage.vue (585)
- AdminUsersPage.vue (577)
- AdminRolesPage.vue (555)

**Strategie:** Pages sollten max 200 LOC haben - nur Orchestrierung!

---

### 2. COMPONENTS/USER (18 Dateien)

#### Tutor-System (10 Dateien!)

**LessonTutorPlayer.vue (1692 LOC)** 🔥🔥🔥
```
Problem: Monolithischer Tutor mit allem
Ziel:
components/user/tutor/
├── LessonTutorPlayer.vue           (200 LOC) ← Orchestrator
├── avatar/
│   ├── TutorAvatar.vue             (200 LOC) ← Aktuell 821!
│   ├── Avatar3D.vue                (200 LOC) ← Aktuell 629!
│   ├── AvatarContainer.vue         (200 LOC) ← Aktuell 620!
│   ├── AnimatedTeacher.vue         (200 LOC) ← Aktuell 626!
│   └── RealisticTeacher3D.vue      (300 LOC) ← Aktuell 1173!
├── interaction/
│   ├── TutorCompanion.vue          (200 LOC) ← Aktuell 696!
│   ├── InteractiveWhiteboard.vue   (250 LOC) ← Aktuell 776!
│   └── OnScreenCalculator.vue      (250 LOC) ← Aktuell 731!
└── composables/
    ├── useTutorState.ts            (150 LOC)
    ├── useTutorAnimation.ts        (150 LOC)
    └── useTutorInteraction.ts      (150 LOC)
```

**Refactoring-Plan Tutor:**
1. Avatar-Komponenten in `tutor/avatar/` zusammenfassen
2. Shared Logic → Composables extrahieren
3. 3D-Rendering in separate Module
4. State-Management vereinfachen

#### Lessons (4 Dateien)

**MethodExecutionPanel.vue (1601 LOC)** 🔥🔥🔥
```
Problem: Alle 33 Lernmethoden in einer Datei!
Ziel:
components/user/lessons/
├── MethodExecutionPanel.vue        (200 LOC) ← Router
└── method-renderers/
    ├── TextMethodRenderer.vue      (150 LOC)
    ├── VideoMethodRenderer.vue     (150 LOC)
    ├── QuizMethodRenderer.vue      (200 LOC)
    ├── MathMethodRenderer.vue      (250 LOC)
    └── ... (pro Methode ein Renderer)
```

**Weitere Lesson-Komponenten:**
- WhiteboardTutorLesson.vue (833)
- MathTaskModal.vue (751)
- OralExplanationLesson.vue (664)

#### Gamification (4 Dateien)

**RpgSkillTree.vue (692 LOC)**
```
Ziel:
components/user/gamification/
├── RpgSkillTree.vue                (200 LOC)
├── SkillNode.vue                   (100 LOC)
├── SkillConnection.vue             (80 LOC)
└── SkillTooltip.vue                (100 LOC)
```

- RpgQuestList.vue (646) → Quest-Komponenten
- RpgInventorySummary.vue (554) → Item-Komponenten
- RpgCharacterCard.vue (547) → Stat-Komponenten

---

### 3. COMPONENTS/ADMIN (30 Dateien!)

#### AI-Operations (13 Dateien)

**LessonExplanationView.vue (1322 LOC)** 🚨
```
Ziel:
components/admin/ai-operations/authoring/tutor/
├── LessonExplanationView.vue       (250 LOC)
├── ExplanationEditor.vue           (200 LOC)
├── ExplanationPreview.vue          (200 LOC)
├── StepManager.vue                 (150 LOC)
└── ExplanationSettings.vue         (150 LOC)
```

**AiStudioMain.vue (1270 LOC) + AiStudioProWindow.vue (1267 LOC)** 🚨
```
Problem: Duplikat-Code + zu groß
Lösung:
1. Einen behalten (AiStudioProWindow.vue)
2. In Sub-Komponenten aufteilen:
   - Tabs bereits vorhanden ✅
   - Main orchestriert nur Tabs
   - Shared-Logic → Composables
```

**Weitere AI-Operations:**
- ChapterTheoryView.vue (945)
- ModelSelector.vue (827)
- ModelSelectorWindow.vue (824)
- AIPricingMain.vue (648)
- WorkflowPanel.vue (637)
- KursBuilderTab.vue (608)
- AnalyticsTab.vue (560)
- GlobalSettingsTab.vue (555)
- SystemFeaturesTab.vue (502)

#### Content-Management (14 Dateien)

**Pattern:** Editor + Window Duplikate!

**Learning Methods:**
- LearningMethodEditor.vue (1054)
- LearningMethodEditorWindow.vue (1051)
→ **DUPLIKAT! Einen löschen + anderen refactoren**

**Chapters:**
- ChapterEditor.vue (1026)
- KapitelEditorWindow.vue (1022)
- ChapterPreview.vue (617)
- ChapterPreviewWindow.vue (613)
→ **DUPLIKATE! Je einen löschen**

**Lessons:**
- LessonPreviewWindow.vue (879)
- LessonPreview.vue (876)
- LessonEditorWindow.vue (655)
- LessonEditor.vue (644)
→ **DUPLIKATE! Je einen löschen**

**Courses:**
- CourseEditorWindow.vue (639)
- CourseEditor.vue (639)
- CourseCreate.vue (587)
- CourseCreateWindow.vue (585)
→ **DUPLIKATE! Je einen löschen**

**Shared:**
- FilePreview.vue (647)
- FilePreviewWindow.vue (644)

#### Assessment (2 Dateien)
- ExamManager.vue (528)
- ExamManagerWindow.vue (526)
→ **DUPLIKAT!**

---

### 4. STORE (5 Dateien)

**admin.store.ts (1353 LOC)** 🚨
```
Problem: Monolithischer Admin-Store
Ziel:
store/admin/
├── users.store.ts              (200 LOC)
├── courses.store.ts            (200 LOC)
├── ai.store.ts                 (200 LOC)
├── analytics.store.ts          (150 LOC)
├── settings.store.ts           (150 LOC)
└── index.ts                    (50 LOC) ← Re-exports
```

**Weitere Stores:**
- player.store.ts (607) → in Sub-Stores aufteilen
- gamification.store.ts (570) → RPG-Logik separieren
- window.store.ts (554) → OK (Desktop-System)
- courseEditor.store.ts (547) → OK, aber optimierbar

---

### 5. API & COMPOSABLES (3 Dateien)

**api/admin/types.ts (1121 LOC)** 🚨
```
Problem: Alle Admin-Types in einer Datei
Ziel:
api/admin/types/
├── users.types.ts              (150 LOC)
├── courses.types.ts            (150 LOC)
├── ai.types.ts                 (150 LOC)
├── analytics.types.ts          (100 LOC)
├── billing.types.ts            (100 LOC)
├── common.types.ts             (100 LOC)
└── index.ts                    (50 LOC) ← Re-exports
```

**Weitere:**
- useTeachingTimeline.ts (647) → in Sub-Composables
- player.api.ts (541) → in API-Module aufteilen

---

## Refactoring Roadmap

### Phase 1: EXTREME Priority (3 Dateien) 🔥
**Geschätzt: 2-3 Sessions**
1. ChapterDetailPage.vue (2315 → 150 LOC)
2. LessonTutorPlayer.vue (1692 → 200 LOC)
3. MethodExecutionPanel.vue (1601 → 200 LOC)

### Phase 2: Duplikate eliminieren (14 Paare) 🚨
**Geschätzt: 1 Session**
- Editor vs. EditorWindow → einen behalten
- Preview vs. PreviewWindow → einen behalten
- 28 Dateien → 14 Dateien (50% Reduktion)

### Phase 3: KRITISCH (11 Dateien) 🚨
**Geschätzt: 3-4 Sessions**
- admin.store.ts (1353)
- LessonExplanationView.vue (1322)
- AdminCourseDetailPage.vue (1319)
- AiStudioMain.vue (1270)
- AiStudioProWindow.vue (1267)
- RealisticTeacher3D.vue (1173)
- api/admin/types.ts (1121)
- LearningMethodEditor.vue (1054)
- ChapterEditor.vue (1026)
- CourseOverviewPage.vue (951)
- ChapterTheoryView.vue (945)

### Phase 4: HOCH (30+ Dateien) ⚠️
**Geschätzt: 5-6 Sessions**
- Alle 800-1000 LOC Dateien
- Tutor-System komplett
- Gamification-Komponenten
- Remaining Admin-Komponenten

---

## Quick Wins (Niedrig hängende Früchte)

### 1. Duplikate entfernen (SOFORT)
**Aufwand:** 2h
**Impact:** -14 Dateien, -10.000 LOC

Pattern:
```bash
# Editor vs. EditorWindow → EditorWindow behalten (hat Window-Wrapper)
# Editor-Logik → Composable extrahieren
```

### 2. Types aufteilen (EINFACH)
**Aufwand:** 1h
**Impact:** api/admin/types.ts: 1121 → 7x150 LOC

```typescript
// Einfach Typen in Dateien verschieben
// api/admin/types/users.types.ts
// api/admin/types/courses.types.ts
// etc.
```

### 3. Pages vereinfachen (PATTERN)
**Aufwand:** 3-4h pro Page
**Impact:** -1500 LOC pro Page

```vue
<!-- VORHER: ChapterDetailPage.vue (2315 LOC) -->
<template>
  <!-- 2000 Zeilen Template -->
</template>
<script>
  // 300 Zeilen Logic
</script>

<!-- NACHHER: ChapterDetailPage.vue (150 LOC) -->
<template>
  <ChapterDetailView :chapter-id="chapterId" />
</template>
<script setup>
const chapterId = route.params.id
</script>
```

---

## Geschätzter Gesamtaufwand

| Phase | Dateien | Sessions | Tage (1 Session = 2h) |
|-------|---------|----------|----------------------|
| Phase 1 (EXTREME) | 3 | 2-3 | 1-2 |
| Phase 2 (Duplikate) | 14 Paare | 1 | 0.5 |
| Phase 3 (KRITISCH) | 11 | 3-4 | 2 |
| Phase 4 (HOCH) | 30+ | 5-6 | 3 |
| **TOTAL** | **68** | **11-14** | **6-7 Tage** |

---

## Monitoring & Quality Gates

### Nach jedem Refactoring:
- [ ] Datei < 500 LOC ✅
- [ ] Build erfolgreich ✅
- [ ] Keine i18n-Verstöße ✅
- [ ] Barrel Exports erstellt ✅
- [ ] Types extrahiert ✅
- [ ] Composables für Shared Logic ✅

### KPIs:
- **Aktuell:** 68 Dateien >500 LOC
- **Ziel:** 0 Dateien >500 LOC
- **Progress:** Track in `.claude/REFACTORING_PROGRESS.md`

---

**Nächster Schritt:** User entscheidet Priorität
- Option A: Phase 1 (EXTREME) - Worst Offenders
- Option B: Phase 2 (Duplikate) - Quick Wins
- Option C: Spezifischer Bereich (z.B. nur Tutor-System)
