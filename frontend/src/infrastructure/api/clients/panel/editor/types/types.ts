/**
 * Content Domain - Centralized Types
 * 
 * This file exports all types used in the Content domain (courses, categories, authoring)
 * to provide a single source of truth for type definitions.
 */

// ============================================================================
// Types from courses.api.ts
// ============================================================================

export interface CourseListItem {
  course_id: number
  title: string
  description: string
  category: string
  category_id?: number
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  language: string
  price: number
  is_public: boolean
  is_published: boolean
  thumbnail_url?: string
  creator_id: number
  creator_name?: string
  organisation_id?: number
  organisation_name?: string
  created_at: string
  updated_at?: string
  tags?: string[]
  total_chapters?: number
  total_lessons?: number
  total_duration_minutes?: number
  enrollment_count?: number
  average_rating?: number
}

export interface EnrolledCourse {
  enrollment_id: number
  course_id: number
  title: string
  description: string
  thumbnail_url?: string
  enrolled_at: string
  last_accessed_at?: string
  progress: number
  is_completed: boolean
  completed_at?: string | null
  status: 'active' | 'completed' | 'cancelled'
  price_paid: number
  total_chapters?: number
  total_lessons?: number
  lessons_completed?: number
}

export interface PaginationParams {
  page?: number
  per_page?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
}

// ============================================================================
// Types from categories.api.ts
// ============================================================================

export interface Category {
  category_id: number
  name: string
  slug: string
  description?: string
  parent_id?: number | null
  level: number
  path: string
  icon?: string
  color?: string
  order_index: number
  is_active: boolean
  course_count?: number
  total_course_count?: number
  children?: Category[]
  created_at?: string
  updated_at?: string
}

export interface CategoryTreeNode extends Category {
  children: CategoryTreeNode[]
}

export interface CategoryTreeResponse {
  categories: CategoryTreeNode[]
  total_categories: number
  max_level: number
  active_categories: number
}

export interface PaginatedCategoryResponse {
  categories: Category[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
}

// ============================================================================
// Types from authoring.api.ts (course authoring)
// ============================================================================

export interface CourseAuthoringSession {
  session_id: string
  course_id: string
  course_title?: string
  status: 'active' | 'finalized' | 'archived'
  model_profile: string
  draft_structure: DraftStructure
  chat_history: ChatMessage[]
  total_tokens_used: number
  total_operations: number
  created_at?: string
  updated_at?: string
  finalized_at?: string
}

export interface DraftStructure {
  chapters?: DraftChapter[]
}

export interface DraftChapter {
  id: string
  title: string
  description?: string
  order_index?: number
  lessons?: DraftLesson[]
}

export interface DraftLesson {
  id: string
  title: string
  description?: string
  order_index?: number
  methods?: DraftMethod[]
}

export interface DraftMethod {
  id: string
  type: string
  title?: string
  data?: Record<string, unknown>
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
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
