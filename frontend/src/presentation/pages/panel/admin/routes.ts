/**
 * Panel Admin Routes - System Administration
 *
 * All admin routes under /panel/admin/
 * Uses PanelLayout wrapper with permission-based guards
 */

import type { RouteRecordRaw } from 'vue-router'

export const panelRoutes: RouteRecordRaw = {
  path: '/panel/admin',
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
      path: 'exams',
      name: 'PanelExams',
      component: () => import('@/presentation/pages/panel/admin/PanelExamsPage.vue'),
    },
    {
      path: 'programs',
      name: 'PanelPrograms',
      component: () => import('@/presentation/components/panel/admin/programs/ProgramManager.vue'),
    },
    {
      path: 'curriculum',
      redirect: '/panel/admin/exams?tab=curriculum',
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
      path: 'system-settings',
      name: 'PanelSystemSettings',
      component: () => import('@/presentation/pages/panel/admin/PanelSystemSettingsPage.vue'),
    },
    {
      path: 'crawler',
      name: 'PanelCrawler',
      component: () => import('@/presentation/pages/panel/admin/PanelCrawlerPage.vue'),
    },
    {
      path: 'editor',
      name: 'PanelAdminEditor',
      component: () => import('@/presentation/pages/panel/editor/CourseEditorMain.vue'),
    },
    {
      path: 'editor/:id',
      name: 'PanelAdminEditorDetail',
      component: () => import('@/presentation/pages/panel/admin/PanelCourseDetailPage.vue'),
      props: true,
    },
  ],
}


/** Standalone fullscreen route — no PanelLayout sidebar */
export const examArchiveRoute: RouteRecordRaw = {
  path: '/exam-archive',
  name: 'PanelExamArchive',
  component: () => import('@/presentation/pages/panel/admin/PanelExamArchivePage.vue'),
  meta: { requiresAuth: true, requiresSystemAdmin: true },
}

export default panelRoutes
