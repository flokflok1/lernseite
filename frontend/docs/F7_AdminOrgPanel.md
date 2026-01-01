# Frontend Phase F7 – Admin- & Organisations-Panel

**Status:** ✅ Abgeschlossen (V1 - Grundstruktur)
**Ziel:** Zweistufige Administrationsoberfläche für System-Admins und Organisations-Admins

---

## 1. Übersicht

Phase F7 implementiert eine vollständige Admin- und Organisations-Verwaltungsoberfläche mit:

- **Globales Admin-Panel** für System-Admins (Admin, Superadmin)
- **Organisations-Panel** für Org-Admins (School Admin, Company Admin)
- **Rollenbasierte Zugriffskontrolle** über Router Guards
- **Dediziertes Admin-Layout** mit Sidebar-Navigation
- **API-Layer** für Admin- und Org-Operationen
- **Pinia Stores** für State Management

---

## 2. Architektur

### 2.1 Rollen-Hierarchie

```
System Admin (Admin, Superadmin)
├── Zugriff auf: /admin/*
├── Funktionen:
│   ├── User Management (alle User)
│   ├── Organisation Management (alle Orgs)
│   ├── Course Management (alle Kurse)
│   ├── Billing & Tokens
│   └── System Analytics
│
Organisation Admin (School Admin, Company Admin)
├── Zugriff auf: /org/*
├── Funktionen:
│   ├── Member Management (nur eigene Org)
│   ├── Course Assignments (nur eigene Org)
│   ├── Org Analytics
│   └── Org Settings
```

### 2.2 Komponenten-Struktur

```
AdminLayout.vue
├── Sidebar (Navigation)
│   ├── Logo & Titel
│   ├── Menu Items (dynamisch je nach Rolle)
│   └── User Section (Profil, Logout)
├── TopBar (Header)
│   ├── Page Title & Subtitle
│   └── Header Actions Slot
└── Content Area
    └── <router-view> (Admin/Org Pages)
```

---

## 3. Neue Dateien

### 3.1 API Layer

**`frontend/src/api/admin.api.ts`** (380 Zeilen)
- TypeScript Interfaces:
  - `AdminUser`, `AdminOrganisation`, `AdminCourse`
  - `AdminSystemStats`, `AdminTokenStats`, `AdminPlanOverview`
  - `PaginatedResponse<T>` für Listen mit Pagination
- Admin API Funktionen:
  - User Management: `adminGetUsers()`, `adminUpdateUserRole()`, `adminToggleUserActive()`, `adminDeleteUser()`
  - Organisation Management: `adminGetOrganisations()`, `adminUpdateOrganisationPlan()`, `adminAddOrganisationTokens()`
  - Course Management: `adminGetCourses()`, `adminPublishCourse()`, `adminArchiveCourse()`, `adminDeleteCourse()`
  - Billing: `adminGetGlobalTokenStats()`, `adminGetPlanOverview()`
  - Analytics: `adminGetSystemStats()`, `adminGetActiveUsers()`

**`frontend/src/api/orgAdmin.api.ts`** (290 Zeilen)
- TypeScript Interfaces:
  - `OrgDetail`, `OrgMember`, `OrgCourse`
  - `OrgAnalyticsOverview`, `OrgInviteRequest`, `OrgSettings`
- Org Admin API Funktionen:
  - Organisation: `getOrganisationDetail()`, `updateOrganisationSettings()`
  - Members: `getOrganisationMembers()`, `inviteUserToOrganisation()`, `removeUserFromOrganisation()`, `updateOrganisationUserRole()`
  - Courses: `getOrganisationCourses()`, `assignCourseToMembers()`, `unassignCourseFromMembers()`
  - Analytics: `getOrganisationAnalytics()`, `getOrganisationTokenUsage()`, `getOrganisationMemberProgress()`

### 3.2 Stores

**`frontend/src/store/admin.store.ts`** (420 Zeilen)
- State:
  - Users: `users`, `usersTotal`, `usersPage`, `userFilters`
  - Organisations: `organisations`, `orgsTotal`, `orgsPage`, `orgFilters`
  - Courses: `courses`, `coursesTotal`, `coursesPage`, `courseFilters`
  - System: `systemStats`, `tokenStats`, `plans`
- Getters:
  - `hasSystemStats`, `totalUsersCount`, `activeUsersCount`, `totalOrgsCount`, `totalCoursesCount`
