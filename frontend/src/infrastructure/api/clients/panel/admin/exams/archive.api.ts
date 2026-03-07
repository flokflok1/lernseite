/**
 * Admin Exam Archive API - IHK Exam Import & Analysis
 */

import http from '@/infrastructure/api/http'

export interface ScannedPaper {
  filename: string
  part: string
  season: string
  year: number
  profession: string
  is_solution: boolean
  full_path: string
}

export interface ArchiveExam {
  exam_id: string
  title: string
  semester: string
  year: number
  season: string
  part: string
  profession: string
  analysis_status: string
  question_count: number
  created_at: string
}

export interface ArchiveQuestion {
  question_id: string
  question_number: string
  question_text: string
  question_type: string
  scenario_title: string
  topics: string[]
  points: number
}

export const archiveScanFolder = async (): Promise<ScannedPaper[]> => {
  const response = await http.get<{ success: boolean; papers: ScannedPaper[] }>(
    '/admin/exams/archive/scan'
  )
  return response.data.papers
}

export const archiveImportPapers = async (
  papers: ScannedPaper[]
): Promise<{ imported: number; skipped: number }> => {
  const response = await http.post<{
    success: boolean
    imported: number
    skipped: number
  }>('/admin/exams/archive/import', { papers })
  return { imported: response.data.imported, skipped: response.data.skipped }
}

export const archiveAnalyzeExam = async (
  examId: string
): Promise<{ task_id: string }> => {
  const response = await http.post<{ success: boolean; task_id: string }>(
    `/admin/exams/archive/analyze/${examId}`
  )
  return { task_id: response.data.task_id }
}

export const archiveAnalyzeAll = async (): Promise<{ triggered: number }> => {
  const response = await http.post<{ success: boolean; triggered: number }>(
    '/admin/exams/archive/analyze-all'
  )
  return { triggered: response.data.triggered }
}

export const archiveListExams = async (
  status?: string
): Promise<ArchiveExam[]> => {
  const params = status ? { status } : {}
  const response = await http.get<{ success: boolean; exams: ArchiveExam[] }>(
    '/admin/exams/archive/list',
    { params }
  )
  return response.data.exams
}

export const archiveGetQuestions = async (
  examId: string
): Promise<ArchiveQuestion[]> => {
  const response = await http.get<{
    success: boolean
    questions: ArchiveQuestion[]
  }>(`/admin/exams/archive/${examId}/questions`)
  return response.data.questions
}

// --- Regions ---

export interface ExamRegion {
  region_code: string
  display_name: Record<string, string>
}

export const archiveListRegions = async (): Promise<ExamRegion[]> => {
  const response = await http.get<{ regions: ExamRegion[] }>(
    '/admin/exam-archive/regions'
  )
  return response.data.regions || []
}

// --- Session Grouping ---

export interface ExamSession {
  session_id: string
  year: number
  season: string
  tags: string[]
  exam_count: number
  ready_count: number
  total_questions: number
}

export interface SessionRegion {
  region_code: string
  region_name: Record<string, string> | null
  sessions: ExamSession[]
}

export interface SessionGroup {
  exam_type: string
  display_name: Record<string, string>
  parts: string[]
  regions: Record<string, SessionRegion>
}

export const archiveListSessions = async (
  examType?: string
): Promise<SessionGroup[]> => {
  const params = examType ? { exam_type: examType } : {}
  const response = await http.get<{ groups: SessionGroup[] }>(
    '/admin/exam-archive/sessions',
    { params }
  )
  return response.data.groups
}

export const archiveSessionExams = async (
  sessionId: string
): Promise<ArchiveExam[]> => {
  const response = await http.get<{ exams: ArchiveExam[] }>(
    `/admin/exam-archive/sessions/${sessionId}/exams`
  )
  return response.data.exams
}

export const archiveUpdateSessionTags = async (
  sessionId: string,
  tags: string[]
): Promise<void> => {
  await http.patch(`/admin/exam-archive/sessions/${sessionId}/tags`, { tags })
}

// --- Community Upload ---

export const communityUploadExam = async (
  file: File,
  metadata: {
    exam_type_key: string
    year: number
    season: string
    part?: string
    region?: string
  }
): Promise<{ exam_id: string; status: string }> => {
  const form = new FormData()
  form.append('file', file)
  form.append('exam_type_key', metadata.exam_type_key)
  form.append('year', String(metadata.year))
  form.append('season', metadata.season)
  if (metadata.part) form.append('part', metadata.part)
  if (metadata.region) form.append('region', metadata.region)

  const response = await http.post<{ exam_id: string; status: string }>(
    '/user/exam-upload/',
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return response.data
}

// --- Admin Moderation ---

export const archiveReviewUpload = async (
  examId: string,
  action: 'approve' | 'reject',
  notes?: string
): Promise<void> => {
  await http.post(`/admin/exam-archive/${examId}/review`, { action, notes })
}
