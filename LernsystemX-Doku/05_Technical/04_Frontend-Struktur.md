# 16 – Frontend-Struktur (DDD Architecture)

**Version:** 4.0.4 (Admin Panel Unification + Cleanup)
**Stand:** 21.01.2026
**Änderungen:** Admin Panel formalisiert und konsolidiert - 12 orphaned org-admin files gelöscht, einheitliche Struktur unter `/admin` etabliert

---

## Überblick

Dieses Dokument definiert die **Domain-Driven Design (DDD) Frontend-Architektur** des LSX Lernsystems mit **4 sauberen Layern**.

Das Frontend folgt **Clean Architecture Prinzipien** mit klarer Trennung von:
- **Presentation Layer** - UI Components, Views, Layouts
- **Application Layer** - Business Logic, Services, Stores
- **Domain Layer** - Models, Value Objects, Factories, Business Rules
- **Infrastructure Layer** - API Clients, External Services, WebSocket

### 🎯 DDD Features v4.0.2

- ✅ **4-Layer Architecture** - Presentation → Application → Domain → Infrastructure
- ✅ **Domain Models** - Immutable, Type-Safe, Business Logic Encapsulation
- ✅ **Factory Pattern** - Centralized Object Creation & Validation
- ✅ **Repository Pattern** - Data Access Abstraction
- ✅ **Value Objects** - Email, UserId, PostId (Type Safety)
- ✅ **Aggregate Roots** - User, Post, Course (Domain Boundaries)
- ✅ **Domain Events** - post:created, user:followed (Event-Driven)
- ✅ **Backward Compatible** - Re-export barrels at old locations (6-12 months)
- ✅ **Course Editor** - Manual + AI Editor (direkt als Domain, aligned mit Backend)

### 🛠️ Tech-Stack

| Technologie | Verwendung |
|------------|-----------|
| ⚡ **Vue.js 3** | Composition API + TypeScript |
| 🚀 **Vite** | Build Tool |
| 📦 **Pinia** | State Management (Application Layer) |
| 🛣️ **Vue Router** | Routing (Presentation Layer) |
| 🎨 **TailwindCSS** | Styling |
| 🌍 **vue-i18n** | Internationalisierung |
| 🎥 **WebRTC** | Video/Audio (Infrastructure) |
| 🔌 **WebSockets** | Real-time (Infrastructure) |
| 📡 **Axios** | HTTP Client (Infrastructure) |
| 🎚️ **Feature Flags** | Progressive Rollout |
| 🛡️ **DOMPurify** | XSS Protection |
| **TypeScript** | Full Type Coverage |

---

## 📚 CONTENT-LERNMETHODEN & SYSTEM-FEATURES

### 🎓 Content-Lernmethoden (LM00-LM11)

Das Frontend muss alle **12 Lernmethoden** in 3 Gruppen unterstützen:

| Gruppe | IDs | Anzahl | Fokus | System Features |
|--------|-----|--------|-------|-----------------|
| **A** Erklärend | LM00-LM04 | 5 | Verständnis aufbauen | Whiteboard, Tutor, Video |
| **B** Praxis | LM05-LM08 | 4 | Anwenden & Üben | CodeSandbox, Calculator, SimEnv |
| **C** Prüfung | LM09-LM11 | 3 | Kompetenz nachweisen | Timer, ExamEngine |

**Konkrete Beispiele:**
- **LM00 - Text Erklärung** → Uses: Tutor, Highlights
- **LM01 - Video Erklärung** → Uses: Video Player, Subtitles
- **LM02 - Interaktive Erklärung** → Uses: Whiteboard, 3D Visualization
- **LM05 - Coding Practice** → Uses: CodeSandbox, Debugger
- **LM06 - Math Tasks** → Uses: Calculator, FormulaEditor, GraphPlotter
- **LM09 - Exam** → Uses: Timer, ExamEngine, Proctoring

### 🛠️ System-Features (25 Features)

System Features sind **NICHT** Lernmethoden, sondern **Tools/Technologien**, die Lernmethoden unterstützen.

**10 Kategorien & Zuordnung zu Lernmethoden:**

| Kategorie | Features | Für Lernmethoden | Beispiel |
|-----------|----------|------------------|----------|
| **audio** | Speech-to-Text, TTS | LM00-LM04 (Erklär) | Text in Audio konvertieren |
| **collaboration** | LiveRoom, Chat, Whiteboard | LM00-LM11 (Alle) | Gemeinsames Lernen |
| **exam_systems** | ExamEngine, IHK-System | LM09-LM11 (Prüfung) | Offizielles Testformat |
| **gamification** | XP, Badges, Quests | LM00-LM11 (Alle) | Motivation & Engagement |
| **interactive_tools** | Calculator, FormulaEditor | LM06 (Mathe), LM05 (Code) | Spezifische Werkzeuge |
| **it_environments** | CodeSandbox, VirtualLab | LM05 (Code), LM07 (IT) | Praktische Umgebung |
| **learning_paths** | Curriculum, Roadmap | LM00-LM11 (Alle) | Strukturiertes Lernen |
| **meta_features** | Timer, Bookmarks, Notes | LM00-LM11 (Alle) | Lern-Unterstützung |
| **tutor** | NPC-Tutor, AI-Tutor | LM00-LM04 (Erklär) | KI-gestützte Hilfe |
| **visualization** | 3D-Graphs, Diagrams, Maps | LM00-LM08 (Nicht Prüfung) | Visuelle Erklärungen |

**Beispiel-Verkopplung:**
```
Lernmethode LM06 "Math Tasks" braucht:
├─ Calculator          (interactive_tools)
├─ FormulaEditor       (interactive_tools)
├─ GraphPlotter        (visualization)
├─ Timer               (meta_features)
└─ AI-Tutor            (tutor) - optional für Hilfe
```

---

## 1. DDD 4-Layer Projektstruktur

### 📁 Komplette DDD Verzeichnisstruktur

