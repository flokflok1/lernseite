/**
 * System API Gateway
 *
 * Re-exports system/i18n/math/exam APIs from infrastructure layer.
 * Provides DDD boundary enforcement.
 */

export * from '@/infrastructure/api/clients/i18n'
export * from '@/infrastructure/api/clients/math-toolkit'
export * from '@/infrastructure/api/clients/exam-simulation'
export type * from '@/infrastructure/api/clients/i18n'
export type * from '@/infrastructure/api/clients/math-toolkit'
export type * from '@/infrastructure/api/clients/exam-simulation'
