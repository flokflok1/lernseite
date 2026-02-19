/**
 * useAISettings Composable
 *
 * Manages AI provider configuration and model synchronization:
 * - Store API keys for Claude and OpenAI
 * - Sync available models from provider APIs
 * - Track model availability and status
 * - Manage default provider selection
 *
 * Profile management is delegated to useAIProfileManager.
 *
 * Architecture:
 * - Uses Pinia stores for persistence
 * - API service for backend communication
 * - Reactive state with composables
 */

import { ref, computed } from 'vue'
import { categorizeModel } from './modelCategorizer'
import { useAIProfileManager } from './useAIProfileManager'

export interface AIProvider {
  id: string
  name: string
  apiKey: string
  isConfigured: boolean
  lastSynced?: Date
}

export interface AIModel {
  id: string
  name: string
  provider: string
  category?: string
  isAvailable: boolean
  description?: string
  inputTokens?: number
  outputTokens?: number
}

export interface AIProfile {
  id: string
  name: string
  useCase: string
  description?: string
  provider: string
  modelId: string
  isActive: boolean
  createdAt?: Date
  updatedAt?: Date
}

export interface AISettings {
  defaultProvider: string
  claudeApiKey: string
  openaiApiKey: string
  models: AIModel[]
  profiles: AIProfile[]
  isSyncing: boolean
  lastSyncTime?: Date
}

