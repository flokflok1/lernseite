/**
 * Learning API Gateway
 *
 * Re-exports learning/player/audio/TTS APIs from infrastructure layer.
 * Provides DDD boundary enforcement.
 */

export * from '@/infrastructure/api/clients/player'
export * from '@/infrastructure/api/clients/audio'
export * from '@/infrastructure/api/clients/tts'
export * from '@/infrastructure/api/clients/tutor'
export type * from '@/infrastructure/api/clients/player'
export type * from '@/infrastructure/api/clients/audio'
export type * from '@/infrastructure/api/clients/tts'
export type * from '@/infrastructure/api/clients/tutor'
