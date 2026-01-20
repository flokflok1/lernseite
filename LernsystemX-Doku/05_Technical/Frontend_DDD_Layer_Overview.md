# Frontend DDD Architecture - Layer Overview

**Version:** 4.0.2 - DDD Architecture
**Stand:** 20.01.2026

---

## 🎯 Frontend 4-Layer DDD Structure (mit Emojis)

```
/src/
├── presentation/           🔴 UI Layer (components, views, layouts, router)
├── application/            🟡 Application Services (services, stores, composables, use-cases)
├── domain/                 🟢 Business Logic (models, value-objects, factories, events, repositories)
├── infrastructure/         🔵 Technical Services (api, websocket, cache, i18n, persistence)
└── shared/                 ⚪ Cross-Cutting (types, constants, utils, guards)
```

---

## 📁 Komplette Verzeichnisstruktur (Detailed)

```
/frontend
│
├── /public
│   ├── favicon.ico
│   └── /assets
│       ├── /images
│       ├── /icons
│       └── /legal
│
├── /src
│   │
│   ├── /presentation                    🔴 UI LAYER
│   │   │
│   │   ├── /components                  # UI Components
│   │   │   ├── /shared                  # Shared UI
│   │   │   │   ├── /ui                  # Button, Input, Modal
│   │   │   │   ├── /layout              # Header, Sidebar, Footer
│   │   │   │   └── /forms               # FormInput, FormSelect
│   │   │   │
│   │   │   ├── /content                 # Content Domain Components
│   │   │   ├── /learning                # Learning Domain Components
│   │   │   ├── /social                  # Social Domain Components
│   │   │   ├── /user                    # User Domain Components
│   │   │   ├── /admin                   # Admin Domain Components
│   │   │   ├── /compliance              # Compliance Domain Components
│   │   │   ├── /moderation              # Moderation Domain Components
│   │   │   ├── /security                # Security Domain Components
│   │   │   └── /course-editor           # Course Editor Domain
│   │   │       ├── CourseEditorMain.vue
│   │   │       ├── EditorSwitcher.vue
│   │   │       ├── /manual-editor       # Manual editing (8 components)
│   │   │       └── /ai-editor           # AI editing (9 components)
│   │   │
│   │   ├── /views                       # Pages/Views
│   │   │   ├── /auth                    # Login, Register
│   │   │   ├── /dashboard               # Dashboard
│   │   │   ├── /social                  # Feed, Profile
│   │   │   ├── /content                 # Courses, Lessons
│   │   │   ├── /course-editor           # Course Editor Views
│   │   │   └── /admin                   # Admin Panel
│   │   │
│   │   ├── /layouts                     # Layouts
│   │   │   ├── MainLayout.vue
│   │   │   ├── AuthLayout.vue
│   │   │   ├── DashboardLayout.vue
│   │   │   ├── AdminLayout.vue
│   │   │   └── EditorLayout.vue
│   │   │
│   │   └── /router                      # Router Configuration
│   │       ├── index.ts
│   │       ├── routes.ts
│   │       ├── guards.ts
│   │       └── middleware.ts
│   │
│   ├── /application                     🟡 APPLICATION LAYER
│   │   │
│   │   ├── /services                    # Business Logic Services
│   │   │   ├── /content                 # CourseService, LessonService
│   │   │   ├── /social                  # PostService, CommentService
│   │   │   ├── /user                    # AuthService, ProfileService
│   │   │   ├── /course-editor           # EditorService, AIService, ChatService
│   │   │   ├── /admin                   # UserAdminService, FeatureFlagService
│   │   │   ├── /compliance              # ConsentService, PrivacyService
│   │   │   └── /moderation              # ReportService, ModerationService
│   │   │
│   │   ├── /stores                      # Pinia Stores (State Management)
│   │   │   ├── /modules
│   │   │   │   ├── /content             # courseViewer.store, courseLibrary.store
│   │   │   │   ├── /course-editor       # editor.store, aiEditor.store, manualEditor.store
│   │   │   │   ├── /social              # feed.store, social.store
│   │   │   │   ├── /user                # auth.store, profile.store
│   │   │   │   └── /core                # ui.store, workspace.store
│   │   │   └── index.ts
│   │   │
│   │   ├── /composables                 # Vue Composables
│   │   │   ├── useAuth.ts
│   │   │   ├── useSocial.ts
│   │   │   ├── useContent.ts
│   │   │   ├── useCourseEditor.ts
│   │   │   ├── useAIEditor.ts
│   │   │   ├── useFeatureFlags.ts
│   │   │   └── usePagination.ts
│   │   │
│   │   └── /use-cases                   # Application Use Cases
│   │       ├── CreatePostUseCase.ts
│   │       ├── EnrollCourseUseCase.ts
│   │       ├── GenerateContentUseCase.ts
│   │       └── SubmitReportUseCase.ts
│   │
│   ├── /domain                          🟢 DOMAIN LAYER
│   │   │
│   │   ├── /models                      # Domain Models (Aggregate Roots)
│   │   │   ├── /content                 # Course.model, Chapter.model, Lesson.model
│   │   │   ├── /course-editor           # Project.model, ChatSession.model, GeneratedContent.model
│   │   │   ├── /social                  # Post.model, Comment.model, Like.model
│   │   │   ├── /user                    # User.model, Profile.model, Session.model
│   │   │   ├── /compliance              # Consent.model, Report.model
│   │   │   └── /moderation              # ContentReport.model, ModerationAction.model
│   │   │
│   │   ├── /value-objects               # Value Objects (Immutable)
│   │   │   ├── Email.vo.ts
│   │   │   ├── UserId.vo.ts
│   │   │   ├── PostId.vo.ts
│   │   │   ├── CourseId.vo.ts
│   │   │   ├── ProjectId.vo.ts
│   │   │   └── Timestamp.vo.ts
│   │   │
│   │   ├── /factories                   # Factory Pattern
│   │   │   ├── /content                 # Course.factory
│   │   │   ├── /course-editor           # Project.factory, ChatSession.factory
│   │   │   ├── /social                  # Post.factory, Comment.factory
│   │   │   └── /user                    # User.factory
│   │   │
│   │   ├── /events                      # Domain Events
│   │   │   ├── PostCreatedEvent.ts
│   │   │   ├── UserFollowedEvent.ts
│   │   │   ├── CourseEnrolledEvent.ts
│   │   │   ├── ContentGeneratedEvent.ts
│   │   │   └── ReportSubmittedEvent.ts
│   │   │
│   │   └── /repositories                # Repository Interfaces (Domain contracts)
│   │       ├── IUserRepository.ts
│   │       ├── IPostRepository.ts
│   │       ├── ICourseRepository.ts
│   │       └── IProjectRepository.ts
│   │
│   ├── /infrastructure                  🔵 INFRASTRUCTURE LAYER
│   │   │
│   │   ├── /api                         # API Clients
│   │   │   ├── /clients
│   │   │   │   ├── content.client.ts    # Content API
│   │   │   │   ├── social.client.ts     # Social API
│   │   │   │   ├── user.client.ts       # User API
│   │   │   │   ├── courseEditor.client.ts # Course Editor API
│   │   │   │   ├── admin.client.ts      # Admin API
│   │   │   │   ├── compliance.client.ts # Compliance API
│   │   │   │   └── moderation.client.ts # Moderation API
│   │   │   ├── http.ts                  # Base HTTP Client (Axios)
│   │   │   ├── interceptors.ts          # Auth Interceptors
│   │   │   └── api-error.ts             # API Error Handling
│   │   │
│   │   ├── /repositories                # Repository Implementations
│   │   │   ├── UserRepository.ts
│   │   │   ├── PostRepository.ts
│   │   │   ├── CourseRepository.ts
│   │   │   └── ProjectRepository.ts
│   │   │
│   │   ├── /websocket                   # WebSocket Integration
│   │   │   ├── websocket.client.ts
│   │   │   ├── events.ts
│   │   │   └── handlers.ts
│   │   │
│   │   ├── /cache                       # Caching Layer
│   │   │   ├── cache.service.ts
│   │   │   └── strategies.ts
│   │   │
│   │   ├── /i18n                        # Internationalization
│   │   │   ├── index.ts
│   │   │   └── /locales
│   │   │       ├── de.json
│   │   │       ├── en.json
│   │   │       └── pl.json
│   │   │
│   │   └── /persistence                 # Local Storage
│   │       ├── storage.service.ts
│   │       └── indexeddb.service.ts
│   │
│   ├── /shared                          ⚪ SHARED (Cross-Cutting)
│   │   │
│   │   ├── /types                       # Shared Type Definitions
│   │   │   ├── api.types.ts
│   │   │   ├── common.types.ts
│   │   │   ├── courseEditor.types.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── /constants                   # Shared Constants
│   │   │   ├── api.constants.ts
│   │   │   ├── events.constants.ts
│   │   │   ├── feature-flags.ts
│   │   │   └── errors.ts
│   │   │
│   │   ├── /utils                       # Utility Functions
│   │   │   ├── date.utils.ts
│   │   │   ├── format.utils.ts
│   │   │   ├── validation.utils.ts
│   │   │   └── crypto.utils.ts
│   │   │
│   │   └── /guards                      # Type Guards
│   │       ├── user.guards.ts
│   │       └── post.guards.ts
│   │
│   ├── App.vue                          # Root Component
│   └── main.ts                          # Application Entry Point
│
├── /scripts                             # Build Scripts
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

---

## 🎨 Layer Comparison: Backend ↔ Frontend

```
┌──────────────────────────────────────────────────────────────────┐
│ BACKEND                              FRONTEND                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 🔴 api/                              🔴 presentation/            │
│    ├── v1/                               ├── components/        │
│    │   ├── auth.py                       ├── views/             │
│    │   ├── courses.py                    ├── layouts/           │
│    │   └── social.py                     └── router/            │
│    │                                                             │
│    HTTP Layer (routes, blueprints)       UI Layer (Vue components)
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 🟡 application/                      🟡 application/            │
│    └── services/                         ├── services/          │
│        ├── content/                      ├── stores/            │
│        ├── social/                       ├── composables/       │
│        └── user/                         └── use-cases/         │
│                                                                  │
│    Application Services                  Application Services   │
│    (Business workflows)                  (State, Logic, Workflows)
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 🟢 domain/                           🟢 domain/                 │
│    ├── models/                           ├── models/            │
│    ├── ai/                               ├── value-objects/     │
│    └── social/                           ├── factories/         │
│                                          ├── events/            │
│                                          └── repositories/      │
│                                                                  │
│    Business Logic                        Business Logic        │
│    (Domain Models, Rules)                (Domain Models, Rules) │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 🔵 infrastructure/                   🔵 infrastructure/         │
│    ├── persistence/                      ├── api/               │
│    │   ├── database.py                   ├── websocket/         │
│    │   └── repositories/                 ├── cache/             │
│    ├── cache/                            ├── i18n/              │
│    ├── i18n/                             └── persistence/       │
│    ├── security/                                                │
│    └── monitoring/                                              │
│                                                                  │
│    Technical Services                    Technical Services    │
│    (DB, Cache, Security, i18n)           (API, WS, Cache, i18n)│
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ⚙️ core/                             ⚪ shared/                 │
│    └── featureflags/                     ├── types/             │
│                                          ├── constants/         │
│ 🔧 setup/                                ├── utils/             │
│    └── setupwizard/                      └── guards/            │
│                                                                  │
│    Feature Flags, Setup                  Cross-Cutting Concerns │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Layer Responsibilities

