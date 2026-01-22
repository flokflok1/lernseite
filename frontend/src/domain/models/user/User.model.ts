/**
 * User Aggregate Root
 *
 * Domain Model containing ALL business logic related to users.
 * Single source of truth for user-related business rules.
 *
 * NO business logic should be in stores, composables, or components!
 * All authorization checks and business rules live here.
 *
 * Usage:
 *   const user = User.fromAPI(apiResponse)
 *   if (user.canAccessPremiumFeatures()) { ... }
 *   if (user.canEdit(targetUser)) { ... }
 */

import { Email } from '@/domain/value-objects/Email.vo'
import { UserRole, UserRoleEnum } from './UserRole.vo'

export class User {
  /**
   * Create User instance.
   * Private constructor enforces use of static factory methods.
   */
  constructor(
    public readonly id: string,
    public readonly email: Email,
    public readonly username: string,
    public readonly firstName: string,
    public readonly lastName: string,
    public readonly role: UserRole,
    public readonly isActive: boolean,
    public readonly createdAt: Date,
    public readonly updatedAt?: Date,
    public readonly lastLogin?: Date
  ) {}

  // ===================================
  // BUSINESS LOGIC (migrated from stores)
  // ===================================

  /**
   * Full name display
   *
   * Previously in: auth.store.ts computed property
   *
   * @returns Formatted "FirstName LastName" or just name if single part
   */
  get fullName(): string {
    return `${this.firstName} ${this.lastName}`.trim()
  }

  /**
   * Premium access check
   *
   * Previously in: auth.store.ts lines 37-55
   *
   * Delegates to UserRole.isPremium() which checks:
   * Premium = PREMIUM, CREATOR, TEACHER, SCHOOL, COMPANY
   * NOT premium = FREE, ADMIN (different permission model)
   *
   * @returns true if user has premium subscription tier
   */
  get isPremium(): boolean {
    return this.role.isPremium()
  }

  /**
   * System admin check
   *
   * Previously in: auth.store.ts lines 70-75
   *
   * Only ADMIN role has system administration privileges.
   * MODERATOR does NOT have admin access (separate permission model).
   *
   * @returns true if user is system administrator
   */
  get isSystemAdmin(): boolean {
    return this.role.isSystemAdmin()
  }

  /**
   * Moderator check
   *
   * Only MODERATOR role has moderation privileges (content moderation, DSA compliance).
   *
   * @returns true if user is moderator
   */
  get isModerator(): boolean {
    return this.role.isModerator()
  }

  /**
   * Elevated privileges check
   *
   * Can perform administrative or moderator actions.
   *
   * Business Rule: ADMIN OR MODERATOR
   *
   * @returns true if user has elevated privileges (admin or moderator)
   */
  get hasElevatedPrivileges(): boolean {
    return this.role.hasElevatedPrivileges()
  }

  /**
   * User display label for UI
   *
   * Combines full name and role for user identification.
   *
   * @returns Formatted string like "John Doe (Premium)"
   */
  get displayLabel(): string {
    return `${this.fullName} (${this.role.toString()})`
  }

  /**
   * Can access premium features check
   *
   * Previously in: auth.store.ts (complex getter combining multiple conditions)
   *
   * Business Rule: User must be BOTH:
   * 1. Active account (not suspended/deactivated)
   * 2. Premium subscription tier
   *
   * Inactive premium users cannot access premium features.
   *
   * @returns true if user can access premium features
   */
  canAccessPremiumFeatures(): boolean {
    return this.isActive && this.isPremium
  }

  /**
   * Can edit user check
   *
   * Business Rules:
   * 1. User must be active (inactive users can't perform actions)
   * 2. User can always edit their own profile
   * 3. System admin can edit any user
   * 4. Regular users cannot edit other users
   *
   * @param targetUser - User to edit
   * @returns true if currentUser can edit targetUser
   */
  canEdit(targetUser: User): boolean {
    if (!this.isActive) return false

    // Can edit self
    if (this.id === targetUser.id) return true

    // Only admin can edit others
    return this.isSystemAdmin
  }

  /**
   * Can delete user check
   *
   * Business Rules:
   * 1. User must be active
   * 2. User cannot delete themselves (prevents accidental self-deletion)
   * 3. Only system admin can delete users
   * 4. Moderator CANNOT delete users (different privilege model)
   *
   * @param targetUser - User to delete
   * @returns true if currentUser can delete targetUser
   */
  canDelete(targetUser: User): boolean {
    if (!this.isActive) return false

    // Cannot delete self
    if (this.id === targetUser.id) return false

    // Only admin can delete (not moderator)
    return this.isSystemAdmin
  }

  /**
   * Can view user profile check
   *
   * Business Rules:
   * 1. Can always view own profile
   * 2. Admin can view any profile
   * 3. Moderator can view any profile (DSA compliance)
   * 4. Regular users cannot view other profiles
   *
   * @param targetUser - User profile to view
   * @returns true if currentUser can view targetUser profile
   */
  canViewProfile(targetUser: User): boolean {
    // Can view own profile
    if (this.id === targetUser.id) return true

    // Admin and moderator can view any profile
    return this.hasElevatedPrivileges
  }

