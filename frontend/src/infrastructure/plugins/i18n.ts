/**
 * Vue i18n Plugin Configuration
 * ==============================
 *
 * HYBRID TRANSLATION SYSTEM:
 * 1. JSON files (src/locales/) = Fallback/Default
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
import { initializeSchemaI18n } from '@/application/composables/i18n/useSchemaI18n'

// =============================================================================
// Import locale modules (organized by language/domain in infrastructure layer)
// =============================================================================

// German (de)
import deCommon from '@/infrastructure/i18n/locales/de/common'
import deErrors from '@/infrastructure/i18n/locales/de/errors'
import deDashboard from '@/infrastructure/i18n/locales/de/dashboard'
import deSetup from '@/infrastructure/i18n/locales/de/setup'
import deTutor from '@/infrastructure/i18n/locales/de/tutor'
import deLegal from '@/infrastructure/i18n/locales/de/legal'

import dePanel from '@/infrastructure/i18n/locales/de/panel'
import deAiEditor from '@/infrastructure/i18n/locales/de/panel/aiEditor'
import deCourses from '@/infrastructure/i18n/locales/de/courses'
import deFeatures from '@/infrastructure/i18n/locales/de/features'
import deSystemFeatures from '@/infrastructure/i18n/locales/de/systemFeatures'

// English (en)
import enCommon from '@/infrastructure/i18n/locales/en/common'
import enErrors from '@/infrastructure/i18n/locales/en/errors'
import enDashboard from '@/infrastructure/i18n/locales/en/dashboard'
import enSetup from '@/infrastructure/i18n/locales/en/setup'
import enTutor from '@/infrastructure/i18n/locales/en/tutor'
import enLegal from '@/infrastructure/i18n/locales/en/legal'

import enPanel from '@/infrastructure/i18n/locales/en/panel'
import enAiEditor from '@/infrastructure/i18n/locales/en/panel/aiEditor'
import enCourses from '@/infrastructure/i18n/locales/en/courses'
import enFeatures from '@/infrastructure/i18n/locales/en/features'
import enSystemFeatures from '@/infrastructure/i18n/locales/en/systemFeatures'

// Polish (pl)
import plCommon from '@/infrastructure/i18n/locales/pl/common'
import plErrors from '@/infrastructure/i18n/locales/pl/errors'
import plDashboard from '@/infrastructure/i18n/locales/pl/dashboard'
import plSetup from '@/infrastructure/i18n/locales/pl/setup'
import plTutor from '@/infrastructure/i18n/locales/pl/tutor'
import plLegal from '@/infrastructure/i18n/locales/pl/legal'

import plPanel from '@/infrastructure/i18n/locales/pl/panel'
import plAiEditor from '@/infrastructure/i18n/locales/pl/panel/aiEditor'
import plCourses from '@/infrastructure/i18n/locales/pl/courses'
import plFeatures from '@/infrastructure/i18n/locales/pl/features'
import plSystemFeatures from '@/infrastructure/i18n/locales/pl/systemFeatures'

// Merge all modules into single language objects
const de = {
  ...deCommon,
  ...deErrors,
  ...deDashboard,
  ...deSetup,
  ...deTutor,
  ...deLegal,
  ...dePanel,
  ...deAiEditor,
  ...deCourses,
  ...deFeatures,
  ...deSystemFeatures
}

const en = {
  ...enCommon,
  ...enErrors,
  ...enDashboard,
  ...enSetup,
  ...enTutor,
  ...enLegal,
  ...enPanel,
  ...enAiEditor,
  ...enCourses,
  ...enFeatures,
  ...enSystemFeatures
}

const pl = {
  ...plCommon,
  ...plErrors,
  ...plDashboard,
  ...plSetup,
  ...plTutor,
  ...plLegal,
  ...plPanel,
  ...plAiEditor,
  ...plCourses,
  ...plFeatures,
  ...plSystemFeatures
}

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
        const { getBundle } = await import('@/infrastructure/api/clients/public/i18n.api')

        // Load German (base language) from API and merge with file translations
        try {
          const deBundle = await getBundle('de')
          if (deBundle && Object.keys(deBundle).length > 0) {
            const currentDe = i18n.global.getLocaleMessage('de')
            i18n.global.setLocaleMessage('de', { ...currentDe, ...deBundle })
            console.log('[i18n] Merged German API bundle with file translations')
          }
        } catch (_e) {
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
          } catch (_e) {
            // Silently fall back to file translations
          }
        }
      } catch (_error) {
        // API not available, using file-based translations only
      }
    } else {
      console.log('[i18n] System not installed - using file-based translations only')
    }

    // Set locale
    i18n.global.locale.value = savedLang
    document.documentElement.lang = savedLang

    console.log('[i18n] Initialized with locale:', savedLang)

    // Initialize schema i18n resolver (for SchemaFormComponent)
    try {
      // Pass the I18n instance (not .global property)
      initializeSchemaI18n(i18n)
      console.log('[i18n] Schema resolver initialized')
    } catch (error) {
      console.error('[i18n] Schema resolver initialization failed:', error)
      // Continue anyway - component will use fallbacks
    }
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
      const { getBundle } = await import('@/infrastructure/api/clients/public/i18n.api')
      const bundle = await getBundle(lang)
      if (bundle && Object.keys(bundle).length > 0) {
        i18n.global.setLocaleMessage(lang, bundle)
      }
    }
  } catch (_e) {
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