```
┌─────────────────────────────────────────────────────────────┐
│ 🔴 PRESENTATION LAYER (UI)                                  │
├─────────────────────────────────────────────────────────────┤
│ • Vue Components (.vue files)                               │
│ • Views (Pages)                                             │
│ • Layouts (MainLayout, DashboardLayout)                     │
│ • Router (Vue Router configuration)                         │
│                                                             │
│ Responsibilities:                                           │
│ ✓ Render UI                                                 │
│ ✓ Handle user interactions (clicks, input)                  │
│ ✓ Display data from stores                                  │
│ ✓ Navigation (router)                                       │
│                                                             │
│ ❌ NO business logic!                                        │
│ ❌ NO direct API calls! (use services)                       │
│ ❌ NO data transformation! (use composables/services)        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 🟡 APPLICATION LAYER (Business Workflows)                   │
├─────────────────────────────────────────────────────────────┤
│ • Services (Business logic orchestration)                   │
│ • Stores (Pinia - State management)                         │
│ • Composables (Reusable Vue logic)                          │
│ • Use Cases (Application workflows)                         │
│                                                             │
│ Responsibilities:                                           │
│ ✓ Orchestrate business workflows                            │
│ ✓ Manage application state (Pinia)                          │
│ ✓ Coordinate between Domain and Infrastructure              │
│ ✓ Handle complex user interactions                          │
│                                                             │
│ Examples:                                                   │
│ • PostService.createPost() - validates, calls API, updates  │
│ • useAuth() - manages auth state, login/logout logic        │
│ • CreatePostUseCase - full workflow: validate → save → notify│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 🟢 DOMAIN LAYER (Business Logic)                            │
├─────────────────────────────────────────────────────────────┤
│ • Models (Aggregate Roots, Entities)                        │
│ • Value Objects (Immutable, type-safe)                      │
│ • Factories (Object creation & validation)                  │
│ • Events (Domain events)                                    │
│ • Repository Interfaces (Contracts)                         │
│                                                             │
│ Responsibilities:                                           │
│ ✓ Define business entities (User, Post, Course)             │
│ ✓ Encapsulate business rules                                │
│ ✓ Validate domain objects                                   │
│ ✓ Emit domain events                                        │
│                                                             │
│ Examples:                                                   │
│ • User.model.ts - User entity with validation               │
│ • Email.vo.ts - Email value object (immutable, validated)   │
│ • Post.factory.ts - Creates valid Post instances            │
│                                                             │
│ ❌ NO framework dependencies (Vue, Pinia)!                   │
│ ❌ NO API calls!                                             │
│ ❌ Pure TypeScript/JavaScript only!                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 🔵 INFRASTRUCTURE LAYER (Technical Services)                │
├─────────────────────────────────────────────────────────────┤
│ • API Clients (HTTP requests)                               │
│ • WebSocket (Real-time communication)                       │
│ • Cache (Redis, LocalStorage)                               │
│ • i18n (Internationalization)                               │
│ • Persistence (IndexedDB, LocalStorage)                     │
│ • Repository Implementations                                │
│                                                             │
│ Responsibilities:                                           │
│ ✓ External API communication (Axios)                        │
│ ✓ WebSocket connections (Socket.io)                         │
│ ✓ Caching strategies                                        │
│ ✓ Data persistence (offline support)                        │
│ ✓ Translations (vue-i18n)                                   │
│                                                             │
│ Examples:                                                   │
│ • content.client.ts - API calls: GET /api/v1/courses        │
│ • websocket.client.ts - WebSocket connection                │
│ • UserRepository.ts - Implements IUserRepository            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ⚪ SHARED LAYER (Cross-Cutting)                             │
├─────────────────────────────────────────────────────────────┤
│ • Types (Shared TypeScript types)                           │
│ • Constants (API endpoints, error codes)                    │
│ • Utils (Helper functions)                                  │
│ • Guards (Type guards)                                      │
│                                                             │
│ Responsibilities:                                           │
│ ✓ Shared types used across all layers                       │
│ ✓ Constants (avoid magic strings)                           │
│ ✓ Pure utility functions (date, format, validation)         │
│ ✓ Type guards (TypeScript narrowing)                        │
│                                                             │
│ Examples:                                                   │
│ • api.types.ts - ApiResponse<T>, PaginatedResponse<T>       │
│ • events.constants.ts - WEBSOCKET_EVENTS                    │
│ • date.utils.ts - formatDate(), parseDate()                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow (Request → Response)

```
┌──────────────────────────────────────────────────────────────┐
│ USER INTERACTION FLOW                                        │
└──────────────────────────────────────────────────────────────┘

