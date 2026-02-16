/**
 * User Domain Model (GBA - Group-Based Authorization)
 *
 * Encapsulates user identity and access control logic.
 * Derives role-like behavior from group hierarchy levels.
 *
 * Hierarchy Levels (from auth.store.ts):
 * - 1000+ = Owner (full system access)
 * - 900+  = SystemAdmin
 * - 750+  = Moderator
 * - 500+  = OrgAdmin
 * - 250+  = Creator/Teacher
 * - 100+  = Premium User
 * - 10+   = Regular User
 * - 0     = Guest
 *
 * Example:
 *   const user = UserModel.fromAPI(loginResponse.user, loginResponse.groups, loginResponse.permissions)
 *   user.isOwner           // true if hierarchy >= 1000
 *   user.canAccessAdminPanel // true if hierarchy >= 500
 *   user.hierarchyLevel    // highest group hierarchy_level
 */

import type { UserGroup } from './types'

export class UserModel {
  constructor(
    public readonly id: string,
    public readonly email: string,
    public readonly fullName: string,
    public readonly organisationId: string | null,
    public readonly isActive: boolean,
    public readonly emailVerified: boolean,
    public readonly groups: UserGroup[],
    public readonly permissions: string[],
    public readonly createdAt: Date
  ) {}

  // ── Hierarchy Level ────────────────────────────────────────────

  /**
   * Highest hierarchy level from all user groups.
   * Determines access tier (Owner=1000, Admin=900, etc.)
   */
  get hierarchyLevel(): number {
    if (this.groups.length === 0) return 0
    return Math.max(...this.groups.map(g => g.hierarchy_level))
  }

  /**
   * Display role derived from highest-level group name.
   */
  get displayRole(): string {
    if (this.groups.length === 0) return 'User'
    const highest = this.groups.reduce((a, b) =>
      a.hierarchy_level > b.hierarchy_level ? a : b
    )
    return highest.name
  }

  // ── Role Checks ────────────────────────────────────────────────

  get isOwner(): boolean {
    return this.hierarchyLevel >= 1000
  }

  get isSystemAdmin(): boolean {
    return this.hierarchyLevel >= 900
  }

  get isModerator(): boolean {
    return this.hierarchyLevel >= 750
  }

  get isOrgAdmin(): boolean {
    return this.hierarchyLevel >= 500
  }

  get isCreator(): boolean {
    return this.hierarchyLevel >= 250
  }

  get isPremium(): boolean {
    return this.hierarchyLevel >= 100
  }

  // ── Panel Access ───────────────────────────────────────────────

  get canAccessAdminPanel(): boolean {
    return this.hierarchyLevel >= 500
  }

  get canAccessUserPanel(): boolean {
    return this.isActive
  }

  // ── Permission Checks ──────────────────────────────────────────

  hasPermission(permission: string): boolean {
    return this.permissions.includes(permission)
  }

  hasAnyPermission(...perms: string[]): boolean {
    return perms.some(p => this.permissions.includes(p))
  }

  // ── Business Logic ─────────────────────────────────────────────

  canBeDeleted(): boolean {
    return !this.isOwner && this.isActive
  }

  /**
   * Check if user belongs to an organisation (team member).
   */
  get isTeamMember(): boolean {
    return this.organisationId !== null
  }

  // ── Factory ────────────────────────────────────────────────────

  /**
   * Create UserModel from API response data.
   *
   * Handles both login response (groups/permissions separate)
   * and merged user objects (groups/permissions on user).
   */
  static fromAPI(
    data: Record<string, unknown>,
    groups?: UserGroup[],
    permissions?: string[]
  ): UserModel {
    const userGroups = groups
      ?? (data.groups as UserGroup[])
      ?? []
    const userPermissions = permissions
      ?? (data.permissions as string[])
      ?? []

    return new UserModel(
      (data.user_id as string) || (data.id as string) || '',
      (data.email as string) || '',
      (data.full_name as string) || (data.fullName as string) || '',
      (data.organisation_id as string | null) ?? null,
      (data.is_active as boolean) ?? true,
      (data.email_verified as boolean) ?? false,
      userGroups,
      userPermissions,
      new Date((data.created_at as string) || Date.now())
    )
  }

  /**
   * Minimal user for domain model references (Course.model.ts).
   */
  toMinimal(): { id: string; isSystemAdmin: boolean } {
    return {
      id: this.id,
      isSystemAdmin: this.isSystemAdmin
    }
  }

  toJSON(): Record<string, unknown> {
    return {
      id: this.id,
      email: this.email,
      fullName: this.fullName,
      organisationId: this.organisationId,
      isActive: this.isActive,
      hierarchyLevel: this.hierarchyLevel,
      displayRole: this.displayRole,
      groups: this.groups,
      permissions: this.permissions
    }
  }
}
