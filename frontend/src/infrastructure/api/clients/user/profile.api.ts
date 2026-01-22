/**
 * LernsystemX - User Profile API Service
 *
 * Pattern: Transform backend DTOs to domain models at API layer
 * Profile responses include user data plus profile-specific fields
 * All snake_case backend fields transformed to camelCase at API layer
 */

import http from '../http'
import { transformUserFromAPI } from '../../utils/transformers'
import { User as UserDomainModel } from '@/domain/models/user/User.model'

// ============================================================================
// BACKEND DTO INTERFACES (what backend sends - snake_case)
// ============================================================================

/**
 * Backend Profile DTO (raw response from API)
 * Contains user profile data in snake_case format
 */
export interface BackendProfileDTO {
  user_id: number
  email: string
  first_name: string
  last_name: string
  role: string
  organisation_id?: number
  organisation_name?: string
  is_active: boolean
  subscription_plan: string
  subscription_status: string
  token_balance: number
  courses_enrolled: number
  courses_created: number
  created_at: string
}

/**
 * Backend ProfileStatsResponse DTO
 */
export interface BackendProfileStatsDTO {
  courses_enrolled: number
  courses_completed: number
  total_learning_time: number
  achievements_count: number
  tokens_used: number
  tokens_remaining: number
}

// ============================================================================
// DOMAIN RESPONSE INTERFACES (what callers get - camelCase)
// ============================================================================

/**
 * Domain Profile Response
 * Contains transformed user profile data in camelCase format
 */
export interface ProfileResponse {
  userId: number
  email: string
  firstName: string
  lastName: string
  role: string
  organisationId?: number
  organisationName?: string
  isActive: boolean
  subscriptionPlan: string
  subscriptionStatus: string
  tokenBalance: number
  coursesEnrolled: number
  coursesCreated: number
  createdAt: string
}

/**
 * Domain ProfileStats Response
 */
export interface ProfileStatsResponse {
  coursesEnrolled: number
  coursesCompleted: number
  totalLearningTime: number
  achievementsCount: number
  tokensUsed: number
  tokensRemaining: number
}

// ============================================================================
// REQUEST INTERFACES (unchanged)
// ============================================================================

export interface UpdateProfileRequest {
  first_name?: string
  last_name?: string
  email?: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
  confirm_password: string
}

export interface ThemePreferenceResponse {
  theme: 'system' | 'light' | 'dark'
}

export interface UpdateThemePreferenceRequest {
  theme: 'system' | 'light' | 'dark'
}

// ============================================================================
// TRANSFORMATION HELPERS
// ============================================================================

/**
 * Transform backend profile DTO to domain model
 * Converts snake_case fields to camelCase
 */
const transformProfileFromAPI = (data: BackendProfileDTO): ProfileResponse => {
  return {
    userId: data.user_id,
    email: data.email,
    firstName: data.first_name,
    lastName: data.last_name,
    role: data.role,
    organisationId: data.organisation_id,
    organisationName: data.organisation_name,
    isActive: data.is_active,
    subscriptionPlan: data.subscription_plan,
    subscriptionStatus: data.subscription_status,
    tokenBalance: data.token_balance,
    coursesEnrolled: data.courses_enrolled,
    coursesCreated: data.courses_created,
    createdAt: data.created_at
  }
}

/**
 * Transform backend profile stats DTO to domain model
 * Converts snake_case fields to camelCase
 */
const transformProfileStatsFromAPI = (data: BackendProfileStatsDTO): ProfileStatsResponse => {
  return {
    coursesEnrolled: data.courses_enrolled,
    coursesCompleted: data.courses_completed,
    totalLearningTime: data.total_learning_time,
    achievementsCount: data.achievements_count,
    tokensUsed: data.tokens_used,
    tokensRemaining: data.tokens_remaining
  }
}

// ============================================================================
// Profile API Functions
// ============================================================================

/**
 * Get current user's profile
 *
 * Returns user profile data transformed from snake_case to camelCase
 *
 * @returns ProfileResponse with transformed profile data
 */
