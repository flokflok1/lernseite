/**
 * useLocaleImport Composable
 *
 * Reads all frontend locale JSON files and imports them into the DB
 * via the import-locales endpoint for de, en, and pl.
 */

import { ref } from 'vue'
import { languagesApi } from '@/infrastructure/api/clients/panel/admin/languages.api'

// Static imports of all locale modules (same as i18n.ts plugin)
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

/** Namespace mapping: barrel key -> { namespace_code: data } */
interface NamespaceMap {
  [namespace: string]: Record<string, unknown>
}

/**
 * Build namespace map from barrel-exported module.
 *
 * Each barrel (e.g. enPanel) exports { panel: { languages: {...}, system: {...} } }
 * We need to convert that to { "panel.languages": {...}, "panel.system": {...} }
 */
function buildNamespaces(modules: Record<string, unknown>[]): NamespaceMap {
  const result: NamespaceMap = {}

  for (const mod of modules) {
    for (const [topKey, topValue] of Object.entries(mod)) {
      if (typeof topValue !== 'object' || topValue === null) continue
      // Each top-level key (e.g. "panel") may contain sub-namespaces
      // like { languages: {...}, system: {...} }
      for (const [subKey, subValue] of Object.entries(topValue as Record<string, unknown>)) {
        if (typeof subValue === 'object' && subValue !== null && !Array.isArray(subValue)) {
          result[`${topKey}.${subKey}`] = subValue as Record<string, unknown>
        } else if (typeof subValue === 'string') {
          // Direct key at top level (e.g. common.save)
          if (!result[topKey]) result[topKey] = {}
          ;(result[topKey] as Record<string, unknown>)[subKey] = subValue
        }
      }
    }
  }

  return result
}

/** Locale data for each reference language */
const LOCALE_DATA: Record<string, Record<string, unknown>[]> = {
  de: [deCommon, deErrors, deDashboard, deSetup, deTutor, deLegal, dePanel, deAiEditor, deCourses, deFeatures],
  en: [enCommon, enErrors, enDashboard, enSetup, enTutor, enLegal, enPanel, enAiEditor, enCourses, enFeatures],
  pl: [plCommon, plErrors, plDashboard, plSetup, plTutor, plLegal, plPanel, plAiEditor, plCourses, plFeatures]
}

const REFERENCE_LANGS = ['de', 'en', 'pl'] as const

export function useLocaleImport() {
  const importing = ref(false)
  const currentLang = ref('')
  const importResults = ref<{ lang: string; count: number }[]>([])
  const error = ref<string | null>(null)

  async function seedAll(): Promise<void> {
    importing.value = true
    error.value = null
    importResults.value = []

    try {
      for (const lang of REFERENCE_LANGS) {
        currentLang.value = lang
        const namespaces = buildNamespaces(LOCALE_DATA[lang])
        const result = await languagesApi.importLocales(lang, namespaces)
        importResults.value.push({ lang, count: result.translations_imported })
      }
    } catch (err: any) {
      error.value = err.message || 'Import failed'
    } finally {
      importing.value = false
      currentLang.value = ''
    }
  }

  return { importing, currentLang, importResults, error, seedAll }
}
