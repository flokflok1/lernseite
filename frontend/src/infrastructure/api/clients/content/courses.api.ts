import http from '../http'

// ============================================================================
// Types & Interfaces
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
  total_chapters?: number  // Refactored: total_modules → total_chapters (2025-11-27)
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
  total_chapters?: number  // Refactored: total_modules → total_chapters (2025-11-27)
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
// Course API Functions
// ============================================================================

/**
 * Get courses current user is enrolled in
 */
export const getMyEnrolledCourses = async (
  params: PaginationParams & { status?: 'active' | 'completed' | 'cancelled' } = {}
): Promise<PaginatedResponse<EnrolledCourse>> => {
  const response = await http.get<{
    success: boolean
    enrollments: EnrolledCourse[]
    pagination: PaginatedResponse<EnrolledCourse>['pagination']
  }>('/courses/enrolled', {
    params: {
      page: params.page || 1,
      per_page: params.per_page || 20,
      status: params.status
    }
  })

  return {
    items: response.data.enrollments,
    pagination: response.data.pagination
  }
}

/**
 * Get courses created by current user
 */
export const getMyCourses = async (includeArchived = false): Promise<CourseListItem[]> => {
  const response = await http.get<{
    success: boolean
    courses: CourseListItem[]
  }>('/courses/my-courses', {
    params: { include_archived: includeArchived }
  })

  return response.data.courses
}

/**
 * Search public courses
 */
export const searchCourses = async (
  params: PaginationParams & {
    search?: string
    category?: string
    level?: string
    language?: string
    min_price?: number
    max_price?: number
    tags?: string[]
    course_type?: 'academy' | 'creator'
    include_drafts?: boolean
  } = {}
): Promise<PaginatedResponse<CourseListItem>> => {
  const response = await http.get<{
    success: boolean
    courses: CourseListItem[]
    pagination: PaginatedResponse<CourseListItem>['pagination']
  }>('/courses', {
    params: {
      search: params.search,
      category: params.category,
      level: params.level,
      language: params.language,
      min_price: params.min_price,
      max_price: params.max_price,
      tags: params.tags?.join(','),
      course_type: params.course_type,
      include_drafts: params.include_drafts ? 'true' : undefined,
      page: params.page || 1,
      per_page: params.per_page || 20
    }
  })

  return {
    items: response.data.courses,
    pagination: response.data.pagination
  }
}

/**
 * Get course details
 */
export const getCourse = async (courseId: number): Promise<CourseListItem> => {
  const response = await http.get<{
    success: boolean
    course: CourseListItem
  }>(`/courses/${courseId}`)

  return response.data.course
}

/**
 * Enroll in a course
 */
export const enrollInCourse = async (courseId: number): Promise<EnrolledCourse> => {
  const response = await http.post<{
    success: boolean
    enrollment: EnrolledCourse
  }>(`/courses/${courseId}/enroll`)

  return response.data.enrollment
}

// ============================================================================
// Course Editor API Functions (Creator/Teacher/Admin)
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
  chapter_id: string  // UUID (Refactored: module_id → chapter_id 2025-11-27)
  course_id: number
  title: string
  description?: string
  order_index: number
  estimated_time?: number
  created_at: string
  updated_at?: string
}

export interface LessonPayload {
  chapter_id: string  // Refactored: module_id → chapter_id (2025-11-27)
  title: string
  description?: string
  lesson_type: 'text' | 'video' | 'quiz' | 'ai' | 'mixed'
  order_index?: number
  duration_minutes?: number
  content?: any
}

export type UpdateLessonPayload = Partial<LessonPayload>

export interface EditableLesson {
  lesson_id: number
  chapter_id: string  // Refactored: module_id → chapter_id (2025-11-27)
  course_id: number
  title: string
  description?: string
  lesson_type: 'text' | 'video' | 'quiz' | 'ai' | 'mixed'
  order_index: number
  duration_minutes?: number
  content?: any
  is_published: boolean
  created_at: string
  updated_at?: string
}

export interface ReorderPayload {
  items: Array<{ id: number; order_index: number }>
}

/**
 * Create a new course (Creator/Teacher/Admin)
 */
export const createCourse = async (payload: CreateCoursePayload): Promise<EditableCourse> => {
  const response = await http.post<{
    success: boolean
    course: EditableCourse
  }>('/courses', payload)

  return response.data.course
}

/**
 * Update course metadata (Creator/Teacher/Admin)
 */