export const getProfile = async (): Promise<ProfileResponse> => {
  const response = await http.get<{ success: boolean; profile: BackendProfileDTO }>('/profile')
  return transformProfileFromAPI(response.data.profile)
}

/**
 * Update current user's profile
 *
 * @param data - Profile update data (first_name, last_name, email)
 * @returns ProfileResponse with transformed profile data
 */
export const updateProfile = async (data: UpdateProfileRequest): Promise<ProfileResponse> => {
  const response = await http.put<{ success: boolean; profile: BackendProfileDTO }>('/profile', data)
  return transformProfileFromAPI(response.data.profile)
}

/**
 * Change current user's password
 */
export const changePassword = async (data: ChangePasswordRequest): Promise<void> => {
  await http.post('/profile/change-password', data)
}

/**
 * Get current user's profile statistics
 *
 * @returns ProfileStatsResponse with transformed stats data
 */
export const getProfileStats = async (): Promise<ProfileStatsResponse> => {
  const response = await http.get<{ success: boolean; stats: BackendProfileStatsDTO }>('/profile/stats')
  return transformProfileStatsFromAPI(response.data.stats)
}

/**
 * Delete own account (soft delete)
 */
export const deleteAccount = async (password: string, confirmation: string): Promise<void> => {
  await http.delete('/profile', {
    data: {
      password,
      confirmation
    }
  })
}

// ============================================================================
// Theme Preference API Functions (Phase B24)
// ============================================================================

/**
 * Get current user's theme preference
 */
export const getThemePreference = async (): Promise<ThemePreferenceResponse> => {
  const response = await http.get<ThemePreferenceResponse>('/profile/theme')
  return response.data
}

/**
 * Update current user's theme preference
 */
export const updateThemePreference = async (data: UpdateThemePreferenceRequest): Promise<ThemePreferenceResponse> => {
  const response = await http.patch<ThemePreferenceResponse>('/profile/theme', data)
  return response.data
}

// ============================================================================
// User Preferences API Functions (Phase Admin Desktop - Window Sizes)
// ============================================================================

export interface WindowSize {
  width: number
  height: number
}

export interface WindowSizesMap {
  [windowType: string]: WindowSize
}

export interface UserPreferences {
  window_sizes: WindowSizesMap
  ui_settings: Record<string, unknown>
  general_settings: Record<string, unknown>
}

export interface PreferencesResponse {
  success: boolean
  preferences: UserPreferences
}

export interface WindowSizesResponse {
  success: boolean
  window_sizes: WindowSizesMap
}

/**
 * Get all user preferences
 */
export const getUserPreferences = async (): Promise<UserPreferences> => {
  const response = await http.get<PreferencesResponse>('/profile/preferences')
  return response.data.preferences
}

/**
 * Get window sizes for all window types
 */
export const getWindowSizes = async (): Promise<WindowSizesMap> => {
  const response = await http.get<WindowSizesResponse>('/profile/preferences/window-sizes')
  return response.data.window_sizes
}

/**
 * Update window size for a specific window type
 */
export const updateWindowSize = async (
  windowType: string,
  width: number,
  height: number
): Promise<WindowSizesMap> => {
  const response = await http.put<{ success: boolean; window_sizes: WindowSizesMap }>(
    '/profile/preferences/window-sizes',
    { window_type: windowType, width, height }
  )
  return response.data.window_sizes
}

/**
 * Delete a specific window size preference
 */
export const deleteWindowSize = async (windowType: string): Promise<WindowSizesMap> => {
  const response = await http.delete<{ success: boolean; window_sizes: WindowSizesMap }>(
    `/profile/preferences/window-sizes/${windowType}`
  )
  return response.data.window_sizes
}

/**
 * Reset all user preferences to defaults
 */
export const resetUserPreferences = async (): Promise<UserPreferences> => {
  const response = await http.post<PreferencesResponse>('/profile/preferences/reset', {})
  return response.data.preferences
}
