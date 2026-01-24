/**
 * Social API Gateway
 *
 * Re-exports social/feedback/gamification APIs from infrastructure layer.
 * Provides DDD boundary enforcement.
 */

export * from '@/infrastructure/api/clients/feedback'
export * from '@/infrastructure/api/clients/gamification'
export type * from '@/infrastructure/api/clients/feedback'
export type * from '@/infrastructure/api/clients/gamification'
