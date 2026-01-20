/**
 * Learning Domain - Barrel Export
 * 
 * This file provides a clean interface for importing all learning APIs and types.
 * Use: import { getLesson, Course } from '@/api/learning'
 */

// ============================================================================
// Types Export
// ============================================================================
export type {
  // Player types
  Course,
  Chapter,
  Lesson,
  LessonProgress,
  ChapterProgress,
  CourseProgress,
  LearningMethod,
  ExecuteMethodRequest,
  ExecuteMethodResponse,
  AnalyticsEventRequest,
  QuizQuestionType,
  QuizQuestionOption,
  QuizQuestion,
  QuizData,
  QuizAnswerSubmission,
  QuizSubmitRequest,
  QuizQuestionResult,
  QuizResult,
  SavedTaskExecution,
  // AI Editor types
  SessionStatus,
  SourceType,
  VariantType,
  SessionStep,
  AIEditorSession,
  AIEditorSessionListItem,
  AIEditorVariant,
  AIEditorSnapshot,
  AIEditorTemplate,
  PDFUploadResponse,
  AIEditorStats,
  CreateSessionRequest,
  UpdateSessionRequest,
  SetSourceDataRequest,
  GenerateContentRequest,
  GenerateContentResponse,
  // Authoring types
  ActionCategory,
  ActionType,
  OutputFormat,
  EntityType,
  AuthoringAction,
  ActionCategoryInfo,
  ActionContext,
  ActionVariables,
  ExecuteActionRequest,
  ExecuteActionResponse,
  CreateActionRequest,
  UpdateActionRequest,
  ActionUsageStats,
  PopularAction,
  LMGroup,
  LMMethodType,
  KIUsage,
  LMSuggestion,
  LMSuggestionsRequest,
  LMSuggestionsResponse,
  LMMethod,
  LMGroupInfo,
  LMGroupsResponse
} from './types'

// ============================================================================
// Player API Export
// ============================================================================
export {
  getLesson,
  getLessonWithProgress,
  getChapter,
  getCourse,
  getCourseLessons,
  getCourseChapters,
  getLessonProgress,
  getChapterProgress,
  getCourseProgress,
  updateLessonProgress,
  getAvailableLearningMethods,
  executeMethod,
  getQuizData,
  submitQuiz,
  trackEvent
} from './player.api'

// ============================================================================
// AI Editor API Export
// ============================================================================
export {
  createSession,
  getSession,
  getSessionsList,
  updateSession,
  deleteSession,
  getTemplates,
  uploadPDF,
  setSourceData,
  generateVariants,
  getSessionStats,
  finalizeSession
} from './editor.api'

// ============================================================================
// Authoring API Export
// ============================================================================
export {
  getActions,
  getActionsByCategory,
  createAction,
  updateAction,
  deleteAction,
  executeAction,
  getActionStats,
  getPopularActions,
  getLMSuggestions,
  getLMGroups,
  getLMById
} from './authoring.api'