- Actions:
  - Dashboard: `loadAdminDashboard()`
  - Users: `loadUsers()`, `updateUserRole()`, `toggleUserActive()`, `deleteUser()`
  - Organisations: `loadOrganisations()`, `updateOrganisationPlan()`, `addOrganisationTokens()`
  - Courses: `loadCourses()`, `publishCourse()`, `unpublishCourse()`, `archiveCourse()`, `deleteCourse()`
  - Billing: `loadPlans()`

**`frontend/src/store/orgAdmin.store.ts`** (330 Zeilen)
- State:
  - Organisation: `organisation`, `orgStats`
  - Members: `members`, `membersTotal`, `membersPage`
  - Courses: `orgCourses`, `orgCoursesTotal`, `orgCoursesPage`
- Getters:
  - `hasOrg`, `orgName`, `orgType`, `memberCount`, `activeMembersCount`
  - `orgCourseCount`, `tokenAvailable`, `tokenUsed`, `tokenUsagePercentage`, `orgCompletionRate`
- Actions:
  - Organisation: `loadOrgDashboard()`, `updateOrgSettings()`
  - Members: `loadOrgMembers()`, `inviteMember()`, `removeMember()`, `updateMemberRole()`
  - Courses: `loadOrgCourses()`, `assignCourseToMembers()`, `unassignCourseFromMembers()`
  - Analytics: `loadOrgAnalytics()`

### 3.3 Layout

**`frontend/src/layouts/AdminLayout.vue`** (170 Zeilen)
- Props:
  - `pageTitle`, `pageSubtitle`, `isOrgAdmin`
- Features:
  - Dynamische Sidebar-Navigation (Admin vs. Org)
  - User-Section mit Profil & Logout
  - TopBar mit Title & Actions Slot
  - Responsive Design
- Verwendung:
  ```vue
  <AdminLayout page-title="Dashboard" page-subtitle="System Übersicht">
    <template #header-actions>
      <button>Aktion</button>
    </template>
    <!-- Page Content -->
  </AdminLayout>
  ```

### 3.4 Pages

#### Admin Pages (`frontend/src/pages/admin/`)

1. **AdminDashboardPage.vue** (vollständig implementiert)
   - System-Statistiken (User, Orgs, Courses, Premium)
   - Token-Stats (verfügbar, verbraucht, 30-Tage-Verbrauch)
   - Quick Actions (Links zu Users, Orgs, Courses)

2. **AdminUsersPage.vue** (vollständig implementiert)
   - User-Tabelle mit Pagination
   - Filter: Suche (Name/Email), Rolle, Status
   - Aktionen: Status togglen (sperren/aktivieren)
   - Rolle-Badges mit Farbcodierung

3. **AdminOrganisationsPage.vue** (Platzhalter)
4. **AdminCoursesPage.vue** (Platzhalter)
5. **AdminBillingPage.vue** (Platzhalter)
6. **AdminAnalyticsPage.vue** (Platzhalter)

#### Org Pages (`frontend/src/pages/org/`)

1. **OrgDashboardPage.vue** (vollständig implementiert)
   - Org-Statistiken (Mitglieder, Kurse, Token, Completion Rate)
   - Quick Actions (Links zu Users, Courses, Analytics)

2. **OrgUsersPage.vue** (Platzhalter)
3. **OrgCoursesPage.vue** (Platzhalter)
4. **OrgAnalyticsPage.vue** (Platzhalter)
5. **OrgSettingsPage.vue** (Platzhalter)

### 3.5 Routing

**`frontend/src/router/index.ts`** (erweitert)
- Admin Routes (`/admin`):
  - Layout: `AdminLayout.vue`
  - Meta: `requiresAuth: true`, `requiresSystemAdmin: true`
  - Children: Dashboard, Users, Organisations, Courses, Billing, Analytics

- Org Routes (`/org`):
  - Layout: `AdminLayout.vue`
  - Meta: `requiresAuth: true`, `requiresOrgAdmin: true`
  - Children: Dashboard, Users, Courses, Analytics, Settings

- Router Guards:
  - `requiresSystemAdmin`: Prüft `authStore.isSystemAdmin`
  - `requiresOrgAdmin`: Prüft `authStore.isOrgAdmin`
  - Bei unzureichender Rolle: Redirect zu `/dashboard`

---

## 4. Modifizierte Dateien

