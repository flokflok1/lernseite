# 04 – Frontend-Struktur (DDD + GBA Edition)

**Version:** 2.1 (DDD Architecture + Course Editor)
**Stand:** 2026-01-29
**Status:** Production Ready

Das Dokument definiert die **Domain-Driven Design (DDD) Frontend-Architektur** des LSX Lernsystems mit **Group-Based Authorization (GBA)** für alle Verwaltungs- und Zugriffskontrollfeatures.

Das Frontend folgt **Clean Architecture Prinzipien** mit klarer Trennung von:
- **Presentation Layer** - UI Components, Views, Layouts
- **Application Layer** - Business Logic, Services, Stores
- **Domain Layer** - Models, Value Objects, Factories, Business Rules
- **Infrastructure Layer** - API Clients, External Services, WebSocket

---

## Überblick: Frontend-Architektur

### 🎯 DDD Features v2.0 (GBA Edition)

- ✅ **4-Layer Architecture** - Presentation → Application → Domain → Infrastructure
- ✅ **GBA-basierte Autorisierung** - Groups statt Roles, feingranulare Permissions
- ✅ **Domain Models** - Immutable, Type-Safe, Business Logic Encapsulation
- ✅ **Factory Pattern** - Centralized Object Creation & Validation
- ✅ **Repository Pattern** - Data Access Abstraction
- ✅ **Value Objects** - Email, UserId, PostId (Type Safety)
- ✅ **Aggregate Roots** - User, Post, Course (Domain Boundaries)
- ✅ **Domain Events** - post:created, user:followed (Event-Driven)
- ✅ **Feature Flags** - Progressive Rollout & A/B Testing
- ✅ **Course Editor** - Manual + AI Editor (aligned mit Backend)

### 🛠️ Tech-Stack

| Technologie | Verwendung |
|------------|-----------|
| ⚡ **Vue.js 3** | Composition API + TypeScript |
| 🚀 **Vite** | Build Tool (Lightning Fast) |
| 📦 **Pinia** | State Management (GBA Stores) |
| 🛣️ **Vue Router** | Routing mit GBA Guards |
| 🎨 **TailwindCSS** | Styling |
| 🌍 **vue-i18n** | Internationalisierung (20 Sprachen) |
| 🎥 **WebRTC** | Video/Audio (LiveRoom) |
| 🔌 **WebSockets** | Real-time Communication |
| 📡 **Axios** | HTTP Client (Interceptors) |
| 🎚️ **Feature Flags** | Progressive Rollout |
| 🛡️ **DOMPurify** | XSS Protection |
| **TypeScript** | Full Type Coverage (100%) |

---

## Content-Lernmethoden & System-Features

### 🎓 Content-Lernmethoden (LM00-LM11)

Das Frontend muss alle **12 Lernmethoden** in 3 Gruppen unterstützen:

| Gruppe | IDs | Anzahl | Fokus | System Features |
|--------|-----|--------|-------|-----------------|
| **A** Erklärend | LM00-LM04 | 5 | Verständnis aufbauen | Whiteboard, Tutor, Video |
| **B** Praxis | LM05-LM08 | 4 | Anwenden & Üben | CodeSandbox, Calculator |
| **C** Prüfung | LM09-LM11 | 3 | Kompetenz nachweisen | Timer, ExamEngine |

**Beispiel-Implementierungen:**
- **LM00 - Text** → Tutor, Highlights
- **LM01 - Video** → Player, Subtitles
- **LM05 - Code** → CodeSandbox, Debugger
- **LM09 - Exam** → Timer, ExamEngine

### 🛠️ System-Features (25 Features)

System Features sind **Tools/Technologien**, die Lernmethoden unterstützen (NICHT die Methoden selbst).

