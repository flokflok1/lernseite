/**
 * User Domain - Barrel Export
 * ===========================
 *
 * This file provides a clean interface for importing all user-related APIs and types.
 * Part of the DDD Architecture - User Domain consolidating authentication, profile, and dashboard.
 *
 * Usage:
 * import { login, getProfile, updateThemePreference } from '@/api/user'
 * import type { User, ProfileResponse, ThemePreferenceResponse } from '@/api/user'
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
  // Dashboard Types
  GetLayoutResponse,
  SaveLayoutRequest,
  SaveLayoutResponse,
} from './types'

// ============================================================================
// Authentication API Export
// ============================================================================

export { getUserProfile, login, logout, refreshToken, register } from './auth.api'

// ============================================================================
// Profile API Export
// ============================================================================

export {
  changePassword,
  deleteAccount,
  deletePanelSize,
  getProfile,
  getProfileStats,
  getPanelSizes,
  getThemePreference,
  getUserPreferences,
  resetUserPreferences,
  updatePanelSize,
  updateProfile,
  updateThemePreference,
} from './profile.api'

// ============================================================================
// Dashboard API Export
// ============================================================================

export {
  applyWidgetPreset,
  getDashboardData,
  getDashboardLayout,
  getWidgetPresets,
  resetDashboardLayout,
  saveDashboardLayout,
} from './dashboard.api'
