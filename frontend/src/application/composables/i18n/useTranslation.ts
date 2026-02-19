/**
 * useTranslation Composable
 * =========================
 * Composable for loading and using translations from the API.
 * Integrates with vue-i18n and provides caching.
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { getBundle, getLanguages, type LanguageProgress } from '@/infrastructure/api/clients/public'

// Cache for loaded bundles
const bundleCache = new Map<string, Record<string, string>>()
const languagesCache = ref<LanguageProgress[] | null>(null)
const currentLanguage = ref<string>(localStorage.getItem('lsx-language') || 'de')
const isLoading = ref(false)
const loadError = ref<string | null>(null)


/**
 * Main translation composable
 */
export function useTranslation() {
  const { t, locale, mergeLocaleMessage, availableLocales } = useI18n()

  /**
   * Load translations for a language from API
   */
  async function loadLanguage(lang: string, namespace?: string): Promise<void> {
    const cacheKey = `${lang}:${namespace || 'all'}`

    // Check cache first
    if (bundleCache.has(cacheKey)) {
      const cached = bundleCache.get(cacheKey)!
      // Merge with existing messages (file-based translations)
      mergeLocaleMessage(lang, cached)
      return
    }

    // Check if system is installed
    const isInstalled = localStorage.getItem('lsx-setup-completed') === 'true'

    // If not installed, file-based translations are already loaded, no API needed
    if (!isInstalled) {
      console.log(`[i18n] Using file-based translations for ${lang} (system not installed)`)
      return
    }

    isLoading.value = true
    loadError.value = null

    try {
      const bundle = await getBundle(lang, namespace)

      // Cache the bundle
      bundleCache.set(cacheKey, bundle)

      // Merge with existing file-based translations (API takes precedence)
      mergeLocaleMessage(lang, bundle)

      // Also save to localStorage for offline fallback
      try {
        localStorage.setItem(`lsx-i18n-${cacheKey}`, JSON.stringify(bundle))
        localStorage.setItem(`lsx-i18n-${cacheKey}-time`, Date.now().toString())
      } catch (_e) {
        // localStorage might be full, ignore
      }
    } catch (error: any) {
      loadError.value = error.message || 'Failed to load translations'

      // Try localStorage fallback
      const cached = localStorage.getItem(`lsx-i18n-${cacheKey}`)
      if (cached) {
        const bundle = JSON.parse(cached)
        bundleCache.set(cacheKey, bundle)
        mergeLocaleMessage(lang, bundle)
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Change the current language
   */
  async function setLanguage(lang: string): Promise<void> {
    // Load translations if not already loaded
    if (!bundleCache.has(`${lang}:all`)) {
      await loadLanguage(lang)
    }

    // Update vue-i18n locale
    locale.value = lang
    currentLanguage.value = lang

    // Persist to localStorage
    localStorage.setItem('lsx-language', lang)

    // Update HTML lang attribute
    document.documentElement.lang = lang
  }

  /**
   * Get available languages dynamically from vue-i18n
   */
  async function fetchLanguages(): Promise<LanguageProgress[]> {
    if (languagesCache.value) {
      return languagesCache.value
    }

    // Check if system is installed
    const isInstalled = localStorage.getItem('lsx-setup-completed') === 'true'

    // Language metadata (flexible - can be extended)
    const languageMetadata: Record<string, { name: string; nativeName: string; flag: string }> = {
      de: { name: 'German', nativeName: 'Deutsch', flag: 'de' },
      en: { name: 'English', nativeName: 'English', flag: 'gb' },
      pl: { name: 'Polish', nativeName: 'Polski', flag: 'pl' }
    }

    if (!isInstalled) {
      // Build language list dynamically from available locales
      const fallbackLanguages: LanguageProgress[] = availableLocales
        .map((code, index) => {
          const meta = languageMetadata[code] || {
            name: code.toUpperCase(),
            nativeName: code.toUpperCase(),
            flag: ''
          }
          return {
            language_code: code,
            language_name: meta.name,
            native_name: meta.nativeName,
            flag_svg_code: meta.flag,
            is_primary: true,
            priority: index + 1,

            rtl: false,
            active: true,
            total_keys: 0,
            translated_keys: 0,
            completion_percent: 100,
            verified_keys: 0,
            pending_suggestions: 0
          }
        })

      return fallbackLanguages
    }

    try {
      const languages = await getLanguages()
      languagesCache.value = languages
      return languages
    } catch (_error) {
      // API not available - build from available locales
      console.warn('[i18n] Could not fetch languages from API, using available locales')

      const fallbackLanguages: LanguageProgress[] = availableLocales
        .map((code, index) => {
          const meta = languageMetadata[code] || {
            name: code.toUpperCase(),
            nativeName: code.toUpperCase(),
            flag: ''
          }
          return {
            language_code: code,
            language_name: meta.name,
            native_name: meta.nativeName,
            flag_svg_code: meta.flag,
            is_primary: true,
            priority: index + 1,

            rtl: false,
            active: true,
            total_keys: 0,
            translated_keys: 0,
            completion_percent: 100,
            verified_keys: 0,
            pending_suggestions: 0
          }
        })

      return fallbackLanguages
    }
  }

  /**
   * Initialize i18n - call on app start
   */
  async function initialize(): Promise<void> {
    // Load primary language (German as base)
    await loadLanguage('de')

    // Load user's preferred language if different
    if (currentLanguage.value !== 'de') {
      await loadLanguage(currentLanguage.value)
    }

    // Set locale
    locale.value = currentLanguage.value
  }

  /**
   * Invalidate cache and reload
   */
  async function refreshTranslations(lang?: string): Promise<void> {
    const targetLang = lang || currentLanguage.value
    const cacheKey = `${targetLang}:all`

    bundleCache.delete(cacheKey)
    localStorage.removeItem(`lsx-i18n-${cacheKey}`)

    await loadLanguage(targetLang)
  }

  /**
   * Check if translations are stale (older than 1 hour)
   */
  function isStale(lang: string, namespace?: string): boolean {
    const cacheKey = `${lang}:${namespace || 'all'}`
    const timeStr = localStorage.getItem(`lsx-i18n-${cacheKey}-time`)

    if (!timeStr) return true

    const time = parseInt(timeStr, 10)
    const oneHour = 60 * 60 * 1000

    return Date.now() - time > oneHour
  }

  return {
    // State
    currentLanguage: computed(() => currentLanguage.value),
    isLoading: computed(() => isLoading.value),
    loadError: computed(() => loadError.value),
    languages: computed(() => languagesCache.value),

    // Methods
    t,
    locale,
    loadLanguage,
    setLanguage,
    fetchLanguages,
    initialize,
    refreshTranslations,
    isStale
  }
}

/**
 * Simple translate function for use outside components
 */
export function translate(key: string, params?: Record<string, any>): string {
  const lang = currentLanguage.value
  const cacheKey = `${lang}:all`
  const bundle = bundleCache.get(cacheKey)

  if (!bundle) {
    return key
  }

  let text = bundle[key] || key

  // Replace placeholders
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      text = text.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v))
    })
  }

  return text
}

/**
 * Get current language code
 */
export function getCurrentLanguage(): string {
  return currentLanguage.value
}

/**
 * Set current language (for use outside Vue)
 */
export function setCurrentLanguage(lang: string): void {
  currentLanguage.value = lang
  localStorage.setItem('lsx-language', lang)
}

export default useTranslation
