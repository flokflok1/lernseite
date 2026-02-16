/**
 * User Domain - Barrel Export
 * ===========================
 *
 * This file provides a clean interface for importing all user-related APIs and types.
 * Part of the DDD Architecture - User Domain consolidating authentication, profile,
 * dashboard, tokens, subscriptions, gamification, TTS, audio, and math toolkit.
 *
 * GBA (Group-Based Authorization):
 * - NO role field - authorization via groups with hierarchy_level (0-1000)
 * - full_name (not first_name/last_name)
 * - groups[] and permissions[] from login response
 *
 * Usage:
 * import { login, getProfile, getMyTokens } from '@/infrastructure/api/clients/panel/user'
 * import type { User, UserGroup, TokenBalanceResponse } from '@/infrastructure/api/clients/panel/user'
 */

// ============================================================================
// Types Export (Single Source of Truth - types.ts + types_part2.ts)
// ============================================================================

export type {
  // Authentication Types (GBA)
  ChangePasswordRequest,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  User,
  UserGroup,
  UserProfileResponse,
  // Profile Types
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
  // Token types
  TokenBalanceResponse,
  TokenTransactionItem,
  TokenUsageResponse,
  // Subscription types
  SubscriptionPlan,
  SubscriptionResponse,
  // Audio types
  TranscriptionResult,
  OralAnalysisResult,
  AudioFormatsResponse,
  // TTS types
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
  // Tutor types
  TutorChatRequest,
  TutorChatResponse,
  TutorTTSRequest,
  // Gamification types
  BaseStats,
  GamificationData,
  GamificationApiResponse,
  // Exam Simulation types
  TopicScore,
  ExamContext,
  ExamSimulationConfig,
  ExamQuestion,
  ExamSimulation,
  ExamAttempt,
  SubmitAnswers,
  AttemptResult,
  UserExamProfile,
  // Math Toolkit types
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
} from './types_part2'

// ============================================================================
// Authentication API Export
// ============================================================================

export {
  login,
  register,
  logout,
  refreshToken,
  getUserProfile,
} from './auth.api'

// ============================================================================
// Profile API Export
// ============================================================================

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
} from './profile.api'

// ============================================================================
// Tokens API Export
// ============================================================================

export {
  getMyTokens,
  getTokenTransactions,
  getTokenUsage,
  estimateAICost,
} from './tokens.api'

// ============================================================================
// Subscriptions API Export
// ============================================================================

export {
  getPlans,
  getMySubscription,
  changeSubscription,
  cancelSubscription,
  reactivateSubscription,
} from './subscriptions.api'

// ============================================================================
// Gamification API Export
// ============================================================================

export {
  getMyGamificationData,
  getMyStats,
  getMySkills,
  getMyAchievements,
} from './gamification.api'

// ============================================================================
// TTS API Export
// ============================================================================

export {
  ttsApi,
  DEFAULT_TUTOR_VOICE,
  PIPER_VOICES,
  OPENAI_VOICES,
  browserTTS,
} from './tts.api'

// ============================================================================
// Audio API Export
// ============================================================================

export {
  transcribeAudio,
  transcribeAudioBase64,
  analyzeOralExplanation,
  getSupportedAudioFormats,
} from './audio.api'

// ============================================================================
// Math Toolkit API Export
// ============================================================================

export {
  mathToolkitApi,
} from './mathToolkit.api'

// ============================================================================
// Dashboard API Export
// ============================================================================

export {
  getDashboardLayout,
  saveDashboardLayout,
} from './dashboard.api'

// ============================================================================
// Feedback API Export
// ============================================================================

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
} from './feedback.api'

export type {
  FeedbackContext,
  SubmitFeedbackRequest,
  FeedbackItem,
  FeedbackListResponse,
  FeedbackDashboardStats,
  FeedbackDashboardResponse,
} from './feedback.api'
