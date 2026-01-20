/**
 * LernsystemX - Theme Store (Pinia)
 *
 * Global theme management with dark/light/system modes.
 * Integrates with Backend API /profile/theme
 * Phase B24 - Theme Support
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as profileApi from '@/api/profile.api'
import { useAuthStore } from '../core'

export type ThemePreference = 'system' | 'light' | 'dark'
export type EffectiveTheme = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
  // ============================================================================
  // State
  // ============================================================================

  /**
   * User's theme preference from backend
   * 'system' = follow OS, 'light' = force light, 'dark' = force dark
   */
  const themePreference = ref<ThemePreference>('dark')

  /**
   * System theme detected from OS
   */
  const systemTheme = ref<EffectiveTheme>('dark')

  /**
   * Effective theme currently applied (result of preference + system)
   */
  const effectiveTheme = ref<EffectiveTheme>('dark')

  /**
   * Whether theme has been initialized
   */
  const isReady = ref(false)

  /**
   * Whether theme is currently being updated
   */
  const isUpdating = ref(false)

  /**
   * MediaQuery for system theme detection
   */
  const mediaQuery = ref<MediaQueryList | null>(null)

  /**
   * System theme change listener
   */
  const systemListener = ref<((event: MediaQueryListEvent) => void) | null>(null)

  /**
   * Debounce timer for system theme changes
   */
  let systemThemeDebounceTimer: number | null = null

  /**
   * Last applied system theme to prevent unnecessary updates
   */
  let lastAppliedSystemTheme: EffectiveTheme | null = null

  /**
   * Timestamp when theme preference was last changed (to ignore spurious events)
   */
  let lastPreferenceChangeTime: number = 0

  // ============================================================================
  // Getters
  // ============================================================================

  /**
   * Whether dark mode is currently active
   */
  const isDarkMode = computed(() => effectiveTheme.value === 'dark')

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Fetch theme preference from backend API
   */
  const fetchBackendThemePreference = async (): Promise<ThemePreference | null> => {
    const authStore = useAuthStore()

    if (!authStore.isAuthenticated) {
      return null
    }

    try {
      const response = await profileApi.getThemePreference()
      return response.theme
    } catch (error) {
      console.warn('[Theme] Failed to load preference from API:', error)
      return null
    }
  }

  /**
   * Refresh system theme by querying OS (without listener setup)
   */
  const refreshSystemTheme = (): void => {
    if (typeof window === 'undefined') return
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    console.log('[Theme] MediaQuery DEBUG - matches:', mq.matches, 'media:', mq.media)
    systemTheme.value = mq.matches ? 'dark' : 'light'
    console.log('[Theme] Refreshed system theme from OS:', systemTheme.value)
  }

  /**
   * Detect system theme from OS using matchMedia
   */
  const detectSystemTheme = (): void => {
    // MediaQuery für OS-Theme
    const mq = window.matchMedia('(prefers-color-scheme: dark)')

    // Initialen Wert setzen
    const systemIsDark = mq.matches
    console.log('[Theme] detectSystemTheme() - mq.matches:', mq.matches, 'media:', mq.media)
    systemTheme.value = systemIsDark ? 'dark' : 'light'

    // Listener entfernen falls schon vorhanden
    if (mediaQuery.value && systemListener.value) {
      mediaQuery.value.removeEventListener('change', systemListener.value)
    }

    // Neuen Listener definieren mit Debounce
    const listener = (event: MediaQueryListEvent) => {
      console.log('[Theme] OS theme changed:', event.matches ? 'dark' : 'light')

      // Ignore events within 500ms of preference change (spurious Windows events)
      const timeSinceChange = Date.now() - lastPreferenceChangeTime
      if (timeSinceChange < 500) {
        console.log('[Theme] Ignoring spurious event (within 500ms of preference change)')
        return
      }

      // Debounce: Clear previous timer
      if (systemThemeDebounceTimer !== null) {
        clearTimeout(systemThemeDebounceTimer)
      }

      // Set new timer (150ms delay to handle Windows double-firing)
      systemThemeDebounceTimer = window.setTimeout(() => {
        systemTheme.value = event.matches ? 'dark' : 'light'

        // Only apply if theme actually changed (prevents Windows double-firing)
        if (themePreference.value === 'system' && lastAppliedSystemTheme !== systemTheme.value) {
          console.log('[Theme] Applying system theme (debounced):', systemTheme.value)
          effectiveTheme.value = systemTheme.value
          applyTheme()
          lastAppliedSystemTheme = systemTheme.value
        } else if (lastAppliedSystemTheme === systemTheme.value) {
          console.log('[Theme] Skipping redundant theme application:', systemTheme.value)
        }

        systemThemeDebounceTimer = null
      }, 150)
    }

    // Speichern und registrieren
    mediaQuery.value = mq
    systemListener.value = listener
    mq.addEventListener('change', listener)

    console.log('[Theme] System theme detection initialized. Current:', systemTheme.value)
  }

  /**
   * Calculate effective theme based on preference and system theme
   */
  const calculateEffectiveTheme = (): EffectiveTheme => {
    if (themePreference.value === 'system') {
      return systemTheme.value
    }
    return themePreference.value as EffectiveTheme
  }

  /**
   * Apply theme to DOM (add/remove 'dark' class on <html>)
   */
  const applyTheme = (): void => {
    if (typeof window === 'undefined') return

    const html = document.documentElement

    if (effectiveTheme.value === 'dark') {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }

    // Optional: set data attribute for debugging/CSS
    html.dataset.theme = effectiveTheme.value

    console.log('[Theme] Applied to DOM:', effectiveTheme.value, '| HTML has dark class:', html.classList.contains('dark'))
  }

  /**
   * Initialize theme system
   * - Detect system theme
   * - Load user preference from API (if logged in)
   * - Apply theme to DOM
   * - Setup system theme listener
   */
  const initTheme = async (): Promise<void> => {
    isReady.value = false

    try {
      // Backend-Wert abfragen
      const backendValue = await fetchBackendThemePreference()
      themePreference.value = backendValue ?? 'dark'
    } catch (e) {
      themePreference.value = 'dark'
    }

    // Immer zuerst System-Theme erkennen
    detectSystemTheme()

    // effectiveTheme korrekt bestimmen
    if (themePreference.value === 'system') {
      effectiveTheme.value = systemTheme.value
    } else {
      effectiveTheme.value = themePreference.value as EffectiveTheme
    }

    // Theme anwenden
    applyTheme()

    // Initialize last applied theme tracker
    lastAppliedSystemTheme = effectiveTheme.value

    isReady.value = true
  }

  /**
   * Set theme preference (with API sync)
   * @param theme - New theme preference
   */
  const setThemePreference = async (theme: ThemePreference): Promise<void> => {
    // Store old value for rollback on error
    const oldPreference = themePreference.value
    const oldEffective = effectiveTheme.value

    try {
      isUpdating.value = true

      // 1. Record preference change time to ignore spurious events
      lastPreferenceChangeTime = Date.now()

      // 2. Optimistically update local state
      themePreference.value = theme

      // 3. If switching to 'system', refresh OS theme to prevent stale values
      if (theme === 'system') {
        refreshSystemTheme()
      }

      // 4. Recalculate effective theme
      effectiveTheme.value = calculateEffectiveTheme()

      // 5. Apply to DOM immediately
      applyTheme()

      // 6. Update last applied theme tracker
      lastAppliedSystemTheme = effectiveTheme.value

      // 7. Sync with backend (if logged in)
      const authStore = useAuthStore()

      if (authStore.isAuthenticated) {
        try {
          await profileApi.updateThemePreference({ theme })

          console.log('[Theme] Updated preference:', theme)
        } catch (error) {
          console.error('[Theme] Failed to update preference in backend:', error)

          // Rollback on API error
          themePreference.value = oldPreference
          effectiveTheme.value = oldEffective
          applyTheme()

          throw error // Re-throw for caller to handle
        }
      }

    } finally {
      isUpdating.value = false
    }
  }

  // ============================================================================
  // Return Store
  // ============================================================================

  return {
    // State
    themePreference,
    systemTheme,
    effectiveTheme,
    isReady,
    isUpdating,

    // Getters
    isDarkMode,

    // Actions
    initTheme,
    setThemePreference,
  }
})
