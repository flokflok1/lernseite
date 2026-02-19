/**
 * User Domain - Extended Types (Part 2)
 * ======================================
 *
 * Types for user-facing APIs that were previously in the system domain:
 * - Tokens (balance, transactions, usage)
 * - Subscriptions (plans, status)
 * - Audio (transcription, oral analysis)
 * - Text-to-Speech (TTS, voices, tutor scripts)
 * - Tutor (chat, knowledge base)
 * - Gamification (XP, stats, achievements)
 * - Exam Simulation (exams, attempts, results)
 * - Math Toolkit (patterns, formulas, sessions)
 */

// ============================================================================
// Tokens API Types
// ============================================================================

export interface TokenBalanceResponse {
  balance: number
  reserved: number
  available: number
  total_purchased: number
  total_granted: number
  total_consumed: number
  monthly_grant: number | null
  last_grant_date: string | null
  source: 'user' | 'organisation'
}

export interface TokenTransactionItem {
  transaction_id: number
  amount: number
  balance_after: number
  reason: string
  description: string
  created_at: string
}

export interface TokenUsageResponse {
  user_id: number
  current_balance: number
  total_tokens_used: number
  total_tokens_bought: number
  total_tokens_granted: number
  by_reason: Record<string, number>
  by_method: Record<string, number>
  period_start: string
  period_end: string
}

// ============================================================================
// Subscriptions API Types
// ============================================================================

export interface SubscriptionPlan {
  plan_id: string
  name: string
  tier: 'free' | 'premium' | 'pro'
  price: number
  currency: string
  billing_cycle: 'monthly' | 'yearly'
  features: string[]
  token_monthly_grant: number
  max_courses: number
  max_students?: number
}

export interface SubscriptionResponse {
  subscription_id?: string
  plan_id: string
  plan_name: string
  status: 'active' | 'cancelled' | 'expired'
  started_at: string
  expires_at?: string
  auto_renew: boolean
  current_period_start: string
  current_period_end: string
}

// ============================================================================
// Audio API Types
// ============================================================================

export interface TranscriptionResult {
  text: string
  duration_seconds: number
  language: string
  confidence: number
  words: Array<{
    word: string
    start_time: number
    end_time: number
  }>
}

export interface OralAnalysisResult {
  phoneme_accuracy: number
  prosody_score: number
  fluency_score: number
  overall_score: number
  feedback: string
  corrections: Array<{
    position: number
    current: string
    suggested: string
  }>
}

export interface AudioFormatsResponse {
  supported_formats: string[]
  max_file_size_mb: number
  sample_rates: number[]
}

// ============================================================================
// Text-to-Speech (TTS) API Types
// ============================================================================

export interface TTSSpeakRequest {
  text: string
  voice: string
  language?: string
  speed?: number
  pitch?: number
}

export interface TTSSpeakResponse {
  audio_url: string
  duration_seconds: number
  format: string
}

export interface VoiceInfo {
  voice_id: string
  name: string
  language: string
  gender?: string
  accent?: string
}

export interface VoicesResponse {
  voices: VoiceInfo[]
  default_voice: string
}

export interface TutorScriptStep {
  text: string
  duration_seconds?: number
  voice?: string
}

export interface TutorScriptRequest {
  topic: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  script_length: 'short' | 'medium' | 'long'
  language: string
}

export interface TutorScriptResultStep {
  text: string
  audio_url: string
  duration_seconds: number
  timestamp: number
}

export interface TutorScriptResponse {
  script_id: string
  topic: string
  steps: TutorScriptResultStep[]
  total_duration_seconds: number
}

export type PiperVoiceKey = string
export type OpenAIVoiceKey = string

export interface TutorKnowledgeRequest {
  course_id: string
  chapter_ids?: string[]
  level: 'beginner' | 'intermediate' | 'advanced'
  include_examples: boolean
  include_formulas: boolean
}

export interface CourseContext {
  course_id: string
  title: string
  description: string
  chapters: Array<{
    chapter_id: string
    title: string
    key_concepts: string[]
  }>
}

export interface ChapterContext {
  chapter_id: string
  title: string
  course_title: string
  lessons: Array<{
    lesson_id: string
    title: string
    key_concepts: string[]
  }>
}

