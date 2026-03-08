/**
 * Panel Routes - System Administration
 *
 * Feature-first routing for panel pages (formerly /admin)
 * Uses PanelLayout wrapper with permission-based guards
 */

import type { RouteRecordRaw } from 'vue-router'

export const panelRoutes: RouteRecordRaw = {
  path: '/panel',
  component: () => import('@/presentation/layouts/PanelLayout.vue'),
  meta: { requiresAuth: true, requiresSystemAdmin: true },
  children: [
    {
      path: '',
      name: 'PanelDashboard',
      component: () => import('@/presentation/pages/panel/admin/PanelDashboardPage.vue'),
    },
    {
      path: 'users',
      name: 'PanelUsers',
      component: () => import('@/presentation/pages/panel/admin/PanelUsersPage.vue'),
    },
    {
      path: 'users/:userId',
      name: 'PanelUserDetail',
      component: () => import('@/presentation/pages/panel/admin/PanelUserDetailPage.vue'),
    },
    {
      path: 'organisations',
      name: 'PanelOrganisations',
      component: () => import('@/presentation/pages/panel/admin/PanelOrganisationsPage.vue'),
    },
    {
      path: 'exam-archive',
      name: 'PanelExamArchive',
      component: () => import('@/presentation/pages/panel/admin/PanelExamArchivePage.vue'),
    },
    {
      path: 'curriculum',
      name: 'PanelCurriculum',
      component: () => import('@/presentation/pages/panel/admin/PanelCurriculumPage.vue'),
    },
    // Legacy redirects → /panel/admin/editor
    {
      path: 'kurse',
      redirect: '/panel/admin/editor',
    },
    {
      path: 'roles',
      redirect: '/panel/groups',
    },
    {
      path: 'kurs-editor',
      redirect: '/panel/admin/editor',
    },
    {
      path: 'kurs-editor/:id',
      redirect: (to) => `/panel/admin/editor/${to.params.id}`,
    },
    {
      path: 'courses',
      redirect: '/panel/admin/editor',
    },
    {
      path: 'courses/:id',
      redirect: (to) => `/panel/admin/editor/${to.params.id}`,
    },
    // Backward compat: /panel/editor → /panel/admin/editor
    {
      path: 'editor',
      redirect: '/panel/admin/editor',
    },
    {
      path: 'editor/:id',
      redirect: (to) => `/panel/admin/editor/${to.params.id}`,
    },
    {
      path: 'categories',
      name: 'PanelCategories',
      component: () => import('@/presentation/pages/panel/admin/PanelCategoriesPage.vue'),
    },
    {
      path: 'billing',
      name: 'PanelBilling',
      component: () => import('@/presentation/pages/panel/admin/PanelBillingPage.vue'),
    },
    {
      path: 'analytics',
      name: 'PanelAnalytics',
      component: () => import('@/presentation/pages/panel/admin/PanelAnalyticsPage.vue'),
    },
    {
      path: 'audit-logs',
      name: 'PanelAuditLogs',
      component: () => import('@/presentation/pages/panel/admin/PanelAuditLogsPage.vue'),
    },
    {
      path: 'languages',
      name: 'PanelLanguages',
      component: () => import('@/presentation/pages/panel/admin/PanelLanguagesPage.vue'),
    },
    {
      path: 'translations',
      name: 'PanelTranslations',
      component: () => import('@/presentation/pages/panel/admin/PanelTranslationsPage.vue'),
    },
    {
      path: 'lm-routing',
      name: 'PanelLMRouting',
      component: () => import('@/presentation/pages/panel/admin/PanelLMRoutingPage.vue'),
    },
    {
      path: 'groups',
      name: 'PanelGroups',
      component: () => import('@/presentation/pages/panel/admin/PanelGroupsPage.vue'),
    },
    {
      path: 'ai-settings',
      redirect: '/panel/system-settings',
    },
    {
      path: 'system-settings',
      name: 'PanelSystemSettings',
      component: () => import('@/presentation/pages/panel/admin/PanelSystemSettingsPage.vue'),
    },
    // Admin Course Editor (windowed interface within panel)
    {
      path: 'admin/editor',
      name: 'PanelAdminEditor',
      component: () => import('@/presentation/pages/panel/editor/CourseEditorMain.vue'),
    },
    {
      path: 'admin/editor/:id',
      name: 'PanelAdminEditorDetail',
      component: () => import('@/presentation/pages/panel/admin/PanelCourseDetailPage.vue'),
      props: true,
    },
  ],
}

export default panelRoutes
