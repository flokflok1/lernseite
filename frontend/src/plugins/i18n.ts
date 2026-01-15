/**
 * Vue i18n Plugin Configuration
 * ==============================
 *
 * HYBRID TRANSLATION SYSTEM:
 * 1. JSON files (src/locales/*.json) = Fallback/Default
 * 2. Database (via API) = Primary source after setup
 *
 * SYNC FLOW:
 * - Fresh Install: JSON files loaded immediately (no DB yet)
 * - After Setup: JSON → DB sync runs automatically (SetupFinishStep)
 * - Normal Operation: DB translations merged on top of JSON (DB wins)
 * - B2B Export: Admin can export DB → JSON files for deployments
 *
 * Primary Languages: DE (primary) → PL → EN
 * Fallback: Always German (de)
 */

import { createI18n } from 'vue-i18n'
import type { App } from 'vue'

// =============================================================================
// Import split locale files (organized by feature domain)
// =============================================================================

// German (de)
import deCommon from '@/locales/de/common.json'
import deAdmin from '@/locales/de/admin'
import deWindowsAdmin from '@/locales/de/windows/admin.json'
import deWindowsAiEditor from '@/locales/de/windows/aiEditor.json'
import deWindowsAiPricing from '@/locales/de/windows/aiPricing.json'
import deWindowsCommon from '@/locales/de/windows/common.json'
import deWindowsViewer from '@/locales/de/windows/viewer.json'
import deWindowsLearningMethods from '@/locales/de/windows/learningMethods.json'
import deCourses from '@/locales/de/courses.json'
import deDashboard from '@/locales/de/dashboard.json'
import deSetup from '@/locales/de/setup.json'
import deLegal from '@/locales/de/legal.json'

// English (en)
import enCommon from '@/locales/en/common.json'
import enAdmin from '@/locales/en/admin'
import enWindowsAdmin from '@/locales/en/windows/admin.json'
import enWindowsAiEditor from '@/locales/en/windows/aiEditor.json'
import enWindowsAiPricing from '@/locales/en/windows/aiPricing.json'
import enWindowsCommon from '@/locales/en/windows/common.json'
import enWindowsViewer from '@/locales/en/windows/viewer.json'
import enWindowsLearningMethods from '@/locales/en/windows/learningMethods.json'
import enCourses from '@/locales/en/courses.json'
import enDashboard from '@/locales/en/dashboard.json'
import enSetup from '@/locales/en/setup.json'
import enLegal from '@/locales/en/legal.json'

// Polish (pl)
import plCommon from '@/locales/pl/common.json'
import plAdmin from '@/locales/pl/admin'
import plWindowsAdmin from '@/locales/pl/windows/admin.json'
import plWindowsAiEditor from '@/locales/pl/windows/aiEditor.json'
import plWindowsAiPricing from '@/locales/pl/windows/aiPricing.json'
import plWindowsCommon from '@/locales/pl/windows/common.json'
import plWindowsViewer from '@/locales/pl/windows/viewer.json'
import plWindowsLearningMethods from '@/locales/pl/windows/learningMethods.json'
import plCourses from '@/locales/pl/courses.json'
import plDashboard from '@/locales/pl/dashboard.json'
import plSetup from '@/locales/pl/setup.json'
import plLegal from '@/locales/pl/legal.json'

// Merge window modules
const deWindows = {
  windows: {
    ...deWindowsAdmin,
    ...deWindowsAiEditor,
    ...deWindowsAiPricing,
    ...deWindowsCommon,
    ...deWindowsViewer,
    learningMethods: deWindowsLearningMethods
  }
}

const enWindows = {
  windows: {
    ...enWindowsAdmin,
    ...enWindowsAiEditor,
    ...enWindowsAiPricing,
    ...enWindowsCommon,
    ...enWindowsViewer,
    learningMethods: enWindowsLearningMethods
  }
}

const plWindows = {
  windows: {
    ...plWindowsAdmin,
    ...plWindowsAiEditor,
    ...plWindowsAiPricing,
    ...plWindowsCommon,
    ...plWindowsViewer,
    learningMethods: plWindowsLearningMethods
  }
}

// Merge all modules into single language objects
const de = { ...deCommon, ...deAdmin, ...deWindows, ...deCourses, ...deDashboard, ...deSetup, ...deLegal }
const en = { ...enCommon, ...enAdmin, ...enWindows, ...enCourses, ...enDashboard, ...enSetup, ...enLegal }
const pl = { ...plCommon, ...plAdmin, ...plWindows, ...plCourses, ...plDashboard, ...plSetup, ...plLegal }

