/**
 * Types for Prompt Builder
 */

export interface PromptTemplate {
  code: string
  name: string
  description: string
  system_prompt: string
  user_prompt: string
  variables: PromptVariable[]
}

export interface PromptVariable {
  key: string
  label: string
  type: 'text' | 'select' | 'number'
  default_value: string
  description?: string
}

export interface PromptPreset {
  id: string
  name_i18n_key: string
  tone: string
  style: string
  icon: string
}

export const PROMPT_PRESETS: PromptPreset[] = [
  { id: 'formal', name_i18n_key: 'aiEditor.prompts.presets.formal', tone: 'formal', style: 'academic', icon: 'GraduationCap' },
  { id: 'casual', name_i18n_key: 'aiEditor.prompts.presets.casual', tone: 'casual', style: 'conversational', icon: 'MessageCircle' },
  { id: 'technical', name_i18n_key: 'aiEditor.prompts.presets.technical', tone: 'precise', style: 'technical', icon: 'Code' },
  { id: 'simplified', name_i18n_key: 'aiEditor.prompts.presets.simplified', tone: 'friendly', style: 'simplified', icon: 'Smile' },
]
