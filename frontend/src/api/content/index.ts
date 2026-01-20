/**
 * Content Domain - Barrel Export
 * 
 * This file provides a clean interface for importing all content APIs and types.
 * Use: import { getMyEnrolledCourses, CourseListItem } from '@/api/content'
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
  getCourseById,
  getPublicCourses,
  searchCourses,
  createCourse,
  updateCourse,
  deleteCourse,
  enrollCourse,
  unenrollCourse,
  getCourseProgress,
  updateCourseProgress
} from './courses.api'

// ============================================================================
// Categories API Export
// ============================================================================
export {
  getAllCategories,
  getCategoryTree,
  getCategoryById,
  getPaginatedCategories,
  searchCategories,
  createCategory,
  updateCategory,
  deleteCategory
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
