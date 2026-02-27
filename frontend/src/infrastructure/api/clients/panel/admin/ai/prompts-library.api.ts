/**
 * Prompts Library API — CRUD for prompt templates (ai_pipeline.prompt_templates)
 *
 * Endpoints:
 *   GET    /panel/prompts           — list all (optional ?category filter)
 *   GET    /panel/prompts/:id       — get template detail
 *   PUT    /panel/prompts/:id       — update template
 *   DELETE /panel/prompts/:id       — soft-delete template
 */
import http from '@/infrastructure/api/http'

export interface PromptTemplateListItem {
  template_id: string
  code: string
  category: string
  style: string
  title: string
  description: string
  icon: string | null
  model: string | null
  provider: string | null
  tts_enabled: boolean
  is_default: boolean
  is_system: boolean
  version: number
  created_at: string
  updated_at: string | null
}

export interface PromptTemplateDetail extends PromptTemplateListItem {
  system_prompt: string
  user_prompt_template: string
  temperature: number | null
  max_tokens: number | null
  variables: Array<{ name: string; description: string; required: boolean; default?: string }>
  output_format: string | null
  output_schema: Record<string, unknown> | null
  tts_voice: string | null
  tts_model: string | null
  tts_speed: number | null
  language: string | null
  target_audience: string | null
  difficulty_level: string | null
  lm_type: string | null
}

export interface PromptTemplateUpdate {
  title?: string
  description?: string
  system_prompt?: string
  user_prompt_template?: string
  model?: string
  provider?: string
  temperature?: number
  max_tokens?: number
  variables?: Array<{ name: string; description: string; required: boolean; default?: string }>
  is_active?: boolean
  is_default?: boolean
}

export async function listPromptTemplates(category?: string): Promise<PromptTemplateListItem[]> {
  const params = category ? { category } : {}
  const response = await http.get<{ success: boolean; templates: PromptTemplateListItem[] }>(
    '/panel/prompts',
    { params }
  )
  return response.data.templates
}

export async function getPromptTemplate(templateId: string): Promise<PromptTemplateDetail> {
  const response = await http.get<{ success: boolean; template: PromptTemplateDetail }>(
    `/panel/prompts/${templateId}`
  )
  return response.data.template
}

export async function updatePromptTemplate(
  templateId: string,
  data: PromptTemplateUpdate
): Promise<PromptTemplateDetail> {
  const response = await http.put<{ success: boolean; template: PromptTemplateDetail }>(
    `/panel/prompts/${templateId}`,
    data
  )
  return response.data.template
}

export async function deletePromptTemplate(templateId: string): Promise<void> {
  await http.delete(`/panel/prompts/${templateId}`)
}
