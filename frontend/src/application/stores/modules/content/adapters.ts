/**
 * Transformation Adapter Layer
 *
 * Converts between API types (EditableX) and domain models
 * Used in courseEditor store for delegating business logic to domain models
 * while maintaining API type compatibility for store state
 */

import type { EditableCourse, EditableChapter, EditableLesson } from '@/infrastructure/api/clients/content'
import { Course } from '@/domain/models/course/Course.model'
import { Chapter } from '@/domain/models/course/Chapter.model'
import { Lesson } from '@/domain/models/course/Lesson.model'

/**
 * Convert EditableLesson (API type) to Lesson domain model
 *
 * @param editable - API type from server
 * @returns Domain model for business logic operations
 *
 * IMPORTANT: EditableLesson.lesson_type (delivery format) ≠ Lesson.learningMethodType (pedagogical method)
 * We default to learningMethodType 0 (LM00) when converting from EditableLesson
 */
export function toLessonDomain(editable: EditableLesson): Lesson {
  return new Lesson(
    String(editable.lesson_id),
    editable.chapter_id,
    editable.title,
    editable.description || '',
    editable.order_index,
    0, // DEFAULT: learningMethodType 0 (LM00) - EditableLesson lacks this field
    editable.is_published,
    [] // Empty completed_by_users for sorting operations
  )
}

/**
 * Convert EditableChapter (API type) to Chapter domain model
 *
 * @param editable - API chapter type
 * @param lessons - Array of EditableLessons for this chapter
 * @returns Domain model with nested lesson domain models
 */
export function toChapterDomain(
  editable: EditableChapter,
  lessons: EditableLesson[]
): Chapter {
  const domainLessons = lessons.map(toLessonDomain)

  return new Chapter(
    editable.chapter_id,
    String(editable.course_id),
    editable.title,
    editable.order_index,
    domainLessons
  )
}

/**
 * Convert EditableCourse (API type) to Course domain model
 *
 * @param editable - API course type
 * @param chapters - Array of EditableChapters with their lessons
 * @returns Domain model with full nested structure
 */
export function toCourseDomain(
  editable: EditableCourse,
  chapters: EditableChapter[],
  lessonsByChapterId: Record<string, EditableLesson[]>
): Course {
  const domainChapters = chapters.map(chapter =>
    toChapterDomain(chapter, lessonsByChapterId[chapter.chapter_id] || [])
  )

  return new Course(
    String(editable.course_id),
    editable.title,
    editable.description || '',
    editable.creator_id,
    domainChapters,
    editable.is_published,
    new Date(editable.created_at)
  )
}

/**
 * Convert sorted domain Lesson back to EditableLesson
 * Used after sorting to maintain API type compatibility
 */
export function fromLessonDomain(domain: Lesson, original: EditableLesson): EditableLesson {
  return {
    ...original,
    order_index: domain.order
  }
}

/**
 * Convert sorted domain Chapter back to EditableChapter
 */
export function fromChapterDomain(domain: Chapter, original: EditableChapter): EditableChapter {
  return {
    ...original,
    order_index: domain.order
  }
}
