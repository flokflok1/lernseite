/**
 * useGlobalSettings Composable
 *
 * Manages state and API operations for the GlobalSettingsTab:
 * - Provider management (sync, test, API keys)
 * - Profile CRUD (create, edit, delete, set default)
 * - Model and category data loading
 * - Toast notifications and action results
 */

import { ref, reactive, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'

// ============================================================================
// Types
// ============================================================================

export interface Provider {
  provider_id: number
  name: string
  display_name: string
  active: boolean
  has_api_key: boolean
}

export interface Profile {
  key: string
  name: string
  description?: string
  is_default: boolean
  [key: string]: any
}

export interface AIModel {
  model_id: number
  model_name: string
  display_name?: string
  provider_name: string
  category: string
  active: boolean
}

export interface Stats {
  total_models: number
  active_models: number
  providers: number
  categories: number
}

export interface ActionResultMessage {
  success: boolean
  message: string
}

export interface ProfileFormData {
  key: string
  name: string
  description: string
  models: Record<string, string>
}

// ============================================================================
// Composable
// ============================================================================

export function useGlobalSettings() {
  const { t } = useI18n()
  const windowStore = useWindowStore()

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

  const formData = reactive<ProfileFormData>({
    key: '',
    name: '',
    description: '',
    models: {}
  })

  // API Key Modal state
  const apiKeyModal = ref<Provider | null>(null)
  const apiKeyInput = ref('')
  const showApiKey = ref(false)
  const testingApiKey = ref(false)
  const savingApiKey = ref(false)
  const apiKeyResult = ref<ActionResultMessage | null>(null)

  // Feedback
  const actionResult = ref<ActionResultMessage | null>(null)
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

  // ============================================================================
  // Toast helper
  // ============================================================================

  function showToast(type: string, message: string): void {
    toast.value = { type, message }
    setTimeout(() => { toast.value = null }, 3000)
  }

  // ============================================================================
  // Data Loading
  // ============================================================================

  async function loadData(): Promise<void> {
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
      showToast('error', t('aiEditorGlobalSettings.loadError'))
    } finally {
      loading.value = false
    }
  }

  async function loadProfiles(): Promise<void> {
    try {
      const response = await http.get('/admin/ai-model-profiles')
      if (response.data.success) {
        profiles.value = response.data.data?.profiles || []
      }
    } catch (error) {
      console.error('Failed to load profiles:', error)
    }
  }

  // ============================================================================
  // Profile Methods
  // ============================================================================

  function populateForm(profile: Profile): void {
    formData.key = profile.key
    formData.name = profile.name
    formData.description = profile.description || ''
    formData.models = {}
    for (const cat of categories.value) {
      const fieldName = `${cat}_model_id`
      formData.models[cat] = profile[fieldName] || ''
    }
  }

  function resetForm(): void {
    formData.key = ''
    formData.name = ''
    formData.description = ''
    formData.models = {}
  }

  function selectProfile(profile: Profile): void {
    selectedProfileKey.value = profile.key
    isCreating.value = false
    populateForm(profile)
  }

  function createNewProfile(): void {
    selectedProfileKey.value = null
    isCreating.value = true
    resetForm()
  }

  function updateFormData(data: ProfileFormData): void {
    Object.assign(formData, data)
  }

  function cancelEdit(): void {
    if (selectedProfile.value) {
      populateForm(selectedProfile.value)
    } else {
      resetForm()
    }
    isCreating.value = false
  }

  async function saveProfile(): Promise<void> {
    if (!formData.name.trim()) {
      showToast('error', t('aiEditorGlobalSettings.nameRequired'))
      return
    }
    if (isCreating.value && !formData.key.trim()) {
      showToast('error', t('aiEditorGlobalSettings.keyRequired'))
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
          ? t('aiEditorGlobalSettings.profileCreated')
          : t('aiEditorGlobalSettings.profileSaved'))
        await loadProfiles()
        if (isCreating.value) selectedProfileKey.value = body.key
        isCreating.value = false
      } else {
        showToast('error', response.data.error?.message || t('aiEditorGlobalSettings.saveError'))
      }
    } catch (error) {
      console.error('Failed to save profile:', error)
      showToast('error', t('aiEditorGlobalSettings.saveError'))
    } finally {
      saving.value = false
    }
  }

  async function deleteProfile(): Promise<void> {
    if (!selectedProfileKey.value) return
    if (!confirm(t('aiEditorGlobalSettings.confirmDeleteProfile'))) return

    try {
      const response = await http.delete(`/admin/ai-model-profiles/${selectedProfileKey.value}`)
      if (response.data.success) {
        showToast('success', t('aiEditorGlobalSettings.profileDeleted'))
        selectedProfileKey.value = null
        resetForm()
        await loadProfiles()
      } else {
        showToast('error', response.data.error?.message || t('aiEditorGlobalSettings.deleteError'))
      }
    } catch (error: any) {
      showToast('error', error.response?.data?.error?.message || t('aiEditorGlobalSettings.deleteError'))
    }
  }

  async function setAsDefault(): Promise<void> {
    if (!selectedProfileKey.value) return
    try {
      const response = await http.post(`/admin/ai-model-profiles/${selectedProfileKey.value}/default`)
      if (response.data.success) {
        showToast('success', t('aiEditorGlobalSettings.setDefaultSuccess'))
        await loadProfiles()
      } else {
        showToast('error', t('aiEditorGlobalSettings.setDefaultError'))
      }
    } catch {
      showToast('error', t('aiEditorGlobalSettings.setDefaultError'))
    }
  }

  // ============================================================================
  // Provider & API Key Methods
  // ============================================================================

  function openApiKeyModal(provider: Provider): void {
    apiKeyModal.value = provider
    apiKeyInput.value = ''
    showApiKey.value = false
    apiKeyResult.value = null
  }

  async function saveApiKey(): Promise<void> {
    if (!apiKeyModal.value || !apiKeyInput.value) return
    savingApiKey.value = true
    try {
      const response = await http.put(`/admin/ai/providers/${apiKeyModal.value.provider_id}/api-key`, {
        api_key: apiKeyInput.value
      })
      if (response.data.success) {
        apiKeyResult.value = { success: true, message: t('aiEditorGlobalSettings.apiKeySaved') }
        apiKeyInput.value = ''
        await loadData()
        setTimeout(() => { apiKeyModal.value = null }, 1000)
      } else {
        apiKeyResult.value = { success: false, message: response.data.error?.message || t('aiEditorGlobalSettings.saveError') }
      }
    } catch (error: any) {
      apiKeyResult.value = { success: false, message: error.response?.data?.error?.message || t('aiEditorGlobalSettings.saveError') }
    } finally {
      savingApiKey.value = false
    }
  }

  async function testApiKey(): Promise<void> {
    if (!apiKeyModal.value) return
    testingApiKey.value = true
    apiKeyResult.value = null
    try {
      const response = await http.get(`/admin/ai/providers/${apiKeyModal.value.provider_id}/test`)
      if (response.data.success) {
        apiKeyResult.value = { success: true, message: t('aiEditorGlobalSettings.connectionOkMs', { ms: response.data.data?.response_time_ms || 0 }) }
      } else {
        apiKeyResult.value = { success: false, message: response.data.error?.message || t('aiEditorGlobalSettings.testFailed') }
      }
    } catch (error: any) {
      apiKeyResult.value = { success: false, message: error.response?.data?.error?.message || t('aiEditorGlobalSettings.connectionFailed') }
    } finally {
      testingApiKey.value = false
    }
  }

  async function testProvider(provider: Provider): Promise<void> {
    testingProvider.value = provider.name
    try {
      const response = await http.get(`/admin/ai/providers/${provider.provider_id}/test`)
      showToast(response.data.success ? 'success' : 'error',
        response.data.success
          ? t('aiEditorGlobalSettings.providerOk', { provider: provider.display_name })
          : t('aiEditorGlobalSettings.providerFailed', { provider: provider.display_name }))
    } catch {
      showToast('error', t('aiEditorGlobalSettings.providerFailed', { provider: provider.display_name }))
    } finally {
      testingProvider.value = null
    }
  }

  // ============================================================================
  // Sync & Test All
  // ============================================================================

  async function syncProvider(providerName: string): Promise<void> {
    isSyncing.value = true
    actionResult.value = null
    try {
      const response = await http.post('/admin/ai/models/sync', { provider: providerName })
      actionResult.value = response.data.success
        ? { success: true, message: t('aiEditorGlobalSettings.syncSuccess', { count: response.data.data?.synced || 0 }) }
        : { success: false, message: response.data.error?.message || t('aiEditorGlobalSettings.syncFailed') }
      if (response.data.success) await loadData()
    } catch (error: any) {
      actionResult.value = { success: false, message: error.response?.data?.error?.message || t('aiEditorGlobalSettings.syncFailed') }
    } finally {
      isSyncing.value = false
    }
  }

  async function syncAllModels(): Promise<void> {
    isSyncing.value = true
    actionResult.value = null
    try {
      const response = await http.post('/admin/ai/models/sync')
      actionResult.value = response.data.success
        ? { success: true, message: t('aiEditorGlobalSettings.syncSuccess', { count: response.data.data?.synced || 0 }) }
        : { success: false, message: response.data.error?.message || t('aiEditorGlobalSettings.syncFailed') }
      if (response.data.success) await loadData()
    } catch (error: any) {
      actionResult.value = { success: false, message: error.response?.data?.error?.message || t('aiEditorGlobalSettings.syncFailed') }
    } finally {
      isSyncing.value = false
    }
  }

  async function testAllConnections(): Promise<void> {
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
      message: t('aiEditorGlobalSettings.testComplete', { success: successCount, failed: failCount })
    }
    isTesting.value = false
  }

  function openPricingWindow(): void {
    windowStore.openWindow({ type: 'admin-ai-pricing', title: t('aiPricing.title'), icon: '💰' })
  }

  return {
    // State
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
    // API Key Modal
    apiKeyModal,
    apiKeyInput,
    showApiKey,
    testingApiKey,
    savingApiKey,
    apiKeyResult,
    // Feedback
    actionResult,
    toast,
    // Computed
    selectedProfile,
    modelCountsByProvider,
    // Methods
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
  }
}
