/**
 * Admin LM Model Routing API
 */

import http from '@/infrastructure/api/http'
import type {
  LMRoutingOverview,
  LMModelAssignment,
  LMRequirement,
  UnconfiguredLM,
  RecommendedModel,
  AutoSetupOptions,
  AutoSetupResult,
  AIAutoSetupOptions,
  AIAutoSetupResult,
  CapabilitySlot,
  LMSlotOverview,
  LMSlotConfig,
  SlotAssignmentRequest,
  BulkSlotAssignment,
  CompatibleModel
} from '../types'

// Basic Routing

export const adminGetLMRoutingOverview = async (): Promise<LMRoutingOverview> => {
  const response = await http.get<{
    success: boolean
    data: LMRoutingOverview
  }>('/admin/lm-routing/overview')
  return response.data.data
}

export const adminGetUnconfiguredLMs = async (): Promise<{
  unconfigured: UnconfiguredLM[]
  count: number
}> => {
  const response = await http.get<{
    success: boolean
    data: {
      unconfigured: UnconfiguredLM[]
      count: number
    }
  }>('/admin/lm-routing/unconfigured')
  return response.data.data
}

export const adminGetLMRequirements = async (): Promise<LMRequirement[]> => {
  const response = await http.get<{
    success: boolean
    data: {
      requirements: LMRequirement[]
    }
  }>('/admin/lm-routing/requirements')
  return response.data.data.requirements
}

export const adminGetLMAssignment = async (lmId: number): Promise<LMModelAssignment & {
  requirement: {
    required: boolean
    recommended_categories: string[]
    requires_vision: boolean
  }
  assignment: {
    assignment_id: number
    model_id: number
    model_name: string
    model_display_name: string
    model_category: string
    provider_name: string
    provider_display_name: string
  } | null
}> => {
  const response = await http.get<{
    success: boolean
    data: LMModelAssignment & {
      requirement: {
        required: boolean
        recommended_categories: string[]
        requires_vision: boolean
      }
      assignment: {
        assignment_id: number
        model_id: number
        model_name: string
        model_display_name: string
        model_category: string
        provider_name: string
        provider_display_name: string
      } | null
    }
  }>(`/admin/lm-routing/${lmId}`)
  return response.data.data
}

export const adminSetLMAssignment = async (
  lmId: number,
  modelId: number
): Promise<{ success: boolean; message: string }> => {
  const response = await http.put<{
    success: boolean
    data: unknown
    message: string
  }>(`/admin/lm-routing/${lmId}`, { model_id: modelId })
  return {
    success: response.data.success,
    message: response.data.message
  }
}

export const adminRemoveLMAssignment = async (
  lmId: number
): Promise<{ success: boolean; message: string }> => {
  const response = await http.delete<{
    success: boolean
    message: string
  }>(`/admin/lm-routing/${lmId}`)
  return {
    success: response.data.success,
    message: response.data.message
  }
}

export const adminBulkSetLMAssignments = async (
  assignments: Array<{ learning_method_id: number; model_id: number }>
): Promise<{ created: number; errors: Array<{ learning_method_id: number; error: string }> }> => {
  const response = await http.post<{
    success: boolean
    data: {
      created: number
      errors: Array<{ learning_method_id: number; error: string }>
    }
  }>('/admin/lm-routing/bulk', { assignments })
  return response.data.data
}

export const adminResolveLMModel = async (
  lmId: number,
  chapterId?: string,
  courseId?: string
): Promise<{
  model_id: number | null
  model_name: string | null
  provider_name: string | null
  scope: string
  is_configured: boolean
  model_required: boolean
  can_generate: boolean
}> => {
  const response = await http.post<{
    success: boolean
    data: {
      model_id: number | null
      model_name: string | null
      provider_name: string | null
      scope: string
      is_configured: boolean
      model_required: boolean
      can_generate: boolean
    }
  }>('/admin/lm-routing/resolve', {
    learning_method_id: lmId,
    chapter_id: chapterId,
    course_id: courseId
  })
  return response.data.data
}

export const adminGetLMRecommendations = async (lmId: number): Promise<{
  learning_method_id: number
  lm_code: string
  lm_name: string
  requirements: {
    recommended_categories: string[]
    requires_vision: boolean
    min_context_window: number | null
  }
  recommended_models: RecommendedModel[]
  total_matching: number
}> => {
  const response = await http.get<{
    success: boolean
    data: {
      learning_method_id: number
      lm_code: string
      lm_name: string
      requirements: {
        recommended_categories: string[]
        requires_vision: boolean
        min_context_window: number | null
      }
      recommended_models: RecommendedModel[]
      total_matching: number
    }
  }>(`/admin/lm-routing/recommend/${lmId}`)
  return response.data.data
}

// Auto-Setup

export const adminAutoSetupLMModels = async (
  options: AutoSetupOptions = {}
): Promise<AutoSetupResult> => {
  const response = await http.post<{
    success: boolean
    data: AutoSetupResult
    message: string
  }>('/admin/lm-routing/auto-setup', options)
  return response.data.data
}