```
/frontend
├── /public
│   ├── favicon.ico
│   └── /assets
│       ├── /images
│       ├── /icons
│       └── /legal
│           ├── privacy-policy.pdf
│           ├── terms-of-service.pdf
│           └── community-guidelines.pdf
│
├── /src
│   │
│   ├── /presentation                      # 🎨 PRESENTATION LAYER
│   │   ├── /components                    # UI Components
│   │   │   ├── /shared                    # Shared UI Components
│   │   │   │   ├── /ui                    # Base UI (Button, Input, Modal)
│   │   │   │   ├── /layout                # Layout Components
│   │   │   │   └── /forms                 # Form Components
│   │   │   │
│   │   │   ├── /content                   # Content Domain Components
│   │   │   │   ├── CourseCard.vue
│   │   │   │   ├── ChapterList.vue
│   │   │   │   ├── LessonPlayer.vue
│   │   │   │   └── ContentViewer.vue
│   │   │   │
│   │   │   ├── /learning-methods          # 🎓 LERNMETHODEN (LM00-LM11) + SYSTEM-FEATURES
│   │   │   │   │
│   │   │   │   ├── /group-a-explanation/  # Gruppe A: Erklärend (LM00-LM04)
│   │   │   │   │   ├── TextExplanation.vue       # LM00
│   │   │   │   │   ├── VideoExplanation.vue      # LM01
│   │   │   │   │   ├── InteractiveExplanation.vue # LM02
│   │   │   │   │   ├── DiagramVisualization.vue  # LM03
│   │   │   │   │   ├── AnimationLesson.vue       # LM04
│   │   │   │   │   └── /system-features/         # System Features für diese Gruppe
│   │   │   │   │       ├── Whiteboard.vue         # Gemeinsames Zeichnen
│   │   │   │   │       ├── AITutor.vue            # KI-Tutor für Hilfe
│   │   │   │   │       ├── TextHighlight.vue      # Hervorhebungen
│   │   │   │   │       └── VideoPlayer.vue        # Video-Wiedergabe
│   │   │   │   │
│   │   │   │   ├── /group-b-practice/    # Gruppe B: Praxis (LM05-LM08)
│   │   │   │   │   ├── CodingPractice.vue        # LM05
│   │   │   │   │   ├── MathTasks.vue             # LM06
│   │   │   │   │   ├── InteractiveSim.vue        # LM07
│   │   │   │   │   ├── Flashcards.vue            # LM08
│   │   │   │   │   └── /system-features/         # System Features für diese Gruppe
│   │   │   │   │       ├── CodeSandbox.vue        # Coding-Umgebung
│   │   │   │   │       ├── Calculator.vue         # Rechner (Mathe)
│   │   │   │   │       ├── FormulaEditor.vue      # Formeln-Editor
│   │   │   │   │       ├── GraphPlotter.vue       # Graphen zeichnen
│   │   │   │   │       ├── Debugger.vue           # Code-Debugger
│   │   │   │   │       ├── Timer.vue              # Zeitmessung
│   │   │   │   │       └── VirtualLab.vue         # Virtuelle Labore
│   │   │   │   │
│   │   │   │   └── /group-c-assessment/  # Gruppe C: Prüfung (LM09-LM11)
│   │   │   │       ├── ExamSimulation.vue        # LM09
│   │   │   │       ├── IHKExam.vue               # LM10
│   │   │   │       ├── AdaptiveTest.vue          # LM11
│   │   │   │       └── /system-features/         # System Features für diese Gruppe
│   │   │   │           ├── ExamEngine.vue         # Prüfungs-Engine
│   │   │   │           ├── Timer.vue              # Zeitmessung
│   │   │   │           ├── Proctoring.vue         # Überwachung
│   │   │   │           └── ResultAnalytics.vue    # Ergebnis-Analyse
│   │   │   │
│   │   │   ├── /system-features           # 🛠️ SYSTEM-FEATURES (Alle 25 Features)
│   │   │   │   ├── /audio/                # Audio-Features
│   │   │   │   │   ├── SpeechToText.vue
│   │   │   │   │   ├── TextToSpeech.vue
│   │   │   │   │   └── AudioRecorder.vue
│   │   │   │   │
│   │   │   │   ├── /collaboration/        # Zusammenarbeit
│   │   │   │   │   ├── LiveRoom.vue       # Echtzeit-Klassenzimmer
│   │   │   │   │   ├── Whiteboard.vue     # Gemeinsames Whiteboard
│   │   │   │   │   ├── Chat.vue           # Live-Chat
│   │   │   │   │   └── Polling.vue        # Live-Abstimmung
│   │   │   │   │
│   │   │   │   ├── /exam-systems/         # Prüfungs-Systeme
│   │   │   │   │   ├── ExamEngine.vue     # Universelle Prüfungs-Engine
│   │   │   │   │   └── IHKFormat.vue      # IHK-spezifisches Format
│   │   │   │   │
│   │   │   │   ├── /gamification/         # Spielifizierung
│   │   │   │   │   ├── XPDisplay.vue
│   │   │   │   │   ├── BadgesPanel.vue
│   │   │   │   │   ├── QuestList.vue
│   │   │   │   │   └── LeaderboardView.vue
│   │   │   │   │
│   │   │   │   ├── /interactive-tools/    # Interaktive Werkzeuge
│   │   │   │   │   ├── Calculator.vue
│   │   │   │   │   ├── FormulaEditor.vue
│   │   │   │   │   ├── GraphPlotter.vue
│   │   │   │   │   └── Geometry.vue
│   │   │   │   │
│   │   │   │   ├── /it-environments/      # IT-Umgebungen
│   │   │   │   │   ├── CodeSandbox.vue
│   │   │   │   │   ├── VirtualLab.vue
│   │   │   │   │   ├── Debugger.vue
│   │   │   │   │   └── TerminalEmulator.vue
│   │   │   │   │
│   │   │   │   ├── /meta-features/        # Meta-Features
│   │   │   │   │   ├── Timer.vue
│   │   │   │   │   ├── Bookmarks.vue
│   │   │   │   │   ├── Notes.vue
│   │   │   │   │   └── SearchHighlight.vue
│   │   │   │   │
│   │   │   │   ├── /tutor/                # KI-Tutor Features
│   │   │   │   │   ├── NPCTutor.vue       # NPC-Tutor Avatar
│   │   │   │   │   ├── AITutorChat.vue    # AI-Tutor Chat
│   │   │   │   │   └── FeedbackSystem.vue # Intelligentes Feedback
│   │   │   │   │
│   │   │   │   ├── /visualization/        # Visualisierungen
│   │   │   │   │   ├── 3DGraphs.vue
│   │   │   │   │   ├── Diagrams.vue
│   │   │   │   │   ├── MindMaps.vue
│   │   │   │   │   └── AnimationVisualizer.vue
│   │   │   │   │
│   │   │   │   └── /learning-paths/       # Lernpfade
│   │   │   │       ├── Curriculum.vue
│   │   │   │       ├── Roadmap.vue
│   │   │   │       └── ProgressTree.vue
│   │   │   │
│   │   │   ├── /social                    # Social Domain Components
│   │   │   │   ├── PostCard.vue
│   │   │   │   ├── PostComposer.vue
│   │   │   │   ├── CommentSection.vue
│   │   │   │   ├── LikeButton.vue
│   │   │   │   └── FollowButton.vue
│   │   │   │
│   │   │   ├── /user                      # User Domain Components
│   │   │   │   ├── ProfileCard.vue
│   │   │   │   ├── AvatarUpload.vue
│   │   │   │   └── SettingsPanel.vue
│   │   │   │
│   │   │   ├── /admin                     # Admin Domain Components
│   │   │   │   ├── UserManagement.vue
│   │   │   │   ├── CourseApproval.vue
│   │   │   │   └── FeatureFlagControl.vue
│   │   │   │
│   │   │   ├── /compliance                # Compliance Domain Components
│   │   │   │   ├── CookieConsent.vue
│   │   │   │   ├── AgeGate.vue
│   │   │   │   ├── PrivacyDashboard.vue
│   │   │   │   └── DataExport.vue
│   │   │   │
│   │   │   ├── /moderation                # Moderation Domain Components
│   │   │   │   ├── ModerationQueue.vue
│   │   │   │   ├── ContentReview.vue
│   │   │   │   └── ReportDetails.vue
│   │   │   │
│   │   │   ├── /security                  # Security Domain Components
│   │   │   │   ├── TwoFactorAuth.vue
│   │   │   │   ├── SessionManager.vue
│   │   │   │   └── DRMLicenseDisplay.vue
│   │   │   │
│   │   │   └── /course-editor             # 📝 COURSE EDITOR DOMAIN (KEIN STUDIO!)
│   │   │       │
│   │   │       ├── CourseEditorMain.vue            # Main Editor Container
│   │   │       ├── EditorSwitcher.vue              # Switch Manual ↔ AI
│   │   │       │
│   │   │       ├── /manual-editor                  # 📝 MANUAL EDITOR
│   │   │       │   ├── ManualEditorContainer.vue  # Manual Editor Main
│   │   │       │   ├── ContentEditor.vue          # Rich Text Editor
│   │   │       │   ├── StructurePanel.vue         # Course Structure Tree
│   │   │       │   ├── ChapterEditor.vue          # Chapter Management
│   │   │       │   ├── LessonEditor.vue           # Lesson Management
│   │   │       │   ├── MediaUpload.vue            # Image/Video Upload
│   │   │       │   ├── PreviewPanel.vue           # Live Preview
│   │   │       │   └── ToolbarActions.vue         # Save/Publish/Draft
│   │   │       │
│   │   │       └── /ai-editor                      # 🤖 AI EDITOR
│   │   │           ├── AIEditorContainer.vue      # AI Editor Main
│   │   │           ├── ChatInterface.vue          # Chat with AI
│   │   │           ├── PromptBuilder.vue          # Structured Prompts
│   │   │           ├── ContentGenerator.vue       # Generate Content
│   │   │           ├── VariantSelector.vue        # Choose from variants
│   │   │           ├── TemplateLibrary.vue        # Pre-built templates
│   │   │           ├── GenerationHistory.vue      # Previous generations
│   │   │           ├── AISettings.vue             # Model selection, tone
│   │   │           └── AIPreview.vue              # Generated content preview
│   │   │
│   │   ├── /views                         # 📄 PAGES/VIEWS
│   │   │   ├── /auth
│   │   │   │   ├── LoginView.vue
│   │   │   │   ├── RegisterView.vue
│   │   │   │   └── ForgotPasswordView.vue
│   │   │   │
│   │   │   ├── /dashboard
│   │   │   │   ├── DashboardView.vue
│   │   │   │   └── SettingsView.vue
│   │   │   │
│   │   │   ├── /social
│   │   │   │   ├── FeedView.vue
│   │   │   │   ├── ProfileView.vue
│   │   │   │   └── ExploreView.vue
│   │   │   │
│   │   │   ├── /content
│   │   │   │   ├── CourseListView.vue
│   │   │   │   ├── CourseDetailView.vue
│   │   │   │   └── LessonView.vue
│   │   │   │
│   │   │   ├── /course-editor             # 📝 COURSE EDITOR VIEWS
│   │   │   │   ├── EditorView.vue                 # Main editor view
│   │   │   │   ├── ProjectsView.vue               # My projects
│   │   │   │   ├── TemplatesView.vue              # Template library
│   │   │   │   └── HistoryView.vue                # Generation history
│   │   │   │
│   │   │   └── /admin
│   │   │       ├── AdminDashboardView.vue
│   │   │       ├── UsersView.vue
│   │   │       └── FeatureFlagsView.vue
│   │   │
│   │   ├── /layouts                       # Layouts
│   │   │   ├── MainLayout.vue
│   │   │   ├── AuthLayout.vue
│   │   │   ├── DashboardLayout.vue
│   │   │   ├── AdminLayout.vue
│   │   │   └── EditorLayout.vue           # Course Editor Layout
│   │   │
│   │   └── /router                        # Router Configuration
│   │       ├── index.ts
│   │       ├── routes.ts
│   │       ├── guards.ts
│   │       └── middleware.ts
│   │
│   ├── /application                       # 🏗️ APPLICATION LAYER
│   │   ├── /services                      # Business Logic Services
│   │   │   ├── /content
│   │   │   │   ├── CourseService.ts       # Course business logic
│   │   │   │   └── LessonService.ts       # Lesson business logic
│   │   │   │
│   │   │   ├── /social
│   │   │   │   ├── PostService.ts         # Post business logic
│   │   │   │   ├── CommentService.ts      # Comment business logic
│   │   │   │   └── FeedService.ts         # Feed aggregation logic
│   │   │   │
│   │   │   ├── /user
│   │   │   │   ├── AuthService.ts         # Authentication logic
│   │   │   │   └── ProfileService.ts      # Profile management
│   │   │   │
│   │   │   ├── /course-editor             # 📝 COURSE EDITOR SERVICES
│   │   │   │   ├── EditorService.ts       # Editor orchestration
│   │   │   │   ├── AIService.ts           # AI generation logic
│   │   │   │   ├── ChatService.ts         # Chat processing
│   │   │   │   ├── VariantService.ts      # Variant management
│   │   │   │   └── TemplateService.ts     # Template handling
│   │   │   │
│   │   │   ├── /admin
│   │   │   │   ├── UserAdminService.ts    # User administration
│   │   │   │   └── FeatureFlagService.ts  # Feature flag management
│   │   │   │
│   │   │   ├── /compliance
│   │   │   │   ├── ConsentService.ts      # Consent management
│   │   │   │   └── PrivacyService.ts      # Privacy operations
│   │   │   │
│   │   │   └── /moderation
│   │   │       ├── ReportService.ts       # Report handling
│   │   │       └── ModerationService.ts   # Moderation workflow
│   │   │
│   │   ├── /stores                        # Pinia Stores (State Management)
│   │   │   ├── /modules
│   │   │   │   ├── /content
│   │   │   │   │   ├── courseViewer.store.ts    # Course viewing (player)
│   │   │   │   │   └── courseLibrary.store.ts   # Course catalog
│   │   │   │   │
│   │   │   │   ├── /course-editor         # 📝 COURSE EDITOR STORES
│   │   │   │   │   ├── editor.store.ts           # Main editor state
│   │   │   │   │   ├── aiEditor.store.ts         # AI editor state
│   │   │   │   │   ├── manualEditor.store.ts     # Manual editor state
│   │   │   │   │   ├── chat.store.ts             # Chat history
│   │   │   │   │   ├── projects.store.ts         # User projects
│   │   │   │   │   └── templates.store.ts        # Templates
│   │   │   │   │
│   │   │   │   ├── /social
│   │   │   │   │   ├── feed.store.ts
│   │   │   │   │   └── social.store.ts
│   │   │   │   │
│   │   │   │   ├── /user
│   │   │   │   │   ├── auth.store.ts
│   │   │   │   │   └── profile.store.ts
│   │   │   │   │
│   │   │   │   └── /core
│   │   │   │       ├── ui.store.ts
│   │   │   │       └── workspace.store.ts
│   │   │   │
│   │   │   └── index.ts
│   │   │
│   │   ├── /composables                   # Vue Composables
│   │   │   ├── useAuth.ts
│   │   │   ├── useSocial.ts
│   │   │   ├── useContent.ts
│   │   │   ├── useCourseEditor.ts         # Course editor composable
│   │   │   ├── useAIEditor.ts             # AI editor composable
│   │   │   ├── useFeatureFlags.ts
│   │   │   └── usePagination.ts
│   │   │
│   │   └── /use-cases                     # Application Use Cases
│   │       ├── CreatePostUseCase.ts       # Create post workflow
│   │       ├── EnrollCourseUseCase.ts     # Enroll in course workflow
│   │       ├── GenerateContentUseCase.ts  # AI content generation
│   │       └── SubmitReportUseCase.ts     # Submit moderation report
│   │
│   ├── /domain                            # 🎯 DOMAIN LAYER
│   │   ├── /models                        # Domain Models (Aggregate Roots)
│   │   │   ├── /content
│   │   │   │   ├── /course
│   │   │   │   │   ├── Course.model.ts    # Course Aggregate Root
│   │   │   │   │   ├── Chapter.model.ts   # Chapter Entity
│   │   │   │   │   └── Lesson.model.ts    # Lesson Entity
│   │   │   │   │
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── /course-editor             # 📝 COURSE EDITOR DOMAIN MODELS
│   │   │   │   ├── Project.model.ts       # Project Aggregate Root
│   │   │   │   ├── ChatSession.model.ts   # Chat Session Entity
│   │   │   │   ├── GeneratedContent.model.ts # Generated content
│   │   │   │   ├── Variant.model.ts       # Content variant
│   │   │   │   └── Template.model.ts      # Template Entity
│   │   │   │
│   │   │   ├── /social
│   │   │   │   ├── Post.model.ts          # Post Aggregate Root
│   │   │   │   ├── Comment.model.ts       # Comment Entity
│   │   │   │   └── Like.model.ts          # Like Value Object
│   │   │   │
│   │   │   ├── /user
│   │   │   │   ├── User.model.ts          # User Aggregate Root
│   │   │   │   ├── Profile.model.ts       # Profile Entity
│   │   │   │   └── Session.model.ts       # Session Value Object
│   │   │   │
│   │   │   ├── /compliance
│   │   │   │   ├── Consent.model.ts       # Consent Aggregate Root
│   │   │   │   └── Report.model.ts        # Report Entity
│   │   │   │
│   │   │   └── /moderation
│   │   │       ├── ContentReport.model.ts # Report Aggregate Root
│   │   │       └── ModerationAction.model.ts
│   │   │
│   │   ├── /value-objects                 # Value Objects (Immutable)
│   │   │   ├── Email.vo.ts                # Email validation
│   │   │   ├── UserId.vo.ts               # Type-safe User ID
│   │   │   ├── PostId.vo.ts               # Type-safe Post ID
│   │   │   ├── CourseId.vo.ts             # Type-safe Course ID
│   │   │   ├── ProjectId.vo.ts            # Type-safe Project ID
│   │   │   └── Timestamp.vo.ts            # Timestamp handling
│   │   │
│   │   ├── /factories                     # Factory Pattern
│   │   │   ├── /content
│   │   │   │   └── Course.factory.ts      # Course creation & validation
│   │   │   │
│   │   │   ├── /course-editor             # 📝 COURSE EDITOR FACTORIES
│   │   │   │   ├── Project.factory.ts     # Project creation
│   │   │   │   ├── ChatSession.factory.ts # Chat session creation
│   │   │   │   └── Template.factory.ts    # Template creation
│   │   │   │
│   │   │   ├── /social
│   │   │   │   ├── Post.factory.ts        # Post creation & validation
│   │   │   │   └── Comment.factory.ts     # Comment creation
│   │   │   │
│   │   │   └── /user
│   │   │       └── User.factory.ts        # User creation & validation
│   │   │
│   │   ├── /events                        # Domain Events
│   │   │   ├── PostCreatedEvent.ts
│   │   │   ├── UserFollowedEvent.ts
│   │   │   ├── CourseEnrolledEvent.ts
│   │   │   ├── ContentGeneratedEvent.ts   # Course Editor event
│   │   │   └── ReportSubmittedEvent.ts
│   │   │
│   │   └── /repositories                  # Repository Interfaces (Domain contracts)
│   │       ├── IUserRepository.ts
│   │       ├── IPostRepository.ts
│   │       ├── ICourseRepository.ts
│   │       └── IProjectRepository.ts      # Course Editor repository
│   │
│   ├── /infrastructure                    # 🔧 INFRASTRUCTURE LAYER
│   │   ├── /api                           # API Clients
│   │   │   ├── /clients
│   │   │   │   ├── content.client.ts      # Content API (courses, lessons)
│   │   │   │   ├── social.client.ts       # Social API (posts, likes)
│   │   │   │   ├── user.client.ts         # User API (auth, profile)
│   │   │   │   ├── courseEditor.client.ts # 📝 Course Editor API (chat, generate)
│   │   │   │   ├── admin.client.ts        # Admin API
│   │   │   │   ├── compliance.client.ts   # Compliance API
│   │   │   │   └── moderation.client.ts   # Moderation API
│   │   │   │
│   │   │   ├── http.ts                    # Base HTTP Client (Axios)
│   │   │   ├── interceptors.ts            # Auth Interceptors
│   │   │   └── api-error.ts               # API Error Handling
│   │   │
│   │   ├── /repositories                  # Repository Implementations
│   │   │   ├── UserRepository.ts          # User data access
│   │   │   ├── PostRepository.ts          # Post data access
│   │   │   ├── CourseRepository.ts        # Course data access
│   │   │   └── ProjectRepository.ts       # Course Editor project data access
│   │   │
│   │   ├── /websocket                     # WebSocket Integration
│   │   │   ├── websocket.client.ts        # WebSocket client
│   │   │   ├── events.ts                  # Event definitions
│   │   │   └── handlers.ts                # Event handlers
│   │   │
│   │   ├── /cache                         # Caching Layer
│   │   │   ├── cache.service.ts           # Cache abstraction
│   │   │   └── strategies.ts              # Cache strategies
│   │   │
│   │   ├── /i18n                          # Internationalization
│   │   │   ├── index.ts                   # i18n setup
│   │   │   └── /locales
│   │   │       ├── de.json
│   │   │       ├── en.json
│   │   │       └── pl.json
│   │   │
│   │   └── /persistence                   # Local Storage
│   │       ├── storage.service.ts         # Local storage abstraction
│   │       └── indexeddb.service.ts       # IndexedDB for offline
│   │
│   ├── /shared                            # 🔄 SHARED (Cross-Cutting)
│   │   ├── /types                         # Shared Type Definitions
│   │   │   ├── api.types.ts               # API Response types
│   │   │   ├── common.types.ts            # Common types
│   │   │   ├── courseEditor.types.ts      # Course Editor types
│   │   │   └── index.ts
│   │   │
│   │   ├── /constants                     # Shared Constants
│   │   │   ├── api.constants.ts           # API endpoints
│   │   │   ├── events.constants.ts        # Event names
│   │   │   ├── feature-flags.ts           # Feature flag names
│   │   │   └── errors.ts                  # Error codes
│   │   │
│   │   ├── /utils                         # Utility Functions
│   │   │   ├── date.utils.ts              # Date helpers
│   │   │   ├── format.utils.ts            # Formatting
│   │   │   ├── validation.utils.ts        # Validators
│   │   │   └── crypto.utils.ts            # Encryption
│   │   │
│   │   └── /guards                        # Type Guards
│   │       ├── user.guards.ts
│   │       └── post.guards.ts
│   │
│   ├── App.vue                            # Root Component
│   └── main.ts                            # Application Entry Point
│
├── /scripts                               # 🛠️ MIGRATION SCRIPTS
│   ├── /transforms
│   │   ├── update-imports.js              # jscodeshift: Update imports
│   │   └── add-deprecation-notices.js     # jscodeshift: Add deprecations
│   │
│   ├── migrate-domain.sh                  # Domain migration script
│   ├── generate-barrels.js                # Barrel generation
│   ├── validate-imports.js                # Import validation
│   └── compare-bundle-size.js             # Bundle size tracking
│
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

---

## 2. Lernmethoden & System Features - Services & Stores

### 📦 Learning Methods Services

Services für jede Lernmethoden-Gruppe:

```typescript
// src/application/services/learning-methods/

