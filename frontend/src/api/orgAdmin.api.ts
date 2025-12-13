/**
 * LernsystemX - Organisation Admin API
 *
 * API endpoints for organisation-specific administration:
 * - Organisation Details & Settings
 * - Member Management
 * - Course Assignments
 * - Analytics & Reports
 */

import http from './http'

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface OrgDetail {
  organisation_id: number
  name: string
  type: 'school' | 'company' | 'teacher_team' | 'creator_team'
  plan_id?: string | null
  plan_name?: string
  token_pool: number
  token_used: number
  token_available: number
  total_users: number
  active_users: number
  created_at: string
  is_active: boolean
  domain?: string | null
  branding?: {
    logo_url?: string
    primary_color?: string
    secondary_color?: string
  }
}

export interface OrgMember {
  user_id: number
  email: string
  first_name: string
  last_name: string
  role: string // within organisation: 'student', 'teacher', 'admin'
  org_role?: string
  is_active: boolean
  joined_at: string
  last_active?: string | null
  token_usage?: number
  assigned_courses?: number
}

export interface OrgCourse {
  course_id: number
  title: string
  description?: string
  category?: string
  level?: string
  assigned_users: number
  completion_rate?: number
  avg_progress?: number
  created_at: string
}

export interface OrgAnalyticsOverview {
  total_members: number
  active_members_7_days: number
  active_members_30_days: number
  total_assigned_courses: number
  avg_completion_rate: number
  token_used_7_days: number
  token_used_30_days: number
  top_courses?: Array<{
    course_id: number
    course_title: string
    enrolled_count: number
    avg_progress: number
  }>
  top_users?: Array<{
    user_id: number
    user_name: string
    courses_completed: number
    total_progress: number
  }>
}

export interface OrgInviteRequest {
  email: string
  first_name: string
  last_name: string
  role: string // 'student', 'teacher'
  send_email?: boolean
}

export interface OrgCourseAssignmentRequest {
  course_id: number
  user_ids: number[]
}

export interface OrgSettings {
  name: string
  branding?: {
    logo_url?: string
    primary_color?: string
    secondary_color?: string
  }
  domain?: string | null
}

// ============================================================================
// Organisation Details
// ============================================================================

/**
 * Get organisation details (org admin)
 */
export const getOrganisationDetail = async (orgId: number): Promise<OrgDetail> => {
  const response = await http.get<{
    success: boolean
    organisation: OrgDetail
  }>(`/organisations/${orgId}`)

  return response.data.organisation
}

/**
 * Update organisation settings (org admin)
 */
export const updateOrganisationSettings = async (
  orgId: number,
  settings: Partial<OrgSettings>
): Promise<void> => {
  await http.patch(`/organisations/${orgId}/settings`, settings)
}

// ============================================================================
// Member Management
// ============================================================================

/**
 * Get organisation members (org admin)
 */
export const getOrganisationMembers = async (
  orgId: number,
  params?: {
    page?: number
    limit?: number
    search?: string
    role?: string
    status?: 'active' | 'inactive'
  }
): Promise<{
  members: OrgMember[]
  total: number
  page: number
  limit: number
}> => {
  const response = await http.get<{
    success: boolean
    members: OrgMember[]
    total: number
    page: number
    limit: number
  }>(`/organisations/${orgId}/members`, { params })

  return {
    members: response.data.members,
    total: response.data.total,
    page: response.data.page,
    limit: response.data.limit
  }
}

/**
 * Invite user to organisation (org admin)
 */
export const inviteUserToOrganisation = async (
  orgId: number,
  request: OrgInviteRequest
): Promise<void> => {
  await http.post(`/organisations/${orgId}/members/invite`, request)
}

/**
 * Remove user from organisation (org admin)
 */
export const removeUserFromOrganisation = async (
  orgId: number,
  userId: number
): Promise<void> => {
  await http.delete(`/organisations/${orgId}/members/${userId}`)
}

/**
 * Update user's organisation role (org admin)
 */
export const updateOrganisationUserRole = async (
  orgId: number,
  userId: number,
  role: string
): Promise<void> => {
  await http.patch(`/organisations/${orgId}/members/${userId}/role`, { role })
}

// ============================================================================
// Course Management
// ============================================================================

/**
 * Get organisation courses (org admin)
 */
export const getOrganisationCourses = async (
  orgId: number,
  params?: {
    page?: number
    limit?: number
    search?: string
  }
): Promise<{
  courses: OrgCourse[]
  total: number
  page: number
  limit: number
}> => {
  const response = await http.get<{
    success: boolean
    courses: OrgCourse[]
    total: number
    page: number
    limit: number
  }>(`/organisations/${orgId}/courses`, { params })

  return {
    courses: response.data.courses,
    total: response.data.total,
    page: response.data.page,
    limit: response.data.limit
  }
}

