/**
 * System Domain - Centralized Types
 * 
 * This file exports all types used in the System domain (setup, i18n, tokens, subscriptions, tutor, audio, etc.)
 * to provide a single source of truth for type definitions.
 */

// ============================================================================
// Setup API Types
// ============================================================================

export interface SetupStatusResponse {
  setup_complete: boolean
  admin_created: boolean
  database_initialized: boolean
  ai_configured: boolean
}

export interface InstallInfo {
  version: string
  installed_at: string | null
  last_updated: string | null
}

export interface SystemCheckResult {
  name: string
  status: 'ok' | 'warning' | 'error'
  message: string
  details?: any
}

export interface SystemCheckResponse {
  passed: boolean
  checks: SystemCheckResult[]
  summary: string
}

export interface DatabaseInitResponse {
  success: boolean
  message: string
  migrations_run: number
}

export interface AdminCreateRequest {
  email: string
  password: string
  full_name: string
  organisation_name?: string
}

export interface AdminCreateResponse {
  success: boolean
  admin_id: string
  email: string
  message: string
}

export interface OrganisationCreateRequest {
  name: string
  description?: string
  website?: string
  logo_url?: string
}

export interface OrganisationCreateResponse {
  success: boolean
  organisation_id: string
  name: string
}

export interface AIConfigRequest {
  ai_provider: 'openai' | 'anthropic' | 'local'
  api_key?: string
  model?: string
}

export interface AIConfigResponse {
  success: boolean
  ai_provider: string
  model: string
}

export interface SeedDataRequest {
  include_courses: boolean
  include_users: boolean
  include_analytics: boolean
}

export interface SeedDataResponse {
  success: boolean
  records_created: number
  message: string
}

export interface SeedStatusResponse {
  seeding_in_progress: boolean
  current_step: string
  progress_percentage: number
}

export interface VerificationResponse {
  database_ok: boolean
  api_ok: boolean
  ai_configured: boolean
}

export interface CompleteInstallationResponse {
  success: boolean
  message: string
  setup_url?: string
}

export interface EnvironmentInfoResponse {
  node_version: string
  python_version: string
  database: string
  redis: string
}

export interface EnvironmentConfigRequest {
  database_url?: string
  redis_url?: string
  ai_provider?: string
  log_level?: string
}

export interface EnvironmentConfigResponse {
  success: boolean
  config_updated: boolean
}

// ============================================================================
// i18n / Translations API Types
// ============================================================================

export interface LanguageProgress {
  language_code: string
  language_name: string
  native_name: string
  flag_svg_code?: string
  total_keys: number
  translated_keys: number
  completion_percent: number | string
  percentage?: number
  priority: number
  active: boolean
  is_primary?: boolean
  created_at?: string
}

export interface TranslationSuggestion {
  key: string
  namespace: string
  original_text: string
  suggested_translation: string
  confidence: number
  source_language: string
  target_language: string
}

export interface ModerationQueueItem {
  item_id: string
  type: 'translation' | 'suggestion'
  content: string
  suggested_by: string
  created_at: string
  status: 'pending' | 'approved' | 'rejected'
}

export interface I18nNamespace {
  namespace_id: string
  name: string
  description: string
  key_count: number
  languages_count: number
}

export interface I18nKey {
  key: string
  namespace: string
  value: Record<string, string>
  last_updated: string
  updated_by: string
}

