<script setup lang="ts">
/**
 * HistoryPanel Component
 *
 * Displays history of past i18n synchronization operations.
 * Shows summary, filtering options, pagination, and rollback capabilities.
 */

import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SyncHistorySummary } from '../types/sync.types'
import { useSyncManager } from '@/features/admin/useSyncManager'

const { t } = useI18n()
const {
  syncHistory,
  historyPage,
  historyPageSize,
  isLoadingHistory,
  paginatedHistory,
  historyTotalPages,
  loadHistory,
  rollbackSync
} = useSyncManager()

// UI State
const statusFilter = ref<string | null>(null)
const modeFilter = ref<string | null>(null)
const showRollbackConfirm = ref(false)
const selectedSyncForRollback = ref<SyncHistorySummary | null>(null)
const rollbackReason = ref('')

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(async () => {
  await loadHistory(statusFilter.value || undefined, modeFilter.value || undefined)
})

// ============================================================================
// COMPUTED
// ============================================================================

/**
 * Available status filters
 */
const statusOptions = computed(() => [
  { value: 'COMPLETED', label: t('admin.i18n.status_completed') },
  { value: 'FAILED', label: t('admin.i18n.status_failed') },
  { value: 'ROLLED_BACK', label: t('admin.i18n.status_rolled_back') }
])

/**
 * Available mode filters
 */
const modeOptions = computed(() => [
  { value: 'MANUAL', label: t('admin.i18n.mode_manual') },
  { value: 'AUTO', label: t('admin.i18n.mode_auto') }
])

/**
 * Get status badge class
 */
const getStatusClass = (status: string): string => {
  const statusMap: Record<string, string> = {
    'COMPLETED': 'status-completed',
    'FAILED': 'status-failed',
    'ROLLED_BACK': 'status-rolled_back'
  }
  return statusMap[status] || 'status-pending'
}

/**
 * Get status icon
 */
const getStatusIcon = (status: string): string => {
  const iconMap: Record<string, string> = {
    'COMPLETED': '✅',
    'FAILED': '❌',
    'ROLLED_BACK': '⏮️',
    'PENDING': '⏳'
  }
  return iconMap[status] || '❓'
}

/**
 * Format date time for display
 */
const formatDateTime = (dateStr: string | null): string => {
  if (!dateStr) return t('admin.i18n.not_applicable')
  const date = new Date(dateStr)
  return date.toLocaleString()
}

/**
 * Can this sync be rolled back?
 */
const canRollback = (sync: SyncHistorySummary): boolean => {
  return sync.sync_status === 'COMPLETED' && !sync.is_rolled_back
}

// ============================================================================
// METHODS
// ============================================================================

/**
 * Apply status filter
 */
async function applyStatusFilter(status: string | null) {
  statusFilter.value = status
  historyPage.value = 0
  await loadHistory(status || undefined, modeFilter.value || undefined)
}

/**
 * Apply mode filter
 */
async function applyModeFilter(mode: string | null) {
  modeFilter.value = mode
  historyPage.value = 0
  await loadHistory(statusFilter.value || undefined, mode || undefined)
}

/**
 * Change page
 */
async function changePage(newPage: number) {
  if (newPage >= 0 && newPage < historyTotalPages.value) {
    historyPage.value = newPage
    await loadHistory(statusFilter.value || undefined, modeFilter.value || undefined)
  }
}

/**
 * Open rollback confirmation
 */
function openRollbackConfirm(sync: SyncHistorySummary) {
  selectedSyncForRollback.value = sync
  rollbackReason.value = ''
  showRollbackConfirm.value = true
}

/**
 * Close rollback confirmation
 */
function closeRollbackConfirm() {
  showRollbackConfirm.value = false
  selectedSyncForRollback.value = null
  rollbackReason.value = ''
}

/**
 * Confirm rollback
 */
async function confirmRollback() {
  if (!selectedSyncForRollback.value) return

  try {
    await rollbackSync(rollbackReason.value)
    closeRollbackConfirm()
    // Reload history after successful rollback
    await loadHistory(statusFilter.value || undefined, modeFilter.value || undefined)
  } catch (err) {
    console.error('Rollback failed:', err)
  }
}
</script>