├── GroupAExplanationService.ts    # LM00-LM04 Services
│   ├── getTextExplanation()
│   ├── getVideoExplanation()
│   ├── getInteractiveExplanation()
│   └── getSystemFeaturesFor(lm: 'LM00'|'LM01'|...)
│       → ['whiteboard', 'ai-tutor', 'video-player', 'highlights']
│
├── GroupBPracticeService.ts        # LM05-LM08 Services
│   ├── getCodingPractice()
│   ├── getMathTasks()
│   ├── getInteractiveSim()
│   ├── getFlashcards()
│   └── getSystemFeaturesFor(lm: 'LM05'|'LM06'|...)
│       → ['code-sandbox', 'calculator', 'formula-editor', 'debugger', 'timer']
│
└── GroupCAssessmentService.ts     # LM09-LM11 Services
    ├── getExamSimulation()
    ├── getIHKExam()
    ├── getAdaptiveTest()
    └── getSystemFeaturesFor(lm: 'LM09'|'LM10'|...)
        → ['exam-engine', 'timer', 'proctoring']
```

### 🛠️ System Features Services

Services für jede Feature-Kategorie:

```typescript
// src/application/services/system-features/

├── AudioService.ts                 # Speech-to-Text, TTS
├── CollaborationService.ts         # LiveRoom, Whiteboard, Chat
├── ExamSystemService.ts            # ExamEngine, IHK-Format
├── GamificationService.ts          # XP, Badges, Quests
├── InteractiveToolsService.ts      # Calculator, FormulaEditor, GraphPlotter
├── ITEnvironmentService.ts         # CodeSandbox, VirtualLab, Debugger
├── MetaFeaturesService.ts          # Timer, Bookmarks, Notes
├── TutorService.ts                 # NPC-Tutor, AI-Tutor
├── VisualizationService.ts         # 3D-Graphs, Diagrams
└── LearningPathsService.ts         # Curriculum, Roadmap
```

### 🎯 Verkopplung im Service

**Beispiel: MathTasks (LM06)**

```typescript
// src/application/services/learning-methods/GroupBPracticeService.ts

