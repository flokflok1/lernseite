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

// --- Analysis Status ---

export interface AnalysisStatus {
  pending: number
  analyzing: number
  ready: number
  failed: number
  total: number
  queue: Array<{ exam_id: string; title: string; status: string }>
}

export async function archiveGetAnalysisStatus(): Promise<AnalysisStatus> {
  const { data } = await http.get<AnalysisStatus>('/admin/exam-archive/analysis-status')
  return data
}

export const archiveScanFolder = async (): Promise<ScannedPaper[]> => {
  const response = await http.get<{ success: boolean; papers: ScannedPaper[] }>(
    '/admin/exam-archive/scan'
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
  }>('/admin/exam-archive/import', { papers })
  return { imported: response.data.imported, skipped: response.data.skipped }
}

export const archiveAnalyzeExam = async (
  examId: string
): Promise<{ task_id: string }> => {
  const response = await http.post<{ success: boolean; task_id: string }>(
    `/admin/exam-archive/analyze/${examId}`
  )
  return { task_id: response.data.task_id }
}

export const archiveAnalyzeAll = async (): Promise<{ triggered: number }> => {
  const response = await http.post<{ success: boolean; triggered: number }>(
    '/admin/exam-archive/analyze-all'
  )
  return { triggered: response.data.triggered }
}

export const archiveListExams = async (
  status?: string
): Promise<ArchiveExam[]> => {
  const params = status ? { status } : {}
  const response = await http.get<{ success: boolean; exams: ArchiveExam[] }>(
    '/admin/exam-archive/list',
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
  }>(`/admin/exam-archive/${examId}/questions`)
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

// --- Session Rows (flat data for client-side tree building) ---

export interface SessionRow {
  program_key: string
  program_name: Record<string, string>
  provider: string
  icon: string
  program_sort: number
  region: string
  region_name: Record<string, string>
  exam_type: string
  type_display_name: Record<string, string>
  type_sort: number
  session_id: string
  year: number
  season: string
  exam_count: number
  ready_count: number
  total_questions: number
}

export const archiveListSessions = async (
  programKey?: string
): Promise<SessionRow[]> => {
  const params = programKey ? { program_key: programKey } : {}
  const response = await http.get<{ rows: SessionRow[] }>(
    '/admin/exam-archive/sessions',
    { params }
  )
  return response.data.rows || []
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

// --- CRUD: Sessions (folders) ---

export const archiveCreateSession = async (
  examTypeKey: string,
  year: number,
  season: string,
  region?: string
): Promise<{ session_id: string }> => {
  const response = await http.post<{ session_id: string }>(
    '/admin/exam-archive/sessions',
    { exam_type_key: examTypeKey, year, season, region }
  )
  return response.data
}

export const archiveDeleteSession = async (
  sessionId: string
): Promise<void> => {
  await http.delete(`/admin/exam-archive/sessions/${sessionId}`)
}

// --- CRUD: Exams (files) ---

export const archiveMoveExam = async (
  examId: string,
  targetSessionId: string
): Promise<void> => {
  await http.patch(`/admin/exam-archive/exams/${examId}/move`, {
    target_session_id: targetSessionId,
  })
}

export const archiveDeleteExam = async (
  examId: string
): Promise<void> => {
  await http.delete(`/admin/exam-archive/exams/${examId}`)
}

// --- Re-Analyze ---

export const archiveReAnalyzeExam = async (
  examId: string
): Promise<void> => {
  await http.put(`/admin/exam-archive/${examId}/re-analyze`)
}

export const archiveReAnalyzeAll = async (): Promise<{ count: number }> => {
  const { data } = await http.put<{ count: number }>(
    '/admin/exam-archive/re-analyze-all'
  )
  return data
}

// --- Admin Moderation ---

export const archiveReviewUpload = async (
  examId: string,
  action: 'approve' | 'reject',
  notes?: string
): Promise<void> => {
  await http.post(`/admin/exam-archive/${examId}/review`, { action, notes })
}

// --- Image Import ---

/** Import multiple images as a single exam */
export const archiveImportImages = async (
  files: File[],
  folderId?: string,
  title?: string
): Promise<{ exam_id: string; title: string; page_count: number; status: string }> => {
  const form = new FormData()
  files.forEach((f) => form.append('files[]', f))
  if (folderId) form.append('folder_id', folderId)
  if (title) form.append('title', title)
  const { data } = await http.post<{
    exam_id: string
    title: string
    page_count: number
    status: string
  }>('/admin/exam-archive/import-images', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