| Kategorie | Features | Beispiel |
|-----------|----------|----------|
| **audio** | Speech-to-Text, TTS | Audio-Ausgabe |
| **collaboration** | LiveRoom, Chat, Whiteboard | Gemeinsames Lernen |
| **exam_systems** | ExamEngine, IHK-Format | Offizielle Tests |
| **gamification** | XP, Badges, Quests | Motivation |
| **interactive_tools** | Calculator, FormulaEditor | Werkzeuge |
| **it_environments** | CodeSandbox, VirtualLab | Praktische Umgebung |
| **learning_paths** | Curriculum, Roadmap | Strukturiertes Lernen |
| **meta_features** | Timer, Bookmarks, Notes | Lern-Unterstützung |
| **tutor** | NPC-Tutor, AI-Tutor | KI-Hilfe |
| **visualization** | 3D-Graphs, Diagrams | Visuelle Erklärungen |

---

## Frontend-Verzeichnisstruktur (DDD Architecture)

```
frontend/
├── src/
│   │
│   ├── presentation/                # 🎨 PRESENTATION LAYER (UI)
│   │   ├── components/              # Vue Components (Feature-Based + Role-Based)
│   │   │   │
│   │   │   ├── admin/               # Admin Features (GBA-protected)
│   │   │   │   ├── ai-operations/   # KI-Operationen
│   │   │   │   │   ├── settings/    # KI-Einstellungen
│   │   │   │   │   ├── learning-methods-management/
│   │   │   │   │   └── system-features-management/
│   │   │   │   ├── content-management/  # Content-Verwaltung
│   │   │   │   │   ├── academy/
│   │   │   │   │   ├── courses/
│   │   │   │   │   └── learning-methods-management/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── feature-flags/
│   │   │   │   ├── groups/          # ✅ Group Management (GBA)
│   │   │   │   ├── translations/
│   │   │   │   └── system-settings/
│   │   │   │
│   │   │   ├── ai/                  # KI-Features
│   │   │   │   ├── admin/           # Admin KI-Studio
│   │   │   │   │   ├── authoring/   # Kurs-Builder, Generation
│   │   │   │   │   ├── management/  # Jobs, Models, Prompts
│   │   │   │   │   ├── settings/
│   │   │   │   │   └── studio/      # AiStudioMain.vue
│   │   │   │   └── user/            # User KI-Features
│   │   │   │       ├── chat/
│   │   │   │       ├── quiz-generation/
│   │   │   │       └── tutor/
│   │   │   │
│   │   │   ├── course-editor/       # ⭐ KURS-EDITOR (Manual + AI)
│   │   │   │   ├── ai-editor/       # KI-gestützte Kurserstellung
│   │   │   │   │   ├── composables/ # useSourceSelection.ts
│   │   │   │   │   ├── steps/       # PDFUploadPanel, SessionSummary
│   │   │   │   │   ├── AIEditorContainer.vue
│   │   │   │   │   ├── ChatInterface.vue
│   │   │   │   │   ├── SourceSelectionContainer.vue
│   │   │   │   │   └── ...
│   │   │   │   ├── manual-editor/   # Manueller Editor
│   │   │   │   │   ├── ManualEditorContainer.vue
│   │   │   │   │   ├── ChapterEditor.vue
│   │   │   │   │   └── LessonEditor.vue
│   │   │   │   ├── content-generation/   # Theorie-Generierung
│   │   │   │   │   ├── composables/
│   │   │   │   │   ├── panels/
│   │   │   │   │   ├── types/
│   │   │   │   │   └── TheoryGenerationContainer.vue
│   │   │   │   ├── explanation-generation/  # Erklärungen
│   │   │   │   │   ├── composables/
│   │   │   │   │   ├── panels/
│   │   │   │   │   ├── types/
│   │   │   │   │   └── ExplanationGenerationContainer.vue
│   │   │   │   ├── shared/          # Gemeinsame Komponenten
│   │   │   │   │   ├── ContentEditor.vue
│   │   │   │   │   ├── MediaUpload.vue
│   │   │   │   │   ├── PreviewPanel.vue
│   │   │   │   │   └── ToolbarActions.vue
│   │   │   │   ├── CourseEditorMain.vue
│   │   │   │   └── EditorSwitcher.vue
│   │   │   │
│   │   │   ├── content/             # Content-Komponenten
│   │   │   │   ├── admin/
│   │   │   │   ├── user/
│   │   │   │   └── shared/
│   │   │   │
│   │   │   ├── base/                # Base UI Components
│   │   │   │   ├── Button.vue, Card.vue, Modal.vue...
│   │   │   │   ├── core/
│   │   │   │   ├── layout/
│   │   │   │   └── learning/
│   │   │   │
│   │   │   ├── compliance/          # GDPR/DSA Compliance
│   │   │   │   ├── CookieConsent.vue
│   │   │   │   ├── AgeGate.vue
│   │   │   │   ├── DataExport.vue
│   │   │   │   └── ...
│   │   │   │
│   │   │   └── ...                  # Weitere Feature-Ordner
│   │   │
│   │   ├── pages/                   # Page Components (Routes)
│   │   │   ├── admin/               # Admin Pages
│   │   │   └── ...
│   │   ├── layouts/                 # Layout Components
│   │   ├── router/                  # Vue Router + GBA Guards
│   │   ├── views/                   # View Components
│   │   ├── App.vue
│   │   └── main.ts
│   │
│   ├── application/                 # 🟡 APPLICATION LAYER (Services & State)
│   │   ├── services/
│   │   │   └── api/                 # API Services
│   │   ├── stores/                  # Pinia Stores
│   │   │   ├── modules/
│   │   │   ├── auth.store.ts
│   │   │   ├── groups.store.ts      # ✅ Group State (replaced roles.store.ts)
│   │   │   └── ...
│   │   └── composables/             # Shared Composables
│   │       ├── useAccessControl.ts
│   │       ├── useGroupTier.ts
│   │       └── ...
│   │
│   ├── domain/                      # 🟢 DOMAIN LAYER (Business Logic)
│   │   ├── models/                  # Domain Models
│   │   │   ├── admin/
│   │   │   ├── content/
│   │   │   ├── course/
│   │   │   ├── course-editor/       # ✅ Course Editor Models
│   │   │   ├── social/
│   │   │   └── user/
│   │   ├── factories/               # Factory Pattern
│   │   │   ├── admin/
│   │   │   ├── content/
│   │   │   ├── course-editor/       # ✅ Course Editor Factories
│   │   │   └── ...
│   │   ├── value-objects/           # Email.vo.ts, etc.
│   │   ├── events/                  # Domain Events
│   │   ├── widgets/                 # Widget Definitions
│   │   └── learning-methods/        # LM Configurations
│   │
│   ├── infrastructure/              # 🔵 INFRASTRUCTURE LAYER (External Services)
│   │   ├── api/                     # API Clients
│   │   │   ├── clients/
│   │   │   ├── admin/
│   │   │   ├── config/
│   │   │   └── utils/
│   │   ├── websocket/               # WebSocket Clients
│   │   ├── cache/                   # Local Caching
│   │   ├── i18n/                    # Internationalization
│   │   └── repositories/            # Data Repositories
│   │
│   └── shared/                      # Shared Resources
│       ├── assets/
│       ├── utils/
│       └── docs/
│
├── public/                          # Static Assets
├── Dockerfile                       # Docker Configuration
├── docker-compose.yml
├── package.json
└── vite.config.ts
```