export class GroupBPracticeService {
  async getMathTasks(courseId: string) {
    const lesson = await this.lessonRepo.findById(courseId)

    // Definiere welche System Features für Mathe nötig sind
    const requiredFeatures = this.getSystemFeaturesFor('LM06')
    // → ['calculator', 'formula-editor', 'graph-plotter', 'timer']

    // Lade die System Features
    const features = await Promise.all(
      requiredFeatures.map(f => this.systemFeaturesService.load(f))
    )

    return {
      lesson,
      systemFeatures: features,
      renderer: MathTasksRenderer
    }
  }

  private getSystemFeaturesFor(lm: string): string[] {
    const FEATURE_MAP = {
      'LM05': ['code-sandbox', 'debugger', 'timer'],
      'LM06': ['calculator', 'formula-editor', 'graph-plotter', 'timer'],
      'LM07': ['virtual-lab', 'simulation-engine'],
      'LM08': ['timer', 'flashcard-engine']
    }
    return FEATURE_MAP[lm] || []
  }
}
```

### 📦 Pinia Stores für Lernmethoden

```typescript
// src/application/stores/modules/learning-methods/

├── groupAExplanation.store.ts      # State für LM00-LM04
│   ├── currentLesson
│   ├── systemFeatures
│   └── activeToolkit
│
├── groupBPractice.store.ts         # State für LM05-LM08
│   ├── currentExercise
│   ├── userProgress
│   ├── systemFeatures
│   └── timer
│
└── groupCAssessment.store.ts       # State für LM09-LM11
    ├── currentExam
    ├── timeRemaining
    ├── systemFeatures
    └── results
```

---

## 2. Course Editor - Detailed Structure (Backend Aligned)

### 📝 Course Editor Architecture

```
/src/presentation/components/course-editor/

├── CourseEditorMain.vue              # Main container (router-view)
├── EditorSwitcher.vue                # Toggle: Manual ↔ AI Editor
│
├── /manual-editor/                   # 📝 MANUAL EDITOR (Traditional)
│   ├── ManualEditorContainer.vue     # Container für manual editing
│   ├── ContentEditor.vue             # Rich text editor (TipTap/Quill)
│   ├── StructurePanel.vue            # Course tree (chapters/lessons)
│   ├── ChapterEditor.vue             # Chapter CRUD
│   ├── LessonEditor.vue              # Lesson CRUD
│   ├── MediaUpload.vue               # Upload images/videos
│   ├── PreviewPanel.vue              # Live preview
│   └── ToolbarActions.vue            # Save/Publish/Draft buttons
│
└── /ai-editor/                       # 🤖 AI EDITOR (AI-assisted)
    ├── AIEditorContainer.vue         # Container für AI editing
    ├── ChatInterface.vue             # Chat with AI (like ChatGPT)
    ├── PromptBuilder.vue             # Structured prompt builder
    ├── ContentGenerator.vue          # Generate lessons/chapters
    ├── VariantSelector.vue           # Choose from multiple variants
    ├── TemplateLibrary.vue           # Pre-built templates
    ├── GenerationHistory.vue         # Previous generations
    ├── AISettings.vue                # Model selection, tone, style
    └── AIPreview.vue                 # Preview generated content
```

### 🔄 Backend-Frontend Alignment

```
BACKEND:
app/
├── api/
│   └── v1/
│       └── ai/                       # AI Editor APIs
│           ├── chat.py               → POST /api/v1/ai/chat
│           ├── generate.py           → POST /api/v1/ai/generate
│           ├── variants.py           → POST /api/v1/ai/variants
│           └── templates.py          → GET /api/v1/ai/templates
│
└── domain/
    └── ai/                           # AI Domain Logic
        ├── aicoursegenerator.py
        ├── chatengine.py
        └── variantmanager.py

