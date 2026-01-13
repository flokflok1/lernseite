/**
 * Course Types - Course Structure Definitions
 *
 * Defines the hierarchical course structure: Course → Chapters → Lessons.
 *
 * @module kurs-builder/types/course
 */

/**
 * Course
 *
 * Top-level course entity.
 */
export interface Course {
  /** Unique course identifier */
  course_id: string

  /** Course title */
  title: string

  /** Course description */
  description?: string

  /** Course status */
  status?: 'draft' | 'published' | 'archived'

  /** Category ID */
  category_id?: string

  /** Created timestamp */
  created_at?: string

  /** Updated timestamp */
  updated_at?: string
}

/**
 * Chapter
 *
 * A chapter within a course (hierarchical container for lessons).
 */
export interface Chapter {
  /** Unique chapter identifier */
  id: string

  /** Parent course ID */
  course_id: string

  /** Chapter title */
  title: string

  /** Chapter description */
  description?: string

  /** Display order */
  order: number

  /** Nested lessons */
  lessons?: Lesson[]

  /** Theory content count */
  theory_count?: number

  /** Created timestamp */
  created_at?: string
}

/**
 * Lesson
 *
 * A lesson within a chapter (contains learning methods).
 */
export interface Lesson {
  /** Unique lesson identifier */
  id: string

  /** Parent chapter ID */
  chapter_id: string

  /** Lesson title */
  title: string

  /** Lesson description */
  description?: string

  /** Display order */
  order: number

  /** Learning method instances */
  methods?: LearningMethodInstance[]

  /** Explanation count */
  explanation_count?: number

  /** Created timestamp */
  created_at?: string
}

/**
 * Learning Method Instance
 *
 * An instance of a learning method within a lesson.
 */
export interface LearningMethodInstance {
  /** Unique instance identifier */
  id: string

  /** Parent lesson ID */
  lesson_id: string

  /** Learning method type (0-11) */
  method_type: number

  /** Method display title */
  title: string

  /** Method configuration (JSONB) */
  config?: Record<string, any>

  /** Method content (JSONB) */
  content?: Record<string, any>

  /** Display order */
  order: number

  /** Active status */
  active: boolean
}

/**
 * Draft Structure
 *
 * The current draft state of course structure during authoring.
 */
export interface DraftStructure {
  /** Course ID */
  course_id: string

  /** Draft chapters with nested lessons */
  chapters: Chapter[]

  /** Draft version number */
  version: number

  /** Last updated timestamp */
  updated_at: string

  /** Unsaved changes indicator */
  has_changes: boolean
}

/**
 * Draft Statistics
 *
 * Statistics about the draft structure.
 */
export interface DraftStats {
  /** Number of chapters */
  chapters: number

  /** Number of lessons across all chapters */
  lessons: number

  /** Number of learning method instances */
  methods: number

  /** Estimated completion percentage */
  completion?: number
}
