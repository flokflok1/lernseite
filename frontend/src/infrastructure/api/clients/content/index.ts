/**
 * Content Domain - Barrel Export
 * 
 * This file provides a clean interface for importing all content APIs and types.
 * Use: import { getMyEnrolledCourses, CourseListItem } from '@/infrastructure/api/content'
 */

// ============================================================================
// Types Export
// ============================================================================
export type {
  CourseListItem,
  EnrolledCourse,
  PaginationParams,
  PaginatedResponse,
  Category,
  CategoryTreeNode,
  CategoryTreeResponse,
  PaginatedCategoryResponse,
  CourseAuthoringSession,
  DraftStructure,
  DraftChapter,
  DraftLesson,
  DraftMethod,
  ChatMessage
} from './types'

// ============================================================================
// Courses API Export
// ============================================================================
export {
  getMyEnrolledCourses,
  getMyCourses,
  searchCourses,
  getCourse,
  enrollInCourse,
  createCourse,
  updateCourse,
  deleteCourse,
  getCourseForEdit,
  createChapter,
  updateChapter,
  deleteChapter,
  reorderChapters,
  getChaptersForEdit,
  createLesson,
  updateLesson,
  deleteLesson,
  reorderLessons,
  getLessonsForEdit,
  publishCourse,
  unpublishCourse,
  type CourseListItem,
  type EnrolledCourse,
  type PaginationParams,
  type PaginatedResponse,
  type CreateCoursePayload,
  type UpdateCoursePayload,
  type EditableCourse,
  type ChapterPayload,
  type UpdateChapterPayload,
  type EditableChapter,
  type LessonPayload,
  type UpdateLessonPayload,
  type EditableLesson,
  type ReorderPayload
} from './courses.api'

// ============================================================================
// Categories API Export
// ============================================================================
export {
  getCategories,
  getCategoryTree,
  searchCategories,
  type Category,
  type CategoryTreeNode,
  type CategoryTreeResponse,
  type PaginatedCategoryResponse
} from './categories.api'

// ============================================================================
// Course Authoring API Export
// ============================================================================
export {
  startAuthoringSession,
  getAuthoringSession,
  updateAuthoringSession,
  finalizeAuthoringSession,
  deleteAuthoringSession,
  addChatMessage,
  generateChapter,
  generateLesson,
  generateMethod
} from './authoring.api'
