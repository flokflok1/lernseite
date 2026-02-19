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
  AIModelUpdateRequest,
  AIModelCategory
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
  const response = await http.get<AIModelRegistryResponse>('/admin/ai/models/registry', {
    params: {
      category: params.category,
      active_only: params.active_only !== false ? 'true' : 'false',
      search: params.search,
      provider: params.provider,
      configured_only: params.configured_only ? 'true' : 'false'
    }
  })

  return response.data
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
