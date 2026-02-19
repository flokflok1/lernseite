/**
 * Admin API - Learning Method Types
 *
 * Types for learning method configuration, LM model routing,
 * capability slots, and auto-setup workflows.
 */

// ============================================================================
// Learning Method Definitions
// ============================================================================

export type LearningMethodGroup = 'A' | 'B' | 'C' | 'D' | 'E' | 'F'

export interface LearningMethodType {
  lm_id: number
  name: string
  group: LearningMethodGroup
  method_type: 'explanatory' | 'practice' | 'exam' | 'meta' | 'it' | 'collaborative'
  ki_usage: 'intensive' | 'medium' | 'optional'
  prompt_key: string
  description: string
}

export interface LearningMethodTypesResponse {
  success: boolean
  types: LearningMethodType[]
  total: number
  groups: {
    A: { name: string; range: string; count: number }
    B: { name: string; range: string; count: number }
    C: { name: string; range: string; count: number }
    D: { name: string; range: string; count: number }
  }
}

export interface AdminLearningMethod {
  method_id: string
  chapter_id: string
  method_type: number
  title: string
  instructions?: string | null
  data: Record<string, unknown>
  solution?: Record<string, unknown> | null
  tier: 'basic' | 'premium' | 'pro'
  duration_minutes?: number | null
  difficulty: 'easy' | 'medium' | 'hard'
  order_index: number
  published: boolean
  created_at: string
  updated_at?: string | null
  method_name?: string
  method_group?: LearningMethodGroup
  method_type_name?: string
  ki_usage?: string
  prompt_key?: string
  method_description?: string
}

export interface AdminLearningMethodCreateRequest {
  method_type: number
  title: string
  instructions?: string
  data?: Record<string, unknown>
  solution?: Record<string, unknown>
  tier?: 'basic' | 'premium' | 'pro'
  duration_minutes?: number
  difficulty?: 'easy' | 'medium' | 'hard'
  order_index?: number
  published?: boolean
}

export interface AdminLearningMethodUpdateRequest {
  method_type?: number
  title?: string
  instructions?: string
  data?: Record<string, unknown>
  solution?: Record<string, unknown>
  tier?: 'basic' | 'premium' | 'pro'
  duration_minutes?: number
  difficulty?: 'easy' | 'medium' | 'hard'
  order_index?: number
  published?: boolean
}

export interface AdminLearningMethodsResponse {
  success: boolean
  learning_methods: AdminLearningMethod[]
  total: number
  chapter_id: string
  statistics?: {
    total_methods: number
    published_count: number
    unique_types: number
    total_duration: number
    easy_count: number
    medium_count: number
    hard_count: number
    basic_count: number
    premium_count: number
    pro_count: number
  }
}

// ============================================================================
// LM Model Routing
// ============================================================================

export interface LMModelAssignment {
  learning_method_id: number
  lm_code: string
  lm_name: string
  lm_group: 'A' | 'B' | 'C' | 'D' | null
  lm_type: 'explanatory' | 'practice' | 'exam' | 'meta' | null
  ki_usage: 'intensive' | 'medium' | 'optional' | null
  model_required: boolean
  recommended_categories: string[]
  requires_vision: boolean
  assignment_id: number | null
  model_id: number | null
  model_name: string | null
  model_display_name: string | null
  model_category: string | null
  provider_name: string | null
  provider_display_name: string | null
  is_configured: boolean
}

export interface LMRoutingOverview {
  assignments: LMModelAssignment[]
  stats: {
    total: number
    configured: number
    unconfigured_required: number
    unconfigured_optional: number
  }
}

export interface LMRequirement {
  learning_method_id: number
  lm_code: string
  lm_name: string
  required: boolean
  recommended_categories: string[]
  requires_vision: boolean
  requires_functions: boolean
  min_context_window: number | null
  description: string | null
}

export interface UnconfiguredLM {
  learning_method_id: number
  lm_code: string
  lm_name: string
  lm_group: string | null
  recommended_categories: string[]
  description: string | null
}

export interface RecommendedModel {
  model_id: number
  model_name: string
  display_name: string
  category: string
  provider_name: string
  provider_display_name: string
  score: number
  reasons: string[]
  cost_level: string
  supports_vision: boolean
  context_window: number | null
}

export interface AutoSetupOptions {
  only_required?: boolean
  prefer_cheap?: boolean
  overwrite_existing?: boolean
}

export interface AutoSetupResult {
  configured: number
  skipped: number
  failed: number
  assignments: Array<{
    lm_id: number
    lm_code: string
    lm_name: string
    model_name: string
    provider: string
    score: number
  }>
}

export interface AIAutoSetupOptions {
  model?: string
  overwrite_existing?: boolean
}

export interface AIAutoSetupAssignment {
  lm_id: number
  lm_code: string
  lm_name: string
  model_id: number
  model_name: string
  provider: string
  reasoning: string
}

export interface AIAutoSetupResult {
  configured: number
  failed: number
  assignments: AIAutoSetupAssignment[]
  ai_model_used: string
  total_cost_eur: number
}

// ============================================================================
// LM Capability Slots
// ============================================================================

export interface CapabilitySlot {
  slot_id: number
  slot_code: string
  display_name: string
  description: string
  required_category: string
  accepted_categories: string[]
  icon: string
  sort_order: number
}

export interface CompatibleModel {
  model_id: number
  model_name: string
  display_name: string
  category: string
  provider_name: string
  provider_display_name: string
  supports_vision: boolean
  supports_functions: boolean
  context_window: number | null
  cost_level: string
}

export interface LMSlotConfig {
  slot_code: string
  slot_display_name: string
  is_required: boolean
  is_primary: boolean
  is_configured: boolean
  model: {
    model_id: number
    model_name: string
    display_name: string
    provider: string
  } | null
  resolved_scope: string
  compatible_models?: CompatibleModel[]
}

export interface LMSlotOverview {
  learning_method_id: number
  name: string
  group: string
  ready: boolean
  required_count: number
  configured_count: number
  slots: LMSlotConfig[]
}

export interface SlotAssignmentRequest {
  model_id: number
  scope?: 'system' | 'course' | 'chapter'
  scope_reference_id?: string | null
}

export interface BulkSlotAssignment {
  slot_code: string
  model_id: number
  priority?: number
}
