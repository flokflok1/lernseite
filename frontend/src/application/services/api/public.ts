/**
 * Public API Gateway
 *
 * Re-exports public (unauthenticated) APIs from infrastructure layer.
 * Contains: i18n, setup APIs.
 * Maps 1:1 to backend api/v1/public/
 */

export * from '@/infrastructure/api/clients/public'
export type * from '@/infrastructure/api/clients/public'