1. 👤 USER clicks "Create Post" button
   └─> 🔴 PostComposer.vue (Presentation)
       │
       │ calls
       ↓

2. 🟡 PostService.createPost() (Application)
   │  - Validates input
   │  - Calls Domain Factory
   │
   ├─> 🟢 Post.factory.create() (Domain)
   │   └─> Returns validated Post entity
   │
   ├─> 🔵 social.client.ts (Infrastructure)
   │   └─> POST /api/v1/social/posts
   │       └─> Backend API
   │
   └─> 🟡 useSocialStore().addPost() (Application)
       └─> Updates Pinia store
           │
           │ reactive update
           ↓

3. 🔴 FeedView.vue (Presentation)
   └─> Displays new post

┌──────────────────────────────────────────────────────────────┐
│ DEPENDENCY DIRECTION (Strict Downward)                       │
└──────────────────────────────────────────────────────────────┘

🔴 Presentation
   ↓ (depends on)
🟡 Application
   ↓ (depends on)
🟢 Domain
   ↓ (depends on)
🔵 Infrastructure

⚠️ NEVER:
   - Domain → Application ❌
   - Application → Presentation ❌
   - Domain → Infrastructure ❌
```

---

## 🎯 Example: Course Editor Flow

```
┌──────────────────────────────────────────────────────────────┐
│ COURSE EDITOR: AI Content Generation Flow                   │
└──────────────────────────────────────────────────────────────┘

