<!--
  Admin AI Settings Page - KI-Provider & API-Keys

  Verwaltung von KI-Providern (OpenAI, Anthropic, Google):
  - API-Keys sicher eingeben und speichern
  - Provider aktivieren/deaktivieren
  - API-Verbindung testen
  - Provider-Status anzeigen
-->

<template>
  <div class="admin-ai-settings-page p-6">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-[var(--color-text-primary)] mb-2">KI-Einstellungen</h1>
      <p class="text-[var(--color-text-secondary)]">
        Verwalten Sie API-Keys und Einstellungen für KI-Provider
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]"></div>
      <span class="ml-3 text-[var(--color-text-secondary)]">Lade Provider...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex items-center gap-2 text-red-700">
        <span class="text-xl">&#x26A0;</span>
        <span>{{ error }}</span>
      </div>
      <button
        @click="loadProviders"
        class="mt-2 text-sm text-red-600 hover:text-red-800 underline"
      >
        Erneut versuchen
      </button>
    </div>

    <!-- Providers List -->
    <div v-else class="space-y-6">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-1">Provider Gesamt</p>
              <p class="text-2xl font-bold text-[var(--color-text-primary)]">{{ providers.length }}</p>
            </div>
            <div class="text-3xl">&#x1F916;</div>
          </div>
        </div>

        <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-1">Aktiv</p>
              <p class="text-2xl font-bold text-green-600">{{ activeProviders }}</p>
            </div>
            <div class="text-3xl">&#x2705;</div>
          </div>
        </div>

        <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-1">Konfiguriert</p>
              <p class="text-2xl font-bold text-blue-600">{{ configuredProviders }}</p>
            </div>
            <div class="text-3xl">&#x1F511;</div>
          </div>
        </div>
      </div>

      <!-- Provider Cards -->
      <div class="space-y-4">
        <div
          v-for="provider in providers"
          :key="provider.provider_id"
          class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden"
        >
          <!-- Provider Header -->
          <div class="px-6 py-4 border-b border-[var(--color-border)] flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="text-3xl">{{ getProviderIcon(provider.name) }}</div>
              <div>
                <h3 class="text-lg font-bold text-[var(--color-text-primary)]">
                  {{ provider.display_name }}
                </h3>
                <p class="text-sm text-[var(--color-text-secondary)]">
                  {{ provider.provider_type }}
                </p>
              </div>
            </div>

            <div class="flex items-center gap-4">
              <!-- Status Badge -->
              <span
                :class="[
                  'px-3 py-1 rounded-full text-sm font-medium',
                  provider.active
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-600'
                ]"
              >
                {{ provider.active ? 'Aktiv' : 'Inaktiv' }}
              </span>

              <!-- API Key Badge -->
              <span
                :class="[
                  'px-3 py-1 rounded-full text-sm font-medium',
                  provider.has_api_key
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-yellow-100 text-yellow-700'
                ]"
              >
                {{ provider.has_api_key ? 'API-Key gesetzt' : 'Kein API-Key' }}
              </span>
            </div>
          </div>

          <!-- Provider Body -->
          <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Left Column: API Key Input -->
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                  API-Key
                </label>
                <div class="flex gap-2">
                  <input
                    v-model="apiKeys[provider.provider_id]"
                    :type="showApiKey[provider.provider_id] ? 'text' : 'password'"
                    :placeholder="provider.has_api_key ? '********** (bereits gesetzt)' : 'API-Key eingeben...'"
                    class="flex-1 px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                  />
                  <button
                    @click="toggleShowApiKey(provider.provider_id)"
                    class="px-3 py-2 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors"
                    :title="showApiKey[provider.provider_id] ? 'Verbergen' : 'Anzeigen'"
                  >
                    {{ showApiKey[provider.provider_id] ? '&#x1F648;' : '&#x1F441;' }}
                  </button>
                </div>

                <!-- Action Buttons -->
                <div class="flex gap-2 mt-3">
                  <button
                    @click="saveApiKey(provider)"
                    :disabled="!apiKeys[provider.provider_id] || savingKey[provider.provider_id]"
                    class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity flex items-center gap-2"
                  >
                    <span v-if="savingKey[provider.provider_id]" class="animate-spin">&#x23F3;</span>
                    <span>{{ savingKey[provider.provider_id] ? 'Speichert...' : 'Speichern' }}</span>
                  </button>

                  <button
                    v-if="provider.has_api_key"
                    @click="testApiKey(provider)"
                    :disabled="testingKey[provider.provider_id]"
                    class="px-4 py-2 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-secondary)] disabled:opacity-50 transition-colors flex items-center gap-2"
                  >
                    <span v-if="testingKey[provider.provider_id]" class="animate-spin">&#x23F3;</span>
                    <span>{{ testingKey[provider.provider_id] ? 'Testet...' : 'Testen' }}</span>
                  </button>

                  <button
                    v-if="provider.has_api_key"
                    @click="deleteApiKey(provider)"
                    :disabled="deletingKey[provider.provider_id]"
                    class="px-4 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 disabled:opacity-50 transition-colors"
                  >
                    Entfernen
                  </button>
                </div>

                <!-- Test Result -->
                <div
                  v-if="testResults[provider.provider_id]"
                  :class="[
                    'mt-3 p-3 rounded-lg text-sm',
                    testResults[provider.provider_id].success
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  ]"
                >
                  <div class="flex items-start gap-2">
                    <span>{{ testResults[provider.provider_id].success ? '&#x2705;' : '&#x274C;' }}</span>
                    <div>
                      <p class="font-medium">{{ testResults[provider.provider_id].message }}</p>
                      <p v-if="testResults[provider.provider_id].response_time" class="text-xs opacity-75">
                        Antwortzeit: {{ testResults[provider.provider_id].response_time }}ms
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Right Column: Settings -->
              <div>
                <div class="space-y-4">
                  <!-- Active Toggle -->
                  <div class="flex items-center justify-between">
                    <label class="text-sm font-medium text-[var(--color-text-primary)]">
                      Provider aktivieren
                    </label>
                    <button
                      @click="toggleActive(provider)"
                      :class="[
                        'relative w-12 h-6 rounded-full transition-colors',
                        provider.active ? 'bg-green-500' : 'bg-gray-300'
                      ]"
                    >
                      <span
                        :class="[
                          'absolute top-1 w-4 h-4 bg-white rounded-full transition-transform',
                          provider.active ? 'right-1' : 'left-1'
                        ]"
                      ></span>
                    </button>
                  </div>

                  <!-- Priority -->
                  <div>
                    <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                      Prioritaet (hoeher = bevorzugt)
                    </label>
                    <input
                      type="number"
                      :value="provider.priority"
                      @change="updatePriority(provider, $event)"
                      min="0"
                      max="100"
                      class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)]"
                    />
                  </div>

                  <!-- Rate Limit -->
                  <div>
                    <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                      Rate Limit (Anfragen/Minute)
                    </label>
                    <input
                      type="number"
                      :value="provider.rate_limit_per_minute"
                      @change="updateRateLimit(provider, $event)"
                      min="1"
                      max="1000"
                      class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)]"
                    />
                  </div>

                  <!-- Last Validated -->
                  <div v-if="provider.last_validated" class="text-sm text-[var(--color-text-secondary)]">
                    Zuletzt validiert: {{ formatDate(provider.last_validated) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Default Model Selection Section -->
      <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden">
        <div class="px-6 py-4 border-b border-[var(--color-border)]">
          <h3 class="text-lg font-bold text-[var(--color-text-primary)]">
            Standard KI-Modell
          </h3>
          <p class="text-sm text-[var(--color-text-secondary)]">
            Waehlen Sie den Standard-Provider und das Modell fuer KI-Operationen
          </p>
        </div>

        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Default Provider Selection -->
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                Standard-Provider
              </label>
              <select
                v-model="defaultSettings.provider"
                @change="onProviderChange"
                class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              >
                <option
                  v-for="(providerData, providerName) in availableModels"
                  :key="providerName"
                  :value="providerName"
                >
                  {{ providerData.display_name }}
                </option>
              </select>
            </div>

            <!-- Default Model Selection -->
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
                Standard-Modell
              </label>
              <select
                v-model="defaultSettings.model"
                class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              >
                <option
                  v-for="model in currentProviderModels"
                  :key="model.name"
                  :value="model.name"
                >
                  {{ model.name }} ({{ formatPrice(model.input_price) }}/{{ formatPrice(model.output_price) }} pro 1K Token)
                </option>
              </select>
            </div>
          </div>

          <!-- Model Info -->
          <div v-if="selectedModelInfo" class="mt-4 p-4 bg-[var(--color-bg)] rounded-lg border border-[var(--color-border)]">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-[var(--color-text-primary)]">{{ selectedModelInfo.name }}</p>
                <p class="text-sm text-[var(--color-text-secondary)]">
                  Input: {{ formatPrice(selectedModelInfo.input_price) }} | Output: {{ formatPrice(selectedModelInfo.output_price) }} pro 1K Token
                </p>
              </div>
              <div class="text-2xl">
                {{ getProviderIcon(defaultSettings.provider) }}
              </div>
            </div>
          </div>

          <!-- Save Button -->
          <div class="mt-4 flex justify-end">
            <button
              @click="saveDefaultSettings"
              :disabled="savingSettings"
              class="px-6 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity flex items-center gap-2"
            >
              <span v-if="savingSettings" class="animate-spin">&#x23F3;</span>
              <span>{{ savingSettings ? 'Speichert...' : 'Einstellungen speichern' }}</span>
            </button>
          </div>

          <!-- Settings Result -->
          <div
            v-if="settingsResult"
            :class="[
              'mt-3 p-3 rounded-lg text-sm',
              settingsResult.success
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            ]"
          >
            {{ settingsResult.message }}
          </div>
        </div>
      </div>

      <!-- Available Models Overview (Compact) -->
      <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden">
        <div class="px-6 py-4 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div>
              <h3 class="text-lg font-bold text-[var(--color-text-primary)]">
                Verfuegbare Modelle
              </h3>
              <p class="text-sm text-[var(--color-text-secondary)]">
                {{ totalModelCount }} Modelle von {{ Object.keys(availableModels).length }} Providern
              </p>
            </div>
            <!-- Provider Badges -->
            <div class="flex gap-2 flex-wrap">
              <span
                v-for="(providerData, providerName) in availableModels"
                :key="providerName"
                class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-[var(--color-bg)] border border-[var(--color-border)]"
              >
                <span>{{ getProviderIcon(providerName as string) }}</span>
                <span class="text-[var(--color-text-secondary)]">{{ providerData.models.length }}</span>
              </span>
            </div>
          </div>
          <button
            @click="openModelSelector"
            class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors flex items-center gap-2"
          >
            <span>&#x1F50D;</span>
            <span>Model Selector</span>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useWindowStore } from '@/store/window.store'

