/**
 * Composable for managing AI provider settings.
 *
 * Handles loading, saving, testing, and deleting provider API keys,
 * as well as model listing and provider configuration.
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

import type {
  AIProvider,
  TestResult,
  ProviderModels,
} from '../types'

export function useAISettingsManager() {
  const { t } = useI18n()

  // ============================================================================
  // State
  // ============================================================================

  const providers = ref<AIProvider[]>([])
  const loading = ref(true)
  const error = ref<string | null>(null)

  const apiKeys = ref<Record<number, string>>({})
  const showApiKey = ref<Record<number, boolean>>({})
  const savingKey = ref<Record<number, boolean>>({})
  const testingKey = ref<Record<number, boolean>>({})
  const deletingKey = ref<Record<number, boolean>>({})
  const testResults = ref<Record<number, TestResult>>({})

  const availableModels = ref<Record<string, ProviderModels>>({})
  const syncingModels = ref(false)
  const syncResult = ref<{ success: boolean; message: string } | null>(null)

  // ============================================================================
  // Computed
  // ============================================================================

  const activeProviders = computed((): number => {
    return providers.value.filter(p => p.active).length
  })

  const configuredProviders = computed((): number => {
    return providers.value.filter(p => p.has_api_key).length
  })

  const totalModelCount = computed((): number => {
    return Object.values(availableModels.value).reduce(
      (sum, p) => sum + p.models.length,
      0
    )
  })

  // ============================================================================
  // Helpers
  // ============================================================================

  function getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem('access_token')
    return { Authorization: `Bearer ${token}` }
  }

  function extractAxiosError(err: unknown, fallbackKey: string): string {
    if (axios.isAxiosError(err)) {
      const errData = err.response?.data?.error
      return typeof errData === 'string' ? errData : (errData?.code || t(fallbackKey))
    }
    return t(fallbackKey)
  }

  // ============================================================================
  // Load operations
  // ============================================================================

  async function loadProviders(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const response = await axios.get(
        '/api/v1/panel/settings/ai/providers?include_inactive=true',
        { headers: getAuthHeaders() }
      )

      if (response.data.success) {
        providers.value = response.data.data.providers || []
        for (const p of providers.value) {
          apiKeys.value[p.provider_id] = ''
          showApiKey.value[p.provider_id] = false
          savingKey.value[p.provider_id] = false
          testingKey.value[p.provider_id] = false
          deletingKey.value[p.provider_id] = false
        }
      } else {
        error.value = response.data.error || t('panel.aiSettingsPage.messages.loadError')
      }
    } catch (err: unknown) {
      console.error('Error loading providers:', err)
      error.value = extractAxiosError(err, 'panel.aiSettingsPage.messages.networkError')
    } finally {
      loading.value = false
    }
  }

  async function loadModels(): Promise<void> {
    try {
      const response = await axios.get(
        '/api/v1/panel/settings/ai/models?include_inactive=true',
        { headers: getAuthHeaders() }
      )

      if (response.data.success) {
        const models = response.data.data.models || []
        const grouped: Record<string, ProviderModels> = {}

        for (const model of models) {
          const providerName = model.provider_name || model.provider_id || 'unknown'
          if (!grouped[providerName]) {
            grouped[providerName] = {
              display_name: model.provider_display_name || providerName,
              models: [],
            }
          }
          grouped[providerName].models.push({
            model_id: model.model_id,
            name: model.model_name || model.name,
            input_price: model.input_cost_per_1k || model.input_price || 0,
            output_price: model.output_cost_per_1k || model.output_price || 0,
          })
        }

        availableModels.value = grouped
      }
    } catch (err) {
      console.error('Error loading models:', err)
    }
  }

  // ============================================================================
  // API key operations
  // ============================================================================

  async function saveApiKey(provider: AIProvider): Promise<void> {
    const key = apiKeys.value[provider.provider_id]
    if (!key) return

    savingKey.value[provider.provider_id] = true
    testResults.value[provider.provider_id] = undefined as unknown as TestResult

    try {
      const response = await axios.put(
        `/api/v1/panel/settings/ai/providers/${provider.provider_id}/api-key`,
        { api_key: key },
        { headers: getAuthHeaders() }
      )

      if (response.data.success) {
        const idx = providers.value.findIndex(p => p.provider_id === provider.provider_id)
        if (idx !== -1) {
          providers.value[idx].has_api_key = true
        }
        apiKeys.value[provider.provider_id] = ''
        testResults.value[provider.provider_id] = {
          success: true,
          message: t('panel.aiSettingsPage.messages.apiKeySaved'),
        }
      } else {
        testResults.value[provider.provider_id] = {
          success: false,
          message: response.data.error || t('panel.aiSettingsPage.messages.apiKeySaveError'),
        }
      }
    } catch (err: unknown) {
      console.error('Error saving API key:', err)
      testResults.value[provider.provider_id] = {
        success: false,
        message: extractAxiosError(err, 'panel.aiSettingsPage.messages.unknownErrorGeneric'),
      }
    } finally {
      savingKey.value[provider.provider_id] = false
    }
  }

  async function testApiKey(provider: AIProvider): Promise<void> {
    testingKey.value[provider.provider_id] = true
    testResults.value[provider.provider_id] = undefined as unknown as TestResult

    try {
      const response = await axios.post(
        `/api/v1/panel/settings/ai/providers/${provider.provider_id}/test`,
        {},
        { headers: getAuthHeaders() }
      )

      testResults.value[provider.provider_id] = {
        success: response.data.success,
        message: response.data.success
          ? t('panel.aiSettingsPage.messages.connectionSuccess')
          : (response.data.data?.error || response.data.message || t('panel.aiSettingsPage.messages.connectionFailed')),
        response_time: response.data.data?.test_results?.response_time_ms,
      }
    } catch (err: unknown) {
      console.error('Error testing API key:', err)
      testResults.value[provider.provider_id] = {
        success: false,
        message: extractAxiosError(err, 'panel.aiSettingsPage.messages.unknownErrorGeneric'),
      }
    } finally {
      testingKey.value[provider.provider_id] = false
    }
  }

  async function deleteApiKey(provider: AIProvider): Promise<void> {
    if (!confirm(t('panel.aiSettingsPage.messages.confirmRemove', { provider: provider.display_name }))) {
      return
    }

    deletingKey.value[provider.provider_id] = true

    try {
      const response = await axios.delete(
        `/api/v1/panel/settings/ai/providers/${provider.provider_id}/api-key`,
        { headers: getAuthHeaders() }
      )

      if (response.data.success) {
        const idx = providers.value.findIndex(p => p.provider_id === provider.provider_id)
        if (idx !== -1) {
          providers.value[idx].has_api_key = false
          providers.value[idx].active = false
        }
        testResults.value[provider.provider_id] = {
          success: true,
          message: t('panel.aiSettingsPage.messages.apiKeyRemoved'),
        }
      }
    } catch (err: unknown) {
      console.error('Error deleting API key:', err)
      testResults.value[provider.provider_id] = {
        success: false,
        message: extractAxiosError(err, 'panel.aiSettingsPage.messages.unknownErrorGeneric'),
      }
    } finally {
      deletingKey.value[provider.provider_id] = false
    }
  }

  // ============================================================================
  // Provider settings operations
  // ============================================================================

  async function toggleActive(provider: AIProvider): Promise<void> {
    try {
      const response = await axios.put(
        `/api/v1/panel/settings/ai/providers/${provider.provider_id}`,
        { active: !provider.active },
        { headers: getAuthHeaders() }
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

  async function updatePriority(provider: AIProvider, event: Event): Promise<void> {
    const target = event.target as HTMLInputElement
    const priority = parseInt(target.value, 10)

    try {
      await axios.put(
        `/api/v1/panel/settings/ai/providers/${provider.provider_id}`,
        { priority },
        { headers: getAuthHeaders() }
      )

      const idx = providers.value.findIndex(p => p.provider_id === provider.provider_id)
      if (idx !== -1) {
        providers.value[idx].priority = priority
      }
    } catch (err) {
      console.error('Error updating priority:', err)
    }
  }

  async function updateRateLimit(provider: AIProvider, event: Event): Promise<void> {
    const target = event.target as HTMLInputElement
    const rateLimit = parseInt(target.value, 10)

    try {
      await axios.put(
        `/api/v1/panel/settings/ai/providers/${provider.provider_id}`,
        { rate_limit_per_minute: rateLimit },
        { headers: getAuthHeaders() }
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
  // Formatting helpers
  // ============================================================================

  function getProviderIcon(name: string): string {
    const icons: Record<string, string> = {
      'openai': '\u{1F7E2}',
      'anthropic': '\u{1F7E0}',
      'google': '\u{1F535}',
      'deepl': '\u{1F30D}',
    }
    return icons[name] || '\u{1F916}'
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString('de-DE')
  }

  function formatPrice(price: number | string | null | undefined): string {
    const numPrice = Number(price)
    if (price == null || isNaN(numPrice) || numPrice === 0) {
      return '0.000'
    }
    if (numPrice < 0.001) {
      return `${(numPrice * 1000).toFixed(3)}m`
    }
    return `${numPrice.toFixed(4)}`
  }

  function toggleShowApiKey(providerId: number): void {
    showApiKey.value[providerId] = !showApiKey.value[providerId]
  }

  // ============================================================================
  // Init
  // ============================================================================

  async function syncModelsFromProviders(): Promise<void> {
    syncingModels.value = true
    syncResult.value = null

    try {
      const configuredProvidersList = providers.value.filter(p => p.has_api_key && p.active)

      if (configuredProvidersList.length === 0) {
        syncResult.value = {
          success: false,
          message: t('panel.aiSettingsPage.sync.noConfiguredProviders'),
        }
        return
      }

      let totalAdded = 0
      let totalUpdated = 0
      let totalDeactivated = 0
      const errors: string[] = []

      for (const provider of configuredProvidersList) {
        try {
          const response = await axios.post(
            `/api/v1/panel/settings/ai/models/sync/${provider.provider_id}`,
            {},
            { headers: getAuthHeaders() }
          )

          if (response.data.success) {
            totalAdded += response.data.data?.models_added || 0
            totalUpdated += response.data.data?.models_updated || 0
            totalDeactivated += response.data.data?.models_deactivated || 0
          } else {
            errors.push(`${provider.display_name}: ${response.data.message || 'Sync failed'}`)
          }
        } catch (err: unknown) {
          errors.push(`${provider.display_name}: ${extractAxiosError(err, 'panel.aiSettingsPage.sync.syncFailed')}`)
        }
      }

      // Reload models after sync
      await loadModels()

      const summary = `${totalAdded} ${t('panel.aiSettingsPage.sync.added')}, ${totalUpdated} ${t('panel.aiSettingsPage.sync.updated')}, ${totalDeactivated} ${t('panel.aiSettingsPage.sync.deactivated')}`
      syncResult.value = {
        success: errors.length === 0,
        message: errors.length > 0
          ? `${summary}. ${t('panel.aiSettingsPage.sync.errors')}: ${errors.join('; ')}`
          : summary,
      }
    } catch (err: unknown) {
      console.error('Error syncing models:', err)
      syncResult.value = {
        success: false,
        message: extractAxiosError(err, 'panel.aiSettingsPage.sync.syncFailed'),
      }
    } finally {
      syncingModels.value = false
    }
  }

  async function initializeAll(): Promise<void> {
    await Promise.all([loadProviders(), loadModels()])
  }

  return {
    // State
    providers,
    loading,
    error,
    apiKeys,
    showApiKey,
    savingKey,
    testingKey,
    deletingKey,
    testResults,
    availableModels,
    syncingModels,
    syncResult,

    // Computed
    activeProviders,
    configuredProviders,
    totalModelCount,

    // Methods
    loadProviders,
    saveApiKey,
    testApiKey,
    deleteApiKey,
    toggleActive,
    updatePriority,
    updateRateLimit,
    getProviderIcon,
    formatDate,
    formatPrice,
    toggleShowApiKey,
    syncModelsFromProviders,
    initializeAll,
  }
}
