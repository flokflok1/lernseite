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
-->

<template>
  <div class="global-settings-tab">
    <!-- Header mit Stats -->
    <div class="header-bar">
      <div class="header-left">
        <h2 class="header-title">{{ $t('windows.aiStudioGlobalSettings.title') }}</h2>
        <div class="header-stats">
          <span class="stat-item">{{ stats.total_models || 0 }} {{ $t('windows.aiStudioGlobalSettings.models') }}</span>
          <span class="stat-divider">|</span>
          <span class="stat-item">{{ stats.providers || 0 }} {{ $t('windows.aiStudioGlobalSettings.providers') }}</span>
          <span class="stat-divider">|</span>
          <span class="stat-item">{{ categories.length }} {{ $t('windows.aiStudioGlobalSettings.categories') }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button @click="openPricingWindow" class="btn-action pricing">
          💰 {{ $t('windows.aiPricing.title') }}
        </button>
        <button @click="syncAllModels" :disabled="isSyncing" class="btn-action">
          <span :class="{ 'animate-spin': isSyncing }">🔄</span>
          {{ isSyncing ? $t('windows.aiStudioGlobalSettings.syncing') : $t('windows.aiStudioGlobalSettings.syncAll') }}
        </button>
        <button @click="testAllConnections" :disabled="isTesting" class="btn-action secondary">
          <span :class="{ 'animate-spin': isTesting }">🔌</span>
          {{ isTesting ? $t('windows.aiStudioGlobalSettings.testing') : $t('windows.aiStudioGlobalSettings.testAll') }}
        </button>
      </div>
    </div>

    <!-- Sync/Test Ergebnis -->
    <div v-if="actionResult" class="action-result" :class="actionResult.success ? 'success' : 'error'">
      {{ actionResult.message }}
      <button @click="actionResult = null" class="close-btn">×</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ $t('windows.aiStudioGlobalSettings.loading') }}</p>
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
          <h3 class="section-title">{{ $t('windows.aiStudioGlobalSettings.aiProfiles') }}</h3>
          <button @click="createNewProfile" class="btn-add">{{ $t('windows.aiStudioGlobalSettings.newProfile') }}</button>
        </div>
        <div class="profile-layout">
          <!-- Profile Liste -->
          <ProfileList
            :profiles="profiles"
            :selected-key="selectedProfileKey"
            @select="selectProfile"
          />

          <!-- Profile Editor -->
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/api/http'
import { useWindowStore } from '@/store/window.store'
import { ProviderGrid, ProfileList, ProfileEditor, ApiKeyModal } from '../../settings/global-settings'

const { t } = useI18n()
const windowStore = useWindowStore()

// Types
interface Provider {
  provider_id: number
  name: string
  display_name: string
  active: boolean
  has_api_key: boolean
}

interface Profile {
  key: string
  name: string
  description?: string
  is_default: boolean
  [key: string]: any
}

interface AIModel {
  model_id: number
  model_name: string
  display_name?: string
  provider_name: string
  category: string
  active: boolean
}

interface Stats {
  total_models: number
  active_models: number
  providers: number
  categories: number
}

// State
const loading = ref(true)
const saving = ref(false)
const isSyncing = ref(false)
const isTesting = ref(false)
const testingProvider = ref<string | null>(null)

const providers = ref<Provider[]>([])
const profiles = ref<Profile[]>([])
const models = ref<AIModel[]>([])
const categories = ref<string[]>([])
const stats = ref<Stats>({ total_models: 0, active_models: 0, providers: 0, categories: 0 })

const selectedProfileKey = ref<string | null>(null)
const isCreating = ref(false)

const formData = reactive({
  key: '',
  name: '',
  description: '',
  models: {} as Record<string, string>
})

// API Key Modal
const apiKeyModal = ref<Provider | null>(null)
const apiKeyInput = ref('')
const showApiKey = ref(false)
const testingApiKey = ref(false)
const savingApiKey = ref(false)
const apiKeyResult = ref<{ success: boolean; message: string } | null>(null)

// Feedback
const actionResult = ref<{ success: boolean; message: string } | null>(null)
const toast = ref<{ type: string; message: string } | null>(null)

// Computed
const selectedProfile = computed(() =>
  profiles.value.find(p => p.key === selectedProfileKey.value)
)

const modelCountsByProvider = computed(() => {
  const counts: Record<string, number> = {}
  for (const model of models.value) {
    counts[model.provider_name] = (counts[model.provider_name] || 0) + 1
  }
  return counts
})