FRONTEND:
/src/
├── presentation/
│   └── components/
│       └── course-editor/            # Course Editor Components
│           ├── /manual-editor/       # Manual editing
│           └── /ai-editor/           # AI editing
│               ├── ChatInterface.vue        → POST /api/v1/ai/chat
│               ├── ContentGenerator.vue     → POST /api/v1/ai/generate
│               ├── VariantSelector.vue      → POST /api/v1/ai/variants
│               └── TemplateLibrary.vue      → GET /api/v1/ai/templates
│
├── application/
│   └── services/
│       └── course-editor/            # Course Editor Services
│           ├── AIService.ts
│           └── ChatService.ts
│
└── domain/
    └── models/
        └── course-editor/            # Course Editor Domain
            ├── Project.model.ts
            └── ChatSession.model.ts

= PERFECT MATCH! ✅
```

---

## 3. Course Editor API Endpoints

### 🌐 Course Editor / AI Endpoints

| Endpoint | Method | Service | Store | Component | Description |
|----------|--------|---------|-------|-----------|-------------|
| `/api/v1/ai/chat` | POST | `ChatService` | `chat.store` | `ChatInterface.vue` | Chat with AI |
| `/api/v1/ai/generate` | POST | `AIService` | `aiEditor.store` | `ContentGenerator.vue` | Generate content |
| `/api/v1/ai/variants` | POST | `VariantService` | `aiEditor.store` | `VariantSelector.vue` | Create variants |
| `/api/v1/ai/templates` | GET | `TemplateService` | `templates.store` | `TemplateLibrary.vue` | List templates |
| `/api/v1/ai/projects` | GET | `EditorService` | `projects.store` | `ProjectsView.vue` | List projects |
| `/api/v1/ai/projects/:id` | GET | `EditorService` | `projects.store` | `CourseEditorMain.vue` | Get project |
| `/api/v1/ai/history` | GET | `EditorService` | `aiEditor.store` | `GenerationHistory.vue` | Generation history |
| `/api/v1/ai/sessions/:id` | GET | `ChatService` | `chat.store` | `ChatInterface.vue` | Get chat session |

### 📡 WebSocket Events (Course Editor)

```typescript
// src/shared/constants/events.constants.ts

export const WEBSOCKET_EVENTS = {
  // Course Editor / AI Events
  AI_MESSAGE_RECEIVED: 'ai:message_received',
  AI_GENERATION_STARTED: 'ai:generation_started',
  AI_GENERATION_COMPLETE: 'ai:generation_complete',
  AI_VARIANT_CREATED: 'ai:variant_created',
  AI_SESSION_UPDATED: 'ai:session_updated',
}
```

---

## 4. Course Editor Stores

### 📦 AI Editor Store

```typescript
// src/application/stores/modules/course-editor/aiEditor.store.ts

import { defineStore } from 'pinia'
import { AIService } from '@/application/services/course-editor/AIService'
import type { GeneratedContent, Variant } from '@/domain/models/course-editor'

export const useAIEditorStore = defineStore('aiEditor', {
  state: () => ({
    currentProject: null as Project | null,
    generatedContent: [] as GeneratedContent[],
    selectedVariant: null as Variant | null,
    isGenerating: false,
    error: null as string | null
  }),

  actions: {
    async generateContent(prompt: string, options: GenerateOptions) {
      this.isGenerating = true
      try {
        const service = new AIService()
        const content = await service.generateContent(prompt, options)
        this.generatedContent.push(content)
        return content
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.isGenerating = false
      }
    },

    async createVariants(contentId: string, count: number) {
      const service = new AIService()
      const variants = await service.createVariants(contentId, count)
      return variants
    }
  }
})
```

### 📦 Manual Editor Store

```typescript
// src/application/stores/modules/course-editor/manualEditor.store.ts

import { defineStore } from 'pinia'
import type { Course, Chapter, Lesson } from '@/domain/models/content'

export const useManualEditorStore = defineStore('manualEditor', {
  state: () => ({
    currentCourse: null as Course | null,
    activeChapter: null as Chapter | null,
    activeLesson: null as Lesson | null,
    isDirty: false,
    autoSaveEnabled: true,
    lastSaved: null as Date | null
  }),

  actions: {
    async saveContent() {
      const service = new CourseService()
      await service.updateCourse(this.currentCourse.id, this.currentCourse)
      this.isDirty = false
      this.lastSaved = new Date()
    }
  }
})
```

---

## 5. Course Editor Domain Models

### 🎯 Project Model

```typescript
// src/domain/models/course-editor/Project.model.ts

import { ProjectId } from '@/domain/value-objects/ProjectId.vo'

export class Project {
  private constructor(
    public readonly id: ProjectId,
    public readonly name: string,
    public readonly description: string,
    public readonly type: 'course' | 'lesson' | 'chapter',
    public readonly createdAt: Date,
    public readonly updatedAt: Date
  ) {
    Object.freeze(this)
  }

  static create(data: ProjectDTO): Project {
    return new Project(
      ProjectId.create(data.id),
      data.name,
      data.description,
      data.type,
      new Date(data.created_at),
      new Date(data.updated_at)
    )
  }
}
```

---

## 6. Component Examples

### 🎨 ChatInterface.vue

```vue
<!-- src/presentation/components/course-editor/ai-editor/ChatInterface.vue -->

