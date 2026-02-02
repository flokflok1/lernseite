import { describe, it, expect } from 'vitest'
import { Chapter } from '../Chapter.model'
import { Lesson } from '../Lesson.model'

describe('Chapter', () => {
  describe('sortedLessons getter', () => {
    it('returns lessons sorted by order', () => {
      const lesson1 = new Lesson('l1', 'ch1', 'Lesson 1', 'Desc 1', 3, 0, true)
      const lesson2 = new Lesson('l2', 'ch1', 'Lesson 2', 'Desc 2', 1, 0, true)
      const lesson3 = new Lesson('l3', 'ch1', 'Lesson 3', 'Desc 3', 2, 0, true)

      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1, lesson2, lesson3])
      const sorted = chapter.sortedLessons

      expect(sorted).toHaveLength(3)
      expect(sorted[0].order).toBe(1)
      expect(sorted[1].order).toBe(2)
      expect(sorted[2].order).toBe(3)
      expect(sorted[0].id).toBe('l2')
      expect(sorted[1].id).toBe('l3')
      expect(sorted[2].id).toBe('l1')
    })

    it('does not mutate original lessons array', () => {
      const lesson1 = new Lesson('l1', 'ch1', 'Lesson 1', 'Desc 1', 3, 0, true)
      const lesson2 = new Lesson('l2', 'ch1', 'Lesson 2', 'Desc 2', 1, 0, true)

      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1, lesson2])

      const sorted1 = chapter.sortedLessons
      const sorted2 = chapter.sortedLessons

      expect(sorted1).toEqual(sorted2)
      expect(chapter.lessons[0].id).toBe('l1')
      expect(chapter.lessons[1].id).toBe('l2')
    })

    it('handles empty lessons array', () => {
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [])

      expect(chapter.sortedLessons).toEqual([])
    })
  })

  describe('getCompletedLessonsCount(userId)', () => {
    it('returns count of lessons completed by user', () => {
      const lesson1 = new Lesson('l1', 'ch1', 'Lesson 1', 'Desc 1', 1, 0, true, ['user-123'])
      const lesson2 = new Lesson('l2', 'ch1', 'Lesson 2', 'Desc 2', 2, 0, true, ['user-123'])
      const lesson3 = new Lesson('l3', 'ch1', 'Lesson 3', 'Desc 3', 3, 0, true, [])

      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1, lesson2, lesson3])

      expect(chapter.getCompletedLessonsCount('user-123')).toBe(2)
    })

    it('returns zero when no lessons completed', () => {
      const lesson1 = new Lesson('l1', 'ch1', 'Lesson 1', 'Desc 1', 1, 0, true, [])
      const lesson2 = new Lesson('l2', 'ch1', 'Lesson 2', 'Desc 2', 2, 0, true, [])

      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1, lesson2])

      expect(chapter.getCompletedLessonsCount('user-123')).toBe(0)
    })

    it('returns zero for empty chapter', () => {
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [])

      expect(chapter.getCompletedLessonsCount('user-123')).toBe(0)
    })
  })

  describe('isValid()', () => {
    it('returns true for valid chapter', () => {
      const lesson = new Lesson('l1', 'ch1', 'Lesson 1', 'Desc 1', 1, 0, true)
      const chapter = new Chapter('ch1', 'course-123', 'Valid Chapter', 1, [lesson])

      expect(chapter.isValid()).toBe(true)
    })

    it('returns false for empty title', () => {
      const lesson = new Lesson('l1', 'ch1', 'Lesson 1', 'Desc 1', 1, 0, true)
      const chapter = new Chapter('ch1', 'course-123', '', 1, [lesson])

      expect(chapter.isValid()).toBe(false)
    })

    it('returns false for whitespace-only title', () => {
      const lesson = new Lesson('l1', 'ch1', 'Lesson 1', 'Desc 1', 1, 0, true)
      const chapter = new Chapter('ch1', 'course-123', '   ', 1, [lesson])

      expect(chapter.isValid()).toBe(false)
    })

    it('returns false when containing invalid lesson', () => {
      const validLesson = new Lesson('l1', 'ch1', 'Lesson 1', 'Desc 1', 1, 0, true)
      const invalidLesson = new Lesson('l2', 'ch1', '', '', 2, 0, true) // Invalid: empty title/description
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [validLesson, invalidLesson])

      expect(chapter.isValid()).toBe(false)
    })
  })

  describe('fromAPI(data)', () => {
    it('transforms API data with snake_case to camelCase', () => {
      const apiData = {
        id: 'ch1',
        course_id: 'course-123',
        title: 'Chapter 1',
        order: 1,
        lessons: []
      }

      const chapter = Chapter.fromAPI(apiData)

      expect(chapter.id).toBe('ch1')
      expect(chapter.courseId).toBe('course-123')
      expect(chapter.title).toBe('Chapter 1')
      expect(chapter.order).toBe(1)
      expect(chapter.lessons).toEqual([])
    })

    it('handles camelCase API data', () => {
      const apiData = {
        id: 'ch1',
        courseId: 'course-123',
        title: 'Chapter 1',
        order: 1,
        lessons: []
      }

      const chapter = Chapter.fromAPI(apiData)

      expect(chapter.courseId).toBe('course-123')
    })

    it('transforms nested lessons', () => {
      const apiData = {
        id: 'ch1',
        course_id: 'course-123',
        title: 'Chapter 1',
        order: 1,
        lessons: [
          {
            id: 'l1',
            chapter_id: 'ch1',
            title: 'Lesson 1',
            description: 'Lesson Description',
            order: 1,
            learning_method_type: 0,
            is_published: true,
            completed_by_users: []
          },
          {
            id: 'l2',
            chapter_id: 'ch1',
            title: 'Lesson 2',
            description: 'Another Lesson',
            order: 2,
            learning_method_type: 5,
            is_published: true,
            completed_by_users: ['user-123']
          }
        ]
      }

      const chapter = Chapter.fromAPI(apiData)

      expect(chapter.lessons).toHaveLength(2)
      expect(chapter.lessons[0].title).toBe('Lesson 1')
      expect(chapter.lessons[0].learningMethodType).toBe(0)
      expect(chapter.lessons[1].title).toBe('Lesson 2')
      expect(chapter.lessons[1].learningMethodType).toBe(5)
      expect(chapter.lessons[1].completedByUsers).toContain('user-123')
    })

    it('handles missing lessons array', () => {
      const apiData = {
        id: 'ch1',
        course_id: 'course-123',
        title: 'Chapter 1',
        order: 1
      }

      const chapter = Chapter.fromAPI(apiData)

      expect(chapter.lessons).toEqual([])
    })
  })

  describe('toJSON()', () => {
    it('returns object with all chapter fields', () => {
      const lesson = new Lesson('l1', 'ch1', 'Lesson 1', 'Desc 1', 1, 0, true)
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson])

      const json = chapter.toJSON()

      expect(json.id).toBe('ch1')
      expect(json.courseId).toBe('course-123')
      expect(json.title).toBe('Chapter 1')
      expect(json.order).toBe(1)
      expect(json.lessons).toHaveLength(1)
    })

    it('includes sorted lessons in output', () => {
      const lesson1 = new Lesson('l1', 'ch1', 'Lesson 1', 'Desc 1', 3, 0, true)
      const lesson2 = new Lesson('l2', 'ch1', 'Lesson 2', 'Desc 2', 1, 0, true)
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1, lesson2])

      const json = chapter.toJSON()

      expect(json.lessons).toHaveLength(2)
      expect(json.lessons[0].order).toBe(1)
      expect(json.lessons[1].order).toBe(3)
    })
  })
})
