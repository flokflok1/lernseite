/**
 * Admin Analytics, Billing & System Stats API
 */

import http from '@/infrastructure/api/http'
import type {
  AdminUser,
  AdminTokenStats,
  AdminSystemStats,
  AdminPlanOverview,
  UserStatsData,
  CourseStatsData,
  SystemStatsData,
  TimeSeriesPoint,
  AdminAnalyticsCourse,
  AdminAnalyticsMethod
} from './types'

// Billing & Tokens

export const adminGetGlobalTokenStats = async (): Promise<AdminTokenStats> => {
  const response = await http.get<{
    success: boolean
    stats: AdminTokenStats
  }>('/admin/tokens/stats')

  return response.data.stats
}

export const adminGetPlanOverview = async (): Promise<AdminPlanOverview[]> => {
  const response = await http.get<{
    success: boolean
    plans: AdminPlanOverview[]
  }>('/admin/billing/plans')

  return response.data.plans
}

// System Analytics

export const adminGetSystemStats = async (): Promise<AdminSystemStats> => {
  const response = await http.get<{
    success: boolean
    data: AdminSystemStats
  }>('/admin/stats/system')

  return response.data.data
}

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

// Dashboard Stats

export const adminGetUserStats = async (): Promise<UserStatsData> => {
  const response = await http.get<{
    success: boolean
    data: UserStatsData
  }>('/admin/stats/users')

  return response.data.data
}

export const adminGetCourseStats = async (): Promise<CourseStatsData> => {
  const response = await http.get<{
    success: boolean
    data: CourseStatsData
  }>('/admin/stats/courses')

  return response.data.data
}

export const adminGetSystemStatsData = async (): Promise<SystemStatsData> => {
  const response = await http.get<{
    success: boolean
    data: SystemStatsData
  }>('/admin/stats/system')

  return response.data.data
}

// Advanced Analytics

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
