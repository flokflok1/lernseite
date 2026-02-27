/**
 * Panel Editor Domain - Barrel Export
 *
 * Domain-organized API clients for editor panel operations.
 * Use: import { getMyEnrolledCourses, courseAuthoringApi } from '@/infrastructure/api/clients/panel/editor'
 */

// Types
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

// Courses
export {
  getMyEnrolledCourses,
  getMyCourses,
  listEditorCourses,
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
  updateCourseStatus,
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
} from './courses/courses.api'

// Activities
export {
  getLessonActivities,
  createLessonActivity,
  updateLessonActivity,
  deleteLessonActivity,
  reorderLessonActivities,
  type LessonActivity,
} from './courses/activities.api'

// Categories
export {
  getCategories,
  getCategoryTree,
  searchCategories,
} from './courses/categories.api'

// Authoring Actions
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
  getLMGroups,
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
  type OutputFormat,
  type LMGroupAPIInfo,
  type LMGroupsAPIResponse
} from './authoring/authoring.api'

// Course Authoring (KI-Kurs-Builder)
export * as courseAuthoringApi from './authoring/courseAuthoring.api'

// AI Editor (unified) — session/chat API accessed via courseAuthoringApi above
// Legacy editor.api.ts removed: used non-existent /admin/ai-editor/ routes
