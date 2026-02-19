/**
 * Admin Feature Flags Management API
 *
 * Endpoints for managing enterprise feature flags and rollouts:
 * - Feature CRUD operations
 * - Enable/disable features
 * - Progressive rollout management
 * - A/B testing and experimentation
 * - Audit logging
 *
 * All endpoints require admin authentication.
 */

import http from '@/infrastructure/api/http'
import type {
  FeatureFlag,
  FeatureFlagCreateRequest,
  FeatureFlagUpdateRequest,
  FeatureFlagFilters,
  RolloutPlan,
  PaginatedResponse
} from '../types'

// ============================================================================
// FEATURE FLAGS CRUD
// ============================================================================

/**
 * List all feature flags with optional filters
 *
 * @param params - Query parameters (limit, offset, enabled, category)
 * @returns Paginated list of feature flags
 */
export const adminGetFeatureFlags = async (
  params: FeatureFlagFilters = {}
): Promise<PaginatedResponse<FeatureFlag>> => {
  const response = await http.get<{
    success: boolean
    data: FeatureFlag[]
    meta: {
      total: number
      limit: number
      offset: number
      timestamp: string
    }
  }>('/admin/feature-configuration/features', { params })

  return {
    items: response.data.data,
    total: response.data.meta.total,
    limit: response.data.meta.limit,
    offset: response.data.meta.offset
  }
}

/**
 * Get a specific feature flag by ID
 *
 * @param featureId - Feature flag ID
 * @returns Feature flag details
 */
export const adminGetFeatureFlag = async (featureId: string): Promise<FeatureFlag> => {
  const response = await http.get<{
    success: boolean
    data: FeatureFlag
  }>(`/admin/feature-configuration/features/${featureId}`)

  return response.data.data
}

/**
 * Create a new feature flag
 *
 * @param data - Feature flag creation data
 * @returns Created feature flag
 */
export const adminCreateFeatureFlag = async (
  data: FeatureFlagCreateRequest
): Promise<FeatureFlag> => {
  const response = await http.post<{
    success: boolean
    data: FeatureFlag
  }>('/admin/feature-configuration/features', data)

  return response.data.data
}

/**
 * Update an existing feature flag
 *
 * @param featureId - Feature flag ID
 * @param data - Update data
 * @returns Updated feature flag
 */
export const adminUpdateFeatureFlag = async (
  featureId: string,
  data: Partial<FeatureFlagUpdateRequest>
): Promise<FeatureFlag> => {
  const response = await http.patch<{
    success: boolean
    data: FeatureFlag
  }>(`/admin/feature-configuration/features/${featureId}`, data)

  return response.data.data
}

// ============================================================================
// FEATURE ENABLE/DISABLE
// ============================================================================

/**
 * Enable a feature flag
 *
 * @param featureId - Feature flag ID
 * @returns Updated feature flag
 */
export const adminEnableFeature = async (featureId: string): Promise<FeatureFlag> => {
  const response = await http.post<{
    success: boolean
    data: FeatureFlag
  }>(`/admin/feature-configuration/features/${featureId}/enable`, {})

  return response.data.data
}

/**
 * Disable a feature flag
 *
 * @param featureId - Feature flag ID
 * @param reason - Optional reason for disabling
 * @returns Updated feature flag
 */
export const adminDisableFeature = async (
  featureId: string,
  reason?: string
): Promise<FeatureFlag> => {
  const response = await http.post<{
    success: boolean
    data: FeatureFlag
  }>(`/admin/feature-configuration/features/${featureId}/disable`, {
    reason
  })

  return response.data.data
}

// ============================================================================
// PROGRESSIVE ROLLOUT
// ============================================================================

/**
 * List all rollout plans
 *
 * @param params - Query parameters (featureName, status, limit, offset)
 * @returns Paginated list of rollout plans
 */
