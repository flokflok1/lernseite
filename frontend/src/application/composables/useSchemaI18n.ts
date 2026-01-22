/**
 * useSchemaI18n Composable
 * =======================
 *
 * Composable for resolving i18n keys from ui_schemas in Vue components.
 * Provides easy access to the I18nSchemaResolver with reactive updates when locale changes.
 *
 * Usage:
 * const { resolveSchema, resolveField, resolveKey, checkCoverage } = useSchemaI18n()
 * const resolved = resolveSchema(uiSchema)
 * const label = resolveField(field, 'label')
 * const coverage = checkCoverage(uiSchema)
 */

import { computed, watch } from 'vue'
import { useI18n, type I18n } from 'vue-i18n'
import { i18n } from '@/infrastructure/plugins/i18n'
import {
  I18nSchemaResolver,
  createGlobalI18nResolver,
  getGlobalI18nResolver,
  type UISchema,
  type ResolvedUISchema,
  type I18nField,
  type ResolvedField
} from '@/infrastructure/utils/i18nResolver'

// Global resolver instance (initialized once)
let resolver: I18nSchemaResolver | null = null

/**
 * Initialize the global i18n resolver
 * Call this in app initialization (e.g., in main.ts or setup.ts)
 *
 * @param i18n - Global I18n instance (from createI18n)
 * @returns Initialized I18nSchemaResolver instance
 */
export function initializeSchemaI18n(i18n: I18n): I18nSchemaResolver {
  if (!resolver) {
    resolver = createGlobalI18nResolver(i18n)
  }
  return resolver
}

/**
 * Main composable for schema i18n resolution
 */
export function useSchemaI18n() {
  const { locale } = useI18n()

  // Get or initialize resolver
  let currentResolver: I18nSchemaResolver
  try {
    currentResolver = getGlobalI18nResolver()
  } catch (error) {
    // Use global i18n instance (not hook return)
    currentResolver = createGlobalI18nResolver(i18n)
  }

  // Watch for locale changes and update resolver
  watch(locale, (newLocale) => {
    if (currentResolver) {
      currentResolver.setLocale(newLocale as string)
    }
  })

  /**
   * Resolve a complete ui_schema for a component
   * Returns schema with all i18n keys translated
   */
  function resolveSchema(schema: UISchema): ResolvedUISchema {
    return currentResolver.resolveSchema(schema, locale.value as string)
  }

  /**
   * Resolve a single field from a schema
   * Returns field with all i18n properties translated
   */
  function resolveField(
    field: I18nField,
    property?: 'label' | 'placeholder' | 'hint' | 'description'
  ): ResolvedField | string {
    if (property) {
      // If specific property requested, return just that property
      return currentResolver.resolveFieldProperty(field, property, locale.value as string)
    }
    // Otherwise return fully resolved field
    return currentResolver.resolveField(field, locale.value as string)
  }

  /**
   * Resolve a single i18n key
   * Returns translated text or falls back to German fallback
   */
  function resolveKey(key: string | undefined, fallback?: string): string {
    return currentResolver.resolveKey(key, fallback, locale.value as string)
  }

  /**
   * Resolve all fields in a schema
   */
  function resolveFields(fields: I18nField[]): ResolvedField[] {
    return currentResolver.resolveFields(fields, locale.value as string)
  }

  /**
   * Get field label by field name
   * Useful for accessing specific field labels dynamically
   */
  function getFieldLabel(schema: UISchema, fieldName: string): string {
    const field = schema.fields.find((f) => f.name === fieldName)
    if (!field) return ''
    return currentResolver.resolveFieldProperty(field, 'label', locale.value as string)
  }

  /**
   * Get field placeholder by field name
   */
  function getFieldPlaceholder(schema: UISchema, fieldName: string): string {
    const field = schema.fields.find((f) => f.name === fieldName)
    if (!field) return ''
    return currentResolver.resolveFieldProperty(field, 'placeholder', locale.value as string)
  }

  /**
   * Get field hint by field name
   */
  function getFieldHint(schema: UISchema, fieldName: string): string {
    const field = schema.fields.find((f) => f.name === fieldName)
    if (!field) return ''
    return currentResolver.resolveFieldProperty(field, 'hint', locale.value as string)
  }

  /**
   * Check translation coverage for a schema
   * Returns statistics: { total, translated, missing, coverage }
   */
  function checkCoverage(schema: UISchema): {
    total: number
    translated: number
    missing: number
    coverage: number
  } {
    return currentResolver.checkTranslationCoverage(schema, locale.value as string)
  }

  /**
   * Get list of missing translations for a schema
   * Useful for debugging and identifying gaps
   */
  function getMissingTranslations(schema: UISchema): string[] {
    return currentResolver.getMissingTranslations(schema, locale.value as string)
  }

  /**
   * Extract all i18n keys from a schema
   * Useful for debugging and understanding schema structure
   */
  function extractKeys(schema: UISchema): string[] {
    return currentResolver.extractI18nKeys(schema)
  }

  /**
   * Create a resolver specifically for one schema
   * Returns object with helper methods for that schema
   */
  function createResolver(schema: UISchema) {
    return currentResolver.createSchemaResolver(schema)
  }

  /**
   * Current locale as computed property
   * Re-renders when locale changes
   */
  const currentLocale = computed(() => locale.value as string)

  return {
    // Computed properties
    currentLocale,

    // Main resolution methods
    resolveSchema,
    resolveField,
    resolveKey,
    resolveFields,

    // Helper methods
    getFieldLabel,
    getFieldPlaceholder,
    getFieldHint,
    createResolver,

    // Debugging/Analysis methods
    checkCoverage,
    getMissingTranslations,
    extractKeys,

    // Access to resolver instance if needed
    getResolver: () => currentResolver
  }
}

export default useSchemaI18n
