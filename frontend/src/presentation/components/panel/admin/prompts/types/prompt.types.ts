/**
 * Prompt Template Types
 *
 * Shared type definitions for the PanelPromptsPage and its sub-components.
 */

export interface PromptTemplate {
  template_id?: string
  code: string
  name: string
  title?: string
  description?: string
  category: string
  style: string
  system_prompt: string
  user_prompt: string
  user_prompt_template?: string
  expected_json?: string
  model?: string
  temperature?: number
  max_tokens?: number
  tts_voice?: string
  tts_model?: string
  is_default?: boolean
  is_active?: boolean
  usage_count?: number
  created_at?: string
  updated_at?: string
}

export interface PromptStats {
  total: number
  usageCount: number
  tokensUsed: number
}

export interface PromptPreviewData {
  system_prompt: string
  rendered_prompt: string
}

export const CATEGORY_LABELS: Record<string, string> = {
  theory: 'Theorieblatt',
  lesson: 'Lektionsschritte',
  quiz: 'Quiz',
  flashcard: 'Karteikarten',
  summary: 'Zusammenfassung',
  explanation: 'Erklaerung'
}

export const STYLE_LABELS: Record<string, string> = {
  standard: 'Standard',
  adhs: 'ADHS-freundlich',
  detailed: 'Ausfuehrlich',
  short: 'Kurz & Kompakt',
  exam_focus: 'Pruefungsfokus'
}

export function createEmptyTemplate(): PromptTemplate {
  return {
    code: '',
    name: '',
    description: '',
    category: 'theory',
    style: 'standard',
    system_prompt: '',
    user_prompt: '',
    expected_json: '',
    model: 'gpt-4o-mini',
    temperature: 0.7,
    max_tokens: 4000,
    tts_voice: 'nova',
    tts_model: 'tts-1',
    is_default: false,
    is_active: true
  }
}
