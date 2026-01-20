/**
 * Feature Flags Composable
 * ==================================
 * Provides reactive access to feature flags with caching and subscriptions.
 */

import { computed, onMounted } from 'vue'
import { useFeatureFlagsStore } from '@/application/stores/modules/admin/feature-flags.store'
import type { FeatureFlag } from '@/infrastructure/api/clients/admin'

export interface UseFeatureFlagsOptions {
  /**
   * Auto-load flags on mount
   * @default true
   */
  autoLoad?: boolean

  /**
   * Cache duration in milliseconds
   * @default 5 * 60 * 1000 (5 minutes)
   */
  cacheDuration?: number
}

/**
 * Composable for feature flag management and checking
 *
 * @param options Configuration options
 * @returns Feature flag utilities and state
 *
 * @example
 * ```typescript
 * const { isEnabled, hasFlag, refresh, loading } = useFeatureFlags()
 *
 * if (isEnabled('whiteboard_engine')) {
 *   // Show whiteboard UI
 * }
 * ```
 */
export function useFeatureFlags(options: UseFeatureFlagsOptions = {}) {
  const store = useFeatureFlagsStore()
  const { autoLoad = true, cacheDuration = 5 * 60 * 1000 } = options

  /**
   * Check if feature flag is enabled by feature code
   *
   * @param featureCode Feature code to check (e.g., 'whiteboard_engine')
   * @param defaultValue Value if feature not found (default: false)
   * @returns true if feature is enabled, false otherwise
   *
   * @example
   * ```typescript
   * if (isEnabled('social_network')) {
   *   // Feature is enabled
   * }
   * ```
   */
  function isEnabled(featureCode: string, defaultValue: boolean = false): boolean {
    const flag = store.flags.find((f) => f.feature_code === featureCode)

    if (!flag) {
      console.warn(`Feature flag "${featureCode}" not found, returning default: ${defaultValue}`)
      return defaultValue
    }

    return flag.is_enabled
  }

  /**
   * Check if feature flag exists
   *
   * @param featureCode Feature code to check
   * @returns true if flag exists, false otherwise
   */
  function hasFlag(featureCode: string): boolean {
    return store.flags.some((f) => f.feature_code === featureCode)
  }

  /**
   * Get feature flag object by code
   *
   * @param featureCode Feature code to retrieve
   * @returns Feature flag object or undefined
   */
  function getFlag(featureCode: string): FeatureFlag | undefined {
    return store.flags.find((f) => f.feature_code === featureCode)
  }

  /**
   * Get rollout percentage for feature (for UI visualization)
   *
   * @param featureCode Feature code to check
   * @returns Rollout percentage (0-100) or 0 if not found
   */
  function getRolloutPercentage(featureCode: string): number {
    const flag = getFlag(featureCode)
    return flag?.rollout_percentage ?? 0
  }

  /**
   * Check if current user is in rollout (deterministic based on user ID)
   *
   * @param featureCode Feature code to check
   * @param userId User ID for deterministic hashing
   * @returns true if user is in rollout, false otherwise
   *
   * @example
   * ```typescript
   * const { isInRollout } = useFeatureFlags()
   * const inRollout = isInRollout('new_dashboard', userId)
   * ```
   */
  function isInRollout(featureCode: string, userId: string): boolean {
    const flag = getFlag(featureCode)

    if (!flag || !flag.is_enabled) {
      return false
    }

    if (flag.rollout_percentage === 100) {
      return true
    }

    if (flag.rollout_percentage === 0) {
      return false
    }

    // Deterministic hashing: same user always gets same result
    // Formula: hash(userId + featureCode) % 100 < rollout_percentage
    let hash = 0
    const combined = userId + featureCode

    for (let i = 0; i < combined.length; i++) {
      hash = ((hash << 5) - hash) + combined.charCodeAt(i)
      hash = hash & hash // Convert to 32-bit integer
    }

    const normalized = ((hash >>> 0) % 100) / 100 // Ensure positive value between 0-1
    return normalized < flag.rollout_percentage / 100
  }

  /**
   * Refresh feature flags from server
   *
   * @param force Force refresh even if cached (default: false)
   * @returns Promise that resolves when flags are loaded
   */
  async function refresh(force: boolean = false): Promise<void> {
    // Check cache
    if (!force && store.lastFetchedAt) {
      const age = Date.now() - store.lastFetchedAt
      if (age < cacheDuration) {
        return // Cache still valid
      }
    }

    await store.fetchFlags()
  }

  /**
   * Subscribe to feature flag changes
   *
   * @param featureCode Feature code to watch
   * @param callback Called when flag state changes
   * @returns Unsubscribe function
   *
   * @example
   * ```typescript
   * const unsubscribe = subscribe('new_dashboard', (isEnabled) => {
   *   console.log('New dashboard is now:', isEnabled ? 'enabled' : 'disabled')
   * })
   *
   * // Later, unsubscribe from updates
   * unsubscribe()
   * ```
   */
  function subscribe(
    featureCode: string,
    callback: (isEnabled: boolean) => void
  ): () => void {
    // Send initial value
    callback(isEnabled(featureCode))

    // Create a watcher for changes
    let previousValue = isEnabled(featureCode)

    const interval = setInterval(() => {
      const currentValue = isEnabled(featureCode)
      if (currentValue !== previousValue) {
        previousValue = currentValue
        callback(currentValue)
      }
    }, 1000) // Check every second

    // Return unsubscribe function
    return () => clearInterval(interval)
  }

  /**
   * Wait for a feature flag to become available (for testing/setup)
   *
   * @param featureCode Feature code to wait for
   * @param timeout Max time to wait in milliseconds (default: 30000)
   * @returns Promise that resolves when flag is loaded
   * @throws Error if timeout exceeded
   */
  async function waitForFlags(timeout: number = 30000): Promise<void> {
    const startTime = Date.now()

    while (store.flags.length === 0) {
      if (Date.now() - startTime > timeout) {
        throw new Error('Timeout waiting for feature flags to load')
      }

      await refresh()
      await new Promise((resolve) => setTimeout(resolve, 100))
    }
  }

  /**
   * Get all enabled features as array of codes
   *
   * @returns Array of feature codes that are enabled
   */
  function getAllEnabled(): string[] {
    return store.enabledFlags.map((f) => f.feature_code)
  }

  /**
   * Get features by category
   *
   * @param category Category to filter by
   * @returns Array of features in category
   */
  function getByCategory(category: string): FeatureFlag[] {
    return store.flagsByCategory[category] || []
  }

  /**
   * Computed: Are flags currently loading
   */
  const loading = computed(() => store.loading)

  /**
   * Computed: Total number of flags
   */
  const totalFlags = computed(() => store.totalFlags)

  /**
   * Computed: Number of enabled flags
   */
  const totalEnabledFlags = computed(() => store.totalEnabledFlags)

  /**
   * Computed: All enabled feature codes
   */
  const enabledFeatureCodes = computed(() => getAllEnabled())

  // Auto-load on mount if enabled
  onMounted(async () => {
    if (autoLoad) {
      try {
        await refresh()
      } catch (error) {
        console.error('Failed to load feature flags:', error)
      }
    }
  })

  return {
    // Reactive state
    flags: computed(() => store.flags),
    loading,
    error: computed(() => store.error),
    totalFlags,
    totalEnabledFlags,
    enabledFeatureCodes,

    // Flag checking functions
    isEnabled,
    hasFlag,
    getFlag,
    getRolloutPercentage,
    isInRollout,

    // Feature retrieval
    getByCategory,
    getAllEnabled,

    // Lifecycle functions
    refresh,
    waitForFlags,
    subscribe
  }
}
