/**
 * i18n Sync System - Type Definitions
 *
 * API types re-exported from infrastructure (canonical source).
 * SyncUIState is presentation-only and defined here.
 */

// Re-export all API types from infrastructure
export {
  SyncMode,
  SyncStatus,
  ResolutionAction,
  ResolutionStatus,
  ChangeMagnitude
} from '@/infrastructure/api/clients/panel/admin/i18n-sync.types'

export type {
  ScanSummary,
  SyncHistoryResponse,
  SyncHistorySummary,
  ComparisonItem,
  ComparisonCategory,
  ComparisonPanelResponse,
  SyncDetailResponse,
  ScanResultsResponse,
  ResolutionUpdate,
  ApplyRequest,
  ApplyResponse,
  RollbackRequest,
  RollbackResponse,
  SyncStatistics,
  DashboardResponse,
  HistoryListResponse,
  ErrorResponse
} from '@/infrastructure/api/clients/panel/admin/i18n-sync.types'

// ============================================================================
// UI STATE (Presentation-only, not an API type)
// ============================================================================

import type { SyncMode, SyncStatus, ResolutionUpdate } from '@/infrastructure/api/clients/panel/admin/i18n-sync.types'

export interface SyncUIState {
  selectedMode: SyncMode
  currentSyncId?: string
  currentStatus: SyncStatus
  selectedCategory?: string
  selectedLanguages: string[]
  resolutions: Record<string, ResolutionUpdate>
  isLoading: boolean
  error?: string
}
