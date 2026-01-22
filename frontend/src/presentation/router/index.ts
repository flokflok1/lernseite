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
import { useAuthStore } from '@/application/stores/auth.store'
import { useAppStore } from '@/application/stores/app.store'

const routes: RouteRecordRaw[] = [
  // Setup Wizard Routes
  {
    path: '/setup',
    name: 'Setup',
    component: () => import('@/presentation/pages/setup/SetupWizardPage.vue'),
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
    component: () => import('@/presentation/pages/auth/LoginPage.vue'),
    meta: { requiresGuest: true }, // Only accessible when NOT logged in
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/presentation/pages/auth/RegisterPage.vue'),
    meta: { requiresGuest: true },
  },

  // Protected Routes
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/presentation/pages/dashboard/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/presentation/pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/presentation/pages/SettingsPage.vue'),
    meta: { requiresAuth: true },
  },

  // Course Routes
  {
    path: '/courses',
    name: 'Courses',
    component: () => import('@/presentation/pages/CoursesPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/course/:courseId',
    name: 'CourseOverview',
    component: () => import('@/presentation/pages/CourseOverviewPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/course/:courseId/chapter/:chapterId',
    name: 'ChapterDetail',
    component: () => import('@/presentation/pages/ChapterDetailPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/course/:courseId/chapter/:chapterId/lesson/:lessonId',
    name: 'LessonPlayer',
    component: () => import('@/presentation/pages/LessonPlayerPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/course/:courseId/exam-simulation',
    name: 'ExamSimulation',
    component: () => import('@/presentation/pages/ExamSimulationPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },

  // Admin Routes (System Admins only)
  {
    path: '/admin',
    component: () => import('@/presentation/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresSystemAdmin: true },
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
        path: 'organisations',
        name: 'AdminOrganisations',
        component: () => import('@/presentation/pages/admin/AdminOrganisationsPage.vue'),
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
        component: () => import('@/presentation/pages/admin/AdminCoursesPage.vue'),
      },
      {
        path: 'kurs-editor/:id',
        name: 'admin-course-detail',
        component: () => import('@/presentation/pages/admin/AdminCourseDetailPage.vue'),
        props: true,
      },
      {
        path: 'ai-studio',
        name: 'AdminAIStudio',
        component: () => import('@/presentation/pages/admin/AdminKIStudioPage.vue'),
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
        component: () => import('@/presentation/pages/admin/AdminCategoriesPage.vue'),
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
      // TODO: Fix i18n translations system (locales dir issue)
      // {
      //   path: 'translations',
      //   name: 'AdminTranslations',
      //   component: () => import('@/presentation/pages/admin/AdminTranslationsPage.vue'),
      // },
      {
        path: 'lm-routing',
        name: 'AdminLMRouting',
        component: () => import('@/presentation/pages/admin/AdminLMRoutingPage.vue'),
      },
      {
        path: 'roles',
        name: 'AdminRoles',
        component: () => import('@/presentation/pages/admin/AdminRolesPage.vue'),
      },
      {
        path: 'system-settings',
        name: 'AdminSystemSettings',
        component: () => import('@/presentation/pages/admin/AdminSystemSettingsPage.vue'),
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
        component: () => import('@/presentation/pages/creator/CreatorCoursesPage.vue'),
      },
      {
        path: 'courses/new',
        name: 'CreateCourse',
        component: () => import('@/presentation/pages/creator/CourseEditorPage.vue'),
        props: { mode: 'create' },
      },
      {
        path: 'courses/:courseId/edit',
        name: 'EditCourse',
        component: () => import('@/presentation/pages/creator/CourseEditorPage.vue'),
        props: (route) => ({ courseId: Number(route.params.courseId), mode: 'edit' }),
      },
    ],
  },

  // Legal Pages (Public - no auth required)
  {
    path: '/legal/imprint',
    name: 'Imprint',
    component: () => import('@/presentation/pages/legal/ImprintPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/privacy',
    name: 'Privacy',
    component: () => import('@/presentation/pages/legal/PrivacyPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/terms',
    name: 'Terms',
    component: () => import('@/presentation/pages/legal/TermsPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/cookies',
    name: 'Cookies',
    component: () => import('@/presentation/pages/legal/CookiesPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/content-usage',
    name: 'ContentUsage',
    component: () => import('@/presentation/pages/legal/ContentUsagePage.vue'),
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
    component: () => import('@/presentation/pages/NotFoundPage.vue'),
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

  // =====================================================
  // CHECK INSTALLATION STATUS FIRST
  // =====================================================
  // IMPORTANT: Must check installation status BEFORE reading localStorage
  // because checkInstallationStatus() fetches static marker and sets localStorage
  // This is critical for Private Mode / new users!
  if (appStore.installed === null && !to.meta.ignoreSetupCheck) {
    await appStore.checkInstallationStatus()
  }

  // =====================================================
  // SETUP LOCKOUT: Check localStorage AFTER installation check
  // =====================================================
  // Now read localStorage (may have been set by checkInstallationStatus above)
  const isSetupCompleted = localStorage.getItem('lsx-setup-completed') === 'true'

  if (isSetupCompleted && to.path === '/setup') {
    console.log('[Router Guard] Setup already completed - redirecting to login')
    next({ name: 'Login' })
    return
  }

  // =====================================================
  // BACKEND DOWN HANDLING
  // =====================================================
  // If backend is unreachable but localStorage says setup is done,
  // show maintenance message instead of redirecting to setup
  if (isSetupCompleted && appStore.setupRequired && !to.meta.ignoreSetupCheck && !to.meta.isPublic) {
    // Backend is down but setup was completed
    // Show maintenance page instead of setup
    console.warn('[Router Guard] Backend unreachable - setup completed but backend down')
    // Allow navigation to show maintenance message in App.vue
    // (App.vue will handle showing maintenance message)
  }
  // If system is not installed and route is not setup, redirect to setup
  // Allow public pages (legal, etc.) even during setup
  else if (appStore.setupRequired && !to.meta.ignoreSetupCheck && !to.meta.isPublic && !isSetupCompleted) {
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
  // Check System Admin access
  if (to.meta.requiresSystemAdmin && !authStore.isSystemAdmin) {
    console.warn('Access denied: System Admin required')
    next({ name: 'Dashboard' })
    return
  }

  // Check Organisation Admin access (includes OWNER role who has org-level permissions)
  if (to.meta.requiresOrgAdmin && !authStore.isOrgAdmin && !authStore.isOwner) {
    console.warn('Access denied: Organisation Admin or Owner role required')
    next({ name: 'Dashboard' })
    return
  }

  // Check Owner-only access (for owner-specific admin features)
  if (to.meta.requiresOwner && !authStore.isOwner) {
    console.warn('Access denied: Owner role required')
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
