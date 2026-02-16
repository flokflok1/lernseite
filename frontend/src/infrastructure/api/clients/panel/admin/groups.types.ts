/**
 * Group Domain Types (GBA System)
 *
 * Canonical type definitions for group-based access control API responses.
 * Presentation layer re-exports these types for component usage.
 */

export interface Group {
  id: string
  name: string
  slug: string
  type: string
  description?: string
  hierarchy_level?: number
  is_system_group: boolean
  is_protected: boolean
  access_level?: 'owner' | 'member' | 'viewer'
  created_at: string
  updated_at?: string
}

export interface GroupMember {
  user_id: string
  email: string
  full_name: string
  username: string
  access_level: string
  joined_at: string
  is_active: boolean
}

export interface GroupPermission {
  id: string
  permission: string
  display_name?: string
  category?: string
  description?: string
  assigned_at?: string
}

/** Permission from global registry (core.permissions table) */
export interface RegistryPermission {
  id: string
  code: string
  display_name: string
  category: string
  description?: string
}
