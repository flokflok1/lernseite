/**
 * Admin Domain - Organisation Management API
 * ==========================================
 *
 * Organisation administration and settings management.
 * Part of the DDD Architecture - Infrastructure Layer (API Clients).
 *
 * Handles:
 * - Organisation details and metadata
 * - Organisation settings and branding
 * - Member management and invitations
 * - Course assignments
 *
 * Usage:
 * import { getOrganisationDetail, updateOrganisationSettings } from '@/infrastructure/api/clients/panel/admin'
 * import type { OrgDetail, OrgMember } from '@/infrastructure/api/clients/panel/admin'
 */

import http from '@/infrastructure/api/http'

// ============================================================================
// Organisation Management Types
// ============================================================================

/**
 * Complete organisation information and statistics.
 * Includes billing, members, and resource usage data.
 */
export interface OrgDetail {
  /** Unique organisation identifier */
  organisation_id: number
  /** Organisation name */
  name: string
  /** Organisation type: school, company, teacher_team, creator_team */
  type: 'school' | 'company' | 'teacher_team' | 'creator_team'
  /** Associated plan ID (if any) */
  plan_id?: string | null
  /** Human-readable plan name */
  plan_name?: string
  /** Total token pool for organisation */
  token_pool: number
  /** Tokens already used */
  token_used: number
  /** Tokens remaining available */
  token_available: number
  /** Total members in organisation */
  total_users: number
  /** Active members (logged in past 30 days) */
  active_users: number
  /** Timestamp when organisation was created */
  created_at: string
  /** Whether organisation is currently active */
  is_active: boolean
  /** Custom domain for organisation (if any) */
  domain?: string | null
  /** Organisation branding/theming settings */
  branding?: {
    /** Logo image URL */
    logo_url?: string
    /** Primary theme color (hex) */
    primary_color?: string
    /** Secondary theme color (hex) */
    secondary_color?: string
  }
}

/**
 * Organisation member information.
 * Represents a user within an organisation context.
 */
export interface OrgMember {
  /** User identifier */
  user_id: number
  /** User email address */
  email: string
  /** User's first name */
  first_name: string
  /** User's last name */
  last_name: string
  /** User's role globally */
  role: string
  /** User's role within this organisation (student, teacher, admin) */
  org_role?: string
  /** Whether member account is active */
  is_active: boolean
  /** When user joined the organisation */
  joined_at: string
  /** Last activity timestamp */
  last_active?: string | null
  /** Token usage by this member */
  token_usage?: number
  /** Number of courses assigned to this member */
  assigned_courses?: number
}

/**
 * Settings for organisation configuration.
 */
export interface OrgSettings {
  /** Organisation name */
  name: string
  /** Branding configuration */
  branding?: {
    /** Logo image URL */
    logo_url?: string
    /** Primary theme color */
    primary_color?: string
    /** Secondary theme color */
    secondary_color?: string
  }
  /** Custom domain (FQDN) */
  domain?: string | null
}

/**
 * Request to invite a new user to the organisation.
 */
export interface OrgInviteRequest {
  /** Email address of user to invite */
  email: string
  /** First name for new user */
  first_name: string
  /** Last name for new user */
  last_name: string
  /** Role to assign (student, teacher) */
  role: string
  /** Whether to send invitation email */
  send_email?: boolean
}

// ============================================================================
// Organisation Details API
// ============================================================================

/**
 * Get organisation details (org admin).
 *
 * Retrieves full organisation information including branding, settings, and usage.
 *
 * @param orgId - Organisation identifier
 * @returns Complete organisation details
 *
 * @example
 * const org = await getOrganisationDetail(123)
 * console.log(`Organisation: ${org.name}`)
 * console.log(`Active users: ${org.active_users}`)
 */
export const getOrganisationDetail = async (orgId: number): Promise<OrgDetail> => {
  const response = await http.get<{
    success: boolean
    organisation: OrgDetail
  }>(`/organisations/${orgId}`)

  return response.data.organisation
}

/**
 * Update organisation settings (org admin).
 *
 * Updates branding, name, and domain settings for the organisation.
 * Only provided fields are updated (partial update).
 *
 * @param orgId - Organisation identifier
 * @param settings - Settings to update (all fields optional)
 *
 * @example
 * await updateOrganisationSettings(123, {
 *   name: 'New Organisation Name',
 *   branding: { primary_color: '#0066FF' }
 * })
 */
export const updateOrganisationSettings = async (
  orgId: number,
  settings: Partial<OrgSettings>
): Promise<void> => {
  await http.patch(`/organisations/${orgId}/settings`, settings)
}

// ============================================================================
// Member Management API
// ============================================================================

/**
 * Get organisation members (org admin).
 *
 * Retrieves paginated list of organisation members with optional filtering.
 *
 * @param orgId - Organisation identifier
 * @param params - Filtering and pagination parameters
 * @returns Paginated member list
 *
 * @example
 * const result = await getOrganisationMembers(123, {
 *   page: 1,
 *   limit: 20,
 *   role: 'teacher'
 * })
 * console.log(`Total members: ${result.total}`)
 */
export const getOrganisationMembers = async (
  orgId: number,
  params?: {
    page?: number
    limit?: number
    search?: string
    role?: string
    status?: 'active' | 'inactive'
  }
): Promise<{
  members: OrgMember[]
  total: number
  page: number
  limit: number
}> => {
  const response = await http.get<{
    success: boolean
    members: OrgMember[]
    total: number
    page: number
    limit: number
  }>(`/organisations/${orgId}/members`, { params })

  return {
    members: response.data.members,
    total: response.data.total,
    page: response.data.page,
    limit: response.data.limit
  }
}

/**
 * Invite user to organisation (org admin).
 *
 * Sends invitation to a new user to join the organisation.
 * Can optionally send invitation email to the user.
 *
 * @param orgId - Organisation identifier
 * @param request - Invitation request with user details and role
 *
 * @example
 * await inviteUserToOrganisation(123, {
 *   email: 'teacher@example.com',
 *   first_name: 'Jane',
 *   last_name: 'Doe',
 *   role: 'teacher',
 *   send_email: true
 * })
 */
export const inviteUserToOrganisation = async (
  orgId: number,
  request: OrgInviteRequest
): Promise<void> => {
  await http.post(`/organisations/${orgId}/members/invite`, request)
}

/**
 * Remove user from organisation (org admin).
 *
 * Removes a user's membership from the organisation.
 * User account is not deleted, just membership revoked.
 *
 * @param orgId - Organisation identifier
 * @param userId - User identifier to remove
 *
 * @example
 * await removeUserFromOrganisation(123, 456)
 */
export const removeUserFromOrganisation = async (
  orgId: number,
  userId: number
): Promise<void> => {
  await http.delete(`/organisations/${orgId}/members/${userId}`)
}

/**
 * Update user's organisation role (org admin).
 *
 * Changes the user's role within the organisation context.
 * Can change from student to teacher or vice versa.
 *
 * @param orgId - Organisation identifier
 * @param userId - User identifier
 * @param role - New role (student, teacher, admin)
 *
 * @example
 * await updateOrganisationUserRole(123, 456, 'teacher')
 */
export const updateOrganisationUserRole = async (
  orgId: number,
  userId: number,
  role: string
): Promise<void> => {
  await http.patch(`/organisations/${orgId}/members/${userId}/role`, { role })
}