// Window store for opening Model Selector
const windowStore = useWindowStore()

// ============================================================================
// Types
// ============================================================================

interface AIProvider {
  provider_id: number
  name: string
  display_name: string
  provider_type: string
  base_url: string | null
  api_version: string | null
  active: boolean
  priority: number
  rate_limit_per_minute: number
  config: Record<string, unknown> | null
  last_validated: string | null
  has_api_key: boolean
}

interface TestResult {
  success: boolean
  message: string
  response_time?: number
}

interface AIModel {
  name: string
  input_price: number
  output_price: number
}

interface ProviderModels {
  display_name: string
  models: AIModel[]
}

interface SettingsResult {
  success: boolean
  message: string
}

// ============================================================================
// State
// ============================================================================

const providers = ref<AIProvider[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

// API Key management
const apiKeys = ref<Record<number, string>>({})
const showApiKey = ref<Record<number, boolean>>({})
const savingKey = ref<Record<number, boolean>>({})
const testingKey = ref<Record<number, boolean>>({})
const deletingKey = ref<Record<number, boolean>>({})
const testResults = ref<Record<number, TestResult>>({})

// Model selection
const availableModels = ref<Record<string, ProviderModels>>({})
const defaultSettings = ref({
  provider: 'openai',
  model: 'gpt-4o-mini'
})
const savingSettings = ref(false)
const settingsResult = ref<SettingsResult | null>(null)

// ============================================================================
// Computed
// ============================================================================

const activeProviders = computed(() => {
  return providers.value.filter(p => p.active).length
})

const configuredProviders = computed(() => {
  return providers.value.filter(p => p.has_api_key).length
})

const totalModelCount = computed(() => {
  return Object.values(availableModels.value).reduce((sum, p) => sum + p.models.length, 0)
})

// Get models for currently selected provider
const currentProviderModels = computed(() => {
  const provider = defaultSettings.value.provider
  return availableModels.value[provider]?.models || []
})

// Get info for selected model
const selectedModelInfo = computed(() => {
  const model = defaultSettings.value.model
  return currentProviderModels.value.find(m => m.name === model) || null
})

// ============================================================================
// Methods
// ============================================================================

const getProviderIcon = (name: string): string => {
  const icons: Record<string, string> = {
    'openai': '\u{1F7E2}',      // Green circle for OpenAI
    'anthropic': '\u{1F7E0}',   // Orange circle for Anthropic
    'google': '\u{1F535}',      // Blue circle for Google
    'deepl': '\u{1F30D}',       // Globe for DeepL
  }
  return icons[name] || '\u{1F916}'  // Robot as default
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString('de-DE')
}

const toggleShowApiKey = (providerId: number) => {
  showApiKey.value[providerId] = !showApiKey.value[providerId]
}

const loadProviders = async () => {
  loading.value = true
  error.value = null

  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get('/api/v1/admin/ai/providers?include_inactive=true', {
      headers: { Authorization: `Bearer ${token}` }
    })

    if (response.data.success) {
      providers.value = response.data.data
      // Initialize state objects
      providers.value.forEach(p => {
        apiKeys.value[p.provider_id] = ''
        showApiKey.value[p.provider_id] = false
        savingKey.value[p.provider_id] = false
        testingKey.value[p.provider_id] = false
        deletingKey.value[p.provider_id] = false
      })
    } else {
      error.value = response.data.error || 'Fehler beim Laden der Provider'
    }
  } catch (err: unknown) {
    console.error('Error loading providers:', err)
    if (axios.isAxiosError(err)) {
      error.value = err.response?.data?.error || 'Netzwerkfehler beim Laden der Provider'
    } else {
      error.value = 'Unbekannter Fehler beim Laden der Provider'
    }
  } finally {
    loading.value = false
  }
}

