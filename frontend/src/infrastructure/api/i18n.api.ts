/**
 * i18n API Client
 * ================
 * API calls for internationalization system
 */

import http from './http'

export interface LanguageProgress {
  language_code: string
  language_name: string
  native_name: string
  flag_svg_code: string
  is_primary: boolean
  priority: number
  rtl: boolean
  active: boolean
  total_keys: number
  translated_keys: number
  completion_percent: number
  verified_keys: number
  pending_suggestions: number
}

export interface TranslationSuggestion {
  suggestion_id: string
  translation_id: string | null
  key_id: string | null
  language_code: string
  suggested_value: string
  reason: string | null
  suggested_by: string
  suggested_by_username: string
  suggested_at: string
  votes_up: number
  votes_down: number
  vote_score: number
  status: 'pending' | 'approved' | 'rejected' | 'duplicate'
  current_value: string | null
  key_path: string
}

export interface ModerationQueueItem {
  queue_id: string
  item_type: 'translation' | 'suggestion'
  translation_id: string | null
  suggestion_id: string | null
  priority: number
  status: string
  quality_score: number | null
  recommendation: string | null
  ai_suggestion: string | null
  ai_explanation: string | null
  suggested_value: string | null
  current_value: string | null
  language_code: string
  key_path: string
  context: string | null
}

export interface I18nNamespace {
  namespace_id: number
  namespace_code: string
  name: string
  description: string
  icon: string
  sort_order: number
  key_count: number
}

export interface I18nKey {
  key_id: string
  namespace_id: number
  namespace_code: string
  key_path: string
  context: string | null
  placeholders: string[]
  is_plural: boolean
  translation_count: number
}

// =============================================================================
// Public API
// =============================================================================

/**
 * Get translation bundle for a language
 */
export async function getBundle(
  languageCode: string,
  namespace?: string
): Promise<Record<string, string>> {
  const params = namespace ? { namespace } : {}
  const response = await http.get(`/i18n/bundle/${languageCode}`, { params })
  return response.data.data
}

/**
 * Get all available languages with progress
 */
export async function getLanguages(): Promise<LanguageProgress[]> {
  const response = await http.get('/i18n/languages')
  return response.data.data
}

/**
 * Get detailed progress for a specific language
 */
export async function getLanguageProgress(languageCode: string): Promise<{
  progress: LanguageProgress
  missing_sample: Array<{ key_path: string; german_value: string }>
}> {
  const response = await http.get(`/i18n/languages/${languageCode}/progress`)
  return response.data.data
}

// =============================================================================
// Authenticated API - Suggestions
// =============================================================================

/**
 * Submit a translation suggestion
 */
export async function submitSuggestion(data: {
  translation_id?: string
  key_id?: string
  language_code: string
  suggested_value: string
  reason?: string
}): Promise<{ suggestion_id: string }> {
  const response = await http.post('/i18n/suggestions', data)
  return response.data.data
}

/**
 * Get translation suggestions
 */
export async function getSuggestions(params?: {
  language_code?: string
  status?: 'pending' | 'approved' | 'rejected'
  limit?: number
}): Promise<TranslationSuggestion[]> {
  const response = await http.get('/i18n/suggestions', { params })
  return response.data.data
}

/**
 * Vote for a suggestion
 */
export async function voteSuggestion(
  suggestionId: string,
  voteType: 'up' | 'down'
): Promise<void> {
  await http.post(`/i18n/suggestions/${suggestionId}/vote`, { vote_type: voteType })
}

/**
 * Request translation for a language (on-demand)
 */
export async function requestTranslation(data: {
  target_language: string
  scope?: 'full' | 'namespace' | 'key'
  namespace_id?: number
}): Promise<{ request_id: string; request_count: number }> {
  const response = await http.post('/i18n/request-translation', data)
  return response.data.data
}

// =============================================================================
// Admin API - Moderation
// =============================================================================

/**
 * Get moderation dashboard data
 */
export async function getModerationDashboard(): Promise<Array<{
  language_code: string
  language_name: string
  flag_svg_code: string
  pending_count: number
  ai_reviewing_count: number
  awaiting_human_count: number
  pending_suggestions: number
  ai_reviews_24h: number
  avg_quality_7d: number | null
}>> {
  const response = await http.get('/i18n/admin/moderation/dashboard')
  return response.data.data
}

/**
 * Get moderation queue
 */
export async function getModerationQueue(params?: {
  status?: 'pending' | 'ai_reviewing' | 'awaiting_human' | 'completed'
  language_code?: string
  limit?: number
}): Promise<ModerationQueueItem[]> {
  const response = await http.get('/i18n/admin/moderation/queue', { params })
  return response.data.data
}

/**
 * Review a queue item (human moderation)
 */
export async function reviewQueueItem(
  queueId: string,
  decision: 'approve' | 'reject',
  comment?: string
): Promise<void> {
  await http.post(`/i18n/admin/moderation/queue/${queueId}/review`, {
    decision,
    comment
  })
}

/**
 * Trigger AI review for a translation/suggestion
 */
export async function triggerAiReview(data: {
  translation_id?: string
  suggestion_id?: string
}): Promise<{
  review_id: string
  quality_score: number
  recommendation: string
  ai_suggestion?: string
}> {
  const response = await http.post('/i18n/admin/moderation/ai-review', data)
  return response.data.data
}

