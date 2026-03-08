/**
 * User Exam Goals API - Goal Management, Weakness & Curriculum Profiles
 */

import http from '@/infrastructure/api/http'

export interface ExamGoal {
  goal_id: string
  exam_type: string
  display_name: Record<string, string>
  status: 'active' | 'passed' | 'paused' | 'planned'
  target_date: string | null
  created_at: string
}

export interface TopicWeakness {
  topic_key: string
  score: number
  attempts: number
  trend: 'improving' | 'stable' | 'declining'
}

export interface WeaknessProfile {
  exam_type: string
  weaknesses: TopicWeakness[]
  overall_score: number
  recommendation: string
}

export interface CurriculumProfile {
  framework_id: number
  framework_name: string
  positions: CurriculumPositionProfile[]
}

export interface CurriculumPositionProfile {
  position_number: string
  title: string
  total_questions: number
  correct_count: number
  score_percent: number
}

// GET /user/exam-goals/
export const fetchExamGoals = async (): Promise<ExamGoal[]> => {
  const { data } = await http.get('/user/exam-goals/')
  return data.goals || []
}

// GET /user/exam-goals/available-types
export const fetchAvailableTypes = async (): Promise<any[]> => {
  const { data } = await http.get('/user/exam-goals/available-types')
  return data.exam_types || []
}

// POST /user/exam-goals/
export const createExamGoal = async (
  payload: { exam_type: string; target_date?: string }
): Promise<ExamGoal> => {
  const { data } = await http.post('/user/exam-goals/', payload)
  return data.goal
}

// PUT /user/exam-goals/:goalId/status
export const updateExamGoalStatus = async (
  goalId: string,
  status: string
): Promise<void> => {
  await http.put(`/user/exam-goals/${goalId}/status`, { status })
}

// DELETE /user/exam-goals/:goalId
export const deleteExamGoal = async (goalId: string): Promise<void> => {
  await http.delete(`/user/exam-goals/${goalId}`)
}

// GET /user/exam-goals/weakness-profile/:examType
export const fetchWeaknessProfile = async (
  examType: string
): Promise<WeaknessProfile> => {
  const { data } = await http.get(
    `/user/exam-goals/weakness-profile/${examType}`
  )
  return data.profile
}

// GET /user/exam-goals/curriculum-profile/:examTypeKey
export const fetchCurriculumProfile = async (
  examTypeKey: string
): Promise<CurriculumProfile> => {
  const { data } = await http.get(
    `/user/exam-goals/curriculum-profile/${examTypeKey}`
  )
  return data.profile
}