const loadModels = async () => {
  try {
    const token = localStorage.getItem('access_token')
    // Use /grouped endpoint for provider-grouped format
    const response = await axios.get('/api/v1/admin/ai/models/grouped', {
      headers: { Authorization: `Bearer ${token}` }
    })

    if (response.data.success) {
      availableModels.value = response.data.data
    }
  } catch (err) {
    console.error('Error loading models:', err)
  }
}

const loadSettings = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get('/api/v1/admin/ai/settings', {
      headers: { Authorization: `Bearer ${token}` }
    })

    if (response.data.success) {
      defaultSettings.value.provider = response.data.data.default_provider || 'openai'
      defaultSettings.value.model = response.data.data.default_model || 'gpt-4o-mini'
    }
  } catch (err) {
    console.error('Error loading settings:', err)
  }
}

const onProviderChange = () => {
  // Reset model to first available when provider changes
  const models = currentProviderModels.value
  if (models.length > 0) {
    defaultSettings.value.model = models[0].name
  }
}

const formatPrice = (price: number | string | null | undefined): string => {
  const numPrice = Number(price)
  if (price == null || isNaN(numPrice) || numPrice === 0) {
    return '0.000'
  }
  if (numPrice < 0.001) {
    return `${(numPrice * 1000).toFixed(3)}m`
  }
  return `${numPrice.toFixed(4)}`
}

