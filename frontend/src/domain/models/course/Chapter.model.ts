/**
 * Chapter Domain Model
 *
 * Encapsulates a chapter within a course with lessons.
 * Delegates lesson management to Lesson entities.
 *
 * Structure:
 * - ID: Unique identifier
 * - CourseId: Parent course ID
 * - Title: Chapter title
 * - Order: Sequential order within course
 * - Lessons: Ordered collection of lessons
 *
 * Example:
 *   const chapter = Chapter.fromAPI({
 *     id: 'chapter-123',
 *     course_id: 'course-456',
 *     title: 'Introduction to TypeScript',
 *     order: 1,
 *     lessons: [{ ... }, { ... }]
 *   })
 *   chapter.sortedLessons    // lessons sorted by order
 *   chapter.isValid()        // true if title non-empty
 *   chapter.getCompletedLessonsCount(userId)  // count completed lessons
 */

import { Lesson } from './Lesson.model'

export class Chapter {
  constructor(
    public readonly id: string,
    public readonly courseId: string,
    public readonly title: string,
    public readonly order: number,
    public readonly lessons: Lesson[]
  ) {}

  /**
   * Get sorted lessons by order.
   *
   * Business Logic: Lessons must be in consistent order.
   * Previously in: courseEditor.store.ts lines 60-63
   *
   * @returns Sorted lessons array
   *
   * @example
   * chapter.sortedLessons // Returns lessons ordered by their order field
   */
  get sortedLessons(): Lesson[] {
    return [...this.lessons].sort((a, b) => a.order - b.order)
  }

  /**
   * Get chapter display title.
   *
   * @returns Chapter title with whitespace trimmed
   */
  get displayTitle(): string {
    return this.title.trim()
  }

  /**
   * Get total number of lessons in chapter.
   *
   * @returns Lesson count
   */
  get totalLessons(): number {
    return this.lessons.length
  }

  /**
   * Count completed lessons for a user.
   *
   * Business Calculation: Count lessons where user has marked complete.
   *
   * @param userId - User ID to count completed lessons for
   * @returns Number of completed lessons (0 to totalLessons)
   *
   * @example
   * chapter.getCompletedLessonsCount('user-123')  // 3
   */
  getCompletedLessonsCount(userId: string): number {
    return this.lessons.filter(lesson => lesson.isCompletedBy(userId)).length
  }

  /**
   * Check if chapter is fully valid.
   *
   * Validation includes:
   * - Title not empty
   * - All nested lessons valid
   *
   * @returns true if chapter is fully valid, false otherwise
   */
  isValid(): boolean {
    // Title validation
    if (!this.title || this.title.trim().length === 0) return false

    // Lessons validation
    for (const lesson of this.lessons) {
      if (!lesson.isValid()) return false
    }

    return true
  }

  /**
   * Convert API DTO to domain model.
   *
   * Single transformation point handling:
   * - snake_case → camelCase conversion
   * - Nested lesson transformation
   * - Proper error propagation
   *
   * @param data Raw API data
   * @returns Chapter instance
   * @throws Error if data is invalid
   *
   * @example
   * Chapter.fromAPI({
   *   id: 'chapter-123',
   *   course_id: 'course-456',
   *   title: 'Chapter Title',
   *   order: 1,
   *   lessons: [{ ... }]
   * })
   */
  static fromAPI(data: any): Chapter {
    return new Chapter(
      data.id,
      data.course_id !== undefined ? data.course_id : data.courseId,
      data.title,
      data.order,
      (data.lessons || []).map((l: any) => Lesson.fromAPI(l))
    )
  }

  /**
   * Convert to plain object for UI display/serialization.
   *
   * @returns Plain object representation
   *
   * @example
   * chapter.toJSON()
   * // Returns: {
   * //   id: 'chapter-123',
   * //   courseId: 'course-456',
   * //   title: 'Chapter Title',
   * //   order: 1,
   * //   lessons: [...],
   * //   displayTitle: 'Chapter Title',
   * //   totalLessons: 2,
   * //   sortedLessons: [...]
   * // }
   */
  toJSON(): object {
    return {
      id: this.id,
      courseId: this.courseId,
      title: this.title,
      order: this.order,
      lessons: this.lessons.map(l => l.toJSON()),
      displayTitle: this.displayTitle,
      totalLessons: this.totalLessons,
      sortedLessons: this.sortedLessons.map(l => l.toJSON())
    }
  }
}