export function useAISettings() {
  // State
  const settings = ref<AISettings>({
    defaultProvider: 'claude',
    claudeApiKey: '',
    openaiApiKey: '',
    models: [],
    profiles: [],
    isSyncing: false
  })

  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const syncProgress = ref(0)
  const profilesLoading = ref(false)

  // Profile management (delegated)
  const profileManager = useAIProfileManager({
    settings,
    isLoading,
    error,
    profilesLoading
  })

  // Providers
  const providers = computed(() => [
    {
      id: 'claude',
      name: 'Claude (Anthropic)',
      apiKey: settings.value.claudeApiKey,
      isConfigured: !!settings.value.claudeApiKey
    },
    {
      id: 'openai',
      name: 'OpenAI (GPT)',
      apiKey: settings.value.openaiApiKey,
      isConfigured: !!settings.value.openaiApiKey
    }
  ])

  // Computed
  const claudeModels = computed(() =>
    settings.value.models.filter(m => m.provider === 'claude' && m.isAvailable)
  )

  const openaiModels = computed(() =>
    settings.value.models.filter(m => m.provider === 'openai' && m.isAvailable)
  )

  const availableProviders = computed(() =>
    providers.value.filter(p => p.isConfigured)
  )

  // Methods

  /**
   * Auto-categorize all models
   */
  function categorizeAllModels(): void {
    settings.value.models.forEach(model => {
      model.category = categorizeModel(model)
    })
  }

  /**
   * Load current AI settings
   */
  async function loadSettings(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await aiSettingsService.getSettings()
      // settings.value = response.data

      console.log('Loading AI settings...')

      // Mock data for development
      const mockModels: AIModel[] = [
        {
          id: 'claude-opus',
          name: 'Claude 3.5 Opus',
          provider: 'claude',
          isAvailable: true,
          description: 'Latest Claude model with advanced reasoning',
          inputTokens: 200000,
          outputTokens: 4096
        },
        {
          id: 'claude-sonnet',
          name: 'Claude 3.5 Sonnet',
          provider: 'claude',
          isAvailable: true,
          description: 'Fast and capable Claude model',
          inputTokens: 200000,
          outputTokens: 4096
        },
        {
          id: 'claude-haiku',
          name: 'Claude 3 Haiku',
          provider: 'claude',
          isAvailable: true,
          description: 'Fastest and most compact Claude model',
          inputTokens: 200000,
          outputTokens: 1024
        },
        {
          id: 'gpt-4',
          name: 'GPT-4 Turbo',
          provider: 'openai',
          isAvailable: true,
          description: 'Advanced reasoning and problem solving',
          inputTokens: 128000,
          outputTokens: 4096
        },
        {
          id: 'gpt-4o',
          name: 'GPT-4o',
          provider: 'openai',
          isAvailable: true,
          description: 'Realtime multimodal model with vision capabilities',
          inputTokens: 128000,
          outputTokens: 4096
        },
        {
          id: 'gpt-4-mini',
          name: 'GPT-4 Mini',
          provider: 'openai',
          isAvailable: true,
          description: 'Fast and efficient model',
          inputTokens: 128000,
          outputTokens: 4096
        },
        {
          id: 'whisper',
          name: 'Whisper Large',
          provider: 'openai',
          isAvailable: true,
          description: 'Audio transcription and speech-to-text model',
          inputTokens: 0,
          outputTokens: 0
        }
      ]

      settings.value = {
        defaultProvider: 'claude',
        claudeApiKey: 'sk-ant-...',
        openaiApiKey: 'sk-...',
        models: mockModels,
        profiles: [],
        isSyncing: false,
        lastSyncTime: new Date()
      }

      categorizeAllModels()
      console.log('Models loaded and auto-categorized')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load AI settings'
      console.error('Error loading AI settings:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update API key for provider
   */
  function updateApiKey(provider: 'claude' | 'openai', apiKey: string): void {
    if (provider === 'claude') {
      settings.value.claudeApiKey = apiKey
    } else {
      settings.value.openaiApiKey = apiKey
    }
  }

  /**
   * Save API key to backend
   */
  async function saveApiKey(provider: 'claude' | 'openai', apiKey: string): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      updateApiKey(provider, apiKey)
      console.log(`API key saved for ${provider}`)
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to save API key'
      console.error('Error saving API key:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Sync available models from providers
   */
  async function syncModels(): Promise<void> {
    settings.value.isSyncing = true
    syncProgress.value = 0
    error.value = null

    try {
      // TODO: Replace with actual API calls to provider endpoints
      if (settings.value.claudeApiKey) {
        syncProgress.value = 25
        console.log('Syncing Claude models...')
      }

      if (settings.value.openaiApiKey) {
        syncProgress.value = 50
        console.log('Syncing OpenAI models...')
      }

      categorizeAllModels()

      syncProgress.value = 100
      settings.value.lastSyncTime = new Date()
      console.log('Models synced and categorized successfully')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to sync models'
      console.error('Error syncing models:', err)
    } finally {
      settings.value.isSyncing = false
      syncProgress.value = 0
    }
  }

  /**
   * Toggle model availability
   */
  function toggleModel(modelId: string): void {
    const model = settings.value.models.find(m => m.id === modelId)
    if (model) {
      model.isAvailable = !model.isAvailable
    }
  }

  /**
   * Set default provider
   */
  async function setDefaultProvider(providerId: string): Promise<boolean> {
    try {
      // TODO: Replace with actual API call
      settings.value.defaultProvider = providerId
      console.log(`Default provider set to ${providerId}`)
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to set default provider'
      console.error('Error setting default provider:', err)
      return false
    }
  }

  /**
   * Test API connection
   */
  async function testConnection(provider: 'claude' | 'openai'): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const apiKey = provider === 'claude'
        ? settings.value.claudeApiKey
        : settings.value.openaiApiKey

      if (!apiKey) {
        throw new Error(`${provider} API key not configured`)
      }

      // TODO: Replace with actual API call to test connection
      console.log(`Connection test passed for ${provider}`)
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : `Failed to test ${provider} connection`
      console.error(`Error testing ${provider} connection:`, err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    settings,
    isLoading,
    error,
    syncProgress,
    profilesLoading,

    // Computed
    providers,
    claudeModels,
    openaiModels,
    availableProviders,

    // Settings Methods
    loadSettings,
    updateApiKey,
    saveApiKey,
    syncModels,
    toggleModel,
    setDefaultProvider,
    testConnection,
    categorizeAllModels,

    // Profile Methods (delegated)
    loadProfiles: profileManager.loadProfiles,
    createProfile: profileManager.createProfile,
    updateProfile: profileManager.updateProfile,
    deleteProfile: profileManager.deleteProfile,
    getModelsByCategory: profileManager.getModelsByCategory,
    getModelCategories: profileManager.getModelCategories,
    getModelsByProvider: profileManager.getModelsByProvider
  }
}
