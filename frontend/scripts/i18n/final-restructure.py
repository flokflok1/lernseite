#!/usr/bin/env python3
"""
Final i18n restructure - Senior Dev Quality
- All JSON files in subdirectories (no root-level JSONs)
- Clear naming (no multiple "common", "courses" confusion)
- Barrel exports everywhere
"""
import json
import shutil
from pathlib import Path
from collections import OrderedDict

LOCALES_DIR = Path('.')
LANGUAGES = ['de', 'en', 'pl']

def sort_json_keys(obj):
    """Recursively sort JSON keys alphabetically."""
    if isinstance(obj, dict):
        return OrderedDict(sorted((k, sort_json_keys(v)) for k, v in obj.items()))
    elif isinstance(obj, list):
        return [sort_json_keys(item) for item in obj]
    else:
        return obj

def save_json(path: Path, data: dict):
    """Save JSON file with proper formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sort_json_keys(data), f, ensure_ascii=False, indent=2)

def create_barrel_export(directory: Path, files: list):
    """Create index.ts barrel export."""
    imports = '\n'.join([f"import {f.stem.replace('-', '_')} from './{f.name}'" for f in files])
    exports = '\n  ' + ',\n  '.join([f'...{f.stem.replace("-", "_")}' for f in files])

    content = f"""// Auto-generated barrel export
{imports}

export default {{{exports}
}}
"""

    with open(directory / 'index.ts', 'w', encoding='utf-8') as f:
        f.write(content)

def restructure_language(lang: str):
    """Complete restructure for one language."""
    print(f"\n{'='*70}")
    print(f"Processing {lang.upper()}...")
    print('='*70)

    lang_dir = LOCALES_DIR / lang

    # =========================================================================
    # 1. RENAME EXISTING SUBDIRECTORIES
    # =========================================================================
    print("\n🔄 Step 1: Renaming subdirectories...")

    # Rename admin/common.json → admin/shared.json
    if (lang_dir / 'admin' / 'common.json').exists():
        shutil.move(
            lang_dir / 'admin' / 'common.json',
            lang_dir / 'admin' / 'shared.json'
        )
        print(f"  ✓ Renamed admin/common.json → admin/shared.json")

    # Rename admin/courses.json → admin/course-management.json
    if (lang_dir / 'admin' / 'courses.json').exists():
        shutil.move(
            lang_dir / 'admin' / 'courses.json',
            lang_dir / 'admin' / 'course-management.json'
        )
        print(f"  ✓ Renamed admin/courses.json → admin/course-management.json")

    # Rename admin/ai.json → admin/ai-settings.json
    if (lang_dir / 'admin' / 'ai.json').exists():
        shutil.move(
            lang_dir / 'admin' / 'ai.json',
            lang_dir / 'admin' / 'ai-settings.json'
        )
        print(f"  ✓ Renamed admin/ai.json → admin/ai-settings.json")

    # Rename features/common.json → features/shared.json
    if (lang_dir / 'features' / 'common.json').exists():
        shutil.move(
            lang_dir / 'features' / 'common.json',
            lang_dir / 'features' / 'shared.json'
        )
        print(f"  ✓ Renamed features/common.json → features/shared.json")

    # Rename aiEditor/common.json → aiEditor/shared.json
    if (lang_dir / 'aiEditor' / 'common.json').exists():
        shutil.move(
            lang_dir / 'aiEditor' / 'common.json',
            lang_dir / 'aiEditor' / 'shared.json'
        )
        print(f"  ✓ Renamed aiEditor/common.json → aiEditor/shared.json")

    # Rename courses/courses.json → courses/overview.json (to avoid confusion)
    if (lang_dir / 'courses' / 'courses.json').exists():
        shutil.move(
            lang_dir / 'courses' / 'courses.json',
            lang_dir / 'courses' / 'overview.json'
        )
        print(f"  ✓ Renamed courses/courses.json → courses/overview.json")

    # =========================================================================
    # 2. MOVE ROOT-LEVEL JSONs INTO SUBDIRECTORIES
    # =========================================================================
    print("\n📦 Step 2: Moving root-level JSONs to subdirectories...")

    root_files = {
        'common.json': 'common',
        'dashboard.json': 'dashboard',
        'errors.json': 'errors',
        'legal.json': 'legal',
        'setup.json': 'setup',
        'tutor.json': 'tutor'
    }

    for filename, subdir in root_files.items():
        source = lang_dir / filename
        if source.exists():
            # Load JSON
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Create subdirectory
            target_dir = lang_dir / subdir
            target_dir.mkdir(exist_ok=True)

            # Split if large (>400 lines)
            lines = len(json.dumps(data, indent=2).split('\n'))

            if lines > 400 and isinstance(data, dict) and len(data) > 3:
                # Split into multiple files
                print(f"  ✓ Splitting {filename} ({lines} lines) into {subdir}/")

                # Split by top-level keys
                for key, value in data.items():
                    save_json(target_dir / f"{key}.json", {key: value})

                # Create barrel export
                json_files = sorted(target_dir.glob('*.json'))
                create_barrel_export(target_dir, json_files)
            else:
                # Move as single file (rename to index.json)
                print(f"  ✓ Moving {filename} → {subdir}/index.json")
                save_json(target_dir / 'index.json', data)

                # Create simple barrel export
                with open(target_dir / 'index.ts', 'w', encoding='utf-8') as f:
                    f.write(f"// Re-export from index.json\nimport data from './index.json'\nexport default data\n")

            # Remove old root file
            source.unlink()

    # =========================================================================
    # 3. UPDATE BARREL EXPORTS FOR RENAMED FILES
    # =========================================================================
    print("\n🔧 Step 3: Updating barrel exports...")

    for subdir in ['admin', 'aiEditor', 'courses', 'features']:
        subdir_path = lang_dir / subdir
        if subdir_path.exists():
            json_files = sorted(subdir_path.glob('*.json'))
            if json_files:
                create_barrel_export(subdir_path, json_files)
                print(f"  ✓ Updated {subdir}/index.ts")

def update_i18n_plugin():
    """Update i18n.ts with new structure."""
    print("\n🔧 Updating i18n.ts...")

    i18n_file = Path('..') / 'plugins' / 'i18n.ts'

    new_content = """/**
 * Vue i18n Plugin Configuration
 * ==============================
 *
 * HYBRID TRANSLATION SYSTEM:
 * 1. JSON files (src/locales/*/) = Fallback/Default
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
// Import locale modules (all in subdirectories)
// =============================================================================

