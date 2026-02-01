/**
 * Panel Store Modules
 * ===================
 * Barrel export for all panel-related stores.
 * Renamed: admin → panel (2026-02-01)
 */

export * from './panel.store'
export { useGroupsStore } from './groups.store'

// Deprecated: Use useGroupsStore instead
export { useGroupsStore as useRolesStore } from './groups.store'