**`frontend/src/store/auth.store.ts`**
- Neue Getter:
  - `isSystemAdmin` (prüft Admin, Superadmin)
  - `currentOrganisationId` (Organisation des Users)
- Return erweitert um neue Getter

---

## 5. Datenflüsse

### 5.1 Admin Dashboard Flow

```
AdminDashboardPage
└─> onMounted()
    └─> adminStore.loadAdminDashboard()
        └─> adminApi.adminGetSystemStats()
            └─> GET /admin/analytics/system
            └─> Response: AdminSystemStats
                ├─> total_users, active_users_7_days, new_users_7_days
                ├─> total_organisations, total_courses, published_courses
                ├─> premium_subscriptions, total_enrollments
                └─> token_stats (TokenStats)
        └─> Store: systemStats, tokenStats gesetzt
    └─> UI: Stats Cards rendered
```

### 5.2 Admin Users Flow

```
AdminUsersPage
└─> onMounted()
    └─> loadUsers()
        └─> adminStore.loadUsers({ search, role, status, page })
            └─> adminApi.adminGetUsers(params)
                └─> GET /admin/users?search=...&role=...&page=...
                └─> Response: PaginatedResponse<AdminUser>
            └─> Store: users[], usersTotal, usersPage gesetzt
        └─> UI: Tabelle rendered, Pagination

User-Aktion: Status Toggle
└─> toggleUserStatus(user)
    └─> Confirm Dialog
    └─> adminStore.toggleUserActive(userId)
        └─> adminApi.adminToggleUserActive(userId, newStatus)
            └─> PATCH /admin/users/{userId}/status
        └─> Store: user.is_active aktualisiert
    └─> UI: Status Badge updated
```

### 5.3 Org Dashboard Flow

```
OrgDashboardPage
└─> onMounted()
    └─> authStore.currentOrganisationId
    └─> orgAdminStore.loadOrgDashboard(orgId)
        └─> Promise.all([
            orgAdminApi.getOrganisationDetail(orgId)
                └─> GET /organisations/{orgId}
            orgAdminApi.getOrganisationAnalytics(orgId)
                └─> GET /organisations/{orgId}/analytics
        ])
        └─> Store: organisation, orgStats gesetzt
    └─> UI: Stats Cards (Members, Courses, Tokens, Completion)
```

---

## 6. TypeScript Interfaces

### 6.1 Admin Interfaces

```typescript
interface AdminUser {
  user_id: number
  email: string
  first_name: string
  last_name: string
  role: string
  organisation_id?: number | null
  organisation_name?: string | null
  is_active: boolean
  created_at: string
  last_login?: string | null
  token_balance?: number
}

interface AdminOrganisation {
  organisation_id: number
  name: string
  type: 'school' | 'company' | 'teacher_team' | 'creator_team'
  plan_id?: string | null
  plan_name?: string
  active_users: number
  total_users: number
  token_pool: number
  token_used: number
  created_at: string
  is_active: boolean
  domain?: string | null
}

interface AdminSystemStats {
  total_users: number
  active_users_7_days: number
  active_users_30_days: number
  new_users_7_days: number
  total_organisations: number
  total_courses: number
  published_courses: number
  total_lessons: number
  total_enrollments: number
  premium_subscriptions: number
  revenue_30_days?: number
  token_stats: AdminTokenStats
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  total_pages: number
}
```

### 6.2 Org Interfaces

```typescript
interface OrgDetail {
  organisation_id: number
  name: string
  type: 'school' | 'company' | 'teacher_team' | 'creator_team'
  plan_id?: string | null
  token_pool: number
  token_used: number
  token_available: number
  total_users: number
  active_users: number
  created_at: string
  is_active: boolean
  branding?: {
    logo_url?: string
    primary_color?: string
    secondary_color?: string
  }
}

interface OrgMember {
  user_id: number
  email: string
  first_name: string
  last_name: string
  role: string
  org_role?: string
  is_active: boolean
  joined_at: string
  last_active?: string | null
  token_usage?: number
  assigned_courses?: number
}

interface OrgAnalyticsOverview {
  total_members: number
  active_members_7_days: number
  active_members_30_days: number
  total_assigned_courses: number
  avg_completion_rate: number
  token_used_7_days: number
  token_used_30_days: number
  top_courses?: Array<{...}>
  top_users?: Array<{...}>
}
```

---

## 7. Router Guards & Zugriffskontrolle

### 7.1 Meta-Tags

