/**
 * Application Services - API Gateway Layer
 *
 * 1:1 mapping with Backend api/v1/ structure:
 * - panel-admin  → panel/admin/
 * - panel-editor → panel/editor/
 * - panel-user   → panel/user/
 * - public       → public/
 *
 * Provides DDD boundary enforcement:
 * - Presentation layer imports from application/services/api/*
 * - NOT directly from infrastructure/api/*
 */

// Namespace exports (for qualified access: panelAdminApi.getUsers())
export * as panelAdminApi from './panel-admin'
export * as panelEditorApi from './panel-editor'
export * as panelUserApi from './panel-user'
export * as publicApi from './public'
export * as learningApi from './learning'
// Flat re-exports (for direct access: getUsers())
export * from './panel-admin'
export * from './panel-editor'
export * from './panel-user'
export * from './public'
export * from './learning'