/**
 * Open Model Selector Window (Phase C3.1)
 * Opens a draggable window with all available AI models
 */
const openModelSelector = () => {
  windowStore.openWindow({
    type: 'admin-model-selector',
    title: 'AI Model Selector',
    icon: '🤖',
    size: { width: 700, height: 600 },
    payload: {
      scope: 'global'
    }
  })
}

const saveDefaultSettings = async () => {
  savingSettings.value = true
  settingsResult.value = null

  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.put(
      '/api/v1/admin/ai/settings',
      {
        default_provider: defaultSettings.value.provider,
        default_model: defaultSettings.value.model
      },
      { headers: { Authorization: `Bearer ${token}` } }
    )

    if (response.data.success) {
      settingsResult.value = {
        success: true,
        message: 'Einstellungen erfolgreich gespeichert'
      }
    } else {
      settingsResult.value = {
        success: false,
        message: response.data.error || 'Fehler beim Speichern'
      }
    }
  } catch (err: unknown) {
    console.error('Error saving settings:', err)
    settingsResult.value = {
      success: false,
      message: axios.isAxiosError(err)
        ? (err.response?.data?.error || 'Netzwerkfehler')
        : 'Unbekannter Fehler'
    }
  } finally {
    savingSettings.value = false
  }
}

const saveApiKey = async (provider: AIProvider) => {
  const key = apiKeys.value[provider.provider_id]
  if (!key) return

  savingKey.value[provider.provider_id] = true
  testResults.value[provider.provider_id] = undefined as unknown as TestResult

  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.put(
      `/api/v1/admin/ai/providers/${provider.provider_id}/api-key`,
      { api_key: key },
      { headers: { Authorization: `Bearer ${token}` } }
    )

    if (response.data.success) {
      // Update local state
      const idx = providers.value.findIndex(p => p.provider_id === provider.provider_id)
      if (idx !== -1) {
        providers.value[idx].has_api_key = true
      }
      apiKeys.value[provider.provider_id] = ''
      testResults.value[provider.provider_id] = {
        success: true,
        message: 'API-Key erfolgreich gespeichert'
      }
    } else {
      testResults.value[provider.provider_id] = {
        success: false,
        message: response.data.error || 'Fehler beim Speichern'
      }
    }
  } catch (err: unknown) {
    console.error('Error saving API key:', err)
    testResults.value[provider.provider_id] = {
      success: false,
      message: axios.isAxiosError(err)
        ? (err.response?.data?.error || 'Netzwerkfehler')
        : 'Unbekannter Fehler'
    }
  } finally {
    savingKey.value[provider.provider_id] = false
  }
}

