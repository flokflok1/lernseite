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
-->

<template>
  <div class="global-settings-tab">
    <!-- Header mit Stats -->
    <div class="header-bar">
      <div class="header-left">
        <h2 class="header-title">Globale Einstellungen</h2>
        <div class="header-stats">
          <span class="stat-item">{{ stats.total_models || 0 }} Modelle</span>
          <span class="stat-divider">|</span>
          <span class="stat-item">{{ stats.providers || 0 }} Provider</span>
          <span class="stat-divider">|</span>
          <span class="stat-item">{{ categories.length }} Kategorien</span>
        </div>
      </div>
      <div class="header-actions">
        <button @click="syncAllModels" :disabled="isSyncing" class="btn-action">
          <span :class="{ 'animate-spin': isSyncing }">🔄</span>
          {{ isSyncing ? 'Sync...' : 'Alle Sync' }}
        </button>
        <button @click="testAllConnections" :disabled="isTesting" class="btn-action secondary">
          <span :class="{ 'animate-spin': isTesting }">🔌</span>
          {{ isTesting ? 'Teste...' : 'Test' }}
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
      <p>Lade Einstellungen...</p>
    </div>

    <div v-else class="main-content">
      <!-- Provider Sektion (kompakt) -->
      <div class="section provider-section">
        <div class="section-header">
          <h3 class="section-title">Provider & API-Keys</h3>
        </div>
        <div class="provider-grid">
          <div
            v-for="provider in providers"
            :key="provider.provider_id"
            class="provider-card"
            :class="{ active: provider.active, configured: provider.has_api_key }"
          >
            <div class="provider-icon" :class="getProviderClass(provider.name)">
              {{ getProviderIcon(provider.name) }}
            </div>
            <div class="provider-info">
              <span class="provider-name">{{ provider.display_name }}</span>
              <span class="provider-meta">{{ getModelCountForProvider(provider.name) }} Modelle</span>
            </div>
            <div class="provider-status">
              <span class="status-dot" :class="provider.has_api_key ? 'ok' : 'missing'"></span>
            </div>
            <div class="provider-actions">
              <button @click="openApiKeyModal(provider)" class="btn-small" title="API-Key">
                🔑
              </button>
              <button @click="testProvider(provider)" :disabled="testingProvider === provider.name" class="btn-small" title="Testen">
                <span :class="{ 'animate-spin': testingProvider === provider.name }">🔌</span>
              </button>
              <button @click="syncProvider(provider.name)" :disabled="isSyncing" class="btn-small" title="Sync">
                🔄
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Profile Sektion -->
      <div class="section profile-section">
        <div class="section-header">
          <h3 class="section-title">KI-Profile</h3>
          <button @click="createNewProfile" class="btn-add">+ Neues Profil</button>
        </div>
        <div class="profile-layout">
          <!-- Profile Liste -->
          <div class="profile-list">
            <div
              v-for="profile in profiles"
              :key="profile.key"
              class="profile-item"
              :class="{ active: selectedProfileKey === profile.key }"
              @click="selectProfile(profile)"
            >
              <div class="profile-indicator" :class="{ default: profile.is_default }"></div>
              <div class="profile-content">
                <span class="profile-name">{{ profile.name }}</span>
                <span class="profile-key">{{ profile.key }}</span>
              </div>
              <span v-if="profile.is_default" class="default-badge">Default</span>
            </div>
            <div v-if="!profiles.length" class="empty-list">
              Keine Profile vorhanden
            </div>
          </div>

          <!-- Profile Editor -->
          <div class="profile-editor">
            <div v-if="!selectedProfile && !isCreating" class="editor-empty">
              <p>Wähle ein Profil aus der Liste</p>
            </div>

            <template v-else>
              <!-- Meta -->
              <div class="editor-header">
                <h4>{{ isCreating ? 'Neues Profil' : 'Profil bearbeiten' }}</h4>
              </div>

              <div class="editor-form">
                <!-- Key -->
                <div class="form-row">
                  <label>Schlüssel</label>
                  <input
                    v-if="isCreating"
                    v-model="formData.key"
                    type="text"
                    placeholder="z.B. premium"
                    class="form-input"
                  />
                  <span v-else class="form-value mono">{{ formData.key }}</span>
                </div>

                <!-- Name -->
                <div class="form-row">
                  <label>Name</label>
                  <input
                    v-model="formData.name"
                    type="text"
                    placeholder="Anzeigename"
                    class="form-input"
                  />
                </div>

                <!-- Description -->
                <div class="form-row">
                  <label>Beschreibung</label>
                  <input
                    v-model="formData.description"
                    type="text"
                    placeholder="Optional"
                    class="form-input"
                  />
                </div>

                <!-- Dynamische Kategorien -->
                <div class="categories-section">
                  <h5>Modelle pro Kategorie</h5>
                  <div class="category-grid">
                    <div
                      v-for="category in categories"
                      :key="category"
                      class="category-item"
                    >
                      <label class="category-label">
                        <span class="category-icon">{{ getCategoryIcon(category) }}</span>
                        <span class="category-name">{{ category }}</span>
                      </label>
                      <select
                        v-model="formData.models[category]"
                        class="category-select"
                      >
                        <option value="">Nicht gesetzt</option>
                        <option
                          v-for="model in getModelsForCategory(category)"
                          :key="model.model_id"
                          :value="model.model_id || model.model_name"
                        >
                          {{ model.display_name || model.model_name }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div class="editor-actions">
                  <button v-if="!isCreating && !selectedProfile?.is_default" @click="deleteProfile" class="btn-danger">
                    Löschen
                  </button>
                  <div class="action-spacer"></div>
                  <button v-if="!isCreating && !selectedProfile?.is_default" @click="setAsDefault" class="btn-secondary">
                    Als Default
                  </button>
                  <button @click="cancelEdit" class="btn-secondary">
                    Abbrechen
                  </button>
                  <button @click="saveProfile" :disabled="saving" class="btn-primary">
                    {{ saving ? 'Speichern...' : 'Speichern' }}
                  </button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- API-Key Modal -->
    <div v-if="apiKeyModal" class="modal-overlay" @click="apiKeyModal = null">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ apiKeyModal.display_name }} - API-Key</h3>
          <button @click="apiKeyModal = null" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label>API-Key</label>
            <div class="input-group">
              <input
                v-model="apiKeyInput"
                :type="showApiKey ? 'text' : 'password'"
                :placeholder="apiKeyModal.has_api_key ? '••••••••••••••••' : 'API Key eingeben...'"
                class="form-input mono"
              />
              <button @click="showApiKey = !showApiKey" class="btn-icon">
                {{ showApiKey ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>
          <div v-if="apiKeyResult" class="api-key-result" :class="apiKeyResult.success ? 'success' : 'error'">
            {{ apiKeyResult.message }}
          </div>
        </div>
        <div class="modal-footer">
          <button @click="testApiKey" :disabled="testingApiKey" class="btn-secondary">
            {{ testingApiKey ? 'Teste...' : 'Testen' }}
          </button>
          <button @click="saveApiKey" :disabled="!apiKeyInput || savingApiKey" class="btn-primary">
            {{ savingApiKey ? 'Speichern...' : 'Speichern' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Status Toast -->
    <div v-if="toast" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import http from '@/api/http'

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
  [key: string]: any // Für dynamische Model-IDs
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

// Category Icons
const categoryIcons: Record<string, string> = {
  chat: '💬',
  audio: '🔊',
  video: '🎬',
  embedding: '📊',
  image: '🖼️',
  reasoning: '🧠',
  realtime: '⚡',
  moderation: '🛡️',
  vision: '👁️',
  transcription: '📝',
  translation: '🌍',
  legacy: '⚙️'
}

// Methods
function getCategoryIcon(category: string): string {
  return categoryIcons[category] || '📦'
}

function getProviderIcon(provider: string): string {
  const icons: Record<string, string> = {
    openai: '🤖',
    anthropic: '🧠',
    google: '🔍',
    deepl: '🌍'
  }
  return icons[provider?.toLowerCase()] || '⚙️'
}

function getProviderClass(provider: string): string {
  return `provider-${provider?.toLowerCase() || 'default'}`
}

function getModelCountForProvider(providerName: string): number {
  return models.value.filter(m => m.provider_name === providerName).length
}

function getModelsForCategory(category: string): AIModel[] {
  return models.value.filter(m => m.category === category && m.active)
}

// Data Loading
async function loadData() {
  loading.value = true
  try {
    // Load providers
    const providersRes = await http.get('/admin/ai/providers')
    if (providersRes.data.success) {
      providers.value = providersRes.data.data.providers || providersRes.data.data || []
    }

    // Load models with categories
    const modelsRes = await http.get('/admin/ai/models', { params: { include_inactive: false } })
    if (modelsRes.data.success) {
      models.value = modelsRes.data.data.models || modelsRes.data.data || []
      // Extract unique categories
      const cats = [...new Set(models.value.map(m => m.category).filter(Boolean))]
      categories.value = cats.sort()
    }

    // Load stats
    const statsRes = await http.get('/admin/ai/models/stats')
    if (statsRes.data.success) {
      stats.value = statsRes.data.data.stats || statsRes.data.data || stats.value
    }

    // Load profiles
    await loadProfiles()

  } catch (error) {
    console.error('Failed to load data:', error)
    showToast('error', 'Fehler beim Laden der Daten')
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

  // Populate model selections from profile
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
    showToast('error', 'Name ist erforderlich')
    return
  }
  if (isCreating.value && !formData.key.trim()) {
    showToast('error', 'Schlüssel ist erforderlich')
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

    // Add model IDs for each category
    for (const cat of categories.value) {
      const fieldName = `${cat}_model_id`
      body[fieldName] = formData.models[cat] || null
    }

    let response
    if (isCreating.value) {
      response = await http.post('/admin/ai-model-profiles', body)
    } else {
      response = await http.put(`/admin/ai-model-profiles/${formData.key}`, body)
    }

    if (response.data.success) {
      showToast('success', isCreating.value ? 'Profil erstellt' : 'Profil gespeichert')
      await loadProfiles()
      if (isCreating.value) {
        selectedProfileKey.value = body.key
      }
      isCreating.value = false
    } else {
      showToast('error', response.data.error?.message || 'Fehler beim Speichern')
    }
  } catch (error) {
    console.error('Failed to save profile:', error)
    showToast('error', 'Fehler beim Speichern')
  } finally {
    saving.value = false
  }
}

async function deleteProfile() {
  if (!selectedProfileKey.value) return
  if (!confirm('Profil wirklich löschen?')) return

  try {
    const response = await http.delete(`/admin/ai-model-profiles/${selectedProfileKey.value}`)

    if (response.data.success) {
      showToast('success', 'Profil gelöscht')
      selectedProfileKey.value = null
      resetForm()
      await loadProfiles()
    } else {
      showToast('error', response.data.error?.message || 'Fehler beim Löschen')
    }
  } catch (error: any) {
    showToast('error', error.response?.data?.error?.message || 'Fehler beim Löschen')
  }
}

async function setAsDefault() {
  if (!selectedProfileKey.value) return

  try {
    const response = await http.post(`/admin/ai-model-profiles/${selectedProfileKey.value}/default`)

    if (response.data.success) {
      showToast('success', 'Als Default gesetzt')
      await loadProfiles()
    } else {
      showToast('error', 'Fehler beim Setzen des Defaults')
    }
  } catch (error) {
    showToast('error', 'Fehler beim Setzen des Defaults')
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
      apiKeyResult.value = { success: true, message: 'API-Key gespeichert!' }
      apiKeyInput.value = ''
      await loadData()
      setTimeout(() => { apiKeyModal.value = null }, 1000)
    } else {
      apiKeyResult.value = { success: false, message: response.data.error?.message || 'Fehler' }
    }
  } catch (error: any) {
    apiKeyResult.value = { success: false, message: error.response?.data?.error?.message || 'Fehler' }
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
      apiKeyResult.value = { success: true, message: `Verbindung OK (${response.data.data?.response_time_ms || 0}ms)` }
    } else {
      apiKeyResult.value = { success: false, message: response.data.error?.message || 'Test fehlgeschlagen' }
    }
  } catch (error: any) {
    apiKeyResult.value = { success: false, message: error.response?.data?.error?.message || 'Verbindung fehlgeschlagen' }
  } finally {
    testingApiKey.value = false
  }
}

async function testProvider(provider: Provider) {
  testingProvider.value = provider.name
  try {
    const response = await http.get(`/admin/ai/providers/${provider.provider_id}/test`)
    if (response.data.success) {
      showToast('success', `${provider.display_name}: OK`)
    } else {
      showToast('error', `${provider.display_name}: Fehlgeschlagen`)
    }
  } catch (error) {
    showToast('error', `${provider.display_name}: Fehlgeschlagen`)
  } finally {
    testingProvider.value = null
  }
}

async function syncProvider(providerName: string) {
  isSyncing.value = true
  actionResult.value = null
  try {
    const response = await http.post('/admin/ai/models/sync', { provider: providerName })
    if (response.data.success) {
      actionResult.value = {
        success: true,
        message: `Sync erfolgreich: ${response.data.data?.synced || 0} Modelle`
      }
      await loadData()
    } else {
      actionResult.value = { success: false, message: response.data.error?.message || 'Sync fehlgeschlagen' }
    }
  } catch (error: any) {
    actionResult.value = { success: false, message: error.response?.data?.error?.message || 'Sync fehlgeschlagen' }
  } finally {
    isSyncing.value = false
  }
}

async function syncAllModels() {
  isSyncing.value = true
  actionResult.value = null
  try {
    const response = await http.post('/admin/ai/models/sync')
    if (response.data.success) {
      actionResult.value = {
        success: true,
        message: `Sync erfolgreich: ${response.data.data?.synced || 0} Modelle`
      }
      await loadData()
    } else {
      actionResult.value = { success: false, message: response.data.error?.message || 'Sync fehlgeschlagen' }
    }
  } catch (error: any) {
    actionResult.value = { success: false, message: error.response?.data?.error?.message || 'Sync fehlgeschlagen' }
  } finally {
    isSyncing.value = false
  }
}

async function testAllConnections() {
  isTesting.value = true
  let successCount = 0
  let failCount = 0

  for (const provider of providers.value.filter(p => p.has_api_key)) {
    try {
      const response = await http.get(`/admin/ai/providers/${provider.provider_id}/test`)
      if (response.data.success) {
        successCount++
      } else {
        failCount++
      }
    } catch {
      failCount++
    }
  }

  actionResult.value = {
    success: failCount === 0,
    message: `Test abgeschlossen: ${successCount} OK, ${failCount} fehlgeschlagen`
  }
  isTesting.value = false
}

function showToast(type: string, message: string) {
  toast.value = { type, message }
  setTimeout(() => { toast.value = null }, 3000)
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.global-settings-tab {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.header-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.header-stats {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.stat-divider {
  color: var(--color-border);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.625rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  transition: opacity 0.15s;
}

.btn-action:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-action:disabled {
  opacity: 0.5;
}

.btn-action.secondary {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

/* Action Result */
.action-result {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
}

.action-result.success {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.action-result.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.close-btn {
  font-size: 1.25rem;
  line-height: 1;
  opacity: 0.7;
}

.close-btn:hover {
  opacity: 1;
}

/* Loading */
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Main Content */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Sections */
.section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.section-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.btn-add {
  padding: 0.375rem 0.75rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Provider Grid */
.provider-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.75rem;
}

.provider-card {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  min-width: 220px;
}

.provider-card.configured {
  border-color: var(--color-primary);
}

.provider-icon {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  font-size: 1rem;
  background: var(--color-surface);
}

.provider-openai { background: rgba(16, 163, 127, 0.1); }
.provider-anthropic { background: rgba(249, 115, 22, 0.1); }

.provider-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.provider-name {
  font-weight: 500;
  color: var(--color-text-primary);
  font-size: 0.8125rem;
}

.provider-meta {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.provider-status {
  padding: 0 0.5rem;
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.status-dot.ok { background: #22c55e; }
.status-dot.missing { background: #ef4444; }

.provider-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-small {
  padding: 0.375rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.875rem;
  transition: all 0.15s;
}

.btn-small:hover:not(:disabled) {
  border-color: var(--color-primary);
}

.btn-small:disabled {
  opacity: 0.5;
}

/* Profile Layout */
.profile-layout {
  display: grid;
  grid-template-columns: 180px 1fr;
  max-height: 320px;
}

.profile-list {
  border-right: 1px solid var(--color-border);
  overflow-y: auto;
  max-height: 320px;
}

.profile-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
  transition: background 0.15s;
}

.profile-item:hover {
  background: var(--color-surface-secondary);
}

.profile-item.active {
  background: var(--color-primary-subtle);
}

.profile-indicator {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: var(--color-border);
}

.profile-indicator.default {
  background: var(--color-primary);
}

.profile-content {
  flex: 1;
  min-width: 0;
}

.profile-name {
  display: block;
  font-weight: 500;
  color: var(--color-text-primary);
  font-size: 0.8125rem;
}

.profile-key {
  display: block;
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  font-family: ui-monospace, monospace;
}

.default-badge {
  padding: 0.125rem 0.375rem;
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 600;
}

.empty-list {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}

/* Profile Editor */
.profile-editor {
  padding: 1rem;
  overflow-y: auto;
  max-height: 320px;
}

.editor-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-tertiary);
}

.editor-header {
  margin-bottom: 0.75rem;
}

.editor-header h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.editor-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-row label {
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-input {
  padding: 0.375rem 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  color: var(--color-text-primary);
  font-size: 0.8125rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-input.mono {
  font-family: ui-monospace, monospace;
}

.form-value {
  padding: 0.5rem 0;
  color: var(--color-text-primary);
  font-size: 0.875rem;
}

.form-value.mono {
  font-family: ui-monospace, monospace;
}

/* Categories Section */
.categories-section {
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.categories-section h5 {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.category-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.category-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
}

.category-icon {
  font-size: 0.75rem;
}

.category-name {
  text-transform: capitalize;
}

.category-select {
  padding: 0.35rem 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  color: var(--color-text-primary);
  font-size: 0.6875rem;
}

.category-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* Editor Actions */
.editor-actions {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
}

.action-spacer {
  flex: 1;
}

.btn-primary {
  padding: 0.375rem 0.75rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.btn-primary:disabled {
  opacity: 0.5;
}

.btn-secondary {
  padding: 0.375rem 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  color: var(--color-text-primary);
  font-size: 0.75rem;
}

.btn-danger {
  padding: 0.375rem 0.75rem;
  background: #ef4444;
  color: white;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-surface);
  border-radius: 0.75rem;
  width: 100%;
  max-width: 450px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close {
  font-size: 1.5rem;
  line-height: 1;
  color: var(--color-text-tertiary);
}

.modal-body {
  padding: 1.25rem;
}

.input-group {
  display: flex;
  gap: 0.5rem;
}

.input-group .form-input {
  flex: 1;
}

.btn-icon {
  padding: 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
}

.api-key-result {
  margin-top: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
}

.api-key-result.success {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.api-key-result.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

/* Toast */
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 0.75rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  z-index: 1001;
  animation: slideIn 0.2s ease;
}

.toast.success {
  background: #22c55e;
  color: white;
}

.toast.error {
  background: #ef4444;
  color: white;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(1rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Animate spin */
.animate-spin {
  animation: spin 1s linear infinite;
  display: inline-block;
}
</style>
