/**
 * User Domain - TypeScript Types & Interfaces
 * =============================================
 *
 * Consolidated type definitions for all user-related APIs:
 * - Authentication (login, register, tokens)
 * - Profile (user data, preferences, theme)
 * - Dashboard (layout management)
 */

import type { DashboardLayout } from '@/domain/widgets'

// ============================================================================
// Authentication Types
// ============================================================================

export interface LoginRequest {
  email: string
  password: string
  totp_code?: string // Optional 2FA code
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string                    // GBA: Single full_name field
  username?: string                    // Optional username
  organisation_id?: string             // UUID string
}

/**
 * Group information returned from login (GBA - Group-Based Authorization)
 */
export interface UserGroup {
  id: string
  name: string
  slug: string
  type: string
  hierarchy_level: number
  access_level: string
}

export interface LoginResponse {
  success: boolean
  message: string
  access_token: string
  token_type: string
  expires_in: number
  refresh_token: string
  user: User
  groups: UserGroup[]           // GBA: User's groups with hierarchy levels
  permissions: string[]         // GBA: Effective permissions
  two_factor_required?: boolean
}

export interface RegisterResponse {
  success: boolean
  message: string
  user: User
  email_verification_required: boolean
}

export interface User {
  user_id: string
  email: string
  full_name: string                    // GBA: Single full_name field (not first_name/last_name)
  organisation_id: string | null       // UUID string
  is_active: boolean
  email_verified: boolean
  two_factor_enabled: boolean
  created_at: string
  updated_at: string
  last_login_at: string | null
  // GBA fields (populated after login from merged groups)
  groups?: UserGroup[]                 // User's groups with hierarchy levels
  permissions?: string[]               // Effective permissions
}

export interface UserProfileResponse {
  success: boolean
  user: User
}

// ============================================================================
// Profile Types
// ============================================================================

export interface ProfileResponse {
  user_id: string                      // UUID string
  email: string
  full_name: string                    // GBA: Single full_name field
  organisation_id?: string             // UUID string
  organisation_name?: string
  is_active: boolean
  email_verified: boolean
  two_factor_enabled: boolean
  subscription_plan: string
  subscription_status: string
  token_balance: number
  courses_enrolled: number
  courses_created: number
  created_at: string
  updated_at: string
  // GBA fields
  groups?: UserGroup[]                 // User's groups
  permissions?: string[]               // Effective permissions
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
  full_name?: string                   // GBA: Single full_name field
  email?: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
  confirm_password: string
}

// ============================================================================
// Theme Preference Types
// ============================================================================

export interface ThemePreferenceResponse {
  theme: 'system' | 'light' | 'dark'
}

export interface UpdateThemePreferenceRequest {
  theme: 'system' | 'light' | 'dark'
}

// ============================================================================
// User Preferences Types (Panel Sizes, UI Settings)
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

// ============================================================================
// Dashboard Types
// ============================================================================

export interface SaveLayoutRequest {
  layout: DashboardLayout
}

export interface SaveLayoutResponse {
  success: boolean
  message: string
  layout: DashboardLayout
}

export interface GetLayoutResponse {
  success: boolean
  layout: DashboardLayout
}
