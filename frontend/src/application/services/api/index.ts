/**
 * Application Services - API Gateway Layer
 *
 * Provides DDD boundary enforcement:
 * - Presentation layer imports from application/services/api/*
 * - NOT directly from infrastructure/api/*
 *
 * This prevents circular dependencies and enforces clean architecture layers.
 */

export * as adminApi from './admin'
export * as contentApi from './content'
export * as learningApi from './learning'
export * as systemApi from './system'
export * as userApi from './user'
export * as socialApi from './social'

// Re-export most common imports directly
export * from './admin'
export * from './content'
export * from './learning'
export * from './system'
export * from './user'
export * from './social'
