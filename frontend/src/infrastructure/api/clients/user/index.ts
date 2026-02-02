/**
 * User Domain - Barrel Export
 * ===========================
 *
 * This file provides a clean interface for importing all user-related APIs and types.
 * Part of the DDD Architecture - User Domain consolidating authentication, profile, and dashboard.
 *
 * GBA (Group-Based Authorization):
 * - NO role field - authorization via groups with hierarchy_level (0-1000)
 * - full_name (not first_name/last_name)
 * - groups[] and permissions[] from login response
 *
 * Usage:
 * import { login, getProfile, updateThemePreference } from '@/application/services/api/user'
 * import type { User, UserGroup, LoginResponse } from '@/application/services/api/user'
 */

// ============================================================================
// Types Export (Single Source of Truth - types.ts)
// ============================================================================

export type {
  // Authentication Types (GBA)
  ChangePasswordRequest,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  User,
  UserGroup,                          // GBA: Group type for authorization
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
// Authentication API Export (Functions only - types from ./types)
// ============================================================================

export {
  login,
  register,
  logout,
  refreshToken,
  getUserProfile,
} from './auth.api'

// ============================================================================
// Profile API Export (Functions only - types from ./types)
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
} from './profile.api'

// ============================================================================
// Dashboard APIs
// ============================================================================

// NOTE: Dashboard APIs are in the system domain
// Import them from '@/application/services/api/system' instead
