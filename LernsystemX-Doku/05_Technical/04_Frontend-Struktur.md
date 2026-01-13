# 16 – Frontend-Struktur (Final) + API Contracts

**Version:** 3.1
**Stand:** 13.01.2026
**Änderungen:** Component Consolidation: 21 domains → 7 documented domains. /base now includes 11 subdirectories for consolidated components. /studio consolidates AI, Assessment, and System-Features. Full directory tree with all subdirectories documented.

---

## Überblick

Dieses Dokument definiert die **Enterprise-Grade Frontend-Architektur** des LSX Lernsystems **mit kompletten API Contracts**.

Das Frontend ist **modular**, **komponentenbasiert**, **mehrsprachig**, **performant**, **compliance-konform**, **typesicher** und für **ADHD/ADHS optimiert**.

### 🎯 Features v3.0

- ✅ **Social Network UI** - Posts, Feed, Follow, Engagement Components
- ✅ **Compliance Components** - Cookie Consent, Age Gates, Privacy Controls
- ✅ **Moderation Dashboard** - Content Review, Reports, Statistics
- ✅ **Feature Flag UI** - Admin Controls, A/B Testing, Rollout Management
- ✅ **API Contract Integration** - Jede Component hat klaren API-Endpoint
- ✅ **Pinia Store Mappings** - Store ↔ Backend Service
- ✅ **WebSocket Events** - Real-time Datenflüsse dokumentiert
- ✅ **TypeScript Types** - Alle Models definiert
- ✅ **Error Handling** - Standardisierte Error Codes

### 🛠️ Tech-Stack

| Technologie | Verwendung |
|------------|-----------|
| ⚡ **Vue.js 3** | Composition API + TypeScript |
| 🚀 **Vite** | Build Tool |
| 📦 **Pinia** | State Management (Type-Safe) |
| 🛣️ **Vue Router** | Routing mit Feature Flag Guards |
| 🎨 **TailwindCSS** | Styling |
| 🌍 **vue-i18n** | Internationalisierung (20+ Sprachen) |
| 🎥 **WebRTC** | Video/Audio (LiveRoom) |
| 🔌 **WebSockets** | Real-time (Notifications, Feed) |
| 📡 **Axios** | API Requests mit Interceptors & Type Safety |
| 🎚️ **Feature Flags** | Progressive Feature Rollout |
| 🛡️ **DOMPurify** | XSS Protection |
| 🍪 **js-cookie** | Cookie Management (GDPR) |
| 📊 **Chart.js** | Analytics & Statistics |
| 🔒 **CryptoJS** | Client-side Encryption (DRM) |
| **TypeScript** | Full Type Coverage |

---

## 1. Projektstruktur (Frontend-Verzeichnis)

