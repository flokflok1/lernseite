/**
 * Practice Session API Client
 *
 * Configurable practice mode with sequential/mixed ordering,
 * learning strategies, and intelligent features.
 */

import http from '@/infrastructure/api/http'

export interface PracticeSessionConfig {
  mode: 'discover' | 'strengthen' | 'exam_ready'
  order: 'sequential' | 'mixed'
  question_count?: number | null
  time_limit_minutes?: number | null
  exam_filter?: string[]
  topic_filter?: string[]
}

export interface PracticeSessionResponse {
  success: boolean
  attempt_id: string
  questions: PracticeQuestion[]
  total_available: number
  has_more: boolean
  config: {
    mode: string
    order: string
    question_count: number | null
  }
}

export interface PracticeQuestion {
  question_id: string
  exam_id: string
  question_number: string
  question_text: string
  question_type: string
  points: number
  topics: string[]
  data: Record<string, unknown>
  scenario_title: string | null
  scenario_text: string | null
  exam_title: string
  year: number
  season: string
  semester: string
}

export interface BatchResponse {
  success: boolean
  questions: PracticeQuestion[]
  has_more: boolean
  spaced_repeats: string[]
  streak_alert: StreakAlert | null
  difficulty_shift: 'up' | 'down' | 'stay'
}

export interface StreakAlert {
  topic: string
  consecutive_wrong: number
  suggested_extra: number
}

export interface PracticeSummary {
  total_questions: number
  correct: number
  overall_score: number
  time_spent_seconds: number
  topics: TopicResult[]
  strongest_topic: string
  weakest_topic: string
  recommendation: {
    type: 'strengthen_focus' | 'discover_more' | 'exam_ready'
    topic?: string
  }
}

export interface TopicResult {
  name: string
  total: number
  correct: number
  pct: number
}

export async function practiceGetQuestionCount(
  examFilter?: string[],
  topicFilter?: string[],
): Promise<number> {
  const params = new URLSearchParams()
  examFilter?.forEach(id => params.append('exam_filter', id))
  topicFilter?.forEach(t => params.append('topic_filter', t))
  const qs = params.toString()
  const url = qs ? `/user/exam-trainer/practice-config/count?${qs}` : '/user/exam-trainer/practice-config/count'
  const response = await http.get<{ success: boolean; count: number }>(url)
  return response.data.count
}

export async function practiceStartSession(
  config: PracticeSessionConfig,
): Promise<PracticeSessionResponse> {
  const response = await http.post<PracticeSessionResponse>(
    '/user/exam-trainer/practice-session',
    config,
  )
  return response.data
}

export async function practiceLoadNextBatch(
  attemptId: string,
  recentResults: Array<{ question_id: string; correct: boolean }>,
): Promise<BatchResponse> {
  const response = await http.post<BatchResponse>(
    `/user/exam-trainer/practice-session/${attemptId}/next-batch`,
    { recent_results: recentResults },
  )
  return response.data
}

export async function practiceGetSummary(
  attemptId: string,
): Promise<PracticeSummary> {
  const response = await http.get<{ success: boolean; summary: PracticeSummary }>(
    `/user/exam-trainer/practice-session/${attemptId}/summary`,
  )
  return response.data.summary
}
