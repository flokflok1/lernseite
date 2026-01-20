import { Course } from './Course.model'
import { Chapter } from './Chapter.model'

/**
 * Course Factory
 *
 * Implements DDD Factory Pattern for Course creation.
 * Handles complex course initialization with validation and sensible defaults.
 *
 * Pattern from Backend: UserFactory.createWithRole(), CourseFactory.createDraft()
 *
 * Business Rules:
 * - New courses start in DRAFT status (unpublished)
 * - Title is required and must be trimmed
 * - Description is optional but recommended
 * - Creator ID is required
 * - Factory handles all default values and complex initialization
 * - No chapters on creation (added via separate methods)
 */
export class CourseFactory {
  /**
   * Create new course draft with defaults.
   *
   * Business Rule: New courses always start as unpublished drafts.
   * This allows creators to build content before publishing.
   *
   * @param creatorId - ID of the user creating the course
   * @param title - Course title (required)
   * @returns Course instance in draft status
   * @throws Error if creatorId or title is missing/invalid
   *
   * @example
   * const course = CourseFactory.createDraft(
   *   'user-123',
   *   'Advanced TypeScript'
   * )
   * // Returns unpublished course with empty description
   */
  static createDraft(creatorId: string, title: string): Course {
    // Validation: Creator ID required
    if (!creatorId || creatorId.trim().length === 0) {
      throw new Error('Creator ID is required')
    }

    // Validation: Title required and non-empty
    if (!title || title.trim().length === 0) {
      throw new Error('Course title is required')
    }

    // Validation: Title length (practical limit)
    if (title.trim().length > 200) {
      throw new Error('Course title must not exceed 200 characters')
    }

    // Create course with sensible defaults
    return new Course(
      crypto.randomUUID(), // Generate unique ID
      title.trim(), // Trim whitespace
      '', // Empty description (to be filled later)
      creatorId, // Creator must be set
      [], // No chapters initially
      false, // DRAFT status (unpublished)
      new Date(), // Creation timestamp
      undefined // No update timestamp on creation
    )
  }

  /**
   * Create course from form data with full validation.
   *
   * Validates all required fields before creating course instance.
   * This is typically used when creating a course with initial data from a form.
   *
   * @param creatorId - ID of the user creating the course
   * @param formData - Form data object
   * @param formData.title - Course title (required, 1-200 chars)
   * @param formData.description - Course description (optional, 0-2000 chars)
   * @returns Course instance with provided data
   * @throws Error if validation fails
   *
   * @example
   * const course = CourseFactory.createFromFormData(
   *   'user-123',
   *   {
   *     title: 'My Course',
   *     description: 'An interesting course about TypeScript'
   *   }
   * )
   */
  static createFromFormData(
    creatorId: string,
    formData: {
      title: string
      description?: string
    }
  ): Course {
    // Validation: Creator ID required
    if (!creatorId || creatorId.trim().length === 0) {
      throw new Error('Creator ID is required')
    }

    // Validation: Title required
    if (!formData.title || formData.title.trim().length === 0) {
      throw new Error('Course title is required')
    }

    // Validation: Title length
    if (formData.title.trim().length > 200) {
      throw new Error('Course title must not exceed 200 characters')
    }

    // Validation: Description (if provided)
    const description = (formData.description || '').trim()
    if (description.length > 2000) {
      throw new Error('Course description must not exceed 2000 characters')
    }

    // Create course with form data
    return new Course(
      crypto.randomUUID(), // Generate unique ID
      formData.title.trim(), // Trim and validate
      description, // Use provided or empty string
      creatorId, // Creator ID
      [], // No chapters initially
      false, // DRAFT status by default
      new Date(), // Creation timestamp
      undefined // No update timestamp on creation
    )
  }

  /**
   * Create course from existing API response.
   *
   * This is used when loading courses from the backend.
   * For transformation from API DTOs, use Course.fromAPI() instead.
   * This factory method is for cases where we need to apply additional business logic
   * during course creation (e.g., applying feature flags, defaults, etc.).
   *
   * @param apiData - Data from API
   * @returns Course instance
   *
   * @example
   * const course = CourseFactory.createFromAPI(apiResponse)
   */
  static createFromAPI(apiData: any): Course {
    return Course.fromAPI(apiData)
  }

  /**
   * Create empty course for testing/demo purposes.
   *
   * Business Rule: This should only be used in development/test scenarios.
   * In production, always use createDraft() or createFromFormData() with real data.
   *
   * @param creatorId - Creator ID (required)
   * @returns Course with minimal data for testing
   * @throws Error if creatorId is invalid
   */
  static createForTesting(creatorId: string): Course {
    if (!creatorId || creatorId.trim().length === 0) {
      throw new Error('Creator ID is required for testing course')
    }

    return new Course(
      'test-course-' + crypto.randomUUID().substring(0, 8),
      'Test Course',
      'This is a test course',
      creatorId,
      [],
      false,
      new Date(),
      undefined
    )
  }

  /**
   * Validate course data before creation.
   *
   * Can be used as a pre-check before calling factory methods.
   *
   * @param data - Data to validate
   * @returns Object with { isValid: boolean, errors: string[] }
   *
   * @example
   * const validation = CourseFactory.validate(formData)
   * if (!validation.isValid) {
   *   console.error(validation.errors)
   * }
   */
  static validate(data: {
    creatorId?: string
    title?: string
    description?: string
  }): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    // Validate creator ID
    if (!data.creatorId || data.creatorId.trim().length === 0) {
      errors.push('Creator ID is required')
    }

    // Validate title
    if (!data.title || data.title.trim().length === 0) {
      errors.push('Course title is required')
    } else if (data.title.trim().length > 200) {
      errors.push('Course title must not exceed 200 characters')
    }

    // Validate description (optional but validated if provided)
    if (data.description && data.description.trim().length > 2000) {
      errors.push('Course description must not exceed 2000 characters')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }
}
