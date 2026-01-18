/**
 * useSystemMode Composable
 *
 * Manages system mode state and operations.
 * Shared across all system settings components.
 */

import { ref, computed } from 'vue'
import * as systemApi from '@/api/admin/system-settings.api'
import type { SystemStatus } from '@/api/admin/system-settings.api'

// Shared state (singleton pattern)
const systemStatus = ref<SystemStatus | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

export function useSystemMode() {
  // ============================================================================
  // Computed Properties
  // ============================================================================

  const currentMode = computed(
    () => systemStatus.value?.environment || 'development'
  )

  const maintenanceMode = computed(
    () => systemStatus.value?.maintenance_mode || false
  )

  const debugEnabled = computed(
    () => systemStatus.value?.debug_enabled || false
  )

  const uptime = computed(() => {
    if (!systemStatus.value) return '0h 0m'

    const seconds = systemStatus.value.uptime_seconds
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  })

  const isProduction = computed(() => currentMode.value === 'production')

  const isDevelopment = computed(() => currentMode.value === 'development')

  // ============================================================================
  // Methods
  // ============================================================================

  async function refreshStatus() {
    loading.value = true
    error.value = null

    try {
      systemStatus.value = await systemApi.getSystemStatus()
    } catch (e: any) {
      error.value = e.response?.data?.error || e.message || 'Failed to load system status'
      console.error('Failed to refresh system status:', e)
    } finally {
      loading.value = false
    }
  }

  async function switchEnvironment(mode: 'development' | 'production'): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await systemApi.switchSystemMode({ mode })

      if (response.success) {
        // Refresh status to get new state
        await refreshStatus()
        return true
      } else {
        error.value = 'Failed to switch environment'
        return false
      }
    } catch (e: any) {
      error.value = e.response?.data?.error || e.message || 'Failed to switch environment'
      console.error('Failed to switch environment:', e)
      return false
    } finally {
      loading.value = false
    }
  }

  async function toggleMaintenanceMode(
    enabled: boolean,
    message?: string
  ): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await systemApi.toggleMaintenanceMode({ enabled, message })

      if (response.success) {
        // Refresh status to get new state
        await refreshStatus()
        return true
      } else {
        error.value = 'Failed to toggle maintenance mode'
        return false
      }
    } catch (e: any) {
      error.value = e.response?.data?.error || e.message || 'Failed to toggle maintenance mode'
      console.error('Failed to toggle maintenance mode:', e)
      return false
    } finally {
      loading.value = false
    }
  }

  // ============================================================================
  // Exports
  // ============================================================================

  return {
    // State
    systemStatus,
    loading,
    error,

    // Computed
    currentMode,
    maintenanceMode,
    debugEnabled,
    uptime,
    isProduction,
    isDevelopment,

    // Methods
    refreshStatus,
    switchEnvironment,
    toggleMaintenanceMode
  }
}