// Data Loading
async function loadData() {
  loading.value = true
  try {
    const providersRes = await http.get('/admin/ai/providers')
    if (providersRes.data.success) {
      providers.value = providersRes.data.data.providers || providersRes.data.data || []
    }

    const modelsRes = await http.get('/admin/ai/models', { params: { include_inactive: false } })
    if (modelsRes.data.success) {
      models.value = modelsRes.data.data.models || modelsRes.data.data || []
      const cats = [...new Set(models.value.map(m => m.category).filter(Boolean))]
      categories.value = cats.sort()
    }

    const statsRes = await http.get('/admin/ai/models/stats')
    if (statsRes.data.success) {
      stats.value = statsRes.data.data.stats || statsRes.data.data || stats.value
    }

    await loadProfiles()
  } catch (error) {
    console.error('Failed to load data:', error)
    showToast('error', t('windows.aiStudioGlobalSettings.loadError'))
  } finally {
    loading.value = false
  }
}

async function loadProfiles() {
  try {
    const response = await http.get('/admin/ai-model-profiles')
    if (response.data.success) {
      profiles.value = response.data.data?.profiles || []
    }
  } catch (error) {
    console.error('Failed to load profiles:', error)
  }
}

// Profile Methods
function selectProfile(profile: Profile) {
  selectedProfileKey.value = profile.key
  isCreating.value = false
  populateForm(profile)
}

function createNewProfile() {
  selectedProfileKey.value = null
  isCreating.value = true
  resetForm()
}

function populateForm(profile: Profile) {
  formData.key = profile.key
  formData.name = profile.name
  formData.description = profile.description || ''
  formData.models = {}
  for (const cat of categories.value) {
    const fieldName = `${cat}_model_id`
    formData.models[cat] = profile[fieldName] || ''
  }
}

function resetForm() {
  formData.key = ''
  formData.name = ''
  formData.description = ''
  formData.models = {}
}

function updateFormData(data: typeof formData) {
  Object.assign(formData, data)
}

function cancelEdit() {
  if (selectedProfile.value) {
    populateForm(selectedProfile.value)
  } else {
    resetForm()
  }
  isCreating.value = false
}

async function saveProfile() {
  if (!formData.name.trim()) {
    showToast('error', t('windows.aiStudioGlobalSettings.nameRequired'))
    return
  }
  if (isCreating.value && !formData.key.trim()) {
    showToast('error', t('windows.aiStudioGlobalSettings.keyRequired'))
    return
  }

  saving.value = true
  try {
    const body: Record<string, any> = {
      name: formData.name,
      description: formData.description || null
    }

    if (isCreating.value) {
      body.key = formData.key.toLowerCase().replace(/\s+/g, '_')
    }

    for (const cat of categories.value) {
      body[`${cat}_model_id`] = formData.models[cat] || null
    }

    const response = isCreating.value
      ? await http.post('/admin/ai-model-profiles', body)
      : await http.put(`/admin/ai-model-profiles/${formData.key}`, body)

    if (response.data.success) {
      showToast('success', isCreating.value
        ? t('windows.aiStudioGlobalSettings.profileCreated')
        : t('windows.aiStudioGlobalSettings.profileSaved'))
      await loadProfiles()
      if (isCreating.value) selectedProfileKey.value = body.key
      isCreating.value = false
    } else {
      showToast('error', response.data.error?.message || t('windows.aiStudioGlobalSettings.saveError'))
    }
  } catch (error) {
    console.error('Failed to save profile:', error)
    showToast('error', t('windows.aiStudioGlobalSettings.saveError'))
  } finally {
    saving.value = false
  }
}

async function deleteProfile() {
  if (!selectedProfileKey.value) return
  if (!confirm(t('windows.aiStudioGlobalSettings.confirmDeleteProfile'))) return

  try {
    const response = await http.delete(`/admin/ai-model-profiles/${selectedProfileKey.value}`)
    if (response.data.success) {
      showToast('success', t('windows.aiStudioGlobalSettings.profileDeleted'))
      selectedProfileKey.value = null
      resetForm()
      await loadProfiles()
    } else {
      showToast('error', response.data.error?.message || t('windows.aiStudioGlobalSettings.deleteError'))
    }
  } catch (error: any) {
    showToast('error', error.response?.data?.error?.message || t('windows.aiStudioGlobalSettings.deleteError'))
  }
}

async function setAsDefault() {
  if (!selectedProfileKey.value) return
  try {
    const response = await http.post(`/admin/ai-model-profiles/${selectedProfileKey.value}/default`)
    if (response.data.success) {
      showToast('success', t('windows.aiStudioGlobalSettings.setDefaultSuccess'))
      await loadProfiles()
    } else {
      showToast('error', t('windows.aiStudioGlobalSettings.setDefaultError'))
    }
  } catch (error) {
    showToast('error', t('windows.aiStudioGlobalSettings.setDefaultError'))
  }
}

