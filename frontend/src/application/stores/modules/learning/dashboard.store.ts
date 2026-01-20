/**
 * LernsystemX - Dashboard Store (Pinia)
 *
 * Manages:
 * - Dashboard layout configuration
 * - Widget instances and visibility
 * - LocalStorage persistence
 * - Future backend API integration
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from '../core'
import type { DashboardLayout, DashboardWidgetInstance } from '@/domain/widgets'
import { WIDGET_DEFINITIONS, getWidgetsForRole } from '@/config/widgetRegistry'

const STORAGE_KEY = 'lsx_dashboard_layout'
const LAYOUT_VERSION = 1

export const useDashboardStore = defineStore('dashboard', () => {
  const authStore = useAuthStore()

  // ============================================================================
  // State
  // ============================================================================

  const layout = ref<DashboardLayout | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ============================================================================
  // Getters
  // ============================================================================

  /**
   * Get widgets that are visible for the current user
   */
  const visibleWidgets = computed(() => {
    if (!layout.value) return []
    return layout.value.widgets
      .filter(w => w.visible)
      .sort((a, b) => a.order - b.order)
  })

  /**
   * Get all widgets available for the current user (based on role)
   */
  const availableWidgets = computed(() => {
    const role = authStore.userRole
    const isPremium = authStore.isPremium

    return getWidgetsForRole(role, isPremium)
  })

  /**
   * Check if user can customize widgets (Premium+)
   */
  const canCustomizeWidgets = computed(() => {
    return authStore.isPremium ||
           authStore.isCreator ||
           authStore.isTeacher ||
           authStore.isOrgAdmin ||
           authStore.userRole === 'admin'
  })

  /**
   * Get layout status
   */
  const hasLayout = computed(() => !!layout.value)

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Initialize default layout for user based on role
   */
  const initDefaultLayoutForUser = (role: string, userId: number): DashboardLayout => {
    const isPremium = ['premium', 'creator', 'teacher', 'school_admin', 'company_admin', 'admin'].includes(role)
    const availableWidgetDefs = getWidgetsForRole(role, isPremium)

    const widgets: DashboardWidgetInstance[] = availableWidgetDefs.map(def => ({
      instanceId: `${userId}-${def.id}`,
      widgetId: def.id,
      order: def.defaultOrder || 99,
      visible: def.defaultVisible !== false,
      config: {}
    }))

    return {
      userId,
      role,
      widgets,
      version: LAYOUT_VERSION,
      updatedAt: new Date().toISOString()
    }
  }

  /**
   * Load layout from LocalStorage or create default
   */
  const loadLayout = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const userId = authStore.user?.user_id
      const role = authStore.userRole

      if (!userId) {
        throw new Error('User not authenticated')
      }

      // Try to load from localStorage
      const stored = localStorage.getItem(STORAGE_KEY)

      if (stored) {
        try {
          const parsed: DashboardLayout = JSON.parse(stored)

          // Validate that layout belongs to current user
          if (parsed.userId === userId) {
            // Check if layout version is compatible
            if (!parsed.version || parsed.version < LAYOUT_VERSION) {
              console.warn('Layout version outdated, creating new default layout')
              layout.value = initDefaultLayoutForUser(role, userId)
            } else {
              layout.value = parsed
            }
          } else {
            // Layout is for different user, create new
            layout.value = initDefaultLayoutForUser(role, userId)
          }
        } catch (parseError) {
          console.error('Failed to parse stored layout:', parseError)
          layout.value = initDefaultLayoutForUser(role, userId)
        }
      } else {
        // No stored layout, create default
        layout.value = initDefaultLayoutForUser(role, userId)
      }

      // Save to localStorage
      await saveLayout()

    } catch (err: any) {
      error.value = err.message || 'Failed to load dashboard layout'
      console.error('Dashboard layout load error:', err)

      // Fallback: Create default layout
      if (authStore.user?.user_id) {
        layout.value = initDefaultLayoutForUser(authStore.userRole, authStore.user.user_id)
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * Save layout to LocalStorage (and prepare for backend API)
   */
  const saveLayout = async (): Promise<void> => {
    if (!layout.value) {
      console.warn('No layout to save')
      return
    }

    try {
      // Update timestamp
      layout.value.updatedAt = new Date().toISOString()

      // Save to localStorage
      localStorage.setItem(STORAGE_KEY, JSON.stringify(layout.value))

      // TODO: Backend API integration
      // await dashboardApi.saveDashboardLayout(layout.value)

    } catch (err: any) {
      error.value = err.message || 'Failed to save dashboard layout'
      console.error('Dashboard layout save error:', err)
      throw err
    }
  }

  /**
   * Toggle widget visibility
   */
  const toggleWidgetVisibility = async (instanceId: string): Promise<void> => {
    if (!layout.value) return
    if (!canCustomizeWidgets.value) {
      error.value = 'Widget-Anpassung nur für Premium-Nutzer verfügbar'
      return
    }

    const widget = layout.value.widgets.find(w => w.instanceId === instanceId)
    if (widget) {
      widget.visible = !widget.visible
      await saveLayout()
    }
  }

  /**
   * Reorder widgets
   */
  const reorderWidgets = async (newOrder: string[]): Promise<void> => {
    if (!layout.value) return
    if (!canCustomizeWidgets.value) {
      error.value = 'Widget-Anpassung nur für Premium-Nutzer verfügbar'
      return
    }

    // Update order based on array index
    layout.value.widgets.forEach(widget => {
      const index = newOrder.indexOf(widget.instanceId)
      if (index !== -1) {
        widget.order = index
      }
    })

    await saveLayout()
  }

  /**
   * Reset layout to default
   */
  const resetToDefault = async (): Promise<void> => {
    if (!authStore.user?.user_id) return

    layout.value = initDefaultLayoutForUser(authStore.userRole, authStore.user.user_id)
    await saveLayout()
  }

  /**
   * Update widget configuration
   */
  const updateWidgetConfig = async (instanceId: string, config: Record<string, any>): Promise<void> => {
    if (!layout.value) return
    if (!canCustomizeWidgets.value) {
      error.value = 'Widget-Anpassung nur für Premium-Nutzer verfügbar'
      return
    }

    const widget = layout.value.widgets.find(w => w.instanceId === instanceId)
    if (widget) {
      widget.config = { ...widget.config, ...config }
      await saveLayout()
    }
  }

  /**
   * Clear layout (logout)
   */
  const clearLayout = (): void => {
    layout.value = null
    error.value = null
  }

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State
    layout,
    loading,
    error,

    // Getters
    visibleWidgets,
    availableWidgets,
    canCustomizeWidgets,
    hasLayout,

    // Actions
    loadLayout,
    saveLayout,
    toggleWidgetVisibility,
    reorderWidgets,
    resetToDefault,
    updateWidgetConfig,
    clearLayout,
    initDefaultLayoutForUser
  }
})
