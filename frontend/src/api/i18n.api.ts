/**
 * Backward Compatibility Re-export
 * This file re-exports from the new domain-organized location.
 * Existing imports like `import * from '@/api/i18n.api'` continue to work.
 *
 * New code should use: import { ... } from '@/api/system'
 */
export * from './system/i18n.api'
