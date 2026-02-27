import { ref, computed } from 'vue'
import {
  getAvailableModels,
  type AvailableProvider,
  type AvailableModel,
} from '@/infrastructure/api/clients/panel/editor/authoring/courseAuthoring.api'

/**
 * Composable for provider/model selection in the AI Editor.
 * Loads active providers with API keys and their active chat models.
 */
export function useModelSelector() {
  const providers = ref<AvailableProvider[]>([])
  const selectedProvider = ref('')
  const selectedModel = ref('')
  const isLoading = ref(false)

  const currentModels = computed<AvailableModel[]>(() => {
    if (!selectedProvider.value) return []
    const p = providers.value.find((p) => p.provider_name === selectedProvider.value)
    return p?.models ?? []
  })

  const selectionLabel = computed(() => {
    if (!selectedProvider.value || !selectedModel.value) return ''
    const p = providers.value.find((p) => p.provider_name === selectedProvider.value)
    const m = p?.models.find((m) => m.model_name === selectedModel.value)
    return m ? `${p?.display_name} / ${m.display_name}` : ''
  })

  async function loadAvailableModels(): Promise<void> {
    isLoading.value = true
    try {
      providers.value = await getAvailableModels()
      // Auto-select first provider with a default model (or just first provider)
      if (providers.value.length > 0 && !selectedProvider.value) {
        const withDefault = providers.value.find((p) =>
          p.models.some((m) => m.is_default)
        )
        const initial = withDefault || providers.value[0]
        handleProviderChange(initial.provider_name)
      }
    } catch (err) {
      console.warn('[ModelSelector] Failed to load models:', err)
    } finally {
      isLoading.value = false
    }
  }

  function handleProviderChange(providerName: string): void {
    selectedProvider.value = providerName
    const p = providers.value.find((p) => p.provider_name === providerName)
    if (!p || p.models.length === 0) {
      selectedModel.value = ''
      return
    }
    // Prefer default model, else first
    const defaultModel = p.models.find((m) => m.is_default)
    selectedModel.value = (defaultModel || p.models[0]).model_name
  }

  return {
    providers,
    selectedProvider,
    selectedModel,
    currentModels,
    selectionLabel,
    isLoading,
    loadAvailableModels,
    handleProviderChange,
  }
}
