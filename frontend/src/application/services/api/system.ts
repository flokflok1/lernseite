/**
 * System API Gateway
 *
 * Re-exports system domain APIs from infrastructure layer.
 * Provides DDD boundary enforcement.
 */

// default export: http client
export { default } from '@/infrastructure/api/clients/system/http'

// named exports/types: everything from system client index
export * from '@/infrastructure/api/clients/system'
export type * from '@/infrastructure/api/clients/system'

