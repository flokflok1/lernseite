/**
 * Admin API - Analytics Types
 *
 * Types for admin analytics dashboards: user stats,
 * course stats, system stats, and time-series data.
 */

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
