# 16 – Frontend-Struktur (DDD Architecture)

**Version:** 4.0.2 (DDD Migration - Course Editor Fix)
**Stand:** 20.01.2026
**Änderungen:** Course Editor direkt als Domain (kein Studio parent) - Aligned mit Backend

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
│   │   │   ├── /learning                  # Learning Domain Components
│   │   │   │   ├── FlashcardPlayer.vue
│   │   │   │   ├── QuizEngine.vue
│   │   │   │   └── ProgressTracker.vue
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

```typescript
// src/presentation/router/routes.ts

const routes = [
  {
    path: '/editor',
    component: () => import('@/presentation/layouts/EditorLayout.vue'),
    beforeEnter: [requireAuth, requireFeature('course-editor')],
    children: [
      {
        path: '',
        name: 'EditorDashboard',
        component: () => import('@/presentation/views/course-editor/ProjectsView.vue'),
      },
      {
        path: 'course/:projectId?',
        name: 'CourseEditor',
        component: () => import('@/presentation/views/course-editor/EditorView.vue'),
        // Loads: CourseEditorMain.vue → EditorSwitcher.vue → Manual/AI Editor
      },
      {
        path: 'templates',
        name: 'Templates',
        component: () => import('@/presentation/views/course-editor/TemplatesView.vue'),
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/presentation/views/course-editor/HistoryView.vue'),
      }
    ]
  }
]
```

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

**END OF DOCUMENT**

Version 4.0.2 - DDD Architecture (Course Editor FINAL)
Stand: 20.01.2026
