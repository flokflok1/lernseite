/**
 * Admin Exam Management API
 */

import http from '../http'
import type {
  Exam,
  ExamCreateRequest,
  ExamUpdateRequest,
  ExamGenerateRequest
} from './types'

export const adminListExams = async (courseId: string): Promise<Exam[]> => {
  const response = await http.get<{ success: boolean; exams: Exam[] }>(
    `/admin/courses/${courseId}/exams`
  )
  return response.data.exams
}

export const adminGetExam = async (examId: string): Promise<Exam> => {
  const response = await http.get<{ success: boolean; exam: Exam }>(
    `/admin/exams/${examId}`
  )
  return response.data.exam
}

export const adminCreateExam = async (
  courseId: string,
  data: ExamCreateRequest
): Promise<Exam> => {
  const response = await http.post<{ success: boolean; exam: Exam }>(
    `/admin/courses/${courseId}/exams`,
    data
  )
  return response.data.exam
}

export const adminUpdateExam = async (
  examId: string,
  data: ExamUpdateRequest
): Promise<Exam> => {
  const response = await http.patch<{ success: boolean; exam: Exam }>(
    `/admin/exams/${examId}`,
    data
  )
  return response.data.exam
}

export const adminDeleteExam = async (
  examId: string,
  reason?: string
): Promise<void> => {
  await http.delete(`/admin/exams/${examId}`, {
    data: { reason }
  })
}

export const adminGenerateExam = async (
  courseId: string,
  data: ExamGenerateRequest
): Promise<{ job_id: string; exam_id: string }> => {
  const response = await http.post<{
    success: boolean
    message: string
    job_id: string
    exam_id: string
  }>(`/admin/courses/${courseId}/exams/generate`, data)

  return {
    job_id: response.data.job_id,
    exam_id: response.data.exam_id
  }
}
