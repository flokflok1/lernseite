/**
 * Admin Curriculum Framework API
 *
 * Endpoints for managing curriculum frameworks, AI PDF import,
 * question-objective mapping, and coverage statistics.
 */

import http from '@/infrastructure/api/http'

// --- Types ---

export interface CurriculumFramework {
  framework_id: number
  name: string
  framework_type: string
  source_document: string | null
  display_name: Record<string, string>
  version: string | null
  created_at: string
}

export interface CurriculumObjective {
  objective_id: number
  code: string
  description_text: string
  bloom_level: string | null
}

export interface CurriculumPosition {
  position_id: number
  position_number: string
  title: string
  objectives: CurriculumObjective[]
}

export interface CurriculumSection {
  section_id: number
  section_number: string
  title: string
  positions: CurriculumPosition[]
}

export interface CurriculumTree extends CurriculumFramework {
  sections: CurriculumSection[]
}

export interface CurriculumTag {
  question_id: string
  objective_id: number
  confidence: number
  tagged_by: string
}

export interface CoverageStats {
  total_objectives: number
  mapped_objectives: number
  coverage_percent: number
  unmapped_count: number
}

export interface AutoMapStats {
  mapped: number
  skipped: number
  errors: number
}

// --- Framework CRUD ---

export const fetchFrameworks = async (): Promise<CurriculumFramework[]> => {
  const { data } = await http.get('/admin/curriculum/frameworks')
  return data.frameworks || []
}

export const fetchFrameworkTree = async (
  frameworkId: number
): Promise<CurriculumTree | null> => {
  const { data } = await http.get(
    `/admin/curriculum/frameworks/${frameworkId}`
  )
  return data.framework || null
}

export const createFramework = async (
  payload: Partial<CurriculumFramework>
): Promise<CurriculumFramework> => {
  const { data } = await http.post(
    '/admin/curriculum/frameworks',
    payload
  )
  return data.framework
}

export const deleteFramework = async (
  frameworkId: number
): Promise<void> => {
  await http.delete(`/admin/curriculum/frameworks/${frameworkId}`)
}

// --- AI PDF Import ---

export const importPdfPreview = async (
  pdfText: string,
  provider?: string,
  model?: string,
): Promise<Record<string, any>> => {
  const { data } = await http.post(
    '/admin/curriculum/frameworks/import-pdf',
    { pdf_text: pdfText, provider, model }
  )
  return data.preview
}

export const importPdfFilePreview = async (
  file: File,
  provider?: string,
  model?: string,
): Promise<Record<string, any>> => {
  const formData = new FormData()
  formData.append('file', file)
  if (provider) formData.append('provider', provider)
  if (model) formData.append('model', model)

  const { data } = await http.post(
    '/admin/curriculum/frameworks/import-pdf-upload',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return data.preview
}

export const importPdfConfirm = async (
  aiResult: Record<string, any>,
  sourceDocument?: string
): Promise<CurriculumFramework> => {
  const { data } = await http.post(
    '/admin/curriculum/frameworks/import-confirm',
    { ai_result: aiResult, source_document: sourceDocument }
  )
  return data.framework
}

// --- Framework <-> Exam Type ---

export const linkFrameworkToExamType = async (
  frameworkId: number,
  examTypeKey: string
): Promise<void> => {
  await http.post(
    `/admin/curriculum/frameworks/${frameworkId}/link/${examTypeKey}`
  )
}

// --- Auto-mapping ---

export const autoMapQuestions = async (
  examTypeKey: string
): Promise<AutoMapStats> => {
  const { data } = await http.post(
    `/admin/curriculum/auto-map/${examTypeKey}`
  )
  return data.stats
}

// --- Question Tags ---

export const fetchQuestionTags = async (
  questionId: string
): Promise<CurriculumTag[]> => {
  const { data } = await http.get(
    `/admin/curriculum/questions/${questionId}/tags`
  )
  return data.tags || []
}

export const addQuestionTag = async (
  questionId: string,
  objectiveId: number,
  confidence?: number
): Promise<CurriculumTag> => {
  const { data } = await http.post(
    `/admin/curriculum/questions/${questionId}/tags`,
    { objective_id: objectiveId, confidence: confidence ?? 1.0 }
  )
  return data.tag
}

export const removeQuestionTag = async (
  questionId: string,
  objectiveId: number
): Promise<void> => {
  await http.delete(
    `/admin/curriculum/questions/${questionId}/tags/${objectiveId}`
  )
}

// --- Coverage & Relevance ---

export const fetchCoverageStats = async (
  frameworkId: number
): Promise<CoverageStats> => {
  const { data } = await http.get(
    `/admin/curriculum/frameworks/${frameworkId}/coverage`
  )
  return data.coverage
}

export const fetchRelevanceWeights = async (
  frameworkId: number
): Promise<Record<string, any>> => {
  const { data } = await http.get(
    `/admin/curriculum/frameworks/${frameworkId}/relevance`
  )
  return data.relevance
}
