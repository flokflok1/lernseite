/**
 * LernsystemX - Application Store (Pinia)
 *
 * Global application state:
 * - Installation status
 * - System readiness
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as setupApi from '@/application/services/api/system'

export const useAppStore = defineStore('app', () => {
  // State
  const installed = ref<boolean | null>(null) // null = not checked yet
  const setupRequired = ref(false)
  const version = ref<string | null>(null)
  const isCheckingStatus = ref(false)

  // Actions

  /**
   * Check static installation marker file
   *
   * This checks if the static .lsx-installed file exists in public/
   * Works even when backend is down!
   * Allows new users and private mode users to detect installation status.
   */
  const checkStaticMarker = async (): Promise<boolean> => {
    try {
      // Fetch static marker file from public/ directory
      // This works even when backend API is completely down
      const response = await fetch('/.lsx-installed')

      if (response.ok) {
        const data = await response.json()

        if (data.installed === true) {
          // Setup was completed! Set localStorage for future checks
          localStorage.setItem('lsx-setup-completed', 'true')
          console.log('[App Store] Static marker found - setup was previously completed')
          return true
        }
      }
    } catch (error) {
      // Static file doesn't exist or fetch failed - this is OK
      // It just means setup was never completed
      console.log('[App Store] No static marker found (setup not completed yet)')
    }

    return false
  }

  /**
   * Check installation status
   */
  const checkInstallationStatus = async (): Promise<void> => {
    isCheckingStatus.value = true

    // FIRST: Check static marker file (works even when backend is down)
    // This allows new users and private mode to detect installation status
    await checkStaticMarker()

    try {
      const response = await setupApi.getSetupStatus()

      installed.value = response.installed
      setupRequired.value = response.requires_setup
      version.value = response.version

      // Persist to localStorage so i18n system knows setup is complete
      if (response.installed) {
        localStorage.setItem('lsx-setup-completed', 'true')
      }

    } catch (error) {
      console.error('Failed to check installation status:', error)

      // Check localStorage to determine if setup was previously completed
      // Note: localStorage may have been set by checkStaticMarker() above!
      const setupCompleted = localStorage.getItem('lsx-setup-completed') === 'true'

      if (setupCompleted) {
        // Setup was completed before - backend is just down temporarily
        // Keep installed=true and setupRequired=false so user can access login
        installed.value = true
        setupRequired.value = false
        console.warn('[App Store] Backend unreachable, but setup was previously completed')
      } else {
        // Setup was never completed - assume not installed
        installed.value = false
        setupRequired.value = true
      }

      // NEVER remove localStorage - it's our persistent source of truth!
      // Only remove it when explicitly resetting the system, not on API failures
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
    localStorage.setItem('lsx-setup-completed', 'true')
  }

  /**
   * Reset setup state (for debugging)
   * Clears all localStorage and resets state to uninstalled
   */
  const resetSetup = (): void => {
    console.log('[App Store] Resetting setup state...')

    // Clear all setup-related localStorage
    localStorage.removeItem('lsx-setup-completed')
    localStorage.removeItem('lsx-setup-status')
    sessionStorage.removeItem('lsx-setup-completed')
    sessionStorage.removeItem('lsx-setup-status')

    // Reset state
    installed.value = false
    setupRequired.value = true
    version.value = null

    console.log('[App Store] ✅ Setup reset complete - localStorage cleared')
    console.log('[App Store] State:', {
      installed: installed.value,
      setupRequired: setupRequired.value,
      version: version.value
    })
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
    resetSetup,
  }
})
