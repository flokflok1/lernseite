// workflow.types.ts — Types for workflow phase tracking

export type WorkflowPhase = 'plan' | 'generate' | 'accept'

export interface GenerateProgress {
  current: number
  total: number
  label: string
  percent: number
  skillCode?: string
}

/** Frontend-normalized result from workflow phase generate. See also GenerationResult in generation.types.ts for API shape. */
export interface GenerateResult {
  generationId: string
  skillCode: string
  content: Record<string, unknown>
  tokensInput: number
  tokensOutput: number
  modelName: string
  targetType?: string
  targetId?: string
  targetTitle?: string
}
