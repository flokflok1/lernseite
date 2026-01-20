/**
 * LernsystemX - Course Editor Store (Pinia)
 *
 * Manages:
 * - Current course being edited
 * - Chapters and lessons structure
 * - Dirty state (unsaved changes)
 * - Save/discard operations
 *
 * Refactored: modules → chapters (2025-11-27)
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  EditableCourse,
  EditableChapter,
  EditableLesson,
  CreateCoursePayload,
  UpdateCoursePayload,
  ChapterPayload,
  UpdateChapterPayload,
  LessonPayload,
  UpdateLessonPayload,
} from '@/infrastructure/api/clients/content'
import * as coursesApi from '@/infrastructure/api/clients/content'
import { toCourseDomain, toChapterDomain, fromChapterDomain, fromLessonDomain } from './adapters'
import { Course } from '@/domain/models/course/Course.model'
import { Chapter } from '@/domain/models/course/Chapter.model'

export const useCourseEditorStore = defineStore('courseEditor', () => {
  // State
  const currentCourse = ref<EditableCourse | null>(null)
  const chapters = ref<EditableChapter[]>([])
  const lessonsByChapterId = ref<Record<string, EditableLesson[]>>({})  // chapter_id is UUID string
  const selectedChapterId = ref<string | null>(null)
  const selectedLessonId = ref<number | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const dirty = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const hasCourse = computed(() => !!currentCourse.value)

  const isDirty = computed(() => dirty.value)

  const currentChapter = computed(() => {
    if (!selectedChapterId.value) return null
    return chapters.value.find((c) => c.chapter_id === selectedChapterId.value) || null
  })

  const currentLesson = computed(() => {
    if (!selectedLessonId.value || !selectedChapterId.value) return null
    const chapterLessons = lessonsByChapterId.value[selectedChapterId.value] || []
    return chapterLessons.find((l) => l.lesson_id === selectedLessonId.value) || null
  })

  const sortedChapters = computed(() => {
    // ✅ REFACTORED: Delegate to Course domain model
    // Transform API types → Domain model → Sorting via domain getter → Transform back to API types
    if (!currentCourse.value) return []

    const courseDomain = toCourseDomain(currentCourse.value, chapters.value, lessonsByChapterId.value)
    const sortedDomainChapters = courseDomain.sortedChapters

    return sortedDomainChapters.map((domainChapter) => {
      const originalChapter = chapters.value.find(c => c.chapter_id === domainChapter.id)
      return originalChapter ? fromChapterDomain(domainChapter, originalChapter) : null
    }).filter((c): c is EditableChapter => c !== null)
  })

  const sortedLessons = (chapterId: string) => {
    // ✅ REFACTORED: Delegate to Chapter domain model
    // Transform API types → Domain model → Sorting via domain getter → Transform back to API types
    const lessons = lessonsByChapterId.value[chapterId] || []
    if (lessons.length === 0) return []

    const chapterData = chapters.value.find(c => c.chapter_id === chapterId)
    if (!chapterData) return lessons

    const chapterDomain = toChapterDomain(chapterData, lessons)
    const sortedDomainLessons = chapterDomain.sortedLessons

    return sortedDomainLessons.map(domainLesson => {
      const originalLesson = lessons.find(l => l.lesson_id === domainLesson.id)
      return originalLesson ? fromLessonDomain(domainLesson, originalLesson) : null
    }).filter((l): l is EditableLesson => l !== null)
  }

  const canPublishCourse = computed(() => {
    // ✅ REFACTORED: Uses Course domain model's canPublish() validation
    if (!currentCourse.value) return false

    const courseDomain = toCourseDomain(currentCourse.value, chapters.value, lessonsByChapterId.value)
    return courseDomain.canPublish()
  })

  const courseIsValid = computed(() => {
    // ✅ REFACTORED: Uses Course domain model's isValid() validation
    if (!currentCourse.value) return false

    const courseDomain = toCourseDomain(currentCourse.value, chapters.value, lessonsByChapterId.value)
    return courseDomain.isValid()
  })

  // Actions

  /**
   * Load course and all its chapters & lessons for editing
   */
  const loadCourseForEdit = async (courseId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      // Load course
      currentCourse.value = await coursesApi.getCourseForEdit(courseId)

      // Load chapters
      chapters.value = await coursesApi.getChaptersForEdit(courseId)

      // Load lessons for each chapter
      lessonsByChapterId.value = {}
      for (const chapter of chapters.value) {
        const lessons = await coursesApi.getLessonsForEdit(chapter.chapter_id)
        lessonsByChapterId.value[chapter.chapter_id] = lessons
      }

      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to load course'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a new course (empty state)
   */
  const createNewCourse = async (initialData?: Partial<CreateCoursePayload>): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const payload: CreateCoursePayload = {
        title: initialData?.title || 'Neuer Kurs',
        subtitle: initialData?.subtitle,
        description: initialData?.description || '',
        level: initialData?.level || 'beginner',
        language: initialData?.language || 'de',
        visibility: initialData?.visibility || 'private',
        tags: initialData?.tags || [],
        learning_goals: initialData?.learning_goals || [],
        requirements: initialData?.requirements || [],
      }

      currentCourse.value = await coursesApi.createCourse(payload)
      chapters.value = []
      lessonsByChapterId.value = {}
      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to create course'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update course metadata (local + API)
   * ✅ REFACTORED: Validates using Course domain model
   */
  const updateCourseMeta = async (partialMeta: UpdateCoursePayload): Promise<void> => {
    if (!currentCourse.value) {
      throw new Error('No course loaded')
    }

    saving.value = true
    error.value = null

    try {
      // Create temporary domain model to validate changes
      const tmpCourse = toCourseDomain(
        { ...currentCourse.value, ...partialMeta },
        chapters.value,
        lessonsByChapterId.value
      )

      // Validate before saving
      if (!tmpCourse.isValid()) {
        throw new Error('Course metadata is invalid')
      }

      currentCourse.value = await coursesApi.updateCourse(
        currentCourse.value.course_id,
        partialMeta
      )
      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to update course'
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Add a new chapter to the current course
   */
  const addChapter = async (title: string): Promise<EditableChapter> => {
    if (!currentCourse.value) {
      throw new Error('No course loaded')
    }

    saving.value = true
    error.value = null

    try {
      const payload: ChapterPayload = {
        course_id: currentCourse.value.course_id,
        title,
        order_index: chapters.value.length + 1,
      }

      const newChapter = await coursesApi.createChapter(payload)
      chapters.value.push(newChapter)
      lessonsByChapterId.value[newChapter.chapter_id] = []
      dirty.value = false

      return newChapter
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to add chapter'
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Update chapter (title, description, etc.)
   */
  const updateChapterMeta = async (
    chapterId: string,
    payload: UpdateChapterPayload
  ): Promise<void> => {
    saving.value = true
    error.value = null

    try {
      const updatedChapter = await coursesApi.updateChapter(chapterId, payload)

      // Update local state
      const index = chapters.value.findIndex((c) => c.chapter_id === chapterId)
      if (index !== -1) {
        chapters.value[index] = updatedChapter
      }

      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to update chapter'
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Remove chapter and all its lessons
   */
  const removeChapter = async (chapterId: string): Promise<void> => {
    saving.value = true
    error.value = null

    try {
      await coursesApi.deleteChapter(chapterId)

      // Remove from local state
      chapters.value = chapters.value.filter((c) => c.chapter_id !== chapterId)
      delete lessonsByChapterId.value[chapterId]

      if (selectedChapterId.value === chapterId) {
        selectedChapterId.value = null
        selectedLessonId.value = null
      }

      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to remove chapter'
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Reorder chapters
   */
  const reorderChapters = async (reorderedChapters: EditableChapter[]): Promise<void> => {
    if (!currentCourse.value) {
      throw new Error('No course loaded')
    }

    saving.value = true
    error.value = null

    try {
      const items = reorderedChapters.map((chap, index) => ({
        id: chap.chapter_id,
        order_index: index + 1,
      }))

      await coursesApi.reorderChapters(currentCourse.value.course_id, { items })

      // Update local state
      chapters.value = reorderedChapters.map((chap, index) => ({
        ...chap,
        order_index: index + 1,
      }))

      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to reorder chapters'
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Add a new lesson to a chapter
   */
  const addLesson = async (chapterId: string, title: string): Promise<EditableLesson> => {
    saving.value = true
    error.value = null

    try {
      const currentLessons = lessonsByChapterId.value[chapterId] || []

      const payload: LessonPayload = {
        chapter_id: chapterId,
        title,
        lesson_type: 'text',
        order_index: currentLessons.length + 1,
      }

      const newLesson = await coursesApi.createLesson(payload)

      // Add to local state
      if (!lessonsByChapterId.value[chapterId]) {
        lessonsByChapterId.value[chapterId] = []
      }
      lessonsByChapterId.value[chapterId].push(newLesson)

      dirty.value = false

      return newLesson
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to add lesson'
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Update lesson metadata
   */
  const updateLessonMeta = async (
    lessonId: number,
    payload: UpdateLessonPayload
  ): Promise<void> => {
    saving.value = true
    error.value = null

    try {
      const updatedLesson = await coursesApi.updateLesson(lessonId, payload)

      // Update local state
      const chapterId = updatedLesson.chapter_id
      const chapterLessons = lessonsByChapterId.value[chapterId] || []
      const index = chapterLessons.findIndex((l) => l.lesson_id === lessonId)
      if (index !== -1) {
        chapterLessons[index] = updatedLesson
      }

      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to update lesson'
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Remove lesson
   */
  const removeLesson = async (chapterId: string, lessonId: number): Promise<void> => {
    saving.value = true
    error.value = null

    try {
      await coursesApi.deleteLesson(lessonId)

      // Remove from local state
      const chapterLessons = lessonsByChapterId.value[chapterId] || []
      lessonsByChapterId.value[chapterId] = chapterLessons.filter((l) => l.lesson_id !== lessonId)

      if (selectedLessonId.value === lessonId) {
        selectedLessonId.value = null
      }

      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to remove lesson'
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Reorder lessons within a chapter
   */
  const reorderLessons = async (chapterId: string, reorderedLessons: EditableLesson[]): Promise<void> => {
    saving.value = true
    error.value = null

    try {
      const items = reorderedLessons.map((lesson, index) => ({
        id: lesson.lesson_id,
        order_index: index + 1,
      }))

      await coursesApi.reorderLessons(chapterId, { items })

      // Update local state
      lessonsByChapterId.value[chapterId] = reorderedLessons.map((lesson, index) => ({
        ...lesson,
        order_index: index + 1,
      }))

      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to reorder lessons'
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Update lesson content (text, video, quiz data, etc.)
   */
  const updateLessonContent = async (lessonId: number, content: any): Promise<void> => {
    return updateLessonMeta(lessonId, { content })
  }

  /**
   * Save all changes (currently just marks dirty as false, actual saves happen per operation)
   */
  const saveAllChanges = async (): Promise<void> => {
    // In current implementation, changes are saved immediately per operation
    // This function could be extended for batch saves if needed
    dirty.value = false
  }

  /**
   * Discard all unsaved changes (reload from server)
   */
  const discardChanges = async (): Promise<void> => {
    if (!currentCourse.value) return

    await loadCourseForEdit(currentCourse.value.course_id)
    dirty.value = false
  }

  /**
   * Mark as dirty (unsaved changes)
   */
  const markDirty = (): void => {
    dirty.value = true
  }

  /**
   * Select a chapter
   */
  const selectChapter = (chapterId: string | null): void => {
    selectedChapterId.value = chapterId
    selectedLessonId.value = null
  }

  /**
   * Select a lesson
   */
  const selectLesson = (chapterId: string, lessonId: number): void => {
    selectedChapterId.value = chapterId
    selectedLessonId.value = lessonId
  }

  /**
   * Clear editor state
   */
  const clearEditor = (): void => {
    currentCourse.value = null
    chapters.value = []
    lessonsByChapterId.value = {}
    selectedChapterId.value = null
    selectedLessonId.value = null
    dirty.value = false
    error.value = null
  }

  /**
   * Publish course
   * ✅ REFACTORED: Uses Course domain model's canPublish() validation
   */
  const publishCourse = async (): Promise<void> => {
    if (!currentCourse.value) {
      throw new Error('No course loaded')
    }

    saving.value = true
    error.value = null

    try {
      // Validate using domain model before publishing
      const courseDomain = toCourseDomain(currentCourse.value, chapters.value, lessonsByChapterId.value)

      if (!courseDomain.canPublish()) {
        throw new Error('Course must have at least one chapter with lessons before publishing')
      }

      currentCourse.value = await coursesApi.publishCourse(currentCourse.value.course_id)
      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to publish course'
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Unpublish course
   */
  const unpublishCourse = async (): Promise<void> => {
    if (!currentCourse.value) {
      throw new Error('No course loaded')
    }

    saving.value = true
    error.value = null

    try {
      currentCourse.value = await coursesApi.unpublishCourse(currentCourse.value.course_id)
      dirty.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to unpublish course'
      throw err
    } finally {
      saving.value = false
    }
  }

  return {
    // State
    currentCourse,
    chapters,
    lessonsByChapterId,
    selectedChapterId,
    selectedLessonId,
    loading,
    saving,
    dirty,
    error,

    // Getters
    hasCourse,
    isDirty,
    currentChapter,
    currentLesson,
    sortedChapters,
    sortedLessons,
    canPublishCourse,
    courseIsValid,

    // Actions
    loadCourseForEdit,
    createNewCourse,
    updateCourseMeta,
    addChapter,
    updateChapterMeta,
    removeChapter,
    reorderChapters,
    addLesson,
    updateLessonMeta,
    removeLesson,
    reorderLessons,
    updateLessonContent,
    saveAllChanges,
    discardChanges,
    markDirty,
    selectChapter,
    selectLesson,
    clearEditor,
    publishCourse,
    unpublishCourse,
  }
})
