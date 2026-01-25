/**
 * Admin Store Modules
 * ===================
 * Barrel export for all admin-related stores.
 */

export * from './admin.store'
export { useGroupsStore } from './groups.store'

// Deprecated: Use useGroupsStore instead
export { useGroupsStore as useRolesStore } from './groups.store'
