/**
 * Group Domain Types (GBA System)
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