```typescript
// Admin Route
{
  path: '/admin',
  meta: {
    requiresAuth: true,
    requiresSystemAdmin: true
  }
}

// Org Route
{
  path: '/org',
  meta: {
    requiresAuth: true,
    requiresOrgAdmin: true
  }
}
```

### 7.2 Guard Logic

```typescript
router.beforeEach((to, _from, next) => {
  // ... Auth-Check ...

  // System Admin Check
  if (to.meta.requiresSystemAdmin && !authStore.isSystemAdmin) {
    console.warn('Access denied: System Admin required')
    next({ name: 'Dashboard' })
    return
  }

  // Org Admin Check
  if (to.meta.requiresOrgAdmin && !authStore.isOrgAdmin) {
    console.warn('Access denied: Organisation Admin required')
    next({ name: 'Dashboard' })
    return
  }

  next()
})
```

---

## 8. UX-Patterns

### 8.1 Loading States

```vue
<div v-if="adminStore.loading" class="flex justify-center items-center py-12">
  <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
</div>
```

### 8.2 Error States

```vue
<div v-if="adminStore.error" class="bg-red-50 border border-red-200 rounded-lg p-4">
  <p class="text-red-700">{{ adminStore.error }}</p>
</div>
```

### 8.3 Empty States

```vue
<div v-if="adminStore.users.length === 0" class="p-8 text-center text-gray-500">
  Keine Benutzer gefunden
</div>
```

### 8.4 Confirmation Dialogs

```typescript
const deleteUser = async (user: AdminUser) => {
  if (confirm(`Möchten Sie ${user.first_name} ${user.last_name} wirklich löschen?`)) {
    await adminStore.deleteUser(user.user_id)
  }
}
```

---

## 9. Erweiterungspunkte

### 9.1 Admin Pages (noch zu implementieren)

1. **AdminOrganisationsPage**:
   - Organisations-Tabelle mit Pagination
   - Filter: Typ, Plan, Status
   - Aktionen: Plan ändern, Tokens hinzufügen, Details anzeigen

2. **AdminCoursesPage**:
   - Kurs-Tabelle mit Pagination
   - Filter: Status, Creator, Kategorie
   - Aktionen: Publish/Unpublish, Archive, Delete

3. **AdminBillingPage**:
   - Pläne-Übersicht (Free, Premium, Org, Creator)
   - Subscriber-Count pro Plan
   - Revenue-Statistiken

4. **AdminAnalyticsPage**:
   - Charts für aktive User (7/30 Tage)
   - Top Courses (Enrollments, Completions)
   - Event-Logs (Analytics-Events)

### 9.2 Org Pages (noch zu implementieren)

1. **OrgUsersPage**:
   - Member-Tabelle mit Pagination
   - Filter: Rolle, Status
   - Aktionen: Einladen, Entfernen, Rolle ändern

2. **OrgCoursesPage**:
   - Kurs-Liste
   - Multi-Select für Member-Zuweisung
   - Fortschritts-Übersicht pro Kurs

3. **OrgAnalyticsPage**:
   - Aktive Mitglieder (7/30 Tage)
   - Kurs-Completion-Rate
   - Top Performers

4. **OrgSettingsPage**:
   - Name, Branding (Logo, Farben)
   - Domain-Einstellungen
   - Default-Layouts

### 9.3 Features (Zukunft)

- **Bulk-Operations**: Multi-Select + Bulk-Actions (z.B. mehrere User sperren)
- **Export**: CSV/Excel-Export von Tabellen
- **Advanced Filters**: Datumsbereich, Custom-Fields
- **Charts & Visualisierung**: Chart.js / Recharts Integration
- **Real-Time Updates**: WebSocket für Live-Stats
- **Audit Logs**: Admin-Aktionen protokollieren
- **Email-Templates**: Einladungs-/Benachrichtigungs-Templates

---

## 10. Backend-Abhängigkeiten

Die Frontend-Implementierung erwartet folgende Backend-Endpoints:

### Admin Endpoints
- `GET /admin/analytics/system` → SystemStats
- `GET /admin/users` → PaginatedResponse<AdminUser>
- `PATCH /admin/users/{id}/role` → Update Role
- `PATCH /admin/users/{id}/status` → Toggle Active
- `DELETE /admin/users/{id}` → Delete User
- `GET /admin/organisations` → PaginatedResponse<AdminOrganisation>
- `PATCH /admin/organisations/{id}/plan` → Update Plan
- `POST /admin/organisations/{id}/tokens` → Add Tokens
- `GET /admin/courses` → PaginatedResponse<AdminCourse>
- `POST /admin/courses/{id}/publish` → Publish Course
- `POST /admin/courses/{id}/archive` → Archive Course
- `GET /admin/tokens/stats` → TokenStats
- `GET /admin/billing/plans` → PlanOverview[]

