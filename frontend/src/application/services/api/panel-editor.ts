/**
 * Panel Editor API Gateway
 *
 * Re-exports editor APIs from infrastructure layer.
 * Consolidates former content.ts + course-editor.ts.
 * Maps 1:1 to backend api/v1/panel/editor/
 */

export * from '@/infrastructure/api/clients/panel/editor'
export type * from '@/infrastructure/api/clients/panel/editor'
