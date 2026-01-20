/**
 * Backward Compatibility Re-export
 * This file re-exports from the new domain-organized location.
 * Original file was moved from root to /api/learning/authoring.api.ts
 * Existing imports like `import * from '@/api/ai-authoring.api'` continue to work.
 *
 * New code should use: import { ... } from '@/api/learning'
 */
export * from './learning/authoring.api'
