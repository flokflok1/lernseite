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
      <span class="ml-3 text-[var(--color-text-secondary)]">{{ $t('aiEditorModels.loading') }}</span>
    </div>

    <!-- Error State -->
    <div v-else-if="loadError" class="p-6 bg-red-50 dark:bg-red-900/20 rounded-xl text-center">
      <div class="text-4xl mb-3">❌</div>
      <h3 class="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">{{ $t('aiEditorModels.loadError') }}</h3>
      <p class="text-red-500 dark:text-red-300 mb-4">{{ loadError }}</p>
      <button @click="loadData" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
        {{ $t('aiEditorModels.retry') }}
      </button>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Header -->
      <ModelsHeader
        :model-count="models.length"
        :provider-count="providers.length"
        :is-syncing="isSyncing"
        :is-testing="isTesting"
        @sync="syncModels(null)"
        @test-all="testAllConnections"
      />

      <!-- Stats Overview -->
      <StatsOverview :stats="stats" />

      <!-- Sync Result Message -->
      <SyncResultBanner :result="syncResult" />

      <!-- API Keys Section -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
            {{ $t('aiEditorModels.apiKeys') }}
          </h3>
        </div>
        <div class="space-y-3">
          <ProviderRow
            v-for="provider in providers"
            :key="provider.provider_id"
            :provider="provider"
            :model-count="getModelCountForProvider(provider.name)"
            :api-key-input="apiKeyInputs[provider.name] || ''"
            :is-visible="visibleKeys[provider.name] || false"
            :is-testing="testingProvider === provider.name"
            :is-syncing="isSyncing"
            :test-result="testResults[provider.name]"
            :provider-icon="getProviderIcon(provider.name)"
            :provider-style="getProviderStyle(provider.name)"
            @update:api-key-input="apiKeyInputs[provider.name] = $event"
            @toggle-visibility="toggleKeyVisibility(provider.name)"
            @save="saveApiKey(provider)"
            @test="testApiKey(provider)"
            @sync="syncModels(provider.name)"
          />
        </div>
      </div>

      <!-- Category-based Default Model Selection -->
      <div class="mb-8">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide mb-4">
          {{ $t('aiEditorModels.defaultPerCategory') }}
        </h3>
        <div class="grid grid-cols-3 gap-4">
          <CategorySelector
            v-for="category in categories"
            :key="category"
            :category="category"
            :category-style="getCategoryStyle(category)"
            :models="getModelsForCategory(category)"
            :selected-model-id="defaultModels[category]"
            @update:selected-model-id="handleDefaultModelChange(category, $event)"
          />
        </div>
      </div>

      <!-- Available Models -->
      <div class="mb-8">
        <ModelsFilter
          :model-count="filteredModels.length"
          :providers="providers"
          :categories="categories"
          v-model:provider-filter="providerFilter"
          v-model:category-filter="categoryFilter"
          v-model:search="modelSearch"
        />

        <!-- Model Grid -->
        <div class="grid grid-cols-2 gap-4 max-h-[500px] overflow-y-auto">
          <ModelCard
            v-for="model in filteredModels"
            :key="model.model_id"
            :model="model"
            :provider-icon="getProviderIcon(model.provider_name)"
            :provider-style="getProviderStyle(model.provider_name)"
            @toggle-active="toggleModelActive(model)"
            @make-default="makeDefault(model)"
          />
        </div>

        <!-- Empty State -->
        <div v-if="filteredModels.length === 0" class="text-center py-10 text-[var(--color-text-tertiary)]">
          <div class="text-4xl mb-3">🔍</div>
          <p>{{ $t('aiEditorModels.noModelsFound') }}</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'
import { ProviderRow, ModelCard, CategorySelector, StatsOverview, SyncResultBanner, ModelsHeader, ModelsFilter } from '@/presentation/components/panel/admin/ai/settings/models'

const { t } = useI18n()

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

// Category styles - computed for i18n reactivity
const categoryStylesBase: Record<string, { emoji: string; bgColor: string; key: string }> = {
  chat: { emoji: '💬', bgColor: 'bg-blue-500', key: 'catChat' },
  audio: { emoji: '🎵', bgColor: 'bg-green-500', key: 'catAudio' },
  video: { emoji: '🎬', bgColor: 'bg-red-500', key: 'catVideo' },
  embedding: { emoji: '📊', bgColor: 'bg-cyan-500', key: 'catEmbedding' },
  image: { emoji: '🖼️', bgColor: 'bg-pink-500', key: 'catImage' },
  reasoning: { emoji: '🧠', bgColor: 'bg-orange-500', key: 'catReasoning' },
  realtime: { emoji: '⚡', bgColor: 'bg-yellow-500', key: 'catRealtime' },
  moderation: { emoji: '🛡️', bgColor: 'bg-gray-500', key: 'catModeration' },
  vision: { emoji: '👁️', bgColor: 'bg-indigo-500', key: 'catVision' },
  transcription: { emoji: '📝', bgColor: 'bg-teal-500', key: 'catTranscription' },
  translation: { emoji: '🌍', bgColor: 'bg-emerald-500', key: 'catTranslation' }
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
  const base = categoryStylesBase[category]
  if (base) {
    return {
      emoji: base.emoji,
      bgColor: base.bgColor,
      description: t(`aiEditorModels.${base.key}`)
    }
  }
  return { emoji: '⚙️', bgColor: 'bg-gray-500', description: category }
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
    loadError.value = error.response?.data?.error?.message || error.message || t('aiEditorModels.loadFailed')
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
        message: response.data.message || t('aiEditorModels.syncSuccess'),
        details: response.data.data
      }
      // Reload data
      await loadData()
    } else {
      syncResult.value = {
        success: false,
        message: response.data.error?.message || t('aiEditorModels.syncFailed')
      }
    }
  } catch (error: any) {
    console.error('Sync failed:', error)
    syncResult.value = {
      success: false,
      message: error.response?.data?.error?.message || error.message || t('aiEditorModels.syncFailed')
    }
  } finally {
    isSyncing.value = false
  }
}

async function testApiKey(provider: AIProvider) {
  testingProvider.value = provider.name
  testResults.value[provider.name] = { success: false, message: t('aiEditorModels.testing') }

  try {
    const response = await http.get(`/admin/ai/providers/${provider.provider_id}/test`)

    if (response.data.success) {
      testResults.value[provider.name] = {
        success: true,
        message: `✅ ${t('aiEditorModels.connectionOk')} (${response.data.data?.response_time_ms || 0}ms)`
      }
    } else {
      testResults.value[provider.name] = {
        success: false,
        message: `❌ ${response.data.error?.message || t('aiEditorModels.testFailed')}`
      }
    }
  } catch (error: any) {
    testResults.value[provider.name] = {
      success: false,
      message: `❌ ${error.response?.data?.error?.message || error.message || t('aiEditorModels.connectionFailed')}`
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
        message: `✅ ${t('aiEditorModels.apiKeySaved')}`
      }
      apiKeyInputs.value[provider.name] = ''
      // Reload providers
      await loadData()
    } else {
      testResults.value[provider.name] = {
        success: false,
        message: `❌ ${response.data.error?.message || t('aiEditorModels.saveFailed')}`
      }
    }
  } catch (error: any) {
    testResults.value[provider.name] = {
      success: false,
      message: `❌ ${error.response?.data?.error?.message || error.message || t('aiEditorModels.saveFailed')}`
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

function handleDefaultModelChange(category: string, modelId: number | null) {
  defaultModels.value[category] = modelId
  if (modelId) {
    setDefaultModel(category)
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
