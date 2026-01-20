import { describe, it, expect, beforeEach } from 'vitest'
import { Course } from '../Course.model'
import { Chapter } from '../Chapter.model'
import { Lesson } from '../Lesson.model'
import { User } from '../../user/User.model'
import { Email } from '../../value-objects/Email.vo'
import { UserRole, UserRoleEnum } from '../../user/UserRole.vo'

describe('Course Domain Model', () => {
  // Helper function to create test users
  const createTestUser = (role: UserRoleEnum = UserRoleEnum.FREE, isAdmin = false) => {
    return new User(
      'user-123',
      Email.create('test@example.com'),
      'testuser',
      'John',
      'Doe',
      UserRole.create(role),
      true,
      new Date('2024-01-01')
    )
  }

  // Helper function to create test lessons
  const createTestLesson = (id: string, chapterId: string, completedByUsers: string[] = []) => {
    return new Lesson(
      id,
      chapterId,
      'Test Lesson',
      'Test Description',
      1,
      0, // LM00
      true,
      completedByUsers
    )
  }

  // Helper function to create test chapters
  const createTestChapter = (id: string, courseId: string, lessons: Lesson[] = []) => {
    return new Chapter(id, courseId, 'Test Chapter', 1, lessons)
  }

  // Helper function to create test course
  const createTestCourse = (chapters: Chapter[] = []) => {
    return new Course(
      'course-123',
      'Test Course',
      'Test Description',
      'creator-123',
      chapters,
      false,
      new Date('2024-01-01')
    )
  }

  describe('sortedChapters getter', () => {
    it('returns chapters sorted by order', () => {
      const chapter1 = createTestChapter('ch1', 'course-123', [])
      const chapter2 = createTestChapter('ch2', 'course-123', [])
      const chapter3 = createTestChapter('ch3', 'course-123', [])

      // Manually set order (since constructor parameter is 'order' not in Chapter constructor)
      const chapters = [
        new Chapter('ch1', 'course-123', 'Chapter 1', 3, []),
        new Chapter('ch2', 'course-123', 'Chapter 2', 1, []),
        new Chapter('ch3', 'course-123', 'Chapter 3', 2, [])
      ]

      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', chapters, false, new Date())
      const sorted = course.sortedChapters

      expect(sorted[0].order).toBe(1)
      expect(sorted[1].order).toBe(2)
      expect(sorted[2].order).toBe(3)
    })

    it('does not mutate original chapters array', () => {
      const chapters = [
        new Chapter('ch1', 'course-123', 'Chapter 1', 3, []),
        new Chapter('ch2', 'course-123', 'Chapter 2', 1, [])
      ]
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', chapters, false, new Date())

      const sorted = course.sortedChapters

      expect(chapters[0].order).toBe(3)
      expect(chapters[1].order).toBe(1)
      expect(sorted[0].order).toBe(1)
    })

    it('returns empty array for course with no chapters', () => {
      const course = createTestCourse([])
      expect(course.sortedChapters).toEqual([])
    })
  })

  describe('displayTitle getter', () => {
    it('trims whitespace from title', () => {
      const course = new Course(
        'course-123',
        '  Test Course  ',
        'Description',
        'creator-123',
        [],
        false,
        new Date()
      )
      expect(course.displayTitle).toBe('Test Course')
    })

    it('returns title as-is if no whitespace', () => {
      const course = createTestCourse()
      expect(course.displayTitle).toBe('Test Course')
    })
  })

  describe('totalLessons getter', () => {
    it('returns total number of lessons across all chapters', () => {
      const lesson1 = createTestLesson('l1', 'ch1')
      const lesson2 = createTestLesson('l2', 'ch1')
      const lesson3 = createTestLesson('l3', 'ch2')

      const chapter1 = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1, lesson2])
      const chapter2 = new Chapter('ch2', 'course-123', 'Chapter 2', 2, [lesson3])

      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [chapter1, chapter2], false, new Date())

      expect(course.totalLessons).toBe(3)
    })

    it('returns 0 for course with no lessons', () => {
      const course = createTestCourse([])
      expect(course.totalLessons).toBe(0)
    })
  })

  describe('totalChapters getter', () => {
    it('returns number of chapters', () => {
      const chapters = [
        createTestChapter('ch1', 'course-123'),
        createTestChapter('ch2', 'course-123'),
        createTestChapter('ch3', 'course-123')
      ]
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', chapters, false, new Date())

      expect(course.totalChapters).toBe(3)
    })

    it('returns 0 for course with no chapters', () => {
      const course = createTestCourse([])
      expect(course.totalChapters).toBe(0)
    })
  })

  describe('status getter', () => {
    it('returns "draft" for unpublished course', () => {
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [], false, new Date())
      expect(course.status).toBe('draft')
    })

    it('returns "published" for published course', () => {
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [], true, new Date())
      expect(course.status).toBe('published')
    })
  })

  describe('getCompletionPercentage(userId)', () => {
    it('returns 0 for user with no completed lessons', () => {
      const lesson1 = createTestLesson('l1', 'ch1', [])
      const lesson2 = createTestLesson('l2', 'ch1', [])
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1, lesson2])
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [chapter], false, new Date())

      const percentage = course.getCompletionPercentage('user-123')
      expect(percentage).toBe(0)
    })

    it('returns 100 for user who completed all lessons', () => {
      const lesson1 = createTestLesson('l1', 'ch1', ['user-123'])
      const lesson2 = createTestLesson('l2', 'ch1', ['user-123'])
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1, lesson2])
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [chapter], false, new Date())

      const percentage = course.getCompletionPercentage('user-123')
      expect(percentage).toBe(100)
    })

    it('returns partial completion percentage (rounded)', () => {
      const lesson1 = createTestLesson('l1', 'ch1', ['user-123'])
      const lesson2 = createTestLesson('l2', 'ch1', [])
      const lesson3 = createTestLesson('l3', 'ch1', [])
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1, lesson2, lesson3])
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [chapter], false, new Date())

      // 1 completed / 3 total = 33.33% → rounds to 33%
      const percentage = course.getCompletionPercentage('user-123')
      expect(percentage).toBe(33)
    })

    it('returns 0 for course with no lessons', () => {
      const course = createTestCourse([])
      const percentage = course.getCompletionPercentage('user-123')
      expect(percentage).toBe(0)
    })

    it('returns different percentages for different users', () => {
      const lesson1 = createTestLesson('l1', 'ch1', ['user-1', 'user-2'])
      const lesson2 = createTestLesson('l2', 'ch1', ['user-1'])
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1, lesson2])
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [chapter], false, new Date())

      expect(course.getCompletionPercentage('user-1')).toBe(100) // 2/2
      expect(course.getCompletionPercentage('user-2')).toBe(50) // 1/2
    })
  })

  describe('canEdit(user)', () => {
    it('allows creator to edit course', () => {
      const creator = createTestUser()
      const course = new Course('course-123', 'Test', 'Desc', 'user-123', [], false, new Date())

      expect(course.canEdit(creator)).toBe(true)
    })

    it('allows admin to edit any course', () => {
      const admin = new User(
        'admin-123',
        Email.create('admin@example.com'),
        'admin',
        'Admin',
        'User',
        UserRole.create(UserRoleEnum.ADMIN),
        true,
        new Date()
      )
      const course = new Course('course-123', 'Test', 'Desc', 'creator-456', [], false, new Date())

      expect(course.canEdit(admin)).toBe(true)
    })

    it('denies non-creator, non-admin user', () => {
      const otherUser = new User(
        'other-user',
        Email.create('other@example.com'),
        'other',
        'Other',
        'User',
        UserRole.create(UserRoleEnum.FREE),
        true,
        new Date()
      )
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [], false, new Date())

      expect(course.canEdit(otherUser)).toBe(false)
    })
  })

  describe('canDelete(user)', () => {
    it('allows creator to delete course', () => {
      const creator = new User(
        'creator-123',
        Email.create('creator@example.com'),
        'creator',
        'Creator',
        'User',
        UserRole.create(UserRoleEnum.FREE),
        true,
        new Date()
      )
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [], false, new Date())

      expect(course.canDelete(creator)).toBe(true)
    })

    it('allows admin to delete any course', () => {
      const admin = new User(
        'admin-123',
        Email.create('admin@example.com'),
        'admin',
        'Admin',
        'User',
        UserRole.create(UserRoleEnum.ADMIN),
        true,
        new Date()
      )
      const course = new Course('course-123', 'Test', 'Desc', 'creator-456', [], false, new Date())

      expect(course.canDelete(admin)).toBe(true)
    })

    it('denies non-creator, non-admin user', () => {
      const otherUser = createTestUser()
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [], false, new Date())

      expect(course.canDelete(otherUser)).toBe(false)
    })
  })

  describe('canPublish()', () => {
    it('requires at least one chapter', () => {
      const course = createTestCourse([])
      expect(course.canPublish()).toBe(false)
    })

    it('requires at least one lesson in a chapter', () => {
      const emptyChapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [])
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [emptyChapter], false, new Date())

      expect(course.canPublish()).toBe(false)
    })

    it('allows publishing when chapter has lessons', () => {
      const lesson = createTestLesson('l1', 'ch1')
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson])
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [chapter], false, new Date())

      expect(course.canPublish()).toBe(true)
    })

    it('allows publishing with multiple chapters and lessons', () => {
      const lesson1 = createTestLesson('l1', 'ch1')
      const lesson2 = createTestLesson('l2', 'ch2')
      const chapter1 = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson1])
      const chapter2 = new Chapter('ch2', 'course-123', 'Chapter 2', 2, [lesson2])
      const course = new Course('course-123', 'Test', 'Desc', 'creator-123', [chapter1, chapter2], false, new Date())

      expect(course.canPublish()).toBe(true)
    })
  })

  describe('isValid()', () => {
    it('requires non-empty title', () => {
      const course = new Course('course-123', '', 'Description', 'creator-123', [], false, new Date())
      expect(course.isValid()).toBe(false)
    })

    it('requires non-empty description', () => {
      const course = new Course('course-123', 'Test', '', 'creator-123', [], false, new Date())
      expect(course.isValid()).toBe(false)
    })

    it('requires valid chapters', () => {
      // Chapter with no title is invalid
      const invalidChapter = new Chapter('ch1', 'course-123', '', 1, [])
      const course = new Course('course-123', 'Test', 'Description', 'creator-123', [invalidChapter], false, new Date())

      expect(course.isValid()).toBe(false)
    })

    it('is valid with all required fields', () => {
      const lesson = createTestLesson('l1', 'ch1')
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson])
      const course = new Course('course-123', 'Test', 'Description', 'creator-123', [chapter], false, new Date())

      expect(course.isValid()).toBe(true)
    })

    it('handles courses with no chapters', () => {
      const course = new Course('course-123', 'Test', 'Description', 'creator-123', [], false, new Date())
      // Valid structure even without chapters
      expect(course.isValid()).toBe(true)
    })
  })

  describe('fromAPI(data)', () => {
    it('transforms API data with snake_case to camelCase', () => {
      const apiData = {
        id: 'course-123',
        title: 'My Course',
        description: 'My Description',
        creator_id: 'user-456',
        chapters: [],
        is_published: false,
        created_at: '2026-01-19T10:00:00Z'
      }

      const course = Course.fromAPI(apiData)

      expect(course.id).toBe('course-123')
      expect(course.title).toBe('My Course')
      expect(course.description).toBe('My Description')
      expect(course.creatorId).toBe('user-456')
      expect(course.isPublished).toBe(false)
      expect(course.createdAt).toBeInstanceOf(Date)
    })

    it('handles camelCase API data', () => {
      const apiData = {
        id: 'course-123',
        title: 'My Course',
        description: 'My Description',
        creatorId: 'user-456',
        chapters: [],
        isPublished: false,
        createdAt: '2026-01-19T10:00:00Z'
      }

      const course = Course.fromAPI(apiData)

      expect(course.creatorId).toBe('user-456')
      expect(course.isPublished).toBe(false)
    })

    it('transforms nested chapters', () => {
      const apiData = {
        id: 'course-123',
        title: 'My Course',
        description: 'Description',
        creator_id: 'user-456',
        chapters: [
          {
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
              }
            ]
          }
        ],
        is_published: false,
        created_at: '2026-01-19T10:00:00Z'
      }

      const course = Course.fromAPI(apiData)

      expect(course.chapters).toHaveLength(1)
      expect(course.chapters[0].title).toBe('Chapter 1')
      expect(course.chapters[0].lessons).toHaveLength(1)
      expect(course.chapters[0].lessons[0].title).toBe('Lesson 1')
    })

    it('handles updatedAt timestamp when provided', () => {
      const apiData = {
        id: 'course-123',
        title: 'My Course',
        description: 'Description',
        creator_id: 'user-456',
        chapters: [],
        is_published: true,
        created_at: '2026-01-19T10:00:00Z',
        updated_at: '2026-01-20T15:30:00Z'
      }

      const course = Course.fromAPI(apiData)

      expect(course.updatedAt).toBeInstanceOf(Date)
      expect(course.updatedAt?.toISOString()).toContain('2026-01-20')
    })

    it('handles undefined updatedAt', () => {
      const apiData = {
        id: 'course-123',
        title: 'My Course',
        description: 'Description',
        creator_id: 'user-456',
        chapters: [],
        is_published: false,
        created_at: '2026-01-19T10:00:00Z'
      }

      const course = Course.fromAPI(apiData)

      expect(course.updatedAt).toBeUndefined()
    })
  })

  describe('toJSON()', () => {
    it('includes all course fields', () => {
      const lesson = createTestLesson('l1', 'ch1', ['user-123'])
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson])
      const course = new Course('course-123', 'Test', 'Description', 'creator-123', [chapter], true, new Date('2024-01-01'))

      const json = course.toJSON() as any

      expect(json.id).toBe('course-123')
      expect(json.title).toBe('Test')
      expect(json.description).toBe('Description')
      expect(json.creatorId).toBe('creator-123')
      expect(json.isPublished).toBe(true)
      expect(json.status).toBe('published')
      expect(json.totalChapters).toBe(1)
      expect(json.totalLessons).toBe(1)
    })

    it('includes computed properties', () => {
      const lesson = createTestLesson('l1', 'ch1', ['user-123'])
      const chapter = new Chapter('ch1', 'course-123', 'Chapter 1', 1, [lesson])
      const course = new Course('course-123', 'Test', 'Description', 'creator-123', [chapter], false, new Date())

      const json = course.toJSON() as any

      expect(json.displayTitle).toBe('Test')
      expect(json.totalChapters).toBe(1)
      expect(json.totalLessons).toBe(1)
      expect(json.sortedChapters).toBeDefined()
    })

    it('serializes dates to ISO strings', () => {
      const course = new Course(
        'course-123',
        'Test',
        'Description',
        'creator-123',
        [],
        false,
        new Date('2024-01-01T10:00:00Z'),
        new Date('2024-01-02T15:30:00Z')
      )

      const json = course.toJSON() as any

      expect(json.createdAt).toBe('2024-01-01T10:00:00.000Z')
      expect(json.updatedAt).toBe('2024-01-02T15:30:00.000Z')
    })
  })
})
