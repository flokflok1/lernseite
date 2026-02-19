/**
 * LernsystemX - Panel Store (Pinia) - Orchestrator
 *
 * Thin facade that composes domain-specific sub-stores into a unified
 * interface for backward compatibility. All state and actions are delegated
 * to the sub-stores:
 *
 * - panel-users.store.ts     - User management
 * - panel-organisations.store.ts - Organisation management
 * - panel-courses.store.ts   - Courses, chapters, categories
 * - panel-analytics.store.ts - Dashboard stats, analytics, audit logs, billing
 * - panel-ai-jobs.store.ts   - AI job lifecycle
 *
 * Consumers can import usePanelStore for the unified API, or import
 * individual sub-stores directly for more focused access.
 */

import { defineStore } from 'pinia'
import { computed } from 'vue'
import { usePanelUsersStore } from './panel-users.store'
import { usePanelOrganisationsStore } from './panel-organisations.store'
import { usePanelCoursesStore } from './panel-courses.store'
import { usePanelAnalyticsStore } from './panel-analytics.store'
import { usePanelAIJobsStore } from './panel-ai-jobs.store'

export const usePanelStore = defineStore('panel', () => {
  const usersStore = usePanelUsersStore()
  const orgsStore = usePanelOrganisationsStore()
  const coursesStore = usePanelCoursesStore()
  const analyticsStore = usePanelAnalyticsStore()
  const aiJobsStore = usePanelAIJobsStore()

  /**
   * Global loading state: true if any sub-store is loading
   */
  const loading = computed(() =>
    usersStore.loading ||
    orgsStore.loading ||
    coursesStore.loading ||
    analyticsStore.loading
  )

  /**
   * Global error state: first non-null error from sub-stores
   */
  const error = computed(() =>
    usersStore.error ||
    orgsStore.error ||
    coursesStore.error ||
    analyticsStore.error ||
    null
  )

  return {
    // State - Users (delegated)
    users: computed(() => usersStore.users),
    usersTotal: computed(() => usersStore.usersTotal),
    usersPage: computed(() => usersStore.usersPage),
    usersLimit: computed(() => usersStore.usersLimit),
    usersTotalPages: computed(() => usersStore.usersTotalPages),
    userFilters: computed(() => usersStore.userFilters),

    // State - Organisations (delegated)
    organisations: computed(() => orgsStore.organisations),
    orgsTotal: computed(() => orgsStore.orgsTotal),
    orgsPage: computed(() => orgsStore.orgsPage),
    orgsLimit: computed(() => orgsStore.orgsLimit),
    orgsTotalPages: computed(() => orgsStore.orgsTotalPages),
    orgFilters: computed(() => orgsStore.orgFilters),

    // State - Courses (delegated)
    courses: computed(() => coursesStore.courses),
    coursesTotal: computed(() => coursesStore.coursesTotal),
    coursesPage: computed(() => coursesStore.coursesPage),
    coursesLimit: computed(() => coursesStore.coursesLimit),
    coursesTotalPages: computed(() => coursesStore.coursesTotalPages),
    courseFilters: computed(() => coursesStore.courseFilters),

    // State - Chapters (delegated)
    courseChapters: computed(() => coursesStore.courseChapters),
    currentChapters: computed(() => coursesStore.currentChapters),

    // State - Categories (delegated)
    categoryTree: computed(() => coursesStore.categoryTree),
    categoriesFlat: computed(() => coursesStore.categoriesFlat),
    categoriesLoaded: computed(() => coursesStore.categoriesLoaded),

    // State - System (delegated)
    systemStats: computed(() => analyticsStore.systemStats),
    tokenStats: computed(() => analyticsStore.tokenStats),
    plans: computed(() => analyticsStore.plans),

    // State - Audit Logs (delegated)
    auditLogs: computed(() => analyticsStore.auditLogs),
    auditLogsTotal: computed(() => analyticsStore.auditLogsTotal),
    auditLogsPage: computed(() => analyticsStore.auditLogsPage),
    auditLogsLimit: computed(() => analyticsStore.auditLogsLimit),
    auditLogsTotalPages: computed(() => analyticsStore.auditLogsTotalPages),
    auditLogsFilters: computed(() => analyticsStore.auditLogsFilters),

    // State - Analytics (delegated)
    systemAnalytics: computed(() => analyticsStore.systemAnalytics),
    systemAnalyticsLoading: computed(() => analyticsStore.systemAnalyticsLoading),
    systemAnalyticsError: computed(() => analyticsStore.systemAnalyticsError),

    // State - AI Jobs (delegated)
    aiJobs: computed(() => aiJobsStore.aiJobs),
    currentAIJob: computed(() => aiJobsStore.currentAIJob),
    aiJobLoading: computed(() => aiJobsStore.aiJobLoading),
    aiJobError: computed(() => aiJobsStore.aiJobError),

    // State - UI (composed)
    loading,
    error,

    // Getters (delegated)
    hasSystemStats: computed(() => analyticsStore.hasSystemStats),
    totalUsersCount: computed(() => analyticsStore.totalUsersCount),
    activeUsersCount: computed(() => analyticsStore.activeUsersCount),
    totalOrgsCount: computed(() => analyticsStore.totalOrgsCount),
    totalCoursesCount: computed(() => analyticsStore.totalCoursesCount),
    hasAnalytics: computed(() => analyticsStore.hasAnalytics),
    analyticsTimeframe: computed(() => analyticsStore.analyticsTimeframe),

    // Actions - Dashboard
    loadAdminDashboard: analyticsStore.loadAdminDashboard,

    // Actions - Users
    loadUsers: usersStore.loadUsers,
    updateUserRole: usersStore.updateUserRole,
    toggleUserActive: usersStore.toggleUserActive,
    deleteUser: usersStore.deleteUser,
    createUser: usersStore.createUser,
    banUser: usersStore.banUser,
    unbanUser: usersStore.unbanUser,
    grantTokens: usersStore.grantTokens,
    verifyCreator: usersStore.verifyCreator,

    // Actions - Audit Logs
    loadAuditLogs: analyticsStore.loadAuditLogs,

    // Actions - Organisations
    loadOrganisations: orgsStore.loadOrganisations,
    updateOrganisationPlan: orgsStore.updateOrganisationPlan,
    addOrganisationTokens: orgsStore.addOrganisationTokens,

    // Actions - Courses
    loadCourses: coursesStore.loadCourses,
    getCourseDetail: coursesStore.getCourseDetail,
    createCourse: coursesStore.createCourse,
    updateCourse: coursesStore.updateCourse,
    publishCourse: coursesStore.publishCourse,
    unpublishCourse: coursesStore.unpublishCourse,
    archiveCourse: coursesStore.archiveCourse,
    unarchiveCourse: coursesStore.unarchiveCourse,
    deleteCourse: coursesStore.deleteCourse,
    permanentDeleteCourse: coursesStore.permanentDeleteCourse,

    // Actions - Chapters
    loadCourseChapters: coursesStore.loadCourseChapters,
    createChapter: coursesStore.createChapter,
    updateChapter: coursesStore.updateChapter,
    deleteChapter: coursesStore.deleteChapter,
    reorderChapters: coursesStore.reorderChapters,

    // Actions - Categories
    loadCategoryTree: coursesStore.loadCategoryTree,
    loadCategories: coursesStore.loadCategories,
    findCategoryById: coursesStore.findCategoryById,
    createCategory: coursesStore.createCategory,
    updateCategory: coursesStore.updateCategory,
    deleteCategory: coursesStore.deleteCategory,

    // Actions - Billing
    loadPlans: analyticsStore.loadPlans,

    // Actions - Analytics
    loadAdminAnalytics: analyticsStore.loadAdminAnalytics,
    changeAnalyticsTimeframe: analyticsStore.changeAnalyticsTimeframe,

    // Actions - AI Jobs
    startAIJob: aiJobsStore.startAIJob,
    pollAIJob: aiJobsStore.pollAIJob,
    getAIJob: aiJobsStore.getAIJob,
    cancelAIJob: aiJobsStore.cancelAIJob,
    finalizeAIJob: aiJobsStore.finalizeAIJob,
    clearCurrentAIJob: aiJobsStore.clearCurrentAIJob,
    startAIJobPolling: aiJobsStore.startAIJobPolling,
    stopAIJobPolling: aiJobsStore.stopAIJobPolling
  }
})

/**
 * Alias for backward compatibility.
 * Some barrel exports reference this name.
 */
export const useAdminPanelStore = usePanelStore
