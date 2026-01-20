/**
 * User Factory
 *
 * Handles complex user creation with validation and defaults.
 * Factory Pattern from Domain-Driven Design (DDD).
 *
 * Encapsulates creation logic:
 * - Default value setting
 * - Business rule validation
 * - Complex initialization workflows
 *
 * Pattern reference: backend AIModelFactory.createFromProviderSync()
 *
 * Usage:
 *   // Create new user with defaults
 *   const newUser = UserFactory.createNew({
 *     email: 'john@example.com',
 *     username: 'johndoe',
 *     firstName: 'John',
 *     lastName: 'Doe'
 *   })
 *
 *   // Create from registration with validation
 *   const user = UserFactory.createFromRegistration(formData)
 *
 *   // Upgrade existing user to premium
 *   const premiumUser = UserFactory.upgradeToPremium(user)
 */

import { User } from './User.model'
import { Email } from '@/domain/value-objects/Email.vo'
import { UserRole, UserRoleEnum } from './UserRole.vo'

export interface UserCreationData {
  email: string
  username: string
  firstName: string
  lastName: string
}

export interface UserRegistrationData extends UserCreationData {
  password: string
  confirmPassword?: string
}

export class UserFactory {
  /**
   * Create new user with defaults
   *
   * Business Rules:
   * 1. New users start as Free role (no premium access)
   * 2. New users are active by default
   * 3. createdAt is set to now
   *
   * @param data - User creation data (email, username, firstName, lastName)
   * @returns New User instance with default values
   * @throws Error if data is invalid
   *
   * @example
   * const user = UserFactory.createNew({
   *   email: 'john@example.com',
   *   username: 'johndoe',
   *   firstName: 'John',
   *   lastName: 'Doe'
   * })
   * // Returns User with:
   * // - role: FREE
   * // - isActive: true
   * // - createdAt: now
   * // - id: generated UUID
   */
  static createNew(data: UserCreationData): User {
    // Validate input
    if (!data) {
      throw new Error('User creation data is required')
    }

    const { email, username, firstName, lastName } = data

    if (!email?.trim()) {
      throw new Error('Email is required')
    }

    if (!username?.trim()) {
      throw new Error('Username is required')
    }

    if (!firstName?.trim()) {
      throw new Error('First name is required')
    }

    if (!lastName?.trim()) {
      throw new Error('Last name is required')
    }

    // Generate unique ID (UUIDv4)
    const id = crypto.randomUUID()

    // Create user with defaults
    return new User(
      id,
      Email.create(email),
      username.trim(),
      firstName.trim(),
      lastName.trim(),
      UserRole.create(UserRoleEnum.FREE), // Default role
      true, // Active by default
      new Date() // Created now
    )
  }

  /**
   * Create user from registration form
   *
   * Validates registration data including:
   * - Password strength (min 8 characters)
   * - Username length (min 3 characters)
   * - Name fields present (cannot be empty)
   * - Password confirmation match
   *
   * Business Rule: Validates input before creation.
   *
   * @param data - Registration form data including password
   * @returns New User instance
   * @throws Error if validation fails
   *
   * @example
   * const user = UserFactory.createFromRegistration({
   *   email: 'john@example.com',
   *   username: 'johndoe',
   *   firstName: 'John',
   *   lastName: 'Doe',
   *   password: 'SecurePass123!',
   *   confirmPassword: 'SecurePass123!'
   * })
   * // Validates all fields before creating user
   */
  static createFromRegistration(data: UserRegistrationData): User {
    // Validate basic user data
    const basicValidation = this.validateBasicUserData(data)
    if (basicValidation) {
      throw new Error(basicValidation)
    }

    // Validate password
    const passwordValidation = this.validatePassword(data.password)
    if (passwordValidation) {
      throw new Error(passwordValidation)
    }

    // Validate password confirmation
    if (data.confirmPassword && data.confirmPassword !== data.password) {
      throw new Error('Passwords do not match')
    }

    // Create user with validated data
    return this.createNew(data)
  }

  /**
   * Upgrade user to premium
   *
   * Business Rules:
   * 1. User must be active (cannot upgrade suspended accounts)
   * 2. User must be on Free tier (cannot re-upgrade premium users)
   * 3. Preserves all user data except role
   * 4. Updates timestamp to reflect upgrade
   *
   * @param user - User to upgrade
   * @returns New User instance with Premium role
   * @throws Error if user cannot be upgraded
   *
   * @example
   * try {
   *   const premiumUser = UserFactory.upgradeToPremium(user)
   *   console.log(premiumUser.role.toString()) // 'Premium'
   * } catch (e) {
   *   console.error(e.message)
   *   // Error: Cannot upgrade inactive user
   *   // Error: User is already premium
   * }
   */
  static upgradeToPremium(user: User): User {
    // Check if user is active
    if (!user.isActive) {
      throw new Error('Cannot upgrade inactive user (account must be active)')
    }

    // Check if user is already premium
    if (user.isPremium) {
      throw new Error('User is already premium (cannot re-upgrade)')
    }

    // Check if user is Free tier
    const freeRole = UserRole.create(UserRoleEnum.FREE)
    if (!user.role.equals(freeRole)) {
      throw new Error('Only Free tier users can be upgraded to Premium')
    }

    // Create new user with Premium role, preserving all other data
    return new User(
      user.id,
      user.email,
      user.username,
      user.firstName,
      user.lastName,
      UserRole.create(UserRoleEnum.PREMIUM),
      user.isActive,
      user.createdAt,
      new Date(), // Updated now
      user.lastLogin
    )
  }

