/**
 * Types for AI Skill Catalog and Execution
 */

export type SkillCategory = 'explanatory' | 'practice' | 'assessment' | 'content' | 'review'
export type SkillContextLevel = 'course' | 'chapter' | 'lesson'

export interface SkillConfig {
  code: string
  name_i18n_key: string
  description_i18n_key: string
  icon: string
  category: SkillCategory
  learning_method_id: number | null
  prompt_template_code: string
  required_context: SkillContextLevel[]
  parameters: SkillParameter[]
  supports_variants: boolean
  estimated_tokens: number
}

export interface SkillParameter {
  key: string
  label_i18n_key: string
  type: 'string' | 'number' | 'select' | 'boolean'
  default_value: unknown
  options?: SkillParameterOption[]
  required: boolean
}

export interface SkillParameterOption {
  value: string
  label_i18n_key: string
}

export interface ExecuteSkillRequest {
  skill_code: string
  course_id: string
  target_type?: 'chapter' | 'lesson'
  target_id?: string
  parameters?: Record<string, unknown>
  prompt_override?: string
}

export interface BatchExecuteRequest {
  plan_id: string
  steps: ExecuteSkillRequest[]
}

export interface SkillCatalogResponse {
  skills: SkillConfig[]
  categories: SkillCategory[]
}
