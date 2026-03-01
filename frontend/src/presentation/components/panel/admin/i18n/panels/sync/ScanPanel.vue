<script setup lang="ts">
/**
 * ScanPanel Component
 *
 * Displays scan results with statistics and category breakdown
 * Shows summary of detected changes:
 * - New keys (in frontend JSON, not in database)
 * - Changed keys (value differences)
 * - Deleted keys (in database, not in frontend JSON)
 * - Conflicted keys (manual resolution needed)
 */

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ScanResultsResponse } from '../types/sync.types'

interface Props {
  results: ScanResultsResponse
  syncId: string
}

defineProps<Props>()

const { t } = useI18n()

// ============================================================================
// COMPUTED
// ============================================================================

// Stats grid data
const statsData = computed(() => {
  const summary = results?.summary
  if (!summary) return []

  return [
    {
      icon: '➕',
      label: t('panel.i18n.new_keys'),
      value: summary.new_keys,
      color: 'new'
    },
    {
      icon: '✏️',
      label: t('panel.i18n.changed_keys'),
      value: summary.changed_keys,
      color: 'changed'
    },
    {
      icon: '🗑️',
      label: t('panel.i18n.deleted_keys'),
      value: summary.deleted_keys,
      color: 'deleted'
    },
    {
      icon: '⚠️',
      label: t('panel.i18n.conflicted_keys'),
      value: summary.conflicted_keys,
      color: 'conflict'
    }
  ]
})

// Total changes
const totalChanges = computed(() => {
  const s = results?.summary
  if (!s) return 0
  return s.new_keys + s.changed_keys + s.deleted_keys
})

// Percentage of completion
const completionPercentage = computed(() => {
  const total = results?.summary?.total_keys
  const processed =
    results?.summary &&
    results.summary.new_keys +
      results.summary.changed_keys +
      results.summary.deleted_keys +
      results.summary.conflicted_keys
  if (!total || !processed) return 0
  return Math.round((processed / total) * 100)
})

// Languages affected as badge list
const languagesList = computed(() => {
  return results?.summary?.languages_affected || []
})
</script>

