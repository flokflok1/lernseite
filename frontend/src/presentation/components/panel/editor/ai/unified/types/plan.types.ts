/**
 * Types for AI Content Plan Mode
 */

export type PlanScope = 'course' | 'chapter' | 'lesson'
export type PlanStatus = 'draft' | 'approved' | 'executing' | 'completed' | 'paused'
export type PlanStepStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped'

export interface ContentPlan {
  plan_id: string
  course_id: string
  scope: PlanScope
  scope_id: string | null
  status: PlanStatus
  phases: PlanPhase[]
  estimated_total_tokens: number
  actual_tokens: number
  created_at: string
  updated_at: string
}

export interface PlanPhase {
  phase_id: string
  order: number
  title: string
  steps: PlanStep[]
}

export interface PlanStep {
  step_id: string
  order: number
  skill_code: string
  target_type: 'chapter' | 'lesson'
  target_id: string
  target_title: string
  parameters: Record<string, unknown>
  status: PlanStepStatus
  result?: import('./generation.types').GenerationResult
}

export interface CreatePlanRequest {
  course_id: string
  scope: PlanScope
  scope_id?: string
}

export interface CreatePlanFromFileRequest {
  course_id: string
  file_id: string
}

export interface UpdatePlanRequest {
  plan_data?: { phases: PlanPhase[] }
}
