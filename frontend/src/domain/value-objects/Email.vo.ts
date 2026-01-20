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
   * Create Email value object from string
   *
   * @param email - Email address to validate
   * @returns Email instance
   * @throws Error if email format is invalid
   *
   * @example
   * const email = Email.create('user@example.com')
   * // Throws: Error('Invalid email format: invalid')
   * Email.create('invalid')
   */
  static create(email: string): Email {
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