export const adminGetRolloutPlans = async (
  params: {
    featureName?: string
    status?: string
    limit?: number
    offset?: number
  } = {}
): Promise<PaginatedResponse<RolloutPlan>> => {
  const response = await http.get<{
    success: boolean
    data: RolloutPlan[]
    meta: {
      total: number
      limit: number
      offset: number
      timestamp: string
    }
  }>('/admin/feature-configuration/rollout/plans', { params })

  return {
    items: response.data.data,
    total: response.data.meta.total,
    limit: response.data.meta.limit,
    offset: response.data.meta.offset
  }
}

/**
 * Get a specific rollout plan by ID
 *
 * @param planId - Rollout plan ID
 * @returns Rollout plan details
 */
export const adminGetRolloutPlan = async (planId: string): Promise<RolloutPlan> => {
  const response = await http.get<{
    success: boolean
    data: RolloutPlan
  }>(`/admin/feature-configuration/rollout/plans/${planId}`)

  return response.data.data
}

/**
 * Create a new rollout plan
 *
 * @param data - Rollout plan creation data
 * @returns Created rollout plan
 */
export const adminCreateRolloutPlan = async (
  data: {
    featureName: string
    description?: string
    targetPercentage?: number
    startDate?: string
    estimatedEndDate?: string
  }
): Promise<RolloutPlan> => {
  const response = await http.post<{
    success: boolean
    data: RolloutPlan
  }>('/admin/feature-configuration/rollout/plans', data)

  return response.data.data
}

/**
 * Update rollout percentage (advance to next phase)
 *
 * @param planId - Rollout plan ID
 * @param percentage - New rollout percentage (5, 25, 50, 100)
 * @returns Updated rollout plan
 */
export const adminUpdateRolloutPercentage = async (
  planId: string,
  percentage: number
): Promise<RolloutPlan> => {
  const response = await http.patch<{
    success: boolean
    data: RolloutPlan
  }>(`/admin/feature-configuration/rollout/plans/${planId}/percentage`, {
    percentage
  })

  return response.data.data
}

/**
 * Pause a rollout
 *
 * @param planId - Rollout plan ID
 * @param reason - Optional reason for pausing
 * @returns Updated rollout plan
 */
export const adminPauseRollout = async (
  planId: string,
  reason?: string
): Promise<RolloutPlan> => {
  const response = await http.post<{
    success: boolean
    data: RolloutPlan
  }>(`/admin/feature-configuration/rollout/plans/${planId}/pause`, {
    reason
  })

  return response.data.data
}

/**
 * Resume a paused rollout
 *
 * @param planId - Rollout plan ID
 * @returns Updated rollout plan
 */
export const adminResumeRollout = async (planId: string): Promise<RolloutPlan> => {
  const response = await http.post<{
    success: boolean
    data: RolloutPlan
  }>(`/admin/feature-configuration/rollout/plans/${planId}/resume`, {})

  return response.data.data
}

/**
 * Rollback a feature (cancel rollout)
 *
 * @param planId - Rollout plan ID
 * @param reason - Optional reason for rollback
 * @returns Updated rollout plan
 */
export const adminRollbackFeature = async (
  planId: string,
  reason?: string
): Promise<RolloutPlan> => {
  const response = await http.post<{
    success: boolean
    data: RolloutPlan
  }>(`/admin/feature-configuration/rollout/plans/${planId}/rollback`, {
    reason
  })

  return response.data.data
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get all enabled features
 */
export const adminGetEnabledFeatures = async (): Promise<FeatureFlag[]> => {
  const result = await adminGetFeatureFlags({ enabled: true, limit: 500 })
  return result.items
}

/**
 * Get features by category
 */
export const adminGetFeaturesByCategory = async (
  category: string
): Promise<FeatureFlag[]> => {
  const result = await adminGetFeatureFlags({ category, limit: 500 })
  return result.items
}

/**
 * Toggle feature enable/disable status
 */
export const adminToggleFeature = async (
  featureId: string,
  isEnabled: boolean,
  reason?: string
): Promise<FeatureFlag> => {
  if (isEnabled) {
    return adminEnableFeature(featureId)
  } else {
    return adminDisableFeature(featureId, reason)
  }
}