  /**
   * Downgrade user from premium to free
   *
   * Business Rules:
   * 1. User must currently be premium tier
   * 2. Admin override flag can force downgrade
   * 3. Typically done when subscription expires
   *
   * @param user - User to downgrade
   * @param reason - Reason for downgrade (subscription expired, etc)
   * @returns New User instance with Free role
   * @throws Error if user cannot be downgraded
   */
  static downgradeToPremium(user: User, reason?: string): User {
    // Check if user is currently premium
    if (!user.isPremium) {
      throw new Error('User is not premium (cannot downgrade non-premium user)')
    }

    // Create new user with Free role
    return new User(
      user.id,
      user.email,
      user.username,
      user.firstName,
      user.lastName,
      UserRole.create(UserRoleEnum.FREE),
      user.isActive,
      user.createdAt,
      new Date(), // Updated now
      user.lastLogin
    )
  }

  /**
   * Activate suspended user account
   *
   * Business Rule: Re-activates an inactive user account.
   *
   * @param user - Inactive user to activate
   * @returns User instance with isActive = true
   * @throws Error if user is already active
   */
  static activateUser(user: User): User {
    if (user.isActive) {
      throw new Error('User is already active (cannot re-activate active user)')
    }

    return new User(
      user.id,
      user.email,
      user.username,
      user.firstName,
      user.lastName,
      user.role,
      true, // Activate
      user.createdAt,
      new Date(), // Updated now
      user.lastLogin
    )
  }

  /**
   * Deactivate (suspend) user account
   *
   * Business Rule: Deactivates user account (soft delete, data preserved).
   *
   * @param user - Active user to deactivate
   * @returns User instance with isActive = false
   * @throws Error if user is already inactive
   */
  static deactivateUser(user: User): User {
    if (!user.isActive) {
      throw new Error('User is already inactive (cannot re-deactivate)')
    }

    return new User(
      user.id,
      user.email,
      user.username,
      user.firstName,
      user.lastName,
      user.role,
      false, // Deactivate
      user.createdAt,
      new Date(), // Updated now
      user.lastLogin
    )
  }

  /**
   * Update user last login timestamp
   *
   * Called when user logs in successfully.
   *
   * @param user - User that logged in
   * @returns User instance with updated lastLogin timestamp
   */
  static recordLogin(user: User): User {
    return new User(
      user.id,
      user.email,
      user.username,
      user.firstName,
      user.lastName,
      user.role,
      user.isActive,
      user.createdAt,
      user.updatedAt,
      new Date() // Update login time
    )
  }

  /**
   * Change user email
   *
   * Creates new User instance with updated email.
   * Email is validated through Email value object.
   *
   * @param user - User to update
   * @param newEmail - New email address
   * @returns User instance with updated email
   * @throws Error if email is invalid
   */
  static changeEmail(user: User, newEmail: string): User {
    return new User(
      user.id,
      Email.create(newEmail), // Validates email
      user.username,
      user.firstName,
      user.lastName,
      user.role,
      user.isActive,
      user.createdAt,
      new Date(), // Updated now
      user.lastLogin
    )
  }

  /**
   * Change user role
   *
   * Admin operation to change user role.
   * Creates new User instance with updated role.
   *
   * @param user - User to update
   * @param newRole - New role (as string or UserRoleEnum)
   * @returns User instance with updated role
   * @throws Error if role is invalid
   */
  static changeRole(user: User, newRole: string | UserRoleEnum): User {
    return new User(
      user.id,
      user.email,
      user.username,
      user.firstName,
      user.lastName,
      UserRole.create(newRole as string),
      user.isActive,
      user.createdAt,
      new Date(), // Updated now
      user.lastLogin
    )
  }

  // ===================================
  // VALIDATION HELPERS
  // ===================================

  /**
   * Validate basic user data fields
   *
   * @private
   * @param data - User data to validate
   * @returns Error message if invalid, undefined if valid
   */
  private static validateBasicUserData(data: any): string | undefined {
    if (!data) {
      return 'User data is required'
    }

    if (!data.email?.trim()) {
      return 'Email is required'
    }

    if (!data.username?.trim()) {
      return 'Username is required'
    }

    if (data.username.trim().length < 3) {
      return 'Username must be at least 3 characters'
    }

    if (!data.firstName?.trim()) {
      return 'First name is required'
    }

    if (!data.lastName?.trim()) {
      return 'Last name is required'
    }

    // Will be validated by Email value object
    if (!data.email.includes('@')) {
      return 'Invalid email format'
    }

    return undefined
  }

  /**
   * Validate password strength
   *
   * Business Rules:
   * 1. Min 8 characters
   * 2. At least 1 uppercase letter
   * 3. At least 1 lowercase letter
   * 4. At least 1 number
   *
   * @private
   * @param password - Password to validate
   * @returns Error message if invalid, undefined if valid
   */
  private static validatePassword(password: string): string | undefined {
    if (!password) {
      return 'Password is required'
    }

    if (password.length < 8) {
      return 'Password must be at least 8 characters'
    }

    if (!/[A-Z]/.test(password)) {
      return 'Password must contain at least 1 uppercase letter'
    }

    if (!/[a-z]/.test(password)) {
      return 'Password must contain at least 1 lowercase letter'
    }

    if (!/\d/.test(password)) {
      return 'Password must contain at least 1 number'
    }

    return undefined
  }
}
