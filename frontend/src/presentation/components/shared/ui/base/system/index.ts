// System Domain Components
// System operations, settings, and shared utilities
//
// Migrated from:
// - admin/system-operations/* → system/admin/*
// - admin/shared/* → system/shared/*
// - base/dialogs/* → system/shared/dialogs/ (Wave 1)

// Admin System Operations
export { default as SystemStatus } from '../../../../shared/ui/system/admin/SystemStatus.vue'
export * from './admin/settings'
export * from './admin/views'

// Shared System Components
export * from './shared/dialogs'
export * from './shared/previews'
