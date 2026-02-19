/**
 * Public Domain - Barrel Export
 *
 * Clean interface for importing all public (unauthenticated) APIs and types.
 * Use: import { getSetupStatus, getBundle } from '@/infrastructure/api/clients/public'
 */

// Setup
export {
  getSetupStatus,
  getEnvironmentInfo,
  configureEnvironment,
  runSystemCheck,
  initDatabase,
  createAdmin,
  createOrganisation,
  configureAI,
  seedData,
  getSeedStatus,
  verifyInstallation,
  completeInstallation,
  getSystemInfo
} from './setup/setup.api'

// i18n
export {
  getBundle,
  getLanguages,
  getLanguageProgress,
  submitSuggestion,
  getSuggestions,
  voteSuggestion,
  requestTranslation,
  getModerationDashboard,
  getModerationQueue,
  reviewQueueItem,
  triggerAiReview,
  getAiConfig,
  updateAiConfig,
  invalidateCache,
  getNamespaces,
  getKeys,
  getKeyTranslations,
  createKey,
  setTranslation,
  aiTranslate,
  aiTranslateBulk,
  seedKeys,
  createLanguage,
  updateLanguage,
  deleteLanguage
} from './i18n/i18n.api'

// Learning (Player, Tutor)
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
  sendAnalyticsEvent
} from './learning/player/player.api'

export {
  tutorChat,
  tutorTTS,
  getTTSVoices,
  type TutorChatRequest,
  type TutorChatResponse,
  type TutorTTSRequest
} from './learning/tutor/tutor.api'

// Learning Types
export type * from './learning/types/types'

// Types
export type * from './types'
