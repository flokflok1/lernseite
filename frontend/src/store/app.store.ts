/**
 * LernsystemX - Application Store (Pinia)
 *
 * Global application state:
 * - Installation status
 * - System readiness
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as setupApi from '@/api/setup.api'

export const useAppStore = defineStore('app', () => {
  // State
  const installed = ref<boolean | null>(null) // null = not checked yet
  const setupRequired = ref(false)
  const version = ref<string | null>(null)
  const isCheckingStatus = ref(false)

  // Actions

  /**
   * Check installation status
   */
  const checkInstallationStatus = async (): Promise<void> => {
    isCheckingStatus.value = true

    try {
      const response = await setupApi.getSetupStatus()

      installed.value = response.installed
      setupRequired.value = response.requires_setup
      version.value = response.version

    } catch (error) {
      console.error('Failed to check installation status:', error)
      // Assume not installed if check fails
      installed.value = false
      setupRequired.value = true
    } finally {
      isCheckingStatus.value = false
    }
  }

  /**
   * Mark installation as complete
   */
  const markAsInstalled = (): void => {
    installed.value = true
    setupRequired.value = false
  }

  return {
    // State
    installed,
    setupRequired,
    version,
    isCheckingStatus,

    // Actions
    checkInstallationStatus,
    markAsInstalled,
  }
})