---

## GBA-Authentifizierung im Frontend

### 🔐 GBA Store (Pinia)

```typescript
// src/application/stores/auth.store.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Group {
  id: number
  name: string
  slug: string
  type: 'system' | 'organisation' | 'custom'
  permissions: string[]  // e.g., ['admin:system', 'manage:courses']
}

interface User {
  user_id: string
  email: string
  name: string
  organisation_id: string
  groups: Group[]        // ✅ GBA: User has multiple groups
  iat: number
  exp: number
}

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)

  // ✅ GBA: Get all user's effective permissions
  const effectivePermissions = computed(() => {
    if (!currentUser.value) return []
    const perms = new Set<string>()
    currentUser.value.groups.forEach(group => {
      group.permissions.forEach(perm => perms.add(perm))
    })
    return Array.from(perms)
  })

  // ✅ GBA: Check if user has specific permission
  const hasPermission = (permission: string): boolean => {
    return effectivePermissions.value.includes(permission)
  }

  // ✅ GBA: Check if user is system admin
  const isSystemAdmin = computed(() => {
    return currentUser.value?.groups?.some(g => g.slug === 'system_admin') ?? false
  })

  const isOrgAdmin = computed(() => {
    return currentUser.value?.groups?.some(g =>
      g.slug === 'org_admin' || g.slug === 'system_admin'
    ) ?? false
  })

  // Login
  const login = async (email: string, password: string) => {
    isLoading.value = true
    try {
      const response = await authService.login(email, password)
      token.value = response.access_token
      // Decode JWT to get user data with groups
      currentUser.value = decodeJWT(response.access_token)
      localStorage.setItem('token', response.access_token)
    } finally {
      isLoading.value = false
    }
  }

  return {
    currentUser,
    token,
    isLoading,
    effectivePermissions,
    hasPermission,
    isSystemAdmin,
    isOrgAdmin,
    login
  }
})
```

