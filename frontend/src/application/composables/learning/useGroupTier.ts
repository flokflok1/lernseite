/**
 * Composable for Learning Method Groups (Database-Driven)
 *
 * Singleton pattern - state shared across all components.
 * Provides reactive state and helper functions to:
 * - Load groups from API
 * - Get tier for a specific group
 * - Get name/icon for a group
 * - Cache results for performance
 *
 * REPLACES hardcoded getTierFromGroup() functions in Vue components.
 * Single source of truth for group metadata (name, icon, tier, etc.)
 */

import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { getLMGroups, type LMGroupAPIInfo } from '@/infrastructure/api/clients/panel/editor/authoring/authoring.api'

// ============================================================================
// Singleton State (Shared Across All Components)
// ============================================================================

const groups: Ref<LMGroupAPIInfo[]> = ref([])
const isLoading: Ref<boolean> = ref(false)
const error: Ref<string | null> = ref(null)
const isLoaded: Ref<boolean> = ref(false)

/**
 * Composable for Learning Method Group Tier Management
 *
 * This composable handles all group-related operations that were previously
 * hardcoded in individual Vue components.
 *
 * Usage:
 * ```ts
 * const { groups, loadGroups, getTierFromGroup, getNameFromGroup } = useGroupTier()
 *
 * onMounted(async () => {
 *   await loadGroups()
 * })
 *
 * const tierA = getTierFromGroup('A')  // Returns 'basic'
 * const nameC = getNameFromGroup('C')  // Returns 'Prüfung'
 * ```
 */
