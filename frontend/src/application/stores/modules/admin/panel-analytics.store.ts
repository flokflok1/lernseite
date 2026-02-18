/**
 * LernsystemX - Panel Analytics & System Sub-Store (Pinia)
 *
 * Manages:
 * - System statistics (dashboard overview)
 * - Analytics time series and top lists
 * - Audit logs with pagination and filters
 * - Billing plan overview
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as adminApi from '@/application/services/api/panel-admin'
import type {
  AdminSystemStats,
  AdminTokenStats,
  AdminPlanOverview,
  TimeSeriesPoint,
  AdminAnalyticsCourse,
  AdminAnalyticsMethod,
  AuditLog,
  AuditLogsFilterParams,
  PaginatedResponse
} from '@/application/services/api/panel-admin'

export const usePanelAnalyticsStore = defineStore('panel-analytics', () => {
  // State - System Stats
  const systemStats = ref<AdminSystemStats | null>(null)
  const tokenStats = ref<AdminTokenStats | null>(null)
  const plans = ref<AdminPlanOverview[]>([])

  // State - Audit Logs
  const auditLogs = ref<AuditLog[]>([])
  const auditLogsTotal = ref(0)
  const auditLogsPage = ref(1)
  const auditLogsLimit = ref(20)
  const auditLogsTotalPages = ref(0)
  const auditLogsFilters = ref<AuditLogsFilterParams>({})

  // State - Analytics
  const systemAnalytics = ref<{
    timeframe: 7 | 30 | 90
    eventsTimeSeries: TimeSeriesPoint[]
    activeUsersTimeSeries: TimeSeriesPoint[]
    topCourses: AdminAnalyticsCourse[]
    topMethods: AdminAnalyticsMethod[]
  } | null>(null)
  const systemAnalyticsLoading = ref(false)
  const systemAnalyticsError = ref<string | null>(null)

  // State - UI
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
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
  // Actions - Audit Logs
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
   * Load admin analytics (time series and top lists)
   */
  const loadAdminAnalytics = async (timeframe: 7 | 30 | 90 = 7): Promise<void> => {
    systemAnalyticsLoading.value = true
    systemAnalyticsError.value = null

    try {
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

  return {
    // State - System
    systemStats,
    tokenStats,
    plans,

    // State - Audit Logs
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

    // Actions
    loadAdminDashboard,
    loadAuditLogs,
    loadPlans,
    loadAdminAnalytics,
    changeAnalyticsTimeframe
  }
})
