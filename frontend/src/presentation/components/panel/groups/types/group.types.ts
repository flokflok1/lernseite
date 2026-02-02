/**
 * Group Domain Types (GBA System)
 */

export interface Group {
  id: string
  name: string
  slug: string
  type: 'system_admin' | 'org_admin' | 'custom'
  member_role?: 'owner' | 'member' | 'viewer'
  created_at: Date
  updated_at?: Date
}

export interface GroupMember {
  id: string
  group_id: string
  user_id: string
  role: 'owner' | 'member' | 'viewer'
  joined_at: Date
}

export interface GroupPermission {
  id: string
  group_id: string
  permission: string
  granted_at: Date
}
