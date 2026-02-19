<!--
  GlobalSettingsTab.vue

  KI-Studio Pro - Globale Einstellungen
  Alles in einem Tab: Provider, Profile, Modelle

  Features:
  - Provider & API-Keys (kompakt mit Modals)
  - Globale Profile CRUD
  - Kategorien dynamisch aus DB (alle 9+)
  - Sync & Test Funktionen

  Phase: KI-Studio Pro - Globale Einstellungen
  Refactored: Sub-components in ./global-settings/
  Business logic extracted to composables/useGlobalSettings.ts
-->

<template>
  <div class="global-settings-tab">
    <!-- Header mit Stats -->
    <div class="header-bar">
      <div class="header-left">
        <h2 class="header-title">{{ $t('aiEditorGlobalSettings.title') }}</h2>
        <div class="header-stats">
          <span class="stat-item">{{ stats.total_models || 0 }} {{ $t('aiEditorGlobalSettings.models') }}</span>
          <span class="stat-divider">|</span>
          <span class="stat-item">{{ stats.providers || 0 }} {{ $t('aiEditorGlobalSettings.providers') }}</span>
          <span class="stat-divider">|</span>
          <span class="stat-item">{{ categories.length }} {{ $t('aiEditorGlobalSettings.categories') }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button @click="openPricingWindow" class="btn-action pricing">
          {{ $t('aiPricing.title') }}
        </button>
        <button @click="syncAllModels" :disabled="isSyncing" class="btn-action">
          <span :class="{ 'animate-spin': isSyncing }">🔄</span>
          {{ isSyncing ? $t('aiEditorGlobalSettings.syncing') : $t('aiEditorGlobalSettings.syncAll') }}
        </button>
        <button @click="testAllConnections" :disabled="isTesting" class="btn-action secondary">
          <span :class="{ 'animate-spin': isTesting }">🔌</span>
          {{ isTesting ? $t('aiEditorGlobalSettings.testing') : $t('aiEditorGlobalSettings.testAll') }}
        </button>
      </div>
    </div>

    <!-- Sync/Test Ergebnis -->
    <div v-if="actionResult" class="action-result" :class="actionResult.success ? 'success' : 'error'">
      {{ actionResult.message }}
      <button @click="actionResult = null" class="close-btn">&times;</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ $t('aiEditorGlobalSettings.loading') }}</p>
    </div>

    <div v-else class="main-content">
      <!-- Provider Sektion (kompakt) -->
      <ProviderGrid
        :providers="providers"
        :model-counts="modelCountsByProvider"
        :testing-provider="testingProvider"
        :is-syncing="isSyncing"
        @open-api-key="openApiKeyModal"
        @test-provider="testProvider"
        @sync-provider="syncProvider"
      />

      <!-- Profile Sektion -->
      <div class="section profile-section">
        <div class="section-header">
          <h3 class="section-title">{{ $t('aiEditorGlobalSettings.aiProfiles') }}</h3>
          <button @click="createNewProfile" class="btn-add">{{ $t('aiEditorGlobalSettings.newProfile') }}</button>
        </div>
        <div class="profile-layout">
          <ProfileList
            :profiles="profiles"
            :selected-key="selectedProfileKey"
            @select="selectProfile"
          />
          <ProfileEditor
            :profile="selectedProfile"
            :is-creating="isCreating"
            :form-data="formData"
            :categories="categories"
            :models="models"
            :saving="saving"
            @update:form-data="updateFormData"
            @save="saveProfile"
            @cancel="cancelEdit"
            @delete="deleteProfile"
            @set-default="setAsDefault"
          />
        </div>
      </div>
    </div>

    <!-- API-Key Modal -->
    <ApiKeyModal
      :provider="apiKeyModal"
      :api-key="apiKeyInput"
      :show-key="showApiKey"
      :testing="testingApiKey"
      :saving="savingApiKey"
      :result="apiKeyResult"
      @close="apiKeyModal = null"
      @update:api-key="apiKeyInput = $event"
      @toggle-show="showApiKey = !showApiKey"
      @test="testApiKey"
      @save="saveApiKey"
    />

    <!-- Status Toast -->
    <div v-if="toast" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { ProviderGrid, ProfileList, ProfileEditor, ApiKeyModal } from '@/presentation/components/panel/admin/ai/settings/global-settings'