// German (de)
import deCommon from '@/locales/de/common/index'
import deErrors from '@/locales/de/errors/index'
import deDashboard from '@/locales/de/dashboard/index'
import deSetup from '@/locales/de/setup/index'
import deTutor from '@/locales/de/tutor/index'
import deLegal from '@/locales/de/legal/index'

import deAdmin from '@/locales/de/admin/index'
import deAiEditor from '@/locales/de/aiEditor/index'
import deCourses from '@/locales/de/courses/index'
import deFeatures from '@/locales/de/features/index'

// English (en)
import enCommon from '@/locales/en/common/index'
import enErrors from '@/locales/en/errors/index'
import enDashboard from '@/locales/en/dashboard/index'
import enSetup from '@/locales/en/setup/index'
import enTutor from '@/locales/en/tutor/index'
import enLegal from '@/locales/en/legal/index'

import enAdmin from '@/locales/en/admin/index'
import enAiEditor from '@/locales/en/aiEditor/index'
import enCourses from '@/locales/en/courses/index'
import enFeatures from '@/locales/en/features/index'

// Polish (pl)
import plCommon from '@/locales/pl/common/index'
import plErrors from '@/locales/pl/errors/index'
import plDashboard from '@/locales/pl/dashboard/index'
import plSetup from '@/locales/pl/setup/index'
import plTutor from '@/locales/pl/tutor/index'
import plLegal from '@/locales/pl/legal/index'

import plAdmin from '@/locales/pl/admin/index'
import plAiEditor from '@/locales/pl/aiEditor/index'
import plCourses from '@/locales/pl/courses/index'
import plFeatures from '@/locales/pl/features/index'

// Merge all modules into single language objects
const de = {
  ...deCommon,
  ...deErrors,
  ...deDashboard,
  ...deSetup,
  ...deTutor,
  ...deLegal,
  ...deAdmin,
  ...deAiEditor,
  ...deCourses,
  ...deFeatures
}

const en = {
  ...enCommon,
  ...enErrors,
  ...enDashboard,
  ...enSetup,
  ...enTutor,
  ...enLegal,
  ...enAdmin,
  ...enAiEditor,
  ...enCourses,
  ...enFeatures
}

const pl = {
  ...plCommon,
  ...plErrors,
  ...plDashboard,
  ...plSetup,
  ...plTutor,
  ...plLegal,
  ...plAdmin,
  ...plAiEditor,
  ...plCourses,
  ...plFeatures
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
"""

    with open(i18n_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("  ✓ Updated i18n.ts with new import structure")

def main():
    print("🔧 Final i18n restructure - Senior Dev Quality")
    print("="*70)
    print("Strategy:")
    print("  1. Rename files to avoid confusion (common → shared, etc.)")
    print("  2. Move ALL root-level JSONs into subdirectories")
    print("  3. Create barrel exports everywhere")
    print("  4. Update i18n.ts")
    print("="*70)

    for lang in LANGUAGES:
        restructure_language(lang)

    update_i18n_plugin()

    print("\n" + "="*70)
    print("✅ Final restructure complete!")
    print("="*70)
    print("\nNew structure:")
    print("  ✓ NO root-level JSON files")
    print("  ✓ Everything in subdirectories")
    print("  ✓ Clear naming (no confusion)")
    print("  ✓ Barrel exports everywhere")
    print("\nNext steps:")
    print("  1. Run: python3 validate-i18n.py")
    print("  2. Update Vue components with new key names")
    print("  3. Test: npm run build")

if __name__ == '__main__':
    main()
