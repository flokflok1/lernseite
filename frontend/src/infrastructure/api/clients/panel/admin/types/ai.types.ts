/**
 * Admin API - AI Types
 *
 * Types for AI job management, AI model registry,
 * AI model pricing, and provider configuration.
 */

// ============================================================================
// AI Jobs
// ============================================================================

export type AIJobStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
export type AIJobType = 'course_from_pdf' | 'chapter_autogen' | 'lesson_autogen'

export interface AICourseDraft {
  course: {
    title: string
    description: string
    category: string
    level: string
    language: string
  }
  chapters: Array<{
    title: string
    description: string
    duration_minutes: number
    order_index: number
    lessons: Array<{
      title: string
      lesson_type: string
      duration_minutes: number
      order_index: number
    }>
  }>
}

export interface AIJob {
  id: string
  user_id: string
  course_id?: string | null
  type: AIJobType
  status: AIJobStatus
  progress: number
  input_file?: string | null
  input_prompt?: string | null
  output_data?: AICourseDraft | null
  error_message?: string | null
  created_at: string
  updated_at: string
}

export interface AIJobCreateRequest {
  type: AIJobType
  file_name?: string
  prompt?: string
  course_id?: string
}

export interface AIJobResponse {
  success: boolean
  job: AIJob
}

export interface AIJobFinalizeRequest {
  create_course?: boolean
  create_chapters?: boolean
  create_lessons?: boolean
}

export interface AIJobFinalizeResponse {
  success: boolean
  message: string
  course_id: number
  chapters_created: number
  lessons_created: number
}

// ============================================================================
// AI Models
// ============================================================================

export type AIModelCategory =
  | 'reasoning'
  | 'chat'
  | 'realtime'
  | 'audio'
  | 'image'
  | 'video'
  | 'embedding'
  | 'moderation'

export type AIModelCostLevel = 'free' | 'low' | 'medium' | 'high' | 'very_high'
export type AIModelSpeed = 'very_fast' | 'fast' | 'medium' | 'slow'

export interface AIModel {
  model_id: number
  model_name: string
  display_name: string
  model_type?: string
  category: AIModelCategory
  description?: string | null
  cost_level: AIModelCostLevel
  speed: AIModelSpeed
  context_window?: number | null
  max_output_tokens?: number | null
  supports_vision?: boolean
  supports_functions?: boolean
  supports_streaming?: boolean
  is_default: boolean
  active: boolean
  provider_id?: number
  provider_name?: string
  provider_display_name?: string
  created_at?: string
  updated_at?: string
}

export interface AIModelsResponse {
  success: boolean
  data: AIModel[]
  categories: AIModelCategory[]
  total: number
  timestamp: string
}

export interface AIModelFilterParams {
  category?: AIModelCategory
  active_only?: boolean
  search?: string
  provider?: string
  configured_only?: boolean
}

export interface AIModelSyncResponse {
  success: boolean
  data: {
    added: number
    updated: number
    unchanged: number
    total_synced: number
    models: Array<{
      model_name: string
      category: string
      status: 'added' | 'updated'
    }>
  }
  timestamp: string
}

export interface AIModelRegistryCategory {
  id: string
  label: string
}

export interface AIModelRegistryItem extends AIModel {
  provider?: string
  input_price_per_1k?: number | null
  output_price_per_1k?: number | null
}

export interface AIModelUpdateRequest {
  display_name?: string
  description?: string
  cost_level?: AIModelCostLevel
  speed?: AIModelSpeed
  input_price_per_1k?: number | null
  output_price_per_1k?: number | null
  active?: boolean
}

export interface AIProviderInfo {
  provider_id: number
  name: string
  display_name: string
  has_api_key: boolean
}

export interface AIModelRegistryResponse {
  success: boolean
  data: AIModelRegistryItem[]
  categories: AIModelRegistryCategory[]
  providers: AIProviderInfo[]
  total: number
  timestamp: string
}

// ============================================================================
// AI Model Pricing
// ============================================================================

export interface AIModelPricing {
  model_id: number
  provider_id: number
  provider_name: string
  provider_display_name?: string
  model_name: string
  display_name: string
  category: string
  cost_per_1k_input: number | null
  cost_per_1k_output: number | null
  input_price_per_1k: number | null
  output_price_per_1k: number | null
  margin_input: number | null
  margin_output: number | null
  active: boolean
  is_default: boolean
  updated_at: string
}

export interface AIModelPricingResponse {
  success: boolean
  data: {
    models: AIModelPricing[]
    count: number
    categories: string[]
    providers: string[]
  }
}

export interface AIModelPricingUpdateRequest {
  cost_per_1k_input?: number | null
  cost_per_1k_output?: number | null
  input_price_per_1k?: number | null
  output_price_per_1k?: number | null
}

export interface AIModelBulkPricingRequest {
  model_ids: number[]
  updates: AIModelPricingUpdateRequest
}

export interface AIModelApplyMarginRequest {
  model_ids: number[] | 'all'
  margin_percent: number
  apply_to: 'input' | 'output' | 'both'
}

export interface AIModelBulkPricingResponse {
  success: boolean
  data: { updated_count: number }
  message: string
}
