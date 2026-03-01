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
import { useSyncManager } from '@/application/composables/panel/admin/i18n/useSyncManager'
import HistoryTableRow from './HistoryTableRow.vue'
import RollbackConfirmModal from './RollbackConfirmModal.vue'

const { t } = useI18n()
const {
  historyPage,
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

const statusOptions = computed(() => [
  { value: 'COMPLETED', label: t('panel.i18n.status_completed') },
  { value: 'FAILED', label: t('panel.i18n.status_failed') },
  { value: 'ROLLED_BACK', label: t('panel.i18n.status_rolled_back') }
])

const modeOptions = computed(() => [
  { value: 'MANUAL', label: t('panel.i18n.mode_manual') },
  { value: 'AUTO', label: t('panel.i18n.mode_auto') }
])

// ============================================================================
// METHODS
// ============================================================================

async function applyStatusFilter(status: string | null): Promise<void> {
  statusFilter.value = status
  historyPage.value = 0
  await loadHistory(status || undefined, modeFilter.value || undefined)
}

async function applyModeFilter(mode: string | null): Promise<void> {
  modeFilter.value = mode
  historyPage.value = 0
  await loadHistory(statusFilter.value || undefined, mode || undefined)
}

async function changePage(newPage: number): Promise<void> {
  if (newPage >= 0 && newPage < historyTotalPages.value) {
    historyPage.value = newPage
    await loadHistory(statusFilter.value || undefined, modeFilter.value || undefined)
  }
}

function openRollbackConfirm(sync: SyncHistorySummary): void {
  selectedSyncForRollback.value = sync
  rollbackReason.value = ''
  showRollbackConfirm.value = true
}

function closeRollbackConfirm(): void {
  showRollbackConfirm.value = false
  selectedSyncForRollback.value = null
  rollbackReason.value = ''
}

async function confirmRollback(): Promise<void> {
  if (!selectedSyncForRollback.value) return

  try {
    await rollbackSync(rollbackReason.value)
    closeRollbackConfirm()
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
      <h2>{{ $t('panel.i18n.history_title') }}</h2>
      <p class="subtitle">{{ $t('panel.i18n.history_subtitle') }}</p>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label class="filter-label">{{ $t('panel.i18n.filter_status') }}</label>
        <div class="filter-buttons">
          <button
            class="filter-button"
            :class="{ active: statusFilter === null }"
            @click="applyStatusFilter(null)"
          >
            {{ $t('panel.i18n.all') }}
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
        <label class="filter-label">{{ $t('panel.i18n.filter_mode') }}</label>
        <div class="filter-buttons">
          <button
            class="filter-button"
            :class="{ active: modeFilter === null }"
            @click="applyModeFilter(null)"
          >
            {{ $t('panel.i18n.all') }}
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
        <div class="col-syncid">{{ $t('panel.i18n.sync_id') }}</div>
        <div class="col-mode">{{ $t('panel.i18n.mode') }}</div>
        <div class="col-status">{{ $t('panel.i18n.status') }}</div>
        <div class="col-changes">{{ $t('panel.i18n.total_changes') }}</div>
        <div class="col-conflicts">{{ $t('panel.i18n.conflicts') }}</div>
        <div class="col-timestamp">{{ $t('panel.i18n.created_at') }}</div>
        <div class="col-actions">{{ $t('panel.i18n.actions') }}</div>
      </div>

      <HistoryTableRow
        v-for="sync in paginatedHistory"
        :key="sync.sync_id"
        :sync="sync"
        @rollback="openRollbackConfirm"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>{{ $t('panel.i18n.no_history') }}</p>
    </div>

    <!-- Pagination -->
    <div v-if="historyTotalPages > 1" class="pagination">
      <button
        class="pagination-btn"
        :disabled="historyPage === 0"
        @click="changePage(historyPage - 1)"
      >
        {{ $t('panel.i18n.previous') }}
      </button>

      <div class="pagination-info">
        {{ $t('panel.i18n.page_info', {
          current: historyPage + 1,
          total: historyTotalPages
        }) }}
      </div>

      <button
        class="pagination-btn"
        :disabled="historyPage >= historyTotalPages - 1"
        @click="changePage(historyPage + 1)"
      >
        {{ $t('panel.i18n.next') }}
      </button>
    </div>

    <!-- Rollback Confirmation Modal -->
    <RollbackConfirmModal
      v-if="showRollbackConfirm && selectedSyncForRollback"
      :sync="selectedSyncForRollback"
      v-model:reason="rollbackReason"
      @confirm="confirmRollback"
      @cancel="closeRollbackConfirm"
    />
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
</style>
