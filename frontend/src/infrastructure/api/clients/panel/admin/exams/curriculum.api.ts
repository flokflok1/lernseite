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

export interface CoveragePositionDetail {
  section_id: number
  section_code: string
  section_title: string | Record<string, string>
  position_id: number
  position_code: string
  position_title: string | Record<string, string>
  question_count: number
  objective_count: number
  ai_tagged_count: number
}

export interface CoverageStats {
  total_objectives: number
  mapped_objectives: number
  coverage_percent: number
  unmapped_count: number
  positions?: CoveragePositionDetail[]
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

export interface ImportProgressEvent {
  event: 'extracting' | 'extracted' | 'ai_started' | 'ai_progress' | 'log' | 'complete' | 'error'
  data: Record<string, any>
}

export const importPdfFileStreaming = async (
  file: File,
  provider: string | undefined,
  model: string | undefined,
  onProgress: (event: ImportProgressEvent) => void,
): Promise<Record<string, any> | null> => {
  const formData = new FormData()
  formData.append('file', file)
  if (provider) formData.append('provider', provider)
  if (model) formData.append('model', model)

  // Get auth token
  let token: string | null = null
  try {
    const { useAuthStore } = await import('@/application/stores/modules/core/auth.store')
    token = useAuthStore().accessToken
  } catch { /* ignore */ }
  if (!token) token = localStorage.getItem('access_token')

  const baseUrl = '/api/v1'
  const response = await fetch(
    `${baseUrl}/admin/curriculum/frameworks/import-pdf-upload`,
    {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        'Accept': 'text/event-stream',
      },
      body: formData,
    },
  )

  if (!response.ok || !response.body) {
    throw new Error(`Upload failed: ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let result: Record<string, any> | null = null
  // Declared outside loop — event: and data: may arrive in separate chunks
  let currentEvent = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim()
      } else if (line.startsWith('data: ') && currentEvent) {
        try {
          const data = JSON.parse(line.slice(6))
          const evt: ImportProgressEvent = { event: currentEvent as any, data }
          onProgress(evt)

          if (currentEvent === 'complete' && data.preview) {
            result = data.preview
          }
          if (currentEvent === 'error') {
            throw new Error(data.message || 'Import failed')
          }
        } catch (e) {
          if (e instanceof Error && e.message !== 'Import failed') {
            console.error('SSE parse error:', e)
          } else {
            throw e
          }
        }
        currentEvent = ''
      }
    }
  }

  return result
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

export interface RelevanceEntry {
  position_id: number
  exam_count: number
  total_exams: number
  appearance_rate: number
  weighted_score: number
  avg_points_per_exam: number
  recent_count: number
  older_count: number
  trend: 'rising' | 'stable' | 'declining'
}

export const fetchRelevanceWeights = async (
  frameworkId: number
): Promise<RelevanceEntry[]> => {
  const { data } = await http.get(
    `/admin/curriculum/frameworks/${frameworkId}/relevance`
  )
  return data.relevance
}

// --- Coverage Report ---

export interface CoverageReportPosition {
  position_id: string
  code: string
  title: string
  question_count: number
  objective_count: number
  coverage_percent: number
  relevance_score: number
  trend: 'rising' | 'stable' | 'declining'
  has_questions: boolean
  gap: boolean
}

export interface CoverageReportSummary {
  total_positions: number
  covered_positions: number
  gap_positions: number
  coverage_percent: number
  low_confidence_count: number
}

export interface CoverageReportData {
  positions: CoverageReportPosition[]
  summary: CoverageReportSummary
}

export const fetchCoverageReport = async (
  frameworkId: number
): Promise<CoverageReportData> => {
  const { data } = await http.get(
    `/admin/exams/curriculum/frameworks/${frameworkId}/coverage-report`
  )
  return data
}
