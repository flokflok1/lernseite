/**
 * LernsystemX - Admin API
 *
 * REFACTORED: This file now re-exports from modular structure.
 * Original: 3024 lines monolith
 * New: 14 focused modules in ./admin/
 *
 * All imports remain compatible:
 *   import { adminGetUsers, AdminUser } from '@/api/admin.api'
 *
 * Or use new direct imports:
 *   import { adminGetUsers } from '@/api/admin/users.api'
 *   import type { AdminUser } from '@/api/admin/types'
 */

export * from './admin/index'
