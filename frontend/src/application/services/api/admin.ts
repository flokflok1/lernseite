/**
 * Admin API Gateway
 *
 * Re-exports admin API from infrastructure layer.
 * Provides DDD boundary enforcement - presentation layer imports from
 * application services, not directly from infrastructure.
 */

export * from '@/infrastructure/api/clients/admin'
export type * from '@/infrastructure/api/clients/admin'
