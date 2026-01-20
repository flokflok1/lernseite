/**
 * Backward Compatibility Re-export
 * This file re-exports from the new domain-organized location.
 * Original file was moved from root to /api/content/authoring.api.ts
 * Existing imports like `import * from '@/api/course-authoring.api'` continue to work.
 *
 * New code should use: import { ... } from '@/api/content'
 */
export * from './content/authoring.api'
