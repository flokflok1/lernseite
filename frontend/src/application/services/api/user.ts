/**
 * User API Gateway
 *
 * Re-exports user/profile/tokens/subscriptions APIs from infrastructure layer.
 * Provides DDD boundary enforcement.
 */

export * from '@/infrastructure/api/clients/profile'
export * from '@/infrastructure/api/clients/tokens'
export * from '@/infrastructure/api/clients/subscriptions'
export type * from '@/infrastructure/api/clients/profile'
export type * from '@/infrastructure/api/clients/tokens'
export type * from '@/infrastructure/api/clients/subscriptions'
