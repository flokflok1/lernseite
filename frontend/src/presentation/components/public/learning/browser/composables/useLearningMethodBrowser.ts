/**
 * useLearningMethodBrowser Composable
 *
 * Manages learning methods browser UI state and interactions.
 * Handles filtering, searching, and displaying available methods.
 *
 * Features:
 * - Filter by group (A/B/C)
 * - Filter by tier
 * - Search by name
 * - Sort options
 * - Pagination
 *
 * Uses useAccessibleMethods for tier-based filtering
 */

import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGroupTier } from '@/application/composables/learning/useGroupTier'
import { useAccessibleMethods } from '@/application/composables/learning/useAccessibleMethods'
import type { LearningMethodType } from '@/infrastructure/api/clients/panel/admin'

export interface BrowserFilters {
  groupCode?: string
  searchQuery?: string
  sortBy?: 'newest' | 'popular' | 'name'
}

export interface BrowserMethod {
  methodType: LearningMethodType
  groupName: string
  groupIcon: string
  tier: string
  isAccessible: boolean
}

/**
 * Composable for learning methods browser
 *
 * Usage:
 * ```ts
 * const {
 *   filteredMethods,
 *   filters,
 *   setGroupFilter,
 *   setSearchQuery,
 *   availableGroups
 * } = useLearningMethodBrowser()
 * ```
 */
export function useLearningMethodBrowser() {
  const { t: _t } = useI18n()
  const groupTier = useGroupTier()
  const { accessibleMethods, userTier: _userTier } = useAccessibleMethods()

  // Filters state
  const filters = ref<BrowserFilters>({
    groupCode: undefined,
    searchQuery: '',
    sortBy: 'newest'
  })

  // Pagination
  const currentPage = ref(1)
  const itemsPerPage = ref(12)

  /**
   * All available groups that user can access
   */
  const availableGroups = computed(() => {
    return groupTier.getAllGroupCodes().map(code => ({
      code,
      name: groupTier.getNameFromGroup(code) || code,
      icon: groupTier.getIconFromGroup(code) || '📋',
      description: groupTier.getDescriptionFromGroup(code) || '',
      tier: groupTier.getTierFromGroup(code)
    }))
  })

  /**
   * Methods filtered by current filters
   */
  const filteredMethods = computed((): BrowserMethod[] => {
    let results = accessibleMethods.value.map(item => ({
      methodType: item.methodType,
      groupName: groupTier.getNameFromGroup(item.methodType.group) || item.methodType.group,
      groupIcon: groupTier.getIconFromGroup(item.methodType.group) || '📋',
      tier: item.tier,
      isAccessible: item.isAccessible
    }))

    // Filter by group
    if (filters.value.groupCode) {
      results = results.filter(m => m.methodType.group === filters.value.groupCode)
    }

    // Filter by search query
    if (filters.value.searchQuery) {
      const query = filters.value.searchQuery.toLowerCase()
      results = results.filter(m =>
        m.methodType.name.toLowerCase().includes(query) ||
        m.methodType.description?.toLowerCase().includes(query)
      )
    }

    // Sort
    switch (filters.value.sortBy) {
      case 'name':
        results.sort((a, b) => a.methodType.name.localeCompare(b.methodType.name))
        break
      case 'popular':
        // If we had popularity metrics, sort by them
        // For now, sort by access order
        results.sort((a, b) => b.methodType.lm_id - a.methodType.lm_id)
        break
      case 'newest':
      default:
        // Keep original order (database order)
        break
    }

    return results
  })

  /**
   * Paginated results
   */
  const paginatedMethods = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredMethods.value.slice(start, end)
  })

  /**
   * Total pages
   */
  const totalPages = computed(() => {
    return Math.ceil(filteredMethods.value.length / itemsPerPage.value)
  })

  /**
   * Methods grouped by group code
   */
  const methodsByGroup = computed(() => {
    const grouped: Record<string, BrowserMethod[]> = {}

    filteredMethods.value.forEach(method => {
      const groupCode = method.methodType.group
      if (!grouped[groupCode]) {
        grouped[groupCode] = []
      }
      grouped[groupCode].push(method)
    })

    return grouped
  })

  /**
   * Get stats about filtered methods
   */
  const stats = computed(() => ({
    total: filteredMethods.value.length,
    accessible: filteredMethods.value.filter(m => m.isAccessible).length,
    locked: filteredMethods.value.filter(m => !m.isAccessible).length,
    byGroup: Object.entries(methodsByGroup.value).reduce(
      (acc, [group, methods]) => ({
        ...acc,
        [group]: methods.length
      }),
      {} as Record<string, number>
    )
  }))

  /**
   * Set group filter
   *
   * @param groupCode - Group code or undefined to clear
   */
  const setGroupFilter = (groupCode: string | undefined) => {
    filters.value.groupCode = groupCode
    currentPage.value = 1 // Reset pagination
  }

  /**
   * Set search query
   *
   * @param query - Search query
   */
  const setSearchQuery = (query: string) => {
    filters.value.searchQuery = query
    currentPage.value = 1 // Reset pagination
  }

  /**
   * Set sort order
   *
   * @param sortBy - Sort option
   */
  const setSortBy = (sortBy: 'newest' | 'popular' | 'name') => {
    filters.value.sortBy = sortBy
  }

  /**
   * Go to specific page
   *
   * @param page - Page number
   */
  const goToPage = (page: number) => {
    currentPage.value = Math.max(1, Math.min(page, totalPages.value))
  }

  /**
   * Reset all filters
   */
  const resetFilters = () => {
    filters.value = {
      groupCode: undefined,
      searchQuery: '',
      sortBy: 'newest'
    }
    currentPage.value = 1
  }

  /**
   * Get recommended methods for user
   *
   * Returns methods user just got access to or should start with
   */
  const getRecommendedMethods = (limit: number = 3): BrowserMethod[] => {
    return filteredMethods.value
      .filter(m => m.isAccessible)
      .slice(0, limit)
  }

  return {
    // State
    filters,
    currentPage,
    itemsPerPage,
    availableGroups,

    // Computed
    filteredMethods,
    paginatedMethods,
    totalPages,
    methodsByGroup,
    stats,

    // Methods
    setGroupFilter,
    setSearchQuery,
    setSortBy,
    goToPage,
    resetFilters,
    getRecommendedMethods
  }
}