<template>
  <div class="scan-panel">
    <!-- Header -->
    <div class="panel-header">
      <h2>{{ $t('panel.i18n.scan_results') }}</h2>
      <span class="sync-id">{{ syncId }}</span>
    </div>

    <!-- Scan Status -->
    <div v-if="results?.summary" class="scan-status">
      <div class="status-row">
        <span class="status-label">{{ $t('panel.i18n.scan_status') }}:</span>
        <span
          class="status-badge"
          :class="results.summary.scan_status.toLowerCase()"
        >
          {{ results.summary.scan_status }}
        </span>
      </div>

      <div class="status-row">
        <span class="status-label">{{ $t('panel.i18n.scan_duration') }}:</span>
        <span class="status-value">{{ results.summary.scan_duration_ms }}ms</span>
      </div>

      <div class="status-row">
        <span class="status-label">{{ $t('panel.i18n.languages_affected') }}:</span>
        <div class="language-badges">
          <span
            v-for="lang in languagesList"
            :key="lang"
            class="badge badge-language"
          >
            {{ lang.toUpperCase() }}
          </span>
        </div>
      </div>
    </div>

    <!-- Statistics Grid -->
    <div v-if="results?.summary" class="stats-grid">
      <div
        v-for="stat in statsData"
        :key="stat.label"
        class="stat-item"
        :class="`stat-${stat.color}`"
      >
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-info">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-name">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- Progress Bar -->
    <div v-if="results?.summary" class="progress-section">
      <div class="progress-header">
        <span class="progress-label">{{ $t('panel.i18n.keys_processed') }}</span>
        <span class="progress-percentage">{{ completionPercentage }}%</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: completionPercentage + '%' }"></div>
      </div>
      <div class="progress-details">
        <span class="detail">
          {{ $t('panel.i18n.total_keys') }}: {{ results.summary.total_keys }}
        </span>
        <span class="detail">
          {{ $t('panel.i18n.total_changes') }}: {{ totalChanges }}
        </span>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="results?.summary" class="summary-section">
      <h3>{{ $t('panel.i18n.summary') }}</h3>
      <div class="summary-content">
        <p v-if="results.summary.new_keys > 0">
          <strong>{{ results.summary.new_keys }}</strong>
          {{ $t('panel.i18n.new_keys_summary', results.summary.new_keys) }}
        </p>
        <p v-if="results.summary.changed_keys > 0">
          <strong>{{ results.summary.changed_keys }}</strong>
          {{ $t('panel.i18n.changed_keys_summary', results.summary.changed_keys) }}
        </p>
        <p v-if="results.summary.deleted_keys > 0">
          <strong>{{ results.summary.deleted_keys }}</strong>
          {{ $t('panel.i18n.deleted_keys_summary', results.summary.deleted_keys) }}
        </p>
        <p v-if="results.summary.conflicted_keys > 0" class="warning">
          <strong>{{ results.summary.conflicted_keys }}</strong>
          {{ $t('panel.i18n.conflicted_keys_summary', results.summary.conflicted_keys) }}
        </p>
      </div>
    </div>

    <!-- Next Steps -->
    <div v-if="results?.next_action" class="next-steps">
      <h3>{{ $t('panel.i18n.next_steps') }}</h3>
      <div class="steps-content">
        <p v-if="results.next_action === 'REVIEW'">
          {{ $t('panel.i18n.next_review_desc') }}
        </p>
        <p v-else-if="results.next_action === 'APPLY_AUTO'">
          {{ $t('panel.i18n.next_apply_auto_desc') }}
        </p>
        <p v-else-if="results.next_action === 'APPLY_MANUAL'">
          {{ $t('panel.i18n.next_apply_manual_desc') }}
        </p>
      </div>
    </div>

    <!-- Error -->
    <div v-if="results?.summary?.error_message" class="error-section">
      <div class="error-box">
        <span class="error-icon">❌</span>
        <div class="error-content">
          <div class="error-title">{{ $t('panel.i18n.scan_error') }}</div>
          <div class="error-message">{{ results.summary.error_message }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scan-panel {
  padding: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.sync-id {
  font-family: monospace;
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
}

.scan-status {
  padding: 20px 24px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 14px;
}

.status-row:last-child {
  margin-bottom: 0;
}

.status-label {
  font-weight: 600;
  color: #374151;
  min-width: 140px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.failed {
  background: #fee2e2;
  color: #7f1d1d;
}

.status-value {
  color: #6b7280;
  font-weight: 500;
}

.language-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.badge-language {
  background: #dbeafe;
  color: #1e40af;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  padding: 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  background: #f9fafb;
}

.stat-new {
  background: #ecfdf5;
  border-left: 4px solid #10b981;
}

.stat-changed {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
}

.stat-deleted {
  background: #fee2e2;
  border-left: 4px solid #ef4444;
}

.stat-conflict {
  background: #fecaca;
  border-left: 4px solid #dc2626;
}

.stat-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.stat-name {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  margin-top: 4px;
}

.progress-section {
  padding: 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-label {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.progress-percentage {
  font-weight: 700;
  color: #3b82f6;
  font-size: 16px;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  transition: width 0.3s ease;
}

.progress-details {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6b7280;
}

.detail {
  display: flex;
  gap: 4px;
}

.summary-section,
.next-steps {
  padding: 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.summary-section h3,
.next-steps h3 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
}

.summary-content p {
  margin: 8px 0;
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
}

.summary-content p strong {
  color: #1f2937;
  font-weight: 700;
}

.summary-content p.warning {
  color: #92400e;
  background: #fef3c7;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #f59e0b;
}

.steps-content {
  padding: 12px;
  background: #eff6ff;
  border-left: 3px solid #3b82f6;
  border-radius: 4px;
}

.steps-content p {
  margin: 0;
  font-size: 14px;
  color: #1e40af;
  line-height: 1.6;
}

.error-section {
  padding: 24px;
}

.error-box {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #fee2e2;
  border-left: 4px solid #dc2626;
  border-radius: 6px;
}

.error-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.error-content {
  flex: 1;
}

.error-title {
  font-weight: 700;
  color: #7f1d1d;
  margin-bottom: 4px;
}

.error-message {
  font-size: 14px;
  color: #7f1d1d;
  line-height: 1.5;
}
</style>
