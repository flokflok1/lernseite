/**
 * KursBuilder Composables - Barrel Export
 *
 * Central export for all KursBuilder composables.
 * Provides reusable business logic for course authoring components.
 *
 * @example
 * ```typescript
 * import {
 *   useSessionManager,
 *   useChatManager
 * } from '@/presentation/components/panel/editor/ai/authoring/course-builder/composables'
 * ```
 *
 * @module course-builder/composables
 */

export { useSessionManager } from './useSessionManager.ts'
export { useChatManager } from './useChatManager.ts'
export { useFileManagement } from './useFileManagement.ts'