export interface TutorKnowledgeResponse {
  knowledge_base_id: string
  context: CourseContext | ChapterContext
  key_points: string[]
  learning_objectives: string[]
  summary: string
}

// ============================================================================
// Tutor API Types
// ============================================================================

export interface TutorChatRequest {
  message: string
  context: 'course' | 'chapter' | 'lesson'
  context_id: string
  conversation_id?: string
  user_level?: 'beginner' | 'intermediate' | 'advanced'
}

export interface TutorChatResponse {
  reply: string
  conversation_id: string
  suggestions: string[]
  references?: string[]
}

export interface TutorTTSRequest {
  text: string
  voice: string
  language: string
}

// ============================================================================
// Gamification API Types
// ============================================================================

export interface BaseStats {
  total_xp: number
  level: number
  badges: string[]
  achievements: string[]
}

export interface GamificationData {
  user_id: string
  stats: BaseStats
  current_streak: number
  best_streak: number
  total_challenges_completed: number
  leaderboard_position: number
  profile_level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
}

export interface GamificationApiResponse {
  success: boolean
  data: GamificationData
}

// ============================================================================
// Exam Simulation API Types
// ============================================================================

export interface TopicScore {
  topic: string
  score: number
  max_score: number
  percentage: number
}

export interface ExamContext {
  exam_id: string
  exam_type: 'practice' | 'mock' | 'final'
  subject: string
  topics: string[]
  difficulty_level: 'easy' | 'medium' | 'hard'
  time_limit_minutes: number
  total_questions: number
  passing_score: number
}

export interface ExamSimulationConfig {
  exam_id: string
  title: string
  description: string
  duration_minutes: number
  total_questions: number
  passing_percentage: number
  show_answers: boolean
  randomize_questions: boolean
}

export interface ExamQuestion {
  question_id: string
  question_text: string
  question_type: 'multiple_choice' | 'short_answer' | 'essay'
  options?: string[]
  correct_answer?: string
  points: number
}

export interface ExamSimulation {
  simulation_id: string
  config: ExamSimulationConfig
  questions: ExamQuestion[]
  created_at: string
  expires_at?: string
}

export interface ExamAttempt {
  attempt_id: string
  user_id: string
  exam_id: string
  start_time: string
  end_time?: string
  status: 'in_progress' | 'completed' | 'abandoned'
  score: number
  percentage: number
  topic_scores: TopicScore[]
}

export interface SubmitAnswers {
  attempt_id: string
  answers: Array<{
    question_id: string
    answer: string
  }>
}

export interface AttemptResult {
  attempt_id: string
  score: number
  percentage: number
  passed: boolean
  topic_scores: TopicScore[]
  feedback: string
  time_taken_minutes: number
}

export interface UserExamProfile {
  user_id: string
  total_attempts: number
  average_score: number
  best_score: number
  pass_rate: number
  favorite_subject: string
  weak_topics: string[]
}

// ============================================================================
// Math Toolkit API Types
// ============================================================================

export interface MathCategory {
  category_id: string
  name: string
  description: string
  icon?: string
  patterns_count: number
}

export interface MathPattern {
  pattern_id: string
  name: string
  description: string
  formula: string
  category: string
  difficulty: 'easy' | 'medium' | 'hard'
  variables: PatternVariable[]
  steps: PatternStep[]
  examples?: string[]
}

export interface PatternVariable {
  var_name: string
  description: string
  constraints?: string
}

export interface PatternStep {
  step_number: number
  description: string
  formula: string
  explanation?: string
}

export interface MathFormula {
  formula_id: string
  latex: string
  description: string
  category: string
  difficulty: string
  solved_example?: string
}

export interface MathSession {
  session_id: string
  user_id: string
  pattern_id: string
  start_time: string
  end_time?: string
  status: 'in_progress' | 'completed'
  score: number
  steps_taken: number
}

export interface CalculationStep {
  step_id: string
  step_number: number
  input: string
  output: string
  is_correct: boolean
  feedback?: string
}

export interface UserProgress {
  user_id: string
  patterns_learned: number
  patterns_mastered: number
  total_sessions: number
  average_score: number
  current_streak: number
}

export interface PatternTask {
  task_id: string
  pattern_id: string
  problem: string
  difficulty: string
}

export interface CalculatorEntry {
  entry_id: string
  expression: string
  result: string
  timestamp: string
}
