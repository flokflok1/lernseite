<script setup lang="ts">
/**
 * I18nSyncDashboard
 *
 * Main page for i18n synchronization system
 * - Mode selection (MANUAL vs AUTO)
 * - Scan initiation
 * - Tabs for: Scan Results, Comparison Panel, History, Statistics
 */

import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import ScanPanel from './panels/ScanPanel.vue'
import ComparisonPanel from './panels/ComparisonPanel.vue'
import HistoryPanel from './panels/HistoryPanel.vue'
import { useSyncManager } from '@/features/panel/useSyncManager'
import type { SyncMode } from './types/sync.types'

const { t } = useI18n()
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

// UI State
const activeTab = ref<'dashboard' | 'scan' | 'comparison' | 'history'>('dashboard')
const showModeSelector = ref(false)

// Language selection
const availableLanguages = ['de', 'en', 'pl']

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(async () => {
  await loadDashboard()
})

// ============================================================================
// METHODS
// ============================================================================

async function handleStartScan() {
  try {
    await startScan()
    activeTab.value = 'scan'
  } catch (err) {
    console.error('Failed to start scan:', err)
  }
}

function handleModeChange(mode: SyncMode) {
  selectedMode.value = mode
  showModeSelector.value = false
  reset()
}

function toggleLanguage(lang: string) {
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
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-title">
          <h1>{{ $t('panel.i18n.title') }}</h1>
          <p class="subtitle">{{ $t('panel.i18n.subtitle') }}</p>
        </div>

        <!-- Mode Selector -->
        <div class="mode-selector">
          <button
            class="mode-button"
            :class="{ active: selectedMode === 'MANUAL' }"
            @click="handleModeChange('MANUAL')"
          >
            <span class="mode-icon">🎯</span>
            <span class="mode-label">{{ $t('panel.i18n.mode_manual') }}</span>
            <span class="mode-desc">{{ $t('panel.i18n.mode_manual_desc') }}</span>
          </button>

          <button
            class="mode-button"
            :class="{ active: selectedMode === 'AUTO' }"
            @click="handleModeChange('AUTO')"
          >
            <span class="mode-icon">⚙️</span>
            <span class="mode-label">{{ $t('panel.i18n.mode_auto') }}</span>
            <span class="mode-desc">{{ $t('panel.i18n.mode_auto_desc') }}</span>
          </button>
        </div>
      </div>

      <!-- Language Selection -->
      <div class="language-selector">
        <label class="label">{{ $t('panel.i18n.languages') }}</label>
        <div class="language-options">
          <button
            v-for="lang in availableLanguages"
            :key="lang"
            class="language-button"
            :class="{ active: selectedLanguages.includes(lang) }"
            @click="toggleLanguage(lang)"
          >
            {{ lang.toUpperCase() }}
          </button>
        </div>
      </div>
    </div>

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
      <span class="alert-icon">⚠️</span>
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
          📊 {{ $t('panel.i18n.tab_dashboard') }}
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'scan' }"
          :disabled="!currentSyncId"
          @click="activeTab = 'scan'"
        >
          🔍 {{ $t('panel.i18n.tab_scan') }}
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'comparison' }"
          :disabled="!currentSyncId"
          @click="activeTab = 'comparison'"
        >
          📋 {{ $t('panel.i18n.tab_comparison') }}
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'history' }"
          @click="activeTab = 'history'"
        >
          📜 {{ $t('panel.i18n.tab_history') }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Dashboard Tab -->
        <div v-if="activeTab === 'dashboard'" class="tab-pane active">
          <div v-if="isLoadingDashboard" class="loading">
            <span class="spinner"></span>
            {{ $t('common.loading') }}
          </div>

          <div v-else-if="dashboardStats" class="dashboard-grid">
            <!-- Total Syncs -->
            <div class="stat-card">
              <div class="stat-value">{{ dashboardStats.total_syncs }}</div>
              <div class="stat-label">{{ $t('panel.i18n.total_syncs') }}</div>
            </div>

            <!-- Successful Syncs -->
            <div class="stat-card success">
              <div class="stat-value">{{ dashboardStats.successful_syncs }}</div>
              <div class="stat-label">{{ $t('panel.i18n.successful_syncs') }}</div>
            </div>

            <!-- Failed Syncs -->
            <div class="stat-card error">
              <div class="stat-value">{{ dashboardStats.failed_syncs }}</div>
              <div class="stat-label">{{ $t('panel.i18n.failed_syncs') }}</div>
            </div>

            <!-- Pending Resolutions -->
            <div class="stat-card warning">
              <div class="stat-value">{{ dashboardStats.pending_resolutions }}</div>
              <div class="stat-label">{{ $t('panel.i18n.pending_resolutions') }}</div>
            </div>

            <!-- Start Scan Button -->
            <div class="stat-card action">
              <button
                class="btn btn-primary"
                :disabled="isScanning || selectedLanguages.length === 0"
                @click="handleStartScan"
              >
                <span v-if="isScanning" class="spinner-small"></span>
                {{ $t('panel.i18n.start_scan') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Scan Results Tab -->
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

        <!-- Comparison Panel Tab -->
        <div v-if="activeTab === 'comparison'" class="tab-pane active">
          <ComparisonPanel v-if="currentSyncId" :sync-id="currentSyncId" />
          <div v-else class="empty-state">
            {{ $t('panel.i18n.no_sync_active') }}
          </div>
        </div>

        <!-- History Tab -->
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

.dashboard-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-title h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

.header-title .subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: #6b7280;
}

.mode-selector {
  display: flex;
  gap: 12px;
}

.mode-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.mode-button:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.mode-button.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.mode-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.mode-label {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.mode-desc {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.language-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.label {
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.language-options {
  display: flex;
  gap: 8px;
}

.language-button {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-weight: 500;
  font-size: 12px;
  transition: all 0.3s;
}

.language-button:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.language-button.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
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

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.failed {
  background: #fee2e2;
  color: #7f1d1d;
}

.status-badge.rolled_back {
  background: #e0e7ff;
  color: #3730a3;
}

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

.tab-button:hover:not(:disabled) {
  background: white;
  color: #374151;
}

.tab-button.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
  background: white;
}

.tab-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tab-content {
  position: relative;
}

.tab-pane {
  display: none;
  padding: 24px;
  animation: fadeIn 0.3s;
}

.tab-pane.active {
  display: block;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

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

.spinner,
.spinner-small {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.6s linear infinite;
}

.spinner-small {
  width: 12px;
  height: 12px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

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
