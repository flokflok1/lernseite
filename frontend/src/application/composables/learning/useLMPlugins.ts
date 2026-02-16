/**
 * Composable for managing LM Plugins (Admin)
 *
 * Singleton pattern - state shared across all components.
 * Provides reactive state and actions for plugin management.
 */
import { ref, computed } from 'vue'
import { lmPluginsApi } from '@/application/services/api/panel-admin'
import type { LMPluginMetadata } from '@/types/plugins'

// Singleton state (shared across all components)
const plugins = ref<LMPluginMetadata[]>([])
const activePlugins = ref<LMPluginMetadata[]>([])
const pendingPlugins = ref<LMPluginMetadata[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

/**
 * Composable for LM Plugin management
 *
 * Usage:
 * ```ts
 * const { activePlugins, fetchActivePlugins, scanPlugins } = useLMPlugins()
 * await fetchActivePlugins()
 * ```
 */
export function useLMPlugins() {
  /**
   * Fetch active plugins from backend
   */
  async function fetchActivePlugins() {
    isLoading.value = true
    error.value = null

    try {
      const response = await lmPluginsApi.getActive()
      if (response.success && response.data) {
        activePlugins.value = response.data
      } else {
        error.value = response.error?.message || 'Failed to fetch active plugins'
      }
      return activePlugins.value
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch active plugins'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch pending plugins (waiting for approval)
   */
  async function fetchPendingPlugins() {
    isLoading.value = true
    error.value = null

    try {
      const response = await lmPluginsApi.getPending()
      if (response.success && response.data) {
        pendingPlugins.value = response.data
      } else {
        error.value = response.error?.message || 'Failed to fetch pending plugins'
      }
      return pendingPlugins.value
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch pending plugins'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Trigger plugin scan (discovers new plugins)
   */
  async function scanPlugins() {
    isLoading.value = true
    error.value = null

    try {
      const response = await lmPluginsApi.scan()
      if (response.success) {
        // Refresh pending plugins after scan
        await fetchPendingPlugins()
        return response.data
      } else {
        error.value = response.error?.message || 'Failed to scan plugins'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to scan plugins'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Approve a plugin
   */
  async function approvePlugin(pluginId: string) {
    try {
      const response = await lmPluginsApi.approve(pluginId)
      if (response.success) {
        // Refresh pending plugins
        await fetchPendingPlugins()
      } else {
        error.value = response.error?.message || 'Failed to approve plugin'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to approve plugin'
      throw err
    }
  }

  /**
   * Reject a plugin
   */
  async function rejectPlugin(pluginId: string, reason: string) {
    try {
      const response = await lmPluginsApi.reject(pluginId, reason)
      if (response.success) {
        // Refresh pending plugins
        await fetchPendingPlugins()
      } else {
        error.value = response.error?.message || 'Failed to reject plugin'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to reject plugin'
      throw err
    }
  }

  /**
   * Activate an approved plugin
   */
  async function activatePlugin(pluginId: string) {
    try {
      const response = await lmPluginsApi.activate(pluginId)
      if (response.success) {
        // Refresh both lists
        await fetchActivePlugins()
        await fetchPendingPlugins()
      } else {
        error.value = response.error?.message || 'Failed to activate plugin'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to activate plugin'
      throw err
    }
  }

  /**
   * Deactivate a plugin
   */
  async function deactivatePlugin(pluginId: string) {
    try {
      const response = await lmPluginsApi.deactivate(pluginId)
      if (response.success) {
        // Refresh active plugins
        await fetchActivePlugins()
      } else {
        error.value = response.error?.message || 'Failed to deactivate plugin'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to deactivate plugin'
      throw err
    }
  }

  /**
   * Get plugin detail by ID
   */
  async function getPluginDetail(pluginId: string): Promise<LMPluginMetadata | null> {
    isLoading.value = true
    error.value = null

    try {
      const response = await lmPluginsApi.getDetail(pluginId)
      if (response.success && response.data) {
        return response.data
      } else {
        error.value = response.error?.message || 'Plugin not found'
        return null
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch plugin detail'
      return null
    } finally {
      isLoading.value = false
    }
  }

  // Computed properties
  const pendingCount = computed(() => pendingPlugins.value.length)
  const activeCount = computed(() => activePlugins.value.length)
  const hasError = computed(() => error.value !== null)

  return {
    // State
    plugins,
    activePlugins,
    pendingPlugins,
    isLoading,
    error,

    // Computed
    pendingCount,
    activeCount,
    hasError,

    // Actions
    fetchActivePlugins,
    fetchPendingPlugins,
    scanPlugins,
    approvePlugin,
    rejectPlugin,
    activatePlugin,
    deactivatePlugin,
    getPluginDetail
  }
}