### 📁 Komplette Verzeichnisstruktur v3.0

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
│           ├── community-guidelines.pdf
│           └── cookie-policy.pdf
│
├── /src
│   ├── /assets
│   │   ├── /images
│   │   ├── /icons
│   │   └── styles.css
│   │
│   ├── /types                  # ⭐ SHARED TYPE DEFINITIONS
│   │   ├── index.ts            # Main export
│   │   ├── auth.types.ts       # Auth Models
│   │   ├── user.types.ts       # User Models
│   │   ├── social.types.ts     # Social Models (Post, Comment, etc.)
│   │   ├── moderation.types.ts # Moderation Models
│   │   ├── compliance.types.ts # Compliance Models
│   │   ├── course.types.ts     # Course Models
│   │   ├── studio.types.ts     # 🎨 AI Studio Models (NEW)
│   │   ├── api.types.ts        # API Response Wrapper
│   │   └── common.types.ts     # Common Models
│   │
│   ├── /constants              # ⭐ SHARED CONSTANTS
│   │   ├── api.constants.ts    # Endpoints, Status Codes
│   │   ├── events.constants.ts # WebSocket Events
│   │   ├── feature-flags.ts    # Feature Flag Names
│   │   └── errors.ts           # Error Codes
│   │
│   ├── /api                    # 🌐 API CLIENT LAYER
│   │   ├── index.ts            # Main API Client
│   │   ├── auth.api.ts         # Auth Endpoints
│   │   ├── user.api.ts         # User Endpoints
│   │   ├── social.api.ts       # Social Endpoints
│   │   ├── moderation.api.ts   # Moderation Endpoints
│   │   ├── compliance.api.ts   # Compliance Endpoints
│   │   ├── course.api.ts       # Course Endpoints
│   │   ├── studio.api.ts       # 🎨 AI Studio Endpoints (NEW)
│   │   ├── interceptors.ts     # Axios Interceptors (Auth, Errors)
│   │   └── websocket.ts        # WebSocket Client
│   │
│   ├── /stores                 # 📦 PINIA STORES
│   │   ├── index.ts
│   │   ├── auth.store.ts       # Auth State & Actions
│   │   ├── user.store.ts       # User State & Actions
│   │   ├── social.store.ts     # Social State (Posts, Feed, Likes)
│   │   ├── feed.store.ts       # Feed Management
│   │   ├── moderation.store.ts # Moderation State
│   │   ├── compliance.store.ts # Compliance State
│   │   ├── studio.store.ts     # 🎨 AI Studio State (NEW)
│   │   ├── feature.store.ts    # Feature Flags State
│   │   └── ui.store.ts         # UI State (modals, etc.)
│   │
│   ├── /composables            # 🪝 COMPOSITION API HOOKS
│   │   ├── useAuth.ts          # Auth Hooks
│   │   ├── useSocial.ts        # Social Hooks
│   │   ├── useWebSocket.ts     # WebSocket Hooks
│   │   ├── useFeatureFlags.ts  # Feature Flag Hooks
│   │   ├── usePagination.ts    # Pagination Hooks
│   │   └── useApi.ts           # Generic API Hooks
│   │
│   ├── /components             # 🧩 UI COMPONENTS
│   │   ├── /base                # 🏗️ FOUNDATIONAL (Consolidated 11 domains)
│   │   │   ├── /ui              # Core UI components
│   │   │   │   ├── Button.vue
│   │   │   │   ├── Input.vue
│   │   │   │   ├── Textarea.vue
│   │   │   │   ├── Modal.vue
│   │   │   │   ├── Dropdown.vue
│   │   │   │   ├── Tabs.vue
│   │   │   │   ├── Loader.vue
│   │   │   │   ├── Alert.vue
│   │   │   │   ├── Card.vue
│   │   │   │   ├── ProgressBar.vue
│   │   │   │   ├── Tooltip.vue
│   │   │   │   ├── Badge.vue
│   │   │   │   ├── Avatar.vue
│   │   │   │   └── Pagination.vue
│   │   │   │
│   │   │   ├── /admin-ui        # Admin dashboard & management (Consolidated /admin)
│   │   │   ├── /charts          # Analytics charts (Consolidated /analytics)
│   │   │   ├── /content         # Course content UI (Consolidated /content)
│   │   │   ├── /core            # Auth & i18n (Consolidated /core)
│   │   │   ├── /dashboard       # Dashboard widgets (Consolidated /dashboard)
│   │   │   ├── /gamification    # RPG UI elements (Consolidated /gamification)
│   │   │   ├── /layout          # Layout components (Consolidated /layout)
│   │   │   ├── /learning        # Learning method components (Consolidated /learning)
│   │   │   ├── /system          # System admin components (Consolidated /system)
│   │   │   ├── /users           # User profile components (Consolidated /users)
│   │   │   └── /workspace       # Desktop workspace layer (Consolidated /workspace)
│   │   │
│   │   ├── /social             # 🌟 SOCIAL COMPONENTS
│   │   │   ├── PostCard.vue              # [API] GET /api/v1/social/posts/:id
│   │   │   ├── PostComposer.vue          # [API] POST /api/v1/social/posts
│   │   │   ├── PostList.vue              # [API] GET /api/v1/social/posts
│   │   │   ├── CommentSection.vue        # [API] GET /api/v1/social/posts/:id/comments
│   │   │   ├── CommentInput.vue          # [API] POST /api/v1/social/posts/:id/comments
│   │   │   ├── LikeButton.vue            # [API] POST /api/v1/social/posts/:id/likes
│   │   │   ├── ShareButton.vue           # [API] POST /api/v1/social/posts/:id/share
│   │   │   ├── FollowButton.vue          # [API] POST /api/v1/users/:id/follow
│   │   │   ├── FollowersList.vue         # [API] GET /api/v1/users/:id/followers
│   │   │   ├── FollowingList.vue         # [API] GET /api/v1/users/:id/following
│   │   │   ├── UserCard.vue              # [API] GET /api/v1/profile/:id
│   │   │   ├── UserBadge.vue             # Display Achievement Badge
│   │   │   ├── HashtagChip.vue           # Display Hashtag
│   │   │   ├── MentionInput.vue          # @mention Autocomplete
│   │   │   ├── TrendingCard.vue          # [API] GET /api/v1/social/trending
│   │   │   ├── SuggestedUsers.vue        # [API] GET /api/v1/users/suggestions
│   │   │   └── ActivityFeed.vue          # [WS] notification events
│   │   │
│   │   ├── /compliance         # ⚖️ COMPLIANCE COMPONENTS
│   │   │   ├── CookieConsent.vue         # [Local] js-cookie
│   │   │   ├── CookieSettings.vue        # [Local] js-cookie + [API] PUT /api/v1/compliance/cookies
│   │   │   ├── AgeGate.vue               # [API] POST /api/v1/auth/verify-age
│   │   │   ├── ParentalConsent.vue       # [API] POST /api/v1/compliance/parental-consent
│   │   │   ├── PrivacyDashboard.vue      # [API] GET /api/v1/compliance/privacy
│   │   │   ├── DataExport.vue            # [API] POST /api/v1/compliance/data-export
│   │   │   ├── DataDeletion.vue          # [API] POST /api/v1/compliance/data-deletion
│   │   │   ├── ConsentManager.vue        # [API] GET /api/v1/compliance/consent
│   │   │   ├── ReportContent.vue         # [API] POST /api/v1/moderation/reports
│   │   │   ├── ReportStatus.vue          # [API] GET /api/v1/moderation/reports/:id
│   │   │   ├── ContentWarning.vue        # Display Warning
│   │   │   ├── SafeMode.vue              # [API] PUT /api/v1/user/safe-mode
│   │   │   ├── ParentalControls.vue      # [API] GET /api/v1/parental/dashboard
│   │   │   ├── ScreenTimeWidget.vue      # [API] GET /api/v1/parental/screen-time
│   │   │   └── TransparencyReport.vue    # [API] GET /api/v1/transparency/reports
│   │   │
│   │   ├── /moderation         # 🛡️ MODERATION COMPONENTS
│   │   │   ├── ModerationQueue.vue       # [API] GET /api/v1/moderation/queue
│   │   │   ├── ContentReview.vue         # [API] GET /api/v1/moderation/queue/:id
│   │   │   ├── ReportDetails.vue         # [API] GET /api/v1/moderation/reports/:id
│   │   │   ├── ModerationActions.vue     # [API] POST /api/v1/moderation/actions
│   │   │   ├── UserHistory.vue           # [API] GET /api/v1/moderation/users/:id/history
│   │   │   ├── ModerationStats.vue       # [API] GET /api/v1/moderation/statistics
│   │   │   ├── SLAMonitor.vue            # [API] GET /api/v1/moderation/sla-monitor
│   │   │   └── AppealReview.vue          # [API] GET /api/v1/moderation/appeals/:id
│   │   │
│   │   ├── /security           # 🔒 SECURITY COMPONENTS
│   │   │   ├── TwoFactorAuth.vue         # [API] POST /api/v1/auth/2fa-setup
│   │   │   ├── SessionManager.vue        # [API] GET /api/v1/auth/sessions
│   │   │   ├── SecurityLog.vue           # [API] GET /api/v1/security/logs
│   │   │   ├── DRMLicenseDisplay.vue     # [API] GET /api/v1/drm/license
│   │   │   ├── Watermark.vue             # Display Watermark
│   │   │   └── AccessGate.vue            # [API] POST /api/v1/drm/verify-access
│   │   │
│   │   ├── /feature-flags      # 🎚️ FEATURE FLAG COMPONENTS
│   │   │   ├── FeatureGate.vue           # Conditionally render content
│   │   │   ├── FeatureFlagBadge.vue      # Display "Beta" badge
│   │   │   ├── RolloutProgress.vue       # [API] GET /api/v1/admin/features/:id/rollout
│   │   │   └── ABTestBanner.vue          # Display A/B Test info
│   │   │
│   │   └── /studio             # 🎨 AI STUDIO COMPONENTS (Consolidated 3 domains)
│   │       ├── /ai                      # AI Studio & Authoring (Consolidated /ai)
│   │       │   ├── /admin               # Admin AI features
│   │       │   │   ├── /authoring       # Content authoring
│   │       │   │   ├── /management      # AI job/model management
│   │       │   │   ├── /settings        # AI settings
│   │       │   │   └── /studio          # AI Studio UI
│   │       │   └── /user                # User AI features
│   │       │       ├── /chat            # AI chat interface
│   │       │       ├── /quiz-generation # Quiz generation UI
│   │       │       └── /tutor           # AI tutor companion
│   │       │
│   │       ├── /assessment              # Exam & Assessment (Consolidated /assessment)
│   │       │   ├── /admin               # Admin exam management
│   │       │   │   ├── /exams           # Exam CRUD
│   │       │   │   ├── /settings        # Exam settings
│   │       │   │   └── /views           # Admin views
│   │       │   └── /user                # User exam taking
│   │       │       ├── /simulation      # Exam simulation
│   │       │       └── /results         # Results & feedback
│   │       │
│   │       └── /system-features         # 25 System Features (Consolidated /system-features)
│   │           ├── /tutor               # NPC Tutor
│   │           ├── ChapterCompletionSystem.vue
│   │           ├── IHKExamSystem.vue
│   │           ├── WhiteboardEngine.vue
│   │           └── ... (15 more components)
│   │
│   ├── /layouts                # 🏗️ LAYOUTS
│   │   ├── MainLayout.vue
│   │   ├── AuthLayout.vue
│   │   ├── DashboardLayout.vue
│   │   ├── AdminLayout.vue
│   │   ├── ModeratorLayout.vue
│   │   ├── OrganizationLayout.vue
│   │   └── MinimalLayout.vue
│   │
│   ├── /pages                  # 📄 PAGES/VIEWS
│   │   ├── /auth
│   │   │   ├── Login.vue                 # [API] POST /api/v1/auth/login
│   │   │   ├── Register.vue              # [API] POST /api/v1/auth/register
│   │   │   ├── RegisterWithConsent.vue   # [API] POST /api/v1/auth/register
│   │   │   ├── ForgotPassword.vue        # [API] POST /api/v1/auth/forgot-password
│   │   │   └── AgeVerification.vue       # [API] POST /api/v1/auth/verify-age
│   │   │
│   │   ├── /dashboard
│   │   │   ├── Index.vue                 # [API] GET /api/v1/dashboard
│   │   │   ├── Settings.vue              # [API] PUT /api/v1/user/settings
│   │   │   ├── Notifications.vue         # [API] GET /api/v1/notifications
│   │   │   └── LayoutManager.vue         # [API] PUT /api/v1/user/dashboard-layout
│   │   │
│   │   ├── /social
│   │   │   ├── Feed.vue                  # [API] GET /api/v1/social/posts
│   │   │   ├── Explore.vue               # [API] GET /api/v1/social/explore
│   │   │   ├── Trending.vue              # [API] GET /api/v1/social/trending
│   │   │   ├── Profile.vue               # [API] GET /api/v1/profile/:user_id
│   │   │   ├── EditProfile.vue           # [API] PUT /api/v1/profile
│   │   │   ├── Followers.vue             # [API] GET /api/v1/users/:id/followers
│   │   │   ├── Following.vue             # [API] GET /api/v1/users/:id/following
│   │   │   ├── Post.vue                  # [API] GET /api/v1/social/posts/:id
│   │   │   ├── Bookmarks.vue             # [API] GET /api/v1/social/bookmarks
│   │   │   ├── Messages.vue              # [WS] message events
│   │   │   └── Notifications.vue         # [API] GET /api/v1/notifications
│   │   │
│   │   ├── /privacy
│   │   │   ├── PrivacySettings.vue       # [API] GET/PUT /api/v1/compliance/privacy
│   │   │   ├── DataExport.vue            # [API] POST /api/v1/compliance/data-export
│   │   │   ├── DataDeletion.vue          # [API] POST /api/v1/compliance/data-deletion
│   │   │   ├── ConsentHistory.vue        # [API] GET /api/v1/compliance/consent-history
│   │   │   ├── CookiePreferences.vue     # [Local] js-cookie
│   │   │   ├── PrivacyPolicy.vue         # [Static]
│   │   │   ├── TermsOfService.vue        # [Static]
│   │   │   └── CommunityGuidelines.vue   # [Static]
│   │   │
│   │   ├── /moderation
│   │   │   ├── Dashboard.vue             # [API] GET /api/v1/moderation/dashboard
│   │   │   ├── Queue.vue                 # [API] GET /api/v1/moderation/queue
│   │   │   ├── Reports.vue               # [API] GET /api/v1/moderation/reports
│   │   │   ├── ReviewContent.vue         # [API] GET /api/v1/moderation/queue/:id
│   │   │   ├── Appeals.vue               # [API] GET /api/v1/moderation/appeals
│   │   │   ├── Statistics.vue            # [API] GET /api/v1/moderation/statistics
│   │   │   ├── TransparencyReports.vue   # [API] GET /api/v1/transparency/reports
│   │   │   └── UserProfile.vue           # [API] GET /api/v1/moderation/users/:id
│   │   │
│   │   ├── /parental
│   │   │   ├── Dashboard.vue             # [API] GET /api/v1/parental/dashboard
│   │   │   ├── ActivityLog.vue           # [API] GET /api/v1/parental/activity
│   │   │   ├── ScreenTime.vue            # [API] GET /api/v1/parental/screen-time
│   │   │   ├── ContentApproval.vue       # [API] GET /api/v1/parental/approvals
│   │   │   ├── Restrictions.vue          # [API] PUT /api/v1/parental/restrictions
│   │   │   └── Reports.vue               # [API] GET /api/v1/parental/reports
│   │   │
│   │   ├── /admin
│   │   │   ├── Dashboard.vue             # [API] GET /api/v1/admin/dashboard
│   │   │   ├── Users.vue                 # [API] GET /api/v1/admin/users
│   │   │   ├── Organizations.vue         # [API] GET /api/v1/admin/organizations
│   │   │   ├── Courses.vue               # [API] GET /api/v1/admin/courses
│   │   │   ├── FeatureFlags.vue          # [API] GET /api/v1/admin/features
│   │   │   ├── RolloutControl.vue        # [API] PUT /api/v1/admin/features/:id/rollout
│   │   │   └── ComplianceDashboard.vue   # [API] GET /api/v1/admin/compliance
│   │   │
│   │   └── /liveroom
│   │       ├── Room.vue                  # [WS] video, chat
│   │       ├── Whiteboard.vue            # [WS] whiteboard events
│   │       ├── Chat.vue                  # [WS] chat messages
│   │       ├── Recording.vue             # [API] POST /api/v1/liveroom/record
│   │       └── Participants.vue          # [WS] participant events
│   │
│   │   └── /studio              # 🎨 AI STUDIO PAGES (NEW)
│   │       ├── Dashboard.vue             # [API] GET /api/v1/studio/projects
│   │       ├── Editor.vue                # [API] POST /api/v1/studio/chat + generate
│   │       ├── Project.vue               # [API] GET /api/v1/studio/projects/:id
│   │       ├── Chat.vue                  # [WS] studio:message_received
│   │       ├── Generator.vue             # [API] POST /api/v1/studio/generate
│   │       ├── Variants.vue              # [API] POST /api/v1/studio/variants
│   │       ├── Templates.vue             # [API] GET /api/v1/studio/templates
│   │       ├── History.vue               # [API] GET /api/v1/studio/history
│   │       └── Settings.vue              # [API] PUT /api/v1/studio/settings
│   │
│   ├── /router
│   │   ├── index.ts            # Router Config
│   │   ├── routes.ts           # Route Definitions
│   │   ├── guards.ts           # Route Guards (Auth, Feature Flags)
│   │   └── middleware.ts       # Route Middleware
│   │
│   ├── /utils
│   │   ├── api-helpers.ts      # API Helper Functions
│   │   ├── date.ts             # Date Utilities
│   │   ├── format.ts           # Format Utilities
│   │   ├── validation.ts       # Validators
│   │   └── storage.ts          # Local Storage Helpers
│   │
│   ├── App.vue                 # Root Component
│   └── main.ts                 # Application Entry Point
│
├── vite.config.ts
├── tsconfig.json               # TypeScript Config
├── tailwind.config.js
└── package.json
```

---

## 2. TypeScript Type Definitions

### 📋 auth.types.ts

```typescript
// src/types/auth.types.ts

