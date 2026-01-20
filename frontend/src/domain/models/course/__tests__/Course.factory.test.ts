import { describe, it, expect, beforeEach, vi } from 'vitest'
import { CourseFactory } from '../Course.factory'
import { Course } from '../Course.model'

describe('CourseFactory', () => {
  describe('createDraft', () => {
    it('creates course in DRAFT status with sensible defaults', () => {
      const course = CourseFactory.createDraft('user-123', 'Advanced TypeScript')

      expect(course).toBeInstanceOf(Course)
      expect(course.title).toBe('Advanced TypeScript')
      expect(course.description).toBe('')
      expect(course.creatorId).toBe('user-123')
      expect(course.isPublished).toBe(false)
      expect(course.chapters).toEqual([])
      expect(course.createdAt).toBeInstanceOf(Date)
      expect(course.updatedAt).toBeUndefined()
    })

    it('trims title whitespace', () => {
      const course = CourseFactory.createDraft('user-123', '  React Basics  ')

      expect(course.title).toBe('React Basics')
    })

    it('throws error if creatorId is missing', () => {
      expect(() => CourseFactory.createDraft('', 'Course Title')).toThrow('Creator ID is required')
    })

    it('throws error if creatorId is whitespace only', () => {
      expect(() => CourseFactory.createDraft('   ', 'Course Title')).toThrow('Creator ID is required')
    })

    it('throws error if title is missing', () => {
      expect(() => CourseFactory.createDraft('user-123', '')).toThrow('Course title is required')
    })

    it('throws error if title is whitespace only', () => {
      expect(() => CourseFactory.createDraft('user-123', '   ')).toThrow('Course title is required')
    })

    it('throws error if title exceeds 200 characters', () => {
      const longTitle = 'A'.repeat(201)
      expect(() => CourseFactory.createDraft('user-123', longTitle)).toThrow(
        'Course title must not exceed 200 characters'
      )
    })

    it('generates unique course IDs', () => {
      const course1 = CourseFactory.createDraft('user-123', 'Course 1')
      const course2 = CourseFactory.createDraft('user-123', 'Course 2')

      expect(course1.id).not.toBe(course2.id)
    })

    it('sets createdAt to current time', () => {
      const before = new Date()
      const course = CourseFactory.createDraft('user-123', 'My Course')
      const after = new Date()

      expect(course.createdAt.getTime()).toBeGreaterThanOrEqual(before.getTime())
      expect(course.createdAt.getTime()).toBeLessThanOrEqual(after.getTime())
    })
  })

  describe('createFromFormData', () => {
    it('creates course from form data with validation', () => {
      const formData = {
        title: 'Vue.js Masterclass',
        description: 'Learn Vue.js from scratch'
      }

      const course = CourseFactory.createFromFormData('user-456', formData)

      expect(course.title).toBe('Vue.js Masterclass')
      expect(course.description).toBe('Learn Vue.js from scratch')
      expect(course.creatorId).toBe('user-456')
      expect(course.isPublished).toBe(false)
    })

    it('creates course with optional description', () => {
      const formData = { title: 'TypeScript Advanced' }

      const course = CourseFactory.createFromFormData('user-789', formData)

      expect(course.description).toBe('')
    })

    it('trims description whitespace', () => {
      const formData = {
        title: 'Python Basics',
        description: '   Learn Python fundamentals   '
      }

      const course = CourseFactory.createFromFormData('user-123', formData)

      expect(course.description).toBe('Learn Python fundamentals')
    })

    it('throws error if creatorId is missing', () => {
      expect(() =>
        CourseFactory.createFromFormData('', { title: 'Course' })
      ).toThrow('Creator ID is required')
    })

    it('throws error if title is missing', () => {
      expect(() =>
        CourseFactory.createFromFormData('user-123', { title: '' })
      ).toThrow('Course title is required')
    })

    it('throws error if title exceeds 200 characters', () => {
      const longTitle = 'A'.repeat(201)
      expect(() =>
        CourseFactory.createFromFormData('user-123', { title: longTitle })
      ).toThrow('Course title must not exceed 200 characters')
    })

    it('throws error if description exceeds 2000 characters', () => {
      const longDescription = 'A'.repeat(2001)
      expect(() =>
        CourseFactory.createFromFormData('user-123', {
          title: 'My Course',
          description: longDescription
        })
      ).toThrow('Course description must not exceed 2000 characters')
    })

    it('accepts description at boundary (2000 chars)', () => {
      const boundaryDescription = 'A'.repeat(2000)
      const course = CourseFactory.createFromFormData('user-123', {
        title: 'My Course',
        description: boundaryDescription
      })

      expect(course.description.length).toBe(2000)
    })

    it('accepts title at boundary (200 chars)', () => {
      const boundaryTitle = 'A'.repeat(200)
      const course = CourseFactory.createDraft('user-123', boundaryTitle)

      expect(course.title.length).toBe(200)
    })
  })

  describe('createFromAPI', () => {
    it('delegates to Course.fromAPI', () => {
      const apiData = {
        id: 'course-123',
        title: 'Web Development',
        description: 'Learn web development',
        creator_id: 'user-456',
        chapters: [],
        is_published: false,
        created_at: '2026-01-19T10:00:00Z'
      }

      const course = CourseFactory.createFromAPI(apiData)

      expect(course.id).toBe('course-123')
      expect(course.title).toBe('Web Development')
      expect(course.creatorId).toBe('user-456')
      expect(course.isPublished).toBe(false)
    })
  })

  describe('createForTesting', () => {
    it('creates test course with fixed data', () => {
      const course = CourseFactory.createForTesting('test-user')

      expect(course.title).toBe('Test Course')
      expect(course.description).toBe('This is a test course')
      expect(course.creatorId).toBe('test-user')
      expect(course.isPublished).toBe(false)
      expect(course.chapters).toEqual([])
      expect(course.id).toMatch(/^test-course-/)
    })

    it('generates unique test course IDs', () => {
      const course1 = CourseFactory.createForTesting('user-1')
      const course2 = CourseFactory.createForTesting('user-2')

      expect(course1.id).not.toBe(course2.id)
      expect(course1.id).toMatch(/^test-course-/)
      expect(course2.id).toMatch(/^test-course-/)
    })

    it('throws error if creatorId is missing', () => {
      expect(() => CourseFactory.createForTesting('')).toThrow(
        'Creator ID is required for testing course'
      )
    })

    it('throws error if creatorId is whitespace only', () => {
      expect(() => CourseFactory.createForTesting('   ')).toThrow(
        'Creator ID is required for testing course'
      )
    })
  })

  describe('validate', () => {
    it('returns valid for correct data', () => {
      const validation = CourseFactory.validate({
        creatorId: 'user-123',
        title: 'My Course',
        description: 'A great course'
      })

      expect(validation.isValid).toBe(true)
      expect(validation.errors).toEqual([])
    })

    it('returns error for missing creatorId', () => {
      const validation = CourseFactory.validate({
        title: 'My Course'
      })

      expect(validation.isValid).toBe(false)
      expect(validation.errors).toContain('Creator ID is required')
    })

    it('returns error for missing title', () => {
      const validation = CourseFactory.validate({
        creatorId: 'user-123'
      })

      expect(validation.isValid).toBe(false)
      expect(validation.errors).toContain('Course title is required')
    })

    it('returns error for empty title', () => {
      const validation = CourseFactory.validate({
        creatorId: 'user-123',
        title: ''
      })

      expect(validation.isValid).toBe(false)
      expect(validation.errors).toContain('Course title is required')
    })

    it('returns error for title exceeding 200 characters', () => {
      const validation = CourseFactory.validate({
        creatorId: 'user-123',
        title: 'A'.repeat(201)
      })

      expect(validation.isValid).toBe(false)
      expect(validation.errors).toContain('Course title must not exceed 200 characters')
    })

    it('returns error for description exceeding 2000 characters', () => {
      const validation = CourseFactory.validate({
        creatorId: 'user-123',
        title: 'My Course',
        description: 'A'.repeat(2001)
      })

      expect(validation.isValid).toBe(false)
      expect(validation.errors).toContain('Course description must not exceed 2000 characters')
    })

    it('returns multiple errors', () => {
      const validation = CourseFactory.validate({
        title: 'A'.repeat(201),
        description: 'A'.repeat(2001)
      })

      expect(validation.isValid).toBe(false)
      expect(validation.errors.length).toBeGreaterThan(1)
      expect(validation.errors).toContain('Creator ID is required')
      expect(validation.errors).toContain('Course title must not exceed 200 characters')
      expect(validation.errors).toContain('Course description must not exceed 2000 characters')
    })

    it('accepts optional description', () => {
      const validation = CourseFactory.validate({
        creatorId: 'user-123',
        title: 'My Course'
      })

      expect(validation.isValid).toBe(true)
      expect(validation.errors).toEqual([])
    })

    it('validates empty description as valid', () => {
      const validation = CourseFactory.validate({
        creatorId: 'user-123',
        title: 'My Course',
        description: ''
      })

      expect(validation.isValid).toBe(true)
    })
  })
})