1. 👤 USER types prompt in ChatInterface
   └─> 🔴 ChatInterface.vue
       │   (course-editor/ai-editor/)
       │
       │ v-model + @click
       ↓

2. 🟡 useChatStore().sendMessage()
   │   (application/stores/modules/course-editor/chat.store.ts)
   │
   ├─> 🟡 ChatService.sendMessage()
   │   │   (application/services/course-editor/ChatService.ts)
   │   │
   │   ├─> 🟢 ChatSession.addMessage()
   │   │   │   (domain/models/course-editor/ChatSession.model.ts)
   │   │   └─> Returns new ChatSession (immutable)
   │   │
   │   └─> 🔵 courseEditor.client.chat()
   │       │   (infrastructure/api/clients/courseEditor.client.ts)
   │       │
   │       └─> POST /api/v1/ai/chat
   │           └─> Backend API
   │               └─> AI generates response
   │
   └─> 🟡 useAIEditorStore().addGeneratedContent()
       └─> Updates store with AI response
           │
           │ reactive
           ↓

3. 🔴 ContentGenerator.vue
   └─> Displays generated content
   └─> User clicks "Insert into Manual Editor"
       │
       ↓

4. 🟡 useManualEditorStore().insertContent()
   └─> Content transferred to Manual Editor
       │
       │ reactive
       ↓

