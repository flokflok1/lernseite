/**
 * LernsystemX - Admin Store (Pinia)
 *
 * Manages:
 * - Global admin state (users, organisations, courses)
 * - System statistics
 * - Admin actions (user/org/course management)
 *
 * Refactored: modules → chapters (2025-11-27)
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as adminApi from '@/api/admin.api'
import type {
  AdminUser,
  AdminOrganisation,
  AdminCourse,
  AdminSystemStats,
  AdminTokenStats,
  AdminPlanOverview,
  UsersFilterParams,
  OrganisationsFilterParams,
  CoursesFilterParams,
  PaginatedResponse,
  TimeSeriesPoint,
  AdminAnalyticsCourse,
  AdminAnalyticsMethod,
  AuditLog,
  AuditLogsFilterParams,
  BanUserRequest,
  AdminChapter,
  AdminChapterCreateRequest,
  AdminChapterUpdateRequest,
  Category,
  CategoryTreeNode,
  CategoryTree,
  AIJob,
  AIJobStatus,
  AIJobType,
  AICourseDraft
} from '@/api/admin.api'

export const useAdminStore = defineStore('admin', () => {
  // ============================================================================
  // State
  // ============================================================================

  // Users
  const users = ref<AdminUser[]>([])
  const usersTotal = ref(0)
  const usersPage = ref(1)
  const usersLimit = ref(20)
  const usersTotalPages = ref(0)
  const userFilters = ref<UsersFilterParams>({})

  // Organisations
  const organisations = ref<AdminOrganisation[]>([])
  const orgsTotal = ref(0)
  const orgsPage = ref(1)
  const orgsLimit = ref(20)
  const orgsTotalPages = ref(0)
  const orgFilters = ref<OrganisationsFilterParams>({})

  // Courses
  const courses = ref<AdminCourse[]>([])
  const coursesTotal = ref(0)
  const coursesPage = ref(1)
  const coursesLimit = ref(20)
  const coursesTotalPages = ref(0)
  const courseFilters = ref<CoursesFilterParams>({})

  // Chapters (Phase B24-03, refactored from modules 2025-11-27)
  const courseChapters = ref<Map<number, AdminChapter[]>>(new Map())
  const currentChapters = ref<AdminChapter[]>([])

  // Categories (Phase B24-03)
  const categoryTree = ref<CategoryTreeNode[]>([])
  const categoriesFlat = ref<Category[]>([])
  const categoriesLoaded = ref(false)

  // System Stats
  const systemStats = ref<AdminSystemStats | null>(null)
  const tokenStats = ref<AdminTokenStats | null>(null)
  const plans = ref<AdminPlanOverview[]>([])

  // Audit Logs (Phase B24-01)
  const auditLogs = ref<AuditLog[]>([])
  const auditLogsTotal = ref(0)
  const auditLogsPage = ref(1)
  const auditLogsLimit = ref(20)
  const auditLogsTotalPages = ref(0)
  const auditLogsFilters = ref<AuditLogsFilterParams>({})

  // Analytics
  const systemAnalytics = ref<{
    timeframe: 7 | 30 | 90
    eventsTimeSeries: TimeSeriesPoint[]
    activeUsersTimeSeries: TimeSeriesPoint[]
    topCourses: AdminAnalyticsCourse[]
    topMethods: AdminAnalyticsMethod[]
  } | null>(null)
  const systemAnalyticsLoading = ref(false)
  const systemAnalyticsError = ref<string | null>(null)

  // AI Jobs (Phase B24-05)
  const aiJobs = ref<Map<string, adminApi.AIJob>>(new Map())
  const currentAIJob = ref<adminApi.AIJob | null>(null)
  const aiJobPollingInterval = ref<number | null>(null)
  const aiJobLoading = ref(false)
  const aiJobError = ref<string | null>(null)

  // Loading & Error States
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ============================================================================
  // Getters
  // ============================================================================

  const hasSystemStats = computed(() => !!systemStats.value)

  const totalUsersCount = computed(() => systemStats.value?.total_users || 0)

  const activeUsersCount = computed(() => systemStats.value?.active_users_7_days || 0)

  const totalOrgsCount = computed(() => systemStats.value?.total_organisations || 0)

  const totalCoursesCount = computed(() => systemStats.value?.total_courses || 0)

  const hasAnalytics = computed(() => !!systemAnalytics.value)

  const analyticsTimeframe = computed(() => systemAnalytics.value?.timeframe || 7)

  // ============================================================================
  // Actions - Dashboard
  // ============================================================================

  /**
   * Load admin dashboard (system stats)
   */
  const loadAdminDashboard = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const stats = await adminApi.adminGetSystemStats()
      systemStats.value = stats
      tokenStats.value = stats.token_stats
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Statistiken'
      console.error('Failed to load admin dashboard:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // ============================================================================
  // Actions - Users
  // ============================================================================

  /**
   * Load users with filters
   */
  const loadUsers = async (params: UsersFilterParams = {}): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response: PaginatedResponse<AdminUser> = await adminApi.adminGetUsers(params)

      users.value = response.items
      usersTotal.value = response.total
      usersPage.value = response.page
      usersLimit.value = response.limit
      usersTotalPages.value = response.total_pages
      userFilters.value = params
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Benutzer'
      console.error('Failed to load users:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update user role
   */
  const updateUserRole = async (userId: number, role: string): Promise<void> => {
    try {
      await adminApi.adminUpdateUserRole(userId, role)

      // Update local state
      const user = users.value.find(u => u.user_id === userId)
      if (user) {
        user.role = role
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Ändern der Rolle'
      console.error('Failed to update user role:', err)
      throw err
    }
  }

  /**
   * Toggle user active status
   */
  const toggleUserActive = async (userId: number): Promise<void> => {
    const user = users.value.find(u => u.user_id === userId)
    if (!user) return

    try {
      const newStatus = !user.is_active
      await adminApi.adminToggleUserActive(userId, newStatus)

      // Update local state
      user.is_active = newStatus
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Ändern des Status'
      console.error('Failed to toggle user active:', err)
      throw err
    }
  }

  /**
   * Delete user
   */
  const deleteUser = async (userId: number): Promise<void> => {
    try {
      await adminApi.adminDeleteUser(userId)

      // Remove from local state
      users.value = users.value.filter(u => u.user_id !== userId)
      usersTotal.value -= 1
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Löschen des Benutzers'
      console.error('Failed to delete user:', err)
      throw err
    }
  }

  /**
   * Create new user (admin only)
   */
  const createUser = async (userData: {
    email: string
    password: string
    first_name: string
    last_name: string
    role: string
  }): Promise<AdminUser> => {
    try {
      const user = await adminApi.adminCreateUser(userData)
      return user
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Erstellen des Benutzers'
      console.error('Failed to create user:', err)
      throw err
    }
  }

  // ============================================================================
  // Actions - Users (Phase B24-01: Ban, Unban, Grant, Verify)
  // ============================================================================

  /**
   * Ban user (admin only)
   * Prevents user from logging in and accessing the system
   */
  const banUser = async (userId: number, banData: BanUserRequest): Promise<void> => {
    try {
      await adminApi.adminBanUser(userId, banData)

      // Update local state - mark user as inactive after ban
      const user = users.value.find(u => u.user_id === userId)
      if (user) {
        user.is_active = false
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Sperren des Benutzers'
      console.error('Failed to ban user:', err)
      throw err
    }
  }

  /**
   * Unban user (admin only)
   * Restores user access to the system
   */
  const unbanUser = async (userId: number, reason: string): Promise<void> => {
    try {
      await adminApi.adminUnbanUser(userId, reason)

      // Update local state - mark user as active after unban
      const user = users.value.find(u => u.user_id === userId)
      if (user) {
        user.is_active = true
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Entsperren des Benutzers'
      console.error('Failed to unban user:', err)
      throw err
    }
  }

  /**
   * Grant tokens to user (admin only)
   * Adds tokens to user's wallet for AI operations
   */
  const grantTokens = async (
    userId: number,
    amount: number,
    reason: string
  ): Promise<number> => {
    try {
      const newBalance = await adminApi.adminGrantTokens(userId, amount, reason)

      // Update local state - update token balance if available
      const user = users.value.find(u => u.user_id === userId)
      if (user) {
        user.token_balance = newBalance
      }

      return newBalance
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Gewähren von Tokens'
      console.error('Failed to grant tokens:', err)
      throw err
    }
  }

  /**
   * Verify creator status (admin only)
   * Verifies or revokes creator verification badge
   */
  const verifyCreator = async (
    userId: number,
    verified: boolean,
    reason: string
  ): Promise<void> => {
    try {
      await adminApi.adminVerifyCreator(userId, verified, reason)

      // Note: User object doesn't have is_verified field in current schema
      // Backend handles the verification status in user record
    } catch (err: any) {
      error.value =
        err.response?.data?.message || 'Fehler beim Verifizieren des Creators'
      console.error('Failed to verify creator:', err)
      throw err
    }
  }

  // ============================================================================
  // Actions - Audit Logs (Phase B24-01)
  // ============================================================================

  /**
   * Load audit logs with filters
   */
  const loadAuditLogs = async (
    params: AuditLogsFilterParams = {}
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response: PaginatedResponse<AuditLog> = await adminApi.adminGetAuditLogs(
        params
      )

      auditLogs.value = response.items
      auditLogsTotal.value = response.total
      auditLogsPage.value = response.page
      auditLogsLimit.value = response.limit
      auditLogsTotalPages.value = response.total_pages
      auditLogsFilters.value = params
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Audit-Logs'
      console.error('Failed to load audit logs:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // ============================================================================
  // Actions - Organisations
  // ============================================================================

  /**
   * Load organisations with filters
   */
  const loadOrganisations = async (
    params: OrganisationsFilterParams = {}
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response: PaginatedResponse<AdminOrganisation> =
        await adminApi.adminGetOrganisations(params)

      organisations.value = response.items
      orgsTotal.value = response.total
      orgsPage.value = response.page
      orgsLimit.value = response.limit
      orgsTotalPages.value = response.total_pages
      orgFilters.value = params
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Organisationen'
      console.error('Failed to load organisations:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update organisation plan
   */
  const updateOrganisationPlan = async (
    orgId: number,
    planId: string
  ): Promise<void> => {
    try {
      await adminApi.adminUpdateOrganisationPlan(orgId, planId)

      // Update local state
      const org = organisations.value.find(o => o.organisation_id === orgId)
      if (org) {
        org.plan_id = planId
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Ändern des Plans'
      console.error('Failed to update organisation plan:', err)
      throw err
    }
  }

  /**
   * Add tokens to organisation
   */
  const addOrganisationTokens = async (
    orgId: number,
    amount: number,
    reason?: string
  ): Promise<void> => {
    try {
      await adminApi.adminAddOrganisationTokens(orgId, amount, reason)

      // Update local state
      const org = organisations.value.find(o => o.organisation_id === orgId)
      if (org) {
        org.token_pool += amount
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Hinzufügen von Tokens'
      console.error('Failed to add organisation tokens:', err)
      throw err
    }
  }

  // ============================================================================
  // Actions - Courses
  // ============================================================================

  /**
   * Load courses with filters
   */
  const loadCourses = async (params: CoursesFilterParams = {}): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response: PaginatedResponse<AdminCourse> = await adminApi.adminGetCourses(params)

      courses.value = response.items
      coursesTotal.value = response.total
      coursesPage.value = response.page
      coursesLimit.value = response.limit
      coursesTotalPages.value = response.total_pages
      courseFilters.value = params
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kurse'
      console.error('Failed to load courses:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Publish course
   */
  const publishCourse = async (courseId: number): Promise<void> => {
    try {
      await adminApi.adminPublishCourse(courseId)

      // Update local state
      const course = courses.value.find(c => c.course_id === courseId)
      if (course) {
        course.is_published = true
        course.status = 'published'
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Veröffentlichen des Kurses'
      console.error('Failed to publish course:', err)
      throw err
    }
  }

  /**
   * Unpublish course
   */
  const unpublishCourse = async (courseId: number): Promise<void> => {
    try {
      await adminApi.adminUnpublishCourse(courseId)

      // Update local state
      const course = courses.value.find(c => c.course_id === courseId)
      if (course) {
        course.is_published = false
        course.status = 'draft'
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Zurückziehen des Kurses'
      console.error('Failed to unpublish course:', err)
      throw err
    }
  }

  /**
   * Archive course
   */
  const archiveCourse = async (courseId: number): Promise<void> => {
    try {
      await adminApi.adminArchiveCourse(courseId)

      // Update local state
      const course = courses.value.find(c => c.course_id === courseId)
      if (course) {
        course.status = 'archived'
        course.is_published = false
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Archivieren des Kurses'
      console.error('Failed to archive course:', err)
      throw err
    }
  }

  /**
   * Delete course
   */
  const deleteCourse = async (courseId: number, reason?: string): Promise<void> => {
    try {
      await adminApi.adminDeleteCourse(courseId, reason)

      // Update local state (mark as archived, not removed)
      const course = courses.value.find(c => c.course_id === courseId)
      if (course) {
        course.status = 'archived'
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Löschen des Kurses'
      console.error('Failed to delete course:', err)
      throw err
    }
  }

  /**
   * Unarchive course
   */
  const unarchiveCourse = async (courseId: number, reason?: string): Promise<void> => {
    try {
      await adminApi.adminUnarchiveCourse(courseId, reason)

      // Update local state
      const course = courses.value.find(c => c.course_id === courseId)
      if (course) {
        course.status = 'draft'
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Wiederherstellen des Kurses'
      console.error('Failed to unarchive course:', err)
      throw err
    }
  }

  /**
   * Permanently delete course (hard delete)
   * WARNING: This cannot be undone!
   */
  const permanentDeleteCourse = async (courseId: number, reason?: string): Promise<void> => {
    try {
      await adminApi.adminPermanentDeleteCourse(courseId, reason)

      // Remove from local state completely
      courses.value = courses.value.filter(c => c.course_id !== courseId)
      coursesTotal.value -= 1
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim permanenten Löschen des Kurses'
      console.error('Failed to permanently delete course:', err)
      throw err
    }
  }

  /**
   * Get course detail
   */
  const getCourseDetail = async (courseId: number): Promise<adminApi.AdminCourseDetail> => {
    try {
      const course = await adminApi.adminGetCourseDetail(courseId)
      return course
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kursdetails'
      console.error('Failed to load course detail:', err)
      throw err
    }
  }

  /**
   * Create course
   */
  const createCourse = async (data: adminApi.AdminCourseCreateRequest): Promise<adminApi.AdminCourseDetail> => {
    try {
      const course = await adminApi.adminCreateCourse(data)

      // Add to local state
      courses.value.unshift(course as any)
      coursesTotal.value += 1

      return course
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Erstellen des Kurses'
      console.error('Failed to create course:', err)
      throw err
    }
  }

  /**
   * Update course
   */
  const updateCourse = async (
    courseId: number,
    data: adminApi.AdminCourseUpdateRequest
  ): Promise<adminApi.AdminCourseDetail> => {
    try {
      const updatedCourse = await adminApi.adminUpdateCourse(courseId, data)

      // Update local state
      const index = courses.value.findIndex(c => c.course_id === courseId)
      if (index !== -1) {
        courses.value[index] = { ...courses.value[index], ...updatedCourse }
      }

      return updatedCourse
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Aktualisieren des Kurses'
      console.error('Failed to update course:', err)
      throw err
    }
  }

  // ============================================================================
  // Actions - Chapters (Phase B24-03, refactored from modules 2025-11-27)
  // ============================================================================

  /**
   * Load chapters for a specific course
   * Refactored: loadCourseModules → loadCourseChapters (2025-11-27)
   */
  const loadCourseChapters = async (courseId: number): Promise<AdminChapter[]> => {
    loading.value = true
    error.value = null

    try {
      const chapters = await adminApi.adminGetCourseChapters(courseId)

      // Update state
      courseChapters.value.set(courseId, chapters)
      currentChapters.value = chapters

      return chapters
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kapitel'
      console.error('Failed to load course chapters:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create new chapter for a course
   * Refactored: createModule → createChapter (2025-11-27)
   */
  const createChapter = async (
    courseId: number,
    data: AdminChapterCreateRequest
  ): Promise<AdminChapter> => {
    try {
      const chapter = await adminApi.adminCreateChapter(courseId, data)

      // Update local state
      const chapters = courseChapters.value.get(courseId) || []
      chapters.push(chapter)
      courseChapters.value.set(courseId, chapters)
      currentChapters.value = chapters

      return chapter
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Erstellen des Kapitels'
      console.error('Failed to create chapter:', err)
      throw err
    }
  }

  /**
   * Update chapter metadata
   * Refactored: updateModule → updateChapter (2025-11-27)
   */
  const updateChapter = async (
    chapterId: string,
    data: AdminChapterUpdateRequest
  ): Promise<AdminChapter> => {
    try {
      const updatedChapter = await adminApi.adminUpdateChapter(chapterId, data)

      // Update local state
      for (const [courseId, chapters] of courseChapters.value.entries()) {
        const index = chapters.findIndex(c => c.chapter_id === chapterId)
        if (index !== -1) {
          chapters[index] = { ...chapters[index], ...updatedChapter }
          courseChapters.value.set(courseId, chapters)
          if (currentChapters.value === chapters) {
            currentChapters.value = [...chapters]
          }
          break
        }
      }

      return updatedChapter
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Aktualisieren des Kapitels'
      console.error('Failed to update chapter:', err)
      throw err
    }
  }

  /**
   * Delete chapter (cascades to lessons)
   * Refactored: deleteModule → deleteChapter (2025-11-27)
   */
  const deleteChapter = async (chapterId: string, reason?: string): Promise<void> => {
    try {
      await adminApi.adminDeleteChapter(chapterId, reason)

      // Update local state
      for (const [courseId, chapters] of courseChapters.value.entries()) {
        const filtered = chapters.filter(c => c.chapter_id !== chapterId)
        if (filtered.length !== chapters.length) {
          courseChapters.value.set(courseId, filtered)
          if (currentChapters.value === chapters) {
            currentChapters.value = filtered
          }
          break
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Löschen des Kapitels'
      console.error('Failed to delete chapter:', err)
      throw err
    }
  }

  /**
   * Reorder chapters in a course
   * Refactored: reorderModules → reorderChapters (2025-11-27)
   */
  const reorderChapters = async (courseId: number, chapterIds: string[]): Promise<void> => {
    try {
      await adminApi.adminReorderChapters(courseId, chapterIds)

      // Update local state
      const chapters = courseChapters.value.get(courseId)
      if (chapters) {
        // Reorder chapters array based on chapterIds
        const reordered = chapterIds
          .map(id => chapters.find(c => c.chapter_id === id))
          .filter(c => c !== undefined) as AdminChapter[]

        courseChapters.value.set(courseId, reordered)
        currentChapters.value = reordered
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Neu-Sortieren der Kapitel'
      console.error('Failed to reorder chapters:', err)
      throw err
    }
  }

  // ============================================================================
  // Actions - Categories (Phase B24-03)
  // ============================================================================

  /**
   * Load category tree (flexible unlimited-depth hierarchy, practical limit: 20 levels)
   */
  const loadCategoryTree = async (activeOnly: boolean = true, forceReload: boolean = false): Promise<void> => {
    if (categoriesLoaded.value && !forceReload) return

    loading.value = true
    error.value = null

    try {
      const result = await adminApi.adminGetCategoriesTree(activeOnly)
      // API returns { tree: { categories: [...], total_categories, ... } }
      // We need to extract the categories array from the tree object
      categoryTree.value = result.tree?.categories || result.tree || []
      categoriesLoaded.value = true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kategorien'
      console.error('Failed to load category tree:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Load flat list of categories
   */
  const loadCategories = async (params?: adminApi.CategoryFilterParams): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const categories = await adminApi.adminGetCategories(params)
      categoriesFlat.value = categories
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kategorien'
      console.error('Failed to load categories:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Find category by ID (from tree or flat list)
   */
  const findCategoryById = (categoryId: number): Category | CategoryTreeNode | null => {
    // Search in flat list first
    const flatCategory = categoriesFlat.value.find(c => c.category_id === categoryId)
    if (flatCategory) return flatCategory

    // Search in tree recursively
    const searchTree = (nodes: CategoryTreeNode[]): CategoryTreeNode | null => {
      for (const node of nodes) {
        if (node.category_id === categoryId) return node
        if (node.children.length > 0) {
          const found = searchTree(node.children)
          if (found) return found
        }
      }
      return null
    }

    return searchTree(categoryTree.value)
  }

  /**
   * Create a new category
   */
  const createCategory = async (categoryData: any): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await adminApi.adminCreateCategory(categoryData)
      categoriesLoaded.value = false // Force reload on next loadCategoryTree
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Erstellen der Kategorie'
      console.error('Failed to create category:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update an existing category
   */
  const updateCategory = async (categoryId: number, categoryData: any): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await adminApi.adminUpdateCategory(categoryId, categoryData)
      categoriesLoaded.value = false // Force reload on next loadCategoryTree
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Aktualisieren der Kategorie'
      console.error('Failed to update category:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete a category
   */
  const deleteCategory = async (categoryId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await adminApi.adminDeleteCategory(categoryId)
      categoriesLoaded.value = false // Force reload on next loadCategoryTree
    } catch (err: any) {
      // Extract meaningful error message from API response
      const errorMessage = err.response?.data?.message ||
                          err.response?.data?.error ||
                          'Fehler beim Löschen der Kategorie'
      error.value = errorMessage
      console.error('Failed to delete category:', err)
      // Throw error with proper message for UI handling
      const customError = new Error(errorMessage)
      throw customError
    } finally {
      loading.value = false
    }
  }

  // ============================================================================
  // Actions - Billing
  // ============================================================================

  /**
   * Load plan overview
   */
  const loadPlans = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const plansData = await adminApi.adminGetPlanOverview()
      plans.value = plansData
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Pläne'
      console.error('Failed to load plans:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // ============================================================================
  // Actions - Analytics
  // ============================================================================

  /**
   * Load admin analytics (time series & top lists)
   */
  const loadAdminAnalytics = async (timeframe: 7 | 30 | 90 = 7): Promise<void> => {
    systemAnalyticsLoading.value = true
    systemAnalyticsError.value = null

    try {
      // Fetch all analytics data in parallel
      const [eventsTimeSeries, activeUsersTimeSeries, topCourses, topMethods] =
        await Promise.all([
          adminApi.adminGetEventsTimeSeries({ days: timeframe }),
          adminApi.adminGetActiveUsersTimeSeries({ days: timeframe }),
          adminApi.adminGetTopCourses({ days: timeframe, limit: 10 }),
          adminApi.adminGetTopMethods({ days: timeframe, limit: 10 })
        ])

      systemAnalytics.value = {
        timeframe,
        eventsTimeSeries,
        activeUsersTimeSeries,
        topCourses,
        topMethods
      }
    } catch (err: any) {
      systemAnalyticsError.value =
        err.response?.data?.message || 'Fehler beim Laden der Analytics-Daten'
      console.error('Failed to load admin analytics:', err)
      throw err
    } finally {
      systemAnalyticsLoading.value = false
    }
  }

  /**
   * Change analytics timeframe (and reload data)
   */
  const changeAnalyticsTimeframe = async (timeframe: 7 | 30 | 90): Promise<void> => {
    await loadAdminAnalytics(timeframe)
  }

  // ============================================================================
  // Actions - AI Jobs (Phase B24-05)
  // ============================================================================

  /**
   * Start AI Job
   * Creates a new AI job and starts the worker
   * @param file - Optional file to process (PDF, DOCX, PPTX, TXT)
   * @param prompt - Optional custom prompt text
   * @param promptId - Optional prompt template ID from prompt registry
   * @param model - Optional AI model override (Phase C3.4)
   */
  const startAIJob = async (
    file?: File,
    prompt?: string,
    promptId?: string,
    model?: string
  ): Promise<adminApi.AIJob> => {
    aiJobLoading.value = true
    aiJobError.value = null

    try {
      const formData = new FormData()
      formData.append('type', 'course_from_pdf')
      if (file) {
        formData.append('file', file)
      }
      if (prompt) {
        formData.append('prompt', prompt)
      }
      if (promptId) {
        formData.append('prompt_id', promptId)
      }
      // Phase C3.4: AI Model Override
      if (model) {
        formData.append('model', model)
      }

      const job = await adminApi.adminStartAIJob(formData)

      // Store job in map
      aiJobs.value.set(job.id, job)
      currentAIJob.value = job

      // Start polling if job is processing
      if (job.status === 'pending' || job.status === 'processing') {
        startAIJobPolling(job.id)
      }

      return job
    } catch (err: any) {
      aiJobError.value = err.response?.data?.message || 'Fehler beim Starten des AI-Jobs'
      console.error('Failed to start AI job:', err)
      throw err
    } finally {
      aiJobLoading.value = false
    }
  }

  /**
   * Poll AI Job Status
   * Fetches job status and updates state
   */
  const pollAIJob = async (jobId: string): Promise<adminApi.AIJob> => {
    try {
      const job = await adminApi.adminGetAIJob(jobId)

      // Update job in map
      aiJobs.value.set(jobId, job)

      // Update current job if it's the one being polled
      if (currentAIJob.value?.id === jobId) {
        currentAIJob.value = job
      }

      // Stop polling if job is finished
      if (['completed', 'failed', 'cancelled'].includes(job.status)) {
        stopAIJobPolling()
      }

      return job
    } catch (err: any) {
      aiJobError.value = err.response?.data?.message || 'Fehler beim Abrufen des Job-Status'
      console.error('Failed to poll AI job:', err)
      throw err
    }
  }

  /**
   * Start polling for AI job updates
   * Polls every 1500ms until job is completed/failed/cancelled
   */
  const startAIJobPolling = (jobId: string): void => {
    // Stop any existing polling
    stopAIJobPolling()

    // Start new polling interval
    aiJobPollingInterval.value = window.setInterval(async () => {
      try {
        await pollAIJob(jobId)
      } catch (err) {
        console.error('Polling error:', err)
        stopAIJobPolling()
      }
    }, 1500)
  }

  /**
   * Stop polling for AI job updates
   */
  const stopAIJobPolling = (): void => {
    if (aiJobPollingInterval.value !== null) {
      clearInterval(aiJobPollingInterval.value)
      aiJobPollingInterval.value = null
    }
  }

  /**
   * Get AI Job by ID
   * Fetches job from API and updates local state
   */
  const getAIJob = async (jobId: string): Promise<adminApi.AIJob> => {
    aiJobLoading.value = true
    aiJobError.value = null

    try {
      const job = await adminApi.adminGetAIJob(jobId)

      // Store job in map
      aiJobs.value.set(jobId, job)
      currentAIJob.value = job

      // Start polling if job is still processing
      if (job.status === 'pending' || job.status === 'processing') {
        startAIJobPolling(job.id)
      }

      return job
    } catch (err: any) {
      aiJobError.value = err.response?.data?.message || 'Fehler beim Laden des AI-Jobs'
      console.error('Failed to get AI job:', err)
      throw err
    } finally {
      aiJobLoading.value = false
    }
  }

  /**
   * Cancel AI Job
   * Cancels a pending or processing job
   */
  const cancelAIJob = async (jobId: string): Promise<void> => {
    try {
      await adminApi.adminCancelAIJob(jobId)

      // Stop polling
      stopAIJobPolling()

      // Update job in map
      const job = aiJobs.value.get(jobId)
      if (job) {
        job.status = 'cancelled'
        aiJobs.value.set(jobId, job)

        if (currentAIJob.value?.id === jobId) {
          currentAIJob.value = job
        }
      }
    } catch (err: any) {
      aiJobError.value = err.response?.data?.message || 'Fehler beim Abbrechen des Jobs'
      console.error('Failed to cancel AI job:', err)
      throw err
    }
  }

  /**
   * Finalize AI Job
   * Creates actual course, modules, and lessons from AI output
   * Returns the created course ID for navigation
   */
  const finalizeAIJob = async (
    jobId: string,
    options?: adminApi.AIJobFinalizeRequest
  ): Promise<number> => {
    aiJobLoading.value = true
    aiJobError.value = null

    try {
      const response = await adminApi.adminFinalizeAIJob(jobId, options)

      // Stop polling
      stopAIJobPolling()

      // Update job in map (mark as consumed)
      const job = aiJobs.value.get(jobId)
      if (job) {
        job.course_id = response.course_id.toString()
        aiJobs.value.set(jobId, job)

        if (currentAIJob.value?.id === jobId) {
          currentAIJob.value = job
        }
      }

      return response.course_id
    } catch (err: any) {
      aiJobError.value = err.response?.data?.message || 'Fehler beim Finalisieren des Jobs'
      console.error('Failed to finalize AI job:', err)
      throw err
    } finally {
      aiJobLoading.value = false
    }
  }

  /**
   * Clear current AI job
   * Stops polling and clears current job state
   */
  const clearCurrentAIJob = (): void => {
    stopAIJobPolling()
    currentAIJob.value = null
    aiJobError.value = null
  }

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State - Users
    users,
    usersTotal,
    usersPage,
    usersLimit,
    usersTotalPages,
    userFilters,

    // State - Organisations
    organisations,
    orgsTotal,
    orgsPage,
    orgsLimit,
    orgsTotalPages,
    orgFilters,

    // State - Courses
    courses,
    coursesTotal,
    coursesPage,
    coursesLimit,
    coursesTotalPages,
    courseFilters,

    // State - Chapters (Phase B24-03, refactored 2025-11-27)
    courseChapters,
    currentChapters,

    // State - Categories (Phase B24-03)
    categoryTree,
    categoriesFlat,
    categoriesLoaded,

    // State - System
    systemStats,
    tokenStats,
    plans,

    // State - Audit Logs (Phase B24-01)
    auditLogs,
    auditLogsTotal,
    auditLogsPage,
    auditLogsLimit,
    auditLogsTotalPages,
    auditLogsFilters,

    // State - Analytics
    systemAnalytics,
    systemAnalyticsLoading,
    systemAnalyticsError,

    // State - AI Jobs (Phase B24-05)
    aiJobs,
    currentAIJob,
    aiJobLoading,
    aiJobError,

    // State - UI
    loading,
    error,

    // Getters
    hasSystemStats,
    totalUsersCount,
    activeUsersCount,
    totalOrgsCount,
    totalCoursesCount,
    hasAnalytics,
    analyticsTimeframe,

    // Actions - Dashboard
    loadAdminDashboard,

    // Actions - Users
    loadUsers,
    updateUserRole,
    toggleUserActive,
    deleteUser,
    createUser,

    // Actions - Users (Phase B24-01)
    banUser,
    unbanUser,
    grantTokens,
    verifyCreator,

    // Actions - Audit Logs (Phase B24-01)
    loadAuditLogs,

    // Actions - Organisations
    loadOrganisations,
    updateOrganisationPlan,
    addOrganisationTokens,

    // Actions - Courses
    loadCourses,
    getCourseDetail,
    createCourse,
    updateCourse,
    publishCourse,
    unpublishCourse,
    archiveCourse,
    unarchiveCourse,
    deleteCourse,
    permanentDeleteCourse,

    // Actions - Chapters (Phase B24-03, refactored 2025-11-27)
    loadCourseChapters,
    createChapter,
    updateChapter,
    deleteChapter,
    reorderChapters,

    // Actions - Categories (Phase B24-03)
    loadCategoryTree,
    loadCategories,
    findCategoryById,
    createCategory,
    updateCategory,
    deleteCategory,

    // Actions - Billing
    loadPlans,

    // Actions - Analytics
    loadAdminAnalytics,
    changeAnalyticsTimeframe,

    // Actions - AI Jobs (Phase B24-05)
    startAIJob,
    pollAIJob,
    getAIJob,
    cancelAIJob,
    finalizeAIJob,
    clearCurrentAIJob,
    startAIJobPolling,
    stopAIJobPolling
  }
})