---

## Admin Panel Architecture (GBA-Protected)

### 📊 Admin Panel Overview

Das **Admin Panel** ist eine **System Administration Interface** unter `/admin` für System Admins (GBA-geschützt durch `admin:system` Permission).

**Wichtige Eigenschaften:**
- ✅ **GBA-Guard**: Nur Benutzer mit `admin:system` Permission
- ✅ **12 Main Sections**: Users, Groups, Organisations, Courses, Categories, AI Studio, Translations, Billing, Analytics, Audit Logs, LM Routing, System Settings
- ✅ **Backend Aligned**: Mirrors Backend API structure (`/api/v1/admin-panel/*`)
- ✅ **Groups Management**: Verwaltung von Gruppen, Permissions, Member Assignment

### Admin Panel Routes (mit GBA Guard)

```typescript
// src/presentation/router/index.ts

{
  path: '/admin',
  component: () => import('@/presentation/layouts/AdminLayout.vue'),
  meta: {
    requiresAuth: true,
    requiresPermission: 'admin:system'  // ✅ GBA: Requires admin:system
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
      path: 'groups',                                              // ✅ Changed from 'roles'
      name: 'AdminGroups',
      component: () => import('@/presentation/pages/admin/AdminGroupsPage.vue'),
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

### Admin Panel Services (GBA-Aligned)

```typescript
// src/application/services/admin/

├── UserAdminService.ts                     # User CRUD
├── GroupManagementService.ts               # ✅ Group CRUD + Permission Management (replaced RoleAdminService)
├── OrganisationService.ts
├── CourseAdminService.ts
├── CategoryService.ts
├── AIStudioService.ts
├── TranslationService.ts
├── BillingService.ts
├── AnalyticsService.ts
├── AuditLogService.ts
├── LMRoutingService.ts
└── SystemSettingsService.ts
```

### GroupManagementService (NEW - Replaces RoleAdminService)

```typescript
// src/application/services/admin/GroupManagementService.ts

import { groupsClient } from '@/infrastructure/api/clients/groups.client'

export class GroupManagementService {
  // ✅ Create new group
  async createGroup(name: string, type: 'system' | 'organisation', description: string) {
    return await groupsClient.post('/admin-panel/groups', {
      name,
      type,
      description
    })
  }

  // ✅ Update group (name, description, active status)
  async updateGroup(groupId: number, data: any) {
    return await groupsClient.put(`/admin-panel/groups/${groupId}`, data)
  }

  // ✅ Delete group
  async deleteGroup(groupId: number) {
    return await groupsClient.delete(`/admin-panel/groups/${groupId}`)
  }

  // ✅ Add member to group
  async addGroupMember(groupId: number, userId: string, memberRole: string) {
    return await groupsClient.post(`/admin-panel/groups/${groupId}/members`, {
      user_id: userId,
      member_role: memberRole  // owner, moderator, member
    })
  }

  // ✅ Remove member from group
  async removeGroupMember(groupId: number, userId: string) {
    return await groupsClient.delete(`/admin-panel/groups/${groupId}/members/${userId}`)
  }

  // ✅ Assign permissions to group
  async assignPermissions(groupId: number, permissionCodes: string[]) {
    return await groupsClient.put(`/admin-panel/groups/${groupId}/permissions`, {
      permission_codes: permissionCodes
    })
  }

