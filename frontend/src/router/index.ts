/**
 * LernsystemX - Vue Router Configuration
 *
 * Routes:
 * - Setup: /setup (installation wizard)
 * - Public: /login, /register
 * - Protected: /dashboard, /courses, /profile
 *
 * Navigation Guards:
 * - requiresAuth: Redirect to /login if not authenticated
 * - requiresSetup: Redirect to /setup if not installed
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/store/auth.store'
import { useAppStore } from '@/store/app.store'

const routes: RouteRecordRaw[] = [
  // Setup Wizard Routes
  {
    path: '/setup',
    name: 'Setup',
    component: () => import('@/pages/setup/SetupWizardPage.vue'),
    meta: { ignoreSetupCheck: true }, // Don't redirect to setup from setup
  },

  // Public Routes
  {
    path: '/',
    name: 'Root',
    redirect: () => {
      // This will be handled by beforeEach guard
      // which will check setup status and redirect accordingly
      return '/dashboard'
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/auth/LoginPage.vue'),
    meta: { requiresGuest: true }, // Only accessible when NOT logged in
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/auth/RegisterPage.vue'),
    meta: { requiresGuest: true },
  },

  // Protected Routes
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/dashboard/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/SettingsPage.vue'),
    meta: { requiresAuth: true },
  },

  // Course Routes
  {
    path: '/courses',
    name: 'Courses',
    component: () => import('@/pages/CoursesPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/course/:courseId',
    name: 'CourseOverview',
    component: () => import('@/pages/CourseOverviewPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/course/:courseId/chapter/:chapterId',
    name: 'ChapterDetail',
    component: () => import('@/pages/ChapterDetailPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/course/:courseId/chapter/:chapterId/lesson/:lessonId',
    name: 'LessonPlayer',
    component: () => import('@/pages/LessonPlayerPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/course/:courseId/exam-simulation',
    name: 'ExamSimulation',
    component: () => import('@/pages/ExamSimulationPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },

  // Admin Routes (System Admins only)
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresSystemAdmin: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('@/pages/admin/AdminDashboardPage.vue'),
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/pages/admin/AdminUsersPage.vue'),
      },
      {
        path: 'users/:userId',
        name: 'AdminUserDetail',
        component: () => import('@/pages/admin/AdminUserDetailPage.vue'),
      },
      {
        path: 'organisations',
        name: 'AdminOrganisations',
        component: () => import('@/pages/admin/AdminOrganisationsPage.vue'),
      },
      // Redirects for renamed routes (Wave 6)
      {
        path: 'kurse',
        redirect: '/admin/kurs-editor',
      },
      {
        path: 'ki-studio',
        redirect: '/admin/ai-studio',
      },
      // New route names (Wave 6)
      {
        path: 'kurs-editor',
        name: 'AdminCourseEditor',
        component: () => import('@/pages/admin/AdminCoursesPage.vue'),
      },
      {
        path: 'kurs-editor/:id',
        name: 'admin-course-detail',
        component: () => import('@/pages/admin/AdminCourseDetailPage.vue'),
        props: true,
      },
      {
        path: 'ai-studio',
        name: 'AdminAIStudio',
        component: () => import('@/pages/admin/AdminKIStudioPage.vue'),
      },
      // Legacy route (old name)
      {
        path: 'courses',
        redirect: '/admin/kurs-editor',
      },
      {
        path: 'courses/:id',
        redirect: (to) => `/admin/kurs-editor/${to.params.id}`,
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: () => import('@/pages/admin/AdminCategoriesPage.vue'),
      },
      {
        path: 'billing',
        name: 'AdminBilling',
        component: () => import('@/pages/admin/AdminBillingPage.vue'),
      },
      {
        path: 'analytics',
        name: 'AdminAnalytics',
        component: () => import('@/pages/admin/AdminAnalyticsPage.vue'),
      },
      {
        path: 'audit-logs',
        name: 'AdminAuditLogs',
        component: () => import('@/pages/admin/AdminAuditLogsPage.vue'),
      },
      {
        path: 'translations',
        name: 'AdminTranslations',
        component: () => import('@/pages/admin/AdminTranslationsPage.vue'),
      },
      {
        path: 'lm-routing',
        name: 'AdminLMRouting',
        component: () => import('@/pages/admin/AdminLMRoutingPage.vue'),
      },
      {
        path: 'roles',
        name: 'AdminRoles',
        component: () => import('@/pages/admin/AdminRolesPage.vue'),
        meta: { requiresOwner: true }, // RBAC 2.0 - Only Owner can manage roles
      },
      {
        path: 'system-settings',
        name: 'AdminSystemSettings',
        component: () => import('@/pages/admin/AdminSystemSettingsPage.vue'),
      },
    ],
  },

  // Organisation Admin Routes (Org Admins only)
  {
    path: '/org',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresOrgAdmin: true },
    children: [
      {
        path: '',
        name: 'OrgDashboard',
        component: () => import('@/pages/org/OrgDashboardPage.vue'),
      },
      {
        path: 'users',
        name: 'OrgUsers',
        component: () => import('@/pages/org/OrgUsersPage.vue'),
      },
      {
        path: 'courses',
        name: 'OrgCourses',
        component: () => import('@/pages/org/OrgCoursesPage.vue'),
      },
      {
        path: 'analytics',
        name: 'OrgAnalytics',
        component: () => import('@/pages/org/OrgAnalyticsPage.vue'),
      },
      {
        path: 'settings',
        name: 'OrgSettings',
        component: () => import('@/pages/org/OrgSettingsPage.vue'),
      },
    ],
  },

  // Creator/Teacher Routes (Course Editor)
  {
    path: '/creator',
    meta: { requiresAuth: true, requiresCreatorOrTeacher: true },
    children: [
      {
        path: 'courses',
        name: 'CreatorCourses',
        component: () => import('@/pages/creator/CreatorCoursesPage.vue'),
      },
      {
        path: 'courses/new',
        name: 'CreateCourse',
        component: () => import('@/pages/creator/CourseEditorPage.vue'),
        props: { mode: 'create' },
      },
      {
        path: 'courses/:courseId/edit',
        name: 'EditCourse',
        component: () => import('@/pages/creator/CourseEditorPage.vue'),
        props: (route) => ({ courseId: Number(route.params.courseId), mode: 'edit' }),
      },
    ],
  },

  // Legal Pages (Public - no auth required)
  {
    path: '/legal/imprint',
    name: 'Imprint',
    component: () => import('@/pages/legal/ImprintPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/privacy',
    name: 'Privacy',
    component: () => import('@/pages/legal/PrivacyPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/terms',
    name: 'Terms',
    component: () => import('@/pages/legal/TermsPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/cookies',
    name: 'Cookies',
    component: () => import('@/pages/legal/CookiesPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/content-usage',
    name: 'ContentUsage',
    component: () => import('@/pages/legal/ContentUsagePage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/licensing',
    name: 'Licensing',
    redirect: '/legal/content-usage',
  },

  // 404 Not Found
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/NotFoundPage.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation Guards
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  const appStore = useAppStore()

  // Check installation status if not yet checked
  if (appStore.installed === null && !to.meta.ignoreSetupCheck) {
    await appStore.checkInstallationStatus()
  }

  // If system is not installed and route is not setup, redirect to setup
  // Allow public pages (legal, etc.) even during setup
  if (appStore.setupRequired && !to.meta.ignoreSetupCheck && !to.meta.isPublic) {
    if (to.path !== '/setup') {
      next({ name: 'Setup' })
      return
    }
  }

  // If system is installed and trying to access setup, redirect to login
  if (appStore.installed && to.path === '/setup') {
    next({ name: 'Login' })
    return
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login if not authenticated
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // Check if route requires guest (not logged in)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // Redirect to dashboard if already logged in
    next({ name: 'Dashboard' })
    return
  }

  // Role-based access control
  // Check Owner access (RBAC 2.0)
  if (to.meta.requiresOwner && !authStore.isOwner) {
    console.warn('Access denied: Owner role required')
    next({ name: 'Dashboard' })
    return
  }

  // Check System Admin access
  if (to.meta.requiresSystemAdmin && !authStore.isSystemAdmin) {
    console.warn('Access denied: System Admin required')
    next({ name: 'Dashboard' })
    return
  }

  // Check Organisation Admin access
  if (to.meta.requiresOrgAdmin && !authStore.isOrgAdmin) {
    console.warn('Access denied: Organisation Admin required')
    next({ name: 'Dashboard' })
    return
  }

  // Check Creator or Teacher access
  if (to.meta.requiresCreatorOrTeacher) {
    const allowedRoles = ['creator', 'teacher', 'school_admin', 'company_admin', 'admin', 'superadmin']
    const hasAccess = allowedRoles.includes(authStore.userRole)

    if (!hasAccess) {
      console.warn('Access denied: Creator/Teacher role required')
      next({ name: 'Dashboard' })
      return
    }
  }

  // Allow navigation
  next()
})

export default router
