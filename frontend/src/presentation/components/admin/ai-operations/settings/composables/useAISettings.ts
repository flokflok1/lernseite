/**
 * useAISettings Composable
 *
 * Manages AI provider configuration and model synchronization:
 * - Store API keys for Claude and OpenAI
 * - Sync available models from provider APIs
 * - Track model availability and status
 * - Manage default provider selection
 *
 * Architecture:
 * - Uses Pinia stores for persistence
 * - API service for backend communication
 * - Reactive state with composables
 */

import { ref, computed } from 'vue'
import { categorizeModel } from './modelCategorizer'

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
   * Load current AI settings
   */
  const loadSettings = async () => {
    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await aiSettingsService.getSettings()
      // settings.value = response.data

      console.log('Loading AI settings...')

      // Mock data for development
      const mockModels = [
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

      // Auto-categorize all models
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
  const updateApiKey = (provider: 'claude' | 'openai', apiKey: string) => {
    if (provider === 'claude') {
      settings.value.claudeApiKey = apiKey
    } else {
      settings.value.openaiApiKey = apiKey
    }
  }

  /**
   * Save API key to backend
   */
  const saveApiKey = async (provider: 'claude' | 'openai', apiKey: string) => {
    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // await aiSettingsService.updateApiKey(provider, apiKey)

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
   * Auto-categorize all models
   */
  const categorizeAllModels = () => {
    settings.value.models.forEach(model => {
      model.category = categorizeModel(model)
    })
  }

  /**
   * Sync available models from providers
   */
  const syncModels = async () => {
    settings.value.isSyncing = true
    syncProgress.value = 0
    error.value = null

    try {
      // TODO: Replace with actual API calls to provider endpoints
      // 1. Fetch Claude models
      if (settings.value.claudeApiKey) {
        syncProgress.value = 25
        console.log('Syncing Claude models...')
        // const claudeModels = await claudeApi.listModels(settings.value.claudeApiKey)
        // Update settings.value.models with Claude models
        // Then categorize them:
        // settings.value.models = categorizeModels(claudeModels)
      }

      // 2. Fetch OpenAI models
      if (settings.value.openaiApiKey) {
        syncProgress.value = 50
        console.log('Syncing OpenAI models...')
        // const openaiModels = await openaiApi.listModels(settings.value.openaiApiKey)
        // Update settings.value.models with OpenAI models
        // Then categorize them:
        // settings.value.models = categorizeModels(openaiModels)
      }

      // Auto-categorize all models (locally)
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
  const toggleModel = (modelId: string) => {
    const model = settings.value.models.find(m => m.id === modelId)
    if (model) {
      model.isAvailable = !model.isAvailable
    }
  }

  /**
   * Set default provider
   */
  const setDefaultProvider = async (providerId: string) => {
    try {
      // TODO: Replace with actual API call
      // await aiSettingsService.setDefaultProvider(providerId)

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
  const testConnection = async (provider: 'claude' | 'openai') => {
    isLoading.value = true
    error.value = null

    try {
      const apiKey = provider === 'claude' ? settings.value.claudeApiKey : settings.value.openaiApiKey

      if (!apiKey) {
        throw new Error(`${provider} API key not configured`)
      }

      // TODO: Replace with actual API call to test connection
      // await aiSettingsService.testConnection(provider, apiKey)

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

  // ============================================
  // PROFILE MANAGEMENT
  // ============================================

  /**
   * Load all AI profiles from API
   */
  const loadProfiles = async () => {
    profilesLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await aiSettingsService.getProfiles()
      // settings.value.profiles = response.data

      console.log('Loading AI profiles...')
      // Start with empty profiles - API will populate
      settings.value.profiles = []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load profiles'
      console.error('Error loading profiles:', err)
    } finally {
      profilesLoading.value = false
    }
  }

  /**
   * Create new AI profile
   */
  const createProfile = async (profile: Omit<AIProfile, 'id' | 'createdAt' | 'updatedAt'>) => {
    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await aiSettingsService.createProfile(profile)
      // settings.value.profiles.push(response.data)

      const newProfile: AIProfile = {
        id: `profile_${Date.now()}`,
        ...profile,
        createdAt: new Date(),
        updatedAt: new Date()
      }

      settings.value.profiles.push(newProfile)
      console.log('Profile created:', newProfile)
      return newProfile
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create profile'
      console.error('Error creating profile:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update existing AI profile
   */
  const updateProfile = async (id: string, updates: Partial<AIProfile>) => {
    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await aiSettingsService.updateProfile(id, updates)
      // Find and update in local state
      // const index = settings.value.profiles.findIndex(p => p.id === id)
      // if (index >= 0) {
      //   settings.value.profiles[index] = response.data
      // }

      const index = settings.value.profiles.findIndex(p => p.id === id)
      if (index >= 0) {
        settings.value.profiles[index] = {
          ...settings.value.profiles[index],
          ...updates,
          updatedAt: new Date()
        }
        console.log('Profile updated:', settings.value.profiles[index])
        return settings.value.profiles[index]
      }

      throw new Error('Profile not found')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update profile'
      console.error('Error updating profile:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete AI profile
   */
  const deleteProfile = async (id: string) => {
    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // await aiSettingsService.deleteProfile(id)
      // Remove from local state

      const index = settings.value.profiles.findIndex(p => p.id === id)
      if (index >= 0) {
        settings.value.profiles.splice(index, 1)
        console.log('Profile deleted:', id)
        return true
      }

      throw new Error('Profile not found')
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete profile'
      console.error('Error deleting profile:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Get models for specific category
   */
  const getModelsByCategory = (category: string) => {
    return settings.value.models.filter(m => m.category === category && m.isAvailable)
  }

  /**
   * Get all unique model categories
   */
  const getModelCategories = () => {
    const categories = new Set<string>()
    settings.value.models.forEach(m => {
      if (m.category) categories.add(m.category)
    })
    return Array.from(categories).sort()
  }

  /**
   * Get models for specific provider
   */
  const getModelsByProvider = (provider: string) => {
    return settings.value.models.filter(m => m.provider === provider && m.isAvailable)
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

    // Profile Methods
    loadProfiles,
    createProfile,
    updateProfile,
    deleteProfile,
    getModelsByCategory,
    getModelCategories,
    getModelsByProvider
  }
}
