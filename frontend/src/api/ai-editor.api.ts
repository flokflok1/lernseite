/**
 * Backward Compatibility Re-export
 * This file re-exports from the new domain-organized location.
 * Original file was moved from root to /api/learning/editor.api.ts
 * Existing imports like `import * from '@/api/ai-editor.api'` continue to work.
 *
 * New code should use: import { ... } from '@/api/learning'
 */
export * from './learning/editor.api'