export const updateCourse = async (
  courseId: number,
  payload: UpdateCoursePayload
): Promise<EditableCourse> => {
  const response = await http.patch<{
    success: boolean
    course: EditableCourse
  }>(`/courses/${courseId}`, payload)

  return response.data.course
}

/**
 * Delete course (Creator/Teacher/Admin)
 */
export const deleteCourse = async (courseId: number): Promise<void> => {
  await http.delete(`/courses/${courseId}`)
}

/**
 * Get editable course data (includes modules & lessons)
 */
export const getCourseForEdit = async (courseId: number): Promise<EditableCourse> => {
  const response = await http.get<{
    success: boolean
    course: EditableCourse
  }>(`/courses/${courseId}/edit`)

  return response.data.course
}

/**
 * Create a new chapter in a course
 * Refactored: modules → chapters (2025-11-27)
 */
export const createChapter = async (payload: ChapterPayload): Promise<EditableChapter> => {
  const response = await http.post<{
    success: boolean
    chapter: EditableChapter
  }>('/chapters', payload)

  return response.data.chapter
}

/**
 * Update chapter
 * Refactored: modules → chapters (2025-11-27)
 */
export const updateChapter = async (
  chapterId: string,
  payload: UpdateChapterPayload
): Promise<EditableChapter> => {
  const response = await http.patch<{
    success: boolean
    chapter: EditableChapter
  }>(`/chapters/${chapterId}`, payload)

  return response.data.chapter
}

/**
 * Delete chapter
 * Refactored: modules → chapters (2025-11-27)
 */
export const deleteChapter = async (chapterId: string): Promise<void> => {
  await http.delete(`/chapters/${chapterId}`)
}

/**
 * Reorder chapters within a course
 * Refactored: modules → chapters (2025-11-27)
 */
export const reorderChapters = async (
  courseId: number,
  payload: ReorderPayload
): Promise<void> => {
  await http.post(`/courses/${courseId}/chapters/reorder`, payload)
}

/**
 * Get chapters for editing (includes lessons)
 * Refactored: modules → chapters (2025-11-27)
 */
export const getChaptersForEdit = async (courseId: number): Promise<EditableChapter[]> => {
  const response = await http.get<{
    success: boolean
    chapters: EditableChapter[]
  }>(`/courses/${courseId}/chapters/edit`)

  return response.data.chapters
}

/**
 * Create a new lesson in a chapter
 * Refactored: modules → chapters (2025-11-27)
 */
export const createLesson = async (payload: LessonPayload): Promise<EditableLesson> => {
  const response = await http.post<{
    success: boolean
    lesson: EditableLesson
  }>('/lessons', payload)

  return response.data.lesson
}

/**
 * Update lesson
 */
export const updateLesson = async (
  lessonId: number,
  payload: UpdateLessonPayload
): Promise<EditableLesson> => {
  const response = await http.patch<{
    success: boolean
    lesson: EditableLesson
  }>(`/lessons/${lessonId}`, payload)

  return response.data.lesson
}

/**
 * Delete lesson
 */
export const deleteLesson = async (lessonId: number): Promise<void> => {
  await http.delete(`/lessons/${lessonId}`)
}

/**
 * Reorder lessons within a chapter
 * Refactored: modules → chapters (2025-11-27)
 */
export const reorderLessons = async (
  chapterId: string,
  payload: ReorderPayload
): Promise<void> => {
  await http.post(`/chapters/${chapterId}/lessons/reorder`, payload)
}

/**
 * Get lessons for editing
 * Refactored: modules → chapters (2025-11-27)
 */
export const getLessonsForEdit = async (chapterId: string): Promise<EditableLesson[]> => {
  const response = await http.get<{
    success: boolean
    lessons: EditableLesson[]
  }>(`/chapters/${chapterId}/lessons/edit`)

  return response.data.lessons
}

/**
 * Publish course (set is_published = true)
 */
export const publishCourse = async (courseId: number): Promise<EditableCourse> => {
  const response = await http.post<{
    success: boolean
    course: EditableCourse
  }>(`/courses/${courseId}/publish`)

  return response.data.course
}

/**
 * Unpublish course (set is_published = false)
 */
export const unpublishCourse = async (courseId: number): Promise<EditableCourse> => {
  const response = await http.post<{
    success: boolean
    course: EditableCourse
  }>(`/courses/${courseId}/unpublish`)

  return response.data.course
}
