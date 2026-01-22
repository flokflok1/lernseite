/**
 * Email Value Object
 *
 * Ensures email validity and immutability.
 * Single responsibility: Email validation and normalization
 *
 * Usage:
 *   const email = Email.create('test@example.com')
 *   console.log(email.toString()) // 'test@example.com'
 */

export class Email {
  private constructor(private readonly value: string) {}

  /**
   * Create Email value object from string or existing Email instance
   *
   * @param email - Email address to validate or existing Email instance
   * @returns Email instance
   * @throws Error if email format is invalid
   *
   * @example
   * const email = Email.create('user@example.com')
   * const sameEmail = Email.create(email) // Returns same instance
   * // Throws: Error('Invalid email format: invalid')
   * Email.create('invalid')
   */
  static create(email: string | Email): Email {
    // Defensive: If already an Email instance, return it (idempotent)
    // This handles edge cases where Email objects are passed due to:
    // - localStorage round-trip (JSON.stringify/parse of objects with value objects)
    // - Double-transformation in composed domain models
    if (email instanceof Email) {
      return email
    }

    // Type guard: ensure email is a string
    if (typeof email !== 'string') {
      console.error('[Email.create] Invalid email type. Received:', {
        type: typeof email,
        value: email,
        isObject: email !== null && typeof email === 'object',
        keys: email !== null && typeof email === 'object' ? Object.keys(email) : null
      })
      throw new Error(
        `Invalid email type: expected string, got ${typeof email}. Value: ${JSON.stringify(email)}`
      )
    }

    const trimmed = email.trim().toLowerCase()

    if (!this.isValid(trimmed)) {
      throw new Error(`Invalid email format: ${email}`)
    }

    return new Email(trimmed)
  }

  /**
   * Validate email format using regex
   *
   * Pattern explanation:
   * ^[^\s@]+ - Start: one or more non-whitespace, non-@ characters
   * @ - Literal @ symbol
   * [^\s@]+ - One or more non-whitespace, non-@ characters (domain)
   * \. - Literal dot
   * [^\s@]+$ - One or more non-whitespace, non-@ characters (TLD) until end
   *
   * @private
   * @param email - Email to validate
   * @returns true if valid, false otherwise
   */
  private static isValid(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  /**
   * Get email string value
   *
   * @returns Email address
   */
  toString(): string {
    return this.value
  }

  /**
   * Get email for JSON serialization
   *
   * @returns Email address
   */
  toJSON(): string {
    return this.value
  }

  /**
   * Check equality with another Email
   *
   * @param other - Email to compare
   * @returns true if emails are equal (case-insensitive comparison)
   */
  equals(other: Email): boolean {
    return this.value === other.value
  }

  /**
   * Get email value (internal use only)
   *
   * @private
   * @returns Email address
   */
  get rawValue(): string {
    return this.value
  }
}
