/**
 * LernsystemX - Vue Router Configuration
 *
 * Routes:
 * - Setup: /setup (installation wizard)
 * - Public: /login, /register
 * - Protected: /dashboard, /courses, /profile
 * - Panel: /panel (system administration, formerly /admin)
 * - Editor: /editor (course authoring)
 *
 * Navigation Guards:
 * - requiresAuth: Redirect to /login if not authenticated
 * - requiresSetup: Redirect to /setup if not installed
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'
import { useAppStore } from '@/application/stores/modules/core/app.store'
import { panelRoutes, examArchiveRoute } from '@/presentation/pages/panel/admin/routes'
import { editorRoutes } from '@/presentation/pages/panel/editor/routes'

const routes: RouteRecordRaw[] = [
  // Setup Wizard Routes
  {
    path: '/setup',
    name: 'Setup',
    component: () => import('@/presentation/pages/public/setup/SetupWizardPage.vue'),
    // Access controlled by navigation guard - redirects to login if setup not required
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
    component: () => import('@/presentation/pages/public/auth/LoginPage.vue'),
    meta: { requiresGuest: true }, // Only accessible when NOT logged in
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/presentation/pages/public/auth/RegisterPage.vue'),
    meta: { requiresGuest: true },
  },

  // Protected Routes
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/presentation/pages/panel/user/dashboard/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/presentation/pages/panel/user/profile/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/presentation/pages/panel/user/profile/SettingsPage.vue'),
    meta: { requiresAuth: true },
  },

  // Programs (unified view: courses + exam trainer)
  {
    path: '/programs',
    name: 'Programs',
    component: () => import('@/presentation/pages/panel/user/programs/ProgramsPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/programs/:programId',
    name: 'ProgramDetail',
    component: () => import('@/presentation/pages/panel/user/programs/ProgramDetailPage.vue'),
    meta: { requiresAuth: true },
  },

  // Course Routes (redirect to programs)
  {
    path: '/courses',
    redirect: '/programs',
  },
  {
    path: '/course/:courseId',
    name: 'CourseOverview',
    component: () => import('@/presentation/pages/panel/user/courses/CourseOverviewPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/course/:courseId/chapter/:chapterId',
    name: 'ChapterDetail',
    component: () => import('@/presentation/pages/panel/user/courses/ChapterDetailPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/course/:courseId/chapter/:chapterId/lesson/:lessonId',
    name: 'LessonPlayer',
    component: () => import('@/presentation/pages/panel/user/learning/LessonPlayerPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/course/:courseId/exam-simulation',
    name: 'ExamSimulation',
    component: () => import('@/presentation/pages/panel/user/learning/ExamSimulationPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },

  // Exam Trainer (redirect to programs, trainer is now embedded)
  {
    path: '/exam-trainer',
    redirect: '/programs',
  },

  // AP2 Trainer (FISI FA 235 BW) — Vollausbau mit 7 Sub-Views
  {
    path: '/ap2-training',
    component: () => import('@/presentation/pages/panel/user/ap2/AP2TrainingPage.vue'),
    meta: { requiresAuth: true },
    redirect: '/ap2-training/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Ap2Dashboard',
        component: () => import('@/presentation/pages/panel/user/ap2/views/DashboardView.vue'),
      },
      {
        path: 'study',
        name: 'Ap2Study',
        component: () => import('@/presentation/pages/panel/user/ap2/views/StudyView.vue'),
      },
      {
        path: 'study/:topicSlug',
        name: 'Ap2StudyTopic',
        component: () => import('@/presentation/pages/panel/user/ap2/views/StudyView.vue'),
        props: true,
      },
      {
        path: 'review',
        name: 'Ap2Review',
        component: () => import('@/presentation/pages/panel/user/ap2/views/ReviewQueueView.vue'),
      },
      {
        path: 'exam',
        name: 'Ap2Exam',
        component: () => import('@/presentation/pages/panel/user/ap2/views/ExamSimulationView.vue'),
      },
      {
        path: 'cheatsheet',
        name: 'Ap2Cheatsheet',
        component: () => import('@/presentation/pages/panel/user/ap2/views/CheatsheetView.vue'),
      },
      {
        path: 'cheatsheet/:topicSlug',
        name: 'Ap2CheatsheetTopic',
        component: () => import('@/presentation/pages/panel/user/ap2/views/CheatsheetView.vue'),
        props: true,
      },
      {
        path: 'anlagen',
        name: 'Ap2Anlagen',
        component: () => import('@/presentation/pages/panel/user/ap2/views/AnlagenLibraryView.vue'),
      },
    ],
  },

  // Anlage standalone popout (opened via window.open from exam trainer)
  {
    path: '/exam-trainer/anlage/:examId/:anlageNumber',
    name: 'AnlagePopout',
    component: () => import('@/presentation/pages/panel/user/exam-trainer/AnlagePopoutPage.vue'),
    meta: { requiresAuth: true, hideLayout: true },
    props: true,
  },

  // Exam Cockpit (personal exam dashboard)
  {
    path: '/exam-cockpit',
    name: 'ExamCockpit',
    component: () => import('@/presentation/pages/panel/user/exams/ExamCockpitPage.vue'),
    meta: { requiresAuth: true },
  },

  // AI Editor (GBA-based - all authenticated users)
  {
    path: '/ai-editor',
    name: 'AIEditor',
    component: () => import('@/presentation/pages/panel/admin/ai/AIEditorPage.vue'),
    meta: { requiresAuth: true },
    // GBA handles feature visibility inside component
  },

  // Exam Archive (fullscreen, no sidebar — MUST be before panelRoutes)
  examArchiveRoute,

  // Panel Routes (System Administration) — /panel/admin/*
  panelRoutes,

  // Editor Routes (Course Authoring)
  editorRoutes,

  // Creator/Teacher Routes (Course Editor)
  {
    path: '/creator',
    meta: { requiresAuth: true, requiresCreatorOrTeacher: true },
    children: [
      {
        path: 'courses',
        name: 'CreatorCourses',
        component: () => import('@/presentation/pages/panel/editor/CreatorCoursesPage.vue'),
      },
      {
        path: 'courses/new',
        name: 'CreateCourse',
        component: () => import('@/presentation/pages/panel/editor/CourseEditorPage.vue'),
        props: { mode: 'create' },
      },
      {
        path: 'courses/:courseId/edit',
        name: 'EditCourse',
        component: () => import('@/presentation/pages/panel/editor/CourseEditorPage.vue'),
        props: (route) => ({ courseId: Number(route.params.courseId), mode: 'edit' }),
      },
    ],
  },

  // Legal Pages (Public - no auth required)
  {
    path: '/legal/imprint',
    name: 'Imprint',
    component: () => import('@/presentation/pages/public/legal/ImprintPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/privacy',
    name: 'Privacy',
    component: () => import('@/presentation/pages/public/legal/PrivacyPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/terms',
    name: 'Terms',
    component: () => import('@/presentation/pages/public/legal/TermsPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/cookies',
    name: 'Cookies',
    component: () => import('@/presentation/pages/public/legal/CookiesPage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/content-usage',
    name: 'ContentUsage',
    component: () => import('@/presentation/pages/public/legal/ContentUsagePage.vue'),
    meta: { isPublic: true },
  },
  {
    path: '/legal/licensing',
    name: 'Licensing',
    redirect: '/legal/content-usage',
  },

  // Pop-out Windows (independent browser windows for multi-monitor)
  {
    path: '/panel/popout/:windowType',
    component: () => import('@/presentation/layouts/PopoutLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Popout',
        component: () => import('@/presentation/pages/panel/popout/PopoutPage.vue'),
      },
    ],
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

  // ALWAYS check installation status first (only once per session)
  if (appStore.installed === null) {
    console.log('[Router Guard] First load - checking installation status')
    await appStore.checkInstallationStatus()
  }

  // SETUP ROUTE PROTECTION: Block access to /setup when system is already installed
  if (to.path === '/setup') {
    if (!appStore.setupRequired) {
      console.log('[Router Guard] Setup not required, redirecting to login')
      next({ name: 'Login' })
      return
    }
    // Setup is required - allow access to setup page
    next()
    return
  }

  // If setup is required but not on setup page, redirect to setup
  if (appStore.setupRequired) {
    console.log('[Router Guard] Setup required, redirecting to setup')
    next({ name: 'Setup' })
    return
  }

  // SKIP auth checks for public pages
  if (to.meta.isPublic) {
    next()
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

  // Check Creator or Teacher access (hierarchy_level >= 250)
  if (to.meta.requiresCreatorOrTeacher) {
    // Use GBA hierarchy-level based check instead of hardcoded role strings
    // isCreator = hierarchy_level >= 250 (includes Creator, Teacher, OrgAdmin, Moderator, Admin, Owner)
    if (!authStore.isCreator) {
      console.warn('Access denied: Creator/Teacher role required (hierarchy_level >= 250)')
      next({ name: 'Dashboard' })
      return
    }
  }

  // Allow navigation
  next()
})

export default router
