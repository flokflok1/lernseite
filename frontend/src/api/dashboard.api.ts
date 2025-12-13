/**
 * LernsystemX - Dashboard API
 *
 * API endpoints for dashboard and widget management
 * Currently using LocalStorage, prepared for backend integration
 */

// import http from './http'  // TODO: Enable when backend is ready
import type { DashboardLayout } from '@/types/widgets'

// ============================================================================
// Types & Interfaces
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

// ============================================================================
// Dashboard API Functions
// ============================================================================

/**
 * Get user's dashboard layout from backend
 *
 * TODO: Backend Implementation
 * - Endpoint: GET /api/v1/dashboard/layout
 * - Returns: User's saved dashboard configuration
 * - If no layout exists: Return default layout for user's role
 *
 * Backend table: dashboard_layouts
 * Columns: user_id, layout_json, updated_at
 */
export const getDashboardLayout = async (): Promise<DashboardLayout> => {
  // TODO: Uncomment when backend is ready
  // const response = await http.get<GetLayoutResponse>('/dashboard/layout')
  // return response.data.layout

  throw new Error('Dashboard API not yet implemented - using LocalStorage')
}

/**
 * Save user's dashboard layout to backend
 *
 * TODO: Backend Implementation
 * - Endpoint: PUT /api/v1/dashboard/layout
 * - Body: { widgets: [...], presetId?: string }
 * - Validates widget IDs exist
 * - Validates user has access to all widgets (role-based)
 * - Updates or creates layout record
 *
 * Security:
 * - Must validate user can only save their own layout
 * - Validate all widget IDs against WIDGET_DEFINITIONS
 * - Validate role-based widget access
 */
export const saveDashboardLayout = async (_layout: DashboardLayout): Promise<void> => {
  // TODO: Uncomment when backend is ready
  // const response = await http.put<SaveLayoutResponse>('/dashboard/layout', {
  //   layout: {
  //     widgets: layout.widgets,
  //     presetId: layout.presetId,
  //     version: layout.version
  //   }
  // })
  // return response.data.layout

  throw new Error('Dashboard API not yet implemented - using LocalStorage')
}

/**
 * Reset dashboard layout to default
 *
 * TODO: Backend Implementation
 * - Endpoint: POST /api/v1/dashboard/layout/reset
 * - Deletes user's custom layout
 * - Returns default layout for user's role
 */
export const resetDashboardLayout = async (): Promise<DashboardLayout> => {
  // TODO: Uncomment when backend is ready
  // const response = await http.post<GetLayoutResponse>('/dashboard/layout/reset')
  // return response.data.layout

  throw new Error('Dashboard API not yet implemented - using LocalStorage')
}

// ============================================================================
// Widget Data API Functions
// ============================================================================

/**
 * Get aggregated dashboard data
 *
 * TODO: Backend Implementation (Optional Optimization)
 * - Endpoint: GET /api/v1/dashboard/data
 * - Returns: { profile, tokens, subscription, courses, stats }
 * - Single endpoint to reduce frontend API calls
 * - Caching recommended (Redis, 5-10 minutes)
 *
 * Currently frontend loads data separately via:
 * - profile.api.ts
 * - tokens.api.ts
 * - subscriptions.api.ts
 * - courses.api.ts
 */
export const getDashboardData = async () => {
  // TODO: Implement aggregated endpoint
  throw new Error('Aggregated dashboard data API not yet implemented')
}

// ============================================================================
// Widget Presets (Future Feature)
// ============================================================================

/**
 * Get available widget presets
 *
 * TODO: Backend Implementation (Phase F5+)
 * - Endpoint: GET /api/v1/dashboard/presets
 * - Returns: List of predefined layouts (e.g., "Focus Mode", "Teacher View")
 * - Role-based presets
 */
export const getWidgetPresets = async () => {
  // TODO: Implement presets
  throw new Error('Widget presets not yet implemented')
}

/**
 * Apply a widget preset
 *
 * TODO: Backend Implementation (Phase F5+)
 * - Endpoint: POST /api/v1/dashboard/presets/:presetId/apply
 * - Applies a predefined layout to user's dashboard
 */
export const applyWidgetPreset = async (_presetId: string) => {
  // TODO: Implement preset application
  throw new Error('Widget presets not yet implemented')
}
