/**
 * courses.types.ts
 *
 * Type definitions for course, chapter, lesson entities.
 * Split from courses.api.ts (G01: 500 LOC limit).
 */

// ============================================================================
// Public/Shared Course Types
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
  chapter_count?: number
  trashed_at?: string | null
  status?: string
  published?: boolean
  course_type?: string
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
// Editor Course Types (Creator/Teacher/Admin)
// ============================================================================

export interface CreateCoursePayload {
  title: string
  subtitle?: string
  description?: string
  category_id?: number
  subcategory_id?: number
  level?: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  language?: string
  target_group?: string
  tags?: string[]
  learning_goals?: string[]
  requirements?: string[]
  visibility?: 'private' | 'group_private' | 'class_internal' | 'company_internal' | 'community_public' | 'marketplace' | 'academy'
  price?: number
  thumbnail_url?: string
}

export interface UpdateCoursePayload extends Partial<CreateCoursePayload> {
  is_published?: boolean
  draft_state?: boolean
}

export interface EditableCourse {
  course_id: number
  title: string
  subtitle?: string
  description?: string
  category_id?: number
  subcategory_id?: number
  category?: string
  subcategory?: string
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  language: string
  target_group?: string
  created_by: number
  creator_role?: string
  visibility: string
  tags?: string[]
  thumbnail_url?: string
  duration_estimate?: number
  estimated_duration?: number
  learning_goals?: string[]
  requirements?: string[]
  is_published: boolean
  draft_state: boolean
  created_at: string
  updated_at?: string
  last_edit_by?: number
  version?: number
}

export interface ChapterPayload {
  course_id: number
  title: string
  description?: string
  order_index?: number
  estimated_time?: number
}

export type UpdateChapterPayload = Partial<ChapterPayload>

export interface EditableChapter {
  chapter_id: string
  course_id: number
  title: string
  description?: string
  order_index: number
  estimated_time?: number
  created_at: string
  updated_at?: string
}

export interface LessonPayload {
  chapter_id: string
  title: string
  description?: string
  lesson_type: 'text' | 'video' | 'quiz' | 'ai' | 'mixed'
  order_index?: number
  duration_minutes?: number
  content?: string
  notes?: string
}

export type UpdateLessonPayload = Partial<LessonPayload>

export interface EditableLesson {
  lesson_id: number
  chapter_id: string
  course_id: number
  title: string
  description?: string
  lesson_type: 'text' | 'video' | 'quiz' | 'ai' | 'mixed'
  order_index: number
  duration_minutes?: number
  content?: string
  notes?: string
  is_published: boolean
  created_at: string
  updated_at?: string
}

export interface ReorderPayload {
  items: Array<{ id: number; order_index: number }>
}