  // ✅ Get group members
  async getGroupMembers(groupId: number) {
    return await groupsClient.get(`/admin-panel/groups/${groupId}/members`)
  }

  // ✅ Get group permissions
  async getGroupPermissions(groupId: number) {
    return await groupsClient.get(`/admin-panel/groups/${groupId}/permissions`)
  }
}
```

### Admin Panel Stores (Pinia)

```typescript
// src/application/stores/modules/admin/

├── adminDashboard.store.ts
├── users.store.ts
├── groups.store.ts                         # ✅ Group state management (replaced roles.store.ts)
├── organisations.store.ts
├── courses.store.ts
├── categories.store.ts
├── aiStudio.store.ts
├── translations.store.ts
├── billing.store.ts
├── analytics.store.ts
├── auditLogs.store.ts
├── lmRouting.store.ts
└── systemSettings.store.ts
```

### groups.store.ts (NEW - Replaces roles.store.ts)

```typescript
// src/application/stores/modules/admin/groups.store.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { GroupManagementService } from '@/application/services/admin/GroupManagementService'

interface Group {
  id: number
  name: string
  slug: string
  type: 'system' | 'organisation' | 'custom'
  is_active: boolean
  member_count: number
  permissions: string[]
}

export const useGroupsStore = defineStore('admin/groups', () => {
  const service = new GroupManagementService()

  const groups = ref<Group[]>([])
  const selectedGroup = ref<Group | null>(null)
  const isLoading = ref(false)

  const fetchGroups = async () => {
    isLoading.value = true
    try {
      groups.value = await service.getGroups()
    } finally {
      isLoading.value = false
    }
  }

  const createGroup = async (name: string, type: string, description: string) => {
    const newGroup = await service.createGroup(name, type, description)
    groups.value.push(newGroup)
    return newGroup
  }

  const updateGroup = async (groupId: number, data: any) => {
    const updated = await service.updateGroup(groupId, data)
    const index = groups.value.findIndex(g => g.id === groupId)
    if (index !== -1) {
      groups.value[index] = updated
    }
    return updated
  }

  const deleteGroup = async (groupId: number) => {
    await service.deleteGroup(groupId)
    groups.value = groups.value.filter(g => g.id !== groupId)
  }

  const assignPermissions = async (groupId: number, permissionCodes: string[]) => {
    return await service.assignPermissions(groupId, permissionCodes)
  }

  return {
    groups,
    selectedGroup,
    isLoading,
    fetchGroups,
    createGroup,
    updateGroup,
    deleteGroup,
    assignPermissions
  }
})
```

### Admin Layout (mit GBA Menu)

```vue
<!-- src/presentation/layouts/AdminLayout.vue -->

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/application/stores/auth.store'

const { t } = useI18n()
const authStore = useAuthStore()

// ✅ 12 Admin menu items (Groups instead of Roles)
const menuItems = computed(() => [
  { path: '/admin', label: t('admin.nav.dashboard'), icon: '📊' },
  { path: '/admin/users', label: t('admin.nav.users'), icon: '👥' },
  { path: '/admin/groups', label: t('admin.nav.groups'), icon: '👫' },        // ✅ Changed from roles
  { path: '/admin/organisations', label: t('admin.nav.organisations'), icon: '🏢' },
  { path: '/admin/kurs-editor', label: t('admin.nav.courseEditor'), icon: '📝' },
  { path: '/admin/categories', label: t('admin.nav.categories'), icon: '📁' },
  { path: '/admin/ai-studio', label: t('admin.nav.aiStudio'), icon: '🤖' },
  { path: '/admin/translations', label: t('admin.nav.translations'), icon: '🌐' },
  { path: '/admin/billing', label: t('admin.nav.billing'), icon: '💰' },
  { path: '/admin/analytics', label: t('admin.nav.analytics'), icon: '📈' },
  { path: '/admin/audit-logs', label: t('admin.nav.auditLogs'), icon: '📋' },
  { path: '/admin/system-settings', label: t('admin.nav.settings'), icon: '⚙️' }
])
</script>