export interface User {
  id: string
  email: string
  username: string
  role: 'user' | 'moderator' | 'admin' | 'parent'
  avatar?: string
  age_verified: boolean
  is_online: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  user: User
  expires_in: number
}

export interface RegisterRequest {
  email: string
  password: string
  username: string
  age_verified: boolean
  consent: {
    terms: boolean
    privacy: boolean
    marketing?: boolean
  }
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  accessToken: string | null
  refreshToken: string | null
  loading: boolean
  error: string | null
}
```

### 📋 social.types.ts

```typescript
// src/types/social.types.ts

export interface Post {
  id: string
  author_id: string
  author: User
  title: string
  content: string
  media: Media[]
  likes_count: number
  comments_count: number
  shares_count: number
  is_liked_by_user: boolean
  is_bookmarked_by_user: boolean
  created_at: string
  updated_at: string
}

export interface CreatePostRequest {
  title: string
  content: string
  media?: File[]
  tags?: string[]
}

export interface Comment {
  id: string
  post_id: string
  author_id: string
  author: User
  content: string
  likes_count: number
  is_liked_by_user: boolean
  created_at: string
}

export interface CreateCommentRequest {
  content: string
  parent_comment_id?: string
}

export interface Like {
  id: string
  user_id: string
  post_id?: string
  comment_id?: string
  created_at: string
}

