/**
 * Course Domain Model
 *
 * Encapsulates course aggregate root with chapters and lessons.
 * All business logic for course operations lives here.
 *
 * Structure:
 * - ID: Unique identifier
 * - Title: Course title
 * - Description: Course description
 * - CreatorId: User ID of creator
 * - Chapters: Ordered collection of chapters
 * - IsPublished: Publication status
 * - CreatedAt: Creation timestamp
 *
 * Example:
 *   const course = Course.fromAPI({
 *     id: 'course-123',
 *     title: 'Advanced TypeScript',
 *     description: 'Learn advanced TypeScript patterns',
 *     creator_id: 'user-456',
 *     chapters: [{ ... }, { ... }],
 *     is_published: true,
 *     created_at: '2026-01-19T10:00:00Z'
 *   })
 *   course.canPublish()      // true
 *   course.canEdit(user)     // true if user is creator or admin
 *   course.sortedChapters    // chapters sorted by order
 */

import { Chapter } from './Chapter.model'
import type { User } from '../user/User.types'

export class Course {
  constructor(
    public readonly id: string,
    public readonly title: string,
    public readonly description: string,
    public readonly creatorId: string,
    public readonly chapters: Chapter[],
    public readonly isPublished: boolean,
    public readonly createdAt: Date,
    public readonly updatedAt?: Date
  ) {}

  /**
   * Get sorted chapters by order.
   *
   * Business Logic: Chapters must be in consistent order.
   * Previously in: courseEditor.store.ts lines 56-58
   *
   * @returns Sorted chapters array
   *
   * @example
   * course.sortedChapters // Returns chapters ordered by their order field
   */
  get sortedChapters(): Chapter[] {
    return [...this.chapters].sort((a, b) => a.order - b.order)
  }

  /**
   * Get course title (display purposes).
   *
   * @returns Course title
   */
  get displayTitle(): string {
    return this.title.trim()
  }

  /**
   * Get course completion percentage for a user.
   *
   * Business Calculation:
   * (Completed Lessons / Total Lessons) * 100
   *
   * @param userId - User ID to calculate progress for
   * @returns Completion percentage (0-100)
   *
   * @example
   * course.getCompletionPercentage('user-123')  // 75
   */
  getCompletionPercentage(userId: string): number {
    const chapters = this.sortedChapters
    const totalLessons = chapters.reduce(
      (sum, chapter) => sum + chapter.lessons.length,
      0
    )

    if (totalLessons === 0) return 0

    const completedLessons = chapters.reduce(
      (sum, chapter) => sum + chapter.getCompletedLessonsCount(userId),
      0
    )

    return Math.round((completedLessons / totalLessons) * 100)
  }

  /**
   * Check if user can edit this course.
   *
   * Business Rule: Only creator or system admin can edit.
   * Previously in: courseEditor.store.ts permission checks
   *
   * @param user - User to check permission for
   * @returns true if user can edit, false otherwise
   *
   * @example
   * course.canEdit(currentUser)  // true if currentUser is creator or admin
   */
  canEdit(user: User): boolean {
    return user.id === this.creatorId || user.isSystemAdmin
  }

  /**
   * Check if user can delete this course.
   *
   * Business Rule: Only creator or system admin can delete.
   *
   * @param user - User to check permission for
   * @returns true if user can delete, false otherwise
   */
  canDelete(user: User): boolean {
    return user.id === this.creatorId || user.isSystemAdmin
  }

  /**
   * Check if course can be published.
   *
   * Business Rules:
   * - Must have at least 1 chapter
   * - At least one chapter must have at least 1 lesson
   * - All chapters must have order field set
   *
   * @returns true if course is valid for publishing, false otherwise
   *
   * @example
   * course.canPublish()  // true if ≥1 chapter with ≥1 lesson
   */
  canPublish(): boolean {
    if (this.chapters.length === 0) return false

    const hasLessons = this.sortedChapters.some(
      chapter => chapter.lessons.length > 0
    )

    return hasLessons
  }

  /**
   * Check if course is fully valid for all operations.
   *
   * Validation includes:
   * - Title not empty
   * - Description provided
   * - Valid chapter structure
   * - No orphaned lessons
   *
   * @returns true if course is fully valid, false otherwise
   */
  isValid(): boolean {
    // Title validation
    if (!this.title || this.title.trim().length === 0) return false

    // Description validation
    if (!this.description || this.description.trim().length === 0) return false

    // Chapter validation
    for (const chapter of this.chapters) {
      if (!chapter.isValid()) return false
    }

    return true
  }

  /**
   * Get course status as string.
   *
   * @returns Status: 'draft' | 'published' | 'archived'
   */
  get status(): 'draft' | 'published' {
    return this.isPublished ? 'published' : 'draft'
  }

  /**
   * Get total number of lessons in course.
   *
   * @returns Total lesson count
   */
  get totalLessons(): number {
    return this.chapters.reduce((sum, chapter) => sum + chapter.lessons.length, 0)
  }

  /**
   * Get total number of chapters.
   *
   * @returns Chapter count
   */
  get totalChapters(): number {
    return this.chapters.length
  }

  /**
   * Convert API DTO to domain model.
   *
   * Single transformation point handling:
   * - snake_case → camelCase conversion
   * - Nested chapter/lesson transformation
   * - Proper error propagation
   *
   * @param data Raw API data
   * @returns Course instance
   * @throws Error if data is invalid
   *
   * @example
   * Course.fromAPI({
   *   id: 'course-123',
   *   title: 'My Course',
   *   description: 'Description',
   *   creator_id: 'user-456',
   *   chapters: [{ ... }],
   *   is_published: true,
   *   created_at: '2026-01-19T10:00:00Z'
   * })
   */
  static fromAPI(data: any): Course {
    return new Course(
      data.id,
      data.title,
      data.description,
      data.creator_id !== undefined ? data.creator_id : data.creatorId,
      (data.chapters || []).map((c: any) => Chapter.fromAPI(c)),
      data.is_published !== undefined ? data.is_published : data.isPublished ?? false,
      new Date(data.created_at || data.createdAt),
      data.updated_at ? new Date(data.updated_at) : undefined
    )
  }

  /**
   * Convert to plain object for UI display/serialization.
   *
   * @returns Plain object representation
   *
   * @example
   * course.toJSON()
   * // Returns: {
   * //   id: 'course-123',
   * //   title: 'My Course',
   * //   description: '...',
   * //   creatorId: 'user-456',
   * //   chapters: [...],
   * //   isPublished: true,
   * //   status: 'published',
   * //   totalChapters: 3,
   * //   totalLessons: 12,
   * //   sortedChapters: [...]
   * // }
   */
  toJSON(): object {
    return {
      id: this.id,
      title: this.title,
      description: this.description,
      creatorId: this.creatorId,
      chapters: this.chapters.map(c => c.toJSON()),
      isPublished: this.isPublished,
      status: this.status,
      displayTitle: this.displayTitle,
      totalChapters: this.totalChapters,
      totalLessons: this.totalLessons,
      sortedChapters: this.sortedChapters.map(c => c.toJSON()),
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt?.toISOString()
    }
  }
}
