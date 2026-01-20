/**
 * Learning Domain - Centralized Types
 * 
 * This file exports all types used in the Learning domain (player, editor, authoring)
 * to provide a single source of truth for type definitions.
 */

// ============================================================================
// Player API Types
// ============================================================================

export interface Course {
  course_id: string
  title: string
  subtitle?: string
  description: string
  category?: string
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  language: string
  thumbnail_url?: string
  creator_id: number
  creator_name?: string
  is_published: boolean
  tags?: string[]
  learning_goals?: string[]
  requirements?: string[]
  total_chapters?: number
  total_lessons?: number
  total_duration_minutes?: number
  created_at: string
  updated_at?: string
}

export interface Chapter {
  chapter_id: string
  course_id: string
  title: string
  description?: string
  order: number
  duration_minutes?: number
  lessons?: Lesson[]
  is_published: boolean
  created_at: string
}

export interface Lesson {
  lesson_id: string
  chapter_id: string
  course_id: string
  title: string
  description?: string
  order: number
  lesson_type: 'text' | 'video' | 'quiz' | 'ai' | 'mixed'
  content: any
  duration_minutes?: number
  is_published: boolean
  created_at: string
}

export interface LessonProgress {
  lesson_id: string
  user_id: string
  status: 'not_started' | 'in_progress' | 'completed'
  progress_percentage: number
  time_spent_minutes: number
  started_at?: string
  completed_at?: string
  last_accessed_at?: string
}

export interface ChapterProgress {
  chapter_id: string
  user_id: number
  status: 'not_started' | 'in_progress' | 'completed'
  progress_percentage: number
  lessons_completed: number
  total_lessons: number
  started_at?: string
  completed_at?: string
}

export interface CourseProgress {
  course_id: string
  user_id: number
  enrollment_id: number
  status: 'active' | 'completed' | 'cancelled'
  progress_percentage: number
  chapters_completed: number
  total_chapters: number
  lessons_completed: number
  total_lessons: number
  last_accessed_at?: string
  enrolled_at: string
  completed_at?: string
}

export interface LearningMethod {
  method_id: number
  method_name: string
  category: 'basis' | 'premium' | 'pro'
  description: string
  requires_ai: boolean
  token_cost: number
  is_premium: boolean
  icon?: string
  config?: any
}

export interface ExecuteMethodRequest {
  lesson_id: string | number
  method_id: number
  input_data?: any
}

export interface ExecuteMethodResponse {
  success: boolean
  method_execution_id: number
  result: any
  tokens_used: number
  processing_time_ms: number
  message?: string
}

export interface AnalyticsEventRequest {
  event_type: string
  resource_type: string
  resource_id: number | string
  metadata?: any
}

export type QuizQuestionType = 'single_choice' | 'multiple_choice' | 'true_false' | 'fill_blank' | 'matching'

export interface QuizQuestionOption {
  id: string | number
  text: string
  is_correct?: boolean
}

export interface QuizQuestion {
  question_id: number
  type: QuizQuestionType
  question_text: string
  points: number
  options?: QuizQuestionOption[]
}

export interface QuizData {
  quiz_id: number
  lesson_id: number
  title: string
  description?: string
  questions: QuizQuestion[]
  passing_percentage: number
  allow_retry: boolean
}

export interface QuizAnswerSubmission {
  question_id: number
  answer: any
  time_spent_seconds: number
}

export interface QuizSubmitRequest {
  quiz_id: number
  answers: QuizAnswerSubmission[]
}

export interface QuizQuestionResult {
  question_id: number
  is_correct: boolean
  points_earned: number
  user_answer: any
  correct_answer: any
  explanation?: string
}

export interface QuizResult {
  quiz_id: number
  passed: boolean
  score: number
  total_points: number
  percentage: number
  questions: QuizQuestionResult[]
  completed_at: string
}

export interface SavedTaskExecution {
  execution_id: number
  lesson_id: number
  method_id: number
  result: any
  created_at: string
}

// ============================================================================
// AI Editor Types
// ============================================================================

export type SessionStatus = 'draft' | 'in_progress' | 'review' | 'completed' | 'cancelled'
export type SourceType = 'manual' | 'pdf' | 'url' | 'existing_chapter' | 'template'
export type VariantType = 'theory' | 'lesson' | 'method' | 'quiz' | 'summary' | 'full_chapter'
export type SessionStep = 'source_selection' | 'theory_generation' | 'lesson_generation' | 'method_generation' | 'quiz_generation' | 'review' | 'finalize'

