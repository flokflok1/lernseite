/**
 * Public Domain - Barrel Export
 *
 * This file provides a clean interface for importing all public (unauthenticated) APIs and types.
 * Use: import { getSetupStatus, getBundle } from '@/infrastructure/api/clients/public'
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
