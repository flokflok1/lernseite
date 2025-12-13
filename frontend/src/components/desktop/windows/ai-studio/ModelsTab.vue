<!--
  Models Tab - AI Model Configuration (Production-Ready)

  Features:
  - KI-Modelle aus der Datenbank laden
  - Modell-Routing pro Kategorie
  - API-Keys verwalten und testen
  - Model Sync via API
  - Keine Demo-Daten!
-->

<template>
  <div class="models-tab p-6">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-20">
      <div class="animate-spin text-4xl">⏳</div>
      <span class="ml-3 text-[var(--color-text-secondary)]">Lade Modelle...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="loadError" class="p-6 bg-red-50 dark:bg-red-900/20 rounded-xl text-center">
      <div class="text-4xl mb-3">❌</div>
      <h3 class="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">Fehler beim Laden</h3>
      <p class="text-red-500 dark:text-red-300 mb-4">{{ loadError }}</p>
      <button @click="loadData" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
        Erneut versuchen
      </button>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-xl font-bold text-[var(--color-text-primary)]">Modell-Konfiguration</h2>
          <p class="text-sm text-[var(--color-text-secondary)] mt-1">
            {{ models.length }} Modelle von {{ providers.length }} Providern
          </p>
        </div>
        <div class="flex gap-2">
          <button
            @click="syncModels(null)"
            :disabled="isSyncing"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            <span :class="{ 'animate-spin': isSyncing }">🔄</span>
            {{ isSyncing ? 'Sync...' : 'Alle synchronisieren' }}
          </button>
          <button
            @click="testAllConnections"
            :disabled="isTesting"
            class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors flex items-center gap-2"
          >
            <span :class="{ 'animate-spin': isTesting }">🔌</span>
            {{ isTesting ? 'Teste...' : 'Verbindungen testen' }}
          </button>
        </div>
      </div>

      <!-- Stats Overview -->
      <div v-if="stats" class="grid grid-cols-5 gap-4 mb-6">
        <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 text-center">
          <div class="text-2xl font-bold text-[var(--color-text-primary)]">{{ stats.total_models || 0 }}</div>
          <div class="text-xs text-[var(--color-text-tertiary)]">Gesamt Modelle</div>
        </div>
        <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 text-center">
          <div class="text-2xl font-bold text-green-600">{{ stats.active_models || 0 }}</div>
          <div class="text-xs text-[var(--color-text-tertiary)]">Aktive Modelle</div>
        </div>
        <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 text-center">
          <div class="text-2xl font-bold text-blue-600">{{ stats.providers || 0 }}</div>
          <div class="text-xs text-[var(--color-text-tertiary)]">Provider</div>
        </div>
        <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 text-center">
          <div class="text-2xl font-bold text-purple-600">{{ stats.categories || 0 }}</div>
          <div class="text-xs text-[var(--color-text-tertiary)]">Kategorien</div>
        </div>
        <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 text-center">
          <div class="text-2xl font-bold text-orange-600">{{ stats.default_models || 0 }}</div>
          <div class="text-xs text-[var(--color-text-tertiary)]">Default Modelle</div>
        </div>
      </div>

      <!-- Sync Result Message -->
      <div v-if="syncResult" class="mb-6 p-4 rounded-xl" :class="syncResult.success ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'">
        <div class="flex items-center gap-2">
          <span>{{ syncResult.success ? '✅' : '❌' }}</span>
          <span :class="syncResult.success ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
            {{ syncResult.message }}
          </span>
        </div>
        <div v-if="syncResult.details" class="mt-2 text-sm text-[var(--color-text-secondary)]">
          Hinzugefügt: {{ syncResult.details.added || 0 }} |
          Aktualisiert: {{ syncResult.details.updated || 0 }} |
          Gesamt: {{ syncResult.details.synced || 0 }}
        </div>
      </div>

      <!-- API Keys Section -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
            API-Schlüssel & Provider
          </h3>
        </div>
        <div class="space-y-3">
          <div
            v-for="provider in providers"
            :key="provider.provider_id"
            class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span
                  class="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                  :class="getProviderStyle(provider.name)"
                >
                  {{ getProviderIcon(provider.name) }}
                </span>
                <div>
                  <h4 class="font-medium text-[var(--color-text-primary)]">{{ provider.display_name }}</h4>
                  <p class="text-xs text-[var(--color-text-tertiary)]">
                    {{ getModelCountForProvider(provider.name) }} Modelle
                    <span v-if="provider.last_validated" class="ml-2">
                      | Validiert: {{ formatDate(provider.last_validated) }}
                    </span>
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <span
                  class="w-3 h-3 rounded-full"
                  :class="provider.has_api_key ? 'bg-green-500' : 'bg-red-500'"
                ></span>
                <span class="text-sm text-[var(--color-text-secondary)]">
                  {{ provider.has_api_key ? 'Konfiguriert' : 'Nicht konfiguriert' }}
                </span>
                <span
                  v-if="provider.active"
                  class="px-2 py-0.5 text-xs bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded"
                >
                  Aktiv
                </span>
              </div>
            </div>
            <div class="mt-3 flex gap-2">
              <input
                v-model="apiKeyInputs[provider.name]"
                type="password"
                class="flex-1 px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-sm font-mono"
                :placeholder="provider.has_api_key ? '••••••••••••••••' : 'API Key eingeben...'"
              />
              <button
                @click="toggleKeyVisibility(provider.name)"
                class="px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-sm hover:bg-[var(--color-surface)] transition-colors"
              >
                {{ visibleKeys[provider.name] ? '🙈' : '👁️' }}
              </button>
              <button
                @click="saveApiKey(provider)"
                :disabled="!apiKeyInputs[provider.name]"
                class="px-3 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 transition-colors disabled:opacity-50"
              >
                💾 Speichern
              </button>
              <button
                @click="testApiKey(provider)"
                :disabled="testingProvider === provider.name"
                class="px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-sm hover:bg-[var(--color-surface)] transition-colors"
              >
                <span :class="{ 'animate-spin': testingProvider === provider.name }">
                  {{ testingProvider === provider.name ? '⏳' : '🔌' }}
                </span>
                Test
              </button>
              <button
                @click="syncModels(provider.name)"
                :disabled="isSyncing"
                class="px-3 py-2 bg-purple-500 text-white rounded-lg text-sm hover:bg-purple-600 transition-colors disabled:opacity-50"
              >
                🔄 Sync
              </button>
            </div>
            <!-- Test Result -->
            <div v-if="testResults[provider.name]" class="mt-2 text-sm" :class="testResults[provider.name].success ? 'text-green-600' : 'text-red-600'">
              {{ testResults[provider.name].message }}
            </div>
          </div>
        </div>
      </div>

      <!-- Category-based Default Model Selection -->
      <div class="mb-8">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide mb-4">
          Default-Modelle pro Kategorie
        </h3>
        <div class="grid grid-cols-3 gap-4">
          <div
            v-for="category in categories"
            :key="category"
            class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4"
          >
            <div class="flex items-center gap-3 mb-3">
              <span
                class="w-10 h-10 rounded-lg flex items-center justify-center text-xl text-white"
                :class="getCategoryStyle(category).bgColor"
              >
                {{ getCategoryStyle(category).emoji }}
              </span>
              <div>
                <h4 class="font-medium text-[var(--color-text-primary)] capitalize">{{ category }}</h4>
                <p class="text-xs text-[var(--color-text-tertiary)]">{{ getCategoryStyle(category).description }}</p>
              </div>
            </div>
            <select
              v-model="defaultModels[category]"
              @change="setDefaultModel(category)"
              class="w-full px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] text-sm"
            >
              <option :value="null">-- Nicht konfiguriert --</option>
              <option
                v-for="model in getModelsForCategory(category)"
                :key="model.model_id"
                :value="model.model_id"
              >
                {{ model.display_name || model.model_name }} ({{ model.provider_name }})
              </option>
            </select>
            <div class="mt-2 flex items-center justify-between text-xs">
              <span class="text-[var(--color-text-tertiary)]">
                {{ getModelsForCategory(category).length }} verfügbar
              </span>
              <span
                v-if="defaultModels[category]"
                class="text-green-500"
              >
                ✓ Konfiguriert
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Available Models -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
            Verfügbare Modelle ({{ filteredModels.length }})
          </h3>
          <div class="flex gap-2">
            <select
              v-model="providerFilter"
              class="px-3 py-1.5 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg"
            >
              <option value="">Alle Provider</option>
              <option v-for="p in providers" :key="p.name" :value="p.name">
                {{ p.display_name }}
              </option>
            </select>
            <select
              v-model="categoryFilter"
              class="px-3 py-1.5 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg"
            >
              <option value="">Alle Kategorien</option>
              <option v-for="c in categories" :key="c" :value="c">
                {{ c }}
              </option>
            </select>
            <input
              v-model="modelSearch"
              type="text"
              placeholder="Suchen..."
              class="px-3 py-1.5 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg w-48"
            />
          </div>
        </div>

        <!-- Model Grid -->
        <div class="grid grid-cols-2 gap-4 max-h-[500px] overflow-y-auto">
          <div
            v-for="model in filteredModels"
            :key="model.model_id"
            class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 hover:border-[var(--color-primary)] transition-colors"
            :class="{ 'border-yellow-500': model.is_default }"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center gap-3">
                <span
                  class="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                  :class="getProviderStyle(model.provider_name)"
                >
                  {{ getProviderIcon(model.provider_name) }}
                </span>
                <div>
                  <h4 class="font-medium text-[var(--color-text-primary)]">{{ model.display_name || model.model_name }}</h4>
                  <p class="text-xs text-[var(--color-text-tertiary)]">{{ model.provider_name }} | {{ model.category }}</p>
                </div>
              </div>
              <div class="flex flex-col gap-1 items-end">
                <span
                  class="px-2 py-1 text-xs rounded-full"
                  :class="model.active
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'"
                >
                  {{ model.active ? 'Aktiv' : 'Inaktiv' }}
                </span>
                <span v-if="model.is_default" class="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
                  ⭐ Default
                </span>
              </div>
            </div>

            <!-- Capabilities -->
            <div class="flex flex-wrap gap-1 mb-3">
              <span v-if="model.supports_vision" class="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 rounded">Vision</span>
              <span v-if="model.supports_functions" class="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 rounded">Functions</span>
              <span class="px-2 py-0.5 text-xs bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] rounded capitalize">{{ model.model_type }}</span>
              <span v-if="model.cost_level" class="px-2 py-0.5 text-xs bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] rounded">{{ model.cost_level }}</span>
            </div>

            <!-- Stats -->
            <div class="grid grid-cols-3 gap-2 text-xs">
              <div class="text-center p-2 bg-[var(--color-surface-secondary)] rounded-lg">
                <div class="text-[var(--color-text-tertiary)]">Input</div>
                <div class="font-medium text-[var(--color-text-primary)]">
                  {{ model.input_price_per_1k ? `$${parseFloat(model.input_price_per_1k).toFixed(4)}/1K` : '-' }}
                </div>
              </div>
              <div class="text-center p-2 bg-[var(--color-surface-secondary)] rounded-lg">
                <div class="text-[var(--color-text-tertiary)]">Output</div>
                <div class="font-medium text-[var(--color-text-primary)]">
                  {{ model.output_price_per_1k ? `$${parseFloat(model.output_price_per_1k).toFixed(4)}/1K` : '-' }}
                </div>
              </div>
              <div class="text-center p-2 bg-[var(--color-surface-secondary)] rounded-lg">
                <div class="text-[var(--color-text-tertiary)]">Context</div>
                <div class="font-medium text-[var(--color-text-primary)]">
                  {{ model.context_window ? formatNumber(model.context_window) : '-' }}
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="mt-3 flex gap-2">
              <button
                @click="toggleModelActive(model)"
                class="flex-1 px-3 py-1.5 text-xs rounded-lg transition-colors"
                :class="model.active
                  ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400'
                  : 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400'"
              >
                {{ model.active ? 'Deaktivieren' : 'Aktivieren' }}
              </button>
              <button
                v-if="!model.is_default && model.active"
                @click="makeDefault(model)"
                class="flex-1 px-3 py-1.5 text-xs bg-yellow-100 text-yellow-700 hover:bg-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 rounded-lg transition-colors"
              >
                Als Default setzen
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredModels.length === 0" class="text-center py-10 text-[var(--color-text-tertiary)]">
          <div class="text-4xl mb-3">🔍</div>
          <p>Keine Modelle gefunden. Versuche einen anderen Filter.</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'

