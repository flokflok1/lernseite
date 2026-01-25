/**
 * User Domain - Barrel Export
 * ===========================
 *
 * This file provides a clean interface for importing all user-related APIs and types.
 * Part of the DDD Architecture - User Domain consolidating authentication, profile, and dashboard.
 *
 * Usage:
 * import { login, getProfile, updateThemePreference } from '@/application/services/api/user'
 * import type { User, ProfileResponse, ThemePreferenceResponse } from '@/application/services/api/user'
 */

// ============================================================================
// Types Export (Consolidated from all user API modules)
// ============================================================================

export type {
  // Authentication Types
  ChangePasswordRequest,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  User,
  UserProfileResponse,
  // Profile Types
  PanelSize,
  PanelSizesMap,
  PanelSizesResponse,
  PreferencesResponse,
  ProfileResponse,
  ProfileStatsResponse,
  UpdateProfileRequest,
  UpdateThemePreferenceRequest,
  ThemePreferenceResponse,
  UserPreferences,
} from './types'

// ============================================================================
// Authentication API Export
// ============================================================================

export {
  login,
  register,
  logout,
  refreshToken,
  getUserProfile,
  type LoginRequest,
  type LoginResponse,
  type RegisterRequest,
  type RegisterResponse,
  type User,
  type UserProfileResponse
} from './auth.api'

// ============================================================================
// Profile API Export
// ============================================================================

export {
  getProfile,
  updateProfile,
  changePassword,
  getProfileStats,
  deleteAccount,
  getThemePreference,
  updateThemePreference,
  getUserPreferences,
  getWindowSizes,
  updateWindowSize,
  deleteWindowSize,
  resetUserPreferences,
  type ProfileResponse,
  type ProfileStatsResponse,
  type UpdateProfileRequest,
  type ChangePasswordRequest,
  type ThemePreferenceResponse,
  type UpdateThemePreferenceRequest,
  type UserPreferences,
  type PanelSize,
  type PanelSizesMap,
  type PanelSizesResponse,
  type PreferencesResponse,
  type UpdateThemePreferenceRequest
} from './profile.api'

// ============================================================================
// Dashboard APIs
// ============================================================================

// NOTE: Dashboard APIs are in the system domain
// Import them from '@/application/services/api/system' instead
