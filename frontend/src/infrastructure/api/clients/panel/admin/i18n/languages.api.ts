/**
 * Admin Languages API Client
 *
 * HTTP client for system language management endpoints.
 * Maps to backend: /api/v1/i18n/admin/languages
 *                   /api/v1/admin/translations/*
 */

import api from '@/infrastructure/api/http'

// Note: http.ts already has baseURL '/api/v1'
const BASE_URL = '/i18n/admin'
const TRANSLATIONS_URL = '/admin/translations'

/** Language record returned by the API */
export interface AdminLanguage {
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
}

/** Payload for creating a new language */
export interface CreateLanguagePayload {
  language_code: string
  language_name: string
  native_name: string
  flag_svg_code: string
  active?: boolean
  rtl?: boolean
  is_primary?: boolean
  priority?: number
}

/** Payload for updating a language */
export interface UpdateLanguagePayload {
  language_name?: string
  native_name?: string
  flag_svg_code?: string
  active?: boolean
  rtl?: boolean
  is_primary?: boolean
  priority?: number
}

/** Response from the deterministic draft endpoint */
export interface LanguageDraft {
  code: string
  name: string
  native_name: string
  flag_svg_code: string
  is_rtl: boolean
  priority: number
}

/** Import result */
export interface ImportResult {
  keys_created: number
  translations_imported: number
}

/** Bulk translate job progress */
export interface BulkTranslateJob {
  job_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress_percentage: number
  output_data: {
    translated: number
    failed: number
    total: number
    offset: number
    error?: string
  }
}

/** Review translation item */
export interface ReviewTranslation {
  translation_id: string
  key_id: string
  key_path: string
  namespace_code: string
  source_value: string
  translated_value: string
  translation_source: string
  is_verified: boolean
  quality_score: number | null
  updated_at: string | null
}

/** Paginated review response */
export interface ReviewResponse {
  data: ReviewTranslation[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

interface ApiSuccessResponse<T> {
  success: true
  data: T
}

interface ApiErrorResponse {
  success: false
  error: { code: string; message: string }
}

/**
 * Admin Languages API Service
 */
export const languagesApi = {
  /**
   * Fetch all languages (including inactive) for admin management.
   */
  getAll: async (): Promise<AdminLanguage[]> => {
    try {
      const response = await api.get<ApiSuccessResponse<AdminLanguage[]>>(
        `${BASE_URL}/languages`
      )
      return response.data.data
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to load languages')
    }
  },

  /**
   * Create a new language.
   */
  create: async (payload: CreateLanguagePayload): Promise<{ language_code: string }> => {
    try {
      const response = await api.post<ApiSuccessResponse<{ language_code: string }>>(
        `${BASE_URL}/languages`,
        payload
      )
      return response.data.data
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to create language')
    }
  },

  /**
   * Update a language.
   */
  update: async (
    languageCode: string,
    payload: UpdateLanguagePayload
  ): Promise<void> => {
    try {
      await api.put(`${BASE_URL}/languages/${languageCode}`, payload)
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to update language')
    }
  },

  /**
   * Suggest language metadata from a code or name (deterministic, no AI).
   */
  draft: async (input: string): Promise<LanguageDraft> => {
    try {
      const response = await api.post<ApiSuccessResponse<LanguageDraft>>(
        `${TRANSLATIONS_URL}/supported-languages/draft`,
        { input }
      )
      return response.data.data
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to get language draft')
    }
  },

  /**
   * Delete a language (cannot delete primary).
   */
  delete: async (languageCode: string): Promise<void> => {
    try {
      await api.delete(`${BASE_URL}/languages/${languageCode}`)
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to delete language')
    }
  },

  /**
   * Import locale JSON data for a language.
   */
  importLocales: async (
    languageCode: string,
    namespaces: Record<string, Record<string, unknown>>
  ): Promise<ImportResult> => {
    try {
      const response = await api.post<ApiSuccessResponse<ImportResult> & ImportResult>(
        `${TRANSLATIONS_URL}/import-locales`,
        { language_code: languageCode, namespaces }
      )
      return {
        keys_created: response.data.keys_created ?? response.data.data?.keys_created ?? 0,
        translations_imported: response.data.translations_imported ?? response.data.data?.translations_imported ?? 0
      }
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to import locales')
    }
  },

  /**
   * Create a bulk translation job.
   */
  startBulkTranslate: async (
    sourceLanguage: string,
    targetLanguage: string,
    namespaceCode?: string | null
  ): Promise<BulkTranslateJob> => {
    try {
      const response = await api.post<{ success: true } & BulkTranslateJob>(
        `${TRANSLATIONS_URL}/bulk-translate`,
        { source_language: sourceLanguage, target_language: targetLanguage, namespace_code: namespaceCode ?? null }
      )
      return response.data
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to start bulk translate')
    }
  },

  /**
   * Execute next step in bulk translation job.
   */
  runBulkTranslateStep: async (jobId: string): Promise<BulkTranslateJob> => {
    try {
      const response = await api.post<{ success: true } & BulkTranslateJob>(
        `${TRANSLATIONS_URL}/bulk-translate/${jobId}/run`
      )
      return response.data
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to run translate step')
    }
  },

  /**
   * Poll bulk translation job progress.
   */
  getBulkTranslateProgress: async (jobId: string): Promise<BulkTranslateJob> => {
    try {
      const response = await api.get<{ success: true } & BulkTranslateJob>(
        `${TRANSLATIONS_URL}/bulk-translate/${jobId}`
      )
      return response.data
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to get translate progress')
    }
  },

  /**
   * Get paginated translations for review.
   */
  getReviewTranslations: async (params: {
    language: string
    source_language?: string
    namespace?: string
    status?: 'all' | 'verified' | 'unverified'
    search?: string
    page?: number
    per_page?: number
  }): Promise<ReviewResponse> => {
    try {
      const response = await api.get<{ success: true } & ReviewResponse>(
        `${TRANSLATIONS_URL}/review`,
        { params }
      )
      return response.data
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to load review translations')
    }
  },

  /**
   * Edit a single translation value.
   */
  editTranslation: async (translationId: string, translatedValue: string): Promise<void> => {
    try {
      await api.put(`${TRANSLATIONS_URL}/review/${translationId}`, { translated_value: translatedValue })
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to edit translation')
    }
  },

  /**
   * Verify a single translation.
   */
  verifyTranslation: async (translationId: string): Promise<void> => {
    try {
      await api.post(`${TRANSLATIONS_URL}/review/${translationId}/verify`)
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to verify translation')
    }
  },

  /**
   * Bulk verify multiple translations.
   */
  bulkVerifyTranslations: async (translationIds: string[]): Promise<void> => {
    try {
      await api.post(`${TRANSLATIONS_URL}/review/bulk-verify`, { translation_ids: translationIds })
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to bulk verify translations')
    }
  }
}
