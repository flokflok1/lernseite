/**
 * courses.api.ts
 *
 * API functions for course CRUD (public + editor).
 * Types: ./courses.types.ts (split for G01 compliance)
 */
import http from '@/infrastructure/api/http'
import type {
  CourseListItem,
  EnrolledCourse,
  PaginationParams,
  PaginatedResponse,
  CreateCoursePayload,
  UpdateCoursePayload,
  EditableCourse,
  ChapterPayload,
  UpdateChapterPayload,
  EditableChapter,
  LessonPayload,
  UpdateLessonPayload,
  EditableLesson,
  ReorderPayload,
} from './courses.types'

// Re-export all types for backwards compatibility
export type {
  CourseListItem,
  EnrolledCourse,
  PaginationParams,
  PaginatedResponse,
  CreateCoursePayload,
  UpdateCoursePayload,
  EditableCourse,
  ChapterPayload,
  UpdateChapterPayload,
  EditableChapter,
  LessonPayload,
  UpdateLessonPayload,
  EditableLesson,
  ReorderPayload,
} from './courses.types'

import { EDITOR_PREFIX } from './constants'

// ============================================================================
// Public Course API Functions
// ============================================================================

/** Fetch the current user's enrolled courses (paginated, filterable by status) */
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

/** Fetch courses created by the current user */
export const getMyCourses = async (includeArchived = false): Promise<CourseListItem[]> => {
  const response = await http.get<{
    success: boolean
    courses: CourseListItem[]
  }>('/courses/my-courses', {
    params: { include_archived: includeArchived }
  })

  return response.data.courses
}

/** Search public course catalog with filters (category, level, language, price, tags) */
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

/** Fetch a single course by ID (public view) */
export const getCourse = async (courseId: number): Promise<CourseListItem> => {
  const response = await http.get<{
    success: boolean
    course: CourseListItem
  }>(`/courses/${courseId}`)

  return response.data.course
}

/** Enroll the current user in a course */
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

/** List courses for the editor panel (optionally filter by status) */
export const listEditorCourses = async (status?: string): Promise<CourseListItem[]> => {
  const response = await http.get<{
    success: boolean
    courses: CourseListItem[]
  }>(`${EDITOR_PREFIX}/courses`, {
    params: status ? { status } : undefined
  })

  return response.data.courses || []
}

/** Create a new course */
export const createCourse = async (payload: CreateCoursePayload): Promise<EditableCourse> => {
  const response = await http.post<{
    success: boolean
    course: EditableCourse
  }>(`${EDITOR_PREFIX}/courses`, payload)

  return response.data.course
}

/** Partially update course metadata */
export const updateCourse = async (
  courseId: number,
  payload: UpdateCoursePayload
): Promise<EditableCourse> => {
  const response = await http.patch<{
    success: boolean
    course: EditableCourse
  }>(`${EDITOR_PREFIX}/courses/${courseId}`, payload)

  return response.data.course
}

/** Soft-delete a course (moves to trash) */
export const deleteCourse = async (courseId: number): Promise<void> => {
  await http.delete(`${EDITOR_PREFIX}/courses/${courseId}`)
}

/** Change course lifecycle status (publish, unpublish, archive, unarchive, restore, purge) */
export const updateCourseStatus = async (
  courseId: number,
  action: 'publish' | 'unpublish' | 'archive' | 'unarchive' | 'restore' | 'purge',
  reason?: string
): Promise<{ success: boolean; status: string }> => {
  const response = await http.post<{ success: boolean; status: string }>(
    `${EDITOR_PREFIX}/courses/${courseId}/status`,
    { action, reason }
  )
  return response.data
}

/** Fetch full course data for the editor (includes all editable fields) */
export const getCourseForEdit = async (courseId: number): Promise<EditableCourse> => {
  const response = await http.get<{
    success: boolean
    course: EditableCourse
  }>(`${EDITOR_PREFIX}/courses/${courseId}`)

  return response.data.course
}

/** Create a new chapter in a course */
export const createChapter = async (payload: ChapterPayload): Promise<EditableChapter> => {
  const response = await http.post<{
    success: boolean
    chapter: EditableChapter
  }>(`${EDITOR_PREFIX}/courses/${payload.course_id}/chapters`, payload)

  return response.data.chapter
}

/** Update chapter metadata (title, position) */
export const updateChapter = async (
  chapterId: string,
  payload: UpdateChapterPayload
): Promise<EditableChapter> => {
  const response = await http.patch<{
    success: boolean
    chapter: EditableChapter
  }>(`${EDITOR_PREFIX}/chapters/${chapterId}`, payload)

  return response.data.chapter
}

/** Delete a chapter and all its lessons */
export const deleteChapter = async (chapterId: string): Promise<void> => {
  await http.delete(`${EDITOR_PREFIX}/chapters/${chapterId}`)
}

/** Reorder chapters within a course */
export const reorderChapters = async (
  courseId: number,
  payload: ReorderPayload
): Promise<void> => {
  await http.post(`${EDITOR_PREFIX}/courses/${courseId}/chapters/reorder`, payload)
}

/** Fetch all chapters for a course (editor view) */
export const getChaptersForEdit = async (courseId: number | string): Promise<EditableChapter[]> => {
  const response = await http.get<{
    success: boolean
    chapters: EditableChapter[]
  }>(`${EDITOR_PREFIX}/courses/${courseId}/chapters`)

  return response.data.chapters
}

/** Create a new lesson in a chapter */
export const createLesson = async (payload: LessonPayload): Promise<EditableLesson> => {
  const response = await http.post<{
    success: boolean
    lesson: EditableLesson
  }>(`${EDITOR_PREFIX}/chapters/${payload.chapter_id}/lessons`, payload)

  return response.data.lesson
}

/** Update lesson fields (title, content, type, settings) */
export const updateLesson = async (
  lessonId: number,
  payload: UpdateLessonPayload
): Promise<EditableLesson> => {
  const response = await http.patch<{
    success: boolean
    lesson: EditableLesson
  }>(`${EDITOR_PREFIX}/lessons/${lessonId}`, payload)

  return response.data.lesson
}

/** Delete a lesson */
export const deleteLesson = async (lessonId: number): Promise<void> => {
  await http.delete(`${EDITOR_PREFIX}/lessons/${lessonId}`)
}

/** Reorder lessons within a chapter */
export const reorderLessons = async (
  chapterId: string,
  payload: ReorderPayload
): Promise<void> => {
  await http.post(`${EDITOR_PREFIX}/chapters/${chapterId}/lessons/reorder`, payload)
}

/** Fetch all lessons for a chapter (editor view) */
export const getLessonsForEdit = async (chapterId: string): Promise<EditableLesson[]> => {
  const response = await http.get<{
    success: boolean
    lessons: EditableLesson[]
  }>(`${EDITOR_PREFIX}/chapters/${chapterId}/lessons`)

  return response.data.lessons
}

