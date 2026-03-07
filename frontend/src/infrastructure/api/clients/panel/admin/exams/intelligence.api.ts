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
}

export interface TopicTaxonomy {
  topic_id: string
  exam_type: string
  topic_key: string
  topic_label: Record<string, string>
  parent_topic_id: string | null
  weight: number
}

// GET /admin/exam-intelligence/types
export const fetchExamTypes = async (): Promise<ExamType[]> => {
  const { data } = await http.get('/panel/admin/exam-intelligence/types')
  return data.types || []
}

// POST /admin/exam-intelligence/types
export const createExamType = async (payload: Partial<ExamType>): Promise<ExamType> => {
  const { data } = await http.post('/panel/admin/exam-intelligence/types', payload)
  return data
}

// PUT /admin/exam-intelligence/types/:exam_type
export const updateExamType = async (
  examType: string,
  payload: Partial<ExamType>
): Promise<ExamType> => {
  const { data } = await http.put(
    `/panel/admin/exam-intelligence/types/${examType}`,
    payload
  )
  return data
}

// DELETE /admin/exam-intelligence/types/:exam_type
export const deleteExamType = async (examType: string): Promise<void> => {
  await http.delete(`/panel/admin/exam-intelligence/types/${examType}`)
}

// GET /admin/exam-intelligence/topics/:exam_type
export const fetchTopics = async (examType: string): Promise<TopicTaxonomy[]> => {
  const { data } = await http.get(
    `/panel/admin/exam-intelligence/topics/${examType}`
  )
  return data.topics || []
}

// POST /admin/exam-intelligence/topics/:exam_type
export const createTopic = async (
  examType: string,
  payload: Partial<TopicTaxonomy>
): Promise<TopicTaxonomy> => {
  const { data } = await http.post(
    `/panel/admin/exam-intelligence/topics/${examType}`,
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
    `/panel/admin/exam-intelligence/topics/${examType}/${topicId}`,
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
    `/panel/admin/exam-intelligence/topics/${examType}/${topicId}`
  )
}