const testApiKey = async (provider: AIProvider) => {
  testingKey.value[provider.provider_id] = true
  testResults.value[provider.provider_id] = undefined as unknown as TestResult

  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.post(
      `/api/v1/admin/ai/providers/${provider.provider_id}/test`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    )

    testResults.value[provider.provider_id] = {
      success: response.data.success,
      message: response.data.success
        ? 'Verbindung erfolgreich!'
        : (response.data.error || 'Verbindung fehlgeschlagen'),
      response_time: response.data.data?.response_time_ms
    }
  } catch (err: unknown) {
    console.error('Error testing API key:', err)
    testResults.value[provider.provider_id] = {
      success: false,
      message: axios.isAxiosError(err)
        ? (err.response?.data?.error || 'Netzwerkfehler beim Testen')
        : 'Unbekannter Fehler'
    }
  } finally {
    testingKey.value[provider.provider_id] = false
  }
}

const deleteApiKey = async (provider: AIProvider) => {
  if (!confirm(`API-Key fuer ${provider.display_name} wirklich entfernen?`)) {
    return
  }

  deletingKey.value[provider.provider_id] = true

  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.delete(
      `/api/v1/admin/ai/providers/${provider.provider_id}/api-key`,
      { headers: { Authorization: `Bearer ${token}` } }
    )

    if (response.data.success) {
      // Update local state
      const idx = providers.value.findIndex(p => p.provider_id === provider.provider_id)
      if (idx !== -1) {
        providers.value[idx].has_api_key = false
        providers.value[idx].active = false
      }
      testResults.value[provider.provider_id] = {
        success: true,
        message: 'API-Key erfolgreich entfernt'
      }
    }
  } catch (err: unknown) {
    console.error('Error deleting API key:', err)
    testResults.value[provider.provider_id] = {
      success: false,
      message: axios.isAxiosError(err)
        ? (err.response?.data?.error || 'Fehler beim Entfernen')
        : 'Unbekannter Fehler'
    }
  } finally {
    deletingKey.value[provider.provider_id] = false
  }
}

const toggleActive = async (provider: AIProvider) => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.patch(
      `/api/v1/admin/ai/providers/${provider.provider_id}`,
      { active: !provider.active },
      { headers: { Authorization: `Bearer ${token}` } }
    )

    if (response.data.success) {
      const idx = providers.value.findIndex(p => p.provider_id === provider.provider_id)
      if (idx !== -1) {
        providers.value[idx].active = !provider.active
      }
    }
  } catch (err) {
    console.error('Error toggling active:', err)
  }
}

const updatePriority = async (provider: AIProvider, event: Event) => {
  const target = event.target as HTMLInputElement
  const priority = parseInt(target.value, 10)

  try {
    const token = localStorage.getItem('access_token')
    await axios.patch(
      `/api/v1/admin/ai/providers/${provider.provider_id}`,
      { priority },
      { headers: { Authorization: `Bearer ${token}` } }
    )

    const idx = providers.value.findIndex(p => p.provider_id === provider.provider_id)
    if (idx !== -1) {
      providers.value[idx].priority = priority
    }
  } catch (err) {
    console.error('Error updating priority:', err)
  }
}

const updateRateLimit = async (provider: AIProvider, event: Event) => {
  const target = event.target as HTMLInputElement
  const rateLimit = parseInt(target.value, 10)

  try {
    const token = localStorage.getItem('access_token')
    await axios.patch(
      `/api/v1/admin/ai/providers/${provider.provider_id}`,
      { rate_limit_per_minute: rateLimit },
      { headers: { Authorization: `Bearer ${token}` } }
    )

    const idx = providers.value.findIndex(p => p.provider_id === provider.provider_id)
    if (idx !== -1) {
      providers.value[idx].rate_limit_per_minute = rateLimit
    }
  } catch (err) {
    console.error('Error updating rate limit:', err)
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  await Promise.all([
    loadProviders(),
    loadModels(),
    loadSettings()
  ])
})
</script>
