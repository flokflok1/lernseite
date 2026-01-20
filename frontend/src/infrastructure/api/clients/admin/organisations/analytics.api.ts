/**
 * Admin Domain - Organisation Analytics API
 * ==========================================
 *
 * Analytics and reporting for organisations.
 * Part of the DDD Architecture - Infrastructure Layer (API Clients).
 *
 * Handles:
 * - Overall analytics summaries
 * - Token usage tracking
 * - Member progress reporting
 * - Advanced time-series analytics
 * - Top performers and top courses
 *
 * Usage:
 * import { getOrganisationAnalytics, getOrganisationTokenUsage } from '@/infrastructure/api/clients/admin'
 * import type { OrgAnalyticsOverview } from '@/infrastructure/api/clients/admin'
 */

import http from '@/infrastructure/api/http'

// ============================================================================
// Analytics Types
// ============================================================================

/**
 * High-level overview of organisation analytics.
 * Provides summary statistics for dashboard display.
 */
export interface OrgAnalyticsOverview {
  /** Total members in organisation */
  total_members: number
  /** Members active in last 7 days */
  active_members_7_days: number
  /** Members active in last 30 days */
  active_members_30_days: number
  /** Total courses assigned to members */
  total_assigned_courses: number
  /** Average course completion rate across all courses */
  avg_completion_rate: number
  /** Tokens used in last 7 days */
  token_used_7_days: number
  /** Tokens used in last 30 days */
  token_used_30_days: number
  /** Top performing courses */
  top_courses?: Array<{
    course_id: number
    course_title: string
    enrolled_count: number
    avg_progress: number
  }>
  /** Top performing members */
  top_users?: Array<{
    user_id: number
    user_name: string
    courses_completed: number
    total_progress: number
  }>
}

/**
 * Single data point in time series (for graphs/charts).
 */
export interface TimeSeriesPoint {
  /** Date for this data point (ISO 8601 format) */
  date: string
  /** Numeric value for this point */
  value: number
}

/**
 * Course analytics data.
 * Statistics about course performance in organisation.
 */
export interface OrgAnalyticsCourse {
  /** Course identifier */
  course_id: number
  /** Course title */
  title: string
  /** Number of members enrolled in this course */
  enrolled_count: number
  /** Average progress percentage across all enrolled members */
  avg_progress: number
  /** Course completion rate percentage */
  completion_rate?: number
  /** Total interaction events for this course */
  events_count?: number
}

/**
 * Chapter analytics data.
 * Statistics about chapter/module performance within a course.
 *
 * @note In 2025-11-27, backend refactored modules → chapters terminology
 * Use chapter_id / chapter_title, but OrgAnalyticsModule alias provided for compatibility
 */
export interface OrgAnalyticsChapter {
  /** Chapter/module identifier */
  chapter_id: string
  /** Chapter/module title */
  chapter_title: string
  /** Course this chapter belongs to */
  course_title: string
  /** Number of members who completed this chapter */
  completions: number
  /** Average time spent in this chapter (minutes) */
  avg_time_spent?: number
}

/**
 * Backward compatibility alias for modules → chapters refactoring.
 * @deprecated Use OrgAnalyticsChapter instead
 */
export type OrgAnalyticsModule = OrgAnalyticsChapter

// ============================================================================
// Analytics API Functions
// ============================================================================

/**
 * Get organisation analytics overview (org admin).
 *
 * High-level summary of organisation activity and engagement.
 * Useful for dashboard and executive reports.
 *
 * @param orgId - Organisation identifier
 * @returns Analytics overview with summary stats
 *
 * @example
 * const analytics = await getOrganisationAnalytics(123)
 * console.log(`Active members (7d): ${analytics.active_members_7_days}`)
 * console.log(`Avg completion rate: ${analytics.avg_completion_rate}%`)
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
 * Get organisation token usage (org admin).
 *
 * Track AI token consumption over time.
 * Useful for budget tracking and usage forecasting.
 *
 * @param orgId - Organisation identifier
 * @param days - Time period to query (7, 30, or all time if undefined)
 * @returns Total usage, available tokens, and daily breakdown
 *
 * @example
 * const usage = await getOrganisationTokenUsage(123, 30)
 * console.log(`30-day usage: ${usage.total_used} tokens`)
 * console.log(`Available: ${usage.available} tokens`)
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
 * Get organisation member progress (org admin).
 *
 * Detailed progress report for a specific member.
 * Shows all assigned courses and completion status.
 *
 * @param orgId - Organisation identifier
 * @param userId - Member identifier
 * @returns Member details with course progress
 *
 * @example
 * const progress = await getOrganisationMemberProgress(123, 456)
 * console.log(`Member: ${progress.user.first_name} ${progress.user.last_name}`)
 * progress.courses.forEach(c => {
 *   console.log(`${c.course_title}: ${c.progress_percentage}%`)
 * })
 */
export const getOrganisationMemberProgress = async (
  orgId: number,
  userId: number
): Promise<{
  user: {
    user_id: number
    email: string
    first_name: string
    last_name: string
    role: string
    org_role?: string
    is_active: boolean
    joined_at: string
    last_active?: string | null
    token_usage?: number
    assigned_courses?: number
  }
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
    user: {
      user_id: number
      email: string
      first_name: string
      last_name: string
      role: string
      org_role?: string
      is_active: boolean
      joined_at: string
      last_active?: string | null
      token_usage?: number
      assigned_courses?: number
    }
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
// Advanced Analytics API Functions
// ============================================================================

/**
 * Get organisation events time series (org admin).
 *
 * Time-series data of learning events for dashboard graphs.
 * Shows activity trends over selected period.
 *
 * @param orgId - Organisation identifier
 * @param params - Time period parameters
 * @returns Array of daily data points
 *
 * @example
 * const timeSeries = await orgGetEventsTimeSeries(123, { days: 30 })
 * timeSeries.forEach(point => {
 *   console.log(`${point.date}: ${point.value} events`)
 * })
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
 * Get organisation active members time series (org admin).
 *
 * Track active member count over time.
 * Useful for engagement trend analysis.
 *
 * @param orgId - Organisation identifier
 * @param params - Time period parameters
 * @returns Array of daily active member counts
 *
 * @example
 * const activeMembers = await orgGetActiveMembersTimeSeries(123, { days: 30 })
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
 * Get organisation top courses (org admin).
 *
 * Rank courses by engagement and completion within organisation.
 *
 * @param orgId - Organisation identifier
 * @param params - Limit and time period
 * @returns Sorted list of top courses
 *
 * @example
 * const topCourses = await orgGetTopCourses(123, { limit: 5, days: 30 })
 * topCourses.forEach(c => {
 *   console.log(`${c.title}: ${c.avg_progress}% avg progress`)
 * })
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
 * Get organisation top modules/chapters (org admin).
 *
 * Rank chapters within courses by completion rate.
 *
 * @param orgId - Organisation identifier
 * @param params - Limit and time period
 * @returns Sorted list of top chapters
 *
 * @example
 * const topChapters = await orgGetTopModules(123, { limit: 10 })
 * topChapters.forEach(c => {
 *   console.log(`${c.chapter_title}: ${c.completions} completions`)
 * })
 *
 * @note This function works with both modules and chapters terminology
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
