/**
 * Admin AI Model Management API
 */

import http from '@/infrastructure/api/http'
import type {
  AIModel,
  AIModelsResponse,
  AIModelFilterParams,
  AIModelSyncResponse,
  AIModelRegistryResponse,
  AIModelRegistryItem,
  AIModelRegistryCategory,
  AIModelUpdateRequest,
  AIModelCategory,
  AIProviderInfo,
} from '../types'

export const adminGetAIModels = async (
  params: AIModelFilterParams = {}
): Promise<AIModelsResponse> => {
  const response = await http.get<AIModelsResponse>('/admin/ai/models', {
    params: {
      category: params.category,
      active_only: params.active_only !== false ? 'true' : 'false',
      search: params.search
    }
  })

  return response.data
}

export const adminSyncAIModels = async (): Promise<AIModelSyncResponse> => {
  const response = await http.post<AIModelSyncResponse>('/admin/ai/models/sync', {})
  return response.data
}

export const adminSetAIModelDefault = async (
  modelId: number,
  isDefault = true
): Promise<{
  success: boolean
  message: string
  data: { model_id: number; model_name: string; category: string; is_default: boolean }
}> => {
  const response = await http.patch<{
    success: boolean
    message: string
    data: {
      model_id: number
      model_name: string
      category: string
      is_default: boolean
    }
  }>(`/admin/ai/models/${modelId}/default`, {
    is_default: isDefault
  })

  return response.data
}

export const adminGetDefaultAIModel = async (
  category: AIModelCategory = 'chat'
): Promise<AIModel | null> => {
  const response = await http.get<{
    success: boolean
    data: AIModel | null
  }>('/admin/ai/models/default', {
    params: { category }
  })

  return response.data.data
}

export const adminGetAIModelsRegistry = async (
  params: AIModelFilterParams = {}
): Promise<AIModelRegistryResponse> => {
  // Reuse existing endpoints: models + providers
  const [modelsRes, providersRes] = await Promise.all([
    http.get<{
      success: boolean
      data: { models: AIModelRegistryItem[]; count: number; categories: string[] }
    }>('/panel/settings/ai/models', {
      params: {
        include_inactive: params.active_only === false ? 'true' : 'false',
        category: params.category,
        provider: params.provider,
      },
    }),
    http.get<{
      success: boolean
      data: { providers: Array<{ provider_id: number; name: string; display_name: string; has_api_key: boolean }>; count: number }
    }>('/panel/settings/ai/providers', {
      params: { include_inactive: 'true' },
    }),
  ])

  const rawModels = modelsRes.data.data.models || []
  const rawProviders = providersRes.data.data.providers || []

  // Map provider_name → provider for ModelSelector compatibility
  const models: AIModelRegistryItem[] = rawModels.map((m: Record<string, unknown>) => ({
    ...m,
    provider: (m.provider_name as string) || (m.provider as string) || '',
  })) as AIModelRegistryItem[]

  // Build categories from raw strings
  const categoryLabels: Record<string, string> = {
    chat: 'Chat', reasoning: 'Reasoning', realtime: 'Realtime',
    audio: 'Audio', image: 'Image', video: 'Video',
    embedding: 'Embedding', moderation: 'Moderation',
  }
  const categories: AIModelRegistryCategory[] = (modelsRes.data.data.categories || []).map(
    (id: string) => ({ id, label: categoryLabels[id] || id })
  )

  // Map providers to AIProviderInfo
  const providers: AIProviderInfo[] = rawProviders.map((p) => ({
    provider_id: p.provider_id,
    name: p.name,
    display_name: p.display_name,
    has_api_key: p.has_api_key,
  }))

  return {
    success: true,
    data: models,
    categories,
    providers,
    total: models.length,
    timestamp: new Date().toISOString(),
  }
}

export const adminUpdateAIModel = async (
  modelId: number,
  data: AIModelUpdateRequest
): Promise<AIModelRegistryItem> => {
  const response = await http.put<{
    success: boolean
    data: AIModelRegistryItem
    message: string
  }>(`/admin/ai/models/${modelId}`, data)

  return response.data.data
}

export const adminToggleAIModelActive = async (
  modelId: number,
  active: boolean
): Promise<AIModelRegistryItem> => {
  const response = await http.put<{
    success: boolean
    data: AIModelRegistryItem
    message: string
  }>(`/admin/ai/models/${modelId}/active`, { active })

  return response.data.data
}
