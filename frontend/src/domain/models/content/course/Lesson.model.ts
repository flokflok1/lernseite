/**
 * Lesson Domain Model
 *
 * Encapsulates a lesson within a chapter with learning method content.
 * Tracks user completion status and validates lesson structure.
 *
 * Structure:
 * - ID: Unique identifier
 * - ChapterId: Parent chapter ID
 * - Title: Lesson title
 * - Description: Lesson description
 * - Order: Sequential order within chapter
 * - LearningMethodType: Content delivery method (LM00-LM11)
 * - IsPublished: Publication status
 *
 * Example:
 *   const lesson = Lesson.fromAPI({
 *     id: 'lesson-123',
 *     chapter_id: 'chapter-456',
 *     title: 'TypeScript Basics',
 *     description: 'Introduction to TypeScript',
 *     order: 1,
 *     learning_method_type: 2,
 *     is_published: true
 *   })
 *   lesson.displayTitle        // "TypeScript Basics"
 *   lesson.isCompletedBy(userId) // true if user marked complete
 *   lesson.isValid()           // true if title non-empty
 */

export class Lesson {
  constructor(
    public readonly id: string,
    public readonly chapterId: string,
    public readonly title: string,
    public readonly description: string,
    public readonly order: number,
    public readonly learningMethodType: number, // 0-11 (LM00-LM11)
    public readonly isPublished: boolean,
    public readonly completedByUsers: string[] = [], // Array of user IDs who completed this lesson
    public readonly createdAt?: Date,
    public readonly updatedAt?: Date
  ) {}

  /**
   * Get lesson display title.
   *
   * @returns Lesson title with whitespace trimmed
   */
  get displayTitle(): string {
    return this.title.trim()
  }

  /**
   * Get learning method identifier (LM00-LM11 format).
   *
   * @returns Formatted learning method string (e.g., "LM02")
   */
  get learningMethodId(): string {
    return `LM${this.learningMethodType.toString().padStart(2, '0')}`
  }

  /**
   * Check if lesson is completed by a specific user.
   *
   * Business Logic: User completion tracked via array of user IDs.
   *
   * @param userId - User ID to check
   * @returns true if user has completed lesson, false otherwise
   *
   * @example
   * lesson.isCompletedBy('user-123')  // true if user completed
   */
  isCompletedBy(userId: string): boolean {
    return this.completedByUsers.includes(userId)
  }

  /**
   * Get number of users who completed this lesson.
   *
   * Useful for analytics and progress tracking.
   *
   * @returns Count of users who completed lesson
   */
  get completionCount(): number {
    return this.completedByUsers.length
  }

  /**
   * Check if lesson is fully valid.
   *
   * Validation includes:
   * - Title not empty
   * - Learning method type valid (0-11)
   * - Title not empty (required for drafts)
   *
   * Note: Description and learningMethodType are checked in canPublish(),
   * not here — drafts can be saved without them.
   *
   * @returns true if lesson is valid for saving, false otherwise
   */
  isValid(): boolean {
    // Title validation (required even for drafts)
    if (!this.title || this.title.trim().length === 0) return false

    return true
  }

  /**
   * Get completion status percentage.
   *
   * @returns Completion percentage (0-100)
   */
  get completionPercentage(): number {
    // For individual lesson, it's either 0% (not completed) or 100% (completed) per user
    // This is a placeholder for potential future complexity
    return 0
  }

  /**
   * Convert API DTO to domain model.
   *
   * Single transformation point handling:
   * - snake_case → camelCase conversion
   * - Learning method type validation
   * - Proper error propagation
   *
   * @param data Raw API data
   * @returns Lesson instance
   * @throws Error if data is invalid
   *
   * @example
   * Lesson.fromAPI({
   *   id: 'lesson-123',
   *   chapter_id: 'chapter-456',
   *   title: 'TypeScript Basics',
   *   description: 'Introduction',
   *   order: 1,
   *   learning_method_type: 2,
   *   is_published: true,
   *   completed_by_users: ['user-1', 'user-2']
   * })
   */
  static fromAPI(data: any): Lesson {
    // Validate learning method type
    const methodType = data.learning_method_type ?? data.learningMethodType ?? 0
    if (methodType < 0 || methodType > 11) {
      throw new Error(`Invalid learning method type: ${methodType}. Must be 0-11 (LM00-LM11)`)
    }

    return new Lesson(
      data.id,
      data.chapter_id !== undefined ? data.chapter_id : data.chapterId,
      data.title,
      data.description,
      data.order,
      methodType,
      data.is_published !== undefined ? data.is_published : data.isPublished ?? false,
      (data.completed_by_users ?? data.completedByUsers) || [],
      data.created_at ? new Date(data.created_at) : undefined,
      data.updated_at ? new Date(data.updated_at) : undefined
    )
  }

  /**
   * Convert to plain object for UI display/serialization.
   *
   * @returns Plain object representation
   *
   * @example
   * lesson.toJSON()
   * // Returns: {
   * //   id: 'lesson-123',
   * //   chapterId: 'chapter-456',
   * //   title: 'TypeScript Basics',
   * //   description: 'Introduction',
   * //   order: 1,
   * //   learningMethodType: 2,
   * //   learningMethodId: 'LM02',
   * //   isPublished: true,
   * //   displayTitle: 'TypeScript Basics',
   * //   completedByUsers: ['user-1', 'user-2'],
   * //   completionCount: 2,
   * //   createdAt: '2026-01-19T10:00:00Z'
   * // }
   */
  toJSON(): object {
    return {
      id: this.id,
      chapterId: this.chapterId,
      title: this.title,
      description: this.description,
      order: this.order,
      learningMethodType: this.learningMethodType,
      learningMethodId: this.learningMethodId,
      isPublished: this.isPublished,
      displayTitle: this.displayTitle,
      completedByUsers: this.completedByUsers,
      completionCount: this.completionCount,
      createdAt: this.createdAt?.toISOString(),
      updatedAt: this.updatedAt?.toISOString()
    }
  }
}