export interface Media {
  id: string
  url: string
  type: 'image' | 'video'
  width?: number
  height?: number
}

export interface Feed {
  posts: Post[]
  total: number
  page: number
  limit: number
  has_more: boolean
}
```

### 📋 moderation.types.ts

```typescript
// src/types/moderation.types.ts

export interface ContentReport {
  id: string
  reporter_id: string
  content_type: 'post' | 'comment' | 'user' | 'message'
  content_id: string
  reason: string
  description?: string
  status: 'new' | 'assigned' | 'under_review' | 'resolved' | 'rejected'
  priority: 'low' | 'medium' | 'high' | 'critical'
  assignee_id?: string
  created_at: string
  updated_at: string
  resolved_at?: string
  sla_deadline: string
}

export interface CreateReportRequest {
  content_type: string
  content_id: string
  reason: string
  description?: string
  evidence?: string[]
}

export interface ModerationAction {
  report_id: string
  action: 'approve' | 'remove' | 'warn_user' | 'suspend_user' | 'ban_user'
  reason: string
  duration?: number // in days, null = permanent
}

export interface ModerationQueue {
  reports: ContentReport[]
  total: number
  page: number
  limit: number
  has_more: boolean
}

export interface ModerationStats {
  total_reports: number
  pending: number
  under_review: number
  resolved: number
  avg_response_time: number
  sla_compliance: number
}
```

---

## 3. API Endpoints & Store Mappings

### 🌐 AUTH Endpoints

| Endpoint | Method | Store Action | Component | Request | Response | WebSocket Event |
|----------|--------|--------------|-----------|---------|----------|-----------------|
| `/api/v1/auth/register` | POST | `authStore.register()` | RegisterWithConsent.vue | `RegisterRequest` | `LoginResponse` | — |
| `/api/v1/auth/login` | POST | `authStore.login()` | Login.vue | `LoginRequest` | `LoginResponse` | `auth:login` |
| `/api/v1/auth/logout` | POST | `authStore.logout()` | (Global) | — | `{ success }` | `auth:logout` |
| `/api/v1/auth/refresh` | POST | `authStore.refreshToken()` | (Interceptor) | `{ refresh_token }` | `{ access_token }` | — |
| `/api/v1/auth/verify-age` | POST | `authStore.verifyAge()` | AgeVerification.vue | `{ age_verified }` | `{ success }` | — |

**Store Implementation:**
```typescript
// src/stores/auth.store.ts
import { defineStore } from 'pinia'
import { authApi } from '@/api/auth.api'
import type { User, LoginRequest, LoginResponse } from '@/types'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    accessToken: null as string | null,
    refreshToken: null as string | null,
    isAuthenticated: false,
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async login(credentials: LoginRequest) {
      this.loading = true
      try {
        const response = await authApi.login(credentials)
        this.user = response.user
        this.accessToken = response.access_token
        this.refreshToken = response.refresh_token
        this.isAuthenticated = true
        localStorage.setItem('accessToken', response.access_token)
        localStorage.setItem('refreshToken', response.refresh_token)
        return response
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        await authApi.logout()
        this.user = null
        this.accessToken = null
        this.refreshToken = null
        this.isAuthenticated = false
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
      } catch (err) {
        console.error('Logout error:', err)
      }
    },
  },
})
```

### 🌟 SOCIAL Endpoints

| Endpoint | Method | Store Action | Component | Request | Response | WebSocket Event |
|----------|--------|--------------|-----------|---------|----------|-----------------|
| `/api/v1/social/posts` | GET | `socialStore.loadFeed()` | Feed.vue | `{ page, limit, sort }` | `Feed` | `feed:updated` |
| `/api/v1/social/posts/:post_id` | GET | `socialStore.loadPost()` | Post.vue | — | `Post` | — |
| `/api/v1/social/posts` | POST | `socialStore.createPost()` | PostComposer.vue | `CreatePostRequest` | `Post` | `post:created` |
| `/api/v1/social/posts/:post_id/likes` | POST | `socialStore.likePost()` | LikeButton.vue | — | `{ likes_count }` | `post:liked` |
| `/api/v1/social/posts/:post_id/likes` | DELETE | `socialStore.unlikePost()` | LikeButton.vue | — | `{ likes_count }` | `post:unliked` |
| `/api/v1/social/posts/:post_id/comments` | GET | `socialStore.loadComments()` | CommentSection.vue | `{ page, limit }` | `Comment[]` | — |
| `/api/v1/social/posts/:post_id/comments` | POST | `socialStore.createComment()` | CommentInput.vue | `CreateCommentRequest` | `Comment` | `comment:created` |
| `/api/v1/users/:user_id/follow` | POST | `userStore.followUser()` | FollowButton.vue | — | `{ following: true }` | `user:followed` |
| `/api/v1/users/:user_id/unfollow` | DELETE | `userStore.unfollowUser()` | FollowButton.vue | — | `{ following: false }` | `user:unfollowed` |
| `/api/v1/social/trending` | GET | `socialStore.loadTrending()` | Trending.vue | — | `Post[]` | — |
| `/api/v1/social/explore` | GET | `socialStore.loadExplore()` | Explore.vue | `{ page, category }` | `Feed` | — |
| `/api/v1/social/bookmarks` | GET | `socialStore.loadBookmarks()` | Bookmarks.vue | `{ page, limit }` | `Post[]` | — |
| `/api/v1/social/posts/:post_id/bookmark` | POST | `socialStore.bookmarkPost()` | PostCard.vue | — | `{ bookmarked: true }` | — |

**Store Implementation:**
```typescript
// src/stores/social.store.ts
import { defineStore } from 'pinia'
import { socialApi } from '@/api/social.api'
import type { Post, Feed, CreatePostRequest } from '@/types'

