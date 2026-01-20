/**
 * MethodType Value Object
 *
 * Encapsulates learning method type constraint and classification.
 * Single responsibility: Validate method_type range (0-11) and provide group classification
 *
 * Valid ranges (LM00-LM11):
 * - Group A (Erklärend): LM00-LM04 (0-4) - Explanation/Theory
 * - Group B (Praxis): LM05-LM08 (5-8) - Practice/Exercises
 * - Group C (Prüfung): LM09-LM11 (9-11) - Assessment/Exams
 *
 * CRITICAL CONSTRAINT: method_type must be 0-11 inclusive
 * - method_type < 0 → INVALID (negative)
 * - method_type > 11 → INVALID (LM12-LM32 are system features, not content LMs)
 * - method_type 0-11 → VALID (LM00-LM11 content learning methods)
 *
 * Usage:
 *   const method = MethodType.create(5)
 *   console.log(method.getGroup())     // 'B'
 *   console.log(method.getGroupName()) // 'Praxis'
 *   console.log(method.toString())     // 'LM05'
 */

export class MethodType {
  private constructor(private readonly value: number) {}

  /**
   * Create MethodType value object from number.
   *
   * @param methodType - Method type ID (0-11)
   * @returns MethodType instance
   * @throws Error if methodType < 0 or > 11
   *
   * @example
   * const method = MethodType.create(0)    // LM00
   * const method = MethodType.create(11)   // LM11
   * MethodType.create(-1)   // Throws: Invalid method type: -1
   * MethodType.create(12)   // Throws: Invalid method type: 12
   */
  static create(methodType: number): MethodType {
    if (methodType < 0 || methodType > 11) {
      throw new Error(`Invalid method type: ${methodType}. Must be 0-11 (LM00-LM11)`)
    }

    return new MethodType(methodType)
  }

  /**
   * Get method group (A, B, C).
   *
   * Business Rule Mapping:
   * - Group A (Erklärend): 0-4 (5 methods) - Explanation focus
   * - Group B (Praxis): 5-8 (4 methods) - Practice focus
   * - Group C (Prüfung): 9-11 (3 methods) - Assessment focus
   *
   * @returns Group identifier ('A', 'B', or 'C')
   *
   * @example
   * MethodType.create(0).getGroup()  // 'A' (LM00)
   * MethodType.create(5).getGroup()  // 'B' (LM05)
   * MethodType.create(11).getGroup() // 'C' (LM11)
   */
  getGroup(): 'A' | 'B' | 'C' {
    if (this.value >= 0 && this.value <= 4) return 'A'
    if (this.value >= 5 && this.value <= 8) return 'B'
    return 'C' // 9-11
  }

  /**
   * Get group display name (German).
   *
   * @returns Group name ('Erklärend', 'Praxis', or 'Prüfung')
   *
   * @example
   * MethodType.create(2).getGroupName()  // 'Erklärend' (Group A)
   * MethodType.create(6).getGroupName()  // 'Praxis' (Group B)
   * MethodType.create(10).getGroupName() // 'Prüfung' (Group C)
   */
  getGroupName(): string {
    const groups: Record<'A' | 'B' | 'C', string> = {
      'A': 'Erklärend',
      'B': 'Praxis',
      'C': 'Prüfung'
    }
    return groups[this.getGroup()]
  }

  /**
   * Get method type as zero-padded string (LM00-LM11).
   *
   * @returns String representation with zero-padding
   *
   * @example
   * MethodType.create(0).toString()   // 'LM00'
   * MethodType.create(5).toString()   // 'LM05'
   * MethodType.create(11).toString()  // 'LM11'
   */
  toString(): string {
    return `LM${this.value.toString().padStart(2, '0')}`
  }

  /**
   * Get method type as numeric value.
   *
   * @returns Original numeric value (0-11)
   *
   * @example
   * MethodType.create(5).toNumber() // 5
   */
  toNumber(): number {
    return this.value
  }

  /**
   * Check equality with another MethodType.
   *
   * @param other - MethodType to compare
   * @returns true if both represent same method type
   *
   * @example
   * MethodType.create(5).equals(MethodType.create(5))  // true
   * MethodType.create(5).equals(MethodType.create(6))  // false
   */
  equals(other: MethodType): boolean {
    return this.value === other.value
  }

  /**
   * Get raw numeric value (for advanced use cases).
   *
   * @internal
   * @returns Numeric value
   */
  get rawValue(): number {
    return this.value
  }
}
