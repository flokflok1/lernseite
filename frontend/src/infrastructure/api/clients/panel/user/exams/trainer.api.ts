/**
 * Exam Trainer API Client
 *
 * User-facing API for practicing with IHK exam questions.
 * Supports exam-based and topic-based practice modes.
 */

import http from '@/infrastructure/api/http'

export interface TrainerExam {
  exam_id: string
  title: string
  semester: string
  year: number
  season: string
  part: string
  question_count: number
  analysis_status: string
  duration_minutes: number | null
  total_points: number | null
  passing_score: number | null
}

export interface TrainerQuestion {
  question_id: string
  question_number: string
  question_text: string
  question_type: string
  scenario_title: string | null
  scenario_text: string | null
  topics: string[]
  points: number
  data: Record<string, unknown>
}

export interface TopicStat {
  topic: string
  question_count: number
  attempts: number
  correct_count: number
}

export interface AnswerResult {
  correct: boolean
  earned_points: number
  max_points: number
  explanation: string | null
}

export interface AttemptResult {
  score: number
  total_points: number
  percentage: number
  passed: boolean
}

export interface GeneratedExamData {
  exam_id: string
  title: string
  questions: TrainerQuestion[]
  question_count: number
}

export const trainerListExams = async (): Promise<TrainerExam[]> => {
  const response = await http.get<{ success: boolean; exams: TrainerExam[] }>(
    '/user/exam-trainer/exams'
  )
  return response.data.exams
}

export const trainerGetQuestions = async (examId: string): Promise<TrainerQuestion[]> => {
  const response = await http.get<{ success: boolean; questions: TrainerQuestion[] }>(
    `/user/exam-trainer/exams/${examId}/questions`
  )
  return response.data.questions
}

export const trainerGetTopics = async (): Promise<TopicStat[]> => {
  const response = await http.get<{ success: boolean; topics: TopicStat[] }>(
    '/user/exam-trainer/topics'
  )
  return response.data.topics
}

export const trainerGetTopicQuestions = async (topic: string): Promise<TrainerQuestion[]> => {
  const response = await http.get<{ success: boolean; questions: TrainerQuestion[] }>(
    `/user/exam-trainer/topics/${encodeURIComponent(topic)}/questions`
  )
  return response.data.questions
}

export const trainerSubmitAnswer = async (
  questionId: string,
  userAnswer: unknown
): Promise<AnswerResult> => {
  const response = await http.post<{ success: boolean } & AnswerResult>(
    '/user/exam-trainer/submit-answer',
    { question_id: questionId, user_answer: userAnswer }
  )
  return response.data
}

export const trainerStartExam = async (examId: string): Promise<string> => {
  const response = await http.post<{ success: boolean; attempt_id: string }>(
    `/user/exam-trainer/start-exam/${examId}`
  )
  return response.data.attempt_id
}

export const trainerCompleteAttempt = async (attemptId: string): Promise<AttemptResult> => {
  const response = await http.post<{ success: boolean } & AttemptResult>(
    `/user/exam-trainer/complete-attempt/${attemptId}`
  )
  return response.data
}

export interface PracticeSessionParams {
  examType: string
  topic?: string
  count?: number
}

export const trainerPracticeSession = async (
  params: PracticeSessionParams
): Promise<TrainerQuestion[]> => {
  const response = await http.post<{
    success: boolean
    questions: TrainerQuestion[]
    session_info: { total: number; topic: string | null }
  }>('/user/exam-trainer/practice-session', {
    exam_type: params.examType,
    topic: params.topic,
    count: params.count ?? 15,
  })
  return response.data.questions
}

export interface ReviewQuestion {
  question_id: string
  question_text: string
  question_type: string
  question_number: string
  scenario_title: string | null
  scenario_text: string | null
  topics: string[]
  data: Record<string, unknown>
  solution: Record<string, unknown> | null
  user_answer: unknown
  is_correct: boolean | null
  points_earned: number
  max_points: number
  needs_review: boolean
}

export interface AttemptHistoryEntry {
  attempt_id: string
  exam_id: string
  exam_title: string
  score: number | null
  total_points: number | null
  percentage: number | null
  passed: boolean | null
  started_at: string
  completed_at: string
}

export const trainerGetAttemptReview = async (
  attemptId: string
): Promise<ReviewQuestion[]> => {
  const response = await http.get<{ success: boolean; questions: ReviewQuestion[] }>(
    `/user/exam-trainer/attempt/${attemptId}/review`
  )
  return response.data.questions
}

export const trainerGetHistory = async (
  limit: number = 20
): Promise<AttemptHistoryEntry[]> => {
  const response = await http.get<{ success: boolean; attempts: AttemptHistoryEntry[] }>(
    `/user/exam-trainer/history?limit=${limit}`
  )
  return response.data.attempts
}

export interface Anlage {
  number: number
  title: string
  type: 'offer' | 'api_reference' | 'info_document' | 'generic'
  raw_text: string
  data: Record<string, unknown>
}

export const trainerGetAnlagen = async (examId: string): Promise<Anlage[]> => {
  const response = await http.get<{ success: boolean; anlagen: Anlage[] }>(
    `/user/exam-trainer/exams/${examId}/anlagen`
  )
  return response.data.anlagen
}

export const generatePracticeExam = async (params: {
  examType: string
  difficulty: string
  focusWeakness: boolean
  questionCount: number
}): Promise<GeneratedExamData> => {
  const response = await http.post<{ success: boolean } & GeneratedExamData>(
    '/system-features/exam/question-generator/generate-practice',
    {
      exam_type: params.examType,
      difficulty: params.difficulty,
      focus_weakness: params.focusWeakness,
      question_count: params.questionCount,
    }
  )
  return response.data
}