export const useSocialStore = defineStore('social', {
  state: () => ({
    feed: {
      posts: [] as Post[],
      total: 0,
      page: 1,
      limit: 20,
      has_more: false,
    } as Feed,
    currentPost: null as Post | null,
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async loadFeed(page = 1, limit = 20) {
      this.loading = true
      try {
        const response = await socialApi.getFeed({ page, limit, sort: 'recent' })
        if (page === 1) {
          this.feed = response
        } else {
          this.feed.posts = [...this.feed.posts, ...response.posts]
          this.feed.page = page
          this.feed.has_more = response.has_more
        }
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    },

    async createPost(data: CreatePostRequest) {
      try {
        const newPost = await socialApi.createPost(data)
        this.feed.posts.unshift(newPost)
        this.feed.total += 1
        return newPost
      } catch (err) {
        this.error = err.message
        throw err
      }
    },

    async likePost(postId: string) {
      try {
        const response = await socialApi.likePost(postId)
        const post = this.feed.posts.find(p => p.id === postId)
        if (post) {
          post.likes_count = response.likes_count
          post.is_liked_by_user = true
        }
      } catch (err) {
        this.error = err.message
      }
    },
  },
})
```

### 🛡️ MODERATION Endpoints

| Endpoint | Method | Store Action | Component | Request | Response | WebSocket Event |
|----------|--------|--------------|-----------|---------|----------|-----------------|
| `/api/v1/moderation/queue` | GET | `moderationStore.loadQueue()` | ModerationQueue.vue | `{ page, limit, status }` | `ModerationQueue` | — |
| `/api/v1/moderation/queue/:report_id` | GET | `moderationStore.loadReport()` | ContentReview.vue | — | `ContentReport` | — |
| `/api/v1/moderation/actions` | POST | `moderationStore.takeAction()` | ModerationActions.vue | `ModerationAction` | `{ success }` | `moderation:action` |
| `/api/v1/moderation/reports` | GET | `moderationStore.loadReports()` | Reports.vue | `{ page, status }` | `ContentReport[]` | — |
| `/api/v1/moderation/statistics` | GET | `moderationStore.loadStats()` | ModerationStats.vue | — | `ModerationStats` | — |
| `/api/v1/moderation/sla-monitor` | GET | `moderationStore.loadSLA()` | SLAMonitor.vue | — | `{ reports, compliance }` | — |

---

## 4. WebSocket Events

### 📡 Real-time Event Streams

```typescript
// src/constants/events.constants.ts

export const WEBSOCKET_EVENTS = {
  // Auth
  AUTH_LOGIN: 'auth:login',
  AUTH_LOGOUT: 'auth:logout',
  
  // Social
  POST_CREATED: 'post:created',
  POST_DELETED: 'post:deleted',
  POST_LIKED: 'post:liked',
  POST_UNLIKED: 'post:unliked',
  COMMENT_CREATED: 'comment:created',
  COMMENT_DELETED: 'comment:deleted',
  FEED_UPDATED: 'feed:updated',
  
  // User
  USER_FOLLOWED: 'user:followed',
  USER_UNFOLLOWED: 'user:unfollowed',
  USER_ONLINE: 'user:online',
  USER_OFFLINE: 'user:offline',
  
  // Notifications
  NOTIFICATION_NEW: 'notification:new',
  NOTIFICATION_READ: 'notification:read',
  
  // Moderation
  MODERATION_ACTION: 'moderation:action',
  REPORT_STATUS_CHANGED: 'report:status_changed',
  
  // Messages
  MESSAGE_NEW: 'message:new',
  MESSAGE_READ: 'message:read',
  
  // LiveRoom
  PARTICIPANT_JOINED: 'participant:joined',
  PARTICIPANT_LEFT: 'participant:left',
  WHITEBOARD_UPDATED: 'whiteboard:updated',
}
```

**Beispiel Event Handler:**
```typescript
// In Feed.vue
import { useWebSocket } from '@/composables/useWebSocket'
import { WEBSOCKET_EVENTS } from '@/constants/events.constants'

export default defineComponent({
  setup() {
    const socialStore = useSocialStore()
    const { on, emit } = useWebSocket()

    onMounted(() => {
      // Subscribe to post creation
      on(WEBSOCKET_EVENTS.POST_CREATED, (post) => {
        socialStore.feed.posts.unshift(post)
      })

      // Subscribe to likes
      on(WEBSOCKET_EVENTS.POST_LIKED, ({ post_id, likes_count }) => {
        const post = socialStore.feed.posts.find(p => p.id === post_id)
        if (post) post.likes_count = likes_count
      })
    })

    return { socialStore }
  },
})
```

---

## 5. Feature Flags Integration

### 🎚️ Feature Flag Management

```typescript
// src/composables/useFeatureFlags.ts
import { computed } from 'vue'
import { useFeatureStore } from '@/stores/feature.store'

export function useFeatureFlags() {
  const featureStore = useFeatureStore()

  return {
    // Check if feature is enabled
    isFeatureEnabled: (featureName: string) => 
      computed(() => featureStore.isFeatureEnabled(featureName)),
    
    // Check if feature is in beta
    isFeatureBeta: (featureName: string) => 
      computed(() => featureStore.isFeatureBeta(featureName)),
    
    // Get rollout percentage
    getRolloutPercentage: (featureName: string) => 
      computed(() => featureStore.getRolloutPercentage(featureName)),
  }
}
```

**In Komponenten verwenden:**
```vue
<template>
  <!-- Option 1: v-feature Directive -->
  <div v-feature="'social-network'">
    <Feed />
  </div>

  <!-- Option 2: v-if -->
  <div v-if="isFeatureEnabled('social-network')">
    <Feed />
  </div>

  <!-- Option 3: Component-level -->
  <FeatureGate feature-name="social-network">
    <Feed />
  </FeatureGate>
</template>

<script setup lang="ts">
import { useFeatureFlags } from '@/composables/useFeatureFlags'

const { isFeatureEnabled } = useFeatureFlags()
</script>
```

---

## 6. Error Handling

### 🛑 Standardisierte Error Codes

```typescript
// src/constants/errors.ts

export const ERROR_CODES = {
  // Auth Errors
  INVALID_CREDENTIALS: 'AUTH_001',
  USER_NOT_FOUND: 'AUTH_002',
  EMAIL_ALREADY_EXISTS: 'AUTH_003',
  TOKEN_EXPIRED: 'AUTH_004',
  INVALID_TOKEN: 'AUTH_005',
  
  // Validation Errors
  INVALID_INPUT: 'VALIDATION_001',
  REQUIRED_FIELD: 'VALIDATION_002',
  
  // Permission Errors
  UNAUTHORIZED: 'PERMISSION_001',
  FORBIDDEN: 'PERMISSION_002',
  
  // Resource Errors
  NOT_FOUND: 'RESOURCE_001',
  CONFLICT: 'RESOURCE_002',
  
  // Server Errors
  INTERNAL_SERVER_ERROR: 'SERVER_001',
  SERVICE_UNAVAILABLE: 'SERVER_002',
}

export const ERROR_MESSAGES: Record<string, string> = {
  [ERROR_CODES.INVALID_CREDENTIALS]: 'Invalid email or password',
  [ERROR_CODES.USER_NOT_FOUND]: 'User not found',
  [ERROR_CODES.EMAIL_ALREADY_EXISTS]: 'Email already exists',
  [ERROR_CODES.TOKEN_EXPIRED]: 'Session expired. Please login again',
  [ERROR_CODES.UNAUTHORIZED]: 'You are not authorized to access this resource',
}
```

**Error Handler in API:**
```typescript
// src/api/interceptors.ts
export function setupInterceptors(apiClient) {
  apiClient.interceptors.response.use(
    response => response,
    error => {
      const errorCode = error.response?.data?.code
      const message = ERROR_MESSAGES[errorCode] || error.message
      
      // Handle token expiration
      if (errorCode === ERROR_CODES.TOKEN_EXPIRED) {
        const authStore = useAuthStore()
        authStore.logout()
        window.location.href = '/login'
      }
      
      return Promise.reject({ code: errorCode, message })
    }
  )
}
```

---

## 7. API Client Setup

### 📡 Axios Configuration

```typescript
// src/api/index.ts
import axios, { AxiosInstance } from 'axios'
import { setupInterceptors } from './interceptors'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

setupInterceptors(apiClient)

export default apiClient
```

### 🔐 JWT Token Management

```typescript
// src/api/interceptors.ts
import { useAuthStore } from '@/stores/auth.store'

export function setupInterceptors(apiClient) {
  // Request Interceptor - Add JWT Token
  apiClient.interceptors.request.use(config => {
    const authStore = useAuthStore()
    const token = authStore.accessToken
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  })

  // Response Interceptor - Handle Errors & Token Refresh
  apiClient.interceptors.response.use(
    response => response,
    async error => {
      const authStore = useAuthStore()
      const originalRequest = error.config
      
      // Token expired - try refresh
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true
        
        try {
          const newToken = await authStore.refreshToken()
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return apiClient(originalRequest)
        } catch (err) {
          authStore.logout()
          window.location.href = '/login'
        }
      }
      
      return Promise.reject(error)
    }
  )
}
```

---

## 8. Component-Store-API Flow Beispiele

### 📝 Post erstellen - Complete Flow

**1. Component (PostComposer.vue)**
```vue
<template>
  <form @submit.prevent="submitPost">
    <textarea v-model="formData.content" placeholder="Was möchtest du teilen?"></textarea>
    <input type="file" multiple @change="handleMediaUpload" />
    <button type="submit" :disabled="isSubmitting">Posten</button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSocialStore } from '@/stores/social.store'