// Type for nested message objects
type MessageValue = string | { [key: string]: MessageValue }
type Messages = { [key: string]: MessageValue }

/**
 * Flatten nested object to dot-notation keys
 * { nav: { home: "Home" } } => { "nav.home": "Home" }
 */
function flattenMessages(obj: Messages, prefix = ''): Record<string, string> {
  const result: Record<string, string> = {}

  for (const key in obj) {
    const value = obj[key]
    const newKey = prefix ? `${prefix}.${key}` : key

    if (typeof value === 'string') {
      result[newKey] = value
    } else if (typeof value === 'object' && value !== null) {
      Object.assign(result, flattenMessages(value as Messages, newKey))
    }
  }

  return result
}

// Flatten messages for vue-i18n (supports both nested and dot notation access)
const messages = {
  de: flattenMessages(de as Messages),
  pl: flattenMessages(pl as Messages),
  en: flattenMessages(en as Messages)
}

// Create i18n instance
export const i18n = createI18n({
  legacy: false, // Use Composition API
  globalInjection: true, // Enable $t in templates
  locale: localStorage.getItem('lsx-language') || 'de',
  fallbackLocale: 'de',
  messages,
  missingWarn: false, // Don't warn about missing translations in console
  fallbackWarn: false,
  silentTranslationWarn: true
})

/**
 * Install i18n plugin
 */
export function setupI18n(app: App): void {
  app.use(i18n)

  // Set HTML lang attribute
  const savedLang = localStorage.getItem('lsx-language') || 'de'
  document.documentElement.lang = savedLang
}

/**
 * Initialize i18n - loads additional translations from API
 * This merges API translations with file-based ones (API takes precedence)
 */
export async function initializeI18n(): Promise<void> {
  try {
    const savedLang = localStorage.getItem('lsx-language') || 'de'

    // Check if system is installed (has setup_completed flag)
    const isInstalled = localStorage.getItem('lsx-setup-completed') === 'true'

    // Only try to load from API if system is installed
    if (isInstalled) {
      try {
        // Import API dynamically to avoid circular dependencies
        const { getBundle } = await import('@/api/i18n.api')

        // Load German (base language) from API and merge with file translations
        try {
          const deBundle = await getBundle('de')
          if (deBundle && Object.keys(deBundle).length > 0) {
            const currentDe = i18n.global.getLocaleMessage('de')
            i18n.global.setLocaleMessage('de', { ...currentDe, ...deBundle })
            console.log('[i18n] Merged German API bundle with file translations')
          }
        } catch (e) {
          // Silently fall back to file translations (expected during setup)
        }

        // Load user's preferred language if different from German
        if (savedLang !== 'de') {
          try {
            const bundle = await getBundle(savedLang)
            if (bundle && Object.keys(bundle).length > 0) {
              const currentLang = i18n.global.getLocaleMessage(savedLang)
              i18n.global.setLocaleMessage(savedLang, { ...currentLang, ...bundle })
              console.log(`[i18n] Merged ${savedLang} API bundle with file translations`)
            }
          } catch (e) {
            // Silently fall back to file translations
          }
        }
      } catch (error) {
        // API not available, using file-based translations only
      }
    } else {
      console.log('[i18n] System not installed - using file-based translations only')
    }

    // Set locale
    i18n.global.locale.value = savedLang
    document.documentElement.lang = savedLang

    console.log('[i18n] Initialized with locale:', savedLang)
  } catch (error) {
    console.error('[i18n] Initialization failed:', error)
    // Keep using file-based translations
  }
}

/**
 * Change language dynamically
 */
export async function setLanguage(lang: string): Promise<void> {
  try {
    // If we don't have this language in memory yet, try loading from API
    const currentMessages = i18n.global.getLocaleMessage(lang)
    if (!currentMessages || Object.keys(currentMessages).length === 0) {
      const { getBundle } = await import('@/api/i18n.api')
      const bundle = await getBundle(lang)
      if (bundle && Object.keys(bundle).length > 0) {
        i18n.global.setLocaleMessage(lang, bundle)
      }
    }
  } catch (e) {
    console.warn(`[i18n] Could not load ${lang} from API`)
  }

  // Set locale regardless
  i18n.global.locale.value = lang
  localStorage.setItem('lsx-language', lang)
  document.documentElement.lang = lang
}

/**
 * Get current locale
 */
export function getCurrentLocale(): string {
  return i18n.global.locale.value
}

/**
 * Check if a translation key exists
 */
export function hasTranslation(key: string): boolean {
  return i18n.global.te(key)
}

export default i18n
