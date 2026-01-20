/**
 * Backward Compatibility Re-export
 * This file re-exports from the new domain-organized location.
 * Existing imports like `import * from '@/api/courses.api'` continue to work.
 *
 * New code should use: import { ... } from '@/api/content'
 */
export * from './content/courses.api'
