/**
 * Panel User API Gateway
 *
 * Re-exports user APIs from infrastructure layer.
 * Consolidates former user.ts + user-specific parts of system.ts
 * (gamification, tts, tokens, subscriptions, audio, dashboard, feedback, mathToolkit).
 * Maps 1:1 to backend api/v1/panel/user/
 */

export * from '@/infrastructure/api/clients/panel/user'
export type * from '@/infrastructure/api/clients/panel/user'