<template>
  <div class="admin-layout flex h-screen overflow-hidden bg-[var(--color-bg)]">
    <!-- Sidebar Navigation -->
    <aside class="w-72 bg-[var(--color-surface)] border-r border-[var(--color-border)]">
      <!-- Logo -->
      <div class="p-5 border-b">
        <h1 class="text-lg font-bold">LSX Admin</h1>
        <p class="text-sm text-secondary">{{ t('admin.system_admin') }}</p>
      </div>

      <!-- Navigation Menu -->
      <nav class="flex-1 overflow-y-auto p-5">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-base font-medium transition-colors"
        >
          <span class="text-xl">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-6 py-4">
        <h2 class="text-2xl font-bold">{{ $t(`admin.nav.${$route.name?.toLowerCase()}`) }}</h2>
      </header>
      <div class="flex-1 overflow-auto p-6">
        <router-view />
      </div>
    </main>
  </div>
</template>
```

---

## GBA Permission Guards (Router)

```typescript
// src/router/gba-guards.ts

import { useAuthStore } from '@/application/stores/auth.store'

export const requirePermission = (permission: string) => {
  return (to: RouteLocationNormalized, from: any, next: any) => {
    const authStore = useAuthStore()

    if (!authStore.hasPermission(permission)) {
      console.warn(`Access denied: requires ${permission}`)
      next({ name: 'Dashboard' })
      return
    }

    next()
  }
}

// Usage in router
{
  path: '/admin',
  meta: {
    requiresPermission: 'admin:system'  // ✅ GBA: Check permission
  },
  beforeEnter: requirePermission('admin:system')
}
```

---

## i18n Keys für Admin Panel

```json
// src/locales/de.json (excerpt)

{
  "admin": {
    "nav": {
      "dashboard": "Dashboard",
      "users": "Benutzer",
      "groups": "Gruppen",              // ✅ Changed from "roles": "Rollen"
      "organisations": "Organisationen",
      "courseEditor": "Kurs-Editor",
      "categories": "Kategorien",
      "aiStudio": "KI-Studio",
      "translations": "Übersetzungen",
      "billing": "Abrechnung",
      "analytics": "Analytics",
      "auditLogs": "Audit-Logs",
      "settings": "Einstellungen"
    },
    "groups": {                         // ✅ New section for groups
      "title": "Gruppenverwaltung",
      "create": "Gruppe erstellen",
      "edit": "Gruppe bearbeiten",
      "delete": "Gruppe löschen",
      "permissions": "Berechtigungen",
      "members": "Mitglieder",
      "memberRole": "Mitgliederrolle"
    }
  }
}
```

---

## Composables für GBA

```typescript
// src/application/composables/useGroupsStore.ts (replaces useRolesStore)

import { useGroupsStore as useStore } from '@/application/stores/modules/admin/groups.store'

