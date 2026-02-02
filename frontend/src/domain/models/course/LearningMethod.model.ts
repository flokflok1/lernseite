/**
 * LearningMethod Domain Model
 *
 * Encapsulates a learning method with type classification and metadata.
 * Delegates type classification to MethodType value object for constraint enforcement.
 *
 * Structure:
 * - ID: Unique identifier
 * - MethodType: Value object enforcing 0-11 constraint (LM00-LM11)
 * - Name: Display name
 * - Description: Method description
 * - Icon: UI icon identifier
 *
 * Example:
 *   const method = LearningMethod.fromAPI({
 *     id: 'lm-05',
 *     method_type: 5,
 *     name: 'Interactive Math',
 *     description: 'Math exercises with interactive feedback',
 *     icon: 'calculate'
 *   })
 *   method.group          // 'B' (Praxis)
 *   method.isPractice()   // true
 *   method.displayName    // 'LM05: Interactive Math'
 */

import { MethodType } from './MethodType.vo'

export class LearningMethod {
  constructor(
    public readonly id: string,
    public readonly methodType: MethodType,
    public readonly name: string,
    public readonly description: string,
    public readonly icon: string
  ) {}

  /**
   * Display name combining method type and name.
   *
   * @returns Formatted string like "LM05: Interactive Math"
   *
   * @example
   * LearningMethod.fromAPI({ method_type: 5, name: 'Interactive Math', ... }).displayName
   * // Returns: "LM05: Interactive Math"
   */
  get displayName(): string {
    return `${this.methodType.toString()}: ${this.name}`
  }

  /**
   * Get method group (A, B, or C).
   *
   * Delegates to MethodType value object to enforce constraint.
   *
   * @returns Group identifier ('A' | 'B' | 'C')
   *
   * @example
   * method.group  // 'B' for method_type 5-8
   */
  get group(): 'A' | 'B' | 'C' {
    return this.methodType.getGroup()
  }

  /**
   * Get group display name (German).
   *
   * @returns Group name ('Erklärend' | 'Praxis' | 'Prüfung')
   *
   * @example
   * method.groupName  // 'Praxis' for Group B
   */
  get groupName(): string {
    return this.methodType.getGroupName()
  }

  /**
   * Check if this is an explanation method (Group A).
   *
   * Business Classification: Group A represents explanation/theory methods.
   *
   * @returns true if group is 'A', false otherwise
   *
   * @example
   * LearningMethod.fromAPI({ method_type: 2, ... }).isExplanation()  // true
   * LearningMethod.fromAPI({ method_type: 5, ... }).isExplanation()  // false
   */
  isExplanation(): boolean {
    return this.group === 'A'
  }

  /**
   * Check if this is a practice method (Group B).
   *
   * Business Classification: Group B represents practice/exercises methods.
   *
   * @returns true if group is 'B', false otherwise
   *
   * @example
   * LearningMethod.fromAPI({ method_type: 6, ... }).isPractice()  // true
   * LearningMethod.fromAPI({ method_type: 2, ... }).isPractice()  // false
   */
  isPractice(): boolean {
    return this.group === 'B'
  }

  /**
   * Check if this is an assessment method (Group C).
   *
   * Business Classification: Group C represents assessment/exam methods.
   *
   * @returns true if group is 'C', false otherwise
   *
   * @example
   * LearningMethod.fromAPI({ method_type: 10, ... }).isAssessment()  // true
   * LearningMethod.fromAPI({ method_type: 5, ... }).isAssessment()   // false
   */
  isAssessment(): boolean {
    return this.group === 'C'
  }

  /**
   * Convert API DTO to domain model.
   *
   * Single transformation point handling:
   * - snake_case → camelCase conversion
   * - MethodType creation with validation
   * - Proper error propagation
   *
   * @param data Raw API data
   * @returns LearningMethod instance
   * @throws Error if method_type is invalid (not 0-11)
   *
   * @example
   * LearningMethod.fromAPI({
   *   id: 'lm-06',
   *   method_type: 6,
   *   name: 'Flashcards',
   *   description: 'Flash card learning system',
   *   icon: 'style'
   * })
   */
  static fromAPI(data: any): LearningMethod {
    return new LearningMethod(
      data.id,
      // Handle both snake_case (API) and camelCase (internal)
      MethodType.create(data.method_type !== undefined ? data.method_type : data.methodType),
      data.name,
      data.description,
      data.icon
    )
  }

  /**
   * Create from MethodType value object directly.
   *
   * Useful for tests and when you already have a validated MethodType.
   *
   * @param methodType MethodType value object
   * @param id Optional ID (auto-generated if not provided)
   * @param name Optional name (defaults to method type string)
   * @returns LearningMethod instance
   *
   * @example
   * const methodType = MethodType.create(5)
   * LearningMethod.fromMethodType(methodType, 'lm-05', 'Interactive Math')
   */
  static fromMethodType(
    methodType: MethodType,
    id?: string,
    name?: string,
    description?: string,
    icon?: string
  ): LearningMethod {
    return new LearningMethod(
      id || `lm-${methodType.toNumber().toString().padStart(2, '0')}`,
      methodType,
      name || methodType.toString(),
      description || `Learning method ${methodType.toString()}`,
      icon || 'school'
    )
  }

  /**
   * Convert to plain object for UI display/serialization.
   *
   * @returns Plain object representation
   *
   * @example
   * method.toJSON()
   * // Returns: {
   * //   id: 'lm-05',
   * //   methodType: 5,
   * //   name: 'Interactive Math',
   * //   description: 'Math exercises...',
   * //   icon: 'calculate',
   * //   displayName: 'LM05: Interactive Math',
   * //   group: 'B',
   * //   groupName: 'Praxis',
   * //   isExplanation: false,
   * //   isPractice: true,
   * //   isAssessment: false
   * // }
   */
  toJSON(): object {
    return {
      id: this.id,
      methodType: this.methodType.toNumber(),
      name: this.name,
      description: this.description,
      icon: this.icon,
      displayName: this.displayName,
      group: this.group,
      groupName: this.groupName,
      isExplanation: this.isExplanation(),
      isPractice: this.isPractice(),
      isAssessment: this.isAssessment()
    }
  }
}
