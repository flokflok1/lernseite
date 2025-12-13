/**
 * LernsystemX - Admin API
 *
 * API endpoints for global system administration:
 * - User Management
 * - Organisation Management
 * - Course Management
 * - Billing & Tokens
 * - System Analytics
 */

import http from './http'

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface AdminUser {
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

export interface AdminOrganisation {
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

export interface AdminCourse {
  course_id: string  // UUID
  title: string
  description?: string | null
  long_description?: string | null  // C1.1
  creator_id: string  // UUID
  creator_name?: string
  creator_email?: string  // C1.1
  organisation_id?: string | null  // UUID
  organisation_name?: string | null
  category?: string | null
  level?: string
  language: string
  price?: number
  is_public: boolean
  status: 'draft' | 'published' | 'archived'
  thumbnail_url?: string | null  // Cover
  preview_video_url?: string | null
  tags?: string[]
  chapter_count: number
  enrollment_count: number

  // C1.1 New fields
  ad_enabled?: boolean
  learning_goals?: string[]
  target_audience?: string | null

  created_at: string
  updated_at?: string | null
  published_at?: string | null
  archived_at?: string | null
}

export interface AdminTokenStats {
  total_tokens_purchased: number
  total_tokens_used: number
  total_tokens_available: number
  tokens_used_today: number
  tokens_used_7_days: number
  tokens_used_30_days: number
  top_consumers?: Array<{
    user_id: number
    user_name: string
    tokens_used: number
  }>
}

export interface AdminSystemStats {
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

export interface AdminPlanOverview {
  plan_id: string
  plan_name: string
  price: number
  currency: string
  features: string[]
  subscriber_count: number
}

export interface UsersFilterParams {
  page?: number
  limit?: number
  search?: string
  role?: string
  status?: 'active' | 'inactive'
  organisation_id?: number
}

export interface OrganisationsFilterParams {
  page?: number
  limit?: number
  search?: string
  type?: 'school' | 'company' | 'teacher_team' | 'creator_team'
  status?: 'active' | 'inactive'
}

export interface CoursesFilterParams {
  page?: number
  per_page?: number
  search?: string
  status?: 'all' | 'draft' | 'published' | 'archived'
  creator_id?: number
  organisation_id?: number
  category?: string
  category_id?: number
  level?: string
  language?: string
  sort?: 'created_at' | 'updated_at' | 'title' | 'enrollment_count'
  order?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// ============================================================================
// Phase B24-01: Admin User Management Types
// ============================================================================

export interface BanUserRequest {
  reason: string
  duration_days?: number
  permanent: boolean
  notify_user: boolean
}

export interface UnbanUserRequest {
  reason: string
}

export interface GrantTokensRequest {
  amount: number
  reason: string
}

export interface VerifyCreatorRequest {
  verified: boolean
  reason: string
}

export interface AuditLog {
  log_id: number
  user_id?: number | null
  user_email?: string | null
  user_role?: string | null
  action: string
  event_category?: string | null
  resource_type?: string | null
  resource_id?: number | null
  description?: string | null
  ip_address?: string | null
  user_agent?: string | null
  session_id?: string | null
  success: boolean
  error_message?: string | null
  created_at: string
  meta?: Record<string, any>
}

export interface AuditLogsFilterParams {
  page?: number
  limit?: number
  user_id?: number
  action?: string
  event_category?: string
  from?: string
  to?: string
  success?: boolean
}

// ============================================================================
// User Management
// ============================================================================

/**
 * Get all users (admin only)
 */
export const adminGetUsers = async (
  params: UsersFilterParams = {}
): Promise<PaginatedResponse<AdminUser>> => {
  const response = await http.get<{
    success: boolean
    users: AdminUser[]
    total: number
    page: number
    limit: number
    total_pages: number
  }>('/admin/users', { params })

  return {
    items: response.data.users,
    total: response.data.total,
    page: response.data.page,
    limit: response.data.limit,
    total_pages: response.data.total_pages
  }
}

/**
 * Get user details (admin)
 */
export const adminGetUserDetail = async (userId: string): Promise<AdminUser> => {
  const response = await http.get<{
    success: boolean
    user: AdminUser
  }>(`/admin/users/${userId}`)

  return response.data.user
}

/**
 * Update user role (admin)
 */
export const adminUpdateUserRole = async (
  userId: string,
  role: string
): Promise<void> => {
  await http.patch(`/admin/users/${userId}/role`, { role })
}

/**
 * Toggle user active status (admin)
 */
export const adminToggleUserActive = async (
  userId: string,
  isActive: boolean
): Promise<void> => {
  await http.patch(`/admin/users/${userId}/status`, {
    is_active: isActive
  })
}

/**
 * Delete user (admin)
 */
export const adminDeleteUser = async (userId: string): Promise<void> => {
  await http.delete(`/admin/users/${userId}`)
}

// ============================================================================
// Phase B24-01: Admin User Management - Ban, Unban, Grant, Verify
// ============================================================================

/**
 * Ban user (admin only)
 * Prevents user from logging in and accessing the system
 */
export const adminBanUser = async (
  userId: string,
  data: BanUserRequest
): Promise<void> => {
  await http.post(`/admin/users/${userId}/ban`, data)
}

/**
 * Unban user (admin only)
 * Restores user access to the system
 */
export const adminUnbanUser = async (
  userId: string,
  reason: string
): Promise<void> => {
  await http.post(`/admin/users/${userId}/unban`, { reason })
}

/**
 * Grant tokens to user (admin only)
 * Adds tokens to user's wallet for AI operations
 */
export const adminGrantTokens = async (
  userId: string,
  amount: number,
  reason: string
): Promise<number> => {
  const response = await http.post<{
    success: boolean
    new_balance: number
  }>(`/admin/users/${userId}/tokens/grant`, {
    amount,
    reason
  })

  return response.data.new_balance
}

/**
 * Verify creator status (admin only)
 * Verifies or revokes creator verification badge
 */
export const adminVerifyCreator = async (
  userId: string,
  verified: boolean,
  reason: string
): Promise<void> => {
  await http.post(`/admin/users/${userId}/verify-creator`, {
    verified,
    reason
  })
}

/**
 * Get audit logs (admin only)
 * Retrieves system audit logs with filtering
 */
export const adminGetAuditLogs = async (
  params: AuditLogsFilterParams = {}
): Promise<PaginatedResponse<AuditLog>> => {
  const response = await http.get<{
    success: boolean
    logs: AuditLog[]
    total: number
    page: number
    limit: number
    total_pages: number
  }>('/admin/audit-logs', { params })

  return {
    items: response.data.logs,
    total: response.data.total,
    page: response.data.page,
    limit: response.data.limit,
    total_pages: response.data.total_pages
  }
}

// ============================================================================
// Organisation Management
// ============================================================================

/**
 * Get all organisations (admin)
 */
export const adminGetOrganisations = async (
  params: OrganisationsFilterParams = {}
): Promise<PaginatedResponse<AdminOrganisation>> => {
  const response = await http.get<{
    success: boolean
    organisations: AdminOrganisation[]
    total: number
    page: number
    limit: number
    total_pages: number
  }>('/admin/organisations', { params })

  return {
    items: response.data.organisations,
    total: response.data.total,
    page: response.data.page,
    limit: response.data.limit,
    total_pages: response.data.total_pages
  }
}

/**
 * Get organisation detail (admin)
 */
export const adminGetOrganisationDetail = async (
  orgId: number
): Promise<AdminOrganisation> => {
  const response = await http.get<{
    success: boolean
    organisation: AdminOrganisation
  }>(`/admin/organisations/${orgId}`)

  return response.data.organisation
}

/**
 * Update organisation plan (admin)
 */
export const adminUpdateOrganisationPlan = async (
  orgId: number,
  planId: string
): Promise<void> => {
  await http.patch(`/admin/organisations/${orgId}/plan`, {
    plan_id: planId
  })
}

/**
 * Add tokens to organisation (admin)
 */
export const adminAddOrganisationTokens = async (
  orgId: number,
  amount: number,
  reason?: string
): Promise<void> => {
  await http.post(`/admin/organisations/${orgId}/tokens`, {
    amount,
    reason
  })
}

// ============================================================================
// Course Management (Phase B24-02)
// ============================================================================

export interface AdminCourseDetail {
  course_id: string  // UUID
  title: string
  description?: string | null
  long_description?: string | null  // C1.1
  creator_id: string  // UUID
  creator_name?: string
  creator_email?: string
  organisation_id?: string | null  // UUID
  organisation_name?: string | null
  category?: string | null
  category_id?: number | null
  category_name?: string | null
  level?: string
  language: string
  price?: number
  is_public: boolean
  status: 'draft' | 'published' | 'archived'
  thumbnail_url?: string | null  // Cover
  preview_video_url?: string | null
  tags?: string[]
  chapter_count: number
  enrollment_count: number

  // C1.1 New fields
  ad_enabled?: boolean
  learning_goals?: string[]
  target_audience?: string | null

  created_at: string
  updated_at?: string | null
  published_at?: string | null
  archived_at?: string | null
}

export interface AdminCourseCreateRequest {
  title: string
  description?: string
  creator_id: string  // UUID string
  organisation_id?: string | null  // UUID string
  category_id?: number | null  // Category ID (references course_categories table)
  level?: string
  language?: string
  price?: number
  is_public?: boolean
  thumbnail_url?: string
  preview_video_url?: string
  tags?: string[]
}

export interface AdminCourseUpdateRequest {
  title?: string
  description?: string
  category_id?: number | null
  category?: string
  level?: string
  language?: string
  price?: number
  is_public?: boolean
  thumbnail_url?: string
  preview_video_url?: string
  tags?: string[]
}

/**
 * Get all courses (admin)
 */
export const adminGetCourses = async (
  params: CoursesFilterParams = {}
): Promise<PaginatedResponse<AdminCourse>> => {
  const response = await http.get<{
    success: boolean
    courses: AdminCourse[]
    pagination: {
      total: number
      page: number
      per_page: number
      total_pages: number
    }
  }>('/admin/courses', { params })

  return {
    items: response.data.courses,
    total: response.data.pagination.total,
    page: response.data.pagination.page,
    limit: response.data.pagination.per_page,
    total_pages: response.data.pagination.total_pages
  }
}

/**
 * Get course details (admin)
 */
export const adminGetCourseDetail = async (courseId: string): Promise<AdminCourseDetail> => {
  const response = await http.get<{
    success: boolean
    course: AdminCourseDetail
  }>(`/admin/courses/${courseId}`)

  return response.data.course
}

/**
 * Create course (admin)
 */
export const adminCreateCourse = async (
  data: AdminCourseCreateRequest
): Promise<AdminCourseDetail> => {
  const response = await http.post<{
    success: boolean
    course: AdminCourseDetail
  }>('/admin/courses', data)

  return response.data.course
}

/**
 * Update course metadata (admin)
 */
export const adminUpdateCourse = async (
  courseId: string,
  data: AdminCourseUpdateRequest
): Promise<AdminCourseDetail> => {
  const response = await http.patch<{
    success: boolean
    course: AdminCourseDetail
  }>(`/admin/courses/${courseId}`, data)

  return response.data.course
}

/**
 * Change course status (admin)
 */
export const adminChangeCourseStatus = async (
  courseId: string,
  action: 'publish' | 'unpublish' | 'archive' | 'unarchive',
  reason?: string
): Promise<string> => {
  const response = await http.post<{
    success: boolean
    status: string
  }>(`/admin/courses/${courseId}/status`, {
    action,
    reason
  })

  return response.data.status
}

/**
 * Publish course (admin) - convenience wrapper
 */
export const adminPublishCourse = async (courseId: string, reason?: string): Promise<void> => {
  await adminChangeCourseStatus(courseId, 'publish', reason)
}

/**
 * Unpublish course (admin) - convenience wrapper
 */
export const adminUnpublishCourse = async (courseId: string, reason?: string): Promise<void> => {
  await adminChangeCourseStatus(courseId, 'unpublish', reason)
}

/**
 * Archive course (admin) - convenience wrapper
 */
export const adminArchiveCourse = async (courseId: string, reason?: string): Promise<void> => {
  await adminChangeCourseStatus(courseId, 'archive', reason)
}

/**
 * Unarchive course (admin) - convenience wrapper
 */
export const adminUnarchiveCourse = async (courseId: string, reason?: string): Promise<void> => {
  await adminChangeCourseStatus(courseId, 'unarchive', reason)
}

/**
 * Delete course (admin) - soft delete via archive
 */
export const adminDeleteCourse = async (courseId: string, reason?: string): Promise<void> => {
  await http.delete(`/admin/courses/${courseId}`, {
    data: { reason }
  })
}

/**
 * Permanently delete a course (hard delete)
 * WARNING: This cannot be undone!
 */
export const adminPermanentDeleteCourse = async (courseId: string, reason?: string): Promise<void> => {
  await http.delete(`/admin/courses/${courseId}/permanent`, {
    data: { confirm: true, reason }
  })
}

// ============================================================================
// Billing & Tokens
// ============================================================================

/**
 * Get global token statistics (admin)
 */
export const adminGetGlobalTokenStats = async (): Promise<AdminTokenStats> => {
  const response = await http.get<{
    success: boolean
    stats: AdminTokenStats
  }>('/admin/tokens/stats')

  return response.data.stats
}

/**
 * Get plan overview (admin)
 */
export const adminGetPlanOverview = async (): Promise<AdminPlanOverview[]> => {
  const response = await http.get<{
    success: boolean
    plans: AdminPlanOverview[]
  }>('/admin/billing/plans')

  return response.data.plans
}

// ============================================================================
// System Analytics
// ============================================================================

/**
 * Get system-wide statistics (admin dashboard)
 */
export const adminGetSystemStats = async (): Promise<AdminSystemStats> => {
  const response = await http.get<{
    success: boolean
    data: AdminSystemStats
  }>('/admin/stats/system')

  return response.data.data
}

/**
 * Get active users (7/30 days)
 */
export const adminGetActiveUsers = async (
  days: 7 | 30
): Promise<{ count: number; users: AdminUser[] }> => {
  const response = await http.get<{
    success: boolean
    count: number
    users: AdminUser[]
  }>(`/admin/analytics/active-users?days=${days}`)

  return {
    count: response.data.count,
    users: response.data.users
  }
}

// ============================================================================
// Phase 2.1 - Admin Dashboard Stats
// ============================================================================

export interface UserStatsData {
  total_users: number
  active_users: number
  banned_users: number
  new_users_30d: number
}

export interface CourseStatsData {
  total_courses: number
  published: number
  pending_review: number
  rejected: number
}

export interface SystemStatsData {
  uptime: number
  db_latency: number
  request_count_24h: number
  error_rate: number
}

/**
 * Get user statistics for admin dashboard (Phase 2.1)
 */
export const adminGetUserStats = async (): Promise<UserStatsData> => {
  const response = await http.get<{
    success: boolean
    data: UserStatsData
  }>('/admin/stats/users')

  return response.data.data
}

/**
 * Get course statistics for admin dashboard (Phase 2.1)
 */
export const adminGetCourseStats = async (): Promise<CourseStatsData> => {
  const response = await http.get<{
    success: boolean
    data: CourseStatsData
  }>('/admin/stats/courses')

  return response.data.data
}

/**
 * Get system statistics for admin dashboard (Phase 2.1)
 */
export const adminGetSystemStatsData = async (): Promise<SystemStatsData> => {
  const response = await http.get<{
    success: boolean
    data: SystemStatsData
  }>('/admin/stats/system')

  return response.data.data
}

// ============================================================================
// Advanced Analytics
// ============================================================================

export interface TimeSeriesPoint {
  date: string
  value: number
}

export interface AdminAnalyticsCourse {
  course_id: number
  title: string
  events_count: number
  enrollments: number
  completions: number
  avg_completion_rate?: number
}

export interface AdminAnalyticsMethod {
  method_id: number
  name: string
  calls: number
  tokens_used?: number
  avg_tokens?: number
}

/**
 * Get events time series (admin)
 */
export const adminGetEventsTimeSeries = async (params: {
  from?: string
  to?: string
  days?: 7 | 30 | 90
}): Promise<TimeSeriesPoint[]> => {
  const response = await http.get<{
    success: boolean
    data: TimeSeriesPoint[]
  }>('/admin/analytics/events/time-series', { params })

  return response.data.data
}

/**
 * Get active users time series (admin)
 */
export const adminGetActiveUsersTimeSeries = async (params: {
  from?: string
  to?: string
  days?: 7 | 30 | 90
}): Promise<TimeSeriesPoint[]> => {
  const response = await http.get<{
    success: boolean
    data: TimeSeriesPoint[]
  }>('/admin/analytics/active-users/time-series', { params })

  return response.data.data
}

/**
 * Get top courses (admin)
 */
export const adminGetTopCourses = async (params?: {
  limit?: number
  days?: 7 | 30 | 90
}): Promise<AdminAnalyticsCourse[]> => {
  const response = await http.get<{
    success: boolean
    courses: AdminAnalyticsCourse[]
  }>('/admin/analytics/top-courses', { params })

  return response.data.courses
}

/**
 * Get top learning methods (admin)
 */
export const adminGetTopMethods = async (params?: {
  limit?: number
  days?: 7 | 30 | 90
}): Promise<AdminAnalyticsMethod[]> => {
  const response = await http.get<{
    success: boolean
    methods: AdminAnalyticsMethod[]
  }>('/admin/analytics/top-methods', { params })

  return response.data.methods
}

// ============================================================================
// Phase B24-03: Chapter Management + Category Picker (Refactored: modules → chapters 2025-11-27)
// ============================================================================

export interface AdminChapter {
  chapter_id: string  // UUID (Refactored: module_id → chapter_id)
  course_id: string  // UUID
  title: string
  description?: string | null
  order_index: number
  duration_minutes: number
  has_video: boolean
  has_quiz: boolean
  has_exam: boolean
  lesson_count?: number
  total_lesson_duration?: number
  created_at: string
  updated_at?: string | null
}

// ============================================================================
// Phase B24-04: Lesson Management
// ============================================================================

export type LessonType = 'text' | 'video' | 'quiz' | 'interactive' | 'assignment' | 'discussion'

export interface AdminLesson {
  lesson_id: string  // UUID
  chapter_id: string  // UUID (Refactored: module_id → chapter_id 2025-11-27)
  title: string
  lesson_type: LessonType
  content?: Record<string, any> | null
  duration_minutes: number
  order_index: number
  published: boolean
  free_preview: boolean
  created_at: string
  updated_at?: string | null
}

export interface AdminLessonCreateRequest {
  title: string
  lesson_type?: LessonType
  content?: Record<string, any>
  duration_minutes?: number
  published?: boolean
  free_preview?: boolean
}

export interface AdminLessonUpdateRequest {
  title?: string
  lesson_type?: LessonType
  content?: Record<string, any>
  duration_minutes?: number
  order_index?: number
  published?: boolean
  free_preview?: boolean
}

export interface AdminChapterCreateRequest {
  title: string
  description?: string
  order_index?: number
  duration_minutes?: number
  has_video?: boolean
  has_quiz?: boolean
  has_exam?: boolean
}

export interface AdminChapterUpdateRequest {
  title?: string
  description?: string
  order_index?: number
  duration_minutes?: number
  has_video?: boolean
  has_quiz?: boolean
  has_exam?: boolean
}

export interface Category {
  category_id: number
  name: string
  slug: string
  description?: string | null
  parent_id?: number | null
  level: number
  is_active: boolean
  created_at: string
  updated_at?: string | null
  // New fields for flexible hierarchy (unlimited depth)
  path?: string | null
  root_id?: number | null
  path_ids?: number[] | null
  course_count?: number
  total_course_count?: number
  // Multi-language support
  name_en?: string | null
  name_es?: string | null
  name_fr?: string | null
  // Tree representation
  children?: Category[]
  has_children?: boolean
  icon?: string | null
  color?: string | null
  order_index?: number
}

export interface CategoryTreeNode {
  category_id: number
  name: string
  slug: string
  description?: string | null
  level: number
  is_active: boolean
  children: CategoryTreeNode[]
  // New fields for flexible hierarchy (unlimited depth)
  path?: string | null
  root_id?: number | null
  path_ids?: number[] | null
  course_count?: number
  total_course_count?: number
  has_children?: boolean
  icon?: string | null
  color?: string | null
  order_index?: number
  parent_id?: number | null
}

export interface CategoryTree {
  tree: CategoryTreeNode[]
  total_categories?: number
  max_level?: number
  active_categories?: number
}

export interface CategoryFilterParams {
  active_only?: boolean
  level?: number
  parent_id?: number
}

/**
 * Get category tree (admin/public)
 * Returns hierarchical category structure (unlimited depth, practical limit: 20 levels)
 */
export const adminGetCategoriesTree = async (activeOnly: boolean = true): Promise<CategoryTree> => {
  const response = await http.get<{
    success: boolean
    tree: CategoryTreeNode[]
  }>('/categories/tree', {
    params: { active_only: activeOnly }
  })

  return { tree: response.data.tree }
}

/**
 * Get all categories (flat list)
 */
export const adminGetCategories = async (params?: CategoryFilterParams): Promise<Category[]> => {
  const response = await http.get<{
    success: boolean
    categories: Category[]
  }>('/categories', { params })

  return response.data.categories
}

/**
 * Admin: Create a new category
 */
export const adminCreateCategory = async (categoryData: any): Promise<Category> => {
  const response = await http.post<{
    success: boolean
    category: Category
  }>('/admin/categories', categoryData)

  return response.data.category
}

/**
 * Admin: Update an existing category
 */
export const adminUpdateCategory = async (categoryId: number, categoryData: any): Promise<Category> => {
  const response = await http.patch<{
    success: boolean
    category: Category
  }>(`/admin/categories/${categoryId}`, categoryData)

  return response.data.category
}

/**
 * Admin: Delete a category
 */
export const adminDeleteCategory = async (categoryId: number): Promise<void> => {
  await http.delete(`/admin/categories/${categoryId}`)
}

/**
 * Get all chapters for a course (admin)
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminGetCourseChapters = async (courseId: string): Promise<AdminChapter[]> => {
  const response = await http.get<{
    success: boolean
    chapters: AdminChapter[]
  }>(`/admin/courses/${courseId}/chapters`)

  return response.data.chapters
}

/**
 * Create new chapter for a course (admin)
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminCreateChapter = async (
  courseId: string,
  data: AdminChapterCreateRequest
): Promise<AdminChapter> => {
  const response = await http.post<{
    success: boolean
    chapter: AdminChapter
  }>(`/admin/courses/${courseId}/chapters`, data)

  return response.data.chapter
}

/**
 * Update chapter metadata (admin)
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminUpdateChapter = async (
  chapterId: string,
  data: AdminChapterUpdateRequest
): Promise<AdminChapter> => {
  const response = await http.patch<{
    success: boolean
    chapter: AdminChapter
  }>(`/admin/chapters/${chapterId}`, data)

  return response.data.chapter
}

/**
 * Delete chapter (admin)
 * Cascades to lessons
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminDeleteChapter = async (chapterId: string, reason?: string): Promise<void> => {
  await http.delete(`/admin/chapters/${chapterId}`, {
    data: { reason }
  })
}

/**
 * Reorder chapters in a course (admin)
 * @param courseId - Course UUID
 * @param chapterIds - Array of chapter IDs in desired order
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminReorderChapters = async (
  courseId: string,
  chapterIds: string[]
): Promise<void> => {
  await http.post(`/admin/courses/${courseId}/chapters/reorder`, {
    chapter_ids: chapterIds
  })
}

// ============================================================================
// Phase B24-04: Lesson Management API
// ============================================================================

/**
 * Get all lessons for a chapter (admin)
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminGetChapterLessons = async (chapterId: string): Promise<AdminLesson[]> => {
  const response = await http.get<{
    success: boolean
    lessons: AdminLesson[]
  }>(`/admin/chapters/${chapterId}/lessons`)

  return response.data.lessons
}

/**
 * Create new lesson for a chapter (admin)
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminCreateLesson = async (
  chapterId: string,
  data: AdminLessonCreateRequest
): Promise<AdminLesson> => {
  const response = await http.post<{
    success: boolean
    lesson: AdminLesson
  }>(`/admin/chapters/${chapterId}/lessons`, data)

  return response.data.lesson
}

/**
 * Update lesson (admin)
 */
export const adminUpdateLesson = async (
  lessonId: string,
  data: AdminLessonUpdateRequest
): Promise<AdminLesson> => {
  const response = await http.patch<{
    success: boolean
    lesson: AdminLesson
  }>(`/admin/lessons/${lessonId}`, data)

  return response.data.lesson
}

/**
 * Delete lesson (admin)
 */
export const adminDeleteLesson = async (lessonId: string, reason?: string): Promise<void> => {
  await http.delete(`/admin/lessons/${lessonId}`, {
    data: { reason }
  })
}

/**
 * Reorder lessons in a chapter (admin)
 * @param chapterId - Chapter UUID
 * @param lessonIds - Array of lesson UUIDs in desired order
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminReorderLessons = async (
  chapterId: string,
  lessonIds: string[]
): Promise<void> => {
  await http.post(`/admin/chapters/${chapterId}/lessons/reorder`, {
    lesson_ids: lessonIds
  })
}

// ============================================================================
// Phase B24-05: AI Course Generator - Job Management
// ============================================================================

/**
 * AI Job Status Enum
 */
export type AIJobStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'

/**
 * AI Job Type
 * Refactored: module_autogen → chapter_autogen (2025-11-27)
 */
export type AIJobType = 'course_from_pdf' | 'chapter_autogen' | 'lesson_autogen'

/**
 * AI Course Draft (generated course structure)
 * Refactored: modules → chapters (2025-11-27)
 */
export interface AICourseDraft {
  course: {
    title: string
    description: string
    category: string
    level: string
    language: string
  }
  chapters: Array<{
    title: string
    description: string
    duration_minutes: number
    order_index: number
    lessons: Array<{
      title: string
      lesson_type: string
      duration_minutes: number
      order_index: number
    }>
  }>
}

/**
 * AI Job
 */
export interface AIJob {
  id: string
  user_id: string
  course_id?: string | null
  type: AIJobType
  status: AIJobStatus
  progress: number
  input_file?: string | null
  input_prompt?: string | null
  output_data?: AICourseDraft | null
  error_message?: string | null
  created_at: string
  updated_at: string
}

/**
 * AI Job Create Request
 */
export interface AIJobCreateRequest {
  type: AIJobType
  file_name?: string
  prompt?: string
  course_id?: string
}

/**
 * AI Job Response
 */
export interface AIJobResponse {
  success: boolean
  job: AIJob
}

/**
 * AI Job Finalize Request
 * Refactored: create_modules → create_chapters (2025-11-27)
 */
export interface AIJobFinalizeRequest {
  create_course?: boolean
  create_chapters?: boolean
  create_lessons?: boolean
}

/**
 * AI Job Finalize Response
 * Refactored: modules_created → chapters_created (2025-11-27)
 */
export interface AIJobFinalizeResponse {
  success: boolean
  message: string
  course_id: number
  chapters_created: number
  lessons_created: number
}

/**
 * Start AI Course Generation Job
 * Uploads PDF and starts AI processing
 */
export const adminStartAIJob = async (data: FormData): Promise<AIJob> => {
  const response = await http.post<AIJobResponse>('/admin/ai/jobs', data, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })

  return response.data.job
}

/**
 * Get AI Job Status
 * Retrieves current status, progress, and output data
 */
export const adminGetAIJob = async (jobId: string): Promise<AIJob> => {
  const response = await http.get<AIJobResponse>(`/admin/ai/jobs/${jobId}`)

  return response.data.job
}

/**
 * Cancel AI Job
 * Cancels a pending or processing job
 */
export const adminCancelAIJob = async (jobId: string): Promise<void> => {
  await http.post(`/admin/ai/jobs/${jobId}/cancel`)
}

/**
 * Finalize AI Job
 * Creates actual course, modules, and lessons from AI output
 */
export const adminFinalizeAIJob = async (
  jobId: string,
  options?: AIJobFinalizeRequest
): Promise<AIJobFinalizeResponse> => {
  const response = await http.post<AIJobFinalizeResponse>(
    `/admin/ai/jobs/${jobId}/finalize`,
    options || {}
  )

  return response.data
}

// ============================================================================
// Exam Management API (Phase C1.3)
// ============================================================================

/**
 * Exam Types & Interfaces
 */
export type ExamType = 'practice' | 'ai_simulation' | 'final'
export type ExamStandard = 'IHK_FISI_AP1' | 'IHK_FIAE_AP1' | 'CompTIA_A+' | 'CompTIA_Network+' | 'Abitur_Informatik' | 'Custom'
export type QuestionType = 'mcq' | 'true_false' | 'fill_blanks' | 'matching' | 'short_answer' | 'math_problem' | 'case_question'

export interface ExamQuestion {
  question_id: string
  exam_id: string
  question_type: QuestionType
  question_text: string
  data: Record<string, any>  // JSONB
  solution: Record<string, any>  // JSONB
  points: number
  order_index: number
}

export interface Exam {
  exam_id: string
  course_id: string
  exam_type: ExamType
  title: string
  description?: string | null
  duration_minutes: number
  passing_score: number
  total_points: number
  settings?: Record<string, any>  // JSONB
  published: boolean
  generated_by_ai: boolean
  ai_model?: string | null
  question_count: number
  questions?: ExamQuestion[]
  created_at: string
  updated_at?: string | null
}

export interface ExamCreateRequest {
  title: string
  description?: string
  exam_type?: ExamType
  duration_minutes?: number
  passing_score?: number
  total_points?: number
  settings?: Record<string, any>
  published?: boolean
}

export interface ExamUpdateRequest {
  title?: string
  description?: string
  duration_minutes?: number
  passing_score?: number
  total_points?: number
  settings?: Record<string, any>
  published?: boolean
}

export interface ExamGenerateRequest {
  title: string
  description?: string
  exam_standard: ExamStandard
  difficulty?: string
  duration_minutes?: number
  passing_score?: number
  total_points?: number
  question_distribution: Record<string, number>  // e.g. {"mcq": 25, "fill_blanks": 10}
  topic_coverage?: Record<string, number>  // e.g. {"netzwerke": 40, "hardware": 20}
  source_chapter_ids?: string[]  // Refactored: source_module_ids → source_chapter_ids (2025-11-27)
}

// ============================================================================
// Course Prompts (Phase C1.4)
// ============================================================================

export type PromptScope =
  | 'course_generation'
  | 'module_generation'
  | 'exam_generation'
  | 'lesson_generation'
  | 'quiz_generation'

export interface CoursePrompt {
  course_prompt_id: string
  course_id: string
  scope: PromptScope
  language: string | null
  prompt_system: string | null
  prompt_user_template: string | null
  metadata: Record<string, any>
  is_active: boolean
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface CoursePromptUpdateRequest {
  language?: string | null
  prompt_system?: string | null
  prompt_user_template?: string | null
  metadata?: Record<string, any>
  is_active?: boolean
}

export interface CoursePromptResolveResponse {
  source: 'course_specific' | 'global' | 'hardcoded_fallback'
  scope: PromptScope
  language: string | null
  prompt_system: string | null
  prompt_user_template: string | null
  metadata: Record<string, any>
}

/**
 * List all exams for a course
 */
export const adminListExams = async (courseId: string): Promise<Exam[]> => {
  const response = await http.get<{ success: boolean; exams: Exam[] }>(
    `/admin/courses/${courseId}/exams`
  )
  return response.data.exams
}

/**
 * Get exam details with questions
 */
export const adminGetExam = async (examId: string): Promise<Exam> => {
  const response = await http.get<{ success: boolean; exam: Exam }>(
    `/admin/exams/${examId}`
  )
  return response.data.exam
}

/**
 * Create exam manually (without AI)
 */
export const adminCreateExam = async (
  courseId: string,
  data: ExamCreateRequest
): Promise<Exam> => {
  const response = await http.post<{ success: boolean; exam: Exam }>(
    `/admin/courses/${courseId}/exams`,
    data
  )
  return response.data.exam
}

/**
 * Update exam metadata
 */
export const adminUpdateExam = async (
  examId: string,
  data: ExamUpdateRequest
): Promise<Exam> => {
  const response = await http.patch<{ success: boolean; exam: Exam }>(
    `/admin/exams/${examId}`,
    data
  )
  return response.data.exam
}

/**
 * Delete exam and all questions
 */
export const adminDeleteExam = async (
  examId: string,
  reason?: string
): Promise<void> => {
  await http.delete(`/admin/exams/${examId}`, {
    data: { reason }
  })
}

/**
 * Generate exam using AI (Phase C1.3 - KI-Prüfungs-Generator)
 */
export const adminGenerateExam = async (
  courseId: string,
  data: ExamGenerateRequest
): Promise<{ job_id: string; exam_id: string }> => {
  const response = await http.post<{
    success: boolean
    message: string
    job_id: string
    exam_id: string
  }>(`/admin/courses/${courseId}/exams/generate`, data)

  return {
    job_id: response.data.job_id,
    exam_id: response.data.exam_id
  }
}

// ============================================================================
// Course Prompts API (Phase C1.4)
// ============================================================================

/**
 * List all custom prompts for a course
 */
export const adminListCoursePrompts = async (
  courseId: string,
  includeInactive = false
): Promise<CoursePrompt[]> => {
  const response = await http.get<{ success: boolean; prompts: CoursePrompt[] }>(
    `/admin/courses/${courseId}/prompts`,
    { params: { include_inactive: includeInactive } }
  )
  return response.data.prompts
}

/**
 * Get a specific prompt for a course and scope
 */
export const adminGetCoursePrompt = async (
  courseId: string,
  scope: PromptScope,
  language?: string | null
): Promise<{
  prompt: CoursePrompt | null
  resolved: CoursePromptResolveResponse
  source: string
}> => {
  const response = await http.get<{
    success: boolean
    prompt: CoursePrompt | null
    resolved?: CoursePromptResolveResponse
    source: string
  }>(`/admin/courses/${courseId}/prompts/${scope}`, {
    params: language ? { language } : {}
  })

  return {
    prompt: response.data.prompt,
    resolved: response.data.resolved!,
    source: response.data.source
  }
}

/**
 * Create or update a course-specific prompt (UPSERT)
 */
export const adminUpsertCoursePrompt = async (
  courseId: string,
  scope: PromptScope,
  data: CoursePromptUpdateRequest
): Promise<{ prompt: CoursePrompt; created: boolean }> => {
  const response = await http.put<{
    success: boolean
    prompt: CoursePrompt
    created: boolean
  }>(`/admin/courses/${courseId}/prompts/${scope}`, data)

  return {
    prompt: response.data.prompt,
    created: response.data.created
  }
}

/**
 * Delete a course-specific prompt (reset to global default)
 */
export const adminDeleteCoursePrompt = async (
  courseId: string,
  scope: PromptScope,
  language?: string | null
): Promise<void> => {
  await http.delete(`/admin/courses/${courseId}/prompts/${scope}`, {
    params: language ? { language } : {}
  })
}

/**
 * Bulk reset course prompts to global defaults
 */
export const adminBulkResetCoursePrompts = async (
  courseId: string,
  scopes?: PromptScope[]
): Promise<{ message: string }> => {
  const response = await http.post<{
    success: boolean
    message: string
  }>(`/admin/courses/${courseId}/prompts/reset`, {
    scopes: scopes || null,
    confirm: true
  })

  return {
    message: response.data.message
  }
}

/**
 * Resolve a prompt for testing/preview
 */
export const adminResolveCoursePrompt = async (
  courseId: string,
  scope: PromptScope,
  language?: string | null
): Promise<CoursePromptResolveResponse> => {
  const response = await http.post<{
    success: boolean
    resolved: CoursePromptResolveResponse
  }>(`/admin/courses/${courseId}/prompts/resolve`, {
    scope,
    language: language || null
  })

  return response.data.resolved
}

// ============================================================================
// Course Files Management API (Phase C2.x)
// ============================================================================

/**
 * Course File Types & Interfaces
 */
export type CourseFileType = 'pdf' | 'docx' | 'pptx' | 'xlsx' | 'txt' | 'image' | 'video' | 'audio' | 'archive' | 'other'
export type CourseFileCategory = 'script' | 'material' | 'exercise' | 'solution' | 'reference' | 'template' | 'other'

export interface CourseFile {
  course_file_id: string
  course_id: string
  file_id: string | null
  file_name: string
  file_type: CourseFileType
  file_size_bytes: number | null
  mime_type: string | null
  display_name: string | null
  description: string | null
  file_category: CourseFileCategory
  order_index: number
  is_public: boolean
  requires_enrollment: boolean
  download_count: number
  processed_for_ai: boolean
  ai_extracted_text: string | null
  ai_summary: string | null
  storage_path: string | null
  external_url: string | null
  uploaded_by: string | null
  uploader_name?: string | null
  public_url?: string | null
  cdn_url?: string | null
  media_status?: string | null
  created_at: string
  updated_at: string | null
}

export interface CourseFileCategorySummary {
  file_category: CourseFileCategory
  count: number
  total_size: number | null
}

export interface CourseFilesListResponse {
  files: CourseFile[]
  total: number
  categories_summary: CourseFileCategorySummary[]
}

export interface CourseFileUploadData {
  display_name?: string
  description?: string
  file_category?: CourseFileCategory
  is_public?: boolean
}

export interface CourseFileUpdateRequest {
  display_name?: string
  description?: string
  file_category?: CourseFileCategory
  is_public?: boolean
}

/**
 * List all files for a course
 */
export const adminListCourseFiles = async (
  courseId: string,
  category?: CourseFileCategory,
  limit = 100,
  offset = 0
): Promise<CourseFilesListResponse> => {
  const params: Record<string, any> = { limit, offset }
  if (category) {
    params.category = category
  }

  const response = await http.get<{
    success: boolean
    files: CourseFile[]
    total: number
    categories_summary: CourseFileCategorySummary[]
  }>(`/admin/courses/${courseId}/files`, { params })

  return {
    files: response.data.files,
    total: response.data.total,
    categories_summary: response.data.categories_summary
  }
}

/**
 * Upload a file to a course
 */
export interface CourseFileUploadResponse {
  file: CourseFile
  already_exists?: boolean
  message?: string
}

/**
 * Upload a file to a course
 * Returns file info and already_exists flag if duplicate detected
 */
export const adminUploadCourseFile = async (
  courseId: string,
  file: File,
  data: CourseFileUploadData = {}
): Promise<CourseFileUploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  if (data.display_name) {
    formData.append('display_name', data.display_name)
  }
  if (data.description) {
    formData.append('description', data.description)
  }
  if (data.file_category) {
    formData.append('file_category', data.file_category)
  }
  if (data.is_public !== undefined) {
    formData.append('is_public', data.is_public ? 'true' : 'false')
  }

  const response = await http.post<{
    success: boolean
    file: CourseFile
    already_exists?: boolean
    message?: string
  }>(
    `/admin/courses/${courseId}/files`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  )

  return {
    file: response.data.file,
    already_exists: response.data.already_exists,
    message: response.data.message
  }
}

/**
 * Get single course file details
 */
export const adminGetCourseFile = async (
  courseId: string,
  fileId: string
): Promise<CourseFile> => {
  const response = await http.get<{ success: boolean; file: CourseFile }>(
    `/admin/courses/${courseId}/files/${fileId}`
  )
  return response.data.file
}

/**
 * Update course file metadata
 */
export const adminUpdateCourseFile = async (
  courseId: string,
  fileId: string,
  data: CourseFileUpdateRequest
): Promise<CourseFile> => {
  const response = await http.patch<{ success: boolean; file: CourseFile }>(
    `/admin/courses/${courseId}/files/${fileId}`,
    data
  )
  return response.data.file
}

/**
 * Delete a course file
 */
export const adminDeleteCourseFile = async (
  courseId: string,
  fileId: string
): Promise<void> => {
  await http.delete(`/admin/courses/${courseId}/files/${fileId}`)
}

/**
 * Reorder course files
 */
export const adminReorderCourseFiles = async (
  courseId: string,
  fileIds: string[]
): Promise<void> => {
  await http.post(`/admin/courses/${courseId}/files/reorder`, {
    file_ids: fileIds
  })
}

// ============================================================================
// Phase C3.0: AI Model Selector System
// ============================================================================

/**
 * AI Model Category (Phase C3.0)
 */
export type AIModelCategory =
  | 'reasoning'
  | 'chat'
  | 'realtime'
  | 'audio'
  | 'image'
  | 'video'
  | 'embedding'
  | 'moderation'

/**
 * AI Model Cost Level
 */
export type AIModelCostLevel = 'free' | 'low' | 'medium' | 'high' | 'very_high'

/**
 * AI Model Speed
 */
export type AIModelSpeed = 'very_fast' | 'fast' | 'medium' | 'slow'

/**
 * AI Model (from database)
 */
export interface AIModel {
  model_id: number
  model_name: string
  display_name: string
  model_type?: string
  category: AIModelCategory
  description?: string | null
  cost_level: AIModelCostLevel
  speed: AIModelSpeed
  context_window?: number | null
  max_output_tokens?: number | null
  supports_vision?: boolean
  supports_functions?: boolean
  supports_streaming?: boolean
  is_default: boolean
  active: boolean
  provider_id?: number
  provider_name?: string
  provider_display_name?: string
  created_at?: string
  updated_at?: string
}

/**
 * AI Models Response
 */
export interface AIModelsResponse {
  success: boolean
  data: AIModel[]
  categories: AIModelCategory[]
  total: number
  timestamp: string
}

/**
 * AI Model Filter Params
 */
export interface AIModelFilterParams {
  category?: AIModelCategory
  active_only?: boolean
  search?: string
  provider?: string
  configured_only?: boolean
}

/**
 * AI Model Sync Response
 */
export interface AIModelSyncResponse {
  success: boolean
  data: {
    added: number
    updated: number
    unchanged: number
    total_synced: number
    models: Array<{
      model_name: string
      category: string
      status: 'added' | 'updated'
    }>
  }
  timestamp: string
}

/**
 * Get all AI models (Phase C3.0)
 * Returns models from database with category, cost, speed info
 */
export const adminGetAIModels = async (
  params: AIModelFilterParams = {}
): Promise<AIModelsResponse> => {
  const response = await http.get<AIModelsResponse>('/admin/ai/models', {
    params: {
      category: params.category,
      active_only: params.active_only !== false ? 'true' : 'false',
      search: params.search
    }
  })

  return response.data
}

/**
 * Sync AI models from OpenAI API (Phase C3.0)
 * Fetches latest models from OpenAI and updates database
 */
export const adminSyncAIModels = async (): Promise<AIModelSyncResponse> => {
  // Send empty object to ensure Content-Type header is set (required by API Gateway)
  const response = await http.post<AIModelSyncResponse>('/admin/ai/models/sync', {})
  return response.data
}

/**
 * Set AI model as default for its category (Phase C3.0)
 */
export const adminSetAIModelDefault = async (
  modelId: number,
  isDefault = true
): Promise<{ success: boolean; message: string; data: { model_id: number; model_name: string; category: string; is_default: boolean } }> => {
  const response = await http.patch<{
    success: boolean
    message: string
    data: {
      model_id: number
      model_name: string
      category: string
      is_default: boolean
    }
  }>(`/admin/ai/models/${modelId}/default`, {
    is_default: isDefault
  })

  return response.data
}

/**
 * Get default AI model for a category (Phase C3.0)
 */
export const adminGetDefaultAIModel = async (
  category: AIModelCategory = 'chat'
): Promise<AIModel | null> => {
  const response = await http.get<{
    success: boolean
    data: AIModel | null
  }>('/admin/ai/models/default', {
    params: { category }
  })

  return response.data.data
}

// ============================================================================
// Phase C3.0: AI Model Registry (for Model Selector Window)
// ============================================================================

/**
 * AI Model Registry Category (with label)
 */
export interface AIModelRegistryCategory {
  id: string
  label: string
}

/**
 * AI Model Registry Item (extended)
 */
export interface AIModelRegistryItem {
  model_id: number
  model_name: string
  display_name: string
  model_type?: string
  category: AIModelCategory
  description?: string | null
  cost_level: AIModelCostLevel
  speed: AIModelSpeed
  context_window?: number | null
  max_output_tokens?: number | null
  supports_vision?: boolean
  supports_functions?: boolean
  supports_streaming?: boolean
  is_default: boolean
  active: boolean
  provider?: string
  input_price_per_1k?: number | null
  output_price_per_1k?: number | null
  created_at?: string
  updated_at?: string
}

/**
 * AI Model Update Request
 */
export interface AIModelUpdateRequest {
  display_name?: string
  description?: string
  cost_level?: AIModelCostLevel
  speed?: AIModelSpeed
  input_price_per_1k?: number | null
  output_price_per_1k?: number | null
  active?: boolean
}

/**
 * AI Provider Info (for registry)
 */
export interface AIProviderInfo {
  provider_id: number
  name: string
  display_name: string
  has_api_key: boolean
}

/**
 * AI Model Registry Response
 */
export interface AIModelRegistryResponse {
  success: boolean
  data: AIModelRegistryItem[]
  categories: AIModelRegistryCategory[]
  providers: AIProviderInfo[]
  total: number
  timestamp: string
}

/**
 * Get AI models from registry (Phase C3.0 - Model Selector Window)
 * Returns flat list with category labels for filtering
 * Used by AdminModelSelectorWindow.vue
 */
export const adminGetAIModelsRegistry = async (
  params: AIModelFilterParams = {}
): Promise<AIModelRegistryResponse> => {
  const response = await http.get<AIModelRegistryResponse>('/admin/ai/models/registry', {
    params: {
      category: params.category,
      active_only: params.active_only !== false ? 'true' : 'false',
      search: params.search,
      provider: params.provider,
      configured_only: params.configured_only ? 'true' : 'false'
    }
  })

  return response.data
}

/**
 * Update AI model (Phase C3.0 - Price Editor)
 * Updates model properties including prices
 */
export const adminUpdateAIModel = async (
  modelId: number,
  data: AIModelUpdateRequest
): Promise<AIModelRegistryItem> => {
  const response = await http.put<{
    success: boolean
    data: AIModelRegistryItem
    message: string
  }>(`/admin/ai/models/${modelId}`, data)

  return response.data.data
}

/**
 * Toggle AI model active status
 */
export const adminToggleAIModelActive = async (
  modelId: number,
  active: boolean
): Promise<AIModelRegistryItem> => {
  const response = await http.put<{
    success: boolean
    data: AIModelRegistryItem
    message: string
  }>(`/admin/ai/models/${modelId}/active`, { active })

  return response.data.data
}

// ============================================================================
// Phase D3.4: Learning Method Management (31 Methoden, 6 Groups A-F)
// ============================================================================

/**
 * Learning Method Group (A-F)
 * A: Erklaerend, B: Praxis, C: Pruefung, D: Pro, E: IT, F: Kollaborativ
 */
export type LearningMethodGroup = 'A' | 'B' | 'C' | 'D' | 'E' | 'F'

/**
 * Learning Method Type Definition
 * Represents one of the 31 learning methods (LM00-LM32, excluding LM05/LM07)
 */
export interface LearningMethodType {
  lm_id: number
  name: string
  group: LearningMethodGroup
  method_type: 'explanatory' | 'practice' | 'exam' | 'meta' | 'it' | 'collaborative'
  ki_usage: 'intensive' | 'medium' | 'optional'
  prompt_key: string
  description: string
}

/**
 * Learning Method Types Response
 */
export interface LearningMethodTypesResponse {
  success: boolean
  types: LearningMethodType[]
  total: number
  groups: {
    A: { name: string; range: string; count: number }
    B: { name: string; range: string; count: number }
    C: { name: string; range: string; count: number }
    D: { name: string; range: string; count: number }
  }
}

/**
 * Learning Method Instance
 * A concrete learning method attached to a chapter/lesson
 * Refactored: module → chapter (2025-11-27)
 */
export interface AdminLearningMethod {
  method_id: string
  chapter_id: string  // Refactored: module_id → chapter_id (2025-11-27)
  method_type: number  // 0-31
  title: string
  instructions?: string | null
  data: Record<string, any>
  solution?: Record<string, any> | null
  tier: 'basic' | 'premium' | 'pro'
  duration_minutes?: number | null
  difficulty: 'easy' | 'medium' | 'hard'
  order_index: number
  published: boolean
  created_at: string
  updated_at?: string | null
  // Enriched fields from mapping
  method_name?: string
  method_group?: LearningMethodGroup
  method_type_name?: string
  ki_usage?: string
  prompt_key?: string
  method_description?: string
}

/**
 * Create Learning Method Request
 */
export interface AdminLearningMethodCreateRequest {
  method_type: number  // 0-31
  title: string
  instructions?: string
  data?: Record<string, any>
  solution?: Record<string, any>
  tier?: 'basic' | 'premium' | 'pro'
  duration_minutes?: number
  difficulty?: 'easy' | 'medium' | 'hard'
  order_index?: number
  published?: boolean
}

/**
 * Update Learning Method Request
 */
export interface AdminLearningMethodUpdateRequest {
  method_type?: number  // 0-31
  title?: string
  instructions?: string
  data?: Record<string, any>
  solution?: Record<string, any>
  tier?: 'basic' | 'premium' | 'pro'
  duration_minutes?: number
  difficulty?: 'easy' | 'medium' | 'hard'
  order_index?: number
  published?: boolean
}

/**
 * Learning Methods Response with Statistics
 * Refactored: module_id → chapter_id (2025-11-27)
 */
export interface AdminLearningMethodsResponse {
  success: boolean
  learning_methods: AdminLearningMethod[]
  total: number
  chapter_id: string
  statistics?: {
    total_methods: number
    published_count: number
    unique_types: number
    total_duration: number
    easy_count: number
    medium_count: number
    hard_count: number
    basic_count: number
    premium_count: number
    pro_count: number
  }
}

/**
 * Get all 32 learning method types (LM00-LM31)
 */
export const adminGetLearningMethodTypes = async (): Promise<LearningMethodTypesResponse> => {
  const response = await http.get<LearningMethodTypesResponse>(
    '/admin/learning-method-types'
  )
  return response.data
}

/**
 * Get all learning methods for a chapter
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminGetChapterLearningMethods = async (
  chapterId: string,
  publishedOnly = false
): Promise<AdminLearningMethodsResponse> => {
  const response = await http.get<AdminLearningMethodsResponse>(
    `/admin/chapters/${chapterId}/learning-methods`,
    { params: { published_only: publishedOnly } }
  )
  return response.data
}

/**
 * Get single learning method by ID
 */
export const adminGetLearningMethod = async (
  methodId: string
): Promise<AdminLearningMethod> => {
  const response = await http.get<{
    success: boolean
    learning_method: AdminLearningMethod
  }>(`/admin/learning-methods/${methodId}`)
  return response.data.learning_method
}

/**
 * Create new learning method for a chapter
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminCreateLearningMethod = async (
  chapterId: string,
  data: AdminLearningMethodCreateRequest
): Promise<AdminLearningMethod> => {
  const response = await http.post<{
    success: boolean
    learning_method: AdminLearningMethod
    message: string
  }>(`/admin/chapters/${chapterId}/learning-methods`, data)
  return response.data.learning_method
}

/**
 * Update learning method
 */
export const adminUpdateLearningMethod = async (
  methodId: string,
  data: AdminLearningMethodUpdateRequest
): Promise<AdminLearningMethod> => {
  const response = await http.patch<{
    success: boolean
    learning_method: AdminLearningMethod
    message: string
  }>(`/admin/learning-methods/${methodId}`, data)
  return response.data.learning_method
}

/**
 * Delete learning method
 */
export const adminDeleteLearningMethod = async (
  methodId: string
): Promise<void> => {
  await http.delete(`/admin/learning-methods/${methodId}`)
}

/**
 * Reorder learning methods in a chapter
 * Refactored: modules → chapters (2025-11-27)
 */
export const adminReorderLearningMethods = async (
  chapterId: string,
  methodIds: string[]
): Promise<void> => {
  await http.post(`/admin/chapters/${chapterId}/learning-methods/reorder`, {
    method_ids: methodIds
  })
}

/**
 * Publish learning method
 */
export const adminPublishLearningMethod = async (
  methodId: string
): Promise<AdminLearningMethod> => {
  const response = await http.post<{
    success: boolean
    learning_method: AdminLearningMethod
    message: string
  }>(`/admin/learning-methods/${methodId}/publish`)
  return response.data.learning_method
}

/**
 * Unpublish learning method
 */
export const adminUnpublishLearningMethod = async (
  methodId: string
): Promise<AdminLearningMethod> => {
  const response = await http.post<{
    success: boolean
    learning_method: AdminLearningMethod
    message: string
  }>(`/admin/learning-methods/${methodId}/unpublish`)
  return response.data.learning_method
}

// ============================================================================
// LM Model Routing (Phase KI-Architektur)
// ============================================================================

export interface LMModelAssignment {
  learning_method_id: number
  lm_code: string
  lm_name: string
  lm_group: 'A' | 'B' | 'C' | 'D' | null
  lm_type: 'explanatory' | 'practice' | 'exam' | 'meta' | null
  ki_usage: 'intensive' | 'medium' | 'optional' | null
  model_required: boolean
  recommended_categories: string[]
  requires_vision: boolean
  assignment_id: number | null
  model_id: number | null
  model_name: string | null
  model_display_name: string | null
  model_category: string | null
  provider_name: string | null
  provider_display_name: string | null
  is_configured: boolean
}

export interface LMRoutingOverview {
  assignments: LMModelAssignment[]
  stats: {
    total: number
    configured: number
    unconfigured_required: number
    unconfigured_optional: number
  }
}

export interface LMRequirement {
  learning_method_id: number
  lm_code: string
  lm_name: string
  required: boolean
  recommended_categories: string[]
  requires_vision: boolean
  requires_functions: boolean
  min_context_window: number | null
  description: string | null
}

export interface UnconfiguredLM {
  learning_method_id: number
  lm_code: string
  lm_name: string
  lm_group: string | null
  recommended_categories: string[]
  description: string | null
}

/**
 * Get LM routing overview (all 33 learning methods with their model assignments)
 */
export const adminGetLMRoutingOverview = async (): Promise<LMRoutingOverview> => {
  const response = await http.get<{
    success: boolean
    data: LMRoutingOverview
  }>('/admin/lm-routing/overview')
  return response.data.data
}

/**
 * Get unconfigured required learning methods
 */
export const adminGetUnconfiguredLMs = async (): Promise<{
  unconfigured: UnconfiguredLM[]
  count: number
}> => {
  const response = await http.get<{
    success: boolean
    data: {
      unconfigured: UnconfiguredLM[]
      count: number
    }
  }>('/admin/lm-routing/unconfigured')
  return response.data.data
}

/**
 * Get all LM requirements
 */
export const adminGetLMRequirements = async (): Promise<LMRequirement[]> => {
  const response = await http.get<{
    success: boolean
    data: {
      requirements: LMRequirement[]
    }
  }>('/admin/lm-routing/requirements')
  return response.data.data.requirements
}

/**
 * Get assignment for specific learning method
 */
export const adminGetLMAssignment = async (lmId: number): Promise<LMModelAssignment & {
  requirement: {
    required: boolean
    recommended_categories: string[]
    requires_vision: boolean
  }
  assignment: {
    assignment_id: number
    model_id: number
    model_name: string
    model_display_name: string
    model_category: string
    provider_name: string
    provider_display_name: string
  } | null
}> => {
  const response = await http.get<{
    success: boolean
    data: LMModelAssignment & {
      requirement: {
        required: boolean
        recommended_categories: string[]
        requires_vision: boolean
      }
      assignment: {
        assignment_id: number
        model_id: number
        model_name: string
        model_display_name: string
        model_category: string
        provider_name: string
        provider_display_name: string
      } | null
    }
  }>(`/admin/lm-routing/${lmId}`)
  return response.data.data
}

/**
 * Set model assignment for learning method
 */
export const adminSetLMAssignment = async (
  lmId: number,
  modelId: number
): Promise<{ success: boolean; message: string }> => {
  const response = await http.put<{
    success: boolean
    data: unknown
    message: string
  }>(`/admin/lm-routing/${lmId}`, { model_id: modelId })
  return {
    success: response.data.success,
    message: response.data.message
  }
}

/**
 * Remove model assignment for learning method
 */
export const adminRemoveLMAssignment = async (
  lmId: number
): Promise<{ success: boolean; message: string }> => {
  const response = await http.delete<{
    success: boolean
    message: string
  }>(`/admin/lm-routing/${lmId}`)
  return {
    success: response.data.success,
    message: response.data.message
  }
}

/**
 * Bulk set model assignments for multiple learning methods
 */
export const adminBulkSetLMAssignments = async (
  assignments: Array<{ learning_method_id: number; model_id: number }>
): Promise<{ created: number; errors: Array<{ learning_method_id: number; error: string }> }> => {
  const response = await http.post<{
    success: boolean
    data: {
      created: number
      errors: Array<{ learning_method_id: number; error: string }>
    }
  }>('/admin/lm-routing/bulk', { assignments })
  return response.data.data
}

/**
 * Resolve which model would be used for a learning method
 */
export const adminResolveLMModel = async (
  lmId: number,
  chapterId?: string,
  courseId?: string
): Promise<{
  model_id: number | null
  model_name: string | null
  provider_name: string | null
  scope: string
  is_configured: boolean
  model_required: boolean
  can_generate: boolean
}> => {
  const response = await http.post<{
    success: boolean
    data: {
      model_id: number | null
      model_name: string | null
      provider_name: string | null
      scope: string
      is_configured: boolean
      model_required: boolean
      can_generate: boolean
    }
  }>('/admin/lm-routing/resolve', {
    learning_method_id: lmId,
    chapter_id: chapterId,
    course_id: courseId
  })
  return response.data.data
}

/**
 * Get recommended models for a learning method
 */
export interface RecommendedModel {
  model_id: number
  model_name: string
  display_name: string
  category: string
  provider_name: string
  provider_display_name: string
  score: number
  reasons: string[]
  cost_level: string
  supports_vision: boolean
  context_window: number | null
}

export const adminGetLMRecommendations = async (lmId: number): Promise<{
  learning_method_id: number
  lm_code: string
  lm_name: string
  requirements: {
    recommended_categories: string[]
    requires_vision: boolean
    min_context_window: number | null
  }
  recommended_models: RecommendedModel[]
  total_matching: number
}> => {
  const response = await http.get<{
    success: boolean
    data: {
      learning_method_id: number
      lm_code: string
      lm_name: string
      requirements: {
        recommended_categories: string[]
        requires_vision: boolean
        min_context_window: number | null
      }
      recommended_models: RecommendedModel[]
      total_matching: number
    }
  }>(`/admin/lm-routing/recommend/${lmId}`)
  return response.data.data
}

/**
 * Auto-setup: automatically assign best models to all LMs
 */
export interface AutoSetupOptions {
  only_required?: boolean    // Only configure required LMs
  prefer_cheap?: boolean     // Prefer cheaper models
  overwrite_existing?: boolean // Overwrite existing assignments
}

export interface AutoSetupResult {
  configured: number
  skipped: number
  failed: number
  assignments: Array<{
    lm_id: number
    lm_code: string
    lm_name: string
    model_name: string
    provider: string
    score: number
  }>
}

export const adminAutoSetupLMModels = async (
  options: AutoSetupOptions = {}
): Promise<AutoSetupResult> => {
  const response = await http.post<{
    success: boolean
    data: AutoSetupResult
    message: string
  }>('/admin/lm-routing/auto-setup', options)
  return response.data.data
}

// ============================================================================
// AI-Powered Auto-Setup (using gpt-4o)
// ============================================================================

export interface AIAutoSetupOptions {
  model?: string             // AI model to use (default: gpt-4o)
  overwrite_existing?: boolean // Overwrite existing assignments
}

export interface AIAutoSetupAssignment {
  lm_id: number
  lm_code: string
  lm_name: string
  model_id: number
  model_name: string
  provider: string
  reasoning: string           // AI-generated reasoning
}

export interface AIAutoSetupResult {
  configured: number
  failed: number
  assignments: AIAutoSetupAssignment[]
  ai_model_used: string
  total_cost_eur: number
}

/**
 * AI-powered intelligent model assignment using gpt-4o.
 * Uses AI to analyze learning methods and select optimal models with reasoning.
 * Note: This operation can take 2-5 minutes as it analyzes all 33 learning methods.
 */
export const adminAIAutoSetupLMModels = async (
  options: AIAutoSetupOptions = {}
): Promise<AIAutoSetupResult> => {
  const response = await http.post<{
    success: boolean
    data: AIAutoSetupResult
    message: string
  }>('/admin/lm-routing/ai-auto-setup', options, {
    timeout: 600000  // 10 minutes - AI analysis of 33 LMs takes time
  })
  return response.data.data
}


// ============================================================================
// LM Capability Slots System (Multi-Model per LM)
// ============================================================================

/**
 * Capability slot definition
 */
export interface CapabilitySlot {
  slot_id: number
  slot_code: string
  display_name: string
  description: string
  required_category: string
  accepted_categories: string[]
  icon: string
  sort_order: number
}

/**
 * Model compatible with a slot
 */
export interface CompatibleModel {
  model_id: number
  model_name: string
  display_name: string
  category: string
  provider_name: string
  provider_display_name: string
  supports_vision: boolean
  supports_functions: boolean
  context_window: number | null
  cost_level: string
}

/**
 * Slot configuration for a specific LM
 */
export interface LMSlotConfig {
  slot_code: string
  slot_display_name: string
  is_required: boolean
  is_primary: boolean
  is_configured: boolean
  model: {
    model_id: number
    model_name: string
    display_name: string
    provider: string
  } | null
  resolved_scope: string
  compatible_models?: CompatibleModel[]
}

/**
 * Full LM slot overview
 */
export interface LMSlotOverview {
  learning_method_id: number
  name: string
  group: string
  ready: boolean
  required_count: number
  configured_count: number
  slots: LMSlotConfig[]
}

/**
 * Slot assignment request
 */
export interface SlotAssignmentRequest {
  model_id: number
  scope?: 'system' | 'course' | 'chapter'
  scope_reference_id?: string | null
}

/**
 * Bulk slot assignment
 */
export interface BulkSlotAssignment {
  slot_code: string
  model_id: number
  priority?: number
}

/**
 * Get all available capability slots
 */
export const getCapabilitySlots = async (): Promise<CapabilitySlot[]> => {
  const response = await http.get<{
    success: boolean
    data: {
      slots: CapabilitySlot[]
    }
  }>('/admin/lm-routing/slots')
  return response.data.data.slots
}

/**
 * Get complete slot overview for a learning method
 */
export const getLMSlotOverview = async (lmId: number): Promise<LMSlotOverview> => {
  const response = await http.get<{
    success: boolean
    data: LMSlotOverview
  }>(`/admin/lm-routing/${lmId}/slots`)
  return response.data.data
}

/**
 * Assign a model to a specific slot for a learning method
 */
export const assignSlotModel = async (
  lmId: number,
  slotCode: string,
  request: SlotAssignmentRequest
): Promise<{ success: boolean; message: string }> => {
  const response = await http.put<{
    success: boolean
    data: unknown
    message: string
  }>(`/admin/lm-routing/${lmId}/slots/${slotCode}`, request)
  return {
    success: response.data.success,
    message: response.data.message
  }
}

/**
 * Remove a slot assignment for a learning method
 */
export const removeSlotAssignment = async (
  lmId: number,
  slotCode: string,
  scope: string = 'system',
  scopeReferenceId?: string
): Promise<{ success: boolean; message: string }> => {
  let url = `/admin/lm-routing/${lmId}/slots/${slotCode}?scope=${scope}`
  if (scopeReferenceId) {
    url += `&scope_reference_id=${scopeReferenceId}`
  }
  const response = await http.delete<{
    success: boolean
    message: string
  }>(url)
  return {
    success: response.data.success,
    message: response.data.message
  }
}

/**
 * Bulk assign multiple slots for a learning method
 */
export const bulkAssignSlots = async (
  lmId: number,
  assignments: BulkSlotAssignment[],
  scope: string = 'system',
  scopeReferenceId?: string | null
): Promise<{ created: number; assignments: unknown[] }> => {
  const response = await http.put<{
    success: boolean
    data: {
      created: number
      assignments: unknown[]
    }
    message: string
  }>(`/admin/lm-routing/${lmId}/slots/bulk`, {
    assignments,
    scope,
    scope_reference_id: scopeReferenceId
  })
  return response.data.data
}

/**
 * Test resolution of all slots for a learning method
 */
export const resolveLMSlots = async (
  lmId: number,
  chapterId?: string,
  courseId?: string
): Promise<{
  learning_method_id: number
  ready: boolean
  required_count: number
  configured_count: number
  missing_slots: string[]
  slots: Record<string, LMSlotConfig | null>
}> => {
  const response = await http.post<{
    success: boolean
    data: {
      learning_method_id: number
      ready: boolean
      required_count: number
      configured_count: number
      missing_slots: string[]
      slots: Record<string, LMSlotConfig | null>
    }
  }>(`/admin/lm-routing/${lmId}/slots/resolve`, {
    chapter_id: chapterId,
    course_id: courseId
  })
  return response.data.data
}

/**
 * Get overview of all LMs with their slot configurations
 */
export const getAllLMSlotsOverview = async (): Promise<{
  lms: LMSlotOverview[]
  stats: {
    total: number
    ready: number
    not_ready: number
    missing_required: number
  }
}> => {
  const response = await http.get<{
    success: boolean
    data: {
      lms: LMSlotOverview[]
      stats: {
        total: number
        ready: number
        not_ready: number
        missing_required: number
      }
    }
  }>('/admin/lm-routing/slots/overview')
  return response.data.data
}

/**
 * Get all models compatible with a specific slot
 */
export const getCompatibleModelsForSlot = async (
  slotCode: string
): Promise<{
  slot_code: string
  slot_display_name: string
  required_category: string
  compatible_models: CompatibleModel[]
}> => {
  const response = await http.get<{
    success: boolean
    data: {
      slot_code: string
      slot_display_name: string
      required_category: string
      compatible_models: CompatibleModel[]
    }
  }>(`/admin/lm-routing/slots/${slotCode}/models`)
  return response.data.data
}

/**
 * Apply a cost preset to all LM slots
 */
export const applySlotPreset = async (
  preset: 'cheap' | 'medium' | 'expensive'
): Promise<{
  preset: string
  preset_label: string
  configured: number
  skipped: number
  failed: number
}> => {
  const response = await http.post<{
    success: boolean
    data: {
      preset: string
      preset_label: string
      configured: number
      skipped: number
      failed: number
    }
    message: string
  }>('/admin/lm-routing/slots/apply-preset', { preset })
  return response.data.data
}

/**
 * Set default model for a category
 */
export const setDefaultModelForCategory = async (
  category: string,
  modelId: number
): Promise<{ category: string; model_id: number }> => {
  const response = await http.post<{
    success: boolean
    data: { category: string; model_id: number }
  }>('/admin/lm-routing/category-defaults', { category, model_id: modelId })
  return response.data.data
}