### Org Endpoints
- `GET /organisations/{id}` → OrgDetail
- `PATCH /organisations/{id}/settings` → Update Settings
- `GET /organisations/{id}/members` → PaginatedResponse<OrgMember>
- `POST /organisations/{id}/members/invite` → Invite Member
- `DELETE /organisations/{id}/members/{userId}` → Remove Member
- `PATCH /organisations/{id}/members/{userId}/role` → Update Role
- `GET /organisations/{id}/courses` → PaginatedResponse<OrgCourse>
- `POST /organisations/{id}/courses/assign` → Assign Course
- `GET /organisations/{id}/analytics` → OrgAnalyticsOverview
- `GET /organisations/{id}/tokens/usage` → TokenUsage

---

## 11. Testing-Checkliste

### Funktionale Tests

- [ ] **Admin Dashboard**: Stats laden, Token-Stats anzeigen
- [ ] **Admin Users**: Tabelle laden, Filter anwenden, User sperren/aktivieren
- [ ] **Admin Routing**: Guards blockieren non-Admin User
- [ ] **Org Dashboard**: Org-Stats laden (nur für Org-Admin)
- [ ] **Org Routing**: Guards blockieren non-Org-Admin User
- [ ] **Rolle-Switch**: Admin kann sowohl /admin als auch /org nutzen (falls Org-Admin)

### Edge Cases

- [ ] User ohne Organisation versucht /org zu betreten
- [ ] Non-Admin User versucht /admin zu betreten (Redirect)
- [ ] Backend-Fehler bei API-Call (Error-State anzeigen)
- [ ] Leere Listen (Empty-State anzeigen)
- [ ] Pagination bei vielen Einträgen

### UI/UX Tests

- [ ] Loading-States bei allen API-Calls
- [ ] Error-States bei Fehlern
- [ ] Empty-States bei leeren Listen
- [ ] Responsive Design (Mobile, Tablet, Desktop)
- [ ] Sidebar-Navigation aktiv-State
- [ ] Confirmation Dialogs bei kritischen Aktionen

---

## 12. Zusammenfassung

### ✅ Implementiert (V1)

- **API-Layer**: admin.api.ts, orgAdmin.api.ts (vollständig)
- **Stores**: admin.store.ts, orgAdmin.store.ts (vollständig)
- **Layout**: AdminLayout.vue (vollständig)
- **Routing**: Admin + Org Routes mit Guards (vollständig)
- **Auth Store**: isSystemAdmin, currentOrganisationId Getter
- **Admin Pages**:
  - ✅ AdminDashboardPage (vollständig)
  - ✅ AdminUsersPage (vollständig)
  - ⏳ AdminOrganisationsPage, AdminCoursesPage, AdminBillingPage, AdminAnalyticsPage (Platzhalter)
- **Org Pages**:
  - ✅ OrgDashboardPage (vollständig)
  - ⏳ OrgUsersPage, OrgCoursesPage, OrgAnalyticsPage, OrgSettingsPage (Platzhalter)

### 🎯 Nächste Schritte (V2)

1. **Org-Pages vervollständigen**:
   - OrgUsersPage mit Invite/Remove Funktionen
   - OrgCoursesPage mit Assignment UI
   - OrgAnalyticsPage mit Charts

2. **Admin-Pages vervollständigen**:
   - AdminOrganisationsPage mit Org-Management
   - AdminCoursesPage mit Course-Actions
   - AdminBillingPage mit Plan-Overview
   - AdminAnalyticsPage mit System-Charts

3. **Advanced Features**:
   - Bulk-Operations
   - CSV-Export
   - Real-Time-Updates
   - Audit-Logs

### 📊 Metriken

- **Neue Dateien**: 15
- **Modifizierte Dateien**: 2
- **Lines of Code**: ~2.500
- **TypeScript Interfaces**: 20+
- **API-Funktionen**: 30+
- **Store Actions**: 25+
- **Routes**: 11

**Phase F7 liefert eine solide, skalierbare Basis für Admin- und Org-Verwaltung!** 🎉