// Provider Methods
function openApiKeyModal(provider: Provider) {
  apiKeyModal.value = provider
  apiKeyInput.value = ''
  showApiKey.value = false
  apiKeyResult.value = null
}

async function saveApiKey() {
  if (!apiKeyModal.value || !apiKeyInput.value) return
  savingApiKey.value = true
  try {
    const response = await http.put(`/admin/ai/providers/${apiKeyModal.value.provider_id}/api-key`, {
      api_key: apiKeyInput.value
    })
    if (response.data.success) {
      apiKeyResult.value = { success: true, message: t('windows.aiStudioGlobalSettings.apiKeySaved') }
      apiKeyInput.value = ''
      await loadData()
      setTimeout(() => { apiKeyModal.value = null }, 1000)
    } else {
      apiKeyResult.value = { success: false, message: response.data.error?.message || t('windows.aiStudioGlobalSettings.saveError') }
    }
  } catch (error: any) {
    apiKeyResult.value = { success: false, message: error.response?.data?.error?.message || t('windows.aiStudioGlobalSettings.saveError') }
  } finally {
    savingApiKey.value = false
  }
}

async function testApiKey() {
  if (!apiKeyModal.value) return
  testingApiKey.value = true
  apiKeyResult.value = null
  try {
    const response = await http.get(`/admin/ai/providers/${apiKeyModal.value.provider_id}/test`)
    if (response.data.success) {
      apiKeyResult.value = { success: true, message: t('windows.aiStudioGlobalSettings.connectionOkMs', { ms: response.data.data?.response_time_ms || 0 }) }
    } else {
      apiKeyResult.value = { success: false, message: response.data.error?.message || t('windows.aiStudioGlobalSettings.testFailed') }
    }
  } catch (error: any) {
    apiKeyResult.value = { success: false, message: error.response?.data?.error?.message || t('windows.aiStudioGlobalSettings.connectionFailed') }
  } finally {
    testingApiKey.value = false
  }
}

async function testProvider(provider: Provider) {
  testingProvider.value = provider.name
  try {
    const response = await http.get(`/admin/ai/providers/${provider.provider_id}/test`)
    showToast(response.data.success ? 'success' : 'error',
      response.data.success
        ? t('windows.aiStudioGlobalSettings.providerOk', { provider: provider.display_name })
        : t('windows.aiStudioGlobalSettings.providerFailed', { provider: provider.display_name }))
  } catch (error) {
    showToast('error', t('windows.aiStudioGlobalSettings.providerFailed', { provider: provider.display_name }))
  } finally {
    testingProvider.value = null
  }
}

async function syncProvider(providerName: string) {
  isSyncing.value = true
  actionResult.value = null
  try {
    const response = await http.post('/admin/ai/models/sync', { provider: providerName })
    actionResult.value = response.data.success
      ? { success: true, message: t('windows.aiStudioGlobalSettings.syncSuccess', { count: response.data.data?.synced || 0 }) }
      : { success: false, message: response.data.error?.message || t('windows.aiStudioGlobalSettings.syncFailed') }
    if (response.data.success) await loadData()
  } catch (error: any) {
    actionResult.value = { success: false, message: error.response?.data?.error?.message || t('windows.aiStudioGlobalSettings.syncFailed') }
  } finally {
    isSyncing.value = false
  }
}

async function syncAllModels() {
  isSyncing.value = true
  actionResult.value = null
  try {
    const response = await http.post('/admin/ai/models/sync')
    actionResult.value = response.data.success
      ? { success: true, message: t('windows.aiStudioGlobalSettings.syncSuccess', { count: response.data.data?.synced || 0 }) }
      : { success: false, message: response.data.error?.message || t('windows.aiStudioGlobalSettings.syncFailed') }
    if (response.data.success) await loadData()
  } catch (error: any) {
    actionResult.value = { success: false, message: error.response?.data?.error?.message || t('windows.aiStudioGlobalSettings.syncFailed') }
  } finally {
    isSyncing.value = false
  }
}

async function testAllConnections() {
  isTesting.value = true
  let successCount = 0, failCount = 0

  for (const provider of providers.value.filter(p => p.has_api_key)) {
    try {
      const response = await http.get(`/admin/ai/providers/${provider.provider_id}/test`)
      response.data.success ? successCount++ : failCount++
    } catch { failCount++ }
  }

  actionResult.value = {
    success: failCount === 0,
    message: t('windows.aiStudioGlobalSettings.testComplete', { success: successCount, failed: failCount })
  }
  isTesting.value = false
}

function showToast(type: string, message: string) {
  toast.value = { type, message }
  setTimeout(() => { toast.value = null }, 3000)
}

function openPricingWindow() {
  windowStore.openWindow({ type: 'admin-ai-pricing', title: t('windows.aiPricing.title'), icon: '💰' })
}

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