import type { CreatePostRequest } from '@/types'

const socialStore = useSocialStore()
const formData = ref<CreatePostRequest>({ title: '', content: '', media: [] })
const isSubmitting = ref(false)

async function submitPost() {
  isSubmitting.value = true
  try {
    // Action ruft API Endpoint auf (siehe Store)
    await socialStore.createPost(formData.value)
    formData.value = { title: '', content: '', media: [] }
  } catch (err) {
    console.error('Error creating post:', err)
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

**2. Store Action (social.store.ts)**
```typescript
async createPost(data: CreatePostRequest) {
  try {
    // Ruft API Endpoint auf
    const newPost = await socialApi.createPost(data)
    
    // Aktualisiert lokalen State
    this.feed.posts.unshift(newPost)
    this.feed.total += 1
    
    return newPost
  } catch (err) {
    this.error = err.message
    throw err
  }
}
```

**3. API Client (social.api.ts)**
```typescript
export const socialApi = {
  async createPost(data: CreatePostRequest): Promise<Post> {
    // Ruft Backend Endpoint auf: POST /api/v1/social/posts
    const response = await apiClient.post('/api/v1/social/posts', data)
    return response.data
  },
}
```

**4. WebSocket Event**
```
Backend emittet nach erfolgreicher Erstellung:
  → WebSocket Event: post:created { id, author, title, content, ... }
  
Frontend empfängt in Feed.vue:
  → Aktualisiert feed Store automatisch
  → UI re-rendert sofort
```

---

## 9. Router Guards & Feature Flags

```typescript
// src/router/guards.ts
import { useAuthStore } from '@/stores/auth.store'
import { useFeatureStore } from '@/stores/feature.store'

export function requireAuth(to, from, next) {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
}

export function requireRole(role: string) {
  return (to, from, next) => {
    const authStore = useAuthStore()
    
    if (authStore.user?.role === role || authStore.user?.role === 'admin') {
      next()
    } else {
      next({ name: 'Unauthorized' })
    }
  }
}

export function requireFeature(featureName: string) {
  return (to, from, next) => {
    const featureStore = useFeatureStore()
    
    if (featureStore.isFeatureEnabled(featureName)) {
      next()
    } else {
      next({ name: 'FeatureNotAvailable' })
    }
  }
}
```

**Route Definition:**
```typescript
// src/router/routes.ts
const routes = [
  {
    path: '/social',
    component: () => import('@/layouts/MainLayout.vue'),
    beforeEnter: [requireAuth, requireFeature('social-network')],
    children: [
      {
        path: 'feed',
        name: 'Feed',
        component: () => import('@/pages/social/Feed.vue'),
      },
    ],
  },
]
```

---

## 10. Zusammenfassung

### ✅ Frontend Architecture v3.0

| Aspekt | Implementation | Status |
|--------|----------------|--------|
| 🧩 **Komponenten** | Vue 3 + Composition API | ✅ |
| 📦 **State Management** | Pinia (Type-Safe) | ✅ |
| 🌐 **API Integration** | Axios + REST Contracts | ✅ |
| 🔄 **WebSocket** | Real-time Events | ✅ |
| 🎚️ **Feature Flags** | v-feature Directive + Guards | ✅ |
| 🔐 **Auth** | JWT + Refresh Token | ✅ |
| 🛡️ **Type Safety** | TypeScript + Interfaces | ✅ |
| ⚠️ **Error Handling** | Standardized Error Codes | ✅ |
| 🌍 **i18n** | vue-i18n (20+ Languages) | ✅ |
| 📊 **Analytics** | Chart.js + Stats | ✅ |

### 💡 Development Workflow

```
1. Backend entwickelt neuen Endpoint
   ↓
2. Type Definition schreiben (auth.types.ts, social.types.ts, etc.)
   ↓
3. API Client Methode erstellen (social.api.ts)
   ↓
4. Store Action implementieren (social.store.ts)
   ↓
5. Component mit Store verbinden
   ↓
6. WebSocket Event definieren & integrieren
   ↓
7. Feature Flag Guard hinzufügen
```

---

## 📌 Dokument abgeschlossen

**Version:** 3.0  
**Status:** Final  
**Letzte Aktualisierung:** 13.01.2026

**Neue Features v3.0:**
- ✅ Komplette API Contract Dokumentation
- ✅ Store ↔ API Mapping für alle Features
- ✅ TypeScript Type Definitions
- ✅ WebSocket Event Dokumentation
- ✅ Feature Flag Integration Beispiele
- ✅ Error Handling Strategien
- ✅ Component-Store-API Flow Diagramme
- ✅ Development Workflow Dokumentation

> **Wichtig:** Frontend und Backend entwickeln gegen diesen Contract. Keine spontanen API-Änderungen ohne Dokumentation zu aktualisieren!
