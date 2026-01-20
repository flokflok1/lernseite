/**
 * System Domain - Barrel Export
 * 
 * This file provides a clean interface for importing all system APIs and types.
 * Use: import { getMyTokens, TokenBalanceResponse } from '@/api/system'
 */

// ============================================================================
// Types Export
// ============================================================================
export type {
  // Setup types
  SetupStatusResponse,
  InstallInfo,
  SystemCheckResult,
  SystemCheckResponse,
  DatabaseInitResponse,
  AdminCreateRequest,
  AdminCreateResponse,
  OrganisationCreateRequest,
  OrganisationCreateResponse,
  AIConfigRequest,
  AIConfigResponse,
  SeedDataRequest,
  SeedDataResponse,
  SeedStatusResponse,
  VerificationResponse,
  CompleteInstallationResponse,
  EnvironmentInfoResponse,
  EnvironmentConfigRequest,
  EnvironmentConfigResponse,
  // i18n types
  LanguageProgress,
  TranslationSuggestion,
  ModerationQueueItem,
  I18nNamespace,
  I18nKey,
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
  // Exam types
  TopicScore,
  ExamContext,
  ExamSimulationConfig,
  ExamQuestion,
  ExamSimulation,
  ExamAttempt,
  SubmitAnswers,
  AttemptResult,
  UserExamProfile,
  // Math toolkit types
  MathCategory,
  MathPattern,
  PatternVariable,
  PatternStep,
  MathFormula,
  MathSession,
  CalculationStep,
  UserProgress,
  PatternTask,
  CalculatorEntry
} from './types'

// ============================================================================
// Setup API Export
// ============================================================================
export {
  getSetupStatus,
  runSystemCheck,
  initializeDatabase,
  createAdmin,
  createOrganisation,
  configureAI,
  seedData,
  getSeedStatus,
  verifySetup,
  completeInstallation,
  getEnvironmentInfo,
  updateEnvironmentConfig
} from './setup.api'

// ============================================================================
// i18n API Export
// ============================================================================
export {
  getLanguageProgress,
  getTranslations,
  suggestTranslation,
  getModerationQueue,
  approveSuggestion,
  rejectSuggestion,
  getNamespaces,
  getNamespaceKeys,
  updateTranslation,
  syncTranslations
} from './i18n.api'

// ============================================================================
// Tokens API Export
// ============================================================================
export {
  getMyTokens,
  getTokenTransactions,
  getTokenUsage,
  estimateAICost,
  purchaseTokens
} from './tokens.api'

// ============================================================================
// Subscriptions API Export
// ============================================================================
export {
  getPlans,
  getCurrentSubscription,
  subscribeToPlan,
  cancelSubscription,
  updateSubscription
} from './subscriptions.api'

// ============================================================================
// Audio API Export
// ============================================================================
export {
  transcribeAudio,
  analyzeOralPerformance,
  getSupportedAudioFormats
} from './audio.api'

// ============================================================================
// TTS API Export
// ============================================================================
export {
  speak,
  getAvailableVoices,
  generateTutorScript,
  getTutorKnowledge
} from './tts.api'

// ============================================================================
// Tutor API Export
// ============================================================================
export {
  chatWithTutor,
  getTutorResponse,
  speakTutorResponse
} from './tutor.api'

// ============================================================================
// Gamification API Export
// ============================================================================
export {
  getGamificationData,
  awardXP,
  completeBadge,
  getLeaderboard
} from './gamification.api'

// ============================================================================
// Exam Simulation API Export
// ============================================================================
export {
  getExamSimulation,
  startExamAttempt,
  submitExamAnswers,
  getExamResults,
  getUserExamProfile
} from './examSimulation.api'

// ============================================================================
// Math Toolkit API Export
// ============================================================================
export {
  getMathCategories,
  getMathPatterns,
  getMathFormulas,
  startMathSession,
  submitCalculationStep,
  getMathSessionResults,
  getUserMathProgress
} from './mathToolkit.api'
