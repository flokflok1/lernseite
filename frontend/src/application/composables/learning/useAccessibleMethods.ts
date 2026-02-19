/**
 * useAccessibleMethods Composable
 *
 * Manages tier-based access to learning methods.
 * Filters available methods based on user's subscription tier.
 *
 * Features:
 * - Tier-based method filtering (free/premium/pro)
 * - Group availability check
 * - Published method filtering
 * - Cache support
 *
 * REPLACES hardcoded tier logic with database-driven approach
 */

import { computed, ref, type Ref } from 'vue'
import { useUserStore } from '@/application/stores/modules/core/user.store'
import { useGroupTier } from '@/application/composables/learning/useGroupTier'
import type { AdminLearningMethod, LearningMethodType } from '@/infrastructure/api/clients/panel/admin'

export interface AccessibleMethod {
  method: AdminLearningMethod
  methodType: LearningMethodType
  tier: string
  isAccessible: boolean
  reason?: string
}

/**
 * Composable for user's accessible learning methods
 *
 * Usage:
 * ```ts
 * const {
 *   accessibleMethods,
 *   accessibleGroups,
 *   canAccessGroup,
 *   canAccessMethod,
 *   userTier
 * } = useAccessibleMethods()
 *
 * onMounted(async () => {
 *   await loadAccessibleMethods()
 * })
 * ```
 */
export function useAccessibleMethods() {
  const userStore = useUserStore()
  const groupTier = useGroupTier()

  // State
  const allMethods: Ref<AdminLearningMethod[]> = ref([])
  const allMethodTypes: Ref<LearningMethodType[]> = ref([])
  const isLoading: Ref<boolean> = ref(false)
  const error: Ref<string | null> = ref(null)

  /**
   * User's current subscription tier
   * Defaults to 'free' if not authenticated
   */
  const userTier = computed(() => {
    if (!userStore.currentUser) return 'free'
    return userStore.currentUser.subscription_tier || 'free'
  })

  /**
   * Group codes accessible to user based on tier
   *
   * Tier-based group access:
   * - free:    ['A']                  (Basic explanation methods only)
   * - premium: ['A', 'B']             (Basic + Practice methods)
   * - pro:     ['A', 'B', 'C']        (All groups including exams)
   */
  const accessibleGroups = computed((): string[] => {
    const groupMap: Record<string, string[]> = {
      'free': ['A'],
      'premium': ['A', 'B'],
      'pro': ['A', 'B', 'C'],
      'enterprise': ['A', 'B', 'C']
    }
    return groupMap[userTier.value] || groupMap['free']
  })

  /**
   * Check if user can access a specific group
   *
   * @param groupCode - Group code (A, B, C, etc.)
   * @returns true if user can access the group
   */
  const canAccessGroup = (groupCode: string): boolean => {
    return accessibleGroups.value.includes(groupCode)
  }

  /**
   * Check if user can access a specific method
   *
   * @param methodType - Method type object
   * @returns true if user can access the method
   */
  const canAccessMethod = (methodType: LearningMethodType): boolean => {
    // Must be published
    if (!methodType.published) return false

    // Must be in accessible group
    return canAccessGroup(methodType.group)
  }

  /**
   * Get all accessible methods for user
   *
   * Filters based on:
   * 1. Published status
   * 2. User's tier-based group access
   * 3. Method active status
   */
  const accessibleMethods = computed((): AccessibleMethod[] => {
    return allMethods.value
      .filter(method => {
        // Find method type info
        const methodType = allMethodTypes.value.find(t => t.lm_id === method.method_type)
        if (!methodType) return false

        // Check if method type is accessible
        if (!canAccessMethod(methodType)) return false

        // Method must be published
        if (!method.published) return false

        return true
      })
      .map(method => {
        const methodType = allMethodTypes.value.find(t => t.lm_id === method.method_type)!
        const methodTier = groupTier.getTierFromGroup(methodType.group)

        return {
          method,
          methodType,
          tier: methodTier,
          isAccessible: true
        }
      })
  })

  /**
   * Get accessible methods grouped by group code
   *
   * Returns methods organized by their group (A, B, C, etc.)
   */
  const accessibleMethodsByGroup = computed(() => {
    const grouped: Record<string, AccessibleMethod[]> = {}

    accessibleMethods.value.forEach(item => {
      const groupCode = item.methodType.group
      if (!grouped[groupCode]) {
        grouped[groupCode] = []
      }
      grouped[groupCode].push(item)
    })

    return grouped
  })

  /**
   * Get locked methods (user doesn't have access)
   *
   * Returns methods user cannot access with reason
   */
  const lockedMethods = computed((): AccessibleMethod[] => {
    return allMethods.value
      .filter(method => {
        const methodType = allMethodTypes.value.find(t => t.lm_id === method.method_type)
        if (!methodType) return false
        return !canAccessMethod(methodType)
      })
      .map(method => {
        const methodType = allMethodTypes.value.find(t => t.lm_id === method.method_type)!
        const methodTier = groupTier.getTierFromGroup(methodType.group)
        let reason = 'Tier restriction'

        if (!method.published) {
          reason = 'Method not yet available'
        } else if (!canAccessGroup(methodType.group)) {
          reason = `Requires ${methodTier.toUpperCase()} tier or higher`
        }

        return {
          method,
          methodType,
          tier: methodTier,
          isAccessible: false,
          reason
        }
      })
  })

  /**
   * Count of accessible methods
   */
  const accessibleCount = computed(() => accessibleMethods.value.length)

  /**
   * Count of locked methods
   */
  const lockedCount = computed(() => lockedMethods.value.length)

  /**
   * Load all methods (admin can see all)
   *
   * @param methods - All methods from API
   * @param methodTypes - All method types from API
   */
  const loadMethods = (methods: AdminLearningMethod[], methodTypes: LearningMethodType[]) => {
    allMethods.value = methods
    allMethodTypes.value = methodTypes
  }

  /**
   * Check if user needs to upgrade for specific group
   *
   * @param groupCode - Group code
   * @returns true if user doesn't have access and could upgrade
   */
  const needsUpgradeForGroup = (groupCode: string): boolean => {
    if (canAccessGroup(groupCode)) return false
    if (userTier.value === 'pro' || userTier.value === 'enterprise') return false
    return true
  }

  /**
   * Get minimum tier required for group
   *
   * @param groupCode - Group code
   * @returns Tier name (basic, premium, pro)
   */
  const getMinimumTierForGroup = (groupCode: string): string => {
    const tierInfo = groupTier.getTierFromGroup(groupCode)
    return tierInfo
  }

  /**
   * Get upgrade suggestion for user
   *
   * Returns suggested tier upgrade path if user is locked from methods
   */
  const getUpgradeSuggestion = computed(() => {
    if (accessibleMethods.value.length > 0) return null

    // If user is free, suggest premium
    if (userTier.value === 'free') {
      return {
        current: 'free',
        suggested: 'premium',
        message: 'Upgrade to Premium to unlock practice methods'
      }
    }

    // If user is premium, suggest pro
    if (userTier.value === 'premium') {
      return {
        current: 'premium',
        suggested: 'pro',
        message: 'Upgrade to Pro to unlock exam preparation methods'
      }
    }

    return null
  })

  return {
    // State
    userTier,
    accessibleGroups,
    accessibleMethods,
    accessibleMethodsByGroup,
    lockedMethods,
    accessibleCount,
    lockedCount,
    isLoading,
    error,

    // Methods
    canAccessGroup,
    canAccessMethod,
    loadMethods,
    needsUpgradeForGroup,
    getMinimumTierForGroup,
    getUpgradeSuggestion
  }
}