// Types
interface AIProvider {
  provider_id: number
  name: string
  display_name: string
  provider_type: string
  active: boolean
  has_api_key: boolean
  last_validated?: string
  priority: number
}

interface AIModel {
  model_id: number
  provider_id: number
  provider_name: string
  model_name: string
  display_name: string
  model_type: string
  category: string
  description?: string
  cost_level?: string
  speed?: string
  context_window?: number
  max_output_tokens?: number
  supports_vision: boolean
  supports_functions: boolean
  input_price_per_1k?: number
  output_price_per_1k?: number
  active: boolean
  is_default: boolean
}

interface ModelStats {
  total_models: number
  active_models: number
  providers: number
  categories: number
  default_models: number
}

// State
const isLoading = ref(true)
const loadError = ref<string | null>(null)
const isSyncing = ref(false)
const isTesting = ref(false)
const testingProvider = ref<string | null>(null)

const providers = ref<AIProvider[]>([])
const models = ref<AIModel[]>([])
const categories = ref<string[]>([])
const stats = ref<ModelStats | null>(null)

const providerFilter = ref('')
const categoryFilter = ref('')
const modelSearch = ref('')

const apiKeyInputs = ref<Record<string, string>>({})
const visibleKeys = ref<Record<string, boolean>>({})
const testResults = ref<Record<string, { success: boolean; message: string }>>({})
const defaultModels = ref<Record<string, number | null>>({})
const syncResult = ref<{ success: boolean; message: string; details?: any } | null>(null)

