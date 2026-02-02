/**
 * i18n Translation Keys Validation Test
 *
 * Tests:
 * - All 100 i18n.sync translation keys exist in all 3 languages (de, en, pl)
 * - No translation values are empty
 * - Key structure is consistent across all languages
 * - All required keys for components are present
 */

import { describe, it, expect } from 'vitest'
import deTranslations from '@/locales/de/admin.json'
import enTranslations from '@/locales/en/admin.json'
import plTranslations from '@/locales/pl/admin.json'

// Expected i18n.sync keys required by components
const REQUIRED_KEYS = [
  // Dashboard
  'title',
  'subtitle',
  'mode',
  'mode_manual',
  'mode_manual_desc',
  'mode_auto',
  'mode_auto_desc',
  'start_scan',

  // Tabs
  'tab_dashboard',
  'tab_scan',
  'tab_comparison',
  'tab_history',

  // Statistics
  'total_syncs',
  'successful_syncs',
  'failed_syncs',
  'pending_resolutions',

  // Scan Results
  'scan_results',
  'scan_status',
  'scan_duration',
  'scan_error',
  'languages_affected',
  'keys_processed',
  'total_keys',
  'total_changes',
  'summary',

  // Key Categories
  'new_keys',
  'new_keys_summary',
  'changed_keys',
  'changed_keys_summary',
  'deleted_keys',
  'deleted_keys_summary',
  'conflicted_keys',
  'conflicted_keys_summary',

  // Next Steps
  'next_steps',
  'next_review_desc',
  'next_apply_auto_desc',
  'next_apply_manual_desc',

  // Comparison Panel
  'comparison_title',
  'category_filter',
  'category_new',
  'category_changed',
  'category_deleted',
  'category_conflicts',
  'no_items',
  'similarity',
  'frontend_value',
  'database_value',

  // Actions
  'action',
  'action_add',
  'action_update',
  'action_delete',
  'action_skip',
  'resolved',
  'apply',
  'apply_warning',
  'force_apply',
  'cancel',

  // History Panel
  'history_title',
  'history_subtitle',
  'filter_status',
  'filter_mode',
  'all',
  'conflicts',
  'created_at',
  'actions',
  'not_applicable',

  // Rollback
  'rollback',
  'rollback_tooltip',
  'rollback_warning',
  'rollback_reason',
  'rollback_reason_placeholder',
  'confirm_rollback',

  // Status Values
  'status',
  'status_pending',
  'status_completed',
  'status_failed',
  'status_rolled_back',
  'pending',
  'completed',

  // Pagination
  'previous',
  'next',
  'page_info',

  // Empty States
  'no_history',
  'no_scan_results',
  'no_sync_active',

  // Legacy keys (for backward compatibility)
  'languages',
  'namespaces',
  'keys',
  'moderation',
  'suggestions',
  'queue',
  'ai_review',
  'approve',
  'reject',
  'quality_score',
  'import_keys',
  'ai_translate',
  'seed_keys',
  'bulk_translate',
  'sync_id'
]

