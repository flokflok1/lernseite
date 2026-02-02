/**
 * Feature Flags Management Store
 * ==================================
 * Pinia store for admin feature flag management with progressive rollouts.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  FeatureFlag,
  FeatureFlagCreateRequest,
  FeatureFlagUpdateRequest,
  RolloutPlan
} from '@/application/services/api/admin'
import {
  adminGetFeatureFlags,
  adminGetFeatureFlag,
  adminCreateFeatureFlag,
  adminUpdateFeatureFlag,
  adminEnableFeature,
  adminDisableFeature,
  adminGetRolloutPlans,
  adminGetRolloutPlan,
  adminCreateRolloutPlan,
  adminUpdateRolloutPercentage,
  adminPauseRollout,
  adminResumeRollout,
  adminRollbackFeature,
  adminToggleFeature,
  adminGetEnabledFeatures,
  adminGetFeaturesByCategory
} from '@/application/services/api/admin'

export const useFeatureFlagsStore = defineStore('feature-flags', () => {
  // =============================================================================
  // State
  // =============================================================================

  const flags = ref<FeatureFlag[]>([])
  const selectedFlag = ref<FeatureFlag | null>(null)
  const rolloutPlans = ref<RolloutPlan[]>([])
  const selectedRolloutPlan = ref<RolloutPlan | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetchedAt = ref<number | null>(null)

  // =============================================================================
  // Computed
  // =============================================================================

  const enabledFlags = computed(() => flags.value.filter((f) => f.is_enabled))
  const disabledFlags = computed(() => flags.value.filter((f) => !f.is_enabled))
  const totalFlags = computed(() => flags.value.length)
  const totalEnabledFlags = computed(() => enabledFlags.value.length)

  const flagsByCategory = computed(() => {
    const categories: Record<string, FeatureFlag[]> = {}
    flags.value.forEach((flag) => {
      const category = flag.category || 'uncategorized'
      if (!categories[category]) {
        categories[category] = []
      }
      categories[category].push(flag)
    })
    return categories
  })

  const activeRollouts = computed(() =>
    rolloutPlans.value.filter((plan) => plan.status === 'in_progress')
  )

  // =============================================================================
  // Actions
  // =============================================================================

  /**
   * Fetch all feature flags with pagination
   */
  async function fetchFlags(params?: {
    limit?: number
    offset?: number
    enabled?: boolean
    category?: string
  }) {
    loading.value = true
    error.value = null

    try {
      const response = await adminGetFeatureFlags(params)
      flags.value = response.items
      lastFetchedAt.value = Date.now()
      return response
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to fetch feature flags'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch single feature flag with details
   */
  async function fetchFlag(featureId: string) {
    loading.value = true
    error.value = null

    try {
      const flag = await adminGetFeatureFlag(featureId)
      selectedFlag.value = flag
      return flag
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to fetch feature flag'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create new feature flag
   */
  async function createFlag(data: FeatureFlagCreateRequest) {
    loading.value = true
    error.value = null

    try {
      const newFlag = await adminCreateFeatureFlag(data)
      flags.value.push(newFlag)
      return newFlag
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to create feature flag'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update existing feature flag
   */
  async function updateFlag(featureId: string, data: FeatureFlagUpdateRequest) {
    loading.value = true
    error.value = null

    try {
      const updatedFlag = await adminUpdateFeatureFlag(featureId, data)
      const index = flags.value.findIndex((f) => f.feature_id === featureId)
      if (index !== -1) {
        flags.value[index] = { ...flags.value[index], ...updatedFlag }
      }
      if (selectedFlag.value?.feature_id === featureId) {
        selectedFlag.value = { ...selectedFlag.value, ...updatedFlag }
      }
      return updatedFlag
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to update feature flag'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Enable feature flag
   */
  async function enableFlag(featureId: string) {
    loading.value = true
    error.value = null

    try {
      const updatedFlag = await adminEnableFeature(featureId)
      const index = flags.value.findIndex((f) => f.feature_id === featureId)
      if (index !== -1) {
        flags.value[index] = updatedFlag
      }
      if (selectedFlag.value?.feature_id === featureId) {
        selectedFlag.value = updatedFlag
      }
      return updatedFlag
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to enable feature flag'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Disable feature flag
   */
  async function disableFlag(featureId: string, reason?: string) {
    loading.value = true
    error.value = null

    try {
      const updatedFlag = await adminDisableFeature(featureId, reason)
      const index = flags.value.findIndex((f) => f.feature_id === featureId)
      if (index !== -1) {
        flags.value[index] = updatedFlag
      }
      if (selectedFlag.value?.feature_id === featureId) {
        selectedFlag.value = updatedFlag
      }
      return updatedFlag
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to disable feature flag'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Toggle feature flag enable/disable status
   */
  async function toggleFlag(featureId: string, isEnabled: boolean, reason?: string) {
    return isEnabled ? enableFlag(featureId) : disableFlag(featureId, reason)
  }

  /**
   * Fetch rollout plans
   */
  async function fetchRolloutPlans(params?: {
    featureName?: string
    status?: string
    limit?: number
    offset?: number
  }) {
    loading.value = true
    error.value = null

    try {
      const response = await adminGetRolloutPlans(params)
      rolloutPlans.value = response.items
      return response
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to fetch rollout plans'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch single rollout plan
   */
  async function fetchRolloutPlan(planId: string) {
    loading.value = true
    error.value = null

    try {
      const plan = await adminGetRolloutPlan(planId)
      selectedRolloutPlan.value = plan
      return plan
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to fetch rollout plan'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create rollout plan
   */
  async function createRolloutPlan(data: {
    featureName: string
    description?: string
    targetPercentage?: number
    startDate?: string
    estimatedEndDate?: string
  }) {
    loading.value = true
    error.value = null

    try {
      const newPlan = await adminCreateRolloutPlan(data)
      rolloutPlans.value.push(newPlan)
      return newPlan
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to create rollout plan'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update rollout percentage
   */
  async function updateRolloutPercentage(planId: string, percentage: number) {
    loading.value = true
    error.value = null

    try {
      const updatedPlan = await adminUpdateRolloutPercentage(planId, percentage)
      const index = rolloutPlans.value.findIndex((p) => p.plan_id === planId)
      if (index !== -1) {
        rolloutPlans.value[index] = updatedPlan
      }
      if (selectedRolloutPlan.value?.plan_id === planId) {
        selectedRolloutPlan.value = updatedPlan
      }
      return updatedPlan
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message ||
        'Failed to update rollout percentage'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Pause rollout
   */
  async function pauseRollout(planId: string, reason?: string) {
    loading.value = true
    error.value = null

    try {
      const updatedPlan = await adminPauseRollout(planId, reason)
      const index = rolloutPlans.value.findIndex((p) => p.plan_id === planId)
      if (index !== -1) {
        rolloutPlans.value[index] = updatedPlan
      }
      if (selectedRolloutPlan.value?.plan_id === planId) {
        selectedRolloutPlan.value = updatedPlan
      }
      return updatedPlan
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to pause rollout'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Resume rollout
   */
  async function resumeRollout(planId: string) {
    loading.value = true
    error.value = null

    try {
      const updatedPlan = await adminResumeRollout(planId)
      const index = rolloutPlans.value.findIndex((p) => p.plan_id === planId)
      if (index !== -1) {
        rolloutPlans.value[index] = updatedPlan
      }
      if (selectedRolloutPlan.value?.plan_id === planId) {
        selectedRolloutPlan.value = updatedPlan
      }
      return updatedPlan
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to resume rollout'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Rollback feature (cancel rollout)
   */
  async function rollbackFeature(planId: string, reason?: string) {
    loading.value = true
    error.value = null

    try {
      const updatedPlan = await adminRollbackFeature(planId, reason)
      const index = rolloutPlans.value.findIndex((p) => p.plan_id === planId)
      if (index !== -1) {
        rolloutPlans.value[index] = updatedPlan
      }
      if (selectedRolloutPlan.value?.plan_id === planId) {
        selectedRolloutPlan.value = updatedPlan
      }
      return updatedPlan
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to rollback feature'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Get enabled features
   */
  async function getEnabledFeatures() {
    loading.value = true
    error.value = null

    try {
      return await adminGetEnabledFeatures()
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message || 'Failed to fetch enabled features'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Get features by category
   */
  async function getFeaturesByCategory(category: string) {
    loading.value = true
    error.value = null

    try {
      return await adminGetFeaturesByCategory(category)
    } catch (err: any) {
      error.value =
        err.response?.data?.error?.message ||
        'Failed to fetch features by category'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear error message
   */
  function clearError() {
    error.value = null
  }

  /**
   * Reset store state
   */
  function reset() {
    flags.value = []
    selectedFlag.value = null
    rolloutPlans.value = []
    selectedRolloutPlan.value = null
    loading.value = false
    error.value = null
    lastFetchedAt.value = null
  }

  return {
    // State
    flags,
    selectedFlag,
    rolloutPlans,
    selectedRolloutPlan,
    loading,
    error,
    lastFetchedAt,
    // Computed
    enabledFlags,
    disabledFlags,
    totalFlags,
    totalEnabledFlags,
    flagsByCategory,
    activeRollouts,
    // Actions
    fetchFlags,
    fetchFlag,
    createFlag,
    updateFlag,
    enableFlag,
    disableFlag,
    toggleFlag,
    fetchRolloutPlans,
    fetchRolloutPlan,
    createRolloutPlan,
    updateRolloutPercentage,
    pauseRollout,
    resumeRollout,
    rollbackFeature,
    getEnabledFeatures,
    getFeaturesByCategory,
    clearError,
    reset
  }
})
