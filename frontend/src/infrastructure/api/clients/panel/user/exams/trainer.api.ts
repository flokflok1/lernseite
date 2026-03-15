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
    '/user/exams/trainer/exams'
  )
  return response.data.exams
}

export const trainerGetQuestions = async (examId: string): Promise<TrainerQuestion[]> => {
  const response = await http.get<{ success: boolean; questions: TrainerQuestion[] }>(
    `/user/exams/trainer/exams/${examId}/questions`
  )
  return response.data.questions
}

export const trainerGetTopics = async (): Promise<TopicStat[]> => {
  const response = await http.get<{ success: boolean; topics: TopicStat[] }>(
    '/user/exams/trainer/topics'
  )
  return response.data.topics
}

export const trainerGetTopicQuestions = async (topic: string): Promise<TrainerQuestion[]> => {
  const response = await http.get<{ success: boolean; questions: TrainerQuestion[] }>(
    `/user/exams/trainer/topics/${encodeURIComponent(topic)}/questions`
  )
  return response.data.questions
}

export const trainerSubmitAnswer = async (
  questionId: string,
  userAnswer: unknown
): Promise<AnswerResult> => {
  const response = await http.post<{ success: boolean } & AnswerResult>(
    '/user/exams/trainer/submit-answer',
    { question_id: questionId, user_answer: userAnswer }
  )
  return response.data
}

export const trainerStartExam = async (examId: string): Promise<string> => {
  const response = await http.post<{ success: boolean; attempt_id: string }>(
    `/user/exams/trainer/start-exam/${examId}`
  )
  return response.data.attempt_id
}

export const trainerCompleteAttempt = async (attemptId: string): Promise<AttemptResult> => {
  const response = await http.post<{ success: boolean } & AttemptResult>(
    `/user/exams/trainer/complete-attempt/${attemptId}`
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
  }>('/user/exams/trainer/practice-session', {
    exam_type: params.examType,
    topic: params.topic,
    count: params.count ?? 15,
  })
  return response.data.questions
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
