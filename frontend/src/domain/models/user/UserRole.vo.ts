/**
 * UserRole Value Object
 *
 * Encapsulates user role logic and permissions hierarchy.
 * Single responsibility: Role validation and role-based method resolution
 *
 * Valid roles (12 total):
 * - Free: FREE
 * - Premium subscription tiers: PREMIUM, CREATOR, TEACHER, SCHOOL, COMPANY
 * - Support staff: SUPPORT, MODERATOR
 * - System admin: ADMIN
 * - Organization-specific admin: SCHOOL_ADMIN, COMPANY_ADMIN, OWNER
 *
 * Permission Hierarchy:
 * - Free tier: No special permissions (readonly user)
 * - Premium tier: Access to premium features (subscription-based)
 * - Organization-level: SCHOOL_ADMIN, COMPANY_ADMIN have elevated privileges within org
 * - OWNER: Organization owner (highest org-level permissions)
 * - System-level: ADMIN (system administrator), MODERATOR (content moderation)
 *
 * Usage:
 *   const role = UserRole.create('Premium')
 *   console.log(role.isPremium()) // true
 *   console.log(role.isSystemAdmin()) // false
 *   console.log(role.hasElevatedPrivileges()) // false
 *
 *   const adminRole = UserRole.create('school_admin')
 *   console.log(adminRole.hasElevatedPrivileges()) // true
 *   console.log(adminRole.isPremium()) // false (orthogonal to subscription)
 */

export enum UserRoleEnum {
  FREE = 'Free',
  PREMIUM = 'Premium',
  CREATOR = 'Creator',
  TEACHER = 'Teacher',
  SCHOOL = 'School',
  COMPANY = 'Company',
  SUPPORT = 'Support',
  MODERATOR = 'Moderator',
  ADMIN = 'Admin',
  SCHOOL_ADMIN = 'school_admin',
  COMPANY_ADMIN = 'company_admin',
  OWNER = 'owner'
}

export class UserRole {
  private constructor(private readonly role: UserRoleEnum) {}

  /**
   * Create UserRole value object from string
   *
   * @param role - Role name to validate
   * @returns UserRole instance
   * @throws Error if role is invalid
   *
   * @example
   * const role = UserRole.create('Premium')
   * // Throws: Error('Invalid user role: invalid')
   * UserRole.create('invalid')
   */
  static create(role: string): UserRole {
    const roleUpper = role as UserRoleEnum

    if (!Object.values(UserRoleEnum).includes(roleUpper)) {
      throw new Error(`Invalid user role: ${role}`)
    }

    return new UserRole(roleUpper)
  }

  /**
   * Check if this role has premium features access
   *
   * Premium tier includes: PREMIUM, CREATOR, TEACHER, SCHOOL, COMPANY
   * Free tier (FREE) does NOT have premium features
   * Admin (ADMIN) is NOT premium (has different permission model)
   *
   * Business Rule:
   * - Premium = "subscription tier" that grants premium features
   * - Admin = "system tier" that grants all access (but not premium features per se)
   *
   * @returns true if role has premium features
   */
  isPremium(): boolean {
    return [
      UserRoleEnum.PREMIUM,
      UserRoleEnum.CREATOR,
      UserRoleEnum.TEACHER,
      UserRoleEnum.SCHOOL,
      UserRoleEnum.COMPANY
    ].includes(this.role)
  }

  /**
   * Check if this role is system admin
   *
   * Only ADMIN role has system administration privileges.
   *
   * Business Rule:
   * - ADMIN can: create/delete users, manage courses, access all data
   * - Other roles cannot (including MODERATOR)
   *
   * @returns true if role is ADMIN
   */
  isSystemAdmin(): boolean {
    return this.role === UserRoleEnum.ADMIN
  }

  /**
   * Check if this role is moderator
   *
   * Only MODERATOR role has moderation privileges.
   *
   * @returns true if role is MODERATOR
   */
  isModerator(): boolean {
    return this.role === UserRoleEnum.MODERATOR
  }

  /**
   * Check if this role has elevated privileges
   *
   * Elevated privileges = can perform administrative actions at any level.
   * Includes: System admins, moderators, and organization-level admins
   *
   * Business Rule:
   * - ADMIN: Full system access
   * - MODERATOR: Content moderation access
   * - SCHOOL_ADMIN: Admin privileges within school organization
   * - COMPANY_ADMIN: Admin privileges within company organization
   * - OWNER: Organization owner (highest org-level privileges)
   * - Others: No elevated privileges
   *
   * @returns true if role has any administrative privileges
   */
  hasElevatedPrivileges(): boolean {
    return [
      UserRoleEnum.ADMIN,
      UserRoleEnum.MODERATOR,
      UserRoleEnum.SCHOOL_ADMIN,
      UserRoleEnum.COMPANY_ADMIN,
      UserRoleEnum.OWNER
    ].includes(this.role)
  }

  /**
   * Get role string value
   *
   * @returns Role name as string
   */
  toString(): string {
    return this.role
  }

  /**
   * Check equality with another UserRole
   *
   * @param other - UserRole to compare
   * @returns true if roles are equal
   */
  equals(other: UserRole): boolean {
    return this.role === other.role
  }

  /**
   * Get raw role enum value
   *
   * @private
   * @returns UserRoleEnum value
   */
  get rawValue(): UserRoleEnum {
    return this.role
  }
}
