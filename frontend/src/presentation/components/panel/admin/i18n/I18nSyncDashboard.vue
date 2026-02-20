<script setup lang="ts">
/**
 * I18nSyncDashboard
 *
 * Main page for i18n synchronization system.
 * Delegates header, stats grid, scan, comparison, and history to sub-components.
 */

import { ref, onMounted } from 'vue'
import SyncDashboardHeader from './panels/SyncDashboardHeader.vue'
import SyncStatsGrid from './panels/SyncStatsGrid.vue'
import ScanPanel from './panels/ScanPanel.vue'
import ComparisonPanel from './panels/ComparisonPanel.vue'
import HistoryPanel from './panels/HistoryPanel.vue'
import { useSyncManager } from '@/application/composables/panel/admin/i18n/useSyncManager'
import type { SyncMode } from './types/sync.types'

const {
  selectedMode,
  selectedLanguages,
  currentSyncId,
  currentStatus,
  isScanning,
  error,
  scanResults,
  dashboardStats,
  isLoadingDashboard,
  startScan,
  loadDashboard,
  reset
} = useSyncManager()

const activeTab = ref<'dashboard' | 'scan' | 'comparison' | 'history'>('dashboard')
const availableLanguages = ['de', 'en', 'pl']

onMounted(async () => {
  await loadDashboard()
})

async function handleStartScan(): Promise<void> {
  try {
    await startScan()
    activeTab.value = 'scan'
  } catch (err) {
    console.error('Failed to start scan:', err)
  }
}

function handleModeChange(mode: SyncMode): void {
  selectedMode.value = mode
  reset()
}

function toggleLanguage(lang: string): void {
  const index = selectedLanguages.value.indexOf(lang)
  if (index > -1) {
    selectedLanguages.value.splice(index, 1)
  } else {
    selectedLanguages.value.push(lang)
  }
}
</script>

<template>
  <div class="i18n-sync-dashboard">
    <!-- Header with mode + language selectors -->
    <SyncDashboardHeader
      :selected-mode="selectedMode"
      :selected-languages="selectedLanguages"
      :available-languages="availableLanguages"
      @mode-change="handleModeChange"
      @toggle-language="toggleLanguage"
    />

    <!-- Scan Status -->
    <div v-if="currentSyncId" class="sync-status">
      <div class="status-content">
        <span class="status-label">{{ $t('panel.i18n.sync_id') }}:</span>
        <code class="status-value">{{ currentSyncId }}</code>
        <span class="status-badge" :class="currentStatus.toLowerCase()">
          {{ $t(`panel.i18n.status_${currentStatus.toLowerCase()}`) }}
        </span>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-error">
      <span class="alert-icon">&#9888;&#65039;</span>
      <span class="alert-message">{{ error }}</span>
    </div>

    <!-- Main Content -->
    <div class="dashboard-content">
      <!-- Tabs -->
      <div class="tabs">
        <button
          class="tab-button"
          :class="{ active: activeTab === 'dashboard' }"
          @click="activeTab = 'dashboard'"
        >
          &#128202; {{ $t('panel.i18n.tab_dashboard') }}
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'scan' }"
          :disabled="!currentSyncId"
          @click="activeTab = 'scan'"
        >
          &#128269; {{ $t('panel.i18n.tab_scan') }}
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'comparison' }"
          :disabled="!currentSyncId"
          @click="activeTab = 'comparison'"
        >
          &#128203; {{ $t('panel.i18n.tab_comparison') }}
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'history' }"
          @click="activeTab = 'history'"
        >
          &#128220; {{ $t('panel.i18n.tab_history') }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <div v-if="activeTab === 'dashboard'" class="tab-pane active">
          <div v-if="isLoadingDashboard" class="loading">
            <span class="spinner"></span>
            {{ $t('common.loading') }}
          </div>
          <SyncStatsGrid
            v-else-if="dashboardStats"
            :stats="dashboardStats"
            :is-scanning="isScanning"
            :has-languages-selected="selectedLanguages.length > 0"
            @start-scan="handleStartScan"
          />
        </div>

        <div v-if="activeTab === 'scan'" class="tab-pane active">
          <ScanPanel
            v-if="scanResults"
            :results="scanResults"
            :sync-id="currentSyncId!"
          />
          <div v-else class="empty-state">
            {{ $t('panel.i18n.no_scan_results') }}
          </div>
        </div>

        <div v-if="activeTab === 'comparison'" class="tab-pane active">
          <ComparisonPanel v-if="currentSyncId" :sync-id="currentSyncId" />
          <div v-else class="empty-state">
            {{ $t('panel.i18n.no_sync_active') }}
          </div>
        </div>

        <div v-if="activeTab === 'history'" class="tab-pane active">
          <HistoryPanel />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.i18n-sync-dashboard {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}

.sync-status {
  background: #f3f4f6;
  border-left: 4px solid #3b82f6;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 14px;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-label {
  font-weight: 600;
  color: #374151;
}

.status-value {
  font-family: monospace;
  background: white;
  padding: 2px 6px;
  border-radius: 3px;
  color: #6b7280;
  font-size: 12px;
}

.status-badge {
  margin-left: auto;
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
}

.status-badge.pending { background: #fef3c7; color: #92400e; }
.status-badge.completed { background: #d1fae5; color: #065f46; }
.status-badge.failed { background: #fee2e2; color: #7f1d1d; }
.status-badge.rolled_back { background: #e0e7ff; color: #3730a3; }

.alert {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.alert-error {
  background: #fee2e2;
  color: #7f1d1d;
  border-left: 4px solid #dc2626;
}

.alert-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.dashboard-content {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.tab-button {
  flex: 1;
  padding: 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 500;
  color: #6b7280;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
  white-space: nowrap;
}

.tab-button:hover:not(:disabled) { background: white; color: #374151; }
.tab-button.active { color: #3b82f6; border-bottom-color: #3b82f6; background: white; }
.tab-button:disabled { opacity: 0.5; cursor: not-allowed; }

.tab-content { position: relative; }

.tab-pane {
  display: none;
  padding: 24px;
  animation: fadeIn 0.3s;
}

.tab-pane.active { display: block; }

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 20px;
  color: #6b7280;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #9ca3af;
  font-size: 16px;
}
</style>
