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
