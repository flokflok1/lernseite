/**
 * useAnalyticsData
 *
 * Composable for loading course analytics data and formatting values.
 * Used by AnalyticsTab and its sub-components.
 */

import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'

export interface AnalyticsContent {
  chapter_count: number
  published_chapters: number
  lesson_count: number
  published_lessons: number
  method_count: number
  unique_methods: number
}

export interface AnalyticsAiUsage {
  total_requests: number
  total_tokens: number
  total_cost_usd: number
  request_types: number
  unique_users: number
  period_days: number
  by_type: Array<{ type: string; count: number; tokens: number }>
}

export interface AnalyticsEnrollments {
  total_enrollments: number
  active_enrollments: number
  completed_enrollments: number
  avg_progress: number
}

export interface MethodDistributionEntry {
  method_type: number
  method_name: string
  count: number
}

export interface RecentSession {
  session_id: string
  status: string
  model_profile: string
  tokens_used: number
  operations: number
  created_at: string
  updated_at: string
}

export interface Analytics {
  content?: AnalyticsContent
  ai_usage?: AnalyticsAiUsage
  enrollments?: AnalyticsEnrollments
  method_distribution?: MethodDistributionEntry[]
  recent_sessions?: RecentSession[]
  generated_at?: string
}

/**
 * Format large token numbers with K/M suffix
 */
export function formatTokens(tokens: number): string {
  if (tokens >= 1000000) return (tokens / 1000000).toFixed(1) + 'M'
  if (tokens >= 1000) return (tokens / 1000).toFixed(1) + 'K'
  return tokens.toString()
}

/**
 * Format ISO date string to localized short format
 */
export function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '-'
  }
}

/**
 * Composable for loading and managing course analytics data.
 *
 * @param getCourseId - Getter function that returns the current course ID or undefined
 */
export function useAnalyticsData(getCourseId: () => string | undefined) {
  const loading = ref(false)
  const analytics = ref<Analytics>({})

  async function loadAnalytics(): Promise<void> {
    const courseId = getCourseId()
    if (!courseId) return

    loading.value = true
    try {
      const response = await http.get(`/admin/course-analytics/${courseId}`)
      analytics.value = response.data.data || {}
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      loading.value = false
    }
  }

  function resetAnalytics(): void {
    analytics.value = {}
  }

  return {
    loading,
    analytics,
    loadAnalytics,
    resetAnalytics
  }
}

/**
 * Composable for formatting request type labels via i18n with fallback.
 */
export function useRequestTypeFormatter() {
  const { t } = useI18n()

  function formatRequestType(type: string): string {
    const key = `aiEditorAnalytics.requestTypeLabels.${type}`
    const translated = t(key)
    return translated !== key ? translated : type
  }

  return { formatRequestType }
}