/**
 * Assign course to organisation members (org admin)
 */
export const assignCourseToMembers = async (
  orgId: number,
  request: OrgCourseAssignmentRequest
): Promise<void> => {
  await http.post(`/organisations/${orgId}/courses/assign`, request)
}

/**
 * Unassign course from members (org admin)
 */
export const unassignCourseFromMembers = async (
  orgId: number,
  courseId: number,
  userIds: number[]
): Promise<void> => {
  await http.post(`/organisations/${orgId}/courses/${courseId}/unassign`, {
    user_ids: userIds
  })
}

// ============================================================================
// Analytics
// ============================================================================

/**
 * Get organisation analytics overview (org admin)
 */
export const getOrganisationAnalytics = async (
  orgId: number
): Promise<OrgAnalyticsOverview> => {
  const response = await http.get<{
    success: boolean
    analytics: OrgAnalyticsOverview
  }>(`/organisations/${orgId}/analytics`)

  return response.data.analytics
}

/**
 * Get organisation token usage (org admin)
 */
export const getOrganisationTokenUsage = async (
  orgId: number,
  days?: 7 | 30
): Promise<{
  total_used: number
  available: number
  usage_by_day: Array<{ date: string; tokens_used: number }>
}> => {
  const response = await http.get<{
    success: boolean
    total_used: number
    available: number
    usage_by_day: Array<{ date: string; tokens_used: number }>
  }>(`/organisations/${orgId}/tokens/usage`, {
    params: { days }
  })

  return {
    total_used: response.data.total_used,
    available: response.data.available,
    usage_by_day: response.data.usage_by_day
  }
}

/**
 * Get organisation member progress (org admin)
 */
export const getOrganisationMemberProgress = async (
  orgId: number,
  userId: number
): Promise<{
  user: OrgMember
  courses: Array<{
    course_id: number
    course_title: string
    progress_percentage: number
    status: string
    started_at?: string
    completed_at?: string
  }>
}> => {
  const response = await http.get<{
    success: boolean
    user: OrgMember
    courses: Array<{
      course_id: number
      course_title: string
      progress_percentage: number
      status: string
      started_at?: string
      completed_at?: string
    }>
  }>(`/organisations/${orgId}/members/${userId}/progress`)

  return {
    user: response.data.user,
    courses: response.data.courses
  }
}

// ============================================================================
// Advanced Analytics
// ============================================================================

export interface TimeSeriesPoint {
  date: string
  value: number
}

export interface OrgAnalyticsCourse {
  course_id: number
  title: string
  enrolled_count: number
  avg_progress: number
  completion_rate?: number
  events_count?: number
}

export interface OrgAnalyticsChapter {
  chapter_id: string  // Refactored: module_id → chapter_id (2025-11-27)
  chapter_title: string  // Refactored: module_title → chapter_title
  course_title: string
  completions: number
  avg_time_spent?: number
}

// Alias for backwards compatibility (modules → chapters refactoring)
export type OrgAnalyticsModule = OrgAnalyticsChapter

/**
 * Get organisation events time series (org admin)
 */
export const orgGetEventsTimeSeries = async (
  orgId: number,
  params: {
    from?: string
    to?: string
    days?: 7 | 30 | 90
  }
): Promise<TimeSeriesPoint[]> => {
  const response = await http.get<{
    success: boolean
    data: TimeSeriesPoint[]
  }>(`/organisations/${orgId}/analytics/events/time-series`, { params })

  return response.data.data
}

/**
 * Get organisation active members time series (org admin)
 */
export const orgGetActiveMembersTimeSeries = async (
  orgId: number,
  params: {
    from?: string
    to?: string
    days?: 7 | 30 | 90
  }
): Promise<TimeSeriesPoint[]> => {
  const response = await http.get<{
    success: boolean
    data: TimeSeriesPoint[]
  }>(`/organisations/${orgId}/analytics/active-members/time-series`, { params })

  return response.data.data
}

/**
 * Get organisation top courses (org admin)
 */
export const orgGetTopCourses = async (
  orgId: number,
  params?: {
    limit?: number
    days?: 7 | 30 | 90
  }
): Promise<OrgAnalyticsCourse[]> => {
  const response = await http.get<{
    success: boolean
    courses: OrgAnalyticsCourse[]
  }>(`/organisations/${orgId}/analytics/top-courses`, { params })

  return response.data.courses
}

/**
 * Get organisation top modules (org admin)
 */
export const orgGetTopModules = async (
  orgId: number,
  params?: {
    limit?: number
    days?: 7 | 30 | 90
  }
): Promise<OrgAnalyticsModule[]> => {
  const response = await http.get<{
    success: boolean
    modules: OrgAnalyticsModule[]
  }>(`/organisations/${orgId}/analytics/top-modules`, { params })

  return response.data.modules
}
