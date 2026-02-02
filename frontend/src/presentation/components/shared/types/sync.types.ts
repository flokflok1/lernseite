/**
 * i18n Sync System - TypeScript Type Definitions
 *
 * Type-safe interfaces matching backend Pydantic models
 * for frontend-backend communication
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum SyncMode {
  MANUAL = 'MANUAL',
  AUTO = 'AUTO'
}

export enum SyncStatus {
  SCANNING = 'SCANNING',
  PENDING = 'PENDING',
  APPLYING = 'APPLYING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  ROLLED_BACK = 'ROLLED_BACK'
}

export enum ResolutionAction {
  ADD = 'ADD',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
  SKIP = 'SKIP',
  CONFLICT = 'CONFLICT'
}

export enum ResolutionStatus {
  PENDING = 'PENDING',
  RESOLVED = 'RESOLVED',
  MANUAL_OVERRIDE = 'MANUAL_OVERRIDE',
  FAILED = 'FAILED'
}

export enum ChangeMagnitude {
  MINOR = 'MINOR',
  MODERATE = 'MODERATE',
  MAJOR = 'MAJOR'
}

// ============================================================================
// SCAN & SYNC HISTORY
// ============================================================================

export interface ScanSummary {
  scan_status: 'COMPLETED' | 'FAILED'
  total_keys: number
  new_keys: number
  changed_keys: number
  deleted_keys: number
  conflicted_keys: number
  languages_affected: string[]
  scan_duration_ms: number
  error_message?: string
}

export interface SyncHistoryResponse {
  sync_id: string
  sync_mode: SyncMode
  sync_status: SyncStatus
  languages_affected: string[]

  // Statistics
  total_keys: number
  keys_added: number
  keys_updated: number
  keys_deleted: number
  keys_skipped: number
  keys_conflicted: number

  // Timeline
  scan_started_at?: string
  scan_completed_at?: string
  apply_started_at?: string
  apply_completed_at?: string

  // Metadata
  initiated_by?: string
  completed_by?: string
  error_message?: string
  created_at: string
  updated_at?: string
}

export interface SyncHistorySummary {
  sync_id: string
  sync_mode: SyncMode
  sync_status: SyncStatus
  total_changes: number
  conflicts: number
  created_at: string
  initiated_by?: string
}

// ============================================================================
// COMPARISON & SYNC DETAILS
// ============================================================================

export interface ComparisonItem {
  namespace_code: string
  key_path: string
  language: string

  action: ResolutionAction
  resolution_status: ResolutionStatus

  frontend_value?: string
  database_value?: string
  similarity: number

  conflict_reason?: string
  proposed_action?: string
}

export interface ComparisonCategory {
  category: 'NEW_KEYS' | 'CHANGED_KEYS' | 'DELETED_KEYS' | 'CONFLICTS'
  items: ComparisonItem[]
  count: number
}

export interface ComparisonPanelResponse {
  success: boolean
  sync_id: string
  categories: ComparisonCategory[]
  total_items: number
  sync_mode: SyncMode
  pending_count: number
  conflicts_count: number
  can_apply: boolean
}

export interface SyncDetailResponse {
  detail_id: string
  sync_id: string
  namespace_code: string
  key_path: string
  language: string

  action: ResolutionAction
  resolution_status: ResolutionStatus

  frontend_value?: string
  database_value?: string
  similarity_score: number

  conflict_reason?: string
  manual_resolution_value?: string

  is_new: boolean
  is_changed: boolean
  is_deleted: boolean
  change_magnitude?: ChangeMagnitude

  resolved_by?: string
  created_at: string
  updated_at?: string
}

// ============================================================================
// SCAN RESULTS
// ============================================================================

export interface ScanResultsResponse {
  success: boolean
  sync_id: string
  summary: ScanSummary
  next_action: 'REVIEW' | 'APPLY_AUTO' | 'APPLY_MANUAL'
}

// ============================================================================
// APPLY & ROLLBACK
// ============================================================================

export interface ResolutionUpdate {
  action: ResolutionAction
  manual_value?: string
}

export interface ApplyRequest {
  sync_id: string
  resolutions?: Record<string, ResolutionUpdate>
  force?: boolean
}

export interface ApplyResponse {
  success: boolean
  status: 'COMPLETED' | 'FAILED'
  applied_count: number
  failed_count: number
  errors: string[]
}

export interface RollbackRequest {
  reason?: string
}

export interface RollbackResponse {
  success: boolean
  keys_restored: number
  rollback_duration_ms: number
  message: string
}

// ============================================================================
// DASHBOARD
// ============================================================================

export interface SyncStatistics {
  total_syncs: number
  syncs_today: number
  successful_syncs: number
  failed_syncs: number
  last_sync_id?: string
  last_sync_timestamp?: string
  last_sync_mode?: SyncMode
  avg_sync_duration_ms: number
  pending_resolutions: number
}

export interface DashboardResponse {
  success: boolean
  data: {
    total_syncs: number
    syncs_today: number
    successful_syncs: number
    failed_syncs: number
    pending_resolutions: number
    recent_syncs: SyncHistorySummary[]
  }
}

// ============================================================================
// HISTORY LIST
// ============================================================================

export interface HistoryListResponse {
  success: boolean
  data: SyncHistorySummary[]
  meta: {
    total: number
    limit: number
    offset: number
    timestamp: string
  }
}

// ============================================================================
// ERROR RESPONSE
// ============================================================================

export interface ErrorResponse {
  success: boolean
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

// ============================================================================
// UI STATE
// ============================================================================

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
