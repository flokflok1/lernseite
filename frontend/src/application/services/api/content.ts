/**
 * Content API Gateway
 *
 * Re-exports content/courses/categories APIs from infrastructure layer.
 * Provides DDD boundary enforcement.
 */

export * from '@/infrastructure/api/clients/courses'
export * from '@/infrastructure/api/clients/categories'
export type * from '@/infrastructure/api/clients/courses'
export type * from '@/infrastructure/api/clients/categories'
