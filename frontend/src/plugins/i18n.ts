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

// Import locale files (available at startup, no API needed)
import de from '@/locales/de.json'
import pl from '@/locales/pl.json'
import en from '@/locales/en.json'

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
    // Import API dynamically to avoid circular dependencies
    const { getBundle } = await import('@/api/i18n.api')
    const savedLang = localStorage.getItem('lsx-language') || 'de'

    // Load German (base language) from API and merge with file translations
    try {
      const deBundle = await getBundle('de')
      if (deBundle && Object.keys(deBundle).length > 0) {
        const currentDe = i18n.global.getLocaleMessage('de')
        i18n.global.setLocaleMessage('de', { ...currentDe, ...deBundle })
      }
    } catch (e) {
      console.warn('[i18n] Failed to load German bundle from API, using file translations')
    }

    // Load user's preferred language if different from German
    if (savedLang !== 'de') {
      try {
        const bundle = await getBundle(savedLang)
        if (bundle && Object.keys(bundle).length > 0) {
          const currentLang = i18n.global.getLocaleMessage(savedLang)
          i18n.global.setLocaleMessage(savedLang, { ...currentLang, ...bundle })
        }
      } catch (e) {
        console.warn(`[i18n] Failed to load ${savedLang} bundle from API`)
      }
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
