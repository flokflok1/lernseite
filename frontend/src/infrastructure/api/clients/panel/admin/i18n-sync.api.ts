/**
 * i18n Sync API Client
 *
 * HTTP client for i18n synchronization endpoints
 * All requests require admin authentication
 */

import api from '@/infrastructure/api/http'
import type {
  SyncMode,
  ScanResultsResponse,
  ComparisonPanelResponse,
  ApplyRequest,
  ApplyResponse,
  RollbackResponse,
  HistoryListResponse,
  DashboardResponse,
  ErrorResponse
} from './i18n-sync.types'

// Note: http.ts already has baseURL '/api/v1', so we only need the relative path
const BASE_URL = '/admin/i18n-sync'

/**
 * i18n Sync API Service
 */
export const i18nSyncApi = {
  /**
   * Initiate a new translation synchronization scan
   *
   * @param syncMode - 'MANUAL' or 'AUTO' mode
   * @param languagesAffected - List of language codes to sync (e.g., ['de', 'en', 'pl'])
   * @returns Promise with sync_id and initial scan results
   *
   * @example
   * const result = await i18nSyncApi.startScan('MANUAL', ['de', 'en'])
   * console.log(result.sync_id) // uuid
   */
  startScan: async (
    syncMode: SyncMode,
    languagesAffected: string[]
  ): Promise<ScanResultsResponse> => {
    try {
      const response = await api.post(`${BASE_URL}/scan`, {
        sync_mode: syncMode,
        languages_affected: languagesAffected
      })
      return response.data.data
    } catch (error: any) {
      const errorData = error.response?.data as ErrorResponse
      throw new Error(
        errorData?.error?.message || 'Failed to start sync scan'
      )
    }
  },

  /**
   * Get comparison panel for a sync operation
   *
   * Displays side-by-side comparison of frontend vs database translations
   * Results are grouped by category: NEW_KEYS, CHANGED_KEYS, DELETED_KEYS, CONFLICTS
   *
   * @param syncId - UUID of the sync operation
   * @param category - Optional filter by category
   * @param limit - Max items per page (default 50, max 100)
   * @param offset - Pagination offset (default 0)
   * @returns Promise with comparison data grouped by categories
   *
   * @example
   * const panel = await i18nSyncApi.getComparisonPanel(
   *   'uuid-here',
   *   'NEW_KEYS',
   *   50,
   *   0
   * )
   * console.log(panel.categories) // ComparisonCategory[]
   */
  getComparisonPanel: async (
    syncId: string,
    category?: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<ComparisonPanelResponse> => {
    try {
      const params = new URLSearchParams()
      if (category) params.append('category', category)
      params.append('limit', Math.min(limit, 100).toString())
      params.append('offset', offset.toString())

      const response = await api.get(
        `${BASE_URL}/${syncId}/compare?${params.toString()}`
      )
      return response.data.data
    } catch (error: any) {
      const errorData = error.response?.data as ErrorResponse
      throw new Error(
        errorData?.error?.message || 'Failed to get comparison panel'
      )
    }
  },

  /**
   * Apply sync changes to database
   *
   * In MANUAL mode: Applies only keys with provided resolutions
   * In AUTO mode: Applies all keys with auto-generated actions
   *
   * @param request - Apply request with sync_id, resolutions, and force flag
   * @returns Promise with apply results
   *
   * @example
   * const result = await i18nSyncApi.applySync({
   *   sync_id: 'uuid-here',
   *   resolutions: {
   *     'detail-id-1': { action: 'SKIP' },
   *     'detail-id-2': { action: 'UPDATE', manual_value: 'New value' }
   *   },
   *   force: false
   * })
   */
  applySync: async (request: ApplyRequest): Promise<ApplyResponse> => {
    try {
      const response = await api.post(`${BASE_URL}/apply`, {
        sync_id: request.sync_id,
        resolutions: request.resolutions || {},
        force: request.force || false
      })
      return response.data.data
    } catch (error: any) {
      const errorData = error.response?.data as ErrorResponse

      // Handle conflict error (409)
      if (error.response?.status === 409) {
        throw new Error(
          errorData?.error?.message || 'Unresolved conflicts - use force=true to override'
        )
      }

      throw new Error(
        errorData?.error?.message || 'Failed to apply sync changes'
      )
    }
  },

  /**
   * Rollback sync to previous state
   *
   * Restores all translations to state before this sync was applied
   * Creates ROLLBACK type snapshot for audit trail
   *
   * @param syncId - UUID of the sync operation to rollback
   * @param reason - Optional reason for rollback
   * @returns Promise with rollback results
   *
   * @example
   * const result = await i18nSyncApi.rollbackSync(
   *   'uuid-here',
   *   'Admin requested rollback'
   * )
   */
  rollbackSync: async (
    syncId: string,
    reason: string = ''
  ): Promise<RollbackResponse> => {
    try {
      const response = await api.post(`${BASE_URL}/${syncId}/rollback`, {
        reason: reason || 'Admin requested rollback'
      })
      return response.data.data
    } catch (error: any) {
      const errorData = error.response?.data as ErrorResponse
      throw new Error(
        errorData?.error?.message || 'Failed to rollback sync'
      )
    }
  },

  /**
   * Get paginated list of past sync operations
   *
   * @param limit - Max results (default 20, max 100)
   * @param offset - Pagination offset (default 0)
   * @param status - Optional filter by status
   * @param mode - Optional filter by mode (MANUAL, AUTO)
   * @returns Promise with sync history list
   *
   * @example
   * const history = await i18nSyncApi.getSyncHistory(20, 0, 'COMPLETED', 'MANUAL')
   */
  getSyncHistory: async (
    limit: number = 20,
    offset: number = 0,
    status?: string,
    mode?: string
  ): Promise<HistoryListResponse> => {
    try {
      const params = new URLSearchParams()
      params.append('limit', Math.min(limit, 100).toString())
      params.append('offset', offset.toString())
      if (status) params.append('status', status)
      if (mode) params.append('mode', mode)

      const response = await api.get(`${BASE_URL}/history?${params.toString()}`)
      return response.data.data
    } catch (error: any) {
      const errorData = error.response?.data as ErrorResponse
      throw new Error(
        errorData?.error?.message || 'Failed to fetch sync history'
      )
    }
  },

  /**
   * Get dashboard statistics for i18n sync overview
   *
   * Returns overview metrics:
   * - Total syncs, syncs today
   * - Successful vs failed syncs
   * - Last sync information
   * - Average sync duration
   * - Pending manual resolutions
   * - Recent syncs list
   *
   * @returns Promise with dashboard statistics
   *
   * @example
   * const stats = await i18nSyncApi.getDashboardStats()
   * console.log(stats.data.total_syncs) // number
   */
  getDashboardStats: async (): Promise<DashboardResponse> => {
    try {
      const response = await api.get(`${BASE_URL}/dashboard`)
      return response.data.data
    } catch (error: any) {
      const errorData = error.response?.data as ErrorResponse
      throw new Error(
        errorData?.error?.message || 'Failed to fetch dashboard statistics'
      )
    }
  }
}