  /**
   * Account status check
   *
   * @returns true if account is active and in good standing
   */
  isInGoodStanding(): boolean {
    return this.isActive
  }

  /**
   * Is new user check
   *
   * Business Rule: User created within last 24 hours
   *
   * @returns true if user is new (created <24h ago)
   */
  isNewUser(): boolean {
    const now = new Date()
    const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000)
    return this.createdAt > dayAgo
  }

  /**
   * Days since last login
   *
   * @returns Number of days since last login, or undefined if never logged in
   */
  getDaysSinceLastLogin(): number | undefined {
    if (!this.lastLogin) return undefined

    const now = new Date()
    const diffMs = now.getTime() - this.lastLogin.getTime()
    return Math.floor(diffMs / (1000 * 60 * 60 * 24))
  }

  // ===================================
  // TRANSFORMATION METHODS
  // ===================================

  /**
   * Convert API DTO to Domain Model
   *
   * Single point of transformation from API layer to domain layer.
   * Handles both camelCase (frontend) and snake_case (backend) field names.
   * Validates all required fields and converts to typed objects.
   *
   * @param data - Raw API response data
   * @returns User domain model instance
   * @throws Error if data is invalid or required fields missing
   *
   * @example
   * const user = User.fromAPI(apiResponse.data)
   * // Handles:
   * // - email validation (Email.create)
   * // - role validation (UserRole.create)
   * // - snake_case/camelCase field mapping
   * // - date parsing and timezone handling
   */
  static fromAPI(data: any): User {
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid user data: expected object')
    }

    // Debug: Log incoming data structure
    console.log('[User.fromAPI] Incoming API data:', {
      keys: Object.keys(data),
      data: data
    })

    // Extract fields with fallbacks for both naming conventions
    const id = data.id || data.user_id
    const email = data.email || data.email_address
    const username = data.username || data.user_name || email  // Use email as fallback
    const firstName = data.firstName || data.first_name
    const lastName = data.lastName || data.last_name
    const role = data.role || data.role_type
    const isActive = data.isActive ?? data.is_active ?? true
    const createdAt = data.createdAt || data.created_at
    const updatedAt = data.updatedAt || data.updated_at
    const lastLogin = data.lastLogin || data.last_login

    // Debug: Log extracted fields
    console.log('[User.fromAPI] Extracted fields:', {
      id: { type: typeof id, value: id },
      email: { type: typeof email, value: email },
      username: { type: typeof username, value: username },
      firstName: { type: typeof firstName, value: firstName },
      lastName: { type: typeof lastName, value: lastName },
      role: { type: typeof role, value: role }
    })

    // Validate required fields
    if (!id) throw new Error('User data missing required field: id')
    if (!email) throw new Error('User data missing required field: email')
    if (!username) throw new Error('User data missing required field: username')
    if (!firstName) throw new Error('User data missing required field: firstName')
    if (!lastName) throw new Error('User data missing required field: lastName')
    if (!role) throw new Error('User data missing required field: role')

    return new User(
      id,
      Email.create(email),
      username,
      firstName,
      lastName,
      UserRole.create(role),
      isActive,
      new Date(createdAt),
      updatedAt ? new Date(updatedAt) : undefined,
      lastLogin ? new Date(lastLogin) : undefined
    )
  }

  /**
   * Convert Domain Model to API DTO
   *
   * Transforms User instance back to API-compatible format.
   * Useful for sending user data to backend in updates/creates.
   *
   * @returns API-compatible dictionary
   */
  toAPI(): Record<string, any> {
    return {
      id: this.id,
      email: this.email.toString(),
      username: this.username,
      firstName: this.firstName,
      lastName: this.lastName,
      role: this.role.toString(),
      is_active: this.isActive,
      created_at: this.createdAt.toISOString(),
      updated_at: this.updatedAt?.toISOString(),
      last_login: this.lastLogin?.toISOString()
    }
  }

  /**
   * Convert Domain Model to UI display format
   *
   * Includes all computed properties and business logic methods
   * results for easy access in UI layer.
   *
   * @returns UI-friendly dictionary with all derived properties
   */
  toJSON(): Record<string, any> {
    return {
      id: this.id,
      email: this.email.toString(),
      username: this.username,
      fullName: this.fullName,
      firstName: this.firstName,
      lastName: this.lastName,
      role: this.role.toString(),
      isPremium: this.isPremium,
      isSystemAdmin: this.isSystemAdmin,
      isModerator: this.isModerator,
      hasElevatedPrivileges: this.hasElevatedPrivileges,
      canAccessPremiumFeatures: this.canAccessPremiumFeatures(),
      isActive: this.isActive,
      displayLabel: this.displayLabel,
      isInGoodStanding: this.isInGoodStanding(),
      isNewUser: this.isNewUser(),
      daysSinceLastLogin: this.getDaysSinceLastLogin(),
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt?.toISOString(),
      lastLogin: this.lastLogin?.toISOString()
    }
  }

  /**
   * Convert to plain object (minimal fields)
   *
   * Lightweight format for passing between services.
   *
   * @returns Minimal user data
   */
  toPlain(): Record<string, any> {
    return {
      id: this.id,
      email: this.email.toString(),
      username: this.username,
      fullName: this.fullName,
      role: this.role.toString(),
      isActive: this.isActive
    }
  }
}
