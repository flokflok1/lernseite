<script setup lang="ts">
/**
 * SyncStatsGrid
 *
 * Renders the dashboard statistics cards and the start-scan action button.
 * Extracted from I18nSyncDashboard to keep the parent under 500 LOC.
 */

import type { DashboardResponse } from '../types/sync.types'

interface Props {
  stats: DashboardResponse
  isScanning: boolean
  hasLanguagesSelected: boolean
}

interface Emits {
  (e: 'start-scan'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<template>
  <div class="dashboard-grid">
    <!-- Total Syncs -->
    <div class="stat-card">
      <div class="stat-value">{{ stats.total_syncs }}</div>
      <div class="stat-label">{{ $t('panel.i18n.total_syncs') }}</div>
    </div>

    <!-- Successful Syncs -->
    <div class="stat-card success">
      <div class="stat-value">{{ stats.successful_syncs }}</div>
      <div class="stat-label">{{ $t('panel.i18n.successful_syncs') }}</div>
    </div>

    <!-- Failed Syncs -->
    <div class="stat-card error">
      <div class="stat-value">{{ stats.failed_syncs }}</div>
      <div class="stat-label">{{ $t('panel.i18n.failed_syncs') }}</div>
    </div>

    <!-- Pending Resolutions -->
    <div class="stat-card warning">
      <div class="stat-value">{{ stats.pending_resolutions }}</div>
      <div class="stat-label">{{ $t('panel.i18n.pending_resolutions') }}</div>
    </div>

    <!-- Start Scan Button -->
    <div class="stat-card action">
      <button
        class="btn btn-primary"
        :disabled="isScanning || !hasLanguagesSelected"
        @click="$emit('start-scan')"
      >
        <span v-if="isScanning" class="spinner-small"></span>
        {{ $t('panel.i18n.start_scan') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-card.success {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  color: #065f46;
}

.stat-card.error {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: #7f1d1d;
}

.stat-card.warning {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #92400e;
}

.stat-card.action {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 2px dashed #d1d5db;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 500;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner-small {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
