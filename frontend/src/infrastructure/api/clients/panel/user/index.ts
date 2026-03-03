/**
 * User Domain - Barrel Export
 *
 * Domain-organized API clients for user panel operations.
 *
 * Usage:
 * import { login, getProfile, getMyTokens } from '@/infrastructure/api/clients/panel/user'
 * import type { User, UserGroup, TokenBalanceResponse } from '@/infrastructure/api/clients/panel/user'
 */

// Types (types.ts + types_part2.ts)
export type {
  ChangePasswordRequest,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  User,
  UserGroup,
  UserProfileResponse,
  PanelSize,
  PanelSizesMap,
  PanelSizesResponse,
  PreferencesResponse,
  ProfileResponse,
  ProfileStatsResponse,
  UpdateProfileRequest,
  UpdateThemePreferenceRequest,
  ThemePreferenceResponse,
  UserPreferences,
} from './types'

export type {
  TokenBalanceResponse,
  TokenTransactionItem,
  TokenUsageResponse,
  SubscriptionPlan,
  SubscriptionResponse,
  TranscriptionResult,
  OralAnalysisResult,
  AudioFormatsResponse,
  TTSSpeakRequest,
  TTSSpeakResponse,
  VoiceInfo,
  VoicesResponse,
  TutorScriptStep,
  TutorScriptRequest,
  TutorScriptResultStep,
  TutorScriptResponse,
  PiperVoiceKey,
  OpenAIVoiceKey,
  TutorKnowledgeRequest,
  CourseContext,
  ChapterContext,
  TutorKnowledgeResponse,
  TutorChatRequest,
  TutorChatResponse,
  TutorTTSRequest,
  BaseStats,
  GamificationData,
  GamificationApiResponse,
  TopicScore,
  ExamContext,
  ExamSimulationConfig,
  ExamQuestion,
  ExamSimulation,
  ExamAttempt,
  SubmitAnswers,
  AttemptResult,
  UserExamProfile,
  MathCategory,
  MathPattern,
  PatternVariable,
  PatternStep,
  MathFormula,
  MathSession,
  CalculationStep,
  UserProgress,
  PatternTask,
  CalculatorEntry,
} from './types/types_part2'

// Auth
export {
  login,
  register,
  logout,
  refreshToken,
  getUserProfile,
} from './auth/auth.api'

// Profile
export {
  getProfile,
  updateProfile,
  changePassword,
  getProfileStats,
  deleteAccount,
  getThemePreference,
  updateThemePreference,
  getUserPreferences,
  getWindowSizes,
  updateWindowSize,
  deleteWindowSize,
  resetUserPreferences,
} from './profile/profile.api'

// Dashboard
export {
  getDashboardLayout,
  saveDashboardLayout,
} from './dashboard/dashboard.api'

// Gamification (tokens, subscriptions)
export {
  getMyTokens,
  getTokenTransactions,
  getTokenUsage,
  estimateAICost,
} from './gamification/tokens.api'

export {
  getPlans,
  getMySubscription,
  changeSubscription,
  cancelSubscription,
  reactivateSubscription,
} from './gamification/subscriptions.api'

export {
  getMyGamificationData,
  getMyStats,
  getMySkills,
  getMyAchievements,
} from './gamification/gamification.api'

// Audio (TTS, transcription)
export {
  ttsApi,
  DEFAULT_TUTOR_VOICE,
  PIPER_VOICES,
  OPENAI_VOICES,
  browserTTS,
} from './audio/tts.api'

export {
  transcribeAudio,
  transcribeAudioBase64,
  analyzeOralExplanation,
  getSupportedAudioFormats,
} from './audio/audio.api'

// Math
export {
  mathToolkitApi,
} from './math/mathToolkit.api'

// Feedback
export {
  submitFeedback,
  getMyFeedback,
  listFeedback,
  getFeedback,
  updateFeedbackStatus,
  updateFeedbackPriority,
  respondToFeedback,
  addFeedbackNote,
  getFeedbackDashboard,
  generateFeedbackSummary,
  getFeedbackSummaries,
} from './profile/feedback.api'

export type {
  FeedbackContext,
  SubmitFeedbackRequest,
  FeedbackItem,
  FeedbackListResponse,
  FeedbackDashboardStats,
  FeedbackDashboardResponse,
} from './profile/feedback.api'

// Exam Simulation
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
} from './exam/examSimulation.api'

// Exam Trainer (IHK archive practice)
export {
  trainerListExams,
  trainerGetQuestions,
  trainerGetTopics,
  trainerGetTopicQuestions,
  trainerSubmitAnswer,
  trainerStartExam,
  trainerCompleteAttempt,
} from './exams/trainer.api'

export type {
  TrainerExam,
  TrainerQuestion,
  TopicStat,
  AnswerResult as TrainerAnswerResult,
  AttemptResult as TrainerAttemptResult,
} from './exams/trainer.api'

// Courses (chapters)
export {
  getChapterDetail,
  getChapterProgress,
  getChapterTheories,
  getChapterTheory,
  getTheoryById,
} from './courses/chapters.api'
