<script setup lang="ts">
/**
 * HistoryTableRow Component
 *
 * Renders a single row in the sync history table with status badges,
 * change counts, conflict indicators, and rollback action button.
 */

import { useI18n } from 'vue-i18n'
import type { SyncHistorySummary } from '../types/sync.types'

interface Props {
  sync: SyncHistorySummary
}

defineProps<Props>()

const emit = defineEmits<{
  rollback: [sync: SyncHistorySummary]
}>()

const { t } = useI18n()

function getStatusClass(status: string): string {
  const statusMap: Record<string, string> = {
    'COMPLETED': 'status-completed',
    'FAILED': 'status-failed',
    'ROLLED_BACK': 'status-rolled_back'
  }
  return statusMap[status] || 'status-pending'
}

function getStatusIcon(status: string): string {
  const iconMap: Record<string, string> = {
    'COMPLETED': 'V',
    'FAILED': 'X',
    'ROLLED_BACK': '<',
    'PENDING': '...'
  }
  return iconMap[status] || '?'
}

function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return t('panel.i18n.not_applicable')
  const date = new Date(dateStr)
  return date.toLocaleString()
}

function canRollback(sync: SyncHistorySummary): boolean {
  return sync.sync_status === 'COMPLETED' && !sync.is_rolled_back
}
</script>

<template>
  <div class="table-row">
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
        {{ getStatusIcon(sync.sync_status) }} {{ $t(`panel.i18n.status_${sync.sync_status.toLowerCase()}`) }}
      </span>
    </div>

    <div class="col-changes">
      <span class="changes-count">{{ sync.total_changes }}</span>
    </div>

    <div class="col-conflicts">
      <span v-if="sync.conflicts_count > 0" class="conflicts-badge">
        {{ sync.conflicts_count }}
      </span>
      <span v-else class="conflicts-none">&mdash;</span>
    </div>

    <div class="col-timestamp">
      <span class="timestamp">{{ formatDateTime(sync.created_at) }}</span>
    </div>

    <div class="col-actions">
      <button
        v-if="canRollback(sync)"
        class="btn btn-rollback"
        :title="$t('panel.i18n.rollback_tooltip')"
        @click="emit('rollback', sync)"
      >
        {{ $t('panel.i18n.rollback') }}
      </button>
      <span v-else class="no-action">&mdash;</span>
    </div>
  </div>
</template>

<style scoped>
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

.no-action {
  color: #9ca3af;
}
</style>
