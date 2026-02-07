/**
 * Admin Languages API Client
 *
 * HTTP client for system language management endpoints.
 * Maps to backend: /api/v1/i18n/admin/languages
 */

import api from '@/infrastructure/api/http'

// Note: http.ts already has baseURL '/api/v1'
const BASE_URL = '/i18n/admin'

/** Language record returned by the API */
export interface AdminLanguage {
  language_code: string
  language_name: string
  native_name: string
  flag_emoji: string
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
  flag_emoji: string
  active?: boolean
  rtl?: boolean
  is_primary?: boolean
  priority?: number
  fallback_language?: string
}

/** Payload for updating a language */
export interface UpdateLanguagePayload {
  language_name?: string
  native_name?: string
  flag_emoji?: string
  active?: boolean
  rtl?: boolean
  is_primary?: boolean
  priority?: number
  fallback_language?: string | null
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
   * Delete a language (cannot delete primary).
   */
  delete: async (languageCode: string): Promise<void> => {
    try {
      await api.delete(`${BASE_URL}/languages/${languageCode}`)
    } catch (error: any) {
      const errorData = error.response?.data as ApiErrorResponse
      throw new Error(errorData?.error?.message || 'Failed to delete language')
    }
  }
}
