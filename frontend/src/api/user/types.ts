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
  first_name: string
  last_name: string
  role?: string
  organisation_id?: number
}

export interface LoginResponse {
  success: boolean
  message: string
  access_token: string
  token_type: string
  expires_in: number
  refresh_token: string
  user: User
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
  first_name: string
  last_name: string
  role: string
  hierarchy_level?: number // RBAC 2.0: Dynamic hierarchy level (1-10, owner=10)
  organisation_id: number | null
  is_active: boolean
  created_at: string
  two_factor_enabled?: boolean
}

export interface UserProfileResponse {
  success: boolean
  user: User
}

// ============================================================================
// Profile Types
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
