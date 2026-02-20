/**
 * useSyncManager Composable
 *
 * Manages i18n synchronization workflow state and API calls.
 * Used by I18nSyncDashboard and its sub-panels.
 *
 * TODO: Wire up to actual i18n sync API endpoints when backend is ready.
 *       Backend sync service: app/application/services/i18n/legacy/sync_service.py
 */

import { ref, computed } from 'vue'
import type {
  SyncMode,
  SyncStatus,
  ScanResultsResponse,
  ComparisonPanelResponse,
  ComparisonItem,
  DashboardResponse,
  SyncHistorySummary,
  ResolutionUpdate,
  ResolutionAction
} from '@/infrastructure/api/clients/panel/admin'

export function useSyncManager() {
  // ============================================================================
  // STATE
  // ============================================================================

  const selectedMode = ref<SyncMode>('full')
  const selectedLanguages = ref<string[]>(['de', 'en', 'pl'])
  const selectedCategory = ref<string | undefined>(undefined)
  const currentSyncId = ref<string | undefined>(undefined)
  const currentStatus = ref<SyncStatus>('idle')

  const isScanning = ref(false)
  const isLoadingDashboard = ref(false)
  const isLoadingComparison = ref(false)
  const isLoadingHistory = ref(false)
  const isApplying = ref(false)
  const error = ref<string | undefined>(undefined)
  const applyError = ref<string | undefined>(undefined)

  const scanResults = ref<ScanResultsResponse | null>(null)
  const dashboardStats = ref<DashboardResponse | null>(null)
  const comparisonPanel = ref<ComparisonPanelResponse | null>(null)
  const resolutions = ref<Record<string, ResolutionUpdate>>({})

  // History
  const historyItems = ref<SyncHistorySummary[]>([])
  const historyPage = ref(1)
  const historyPageSize = 10

  // Comparison pagination
  const comparisonPage = ref(1)
  const comparisonPageSize = ref(20)

  // ============================================================================
  // COMPUTED
  // ============================================================================

  const paginatedComparisonItems = computed((): ComparisonItem[] => {
    if (!comparisonPanel.value?.items) return []
    const start = (comparisonPage.value - 1) * comparisonPageSize.value
    return comparisonPanel.value.items.slice(start, start + comparisonPageSize.value)
  })

  const comparisonTotalPages = computed(() => {
    if (!comparisonPanel.value?.items) return 0
    return Math.ceil(comparisonPanel.value.items.length / comparisonPageSize.value)
  })

  const pendingResolutionsCount = computed(() => {
    return Object.keys(resolutions.value).length
  })

  const conflictsCount = computed(() => {
    if (!comparisonPanel.value?.items) return 0
    return comparisonPanel.value.items.filter(i => i.change_type === 'conflict').length
  })

  const canApply = computed(() => {
    return pendingResolutionsCount.value > 0 && !isApplying.value
  })

  const paginatedHistory = computed((): SyncHistorySummary[] => {
    const start = (historyPage.value - 1) * historyPageSize
    return historyItems.value.slice(start, start + historyPageSize)
  })

  const historyTotalPages = computed(() => {
    return Math.ceil(historyItems.value.length / historyPageSize)
  })

  // ============================================================================
  // ACTIONS (TODO: wire to API)
  // ============================================================================

  async function startScan(): Promise<void> {
    isScanning.value = true
    error.value = undefined
    try {
      // TODO: POST /api/v1/panel/i18n-sync/scan
      console.warn('[useSyncManager] startScan: not yet connected to API')
    } catch (err: any) {
      error.value = err.message || 'Scan failed'
      throw err
    } finally {
      isScanning.value = false
    }
  }

  async function loadDashboard(): Promise<void> {
    isLoadingDashboard.value = true
    try {
      // TODO: GET /api/v1/panel/i18n-sync/dashboard
      console.warn('[useSyncManager] loadDashboard: not yet connected to API')
    } catch (err: any) {
      error.value = err.message || 'Failed to load dashboard'
    } finally {
      isLoadingDashboard.value = false
    }
  }

  async function getComparisonPanel(syncId: string): Promise<void> {
    isLoadingComparison.value = true
    try {
      // TODO: GET /api/v1/panel/i18n-sync/{syncId}/comparison
      console.warn('[useSyncManager] getComparisonPanel: not yet connected to API')
    } catch (err: any) {
      error.value = err.message || 'Failed to load comparison'
    } finally {
      isLoadingComparison.value = false
    }
  }

  async function loadHistory(): Promise<void> {
    isLoadingHistory.value = true
    try {
      // TODO: GET /api/v1/panel/i18n-sync/history
      console.warn('[useSyncManager] loadHistory: not yet connected to API')
    } catch (err: any) {
      error.value = err.message || 'Failed to load history'
    } finally {
      isLoadingHistory.value = false
    }
  }

  function setResolution(changeId: string, action: ResolutionAction): void {
    resolutions.value[changeId] = { change_id: changeId, action }
  }

  function clearResolution(changeId: string): void {
    delete resolutions.value[changeId]
  }

  async function applySync(): Promise<void> {
    isApplying.value = true
    applyError.value = undefined
    try {
      // TODO: POST /api/v1/panel/i18n-sync/{currentSyncId}/apply
      console.warn('[useSyncManager] applySync: not yet connected to API')
    } catch (err: any) {
      applyError.value = err.message || 'Apply failed'
      throw err
    } finally {
      isApplying.value = false
    }
  }

  async function rollbackSync(syncId: string, reason: string): Promise<void> {
    try {
      // TODO: POST /api/v1/panel/i18n-sync/{syncId}/rollback
      console.warn('[useSyncManager] rollbackSync: not yet connected to API')
    } catch (err: any) {
      error.value = err.message || 'Rollback failed'
      throw err
    }
  }

  function reset(): void {
    currentSyncId.value = undefined
    currentStatus.value = 'idle'
    scanResults.value = null
    comparisonPanel.value = null
    resolutions.value = {}
    error.value = undefined
    applyError.value = undefined
  }

  return {
    // State
    selectedMode,
    selectedLanguages,
    selectedCategory,
    currentSyncId,
    currentStatus,
    isScanning,
    isLoadingDashboard,
    isLoadingComparison,
    isLoadingHistory,
    isApplying,
    error,
    applyError,
    scanResults,
    dashboardStats,
    comparisonPanel,
    resolutions,

    // Comparison pagination
    paginatedComparisonItems,
    comparisonPage,
    comparisonTotalPages,
    comparisonPageSize,
    pendingResolutionsCount,
    conflictsCount,
    canApply,

    // History pagination
    historyPage,
    paginatedHistory,
    historyTotalPages,

    // Actions
    startScan,
    loadDashboard,
    getComparisonPanel,
    loadHistory,
    setResolution,
    clearResolution,
    applySync,
    rollbackSync,
    reset
  }
}
