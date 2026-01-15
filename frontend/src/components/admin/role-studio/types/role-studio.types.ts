/**
 * Role Studio Types
 *
 * TypeScript interfaces for role studio mode management
 * Consumed by: RoleStudioDashboard, RoleEditor, PermissionManager
 */

/**
 * Valid studio modes that roles can be assigned to
 */
export type StudioMode = 'admin' | 'moderator' | 'org_admin' | 'org_member' | 'teacher' | 'user' | 'guest'

/**
 * Role studio mode configuration
 * Defines which studio mode a role accesses and what permissions it has
 */
export interface RoleStudioMode {
  role_code: string
  display_name: string
  studio_mode: StudioMode
  permissions: Record<string, boolean>
  requires_organization: boolean
  is_active: boolean
  description: string | null
  created_at: string
  updated_at: string | null
}

/**
 * Request payload for creating a new role studio mode
 */
export interface CreateRoleStudioRequest {
  role_code: string
  display_name: string
  studio_mode: StudioMode
  permissions?: Record<string, boolean>
  requires_organization?: boolean
  description?: string
}

/**
 * Request payload for updating a role studio mode
 */
export interface UpdateRoleStudioRequest {
  display_name?: string
  studio_mode?: StudioMode
  permissions?: Record<string, boolean>
  requires_organization?: boolean
  is_active?: boolean
  description?: string
}

/**
 * Request payload for updating role permissions only
 */
export interface UpdatePermissionsRequest {
  permissions: Record<string, boolean>
  change_reason?: string
}

/**
 * Change history entry for audit trail
 */
export interface RoleChangeHistory {
  history_id: number
  role_code: string
  previous_display_name?: string
  new_display_name?: string
  previous_studio_mode?: string
  new_studio_mode?: string
  previous_permissions?: Record<string, boolean>
  new_permissions?: Record<string, boolean>
  changed_by: string
  change_reason?: string
  changed_at: string
}

/**
 * Studio configuration returned during login
 * Used to configure frontend UI immediately upon authentication
 */
export interface StudioConfig {
  role_code: string
  studio_mode: StudioMode
  display_name: string
  permissions: Record<string, boolean>
  requires_organization: boolean
}

/**
 * API response types
 */
export interface RoleStudioListResponse {
  data: RoleStudioMode[]
  total: number
  limit: number
  offset: number
}

export interface RoleStudioDetailResponse {
  role_code: string
  display_name: string
  studio_mode: string
  requires_organization: boolean
  permissions: Record<string, boolean>
  is_active: boolean
  description?: string
  created_at: string
  updated_at?: string
  permission_count: number
}

export interface ChangeHistoryResponse {
  data: RoleChangeHistory[]
  total: number
}

/**
 * Filter options for role listing
 */
export interface RoleFilterOptions {
  active_only?: boolean
  studio_mode?: StudioMode
  requires_organization?: boolean
  search?: string
}

/**
 * State for role studio management
 */
export interface RoleStudioState {
  roles: RoleStudioMode[]
  selectedRole: RoleStudioMode | null
  loading: boolean
  error: string | null
  totalRoles: number
  currentPage: number
  pageSize: number
  changeHistory: RoleChangeHistory[]
}