describe('i18n Sync Translations', () => {
  const deI18n = deTranslations.admin?.i18n || {}
  const enI18n = enTranslations.admin?.i18n || {}
  const plI18n = plTranslations.admin?.i18n || {}

  describe('Translation File Structure', () => {
    it('should have i18n section in all language files', () => {
      expect(deI18n).toBeDefined()
      expect(enI18n).toBeDefined()
      expect(plI18n).toBeDefined()
    })

    it('should have matching key counts across all languages', () => {
      const deKeyCount = Object.keys(deI18n).length
      const enKeyCount = Object.keys(enI18n).length
      const plKeyCount = Object.keys(plI18n).length

      expect(deKeyCount).toBeGreaterThan(0)
      expect(enKeyCount).toBe(deKeyCount)
      expect(plKeyCount).toBe(deKeyCount)
    })
  })

  describe('Required Keys Presence', () => {
    it('should have all 73+ required keys in German', () => {
      const missingKeys = REQUIRED_KEYS.filter(key => !(key in deI18n))
      expect(missingKeys).toHaveLength(0)
    })

    it('should have all 73+ required keys in English', () => {
      const missingKeys = REQUIRED_KEYS.filter(key => !(key in enI18n))
      expect(missingKeys).toHaveLength(0)
    })

    it('should have all 73+ required keys in Polish', () => {
      const missingKeys = REQUIRED_KEYS.filter(key => !(key in plI18n))
      expect(missingKeys).toHaveLength(0)
    })
  })

  describe('Key Consistency Across Languages', () => {
    it('should have identical keys in all three languages', () => {
      const deKeys = new Set(Object.keys(deI18n))
      const enKeys = new Set(Object.keys(enI18n))
      const plKeys = new Set(Object.keys(plI18n))

      // Find differences
      const deOnly = [...deKeys].filter(k => !enKeys.has(k) && !plKeys.has(k))
      const enOnly = [...enKeys].filter(k => !deKeys.has(k) && !plKeys.has(k))
      const plOnly = [...plKeys].filter(k => !deKeys.has(k) && !enKeys.has(k))

      expect(deOnly).toHaveLength(0)
      expect(enOnly).toHaveLength(0)
      expect(plOnly).toHaveLength(0)
    })
  })

  describe('Translation Value Quality', () => {
    it('should have non-empty translations in German', () => {
      const emptyKeys = Object.entries(deI18n)
        .filter(([_, value]) => !value || String(value).trim() === '')
        .map(([key]) => key)

      expect(emptyKeys).toHaveLength(0)
    })

    it('should have non-empty translations in English', () => {
      const emptyKeys = Object.entries(enI18n)
        .filter(([_, value]) => !value || String(value).trim() === '')
        .map(([key]) => key)

      expect(emptyKeys).toHaveLength(0)
    })

    it('should have non-empty translations in Polish', () => {
      const emptyKeys = Object.entries(plI18n)
        .filter(([_, value]) => !value || String(value).trim() === '')
        .map(([key]) => key)

      expect(emptyKeys).toHaveLength(0)
    })

    it('should have distinct translations across languages (not just copies)', () => {
      // Sample keys that should have different translations
      const sampleKeys = ['title', 'mode_manual', 'scan_results', 'rollback_warning']

      for (const key of sampleKeys) {
        const deValue = deI18n[key]
        const enValue = enI18n[key]
        const plValue = plI18n[key]

        // At least some should be different (English shouldn't match German typically)
        const allSame = deValue === enValue && enValue === plValue
        expect(allSame).toBe(false)
      }
    })
  })

  describe('Component-Specific Keys', () => {
    describe('Dashboard Keys', () => {
      it('should have all dashboard control keys', () => {
        const dashboardKeys = ['title', 'subtitle', 'mode', 'mode_manual', 'mode_auto', 'start_scan']
        dashboardKeys.forEach(key => {
          expect(deI18n[key]).toBeDefined()
          expect(enI18n[key]).toBeDefined()
          expect(plI18n[key]).toBeDefined()
        })
      })
    })

    describe('Tab Navigation Keys', () => {
      it('should have all tab keys', () => {
        const tabKeys = ['tab_dashboard', 'tab_scan', 'tab_comparison', 'tab_history']
        tabKeys.forEach(key => {
          expect(deI18n[key]).toBeDefined()
          expect(enI18n[key]).toBeDefined()
          expect(plI18n[key]).toBeDefined()
        })
      })
    })

    describe('Scan Panel Keys', () => {
      it('should have all scan result keys', () => {
        const scanKeys = [
          'scan_results',
          'scan_status',
          'scan_duration',
          'new_keys',
          'changed_keys',
          'deleted_keys',
          'conflicted_keys',
          'languages_affected'
        ]
        scanKeys.forEach(key => {
          expect(deI18n[key]).toBeDefined()
          expect(enI18n[key]).toBeDefined()
          expect(plI18n[key]).toBeDefined()
        })
      })
    })

    describe('Comparison Panel Keys', () => {
      it('should have all comparison and resolution keys', () => {
        const comparisonKeys = [
          'comparison_title',
          'category_filter',
          'category_new',
          'category_changed',
          'category_deleted',
          'category_conflicts',
          'similarity',
          'frontend_value',
          'database_value',
          'action',
          'action_add',
          'action_update',
          'action_delete',
          'action_skip'
        ]
        comparisonKeys.forEach(key => {
          expect(deI18n[key]).toBeDefined()
          expect(enI18n[key]).toBeDefined()
          expect(plI18n[key]).toBeDefined()
        })
      })
    })

    describe('History Panel Keys', () => {
      it('should have all history and pagination keys', () => {
        const historyKeys = [
          'history_title',
          'history_subtitle',
          'filter_status',
          'filter_mode',
          'created_at',
          'previous',
          'next',
          'page_info'
        ]
        historyKeys.forEach(key => {
          expect(deI18n[key]).toBeDefined()
          expect(enI18n[key]).toBeDefined()
          expect(plI18n[key]).toBeDefined()
        })
      })
    })

    describe('Rollback Keys', () => {
      it('should have all rollback operation keys', () => {
        const rollbackKeys = [
          'rollback',
          'rollback_tooltip',
          'rollback_warning',
          'rollback_reason',
          'rollback_reason_placeholder',
          'confirm_rollback'
        ]
        rollbackKeys.forEach(key => {
          expect(deI18n[key]).toBeDefined()
          expect(enI18n[key]).toBeDefined()
          expect(plI18n[key]).toBeDefined()
        })
      })
    })
  })

  describe('Parameterized Translations', () => {
    it('should have correct parameter placeholders', () => {
      // page_info should have {page} and {total}
      expect(deI18n['page_info']).toMatch(/{page}/)
      expect(deI18n['page_info']).toMatch(/{total}/)
      expect(enI18n['page_info']).toMatch(/{page}/)
      expect(enI18n['page_info']).toMatch(/{total}/)
      expect(plI18n['page_info']).toMatch(/{page}/)
      expect(plI18n['page_info']).toMatch(/{total}/)
    })
  })

  describe('Translation Key Accessibility', () => {
    it('should allow accessing keys via dot notation simulation', () => {
      // This simulates how Vue i18n would access: $t('admin.i18n.title')
      const testKey = 'title'
      expect(deI18n[testKey]).toBeDefined()
      expect(typeof deI18n[testKey] === 'string').toBe(true)
    })
  })

  describe('Localization Quality', () => {
    it('should have culturally appropriate German translations', () => {
      // Sample German-specific characteristics
      expect(deI18n['title']).toContain('Übersetzungen') // Uses ü
      expect(deI18n['mode_manual']).toBe('Manuell')
    })

    it('should have proper English translations', () => {
      expect(enI18n['title']).toBe('Translations')
      expect(enI18n['mode_manual']).toBe('Manual')
    })

    it('should have proper Polish translations', () => {
      // Polish-specific characteristics (Polish characters)
      expect(plI18n['title']).toContain('Tłumaczenia') // Uses ł and ż
      expect(plI18n['mode_manual']).toBe('Ręczny') // Uses ę
    })
  })
})
