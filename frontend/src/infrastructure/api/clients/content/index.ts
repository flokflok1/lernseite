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
  getActions,
  getActionsByCategory,
  getActionsForEntity,
  getAction,
  executeAction,
  createAction,
  updateAction,
  deleteAction,
  getActionStats,
  getLMSuggestions,
  getLMSuggestionsAI,
  getAllLearningMethods,
  groupActionsByCategory,
  filterActionsByLmType,
  getCategoryIcon,
  getActionTypeColor,
  getLMGroupName,
  getLMGroupIcon,
  getKIUsageColor,
  getKIUsageLabel,
  type AuthoringAction,
  type ActionContext,
  type ActionVariables,
  type ExecuteActionRequest,
  type ExecuteActionResponse,
  type CreateActionRequest,
  type UpdateActionRequest,
  type ActionUsageStats,
  type PopularAction,
  type LMSuggestion,
  type LMSuggestionsRequest,
  type LMSuggestionsResponse,
  type LMMethod,
  type LMGroupsResponse,
  type LMMethodType,
  type KIUsage,
  type EntityType,
  type ActionType,
  type OutputFormat
} from './authoring.api'