5. 🔴 ManualEditorContainer.vue
   └─> Shows content in editor
```

---

## 📋 File Count Summary

```
┌────────────────────────────────────────────────────────┐
│ LAYER                 FILES      DESCRIPTION           │
├────────────────────────────────────────────────────────┤
│ 🔴 Presentation       ~150       Components, Views     │
│    ├── components     ~120       Vue components        │
│    ├── views          ~20        Pages                 │
│    ├── layouts        ~5         Layouts               │
│    └── router         ~5         Router config         │
│                                                         │
│ 🟡 Application        ~60        Services, Stores      │
│    ├── services       ~25        Business services     │
│    ├── stores         ~20        Pinia stores          │
│    ├── composables    ~10        Vue composables       │
│    └── use-cases      ~5         Application workflows │
│                                                         │
│ 🟢 Domain             ~50        Models, Logic         │
│    ├── models         ~25        Domain models         │
│    ├── value-objects  ~8         Value objects         │
│    ├── factories      ~10        Factories             │
│    ├── events         ~5         Domain events         │
│    └── repositories   ~2         Repository interfaces │
│                                                         │
│ 🔵 Infrastructure     ~30        API, External         │
│    ├── api            ~15        API clients           │
│    ├── repositories   ~5         Repository impls      │
│    ├── websocket      ~3         WebSocket             │
│    ├── cache          ~2         Caching               │
│    ├── i18n           ~3         Translations          │
│    └── persistence    ~2         Local storage         │
│                                                         │
│ ⚪ Shared             ~20        Types, Utils          │
│    ├── types          ~5         Shared types          │
│    ├── constants      ~4         Constants             │
│    ├── utils          ~8         Utilities             │
│    └── guards         ~3         Type guards           │
│                                                         │
│ TOTAL                 ~310       TypeScript/Vue files  │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Reference

```
Import Examples:

🔴 Presentation:
   import PostCard from '@/presentation/components/social/PostCard.vue'
   import FeedView from '@/presentation/views/social/FeedView.vue'

🟡 Application:
   import { PostService } from '@/application/services/social/PostService'
   import { useSocialStore } from '@/application/stores/modules/social/social.store'
   import { useAuth } from '@/application/composables/useAuth'

🟢 Domain:
   import { Post } from '@/domain/models/social/Post.model'
   import { PostId } from '@/domain/value-objects/PostId.vo'
   import { PostFactory } from '@/domain/factories/social/Post.factory'

🔵 Infrastructure:
   import { socialClient } from '@/infrastructure/api/clients/social.client'
   import { PostRepository } from '@/infrastructure/repositories/PostRepository'

⚪ Shared:
   import type { ApiResponse } from '@/shared/types/api.types'
   import { API_ENDPOINTS } from '@/shared/constants/api.constants'
   import { formatDate } from '@/shared/utils/date.utils'
```

---

**END OF DOCUMENT**

Version: 4.0.2 - Frontend DDD Layer Overview
Stand: 20.01.2026