<template>
  <div class="chat-interface">
    <div class="messages">
      <div 
        v-for="message in messages" 
        :key="message.id"
        :class="['message', message.role]"
      >
        <div class="avatar">
          {{ message.role === 'user' ? '👤' : '🤖' }}
        </div>
        <div class="content">
          {{ message.content }}
        </div>
      </div>
    </div>

    <div class="input-area">
      <textarea
        v-model="userInput"
        @keydown.enter.ctrl="sendMessage"
        placeholder="Beschreibe was du erstellen möchtest..."
      ></textarea>
      <button @click="sendMessage" :disabled="isGenerating">
        {{ isGenerating ? 'Generiert...' : 'Senden' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '@/application/stores/modules/course-editor/chat.store'
import { useAIEditorStore } from '@/application/stores/modules/course-editor/aiEditor.store'

const chatStore = useChatStore()
const aiEditorStore = useAIEditorStore()

const userInput = ref('')
const isGenerating = computed(() => aiEditorStore.isGenerating)
const messages = computed(() => chatStore.currentSession?.messages || [])

async function sendMessage() {
  if (!userInput.value.trim()) return
  await chatStore.sendMessage({
    role: 'user',
    content: userInput.value
  })
  userInput.value = ''
}
</script>
```

---

## 7. Course Editor Routes

**PRIMARY Course Editor Domain Route (for all roles with access):**

```typescript
// src/presentation/router/routes.ts

const routes = [
  {
    path: '/editor',                          // ✅ PRIMARY Course Editor Route
    component: () => import('@/presentation/layouts/EditorLayout.vue'),
    beforeEnter: [requireAuth, requireFeature('course-editor')],
    meta: {
      requiresAuth: true,
      requiresFeature: 'course-editor'
    },
    children: [
      {
        path: '',
        name: 'EditorDashboard',
        component: () => import('@/presentation/views/course-editor/ProjectsView.vue'),
        // Projects overview - access to Course Editor Domain
      },
      {
        path: 'course/:projectId?',
        name: 'CourseEditor',
        component: () => import('@/presentation/views/course-editor/EditorView.vue'),
        // Main Editor View - loads CourseEditorMain.vue
        // → EditorSwitcher.vue (Manual ↔ AI toggle)
        // → ManualEditorContainer OR AIEditorContainer
      },
      {
        path: 'templates',
        name: 'Templates',
        component: () => import('@/presentation/views/course-editor/TemplatesView.vue'),
        // Template Library - pre-built templates
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/presentation/views/course-editor/HistoryView.vue'),
        // Generation History - track AI generations
      }
    ]
  }
]
```

---

**Secondary Admin Route (Admin Panel access to Course Editor Domain):**

At `/admin/kurs-editor`, the Admin Panel provides System Admins with access to:
- Course approval workflows
- Course publication queue management
- Course analytics
- AI generation monitoring

**Both `/editor` and `/admin/kurs-editor` use the SAME Course Editor Domain Services:**
- EditorService (orchestration)
- AIService (AI generation)
- ChatService (AI chat)
- VariantService (content variants)
- TemplateService (template management)

---

## 8. Backward-Compatible Migration

### 📦 Re-Export Barrels

```typescript
// ❌ OLD LOCATION (deprecated): src/components/studio/
/**
 * @deprecated Import from @/presentation/components/course-editor instead
 * This re-export will be REMOVED on 2027-01-20 (12 months)
 */
export * from '@/presentation/components/course-editor'
```

```typescript
// ✅ NEW LOCATION: src/presentation/components/course-editor/
export { default as CourseEditorMain } from './CourseEditorMain.vue'
export { default as ManualEditorContainer } from './manual-editor/ManualEditorContainer.vue'
export { default as AIEditorContainer } from './ai-editor/AIEditorContainer.vue'
```

---

## 9. Migration Checklist

### ✅ Course Editor Domain Migration

```
Phase 1: Components (Week 1-2)
- [ ] Create /course-editor/ structure (root level!)
- [ ] Create /manual-editor/ components (8 components)
- [ ] Create /ai-editor/ components (9 components)
- [ ] Generate backward-compatible barrels
- [ ] Remove old /studio/ references

Phase 2: Application Layer (Week 2-3)
- [ ] Create editor.store.ts
- [ ] Create aiEditor.store.ts
- [ ] Create manualEditor.store.ts
- [ ] Create chat.store.ts
- [ ] Create projects.store.ts
- [ ] Create EditorService.ts
- [ ] Create AIService.ts

Phase 3: Domain Layer (Week 3)
- [ ] Create Project.model.ts
- [ ] Create ChatSession.model.ts
- [ ] Create GeneratedContent.model.ts
- [ ] Create Project.factory.ts

Phase 4: Infrastructure (Week 3-4)
- [ ] Create courseEditor.client.ts (API calls to /api/v1/ai/*)
- [ ] Create ProjectRepository.ts
- [ ] Add WebSocket events (5 events)
- [ ] Update routes (/editor/*)

Phase 5: Testing (Week 4)
- [ ] Unit tests (Domain models)
- [ ] Integration tests (Services)
- [ ] Component tests (Vue)
- [ ] E2E tests (Editor workflows)
```

---

## 10. Zusammenfassung

### ✅ Course Editor Structure (v4.0.2 - FINAL)

| Aspekt | Beschreibung |
|--------|-------------|
| **Structure** | `/course-editor/` direkt als Domain (KEIN /studio/ parent!) |
| **Backend Aligned** | ✅ Matched Backend: app/api/v1/ai/ + app/domain/ai/ |
| **Components** | 18 Components (8 manual + 9 AI + main/switcher) |
| **Stores** | 6 Stores (editor, aiEditor, manualEditor, chat, projects, templates) |
| **Services** | 5 Services (EditorService, AIService, ChatService, etc.) |
| **API Endpoints** | 8 Endpoints (/api/v1/ai/chat, /generate, /variants, etc.) |
| **WebSocket Events** | 5 Events (ai:message_received, ai:generation_complete, etc.) |
| **Domain Models** | 5 Models (Project, ChatSession, GeneratedContent, Variant, Template) |

### 💪 Key Differences vs Previous Versions

```
v4.0 (WRONG):
/presentation/components/studio/
└── /editor/              ❌ Generic "studio" parent

v4.0.1 (WRONG):
/presentation/components/studio/
└── /course-editor/       ❌ Still has "studio" parent

v4.0.2 (CORRECT):
/presentation/components/course-editor/   ✅ Direct as domain!
├── /manual-editor/
└── /ai-editor/

= NO "studio" parent folder! Course Editor ist eigenständige Domain!
```

### 🎯 Backend Alignment Proof

```
BACKEND:
app/domain/ai/              → AI Domain Logic
app/api/v1/ai/              → AI API Endpoints

FRONTEND:
domain/models/course-editor/       → Course Editor Domain Models
application/services/course-editor/ → Course Editor Services
infrastructure/api/clients/courseEditor.client.ts → API Client
presentation/components/course-editor/ → UI Components

= SAME STRUCTURE! ✅
```

---

## 11. Admin Panel Architecture

### 📊 Admin Panel Overview

Das **Admin Panel** ist eine **UNIFIED System Administration Interface** unter `/admin` für System Admins. Es ist NICHT teilbar in separate Org Admin oder User Admin Panels.

**Key Points:**
- ✅ **Single Entry Point**: `/admin` für ALL Admin Features
- ✅ **Role-Based Access**: `requiresSystemAdmin` meta guard on all routes
- ✅ **12 Main Sections**: Users, Roles, Organisations, Courses, Categories, AI Studio, Translations, Billing, Analytics, Audit Logs, LM Routing, System Settings
- ✅ **Backend Aligned**: Mirrors Backend API structure (`/api/v1/admin-panel/*`)
- ❌ **NO Separate `/org` Panel**: Organisation features go through `/admin/organisations`

---

⚠️ **IMPORTANT: Course Editor is a SHARED Domain Component**

**The Course Editor is NOT an Admin-only feature!**

- 📝 **Defined in Section 2** as a separate SHARED Domain component (`/presentation/components/course-editor/`)
- 🎯 **Primary Route**: `/editor` - for creators/users with `course-editor` feature flag
- 🔐 **Admin Route**: `/admin/kurs-editor` - System Admin access point to the same domain
- 🔄 **Same Domain Services**: Both routes access the same Course Editor Services (EditorService, AIService, ChatService, etc.)

**In other words:** The Admin Panel **CONSUMES** the Course Editor Domain but does NOT **DEFINE** it. The Course Editor is documented as a reusable, multi-role domain component.

#### 🎯 Phase 6 Admin Panel Unification (21.01.2026)

**Cleanup & Formalization Completed:**

Die folgende Arbeit wurde durchgeführt, um das Admin Panel zu formalisieren und zu konsolidieren:

**Gelöschte Dateien (12 total):**
- **5 Orphaned Org Admin Pages**: OrgDashboardPage, OrgAnalyticsPage, OrgSettingsPage, OrgCoursesPage, OrgUsersPage (keine Router-Pfade, keine Imports)
- **2 Orphaned Org Admin Stores**: orgAdmin.store.ts (barrel), orgAdmin.store.ts (implementation)
- **2 Orphaned Org Admin APIs**: legacy orgAdmin.api.ts files (beide Strukturen)
- **3 Duplicate OrgOverviewWidget Copies**: Aus verschiedenen Ordnern (nur 1 Kopie in Phase 6 Struktur behalten)

**Aktualisierte Dateien:**
- **AdminLayout.vue**: Entfernt `isOrgAdmin` prop und `/org` Pfad-Referenzen
- **admin/index.ts**: Barrel-Export für orgAdmin.store entfernt

**Verifizierter Status:**
- ✅ Keine verbleibenden `/org/` Pfade in aktivem Code
- ✅ Alle 17 Admin Pages unter `/admin` aktiv und funktionsfähig
- ✅ Organisations API (`/organisations`) korrekt unter `/admin` integriert
- ✅ OrgOverviewWidget konsolidiert in Phase 6 Struktur
- ✅ Backup-Risiko eliminiert
- ✅ Einheitliche Admin Panel Struktur etabliert

### 🗂️ Admin Panel Folder Structure (100+ Components)

```
/src/presentation/
├── /layouts
│   └── AdminLayout.vue                   # 🎨 Admin Panel Master Layout (Sidebar + Top Bar)
│       ├── Sidebar (12 menu items)
│       ├── Top bar (page title + actions)
│       └── Main content area (router-view)
│
├── /components
│   └── /admin/                           # Admin Domain Components (100+ components)
│       │
│       ├── /dashboard                    # 📊 Dashboard Section
│       │   ├── AdminDashboard.vue        # Main admin dashboard
│       │   ├── StatsCard.vue             # Statistics display
│       │   ├── ActivityLog.vue           # Recent activities
│       │   ├── SystemHealth.vue          # System status
│       │   └── QuickActions.vue          # Quick action buttons
│       │
│       ├── /users                        # 👥 User Management
│       │   ├── UserList.vue              # List all users
│       │   ├── UserDetail.vue            # View/edit single user
│       │   ├── UserForm.vue              # User creation/editing form
│       │   ├── BulkActions.vue           # Bulk operations
│       │   ├── RoleAssignment.vue        # Assign roles to users
│       │   └── UserSearch.vue            # Advanced search
│       │
│       ├── /groups                       # 👥 Group Management (GBA)
│       │   ├── GroupsManagement.vue      # Main groups interface
│       │   ├── GroupList.vue             # List all groups
│       │   ├── GroupDetail.vue           # View/edit group
│       │   ├── GroupMembers.vue          # Manage group members
│       │   ├── GroupPermissions.vue      # Permission assignment
│       │   ├── GroupForm.vue             # Create/edit group
│       │   └── GroupTemplate.vue         # Pre-defined group templates
│       │
│       ├── /organisations                # 🏢 Organisation Management
│       │   ├── OrgList.vue               # List organisations
│       │   ├── OrgDetail.vue             # Organisation details
│       │   ├── OrgSettings.vue           # Organisation settings
│       │   ├── OrgUsers.vue              # Users in organisation
│       │   ├── OrgAnalytics.vue          # Organisation analytics
│       │   ├── OrgForm.vue               # Create/edit organisation
│       │   └── OrgSubscription.vue       # Subscription management
│       │
│       ├── /courses                      # 📚 Course Management (kurs-editor)
│       │   │                              # ⚠️ Admin access to Course Editor Domain
│       │   │                              # (See Section 2: Shared Domain)
│       │   ├── CourseList.vue            # List all courses
│       │   ├── CourseDetail.vue          # Course details
│       │   ├── CourseApproval.vue        # Approve/reject courses
│       │   ├── PublicationQueue.vue      # Publishing workflow
│       │   ├── CourseSearch.vue          # Advanced search
│       │   └── BulkCourseActions.vue     # Bulk operations
│       │
│       ├── /categories                   # 📁 Category Management
│       │   ├── CategoryTree.vue          # Hierarchical view
│       │   ├── CategoryForm.vue          # Create/edit category
│       │   ├── CategoryReorder.vue       # Drag-to-reorder
│       │   └── CategoryMapping.vue       # Map courses to categories
│       │
│       ├── /ai-studio                    # 🤖 AI Management
│       │   ├── AIStudioMain.vue          # Main AI studio interface
│       │   ├── ModelManagement.vue       # AI model selection
│       │   ├── ProviderSettings.vue      # LLM provider configuration
│       │   ├── APIKeyManager.vue         # API key management
│       │   ├── PricingManager.vue        # Token pricing
│       │   ├── JobMonitor.vue            # Monitor AI jobs
│       │   ├── PromptLibrary.vue         # Manage prompts
│       │   └── CostAnalytics.vue         # AI cost tracking
│       │
│       ├── /translations                 # 🌐 i18n Management
│       │   ├── TranslationDashboard.vue  # Translation status
│       │   ├── LanguageManager.vue       # Manage languages
│       │   ├── StringEditor.vue          # Edit translation strings
│       │   ├── ExportImport.vue          # Import/export translations
│       │   ├── SyncStatus.vue            # Sync with backend
│       │   └── MissingTranslations.vue   # Find gaps
│       │
│       ├── /billing                      # 💰 Billing Management
│       │   ├── SubscriptionList.vue      # Active subscriptions
│       │   ├── TransactionLog.vue        # Payment history
│       │   ├── InvoiceManager.vue        # Invoice management
│       │   ├── PaymentMethods.vue        # Payment configuration
│       │   ├── TokenPricing.vue          # Token cost settings
│       │   └── RevenueAnalytics.vue      # Revenue tracking
│       │
│       ├── /analytics                    # 📈 Analytics & Reporting
│       │   ├── AnalyticsDashboard.vue    # Main analytics view
│       │   ├── UserMetrics.vue           # User statistics
│       │   ├── CourseMetrics.vue         # Course statistics
│       │   ├── EngagementChart.vue       # Engagement tracking
│       │   ├── RevenueChart.vue          # Revenue tracking
│       │   ├── CustomReports.vue         # Create custom reports
│       │   └── ExportData.vue            # Export analytics
│       │
│       ├── /audit-logs                   # 📋 Audit & Compliance
│       │   ├── AuditLogList.vue          # View audit logs
│       │   ├── AuditLogFilter.vue        # Advanced filtering
│       │   ├── LogDetails.vue            # Log entry details
│       │   ├── ExportAuditLog.vue        # Export for compliance
│       │   └── AuditDashboard.vue        # Summary statistics
│       │
│       ├── /lm-routing                   # 🎓 Learning Method Routing
│       │   ├── RoutingDashboard.vue      # Routing overview
│       │   ├── MethodRouting.vue         # Configure LM routing
│       │   ├── GroupRouting.vue          # Route by LM group (A/B/C)
│       │   └── RoutingRules.vue          # Conditional routing
│       │
│       └── /system-settings              # ⚙️ System Configuration
│           ├── SettingsDashboard.vue     # Settings overview
│           ├── GeneralSettings.vue       # App name, logo, etc.
│           ├── SecuritySettings.vue      # HTTPS, CORS, headers
│           ├── PerformanceSettings.vue   # Cache, rate limits
│           ├── FeatureFlags.vue          # Feature toggle
│           ├── MaintenanceMode.vue       # Maintenance controls
│           ├── BackupSettings.vue        # Backup configuration
│           └── ApiSettings.vue           # API configuration
│
└── /views
    └── /admin
        ├── AdminDashboardPage.vue        # Dashboard page
        ├── AdminUsersPage.vue            # Users management page
        ├── AdminGroupsPage.vue           # Groups management page (GBA)
        ├── AdminOrganisationsPage.vue    # Organisations page
        ├── AdminCoursesPage.vue          # Course management page
        ├── AdminCategoriesPage.vue       # Categories page
        ├── AdminKIStudioPage.vue         # AI Studio page
        ├── AdminTranslationsPage.vue     # Translations page
        ├── AdminBillingPage.vue          # Billing page
        ├── AdminAnalyticsPage.vue        # Analytics page
        ├── AdminAuditLogsPage.vue        # Audit logs page
        ├── AdminLMRoutingPage.vue        # LM Routing page
        └── AdminSystemSettingsPage.vue   # System settings page
```

### 👥 Group-Based Access Control

**Admin Panel Routes with Guards:**

```typescript
// src/presentation/router/index.ts

{
  path: '/admin',
  component: () => import('@/presentation/layouts/AdminLayout.vue'),
  meta: {
    requiresAuth: true,
    requiresSystemAdmin: true  // ⚡ CRITICAL: Only System Admins!
  },
  children: [
    {
      path: '',
      name: 'AdminDashboard',
      component: () => import('@/presentation/pages/admin/AdminDashboardPage.vue'),
    },
    {
      path: 'users',
      name: 'AdminUsers',
      component: () => import('@/presentation/pages/admin/AdminUsersPage.vue'),
    },
    {
      path: 'users/:userId',
      name: 'AdminUserDetail',
      component: () => import('@/presentation/pages/admin/AdminUserDetailPage.vue'),
    },
    {
      path: 'roles',
      name: 'AdminRoles',
      component: () => import('@/presentation/pages/admin/AdminRolesPage.vue'),
    },
    {
      path: 'organisations',
      name: 'AdminOrganisations',
      component: () => import('@/presentation/pages/admin/AdminOrganisationsPage.vue'),
    },
    {
      path: 'kurs-editor',
      name: 'AdminCourseEditor',
      component: () => import('@/presentation/pages/admin/AdminCoursesPage.vue'),
    },
    {
      path: 'categories',
      name: 'AdminCategories',
      component: () => import('@/presentation/pages/admin/AdminCategoriesPage.vue'),
    },
    {
      path: 'ai-studio',
      name: 'AdminAIStudio',
      component: () => import('@/presentation/pages/admin/AdminKIStudioPage.vue'),
    },
    {
      path: 'translations',
      name: 'AdminTranslations',
      component: () => import('@/presentation/pages/admin/AdminTranslationsPage.vue'),
    },
    {
      path: 'billing',
      name: 'AdminBilling',
      component: () => import('@/presentation/pages/admin/AdminBillingPage.vue'),
    },
    {
      path: 'analytics',
      name: 'AdminAnalytics',
      component: () => import('@/presentation/pages/admin/AdminAnalyticsPage.vue'),
    },
    {
      path: 'audit-logs',
      name: 'AdminAuditLogs',
      component: () => import('@/presentation/pages/admin/AdminAuditLogsPage.vue'),
    },
    {
      path: 'lm-routing',
      name: 'AdminLMRouting',
      component: () => import('@/presentation/pages/admin/AdminLMRoutingPage.vue'),
    },
    {
      path: 'system-settings',
      name: 'AdminSystemSettings',
      component: () => import('@/presentation/pages/admin/AdminSystemSettingsPage.vue'),
    },
  ],
}
```

**Navigation Guard (beforeEach):**

```typescript
// Check System Admin access
if (to.meta.requiresSystemAdmin && !authStore.isSystemAdmin) {
  console.warn('Access denied: System Admin required')
  next({ name: 'Dashboard' })
  return
}
```

### 🏗️ Admin Panel Services & Stores (12 Each)

**Admin Panel Services (12 x Domain-Specific):**

```typescript
// src/application/services/admin/

├── UserAdminService.ts         # User CRUD + role assignment
├── RoleAdminService.ts         # Role CRUD + permissions
├── OrganisationService.ts       # Organisation management
├── CourseAdminService.ts        # Course approval workflow
├── CategoryService.ts           # Category hierarchy
├── AIStudioService.ts           # AI model/provider management
├── TranslationService.ts        # i18n management
├── BillingService.ts            # Billing & subscriptions
├── AnalyticsService.ts          # Reporting & metrics
├── AuditLogService.ts           # Compliance logging
├── LMRoutingService.ts          # Learning method routing
└── SystemSettingsService.ts     # System configuration
```

**Admin Panel State Stores (12 x Pinia):**

```typescript
// src/application/stores/modules/admin/ (12 stores für Admin Panel)

├── adminDashboard.store.ts      # Dashboard state
├── users.store.ts               # Users management state
├── roles.store.ts               # Roles management state
├── organisations.store.ts        # Organisations state
├── courses.store.ts             # Course management state
├── categories.store.ts          # Categories state
├── aiStudio.store.ts            # AI Studio state
├── translations.store.ts         # i18n state
├── billing.store.ts             # Billing state
├── analytics.store.ts           # Analytics state
├── auditLogs.store.ts           # Audit logs state
├── lmRouting.store.ts           # LM Routing state
└── systemSettings.store.ts       # System settings state
```

### 📡 Admin API Endpoints

**Backend Admin Panel Endpoints** (via `/api/v1/admin-panel/*`):

| Section | Endpoints | Method | Purpose |
|---------|-----------|--------|---------|
| **Users** | `/admin-panel/users` | GET/POST | List/create users |
| | `/admin-panel/users/:id` | GET/PUT/DELETE | User details |
| **Groups** | `/admin-panel/groups` | GET/POST | List/create groups |
| | `/admin-panel/groups/:id/permissions` | PUT | Update group permissions |
| **Organisations** | `/admin-panel/organisations` | GET/POST | Org management |
| | `/admin-panel/organisations/:id` | GET/PUT/DELETE | Org details |
| **Courses** | `/admin-panel/courses` | GET | List all courses |
| | `/admin-panel/courses/:id/approve` | POST | Approve course |
| **Categories** | `/admin-panel/categories` | GET/POST | Category hierarchy |
| **AI** | `/admin-panel/ai/models` | GET | List AI models |
| | `/admin-panel/ai/providers` | PUT | Update providers |
| | `/admin-panel/ai/pricing` | PUT | Set pricing |
| **Analytics** | `/admin-panel/analytics/users` | GET | User metrics |
| | `/admin-panel/analytics/courses` | GET | Course metrics |
| **Audit Logs** | `/admin-panel/audit-logs` | GET | View logs |

### 🔌 Admin Layout Component

**AdminLayout.vue** - Manages sidebar, navigation, and layout:

```vue
<!-- src/presentation/layouts/AdminLayout.vue -->

<template>
  <div class="admin-layout flex h-screen overflow-hidden bg-[var(--color-bg)]">
    <!-- Sidebar with 12 menu items -->
    <aside class="w-72 bg-[var(--color-surface)] border-r border-[var(--color-border)] flex flex-col">
      <div class="p-5 border-b border-[var(--color-border)]">
        <router-link to="/dashboard" class="flex items-center gap-3">
          <span class="text-3xl">🎓</span>
          <div>
            <h1 class="text-lg font-bold">LSX</h1>
            <p class="text-sm">{{ sidebarTitle }}</p>
          </div>
        </router-link>
      </div>

      <!-- Navigation with 12 menu items -->
      <nav class="flex-1 overflow-y-auto p-5">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :class="{ 'active': isActive(item.path) }"
          class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-base font-medium transition-colors"
        >
          <span class="text-xl">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- User section -->
      <div class="p-5 border-t border-[var(--color-border)]">
        <div class="flex items-center gap-3.5 mb-4">
          <div class="w-11 h-11 bg-primary-100 rounded-full flex items-center justify-center">
            <span class="text-primary-700 font-semibold">{{ userInitials }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-base font-medium truncate">{{ authStore.fullName }}</p>
            <p class="text-sm text-secondary">{{ authStore.userRole }}</p>
          </div>
        </div>

        <button @click="handleLogout" class="w-full px-4 py-2.5 text-red-700 hover:bg-red-50 rounded-lg">
          {{ t('auth.logout') }}
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col overflow-hidden min-h-0">
      <!-- Top Bar with page title -->
      <header class="flex-shrink-0 bg-[var(--color-surface)] border-b border-[var(--color-border)] px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-bold">{{ pageTitle }}</h2>
            <p v-if="pageSubtitle" class="text-sm text-secondary">{{ pageSubtitle }}</p>
          </div>

          <div class="flex items-center gap-4">
            <LanguageSelector :show-label="false" />
            <slot name="header-actions"></slot>
          </div>
        </div>
      </header>

      <!-- Page Content with DesktopLayer -->
      <div class="flex-1 relative">
        <div class="absolute inset-0 overflow-hidden">
          <DesktopLayer>
            <div class="p-2">
              <router-view></router-view>
            </div>
          </DesktopLayer>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/application/stores/auth.store'
import { DesktopLayer } from '@/presentation/components/layout'
import { LanguageSelector } from '@/presentation/components/layout/i18n'

const router = useRouter()
const route = useRoute()
const { t, locale } = useI18n()
const authStore = useAuthStore()

// 12 Admin menu items
const menuItems = computed(() => [
  { path: '/admin', label: t('admin.nav.dashboard'), icon: '📊' },
  { path: '/admin/users', label: t('admin.nav.users'), icon: '👥' },
  { path: '/admin/groups', label: t('admin.nav.groups'), icon: '👫' },
  { path: '/admin/organisations', label: t('admin.nav.organisations'), icon: '🏢' },
  { path: '/admin/kurs-editor', label: t('admin.nav.courseEditor'), icon: '📝' },
  { path: '/admin/categories', label: t('admin.nav.categories'), icon: '📁' },
  { path: '/admin/ai-studio', label: t('admin.nav.aiStudio'), icon: '🤖' },
  { path: '/admin/translations', label: t('admin.nav.translations'), icon: '🌐' },
  { path: '/admin/billing', label: t('admin.nav.billing'), icon: '💰' },
  { path: '/admin/analytics', label: t('admin.nav.analytics'), icon: '📈' },
  { path: '/admin/audit-logs', label: t('admin.nav.audit_logs'), icon: '📋' },
  { path: '/admin/system-settings', label: t('admin.nav.settings'), icon: '⚙️' }
])

const sidebarTitle = computed(() => {
  void locale.value // Trigger reactivity on language change
  return t('admin.system_admin')
})

const userInitials = computed(() => {
  const firstName = authStore.user?.first_name || ''
  const lastName = authStore.user?.last_name || ''
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
})

const isActive = (path: string): boolean => {
  return route.path === path || route.path.startsWith(path + '/')
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
```

### 💡 Example: User Management Page

```vue
<!-- src/presentation/pages/admin/AdminUsersPage.vue -->

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/application/stores/modules/admin/users.store'
import { UserAdminService } from '@/application/services/admin/UserAdminService'

const adminStore = useAdminStore()
const service = new UserAdminService()

const users = computed(() => adminStore.users)
const isLoading = computed(() => adminStore.isLoading)
const selectedUser = ref(null)

onMounted(async () => {
  await adminStore.fetchUsers()
})

const handleAddUser = async (userData) => {
  await adminStore.createUser(userData)
}

const handleUpdateUser = async (userId, updates) => {
  await adminStore.updateUser(userId, updates)
}

const handleDeleteUser = async (userId) => {
  await adminStore.deleteUser(userId)
}
</script>

<template>
  <div class="admin-users-page">
    <div class="flex justify-between items-center mb-6">
      <h1>{{ $t('admin.users.title') }}</h1>
      <button @click="selectedUser = {}" class="btn btn-primary">
        {{ $t('admin.users.add_user') }}
      </button>
    </div>

    <div v-if="isLoading" class="loader">{{ $t('common.loading') }}</div>

    <table v-else class="users-table">
      <thead>
        <tr>
          <th>{{ $t('admin.users.name') }}</th>
          <th>{{ $t('admin.users.email') }}</th>
          <th>{{ $t('admin.users.role') }}</th>
          <th>{{ $t('admin.users.status') }}</th>
          <th>{{ $t('common.actions') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.name }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.role }}</td>
          <td :class="`status-${user.status}`">{{ user.status }}</td>
          <td>
            <button @click="selectedUser = user" class="btn btn-sm">Edit</button>
            <button @click="handleDeleteUser(user.id)" class="btn btn-sm btn-danger">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

### ✅ Admin Panel Structure Summary

| Aspect | Details |
|--------|---------|
| **Location** | `/admin` (single unified entry point) |
| **Layout** | AdminLayout.vue with sidebar + top bar |
| **Menu Items** | 12 sections (Users, Roles, Organisations, etc.) |
| **Access Control** | `requiresSystemAdmin` meta guard on all routes |
| **Components** | 100+ admin components organized by section |
| **Services** | 12 admin services (one per section) |
| **Stores** | 12 Pinia stores for state management |
| **API Client** | admin.client.ts (calls `/api/v1/admin-panel/*`) |
| **Pages** | 13 admin pages (one per route) |
| **Backend Alignment** | ✅ Matches Backend Admin Panel structure |

### ⚠️ Important: NO Separate Org Admin Panel

**Previous Design (WRONG - NOW REMOVED):**
```
/admin/         ← System Admin
/org/           ← Org Admin (DUPLICATE - REMOVED!)
```

**Current Design (CORRECT):**
```
/admin/
├── /organisations      ← All org management here
├── /users             ← All user management here
└── ... (all features centralized)
```

**Why removed:**
- Avoids duplicate code and confusion
- Org features are managed through `/admin/organisations`
- Simpler mental model for developers
- Cleaner backup and database structure

---

**END OF DOCUMENT**

Version 4.0.4 - Admin Panel Unified Architecture (COMPLETE)
Stand: 21.01.2026
