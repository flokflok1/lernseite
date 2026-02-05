/**
 * i18n Schema Resolver Utility
 * ============================
 *
 * Resolves i18n translation keys from schema definitions.
 * Provides a bridge between database ui_schemas and the Vue i18n system.
 *
 * Usage:
 * const resolver = new I18nSchemaResolver(i18n)
 * const label = resolver.resolveLabel(field, 'label_i18n', 'label_fallback')
 * const resolvedSchema = resolver.resolveSchemaFields(uiSchema, fields)
 *
 * Hybrid Strategy:
 * - Primary: i18n key lookup (e.g., 'learning_methods.lm00.field.title')
 * - Fallback: German fallback text if key missing or not translated
 * - Last Resort: Original key as string (debugging)
 */

import type { I18n } from 'vue-i18n'

/**
 * Interface for schema field with i18n keys
 */
export interface I18nField {
  name: string
  type: string
  label_i18n?: string
  label_fallback?: string
  placeholder_i18n?: string
  placeholder_fallback?: string
  hint_i18n?: string
  hint_fallback?: string
  description_i18n?: string
  description_fallback?: string
  [key: string]: unknown
}

/**
 * Interface for resolved field with translated labels
 */
export interface ResolvedField extends I18nField {
  label?: string
  placeholder?: string
  hint?: string
  description?: string
  options?: Array<{
    value: string | number | boolean
    label?: string
    label_i18n?: string
    label_fallback?: string
  }>
}

/**
 * Interface for ui_schema from database
 */
export interface UISchema {
  form_type: string
  language_support: string[]
  layout?: string
  fields: I18nField[]
  ui_config?: {
    show_preview?: boolean
    auto_save?: boolean
    sections?: Array<{
      name: string
      label_i18n?: string
      label_fallback?: string
    }>
    [key: string]: unknown
  }
  [key: string]: unknown
}

/**
 * Resolved UI Schema with all translations applied
 */
export interface ResolvedUISchema extends UISchema {
  fields: ResolvedField[]
  ui_config?: {
    show_preview?: boolean
    auto_save?: boolean
    sections?: Array<{
      name: string
      label?: string
    }>
    [key: string]: unknown
  }
}

/**
 * I18n Schema Resolver - Utility for resolving i18n keys from schemas
 */
export class I18nSchemaResolver {
  private i18n: I18n
  private currentLocale: string

  constructor(i18n: I18n) {
    this.i18n = i18n
    this.currentLocale = i18n.global.locale.value as string
  }

  /**
   * Set current locale
   * Call this when locale changes to update resolver
   */
  setLocale(locale: string): void {
    this.currentLocale = locale
  }

  /**
   * Resolve a single i18n key
   * Returns translated text or falls back to German fallback text
   *
   * @param key - i18n translation key (e.g., 'learning_methods.lm00.fields.title')
   * @param fallback - German fallback text if key not found
   * @param locale - Optional override for locale (defaults to current)
   * @returns Translated text or fallback or key as last resort
   */
  resolveKey(
    key: string | undefined,
    fallback: string | undefined,
    locale?: string
  ): string {
    if (!key) {
      return fallback || ''
    }

    const targetLocale = locale || this.currentLocale

    // Try to get translation from i18n
    try {
      // Use i18n's t() function to resolve the key
      const translated = this.i18n.global.t(key, undefined, { locale: targetLocale })

      // If translation found and different from key (not missing), use it
      if (translated !== key && typeof translated === 'string' && translated.trim() !== '') {
        return translated
      }

      // If locale is not German, try German as fallback
      if (targetLocale !== 'de') {
        const germanTranslation = this.i18n.global.t(key, undefined, { locale: 'de' })
        if (
          germanTranslation !== key &&
          typeof germanTranslation === 'string' &&
          germanTranslation.trim() !== ''
        ) {
          return germanTranslation
        }
      }
    } catch (_error) {
      // Key resolution failed, use fallback
    }

    // Fall back to German fallback text
    if (fallback) {
      return fallback
    }

    // Last resort: return key as string (for debugging)
    return key
  }

  /**
   * Resolve a label or placeholder from a field
   *
   * @param field - Field definition with i18n keys
   * @param type - Type of field property ('label', 'placeholder', 'hint', 'description')
   * @param locale - Optional locale override
   * @returns Resolved translation or fallback
   */
  resolveFieldProperty(
    field: I18nField,
    type: 'label' | 'placeholder' | 'hint' | 'description',
    locale?: string
  ): string {
    const i18nKey = field[`${type}_i18n`] as string | undefined
    const fallback = field[`${type}_fallback`] as string | undefined
    return this.resolveKey(i18nKey, fallback, locale)
  }

  /**
   * Resolve all i18n properties in a field
   *
   * @param field - Field definition with i18n keys
   * @param locale - Optional locale override
   * @returns Field with all i18n properties resolved
   */
  resolveField(field: I18nField, locale?: string): ResolvedField {
    const resolved: ResolvedField = { ...field }

    // Resolve string properties
    if (field.label_i18n || field.label_fallback) {
      resolved.label = this.resolveFieldProperty(field, 'label', locale)
    }

    if (field.placeholder_i18n || field.placeholder_fallback) {
      resolved.placeholder = this.resolveFieldProperty(field, 'placeholder', locale)
    }

    if (field.hint_i18n || field.hint_fallback) {
      resolved.hint = this.resolveFieldProperty(field, 'hint', locale)
    }

    if (field.description_i18n || field.description_fallback) {
      resolved.description = this.resolveFieldProperty(field, 'description', locale)
    }

    // Resolve select/radio options if present
    if (field.options && Array.isArray(field.options)) {
      resolved.options = field.options.map((option: any) => ({
        ...option,
        label: this.resolveKey(option.label_i18n, option.label_fallback, locale)
      }))
    }

    return resolved
  }

