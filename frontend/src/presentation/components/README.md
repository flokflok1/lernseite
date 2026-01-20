# Frontend Components

> **Architektur:** Domain-Driven Design (DDD)
> **Stand:** 2026-01-07

## Struktur

```
components/
├── admin/      # Admin-Panel (DDD-Domains)
├── user/       # User-facing Komponenten
├── shared/     # Gemeinsam genutzte Komponenten
├── desktop/    # Desktop-Window-System
└── ads/        # Werbung/Ads
```

---

## admin/ - Admin-Bereich

Organisiert nach **Business-Domains**:

### content-management/
CMS-Funktionen - Kurse, Kapitel, Lektionen

| Ordner | Inhalt |
|--------|--------|
| `courses/` | CourseCreate, CourseEditor, CourseFiles, CourseForm |
| `chapters/` | ChapterEditor, ChapterManager, ChapterPreview |
| `lessons/` | LessonEditor, LessonPreview |
| `learning-methods/` | LearningMethodEditor |
| `learning-methods/forms/` | LM00-LM11 Formulare |
| `categories/` | CategoryModal, CategoryTreeNode |
| `editor/` | ChapterLessonTree, CourseMetaForm, LessonContentEditor |

### ai-operations/
KI-Funktionen - nach Funktion gruppiert

| Gruppe | Ordner | Inhalt |
|--------|--------|--------|
| **studio/** | `studio/` | AiStudioMain (Hauptkomponente) |
| | `studio/tabs/` | KursBuilderTab, TutorTab, ExamsTab, ModelsTab, GlobalSettingsTab, etc. |
| **authoring/** | `authoring/kurs-builder/` | ChatPanel, MaterialsPanel, StructurePanel, WorkflowPanel |
| | `authoring/tutor/` | ChapterTheoryView, LessonExplanationView |
| | `authoring/generation/` | ChapterGenerator |
| **management/** | `management/jobs/` | AIJobMain |
| | `management/models/` | ModelSelector |
| | `management/pricing/` | AIPricingMain, PricingTable, MarginCalculator |
| | `management/prompts/` | PromptBrowser |
| **settings/** | `settings/global-settings/` | ApiKeyModal, ProfileEditor, ProfileList, ProviderGrid |
| | `settings/exams/` | StatsCard, FormulaModal, MethodCard, etc. |
| | `settings/models/` | ModelCard, ProviderRow, CategorySelector |

### Weitere Domains
- `user-management/` - Benutzer, Organisationen, Rollen
- `assessment/` - Prüfungsverwaltung
- `system-operations/` - Einstellungen, Analytics, Audit
- `shared/` - Admin-spezifische Shared (DeleteConfirmModal)

---

## user/ - Benutzer-Bereich

| Ordner | Inhalt |
|--------|--------|
| `lessons/` | AiLesson, TextLesson, VideoLesson, QuizLesson, QuizResult, DetailedSteps, MathTaskModal, MethodExecutionPanel |
| `lessons/quiz/` | TrueFalseQuestion, MultipleChoiceQuestion |
| `tutor/` | TutorCompanion, LessonTutorPlayer, InteractiveWhiteboard, OnScreenCalculator, AnimatedTeacher, Avatar3D, etc. |
| `chapters/` | ChapterTheorySection |
| `courses/` | CourseCard, EnrolledCourseCard |
| `dashboard/` | DashboardWidgetsArea, WidgetConfigPanel |
| `dashboard/widgets/` | CoursesProgressWidget, EnrolledCoursesWidget, OrgOverviewWidget, PlanTokensWidget, ProfileSummaryWidget, WelcomeWidget |
| `system-features/` | 25 System-Features (WhiteboardEngine, ITSandbox, etc.) |
| `gamification/` | RpgCharacterCard, RpgInventorySummary, RpgQuestList, RpgSkillTree |
| `exams/` | ExamSimulation |

---

## shared/ - Gemeinsame Komponenten

| Ordner | Inhalt |
|--------|--------|
| `ui/` | Button, Card, Input, LanguageSelector |
| `charts/` | AnalyticsKpiCard, BarChart, LineChart |
| `layout/` | Header, Footer, Sidebar, Navigation |
| `audio/` | AudioRecorder |

---

## desktop/ - Desktop-System

| Datei/Ordner | Funktion |
|--------------|----------|
| `LsxDesktopLayer.vue` | Haupt-Container |
| `LsxDesktopWindow.vue` | Basis-Fenster |
| `LsxTaskbar.vue` | Taskleiste |
| `windows/` | Admin-Fenster (Admin*Window.vue) |
| `containers/` | Container für AI-Studio, Pricing |

---

## Import-Beispiele

```typescript
// Shared UI
import { Button, Card } from '@/components/shared/ui'

// Charts
import { LineChart, BarChart } from '@/components/shared/charts'

// Admin Content Management
import { CourseEditor } from '@/components/admin/content-management/courses'
import { ChapterLessonTree } from '@/components/admin/content-management/editor'

// User Components
import { QuizLesson, AiLesson } from '@/components/user/lessons'
import { TutorCompanion } from '@/components/user/tutor'
```

---

## Lernmethoden (LM00-LM11)

| Gruppe | IDs | Fokus |
|--------|-----|-------|
| **A** Erklärend | LM00-LM04 | Verständnis |
| **B** Praxis | LM05-LM08 | Anwenden |
| **C** Prüfung | LM09-LM11 | Testen |

Editor: `admin/content-management/learning-methods/forms/`

## System-Features (25)

In `user/system-features/` - Zusatz-Tools wie WhiteboardEngine, ITSandbox, IHKExamSystem, NPCTutor, etc.
