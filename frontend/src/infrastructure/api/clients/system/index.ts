/**
 * System Domain - Barrel Export
 * 
 * This file provides a clean interface for importing all system APIs and types.
 * Use: import { getMyTokens, TokenBalanceResponse } from '@/infrastructure/api/system'
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
  // Gamification types
  BaseStats,
  GamificationData,
  GamificationApiResponse
} from './types'

// ============================================================================
// Setup API Export
// ============================================================================
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
  getSystemInfo,
  type SetupStatusResponse,
  type InstallInfo,
  type SystemCheckResult,
  type SystemCheckResponse,
  type DatabaseInitResponse,
  type AdminCreateRequest,
  type AdminCreateResponse,
  type OrganisationCreateRequest,
  type OrganisationCreateResponse,
  type AIConfigRequest,
  type AIConfigResponse,
  type SeedDataRequest,
  type SeedDataResponse,
  type SeedStatusResponse,
  type VerificationResponse,
  type CompleteInstallationResponse,
  type EnvironmentInfoResponse,
  type EnvironmentConfigRequest,
  type EnvironmentConfigResponse
} from './setup.api'

// ============================================================================
// i18n API Export
// ============================================================================
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
  deleteLanguage,
  type LanguageProgress,
  type TranslationSuggestion,
  type ModerationQueueItem,
  type I18nNamespace,
  type I18nKey
} from './i18n.api'

// ============================================================================
// Tokens API Export
// ============================================================================

export {
  getMyTokens,
  getTokenTransactions,
  getTokenUsage,
  estimateAICost,
  type TokenBalanceResponse,
  type TokenTransactionItem,
  type TokenUsageResponse
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
  type SubscriptionPlan,
  type SubscriptionResponse
} from './subscriptions.api'

// ============================================================================
// Gamification API Export
// ============================================================================

export {
  getMyGamificationData,
  getMyStats,
  getMySkills,
  getMyAchievements,
  type BaseStats,
  type GamificationData,
  type GamificationApiResponse
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
  type TTSSpeakRequest,
  type TTSSpeakResponse,
  type VoiceInfo,
  type VoicesResponse,
  type TutorScriptStep,
  type TutorScriptRequest,
  type TutorScriptResultStep,
  type TutorScriptResponse,
  type TutorKnowledgeRequest,
  type CourseContext,
  type ChapterContext,
  type TutorKnowledgeResponse
} from './tts.api'

// ============================================================================
// Audio API Export
// ============================================================================
export {
  transcribeAudio,
  transcribeAudioBase64,
  analyzeOralExplanation,
  getSupportedAudioFormats,
  type TranscriptionResult,
  type OralAnalysisResult,
  type AudioFormatsResponse
} from './audio.api'

// ============================================================================
// Math Toolkit API Export
// ============================================================================
export {
  mathToolkitApi,
  type MathCategory,
  type MathPattern,
  type PatternVariable,
  type PatternStep,
  type MathFormula,
  type MathSession,
  type CalculationStep,
  type UserProgress,
  type PatternTask,
  type CalculatorEntry
} from './mathToolkit.api'
