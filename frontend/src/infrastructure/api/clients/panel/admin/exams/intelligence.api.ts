/**
 * Admin Exam Intelligence API - Exam Types & Topic Taxonomy Management
 */

import http from '@/infrastructure/api/http'

export interface ExamType {
  exam_type: string
  display_name: Record<string, string>
  passing_score: number
  parts: string[] | null
  settings: Record<string, any> | null
  program_id: number | null
  applies_to: string[]
  sort_order: number
}

export interface ExamProgram {
  program_id: number
  program_key: string
  display_name: Record<string, string>
  program_type: 'ausbildung' | 'zertifizierung' | 'studium' | 'custom'
  provider: string | null
  icon: string | null
  sort_order: number
  parts: ExamType[]
}

export interface TopicTaxonomy {
  topic_id: string
  exam_type: string
  topic_key: string
  topic_label: Record<string, string>
  parent_topic_id: string | null
  weight: number
}

// GET /admin/exam-intelligence/programs
export const fetchPrograms = async (): Promise<ExamProgram[]> => {
  const { data } = await http.get('/admin/exam-intelligence/programs')
  return data.programs || []
}

// GET /admin/exam-intelligence/types
export const fetchExamTypes = async (): Promise<ExamType[]> => {
  const { data } = await http.get('/admin/exam-intelligence/types')
  return data.exam_types || data.types || []
}

// POST /admin/exam-intelligence/types
export const createExamType = async (payload: Partial<ExamType>): Promise<ExamType> => {
  const { data } = await http.post('/admin/exam-intelligence/types', payload)
  return data
}

// PUT /admin/exam-intelligence/types/:exam_type
export const updateExamType = async (
  examType: string,
  payload: Partial<ExamType>
): Promise<ExamType> => {
  const { data } = await http.put(
    `/admin/exam-intelligence/types/${examType}`,
    payload
  )
  return data
}

// DELETE /admin/exam-intelligence/types/:exam_type
export const deleteExamType = async (examType: string): Promise<void> => {
  await http.delete(`/admin/exam-intelligence/types/${examType}`)
}

// GET /admin/exam-intelligence/topics/:exam_type
export const fetchTopics = async (examType: string): Promise<TopicTaxonomy[]> => {
  const { data } = await http.get(
    `/admin/exam-intelligence/topics/${examType}`
  )
  return data.topics || []
}

// POST /admin/exam-intelligence/topics/:exam_type
export const createTopic = async (
  examType: string,
  payload: Partial<TopicTaxonomy>
): Promise<TopicTaxonomy> => {
  const { data } = await http.post(
    `/admin/exam-intelligence/topics/${examType}`,
    payload
  )
  return data
}

// PUT /admin/exam-intelligence/topics/:exam_type/:topic_id
export const updateTopic = async (
  examType: string,
  topicId: string,
  payload: Partial<TopicTaxonomy>
): Promise<TopicTaxonomy> => {
  const { data } = await http.put(
    `/admin/exam-intelligence/topics/${examType}/${topicId}`,
    payload
  )
  return data
}

// DELETE /admin/exam-intelligence/topics/:exam_type/:topic_id
export const deleteTopic = async (
  examType: string,
  topicId: string
): Promise<void> => {
  await http.delete(
    `/admin/exam-intelligence/topics/${examType}/${topicId}`
  )
}
