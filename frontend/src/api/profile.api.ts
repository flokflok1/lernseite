import http from './http'

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface ProfileResponse {
  user_id: number
  email: string
  first_name: string
  last_name: string
  role: string
  hierarchy_level?: number // RBAC 2.0: Hierarchy level (1-10, owner=10)
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

export interface ProfileStatsResponse {
  courses_enrolled: number
  courses_completed: number
  total_learning_time: number
  achievements_count: number
  tokens_used: number
  tokens_remaining: number
}

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
// Profile API Functions
// ============================================================================

/**
 * Get current user's profile
 */
export const getProfile = async (): Promise<ProfileResponse> => {
  const response = await http.get<{ success: boolean; profile: ProfileResponse }>('/profile')
  return response.data.profile
}

/**
 * Update current user's profile
 */
export const updateProfile = async (data: UpdateProfileRequest): Promise<ProfileResponse> => {
  const response = await http.put<{ success: boolean; profile: ProfileResponse }>('/profile', data)
  return response.data.profile
}

/**
 * Change current user's password
 */
export const changePassword = async (data: ChangePasswordRequest): Promise<void> => {
  await http.post('/profile/change-password', data)
}

/**
 * Get current user's profile statistics
 */
export const getProfileStats = async (): Promise<ProfileStatsResponse> => {
  const response = await http.get<{ success: boolean; stats: ProfileStatsResponse }>('/profile/stats')
  return response.data.stats
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
// User Preferences API Functions (Phase Admin Desktop - Panel Sizes)
// ============================================================================

export interface PanelSize {
  width: number
  height: number
}

export interface PanelSizesMap {
  [panelType: string]: PanelSize
}

export interface UserPreferences {
  panel_sizes: PanelSizesMap
  ui_settings: Record<string, unknown>
  general_settings: Record<string, unknown>
}

export interface PreferencesResponse {
  success: boolean
  preferences: UserPreferences
}

export interface PanelSizesResponse {
  success: boolean
  panel_sizes: PanelSizesMap
}

/**
 * Get all user preferences
 */
export const getUserPreferences = async (): Promise<UserPreferences> => {
  const response = await http.get<PreferencesResponse>('/profile/preferences')
  return response.data.preferences
}

/**
 * Get panel sizes for all panel types
 */
export const getPanelSizes = async (): Promise<PanelSizesMap> => {
  // Note: API endpoint still uses 'window-sizes' for backward compatibility
  const response = await http.get<{ success: boolean; window_sizes: PanelSizesMap }>('/profile/preferences/window-sizes')
  return response.data.window_sizes
}

/**
 * Update panel size for a specific panel type
 */
export const updatePanelSize = async (
  panelType: string,
  width: number,
  height: number
): Promise<PanelSizesMap> => {
  // Note: API endpoint still uses 'window-sizes' for backward compatibility
  const response = await http.put<{ success: boolean; window_sizes: PanelSizesMap }>(
    '/profile/preferences/window-sizes',
    { window_type: panelType, width, height }
  )
  return response.data.window_sizes
}

/**
 * Delete a specific panel size preference
 */
export const deletePanelSize = async (panelType: string): Promise<PanelSizesMap> => {
  // Note: API endpoint still uses 'window-sizes' for backward compatibility
  const response = await http.delete<{ success: boolean; window_sizes: PanelSizesMap }>(
    `/profile/preferences/window-sizes/${panelType}`
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