/**
 * Get AI moderation config
 */
export async function getAiConfig(): Promise<Record<string, any>> {
  const response = await http.get('/i18n/admin/config')
  return response.data.data
}

/**
 * Update AI moderation config
 */
export async function updateAiConfig(config: {
  moderation_model?: string
  auto_approve_threshold?: number
  auto_reject_threshold?: number
  human_review_threshold?: number
  enabled_languages?: string[]
}): Promise<{
  updated_keys: string[]
  config: Record<string, any>
}> {
  const response = await http.put('/i18n/admin/config', config)
  return response.data.data
}

/**
 * Invalidate translation cache
 */
export async function invalidateCache(languageCode?: string): Promise<void> {
  await http.post('/i18n/admin/cache/invalidate', { language_code: languageCode })
}

// =============================================================================
// Admin API - Keys & Translations Management
// =============================================================================

/**
 * Get all namespaces
 */
export async function getNamespaces(): Promise<I18nNamespace[]> {
  const response = await http.get('/i18n/admin/namespaces')
  return response.data.data
}

/**
 * Get translation keys
 */
export async function getKeys(params?: {
  namespace_id?: number
  search?: string
  limit?: number
  offset?: number
}): Promise<I18nKey[]> {
  const response = await http.get('/i18n/admin/keys', { params })
  return response.data.data
}

/**
 * Get translations for a specific key
 */
export async function getKeyTranslations(keyId: string): Promise<Array<{
  translation_id: string
  language_code: string
  language_name: string
  flag_svg_code: string
  value: string
  status: string
  is_verified: boolean
  quality_score: number | null
  ai_recommendation: string | null
}>> {
  const response = await http.get(`/i18n/admin/keys/${keyId}/translations`)
  return response.data.data
}

/**
 * Create a new translation key
 */
export async function createKey(data: {
  namespace_id: number
  key_path: string
  description?: string
  context_hint?: string
  max_length?: number
  placeholders?: string[]
}): Promise<{ key_id: number }> {
  const response = await http.post('/i18n/admin/keys', data)
  return response.data.data
}

/**
 * Set or update a translation
 */
export async function setTranslation(
  keyId: number,
  languageCode: string,
  value: string,
  isMachineTranslated = false
): Promise<void> {
  await http.put(`/i18n/admin/keys/${keyId}/translations/${languageCode}`, {
    value,
    is_machine_translated: isMachineTranslated
  })
}

/**
 * Generate AI translation for a single key
 */
export async function aiTranslate(
  keyId: number,
  targetLanguage: string
): Promise<{
  success: boolean
  translation: string
  tokens_used: number
}> {
  const response = await http.post('/i18n/admin/ai/translate', {
    key_id: keyId,
    target_language: targetLanguage
  })
  return response.data.data
}

/**
 * Generate AI translations for multiple missing keys
 */
export async function aiTranslateBulk(data: {
  target_language: string
  namespace_id?: number
  limit?: number
}): Promise<{
  total: number
  success: number
  failed: number
  tokens_used: number
  details: Array<{
    key_path: string
    success: boolean
    error?: string
  }>
}> {
  const response = await http.post('/i18n/admin/ai/translate/bulk', data)
  return response.data.data
}

/**
 * Seed i18n keys from frontend default messages
 */
export async function seedKeys(messages: Record<string, string>): Promise<{
  created: number
  updated: number
  errors: string[]
}> {
  const response = await http.post('/i18n/admin/seed-keys', { messages })
  return response.data.data
}

/**
 * Create or update a language
 */
export async function createLanguage(data: {
  language_code: string
  language_name: string
  native_name: string
  flag_svg_code: string
  active?: boolean
  rtl?: boolean
  is_primary?: boolean
  priority?: number

}): Promise<{ language_code: string }> {
  const response = await http.post('/i18n/admin/languages', data)
  return response.data.data
}

/**
 * Update a language
 */
export async function updateLanguage(
  languageCode: string,
  data: {
    language_name?: string
    native_name?: string
    flag_svg_code?: string
    active?: boolean
    rtl?: boolean
    is_primary?: boolean
    priority?: number
  
  }
): Promise<void> {
  await http.put(`/i18n/admin/languages/${languageCode}`, data)
}

/**
 * Delete a language
 */
export async function deleteLanguage(languageCode: string): Promise<void> {
  await http.delete(`/i18n/admin/languages/${languageCode}`)
}

export default {
  // Public
  getBundle,
  getLanguages,
  getLanguageProgress,
  // Suggestions
  submitSuggestion,
  getSuggestions,
  voteSuggestion,
  requestTranslation,
  // Admin - Moderation
  getModerationDashboard,
  getModerationQueue,
  reviewQueueItem,
  triggerAiReview,
  getAiConfig,
  updateAiConfig,
  invalidateCache,
  // Admin - Keys
  getNamespaces,
  getKeys,
  getKeyTranslations,
  createKey,
  setTranslation,
  // Admin - AI Translation
  aiTranslate,
  aiTranslateBulk,
  seedKeys,
  // Admin - Languages
  createLanguage,
  updateLanguage,
  deleteLanguage
}