// Category styles
const categoryStyles: Record<string, { emoji: string; bgColor: string; description: string }> = {
  chat: { emoji: '💬', bgColor: 'bg-blue-500', description: 'Text-Generierung' },
  audio: { emoji: '🎵', bgColor: 'bg-green-500', description: 'TTS & STT' },
  video: { emoji: '🎬', bgColor: 'bg-red-500', description: 'Video Generation' },
  embedding: { emoji: '📊', bgColor: 'bg-cyan-500', description: 'Vektoren' },
  image: { emoji: '🖼️', bgColor: 'bg-pink-500', description: 'Bild-Generierung' },
  reasoning: { emoji: '🧠', bgColor: 'bg-orange-500', description: 'o1, DeepSeek' },
  realtime: { emoji: '⚡', bgColor: 'bg-yellow-500', description: 'Live-Tutor' },
  moderation: { emoji: '🛡️', bgColor: 'bg-gray-500', description: 'Content Filter' },
  vision: { emoji: '👁️', bgColor: 'bg-indigo-500', description: 'Bild-Analyse' },
  transcription: { emoji: '📝', bgColor: 'bg-teal-500', description: 'Speech-to-Text' },
  translation: { emoji: '🌍', bgColor: 'bg-emerald-500', description: 'Übersetzungen' }
}

