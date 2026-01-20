/**
 * User Domain - Barrel Export
 * ===========================
 *
 * This file provides a clean interface for importing all user-related APIs and types.
 * Part of the DDD Architecture - User Domain consolidating authentication, profile, and dashboard.
 *
 * Usage:
 * import { login, getProfile, updateThemePreference } from '@/infrastructure/api/clients/user'
 * import type { User, ProfileResponse, ThemePreferenceResponse } from '@/infrastructure/api/clients/user'
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

// NOTE: Authentication API functions are not yet fully migrated
// TODO: Implement auth functions (login, register, logout, refreshToken, getUserProfile) in auth.api.ts

// ============================================================================
// Profile API Export
// ============================================================================

// NOTE: Profile API functions are not yet fully migrated
// TODO: Implement profile functions in profile.api.ts:
// - changePassword, deleteAccount, deletePanelSize, getProfile, getProfileStats
// - getPanelSizes, getThemePreference, getUserPreferences, resetUserPreferences
// - updatePanelSize, updateProfile, updateThemePreference

// ============================================================================
// Dashboard APIs
// ============================================================================

// NOTE: Dashboard APIs are in the system domain
// Import them from '@/infrastructure/api/clients/system' instead
