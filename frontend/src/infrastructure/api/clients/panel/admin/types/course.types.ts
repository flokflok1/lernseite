/**
 * Admin API - Course, Chapter, Lesson, Category, Prompt & File Types
 *
 * Types for the content domain: course CRUD, chapter/lesson management,
 * category trees, course prompts, and file uploads.
 */

// ============================================================================
// Course Management
// ============================================================================

export interface AdminCourseCreateRequest {
  title: string
  description?: string
  creator_id: string
  organisation_id?: string | null
  category_id?: number | null
  level?: string
  language?: string
  price?: number
  is_public?: boolean
  thumbnail_url?: string
  preview_video_url?: string
  tags?: string[]
}

export interface AdminCourseUpdateRequest {
  title?: string
  description?: string
  category_id?: number | null
  category?: string
  level?: string
  language?: string
  price?: number
  is_public?: boolean
  thumbnail_url?: string
  preview_video_url?: string
  tags?: string[]
}

// ============================================================================
// Chapters
// ============================================================================

export interface AdminChapter {
  chapter_id: string
  course_id: string
  title: string
  description?: string | null
  order_index: number
  duration_minutes: number
  has_video: boolean
  has_quiz: boolean
  has_exam: boolean
  lesson_count?: number
  total_lesson_duration?: number
  created_at: string
  updated_at?: string | null
}

export interface AdminChapterCreateRequest {
  title: string
  description?: string
  order_index?: number
  duration_minutes?: number
  has_video?: boolean
  has_quiz?: boolean
  has_exam?: boolean
}

export interface AdminChapterUpdateRequest {
  title?: string
  description?: string
  order_index?: number
  duration_minutes?: number
  has_video?: boolean
  has_quiz?: boolean
  has_exam?: boolean
}

// ============================================================================
// Categories
// ============================================================================

export interface Category {
  category_id: number
  name: string
  slug: string
  description?: string | null
  parent_id?: number | null
  level: number
  is_active: boolean
  created_at: string
  updated_at?: string | null
  path?: string | null
  root_id?: number | null
  path_ids?: number[] | null
  course_count?: number
  total_course_count?: number
  name_en?: string | null
  name_es?: string | null
  name_fr?: string | null
  children?: Category[]
  has_children?: boolean
  icon?: string | null
  color?: string | null
  order_index?: number
}

export interface CategoryTreeNode {
  category_id: number
  name: string
  slug: string
  description?: string | null
  level: number
  is_active: boolean
  children: CategoryTreeNode[]
  path?: string | null
  root_id?: number | null
  path_ids?: number[] | null
  course_count?: number
  total_course_count?: number
  has_children?: boolean
  icon?: string | null
  color?: string | null
  order_index?: number
  parent_id?: number | null
}

export interface CategoryTree {
  tree: CategoryTreeNode[]
  total_categories?: number
  max_level?: number
  active_categories?: number
}

export interface CategoryFilterParams {
  active_only?: boolean
  level?: number
  parent_id?: number
}

// ============================================================================
// Lessons
// ============================================================================

export type LessonType = 'text' | 'video' | 'quiz' | 'interactive' | 'assignment' | 'discussion'

export interface AdminLesson {
  lesson_id: string
  chapter_id: string
  title: string
  lesson_type: LessonType
  content?: Record<string, unknown> | null
  duration_minutes: number
  order_index: number
  published: boolean
  free_preview: boolean
  created_at: string
  updated_at?: string | null
}

export interface AdminLessonCreateRequest {
  title: string
  lesson_type?: LessonType
  content?: Record<string, unknown>
  duration_minutes?: number
  published?: boolean
  free_preview?: boolean
}

export interface AdminLessonUpdateRequest {
  title?: string
  lesson_type?: LessonType
  content?: Record<string, unknown>
  duration_minutes?: number
  order_index?: number
  published?: boolean
  free_preview?: boolean
}

// ============================================================================
// Course Prompts
// ============================================================================

export type PromptScope =
  | 'course_generation'
  | 'module_generation'
  | 'exam_generation'
  | 'lesson_generation'
  | 'quiz_generation'