// Computed
const filteredModels = computed(() => {
  let result = models.value

  if (providerFilter.value) {
    result = result.filter(m => m.provider_name === providerFilter.value)
  }

  if (categoryFilter.value) {
    result = result.filter(m => m.category === categoryFilter.value)
  }

  if (modelSearch.value) {
    const search = modelSearch.value.toLowerCase()
    result = result.filter(m =>
      (m.model_name?.toLowerCase() || '').includes(search) ||
      (m.display_name?.toLowerCase() || '').includes(search) ||
      (m.provider_name?.toLowerCase() || '').includes(search)
    )
  }

  return result
})

// Methods
function getCategoryStyle(category: string) {
  return categoryStyles[category] || { emoji: '⚙️', bgColor: 'bg-gray-500', description: category }
}

function getProviderIcon(provider: string): string {
  const icons: Record<string, string> = {
    openai: '🤖',
    anthropic: '🧠',
    google: '🔍',
    deepl: '🌍',
    cohere: '🔮',
    huggingface: '🤗'
  }
  return icons[provider?.toLowerCase()] || '⚙️'
}

function getProviderStyle(provider: string): string {
  const styles: Record<string, string> = {
    openai: 'bg-green-100 dark:bg-green-900/30',
    anthropic: 'bg-orange-100 dark:bg-orange-900/30',
    google: 'bg-blue-100 dark:bg-blue-900/30',
    deepl: 'bg-cyan-100 dark:bg-cyan-900/30',
    cohere: 'bg-purple-100 dark:bg-purple-900/30',
    huggingface: 'bg-yellow-100 dark:bg-yellow-900/30'
  }
  return styles[provider?.toLowerCase()] || 'bg-gray-100 dark:bg-gray-900/30'
}

function getModelsForCategory(category: string): AIModel[] {
  return models.value.filter(m => m.category === category && m.active)
}