  /**
   * Resolve all fields in a schema
   *
   * @param fields - Array of field definitions
   * @param locale - Optional locale override
   * @returns Array of resolved fields
   */
  resolveFields(fields: I18nField[], locale?: string): ResolvedField[] {
    return fields.map((field) => this.resolveField(field, locale))
  }

  /**
   * Resolve all i18n properties in a complete ui_schema
   *
   * @param schema - UI schema from database
   * @param locale - Optional locale override
   * @returns Complete schema with all i18n properties resolved
   */
  resolveSchema(schema: UISchema, locale?: string): ResolvedUISchema {
    const resolved: ResolvedUISchema = { ...schema }

    // Resolve all fields
    resolved.fields = this.resolveFields(schema.fields, locale)

    // Resolve sections in ui_config if present
    if (schema.ui_config?.sections) {
      resolved.ui_config = {
        ...schema.ui_config,
        sections: schema.ui_config.sections.map((section: any) => ({
          ...section,
          label: this.resolveKey(section.label_i18n, section.label_fallback, locale)
        }))
      }
    }

    return resolved
  }

  /**
   * Extract all i18n keys from a schema
   * Useful for debugging and understanding what translations are needed
   *
   * @param schema - UI schema from database
   * @returns Array of all i18n keys found in schema
   */
  extractI18nKeys(schema: UISchema): string[] {
    const keys: string[] = []

    // Extract from fields
    schema.fields.forEach((field) => {
      if (field.label_i18n) keys.push(field.label_i18n as string)
      if (field.placeholder_i18n) keys.push(field.placeholder_i18n as string)
      if (field.hint_i18n) keys.push(field.hint_i18n as string)
      if (field.description_i18n) keys.push(field.description_i18n as string)

      // Extract from options
      if (field.options && Array.isArray(field.options)) {
        field.options.forEach((option: any) => {
          if (option.label_i18n) keys.push(option.label_i18n)
        })
      }
    })

    // Extract from sections
    if (schema.ui_config?.sections) {
      schema.ui_config.sections.forEach((section: any) => {
        if (section.label_i18n) keys.push(section.label_i18n)
      })
    }

    return [...new Set(keys)] // Remove duplicates
  }

  /**
   * Check translation coverage for a schema
   * Returns statistics about how many fields have translations
   *
   * @param schema - UI schema from database
   * @param locale - Locale to check
   * @returns Coverage statistics
   */
  checkTranslationCoverage(
    schema: UISchema,
    locale?: string
  ): {
    total: number
    translated: number
    missing: number
    coverage: number
  } {
    const targetLocale = locale || this.currentLocale
    const keys = this.extractI18nKeys(schema)

    let translated = 0
    keys.forEach((key) => {
      const result = this.i18n.global.t(key, undefined, { locale: targetLocale })
      if (result !== key) {
        translated++
      }
    })

    return {
      total: keys.length,
      translated,
      missing: keys.length - translated,
      coverage: keys.length > 0 ? Math.round((translated / keys.length) * 100) : 100
    }
  }

  /**
   * Get missing translations for a schema
   * Useful for identifying gaps in translation coverage
   *
   * @param schema - UI schema from database
   * @param locale - Locale to check
   * @returns Array of missing translation keys
   */
  getMissingTranslations(schema: UISchema, locale?: string): string[] {
    const targetLocale = locale || this.currentLocale
    const keys = this.extractI18nKeys(schema)

    return keys.filter((key) => {
      const result = this.i18n.global.t(key, undefined, { locale: targetLocale })
      return result === key // Key not translated (still equals the key)
    })
  }

  /**
   * Create resolver for specific schema
   * Useful for reusable schema resolution in components
   *
   * @param schema - UI schema from database
   * @returns Object with helper methods for this specific schema
   */
  createSchemaResolver(schema: UISchema) {
    return {
      resolve: (locale?: string) => this.resolveSchema(schema, locale),
      getFieldLabel: (fieldName: string, locale?: string) => {
        const field = schema.fields.find((f) => f.name === fieldName)
        return field ? this.resolveFieldProperty(field, 'label', locale) : ''
      },
      getFieldPlaceholder: (fieldName: string, locale?: string) => {
        const field = schema.fields.find((f) => f.name === fieldName)
        return field ? this.resolveFieldProperty(field, 'placeholder', locale) : ''
      },
      checkCoverage: (locale?: string) => this.checkTranslationCoverage(schema, locale),
      getMissing: (locale?: string) => this.getMissingTranslations(schema, locale)
    }
  }
}

/**
 * Create a global i18n resolver instance (usually in composables)
 */
let globalResolver: I18nSchemaResolver | null = null

export function createGlobalI18nResolver(i18n: I18n): I18nSchemaResolver {
  globalResolver = new I18nSchemaResolver(i18n)
  return globalResolver
}

export function getGlobalI18nResolver(): I18nSchemaResolver {
  if (!globalResolver) {
    throw new Error('Global i18n resolver not initialized. Call createGlobalI18nResolver first.')
  }
  return globalResolver
}
