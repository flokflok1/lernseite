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
  display_name?: Record<string, string>
  question_count: number
  attempts: number
  correct_count: number
  child_topics?: string[]
}

export interface AnswerResult {
  is_correct: boolean
  points_earned: number
  max_points?: number
  explanation: string | null
  correct_answer?: string
  needs_review?: boolean
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
  exam_id: string | null
  exam_title: string | null
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
  content_html: string
  data: Record<string, unknown>
}

export const trainerGetAnlagen = async (examId: string): Promise<Anlage[]> => {
  const response = await http.get<{ success: boolean; anlagen: Anlage[] }>(
    `/user/exam-trainer/exams/${examId}/anlagen`
  )
  return response.data.anlagen
}

export interface TrainerProgram {
  program_id: string
  title: string
  total_questions: number
  exam_count: number
  seen_questions: number
  mastered_questions: number
}

/** Dashboard response from GET /dashboard */
export interface TrainerDashboard {
  pool: {
    total_questions: number
    seen_questions: number
    mastered_questions: number
  }
  topics: TopicStat[]
  chapters: Array<{ chapter_id: string; title: string; order_index: number }>
  recent_attempts: AttemptHistoryEntry[]
}

/** Generated adaptive exam from POST /generate-exam */
export interface GeneratedExam {
  attempt_id: string
  questions: TrainerQuestion[]
  duration_minutes: number
  total_points: number
  question_count: number
}

/** Generate an adaptive exam using rotation algorithm */
export async function trainerGenerateExam(
  questionCount: number = 20,
  durationMinutes: number = 90,
): Promise<GeneratedExam> {
  const response = await http.post<{ success: boolean } & GeneratedExam>(
    '/user/exam-trainer/generate-exam',
    {
      question_count: questionCount,
      duration_minutes: durationMinutes,
    }
  )
  return response.data
}

/** Get available exam programs */
export async function trainerGetPrograms(): Promise<TrainerProgram[]> {
  const response = await http.get<{ success: boolean; programs: TrainerProgram[] }>(
    '/user/exam-trainer/programs'
  )
  return response.data.programs
}

/** Get dashboard data (pool stats + topics + recent attempts) */
export async function trainerGetDashboard(courseId?: string): Promise<TrainerDashboard> {
  const params = courseId ? `?course_id=${courseId}` : ''
  const response = await http.get<{ success: boolean } & TrainerDashboard>(
    `/user/exam-trainer/dashboard${params}`
  )
  return response.data
}

export interface TopicFrequency {
  topic: string
  display_name?: Record<string, string>
  exam_count: number
  question_count: number
  latest_year: number | null
  frequency_pct: number
}

/** Get topic frequency analysis across all exams */
export async function trainerGetTopicFrequency(): Promise<{ total_exams: number; topics: TopicFrequency[] }> {
  const response = await http.get<{ success: boolean; total_exams: number; topics: TopicFrequency[] }>(
    '/user/exam-trainer/topic-frequency'
  )
  return { total_exams: response.data.total_exams, topics: response.data.topics }
}

// -- Question Browser types & API --

export interface BrowseQuestion {
  question_id: string
  question_number: string
  question_text: string
  question_type: string
  points: number
  difficulty: string | null
  scenario_title: string | null
  topics: string[]
  exam_id: string
  exam_title: string
  year: number
  season: string
  times_seen: number | null
  times_correct: number | null
  last_seen_at: string | null
}

export interface BrowseResult {
  questions: BrowseQuestion[]
  total: number
  page: number
  per_page: number
}

export async function trainerBrowseQuestions(params: {
  topic?: string
  exam_id?: string
  status?: 'all' | 'unseen' | 'weak' | 'mastered'
  page?: number
  per_page?: number
}): Promise<BrowseResult> {
  const searchParams = new URLSearchParams()
  if (params.topic) searchParams.set('topic', params.topic)
  if (params.exam_id) searchParams.set('exam_id', params.exam_id)
  if (params.status) searchParams.set('status', params.status)
  if (params.page) searchParams.set('page', String(params.page))
  if (params.per_page) searchParams.set('per_page', String(params.per_page))

  const { data } = await http.get<{ success: boolean } & BrowseResult>(
    `/user/exam-trainer/questions/browse?${searchParams.toString()}`
  )
  return {
    questions: data.questions,
    total: data.total,
    page: data.page,
    per_page: data.per_page,
  }
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
