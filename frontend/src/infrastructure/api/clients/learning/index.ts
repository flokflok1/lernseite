/**
 * Learning Domain - Barrel Export
 * 
 * This file provides a clean interface for importing all learning APIs and types.
 * Use: import { getLesson, Course } from '@/infrastructure/api/learning'
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
  LMGroupsResponse,
  LMGroupAPIInfo,
  LMGroupsAPIResponse
} from './types'

// ============================================================================
// Player API Export
// ============================================================================
export {
  getCourse,
  getCourseChapters,
  getChapter,
  getLesson,
  getCourseProgress,
  getChapterProgress,
  getLessonProgress,
  markLessonStarted,
  markLessonCompleted,
  updateLessonProgress,
  getLessonMethods,
  executeMethod,
  getLessonQuiz,
  getQuizAttempts,
  submitQuizAnswers,
  startExam,
  sendAnalyticsEvent,
  type Course,
  type Chapter,
  type Lesson,
  type LessonProgress,
  type ChapterProgress,
  type CourseProgress,
  type LearningMethod,
  type ExecuteMethodRequest,
  type ExecuteMethodResponse,
  type AnalyticsEventRequest,
  type QuizQuestionType,
  type QuizQuestionOption,
  type QuizQuestion,
  type QuizData,
  type QuizAnswerSubmission,
  type QuizSubmitRequest,
  type QuizQuestionResult,
  type QuizResult
} from './player.api'

// ============================================================================
// AI Editor API Export
// ============================================================================
export {
  createSession,
  getSession,
  listSessions as getSessionsList, // Alias: listSessions -> getSessionsList
  updateSession,
  deleteSession,
  getTemplates,
  uploadPDF,
  setSourceData,
  generateContent as generateVariants, // Alias: generateContent -> generateVariants
  getStats as getSessionStats, // Alias: getStats -> getSessionStats
  finalizeSession
} from './editor.api'

// ============================================================================
// Tutor API Export
// ============================================================================
export {
  tutorChat,
  tutorTTS,
  getTTSVoices,
  type TutorChatRequest,
  type TutorChatResponse,
  type TutorTTSRequest
} from './tutor.api'

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
  getLMSuggestions,
  getAllLearningMethods,
  getLMGroups
} from './authoring.api'

// ============================================================================
// Exam Simulation API Export
// ============================================================================
export {
  getExamContext,
  createExamSimulation,
  listExamSimulations,
  getExamSimulation,
  deleteExamSimulation,
  generateExamSimulation,
  startExamAttempt,
  listExamAttempts,
  submitExamAttempt,
  getUserExamProfile,
  updateUserExamProfile,
  type TopicScore,
  type ExamContext,
  type ExamSimulationConfig,
  type ExamQuestion,
  type ExamSimulation,
  type ExamAttempt,
  type SubmitAnswers,
  type AttemptResult,
  type UserExamProfile
} from './examSimulation.api'
export { getActionsForEntity } from './authoring.api'