export const adminAIAutoSetupLMModels = async (
  options: AIAutoSetupOptions = {}
): Promise<AIAutoSetupResult> => {
  const response = await http.post<{
    success: boolean
    data: AIAutoSetupResult
    message: string
  }>('/admin/lm-routing/ai-auto-setup', options, {
    timeout: 600000
  })
  return response.data.data
}

// Capability Slots

export const getCapabilitySlots = async (): Promise<CapabilitySlot[]> => {
  const response = await http.get<{
    success: boolean
    data: {
      slots: CapabilitySlot[]
    }
  }>('/admin/lm-routing/slots')
  return response.data.data.slots
}

export const getLMSlotOverview = async (lmId: number): Promise<LMSlotOverview> => {
  const response = await http.get<{
    success: boolean
    data: LMSlotOverview
  }>(`/admin/lm-routing/${lmId}/slots`)
  return response.data.data
}

export const assignSlotModel = async (
  lmId: number,
  slotCode: string,
  request: SlotAssignmentRequest
): Promise<{ success: boolean; message: string }> => {
  const response = await http.put<{
    success: boolean
    data: unknown
    message: string
  }>(`/admin/lm-routing/${lmId}/slots/${slotCode}`, request)
  return {
    success: response.data.success,
    message: response.data.message
  }
}

export const removeSlotAssignment = async (
  lmId: number,
  slotCode: string,
  scope: string = 'system',
  scopeReferenceId?: string
): Promise<{ success: boolean; message: string }> => {
  let url = `/admin/lm-routing/${lmId}/slots/${slotCode}?scope=${scope}`
  if (scopeReferenceId) {
    url += `&scope_reference_id=${scopeReferenceId}`
  }
  const response = await http.delete<{
    success: boolean
    message: string
  }>(url)
  return {
    success: response.data.success,
    message: response.data.message
  }
}

export const bulkAssignSlots = async (
  lmId: number,
  assignments: BulkSlotAssignment[],
  scope: string = 'system',
  scopeReferenceId?: string | null
): Promise<{ created: number; assignments: unknown[] }> => {
  const response = await http.put<{
    success: boolean
    data: {
      created: number
      assignments: unknown[]
    }
    message: string
  }>(`/admin/lm-routing/${lmId}/slots/bulk`, {
    assignments,
    scope,
    scope_reference_id: scopeReferenceId
  })
  return response.data.data
}

export const resolveLMSlots = async (
  lmId: number,
  chapterId?: string,
  courseId?: string
): Promise<{
  learning_method_id: number
  ready: boolean
  required_count: number
  configured_count: number
  missing_slots: string[]
  slots: Record<string, LMSlotConfig | null>
}> => {
  const response = await http.post<{
    success: boolean
    data: {
      learning_method_id: number
      ready: boolean
      required_count: number
      configured_count: number
      missing_slots: string[]
      slots: Record<string, LMSlotConfig | null>
    }
  }>(`/admin/lm-routing/${lmId}/slots/resolve`, {
    chapter_id: chapterId,
    course_id: courseId
  })
  return response.data.data
}

export const getAllLMSlotsOverview = async (): Promise<{
  lms: LMSlotOverview[]
  stats: {
    total: number
    ready: number
    not_ready: number
    missing_required: number
  }
}> => {
  const response = await http.get<{
    success: boolean
    data: {
      lms: LMSlotOverview[]
      stats: {
        total: number
        ready: number
        not_ready: number
        missing_required: number
      }
    }
  }>('/admin/lm-routing/slots/overview')
  return response.data.data
}

export const getCompatibleModelsForSlot = async (
  slotCode: string
): Promise<{
  slot_code: string
  slot_display_name: string
  required_category: string
  compatible_models: CompatibleModel[]
}> => {
  const response = await http.get<{
    success: boolean
    data: {
      slot_code: string
      slot_display_name: string
      required_category: string
      compatible_models: CompatibleModel[]
    }
  }>(`/admin/lm-routing/slots/${slotCode}/models`)
  return response.data.data
}

export const applySlotPreset = async (
  preset: 'cheap' | 'medium' | 'expensive'
): Promise<{
  preset: string
  preset_label: string
  configured: number
  skipped: number
  failed: number
}> => {
  const response = await http.post<{
    success: boolean
    data: {
      preset: string
      preset_label: string
      configured: number
      skipped: number
      failed: number
    }
    message: string
  }>('/admin/lm-routing/slots/apply-preset', { preset })
  return response.data.data
}

export const setDefaultModelForCategory = async (
  category: string,
  modelId: number
): Promise<{ category: string; model_id: number }> => {
  const response = await http.post<{
    success: boolean
    data: { category: string; model_id: number }
  }>('/admin/lm-routing/category-defaults', { category, model_id: modelId })
  return response.data.data
}
