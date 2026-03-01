import { describe, it, expect } from 'vitest'
import { Lesson } from '../Lesson.model'

describe('Lesson', () => {
  describe('Learning Method Type Constraint (0-11)', () => {
    it('accepts valid learning method types 0-11', () => {
      for (let i = 0; i <= 11; i++) {
        const lesson = new Lesson(
          `l${i}`,
          'ch1',
          'Lesson',
          'Description',
          1,
          i,
          true
        )
        expect(lesson.learningMethodType).toBe(i)
      }
    })

    it('throws error for learning method type > 11', () => {
      expect(() => {
        Lesson.fromAPI({
          id: 'l1',
          chapter_id: 'ch1',
          title: 'Lesson',
          description: 'Desc',
          order: 1,
          learning_method_type: 12,
          is_published: true,
          completed_by_users: []
        })
      }).toThrow('Invalid learning method type: 12. Must be 0-11 (LM00-LM11)')
    })

    it('throws error for negative learning method type', () => {
      expect(() => {
        Lesson.fromAPI({
          id: 'l1',
          chapter_id: 'ch1',
          title: 'Lesson',
          description: 'Desc',
          order: 1,
          learning_method_type: -1,
          is_published: true,
          completed_by_users: []
        })
      }).toThrow('Invalid learning method type: -1. Must be 0-11 (LM00-LM11)')
    })

    it('defaults to 0 when learning_method_type not provided', () => {
      const lesson = Lesson.fromAPI({
        id: 'l1',
        chapter_id: 'ch1',
        title: 'Lesson',
        description: 'Desc',
        order: 1,
        is_published: true,
        completed_by_users: []
      })

      expect(lesson.learningMethodType).toBe(0)
    })
  })

  describe('isCompletedBy(userId)', () => {
    it('returns true when user is in completedByUsers', () => {
      const lesson = new Lesson(
        'l1',
        'ch1',
        'Lesson',
        'Description',
        1,
        0,
        true,
        ['user-123', 'user-456']
      )

      expect(lesson.isCompletedBy('user-123')).toBe(true)
      expect(lesson.isCompletedBy('user-456')).toBe(true)
    })

    it('returns false when user is not in completedByUsers', () => {
      const lesson = new Lesson(
        'l1',
        'ch1',
        'Lesson',
        'Description',
        1,
        0,
        true,
        ['user-123']
      )

      expect(lesson.isCompletedBy('user-456')).toBe(false)
    })

    it('returns false for empty completedByUsers', () => {
      const lesson = new Lesson('l1', 'ch1', 'Lesson', 'Description', 1, 0, true, [])

      expect(lesson.isCompletedBy('user-123')).toBe(false)
    })
  })

  describe('learningMethodId getter', () => {
    it('formats learning method type as LM00-LM11 with zero padding', () => {
      const lesson0 = new Lesson('l0', 'ch1', 'Lesson', 'Desc', 1, 0, true)
      const lesson5 = new Lesson('l5', 'ch1', 'Lesson', 'Desc', 1, 5, true)
      const lesson11 = new Lesson('l11', 'ch1', 'Lesson', 'Desc', 1, 11, true)

      expect(lesson0.learningMethodId).toBe('LM00')
      expect(lesson5.learningMethodId).toBe('LM05')
      expect(lesson11.learningMethodId).toBe('LM11')
    })
  })

  describe('displayTitle getter', () => {
    it('returns title with whitespace trimmed', () => {
      const lesson = new Lesson('l1', 'ch1', '  Lesson Title  ', 'Desc', 1, 0, true)

      expect(lesson.displayTitle).toBe('Lesson Title')
    })

    it('handles title with no whitespace', () => {
      const lesson = new Lesson('l1', 'ch1', 'LessonTitle', 'Desc', 1, 0, true)

      expect(lesson.displayTitle).toBe('LessonTitle')
    })
  })

  describe('completionCount getter', () => {
    it('returns count of users who completed lesson', () => {
      const lesson = new Lesson(
        'l1',
        'ch1',
        'Lesson',
        'Description',
        1,
        0,
        true,
        ['user-1', 'user-2', 'user-3']
      )

      expect(lesson.completionCount).toBe(3)
    })

    it('returns zero when no users have completed', () => {
      const lesson = new Lesson('l1', 'ch1', 'Lesson', 'Description', 1, 0, true, [])

      expect(lesson.completionCount).toBe(0)
    })
  })

  describe('isValid()', () => {
    it('returns true for valid lesson', () => {
      const lesson = new Lesson(
        'l1',
        'ch1',
        'Valid Lesson',
        'Valid Description',
        1,
        0,
        true
      )

      expect(lesson.isValid()).toBe(true)
    })

    it('returns false for empty title', () => {
      const lesson = new Lesson('l1', 'ch1', '', 'Description', 1, 0, true)

      expect(lesson.isValid()).toBe(false)
    })

    it('returns false for whitespace-only title', () => {
      const lesson = new Lesson('l1', 'ch1', '   ', 'Description', 1, 0, true)

      expect(lesson.isValid()).toBe(false)
    })

    it('returns true for empty description (drafts allowed)', () => {
      const lesson = new Lesson('l1', 'ch1', 'Title', '', 1, 0, true)

      // isValid() only checks title — description is validated in canPublish()
      expect(lesson.isValid()).toBe(true)
    })

    it('returns true regardless of learning method type (draft validation)', () => {
      const lessonNeg = new Lesson('l1', 'ch1', 'Title', 'Description', 1, -1, true)
      const lessonHigh = new Lesson('l2', 'ch1', 'Title', 'Description', 1, 12, true)

      // isValid() only checks title — learningMethodType is validated in canPublish()
      expect(lessonNeg.isValid()).toBe(true)
      expect(lessonHigh.isValid()).toBe(true)
    })
  })

  describe('fromAPI(data)', () => {
    it('transforms API data with snake_case to camelCase', () => {
      const apiData = {
        id: 'l1',
        chapter_id: 'ch1',
        title: 'Lesson 1',
        description: 'Description',
        order: 1,
        learning_method_type: 5,
        is_published: true,
        completed_by_users: ['user-123']
      }

      const lesson = Lesson.fromAPI(apiData)

      expect(lesson.id).toBe('l1')
      expect(lesson.chapterId).toBe('ch1')
      expect(lesson.title).toBe('Lesson 1')
      expect(lesson.description).toBe('Description')
      expect(lesson.order).toBe(1)
      expect(lesson.learningMethodType).toBe(5)
      expect(lesson.isPublished).toBe(true)
      expect(lesson.completedByUsers).toEqual(['user-123'])
    })

    it('handles camelCase API data', () => {
      const apiData = {
        id: 'l1',
        chapterId: 'ch1',
        title: 'Lesson 1',
        description: 'Description',
        order: 1,
        learningMethodType: 3,
        isPublished: true,
        completedByUsers: []
      }

      const lesson = Lesson.fromAPI(apiData)

      expect(lesson.chapterId).toBe('ch1')
      expect(lesson.learningMethodType).toBe(3)
      expect(lesson.isPublished).toBe(true)
    })

    it('validates learning_method_type constraint in fromAPI', () => {
      expect(() => {
        Lesson.fromAPI({
          id: 'l1',
          chapter_id: 'ch1',
          title: 'Lesson',
          description: 'Desc',
          order: 1,
          learning_method_type: 20,
          is_published: true,
          completed_by_users: []
        })
      }).toThrow('Invalid learning method type: 20. Must be 0-11 (LM00-LM11)')
    })

    it('handles timestamps in fromAPI', () => {
      const apiData = {
        id: 'l1',
        chapter_id: 'ch1',
        title: 'Lesson',
        description: 'Desc',
        order: 1,
        learning_method_type: 0,
        is_published: true,
        completed_by_users: [],
        created_at: '2026-01-19T10:00:00Z',
        updated_at: '2026-01-19T11:00:00Z'
      }

      const lesson = Lesson.fromAPI(apiData)

      expect(lesson.createdAt).toBeInstanceOf(Date)
      expect(lesson.updatedAt).toBeInstanceOf(Date)
      expect(lesson.createdAt?.toISOString()).toBe('2026-01-19T10:00:00.000Z')
    })

    it('handles missing updated_at in fromAPI', () => {
      const apiData = {
        id: 'l1',
        chapter_id: 'ch1',
        title: 'Lesson',
        description: 'Desc',
        order: 1,
        learning_method_type: 0,
        is_published: true,
        completed_by_users: [],
        created_at: '2026-01-19T10:00:00Z'
      }

      const lesson = Lesson.fromAPI(apiData)

      expect(lesson.createdAt).toBeInstanceOf(Date)
      expect(lesson.updatedAt).toBeUndefined()
    })
  })

  describe('toJSON()', () => {
    it('returns object with all lesson fields', () => {
      const lesson = new Lesson(
        'l1',
        'ch1',
        'Lesson Title',
        'Description',
        1,
        5,
        true,
        ['user-123'],
        new Date('2026-01-19T10:00:00Z'),
        new Date('2026-01-19T11:00:00Z')
      )

      const json = lesson.toJSON()

      expect(json.id).toBe('l1')
      expect(json.chapterId).toBe('ch1')
      expect(json.title).toBe('Lesson Title')
      expect(json.description).toBe('Description')
      expect(json.order).toBe(1)
      expect(json.learningMethodType).toBe(5)
      expect(json.learningMethodId).toBe('LM05')
      expect(json.isPublished).toBe(true)
      expect(json.displayTitle).toBe('Lesson Title')
      expect(json.completedByUsers).toEqual(['user-123'])
      expect(json.completionCount).toBe(1)
    })

    it('includes ISO string timestamps in toJSON', () => {
      const createdDate = new Date('2026-01-19T10:00:00Z')
      const updatedDate = new Date('2026-01-19T11:00:00Z')

      const lesson = new Lesson(
        'l1',
        'ch1',
        'Lesson',
        'Desc',
        1,
        0,
        true,
        [],
        createdDate,
        updatedDate
      )

      const json = lesson.toJSON()

      expect(json.createdAt).toBe(createdDate.toISOString())
      expect(json.updatedAt).toBe(updatedDate.toISOString())
    })

    it('includes undefined for missing timestamps in toJSON', () => {
      const lesson = new Lesson('l1', 'ch1', 'Lesson', 'Desc', 1, 0, true, [], undefined, undefined)

      const json = lesson.toJSON()

      expect(json.createdAt).toBeUndefined()
      expect(json.updatedAt).toBeUndefined()
    })
  })
})
