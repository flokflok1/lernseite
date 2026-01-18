/**
 * useSyncManager Composable
 *
 * State management and business logic for i18n sync system
 * Handles scan initiation, comparison panel, apply/rollback operations
 */

import { ref, computed, reactive } from 'vue'
import { i18nSyncApi } from '@/api/admin/i18n-sync.api'
import type {
  SyncMode,
  SyncStatus,
  ResolutionAction,
  ScanResultsResponse,
  ComparisonPanelResponse,
  SyncHistorySummary,
  SyncStatistics,
  ResolutionUpdate,
  ComparisonItem
} from '@/components/admin/i18n-sync/types/sync.types'

/**
 * Main composable for managing i18n sync state and operations
 *
 * @example
 * const {
 *   selectedMode,
 *   currentSyncId,
 *   isScanning,
 *   scanResults,
 *   startScan,
 *   getComparisonPanel
 * } = useSyncManager()
 */
export function useSyncManager() {
  // ============================================================================
  // STATE
  // ============================================================================

  // UI Mode Selection
  const selectedMode = ref<SyncMode>('MANUAL')
  const selectedLanguages = ref<string[]>(['de', 'en', 'pl'])

  // Current Operation
  const currentSyncId = ref<string | null>(null)
  const currentStatus = ref<SyncStatus>('SCANNING')

  // Scan Results
  const scanResults = reactive<ScanResultsResponse | null>(null)
  const isScanning = ref(false)

  // Comparison Panel
  const comparisonPanel = reactive<ComparisonPanelResponse | null>(null)
  const isLoadingComparison = ref(false)
  const selectedCategory = ref<string | null>(null)
  const comparisonPage = ref(0)
  const comparisonPageSize = ref(50)

  // Resolutions (for MANUAL mode)
  const resolutions = reactive<Record<string, ResolutionUpdate>>({})

  // Apply Operation
  const isApplying = ref(false)
  const applyError = ref<string | null>(null)

  // Rollback Operation
  const isRollingBack = ref(false)
  const rollbackError = ref<string | null>(null)

  // History
  const syncHistory = ref<SyncHistorySummary[]>([])
  const isLoadingHistory = ref(false)
  const historyPage = ref(0)
  const historyPageSize = ref(20)

  // Dashboard
  const dashboardStats = reactive<SyncStatistics | null>(null)
  const isLoadingDashboard = ref(false)

  // Error Handling
  const error = ref<string | null>(null)

  // ============================================================================
  // COMPUTED PROPERTIES
  // ============================================================================

  /**
   * Current comparison items based on selected category and pagination
   */
  const currentComparisonItems = computed(() => {
    if (!comparisonPanel?.categories) return []

    if (selectedCategory.value) {
      const category = comparisonPanel.categories.find(
        c => c.category === selectedCategory.value
      )
      return category?.items || []
    }

    return comparisonPanel.categories.flatMap(c => c.items)
  })

  /**
   * Number of pending resolutions needed
   */
  const pendingResolutionsCount = computed(() => {
    return comparisonPanel?.pending_count || 0
  })

  /**
   * Number of conflicts detected
   */
  const conflictsCount = computed(() => {
    return comparisonPanel?.conflicts_count || 0
  })

  /**
   * Can we apply the sync?
   * - All conflicts must be resolved (unless forcing)
   * - Or all items must have resolutions in MANUAL mode
   */
  const canApply = computed(() => {
    if (!comparisonPanel) return false

    if (selectedMode.value === 'AUTO') {
      return comparisonPanel.can_apply
    }

    // MANUAL mode: All pending must be resolved
    return pendingResolutionsCount.value === 0
  })

  /**
   * Paginated comparison items
   */
  const paginatedComparisonItems = computed(() => {
    const start = comparisonPage.value * comparisonPageSize.value
    const end = start + comparisonPageSize.value
    return currentComparisonItems.value.slice(start, end)
  })

  /**
   * Total pages for comparison panel
   */
  const comparisonTotalPages = computed(() => {
    return Math.ceil(
      currentComparisonItems.value.length / comparisonPageSize.value
    )
  })

  /**
   * Paginated history items
   */
  const paginatedHistory = computed(() => {
    const start = historyPage.value * historyPageSize.value
    const end = start + historyPageSize.value
    return syncHistory.value.slice(start, end)
  })

  /**
   * Total pages for history
   */
  const historyTotalPages = computed(() => {
    return Math.ceil(syncHistory.value.length / historyPageSize.value)
  })

  // ============================================================================
  // METHODS
  // ============================================================================

  /**
   * Start a new sync scan
   */
  async function startScan() {
    try {
      error.value = null
      isScanning.value = true

      const results = await i18nSyncApi.startScan(
        selectedMode.value,
        selectedLanguages.value
      )

      // Store results
      Object.assign(scanResults, results)
      currentSyncId.value = results.sync_id
      currentStatus.value = 'PENDING'

      // Clear previous resolutions
      Object.keys(resolutions).forEach(key => delete resolutions[key])

      return results
    } catch (err: any) {
      error.value = err.message || 'Failed to start scan'
      throw err
    } finally {
      isScanning.value = false
    }
  }

  /**
   * Get comparison panel data
   */
  async function getComparisonPanel(reset = false) {
    if (!currentSyncId.value) {
      error.value = 'No active sync operation'
      return
    }

    try {
      error.value = null
      isLoadingComparison.value = true

      if (reset) {
        selectedCategory.value = null
        comparisonPage.value = 0
      }

      const panel = await i18nSyncApi.getComparisonPanel(
        currentSyncId.value,
        selectedCategory.value || undefined,
        comparisonPageSize.value,
        comparisonPage.value * comparisonPageSize.value
      )

      // Store panel data
      Object.assign(comparisonPanel, panel)

      return panel
    } catch (err: any) {
      error.value = err.message || 'Failed to get comparison panel'
      throw err
    } finally {
      isLoadingComparison.value = false
    }
  }

  /**
   * Set resolution for a comparison item
   */
  function setResolution(
    detailId: string,
    action: ResolutionAction,
    manualValue?: string
  ) {
    resolutions[detailId] = {
      action,
      manual_value: manualValue
    }
  }

  /**
   * Clear resolution for a comparison item
   */
  function clearResolution(detailId: string) {
    delete resolutions[detailId]
  }

  /**
   * Clear all resolutions
   */
  function clearAllResolutions() {
    Object.keys(resolutions).forEach(key => delete resolutions[key])
  }

  /**
   * Apply sync changes
   */
  async function applySync(force = false) {
    if (!currentSyncId.value) {
      error.value = 'No active sync operation'
      return
    }

    try {
      error.value = null
      applyError.value = null
      isApplying.value = true

      const result = await i18nSyncApi.applySync({
        sync_id: currentSyncId.value,
        resolutions:
          selectedMode.value === 'MANUAL' ? resolutions : undefined,
        force
      })

      currentStatus.value = 'COMPLETED'
      return result
    } catch (err: any) {
      applyError.value = err.message || 'Failed to apply sync'
      error.value = applyError.value
      throw err
    } finally {
      isApplying.value = false
    }
  }

  /**
   * Rollback sync operation
   */
  async function rollbackSync(reason = '') {
    if (!currentSyncId.value) {
      error.value = 'No active sync operation'
      return
    }

    try {
      error.value = null
      rollbackError.value = null
      isRollingBack.value = true

      const result = await i18nSyncApi.rollbackSync(
        currentSyncId.value,
        reason
      )

      currentStatus.value = 'ROLLED_BACK'
      return result
    } catch (err: any) {
      rollbackError.value = err.message || 'Failed to rollback sync'
      error.value = rollbackError.value
      throw err
    } finally {
      isRollingBack.value = false
    }
  }

  /**
   * Load sync history
   */
  async function loadHistory(
    status?: string,
    mode?: string
  ) {
    try {
      error.value = null
      isLoadingHistory.value = true

      const result = await i18nSyncApi.getSyncHistory(
        historyPageSize.value,
        historyPage.value * historyPageSize.value,
        status,
        mode
      )

      syncHistory.value = result.data || []
      return result
    } catch (err: any) {
      error.value = err.message || 'Failed to load history'
      throw err
    } finally {
      isLoadingHistory.value = false
    }
  }

  /**
   * Load dashboard statistics
   */
  async function loadDashboard() {
    try {
      error.value = null
      isLoadingDashboard.value = true

      const result = await i18nSyncApi.getDashboardStats()

      Object.assign(dashboardStats, result.data)
      return result
    } catch (err: any) {
      error.value = err.message || 'Failed to load dashboard'
      throw err
    } finally {
      isLoadingDashboard.value = false
    }
  }

  /**
   * Reset all state
   */
  function reset() {
    currentSyncId.value = null
    currentStatus.value = 'SCANNING'
    Object.assign(scanResults, null)
    Object.assign(comparisonPanel, null)
    clearAllResolutions()
    error.value = null
    applyError.value = null
    rollbackError.value = null
    selectedCategory.value = null
    comparisonPage.value = 0
    historyPage.value = 0
  }

  // ============================================================================
  // RETURN
  // ============================================================================

  return {
    // State - Mode Selection
    selectedMode,
    selectedLanguages,

    // State - Current Operation
    currentSyncId,
    currentStatus,

    // State - Scan
    scanResults,
    isScanning,

    // State - Comparison
    comparisonPanel,
    isLoadingComparison,
    selectedCategory,
    comparisonPage,
    comparisonPageSize,
    paginatedComparisonItems,
    comparisonTotalPages,

    // State - Resolutions
    resolutions,

    // State - Apply
    isApplying,
    applyError,

    // State - Rollback
    isRollingBack,
    rollbackError,

    // State - History
    syncHistory,
    isLoadingHistory,
    historyPage,
    historyPageSize,
    paginatedHistory,
    historyTotalPages,

    // State - Dashboard
    dashboardStats,
    isLoadingDashboard,

    // State - Error
    error,

    // Computed
    currentComparisonItems,
    pendingResolutionsCount,
    conflictsCount,
    canApply,

    // Methods
    startScan,
    getComparisonPanel,
    setResolution,
    clearResolution,
    clearAllResolutions,
    applySync,
    rollbackSync,
    loadHistory,
    loadDashboard,
    reset
  }
}
