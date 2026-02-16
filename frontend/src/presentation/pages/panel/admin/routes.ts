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
    // Redirects for renamed routes (Wave 6)
    {
      path: 'kurse',
      redirect: '/editor',
    },
    {
      path: 'roles',
      redirect: '/panel/groups',
    },
    // Course Editor now at /editor (separate feature)
    {
      path: 'kurs-editor',
      redirect: '/editor',
    },
    {
      path: 'kurs-editor/:id',
      redirect: (to) => `/editor/${to.params.id}`,
    },
    {
      path: 'ai-studio',
      redirect: '/ai-editor',
    },
    // Legacy route (old name)
    {
      path: 'courses',
      redirect: '/editor',
    },
    {
      path: 'courses/:id',
      redirect: (to) => `/editor/${to.params.id}`,
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
      name: 'PanelAISettings',
      component: () => import('@/presentation/pages/panel/admin/PanelAISettingsPage.vue'),
    },
    {
      path: 'system-settings',
      name: 'PanelSystemSettings',
      component: () => import('@/presentation/pages/panel/admin/PanelSystemSettingsPage.vue'),
    },
  ],
}

export default panelRoutes