function getModelCountForProvider(providerName: string): number {
  return models.value.filter(m => m.provider_name === providerName).length
}

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(0)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(0)}K`
  return num.toString()
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function toggleKeyVisibility(providerName: string) {
  visibleKeys.value[providerName] = !visibleKeys.value[providerName]
}

// API Methods
async function loadData() {
  isLoading.value = true
  loadError.value = null

  try {
    // Load providers
    const providersRes = await http.get('/admin/ai/providers')
    if (providersRes.data.success) {
      providers.value = providersRes.data.data.providers || providersRes.data.data || []
    }

    // Load models
    const modelsRes = await http.get('/admin/ai/models', { params: { include_inactive: true } })
    if (modelsRes.data.success) {
      models.value = modelsRes.data.data.models || modelsRes.data.data || []
      categories.value = modelsRes.data.data.categories || [...new Set(models.value.map(m => m.category).filter(Boolean))]
    }

    // Load stats
    const statsRes = await http.get('/admin/ai/models/stats')
    if (statsRes.data.success) {
      stats.value = statsRes.data.data.stats || statsRes.data.data
    }

    // Initialize default models
    for (const category of categories.value) {
      const defaultModel = models.value.find(m => m.category === category && m.is_default)
      defaultModels.value[category] = defaultModel?.model_id || null
    }

  } catch (error: any) {
    console.error('Failed to load AI data:', error)
    loadError.value = error.response?.data?.error?.message || error.message || 'Fehler beim Laden der Daten'
  } finally {
    isLoading.value = false
  }
}

async function syncModels(provider: string | null) {
  isSyncing.value = true
  syncResult.value = null

  try {
    const endpoint = '/admin/ai/models/sync'
    const payload = provider ? { provider } : {}

    const response = await http.post(endpoint, payload)

    if (response.data.success) {
      syncResult.value = {
        success: true,
        message: response.data.message || 'Synchronisation erfolgreich!',
        details: response.data.data
      }
      // Reload data
      await loadData()
    } else {
      syncResult.value = {
        success: false,
        message: response.data.error?.message || 'Synchronisation fehlgeschlagen'
      }
    }
  } catch (error: any) {
    console.error('Sync failed:', error)
    syncResult.value = {
      success: false,
      message: error.response?.data?.error?.message || error.message || 'Synchronisation fehlgeschlagen'
    }
  } finally {
    isSyncing.value = false
  }
}

async function testApiKey(provider: AIProvider) {
  testingProvider.value = provider.name
  testResults.value[provider.name] = { success: false, message: 'Teste...' }

  try {
    const response = await http.get(`/admin/ai/providers/${provider.provider_id}/test`)

    if (response.data.success) {
      testResults.value[provider.name] = {
        success: true,
        message: `✅ Verbindung OK (${response.data.data?.response_time_ms || 0}ms)`
      }
    } else {
      testResults.value[provider.name] = {
        success: false,
        message: `❌ ${response.data.error?.message || 'Test fehlgeschlagen'}`
      }
    }
  } catch (error: any) {
    testResults.value[provider.name] = {
      success: false,
      message: `❌ ${error.response?.data?.error?.message || error.message || 'Verbindung fehlgeschlagen'}`
    }
  } finally {
    testingProvider.value = null
  }
}

async function testAllConnections() {
  isTesting.value = true

  for (const provider of providers.value.filter(p => p.has_api_key)) {
    await testApiKey(provider)
  }

  isTesting.value = false
}

async function saveApiKey(provider: AIProvider) {
  const apiKey = apiKeyInputs.value[provider.name]
  if (!apiKey) return

  try {
    const response = await http.put(`/admin/ai/providers/${provider.provider_id}/api-key`, {
      api_key: apiKey
    })

    if (response.data.success) {
      testResults.value[provider.name] = {
        success: true,
        message: '✅ API-Key gespeichert!'
      }
      apiKeyInputs.value[provider.name] = ''
      // Reload providers
      await loadData()
    } else {
      testResults.value[provider.name] = {
        success: false,
        message: `❌ ${response.data.error?.message || 'Speichern fehlgeschlagen'}`
      }
    }
  } catch (error: any) {
    testResults.value[provider.name] = {
      success: false,
      message: `❌ ${error.response?.data?.error?.message || error.message || 'Speichern fehlgeschlagen'}`
    }
  }
}

async function toggleModelActive(model: AIModel) {
  try {
    const response = await http.put(`/admin/ai/models/${model.model_id}/active`, {
      active: !model.active
    })

    if (response.data.success) {
      model.active = !model.active
    }
  } catch (error: any) {
    console.error('Failed to toggle model:', error)
  }
}

async function makeDefault(model: AIModel) {
  try {
    const response = await http.put(`/admin/ai/models/${model.model_id}/default`)

    if (response.data.success) {
      // Update local state
      models.value.forEach(m => {
        if (m.category === model.category) {
          m.is_default = m.model_id === model.model_id
        }
      })
      defaultModels.value[model.category] = model.model_id
    }
  } catch (error: any) {
    console.error('Failed to set default:', error)
  }
}

async function setDefaultModel(category: string) {
  const modelId = defaultModels.value[category]
  if (!modelId) return

  const model = models.value.find(m => m.model_id === modelId)
  if (model) {
    await makeDefault(model)
  }
}

// Load data on mount
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.models-tab {
  min-height: 400px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}
</style>