export interface AIEditorSession {
  session_id: string
  course_id?: string
  chapter_id?: string
  title: string
  status: SessionStatus
  source_type: SourceType
  source_data?: any
  current_step: SessionStep
  content_variants: AIEditorVariant[]
  snapshots: AIEditorSnapshot[]
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface AIEditorSessionListItem {
  session_id: string
  title: string
  status: SessionStatus
  source_type: SourceType
  current_step: SessionStep
  created_at: string
  updated_at: string
}

export interface AIEditorVariant {
  variant_id: string
  variant_type: VariantType
  title: string
  content: any
  tokens_used: number
  created_at: string
}

export interface AIEditorSnapshot {
  snapshot_id: string
  session_id: string
  content: any
  timestamp: string
  created_at: string
}

export interface AIEditorTemplate {
  template_id: string
  name: string
  description: string
  category: string
  content_structure: any
  preview?: any
}

export interface PDFUploadResponse {
  upload_id: string
  file_name: string
  pages: number
  extracted_text: string
  created_at: string
}

export interface AIEditorStats {
  total_sessions: number
  completed_sessions: number
  average_tokens_per_session: number
  total_tokens_used: number
  most_used_variant: VariantType
}

export interface CreateSessionRequest {
  title: string
  source_type: SourceType
  source_data?: any
  course_id?: string
  chapter_id?: string
}

export interface UpdateSessionRequest {
  title?: string
  current_step?: SessionStep
}

export interface SetSourceDataRequest {
  source_data: any
}

export interface GenerateContentRequest {
  variant_types: VariantType[]
  tone?: string
  length?: 'short' | 'medium' | 'long'
  language?: string
}

export interface GenerateContentResponse {
  variants: AIEditorVariant[]
  tokens_used: number
}

// ============================================================================
// Authoring API Types
// ============================================================================

export type ActionCategory = 'course_builder' | 'chat' | 'chapter' | 'lesson' | 'method' | 'content'
export type ActionType = 'chat' | 'generate' | 'edit' | 'delete' | 'preview'
export type OutputFormat = 'text' | 'json' | 'markdown' | 'html'
export type EntityType = 'course' | 'chapter' | 'lesson' | 'method'

export interface AuthoringAction {
  action_id: string
  category: ActionCategory
  type: ActionType
  name: string
  description?: string
  output_format: OutputFormat
  parameters?: Record<string, any>
  created_at: string
  updated_at?: string
}

export interface ActionCategoryInfo {
  id: ActionCategory
  name: string
  description: string
  icon?: string
}

export interface ActionContext {
  entity_id: string
  entity_type: EntityType
  parent_id?: string
  position?: number
  scope?: 'course' | 'chapter' | 'lesson'
}

export interface ActionVariables {
  subject?: string
  level?: 'beginner' | 'intermediate' | 'advanced'
  tone?: 'formal' | 'casual' | 'academic'
  length?: 'short' | 'medium' | 'long'
  language?: string
}

export interface ExecuteActionRequest {
  action_id: string
  context: ActionContext
  variables: ActionVariables
  input_data?: any
}

export interface ExecuteActionResponse {
  success: boolean
  action_execution_id: string
  result: any
  tokens_used: number
  duration_ms: number
  error?: string
}

export interface CreateActionRequest {
  category: ActionCategory
  type: ActionType
  name: string
  description?: string
  output_format: OutputFormat
  parameters?: Record<string, any>
}

export interface UpdateActionRequest {
  name?: string
  description?: string
  parameters?: Record<string, any>
}

export interface ActionUsageStats {
  action_id: string
  total_executions: number
  success_count: number
  failure_count: number
  average_tokens_used: number
  last_used: string
}

export interface PopularAction {
  action_id: string
  name: string
  execution_count: number
  category: ActionCategory
}

export type LMGroup = 'A' | 'B' | 'C' | 'D' | 'E' | 'F'
export type LMMethodType = 'explanatory' | 'practice' | 'exam' | 'pro' | 'it' | 'collaborative'
export type KIUsage = 'intensive' | 'medium' | 'optional'

export interface LMSuggestion {
  method_id: number
  method_name: string
  group: LMGroup
  ki_usage: KIUsage
  description: string
  score: number
}

export interface LMSuggestionsRequest {
  context: string
  difficulty_level: 'beginner' | 'intermediate' | 'advanced'
  content_type: 'theory' | 'practice' | 'assessment'
}

export interface LMSuggestionsResponse {
  suggestions: LMSuggestion[]
  context_analysis: string
}

export interface LMMethod {
  method_id: number
  name: string
  group: LMGroup
  description: string
}

export interface LMGroupInfo {
  group_id: LMGroup
  name: string
  description: string
  methods: LMMethod[]
}

export type LMGroupsResponse = Record<string, LMGroupInfo>