export interface CoursePrompt {
  course_prompt_id: string
  course_id: string
  scope: PromptScope
  language: string | null
  prompt_system: string | null
  prompt_user_template: string | null
  metadata: Record<string, unknown>
  is_active: boolean
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface CoursePromptUpdateRequest {
  language?: string | null
  prompt_system?: string | null
  prompt_user_template?: string | null
  metadata?: Record<string, unknown>
  is_active?: boolean
}

export interface CoursePromptResolveResponse {
  source: 'course_specific' | 'global' | 'hardcoded_fallback'
  scope: PromptScope
  language: string | null
  prompt_system: string | null
  prompt_user_template: string | null
  metadata: Record<string, unknown>
}

// ============================================================================
// Course Files
// ============================================================================

export type CourseFileType = 'pdf' | 'docx' | 'pptx' | 'xlsx' | 'txt' | 'image' | 'video' | 'audio' | 'archive' | 'other'
export type CourseFileCategory = 'script' | 'material' | 'exercise' | 'solution' | 'reference' | 'template' | 'other'

export interface CourseFile {
  course_file_id: string
  course_id: string
  file_id: string | null
  file_name: string
  file_type: CourseFileType
  file_size_bytes: number | null
  mime_type: string | null
  display_name: string | null
  description: string | null
  file_category: CourseFileCategory
  order_index: number
  is_public: boolean
  requires_enrollment: boolean
  download_count: number
  processed_for_ai: boolean
  ai_extracted_text: string | null
  ai_summary: string | null
  storage_path: string | null
  external_url: string | null
  uploaded_by: string | null
  uploader_name?: string | null
  public_url?: string | null
  cdn_url?: string | null
  media_status?: string | null
  created_at: string
  updated_at: string | null
}

export interface CourseFileCategorySummary {
  file_category: CourseFileCategory
  count: number
  total_size: number | null
}

export interface CourseFilesListResponse {
  files: CourseFile[]
  total: number
  categories_summary: CourseFileCategorySummary[]
}

export interface CourseFileUploadData {
  display_name?: string
  description?: string
  file_category?: CourseFileCategory
  is_public?: boolean
}

export interface CourseFileUpdateRequest {
  display_name?: string
  description?: string
  file_category?: CourseFileCategory
  is_public?: boolean
}

export interface CourseFileUploadResponse {
  file: CourseFile
  already_exists?: boolean
  message?: string
}

// ============================================================================
// Exams
// ============================================================================

export type ExamType = 'practice' | 'ai_simulation' | 'final'
export type ExamStandard = 'IHK_FISI_AP1' | 'IHK_FIAE_AP1' | 'CompTIA_A+' | 'CompTIA_Network+' | 'Abitur_Informatik' | 'Custom'
export type QuestionType = 'mcq' | 'true_false' | 'fill_blanks' | 'matching' | 'short_answer' | 'math_problem' | 'case_question'

export interface ExamQuestion {
  question_id: string
  exam_id: string
  question_type: QuestionType
  question_text: string
  data: Record<string, unknown>
  solution: Record<string, unknown>
  points: number
  order_index: number
}

export interface Exam {
  exam_id: string
  course_id: string
  exam_type: ExamType
  title: string
  description?: string | null
  duration_minutes: number
  passing_score: number
  total_points: number
  settings?: Record<string, unknown>
  published: boolean
  generated_by_ai: boolean
  ai_model?: string | null
  question_count: number
  questions?: ExamQuestion[]
  created_at: string
  updated_at?: string | null
}

export interface ExamCreateRequest {
  title: string
  description?: string
  exam_type?: ExamType
  duration_minutes?: number
  passing_score?: number
  total_points?: number
  settings?: Record<string, unknown>
  published?: boolean
}

export interface ExamUpdateRequest {
  title?: string
  description?: string
  duration_minutes?: number
  passing_score?: number
  total_points?: number
  settings?: Record<string, unknown>
  published?: boolean
}

export interface ExamGenerateRequest {
  title: string
  description?: string
  exam_standard: ExamStandard
  difficulty?: string
  duration_minutes?: number
  passing_score?: number
  total_points?: number
  question_distribution: Record<string, number>
  topic_coverage?: Record<string, number>
  source_chapter_ids?: string[]
}