import { useGlobalSettings } from '../composables/useGlobalSettings'

const {
  loading,
  saving,
  isSyncing,
  isTesting,
  testingProvider,
  providers,
  profiles,
  models,
  categories,
  stats,
  selectedProfileKey,
  isCreating,
  formData,
  apiKeyModal,
  apiKeyInput,
  showApiKey,
  testingApiKey,
  savingApiKey,
  apiKeyResult,
  actionResult,
  toast,
  selectedProfile,
  modelCountsByProvider,
  loadData,
  selectProfile,
  createNewProfile,
  updateFormData,
  cancelEdit,
  saveProfile,
  deleteProfile,
  setAsDefault,
  openApiKeyModal,
  saveApiKey,
  testApiKey,
  testProvider,
  syncProvider,
  syncAllModels,
  testAllConnections,
  openPricingWindow
} = useGlobalSettings()

onMounted(() => loadData())
</script>

<style scoped>
.global-settings-tab { height: 100%; display: flex; flex-direction: column; overflow: hidden; }

/* Header */
.header-bar { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1rem; background: var(--color-surface); border-bottom: 1px solid var(--color-border); }
.header-left { display: flex; align-items: center; gap: 1.5rem; }
.header-title { font-size: 1rem; font-weight: 600; color: var(--color-text-primary); margin: 0; }
.header-stats { display: flex; align-items: center; gap: 0.375rem; font-size: 0.75rem; color: var(--color-text-secondary); }
.stat-divider { color: var(--color-border); }
.header-actions { display: flex; gap: 0.5rem; }

.btn-action { display: flex; align-items: center; gap: 0.25rem; padding: 0.375rem 0.625rem; background: var(--color-primary); color: white; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 500; transition: opacity 0.15s; }
.btn-action:hover:not(:disabled) { opacity: 0.9; }
.btn-action:disabled { opacity: 0.5; }
.btn-action.secondary { background: var(--color-surface-secondary); color: var(--color-text-primary); border: 1px solid var(--color-border); }
.btn-action.pricing { background: linear-gradient(135deg, #f59e0b, #d97706); border: none; }

/* Action Result */
.action-result { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1.5rem; font-size: 0.875rem; }
.action-result.success { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
.action-result.error { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.close-btn { font-size: 1.25rem; line-height: 1; opacity: 0.7; }
.close-btn:hover { opacity: 1; }

/* Loading */
.loading-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem; }
.spinner { width: 2rem; height: 2rem; border: 3px solid var(--color-border); border-top-color: var(--color-primary); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Main Content */
.main-content { flex: 1; overflow-y: auto; padding: 1rem; display: flex; flex-direction: column; gap: 1rem; }

/* Sections */
.section { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 0.75rem; overflow: hidden; }
.section-header { display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0.75rem; background: var(--color-surface-secondary); border-bottom: 1px solid var(--color-border); }
.section-title { font-size: 0.8125rem; font-weight: 600; color: var(--color-text-primary); margin: 0; }
.btn-add { padding: 0.375rem 0.75rem; background: var(--color-primary); color: white; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 500; }

/* Profile Layout */
.profile-layout { display: grid; grid-template-columns: 180px 1fr; max-height: 320px; }

/* Toast */
.toast { position: fixed; bottom: 2rem; right: 2rem; padding: 0.75rem 1.25rem; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 500; z-index: 1001; animation: slideIn 0.2s ease; }
.toast.success { background: #22c55e; color: white; }
.toast.error { background: #ef4444; color: white; }
@keyframes slideIn { from { opacity: 0; transform: translateY(1rem); } to { opacity: 1; transform: translateY(0); } }

/* Animate spin */
.animate-spin { animation: spin 1s linear infinite; display: inline-block; }
</style>
