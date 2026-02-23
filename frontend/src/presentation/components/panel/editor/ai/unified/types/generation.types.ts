/**
 * Types for AI Content Generation Results
 */

export type GenerationStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface GenerationResult {
  generation_id: string
  skill_code: string
  content: Record<string, unknown>
  tokens_input: number
  tokens_output: number
  model_name: string
  provider_name: string
  status: GenerationStatus
  variants?: GenerationVariant[]
  created_at: string
}

export interface GenerationVariant {
  variant_id: string
  label: string
  content: Record<string, unknown>
}

export interface GenerationHistoryEntry {
  generation_id: string
  plan_id: string | null
  skill_code: string
  course_id: string
  target_type: string | null
  target_id: string | null
  tokens_input: number
  tokens_output: number
  model_name: string
  provider_name: string
  status: GenerationStatus
  created_at: string
}

export interface BatchProgress {
  total_steps: number
  completed_steps: number
  failed_steps: number
  current_step_index: number
  current_skill_code: string | null
  is_running: boolean
  is_paused: boolean
}
