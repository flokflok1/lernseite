/**
 * LernsystemX Frontend - Application Entry Point
 * Phase B24 - Theme Support with async initialization
 * Phase i18n - Internationalization support
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import { useThemeStore } from './store/theme.store'
import { setupI18n, initializeI18n } from './plugins/i18n'

// ============================================================================
// Async App Initialization
// ============================================================================

;(async () => {
  try {
    // 1. Create Vue app instance
    const app = createApp(App)

    // 2. Initialize Pinia (must be installed before using stores)
    const pinia = createPinia()
    app.use(pinia)

    // 3. Initialize Theme Store
    // Auth store auto-initializes via restoreSession() in its setup
    // Theme must be initialized explicitly to load from API and apply before mount
    const themeStore = useThemeStore()
    await themeStore.initTheme()

    console.log('[Main] Theme initialized, effective theme:', themeStore.effectiveTheme)

    // 4. Initialize i18n (Internationalization)
    setupI18n(app)
    await initializeI18n()

    console.log('[Main] i18n initialized')

    // 5. Install router
    app.use(router)

    // 6. Mount app (theme and i18n are already applied)
    app.mount('#app')

    console.log('[Main] App mounted successfully')

  } catch (error) {
    console.error('[Main] App initialization failed:', error)

    // Fallback: Mount app anyway with default dark theme
    // Theme store will have already applied 'dark' fallback on error
    try {
      const app = createApp(App)
      app.use(createPinia())
      setupI18n(app)
      app.use(router)
      app.mount('#app')

      console.warn('[Main] App mounted with fallback after initialization error')
    } catch (fallbackError) {
      console.error('[Main] Critical: Fallback mount failed:', fallbackError)
      // Show critical error to user
      document.body.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif;">
          <div style="text-align: center; padding: 2rem;">
            <h1 style="color: #ef4444; margin-bottom: 1rem;">App-Initialisierung fehlgeschlagen</h1>
            <p style="color: #6b7280;">Bitte laden Sie die Seite neu oder kontaktieren Sie den Support.</p>
            <button onclick="location.reload()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #4f46e5; color: white; border: none; border-radius: 0.5rem; cursor: pointer;">
              Seite neu laden
            </button>
          </div>
        </div>
      `
    }
  }
})()