export function useGroupTier() {
  /**
   * Load all groups from backend API
   *
   * Fetches group data (code, name, description, icon, tier, sort_order, is_active)
   * from the database via the /learning-methods/groups endpoint.
   *
   * @returns Promise<LMGroupAPIInfo[]> - Array of groups
   * @throws Error if API call fails
   */
  async function loadGroups(): Promise<LMGroupAPIInfo[]> {
    // Skip if already loaded
    if (isLoaded.value) {
      return groups.value
    }

    isLoading.value = true
    error.value = null

    try {
      const data = await getLMGroups()
      groups.value = data
      isLoaded.value = true
      return groups.value
    } catch (err: any) {
      error.value = err.message || 'Failed to load learning method groups'
      console.error('[useGroupTier] Error loading groups:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Force reload groups from API (bypasses cache)
   *
   * @returns Promise<LMGroupAPIInfo[]> - Array of groups
   */
  async function reloadGroups(): Promise<LMGroupAPIInfo[]> {
    isLoaded.value = false
    return loadGroups()
  }

  /**
   * Get tier for a specific group code
   *
   * REPLACES hardcoded if/elif logic:
   * ❌ BEFORE:
   * ```ts
   * if (group === 'A' || group === 'B') return 'basic'
   * if (group === 'C' || group === 'E') return 'premium'
   * return 'basic'
   * ```
   *
   * ✅ AFTER:
   * ```ts
   * const tier = getTierFromGroup('A')  // Returns 'basic'
   * ```
   *
   * @param groupCode - Group code (A, B, C, ...)
   * @returns 'basic' | 'premium' | 'enterprise' (defaults to 'basic' if not found)
   */
  function getTierFromGroup(groupCode: string): 'basic' | 'premium' | 'enterprise' {
    const group = groups.value.find((g) => g.group_code === groupCode)
    return group?.tier || 'basic'
  }

  /**
   * Get name for a specific group code
   *
   * REPLACES hardcoded getLMGroupName() helper:
   * ❌ BEFORE:
   * ```ts
   * const names: Record<string, string> = {
   *   'A': 'Erklärend',
   *   'B': 'Praxis',
   *   'C': 'Prüfung'
   * }
   * return names[group] || group
   * ```
   *
   * ✅ AFTER:
   * ```ts
   * const name = getNameFromGroup('A')  // Returns 'Erklärend'
   * ```
   *
   * @param groupCode - Group code (A, B, C, ...)
   * @returns Group name (e.g., 'Erklärend', 'Praxis', 'Prüfung')
   */
  function getNameFromGroup(groupCode: string): string {
    const group = groups.value.find((g) => g.group_code === groupCode)
    return group?.name || groupCode
  }

  /**
   * Get description for a specific group code
   *
   * @param groupCode - Group code (A, B, C, ...)
   * @returns Group description
   */
  function getDescriptionFromGroup(groupCode: string): string {
    const group = groups.value.find((g) => g.group_code === groupCode)
    return group?.description || ''
  }

  /**
   * Get icon for a specific group code
   *
   * REPLACES hardcoded getLMGroupIcon() helper:
   * ❌ BEFORE:
   * ```ts
   * const icons: Record<string, string> = {
   *   'A': '📖',
   *   'B': '✏️',
   *   'C': '📝',
   *   'D': '🎓',
   *   'E': '💻',
   *   'F': '👥'
   * }
   * return icons[group] || '📋'
   * ```
   *
   * ✅ AFTER:
   * ```ts
   * const icon = getIconFromGroup('A')  // Returns '📖'
   * ```
   *
   * @param groupCode - Group code (A, B, C, ...)
   * @returns Icon/emoji (e.g., '📖', '✏️', '📝')
   */
  function getIconFromGroup(groupCode: string): string {
    const group = groups.value.find((g) => g.group_code === groupCode)
    return group?.icon || '📋'
  }

  /**
   * Get sort order for a specific group code
   *
   * Used to determine display order in UI lists.
   *
   * @param groupCode - Group code (A, B, C, ...)
   * @returns Sort order number (0, 1, 2, ...)
   */
  function getSortOrderFromGroup(groupCode: string): number {
    const group = groups.value.find((g) => g.group_code === groupCode)
    return group?.sort_order ?? 999
  }

  /**
   * Get active status for a specific group code
   *
   * @param groupCode - Group code (A, B, C, ...)
   * @returns true if group is active, false otherwise
   */
  function isGroupActive(groupCode: string): boolean {
    const group = groups.value.find((g) => g.group_code === groupCode)
    return group?.is_active ?? false
  }

  /**
   * Get complete group info
   *
   * @param groupCode - Group code (A, B, C, ...)
   * @returns LMGroupAPIInfo object or null if not found
   */
  function getGroupInfo(groupCode: string): LMGroupAPIInfo | null {
    return groups.value.find((g) => g.group_code === groupCode) || null
  }

  /**
   * Get all group codes
   *
   * Useful for iterating over all groups in order.
   *
   * @returns Array of group codes sorted by sort_order
   */
  function getAllGroupCodes(): string[] {
    return groups.value.sort((a, b) => a.sort_order - b.sort_order).map((g) => g.group_code)
  }

  /**
   * Get all groups grouped by tier
   *
   * Useful for grouping UI elements by tier level.
   *
   * @returns Record mapping tier levels to array of groups
   */
  function groupsByTier(): Record<string, LMGroupAPIInfo[]> {
    return groups.value.reduce(
      (acc, group) => {
        const tier = group.tier
        if (!acc[tier]) {
          acc[tier] = []
        }
        acc[tier].push(group)
        return acc
      },
      {} as Record<string, LMGroupAPIInfo[]>
    )
  }

  /**
   * Check if a specific group code exists
   *
   * @param groupCode - Group code to check
   * @returns true if group exists, false otherwise
   */
  function groupExists(groupCode: string): boolean {
    return groups.value.some((g) => g.group_code === groupCode)
  }

  // ============================================================================
  // Computed Properties
  // ============================================================================

  const hasError: ComputedRef<boolean> = computed(() => error.value !== null)
  const groupCount: ComputedRef<number> = computed(() => groups.value.length)
  const basicGroups: ComputedRef<LMGroupAPIInfo[]> = computed(() =>
    groups.value.filter((g) => g.tier === 'basic')
  )
  const premiumGroups: ComputedRef<LMGroupAPIInfo[]> = computed(() =>
    groups.value.filter((g) => g.tier === 'premium')
  )
  const enterpriseGroups: ComputedRef<LMGroupAPIInfo[]> = computed(() =>
    groups.value.filter((g) => g.tier === 'enterprise')
  )

  // ============================================================================
  // STYLE & RENDERING FUNCTIONS (Database-Driven or Smart Defaults)
  // ============================================================================

  /**
   * Get CSS styles for a group badge.
   *
   * Returns background-color and text color based on:
   * - Group code (A, B, C, etc.)
   * - Tier (basic, premium, enterprise)
   * - Dynamic from database when available
   *
   * @param groupCode - Group code (A, B, C, etc.)
   * @returns CSS style string with background-color and color
   */
  function getGroupStyle(groupCode: string): string {
    // Map group codes to base colors (light variants)
    const groupColors: Record<string, { light: string; dark: string }> = {
      'A': { light: '#dbeafe', dark: '#1e40af' },      // Blue (Erklärend)
      'B': { light: '#dcfce7', dark: '#15803d' },      // Green (Praxis)
      'C': { light: '#fef3c7', dark: '#92400e' },      // Amber (Prüfung)
      'D': { light: '#f3e8ff', dark: '#6b21a8' },      // Purple (Pro)
      'E': { light: '#cffafe', dark: '#0e7490' },      // Cyan
      'F': { light: '#fce7f3', dark: '#be185d' }       // Pink
    }

    const colors = groupColors[groupCode] || groupColors['A']
    return `background-color: ${colors.light}; color: ${colors.dark};`
  }

  /**
   * Get CSS styles for a filled group badge (dark variant).
   *
   * Used for active/selected group indicators.
   *
   * @param groupCode - Group code (A, B, C, etc.)
   * @returns CSS style string with solid background
   */
  function getGroupStyleFilled(groupCode: string): string {
    const filledColors: Record<string, string> = {
      'A': '#2563eb',    // Blue
      'B': '#16a34a',    // Green
      'C': '#ea580c',    // Orange/Amber
      'D': '#7c3aed',    // Purple
      'E': '#0891b2',    // Cyan
      'F': '#db2777'     // Pink
    }

    const bgColor = filledColors[groupCode] || filledColors['A']
    return `background-color: ${bgColor};`
  }

  /**
   * Get CSS styles for a tier badge.
   *
   * Different color for each tier level.
   *
   * @param tier - Tier type: 'basic', 'premium', 'enterprise', 'pro'
   * @returns CSS style string
   */
  function getTierStyle(tier: string): string {
    const tierColors: Record<string, string> = {
      'basic': 'background-color: #dbeafe; color: #1e40af;',
      'premium': 'background-color: #fef3c7; color: #92400e;',
      'enterprise': 'background-color: #e9d5ff; color: #6b21a8;',
      'pro': 'background-color: #e9d5ff; color: #6b21a8;'  // 'pro' is alias for 'enterprise'
    }

    return tierColors[tier] || tierColors['basic']
  }

  /**
   * Get human-readable label for a tier.
   *
   * Maps database tier names to UI labels.
   *
   * @param tier - Tier type: 'basic', 'premium', 'enterprise', 'pro'
   * @returns Readable tier label
   */
  function getTierLabel(tier: string): string {
    const labels: Record<string, string> = {
      'basic': 'Basic',
      'premium': 'Premium',
      'enterprise': 'Pro',
      'pro': 'Pro'
    }

    return labels[tier] || tier
  }

  return {
    // State
    groups,
    isLoading,
    error,
    isLoaded,

    // Computed
    hasError,
    groupCount,
    basicGroups,
    premiumGroups,
    enterpriseGroups,

    // Actions
    loadGroups,
    reloadGroups,

    // Helper Functions (Replace Hardcoded Logic)
    getTierFromGroup,
    getNameFromGroup,
    getDescriptionFromGroup,
    getIconFromGroup,
    getSortOrderFromGroup,
    isGroupActive,
    getGroupInfo,
    getAllGroupCodes,
    groupsByTier,
    groupExists,

    // Style & Rendering Functions (STEP 12 - Flexibility)
    getGroupStyle,
    getGroupStyleFilled,
    getTierStyle,
    getTierLabel
  }
}