export const useGroupsStore = () => {
  const groupsStore = useStore()

  const addGroupMember = async (groupId: number, userId: string, role: string) => {
    return await groupsStore.addGroupMember(groupId, userId, role)
  }

  const removeGroupMember = async (groupId: number, userId: string) => {
    return await groupsStore.removeGroupMember(groupId, userId)
  }

  const updateGroupPermissions = async (groupId: number, permissions: string[]) => {
    return await groupsStore.assignPermissions(groupId, permissions)
  }

  return {
    groups: groupsStore.groups,
    selectedGroup: groupsStore.selectedGroup,
    isLoading: groupsStore.isLoading,
    addGroupMember,
    removeGroupMember,
    updateGroupPermissions
  }
}
```

---

## Course Editor Domain (Aligned mit Backend)

Der **Course Editor** ist ein **Feature-Domain Component** mit zwei Modi:

### 🎯 Editor-Modi

| Modus | Komponente | Backend API |
|-------|------------|-------------|
| **AI Editor** | `ai-editor/` | `/api/v1/course_editor/ai_editor/` |
| **Manual Editor** | `manual-editor/` | `/api/v1/course_editor/manual_editor/` |

### 📁 Frontend Struktur

```
src/presentation/components/course-editor/
├── ai-editor/                    # KI-gestützte Kurserstellung
│   ├── composables/              # useSourceSelection.ts
│   ├── steps/                    # Wizard Steps
│   │   ├── PDFUploadPanel.vue    # PDF-Upload für Source
│   │   ├── SessionSummaryPanel.vue
│   │   └── SourceTypeSelector.vue
│   ├── AIEditorContainer.vue     # Haupt-Container
│   ├── ChatInterface.vue         # KI-Chat
│   ├── SourceSelectionContainer.vue
│   └── ...
│
├── manual-editor/                # Manueller Editor
│   ├── ManualEditorContainer.vue # Haupt-Container
│   ├── ChapterEditor.vue
│   └── LessonEditor.vue
│
├── content-generation/           # Theorie-Generierung
│   ├── composables/useTheoryGeneration.ts
│   ├── panels/
│   │   ├── TheoryGenerationDetailPanel.vue
│   │   ├── TheoryGenerationListPanel.vue
│   │   └── TheoryGenerationSettingsPanel.vue
│   ├── types/theory.types.ts
│   └── TheoryGenerationContainer.vue
│
├── explanation-generation/       # Erklärungen-Generierung
│   ├── composables/useExplanationGeneration.ts
│   ├── panels/
│   └── ExplanationGenerationContainer.vue
│
├── shared/                       # Gemeinsame Komponenten
│   ├── ContentEditor.vue
│   ├── MediaUpload.vue
│   ├── PreviewPanel.vue
│   ├── StructurePanel.vue
│   └── ToolbarActions.vue
│
├── CourseEditorMain.vue          # Haupt-Entry Point
├── EditorSwitcher.vue            # Modus-Umschalter (AI/Manual)
└── index.ts                      # Barrel Export
```

### 🔗 Backend API Alignment

| Frontend | Backend |
|----------|---------|
| `ai-editor/AIEditorContainer.vue` | `/api/v1/course_editor/ai_editor/authoring.py` |
| `manual-editor/ChapterEditor.vue` | `/api/v1/course_editor/manual_editor/chapters.py` |
| `manual-editor/LessonEditor.vue` | `/api/v1/course_editor/manual_editor/lessons.py` |
| `content-generation/` | `/api/v1/course_editor/ai_editor/actions.py` |
| `shared/` | `/api/v1/course_editor/shared/` |

### 🛣️ Routing

```typescript
// Editor Routes
{
  path: '/editor',                   // Creator Access
  component: () => import('@/presentation/components/course-editor/CourseEditorMain.vue'),
  meta: { requiresPermission: 'manage:courses' }
},
{
  path: '/admin/kurs-editor',        // Admin Access
  component: () => import('@/presentation/components/course-editor/CourseEditorMain.vue'),
  meta: { requiresPermission: 'admin:system' }
}
```

---

## Zusammenfassung GBA-Migration

### ✅ Abgeschlossene Änderungen

- ✅ **Admin Routes:** Umgestellt von `/admin/roles` zu `/admin/groups`
- ✅ **Services:** `RoleAdminService` → `GroupManagementService`
- ✅ **Stores:** `roles.store.ts` → `groups.store.ts`
- ✅ **Composables:** `useRolesStore()` → `useGroupsStore()`
- ✅ **Components:** All role-related components → group-based equivalents
- ✅ **Router Guards:** GBA-basiert via `requiresPermission` Meta
- ✅ **i18n:** Admin menu updated (groups statt roles)

### ✅ GBA-Features

- ✅ **Permission-basierte Autorisierung** - Feingranulare Kontrolle
- ✅ **Multiple Groups per User** - Flexible Permissions
- ✅ **Permission Codes** - admin:system, manage:courses, view:analytics, etc.
- ✅ **Effective Permissions** - Computed aus allen User-Gruppen
- ✅ **GBA Interceptor** - Automatische Permission-Prüfung bei API Calls
- ✅ **Router Guards** - Automatische Permission-Prüfung bei Navigation

---

**Stand:** 2026-01-29 | **Version:** 2.1 (DDD + Course Editor) | **Status:** Production Ready