<template>
  <div class="history-panel">
    <!-- Header -->
    <div class="panel-header">
      <h2>{{ $t('admin.i18n.history_title') }}</h2>
      <p class="subtitle">{{ $t('admin.i18n.history_subtitle') }}</p>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label class="filter-label">{{ $t('admin.i18n.filter_status') }}</label>
        <div class="filter-buttons">
          <button
            class="filter-button"
            :class="{ active: statusFilter === null }"
            @click="applyStatusFilter(null)"
          >
            {{ $t('admin.i18n.all') }}
          </button>
          <button
            v-for="option in statusOptions"
            :key="option.value"
            class="filter-button"
            :class="{ active: statusFilter === option.value }"
            @click="applyStatusFilter(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">{{ $t('admin.i18n.filter_mode') }}</label>
        <div class="filter-buttons">
          <button
            class="filter-button"
            :class="{ active: modeFilter === null }"
            @click="applyModeFilter(null)"
          >
            {{ $t('admin.i18n.all') }}
          </button>
          <button
            v-for="option in modeOptions"
            :key="option.value"
            class="filter-button"
            :class="{ active: modeFilter === option.value }"
            @click="applyModeFilter(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoadingHistory" class="loading">
      <span class="spinner"></span>
      {{ $t('common.loading') }}
    </div>

    <!-- History Table -->
    <div v-else-if="paginatedHistory.length > 0" class="history-table">
      <div class="table-header">
        <div class="col-syncid">{{ $t('admin.i18n.sync_id') }}</div>
        <div class="col-mode">{{ $t('admin.i18n.mode') }}</div>
        <div class="col-status">{{ $t('admin.i18n.status') }}</div>
        <div class="col-changes">{{ $t('admin.i18n.total_changes') }}</div>
        <div class="col-conflicts">{{ $t('admin.i18n.conflicts') }}</div>
        <div class="col-timestamp">{{ $t('admin.i18n.created_at') }}</div>
        <div class="col-actions">{{ $t('admin.i18n.actions') }}</div>
      </div>

      <div
        v-for="sync in paginatedHistory"
        :key="sync.sync_id"
        class="table-row"
      >
        <div class="col-syncid">
          <code class="sync-id">{{ sync.sync_id }}</code>
        </div>

        <div class="col-mode">
          <span class="badge badge-mode" :class="`mode-${sync.sync_mode.toLowerCase()}`">
            {{ sync.sync_mode }}
          </span>
        </div>

        <div class="col-status">
          <span class="status-badge" :class="getStatusClass(sync.sync_status)">
            {{ getStatusIcon(sync.sync_status) }} {{ $t(`admin.i18n.status_${sync.sync_status.toLowerCase()}`) }}
          </span>
        </div>

        <div class="col-changes">
          <span class="changes-count">{{ sync.total_changes }}</span>
        </div>

        <div class="col-conflicts">
          <span v-if="sync.conflicts_count > 0" class="conflicts-badge">
            {{ sync.conflicts_count }}
          </span>
          <span v-else class="conflicts-none">—</span>
        </div>

        <div class="col-timestamp">
          <span class="timestamp">{{ formatDateTime(sync.created_at) }}</span>
        </div>

        <div class="col-actions">
          <button
            v-if="canRollback(sync)"
            class="btn btn-rollback"
            :title="$t('admin.i18n.rollback_tooltip')"
            @click="openRollbackConfirm(sync)"
          >
            ⏮️ {{ $t('admin.i18n.rollback') }}
          </button>
          <span v-else class="no-action">—</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>{{ $t('admin.i18n.no_history') }}</p>
    </div>

    <!-- Pagination -->
    <div v-if="historyTotalPages > 1" class="pagination">
      <button
        class="pagination-btn"
        :disabled="historyPage === 0"
        @click="changePage(historyPage - 1)"
      >
        {{ $t('admin.i18n.previous') }}
      </button>

      <div class="pagination-info">
        {{ $t('admin.i18n.page_info', {
          current: historyPage + 1,
          total: historyTotalPages
        }) }}
      </div>

      <button
        class="pagination-btn"
        :disabled="historyPage >= historyTotalPages - 1"
        @click="changePage(historyPage + 1)"
      >
        {{ $t('admin.i18n.next') }}
      </button>
    </div>

    <!-- Rollback Confirmation Modal -->
    <div v-if="showRollbackConfirm" class="modal-overlay" @click="closeRollbackConfirm">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('admin.i18n.confirm_rollback') }}</h3>
        </div>

        <div class="modal-content">
          <p class="warning-text">
            ⚠️ {{ $t('admin.i18n.rollback_warning') }}
          </p>

          <div class="sync-info">
            <div class="info-row">
              <span class="label">{{ $t('admin.i18n.sync_id') }}:</span>
              <code>{{ selectedSyncForRollback?.sync_id }}</code>
            </div>
            <div class="info-row">
              <span class="label">{{ $t('admin.i18n.mode') }}:</span>
              <span>{{ selectedSyncForRollback?.sync_mode }}</span>
            </div>
            <div class="info-row">
              <span class="label">{{ $t('admin.i18n.total_changes') }}:</span>
              <span>{{ selectedSyncForRollback?.total_changes }}</span>
            </div>
          </div>

          <div class="reason-input">
            <label for="rollback-reason">{{ $t('admin.i18n.rollback_reason') }}</label>
            <textarea
              id="rollback-reason"
              v-model="rollbackReason"
              :placeholder="$t('admin.i18n.rollback_reason_placeholder')"
              rows="4"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeRollbackConfirm">
            {{ $t('admin.i18n.cancel') }}
          </button>
          <button class="btn btn-danger" @click="confirmRollback">
            {{ $t('admin.i18n.confirm_rollback') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history-panel {
  padding: 0;
}

.panel-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: white;
}

.panel-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.panel-header .subtitle {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}

.filters-section {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 20px 24px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
  min-width: 100px;
}

.filter-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-button {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s;
}

.filter-button:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.filter-button.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 20px;
  color: #6b7280;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.history-table {
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.table-header {
  display: grid;
  grid-template-columns: 150px 100px 120px 100px 100px 150px 120px;
  gap: 16px;
  padding: 16px 24px;
  background: #f9fafb;
  border-bottom: 2px solid #e5e7eb;
  font-weight: 600;
  font-size: 13px;
  color: #374151;
}

.table-row {
  display: grid;
  grid-template-columns: 150px 100px 120px 100px 100px 150px 120px;
  gap: 16px;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  align-items: center;
  font-size: 13px;
}

.table-row:hover {
  background: #f9fafb;
}

.sync-id {
  font-family: monospace;
  font-size: 11px;
  color: #6b7280;
  word-break: break-all;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.badge-mode {
  background: #dbeafe;
  color: #1e40af;
}

.badge-mode.mode-auto {
  background: #dcfce7;
  color: #15803d;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-failed {
  background: #fee2e2;
  color: #7f1d1d;
}

.status-rolled_back {
  background: #e0e7ff;
  color: #3730a3;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.changes-count {
  font-weight: 600;
  color: #1f2937;
}

.conflicts-badge {
  padding: 2px 6px;
  border-radius: 3px;
  background: #fee2e2;
  color: #7f1d1d;
  font-weight: 600;
}

.conflicts-none {
  color: #9ca3af;
}

.timestamp {
  color: #6b7280;
  font-size: 12px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  font-size: 12px;
  transition: all 0.3s;
}

.btn-rollback {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fcd34d;
}

.btn-rollback:hover {
  background: #fde68a;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.no-action {
  color: #9ca3af;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #9ca3af;
  font-size: 16px;
  background: white;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px 24px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 13px;
  color: #6b7280;
  min-width: 150px;
  text-align: center;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.modal-content {
  padding: 24px;
}

.warning-text {
  margin: 0 0 16px;
  padding: 12px;
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  border-radius: 4px;
  color: #92400e;
  font-size: 14px;
  line-height: 1.5;
}

.sync-info {
  margin-bottom: 20px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 4px;
}

.info-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 13px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  font-weight: 600;
  color: #374151;
  min-width: 100px;
}

.reason-input {
  margin-bottom: 20px;
}

.reason-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 13px;
  color: #374151;
}

.reason-input textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-family: inherit;
  font-size: 13px;
  resize: vertical;
}

.reason-input textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}
</style>
