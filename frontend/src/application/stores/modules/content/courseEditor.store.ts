/**
 * LernsystemX - Course Editor Store (Pinia)
 *
 * Manages:
 * - Current course being edited
 * - Chapters and lessons structure
 * - Dirty state (unsaved changes)
 * - Save/discard operations
 *
 * Chapter/lesson CRUD operations are in courseEditor.chapters.ts
 *
 * Refactored: modules -> chapters (2025-11-27)
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  EditableCourse,
  EditableChapter,
  EditableLesson,
  CreateCoursePayload,
  UpdateCoursePayload,
  UpdateLessonPayload,
} from '@/infrastructure/api/clients/panel/editor'
import * as coursesApi from '@/infrastructure/api/clients/panel/editor'
import { toCourseDomain, toChapterDomain, fromChapterDomain, fromLessonDomain } from './adapters'
import * as chapterOps from './courseEditor.chapters'

export const useCourseEditorStore = defineStore('courseEditor', () => {
  // State
  const currentCourse = ref<EditableCourse | null>(null)
  const chapters = ref<EditableChapter[]>([])
  const lessonsByChapterId = ref<Record<string, EditableLesson[]>>({})
  const selectedChapterId = ref<string | null>(null)
  const selectedLessonId = ref<number | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const dirty = ref(false)
  const error = ref<string | null>(null)

  // Shared refs object for chapter/lesson operations
  const editorRefs = {
    currentCourse,
    chapters,
    lessonsByChapterId,
    selectedChapterId,
    selectedLessonId,
    saving,
    dirty,
    error,
  }

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
    if (!currentCourse.value) return []

    const courseDomain = toCourseDomain(currentCourse.value, chapters.value, lessonsByChapterId.value)
    const sortedDomainChapters = courseDomain.sortedChapters

    return sortedDomainChapters.map((domainChapter) => {
      const originalChapter = chapters.value.find(c => c.chapter_id === domainChapter.id)
      return originalChapter ? fromChapterDomain(domainChapter, originalChapter) : null
    }).filter((c): c is EditableChapter => c !== null)
  })

  const sortedLessons = (chapterId: string) => {
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
    if (!currentCourse.value) return false
    const courseDomain = toCourseDomain(currentCourse.value, chapters.value, lessonsByChapterId.value)
    return courseDomain.canPublish()
  })

  const courseIsValid = computed(() => {
    if (!currentCourse.value) return false
    const courseDomain = toCourseDomain(currentCourse.value, chapters.value, lessonsByChapterId.value)
    return courseDomain.isValid()
  })

  // Actions

  /**
   * Load course and all its chapters and lessons for editing
   */
  const loadCourseForEdit = async (courseId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      currentCourse.value = await coursesApi.getCourseForEdit(courseId)
      chapters.value = await coursesApi.getChaptersForEdit(courseId)

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
   * Create a new course
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
   */
  const updateCourseMeta = async (partialMeta: UpdateCoursePayload): Promise<void> => {
    if (!currentCourse.value) {
      throw new Error('No course loaded')
    }

    saving.value = true
    error.value = null

    try {
      const tmpCourse = toCourseDomain(
        { ...currentCourse.value, ...partialMeta },
        chapters.value,
        lessonsByChapterId.value
      )

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
   * Update lesson content (text, video, quiz data, etc.)
   */
  const updateLessonContent = async (lessonId: number, content: any): Promise<void> => {
    return chapterOps.updateLessonMeta(editorRefs, lessonId, { content } as UpdateLessonPayload)
  }

  /**
   * Save all changes (marks dirty as false; actual saves happen per operation)
   */
  const saveAllChanges = async (): Promise<void> => {
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
   */
  const publishCourse = async (): Promise<void> => {
    if (!currentCourse.value) {
      throw new Error('No course loaded')
    }

    saving.value = true
    error.value = null

    try {
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

  // Delegated chapter/lesson actions (bound to shared refs)
  const addChapter = (title: string) => chapterOps.addChapter(editorRefs, title)
  const updateChapterMeta = (chapterId: string, payload: any) =>
    chapterOps.updateChapterMeta(editorRefs, chapterId, payload)
  const removeChapter = (chapterId: string) => chapterOps.removeChapter(editorRefs, chapterId)
  const reorderChapters = (reordered: EditableChapter[]) =>
    chapterOps.reorderChapters(editorRefs, reordered)
  const addLesson = (chapterId: string, title: string) =>
    chapterOps.addLesson(editorRefs, chapterId, title)
  const updateLessonMeta = (lessonId: number, payload: any) =>
    chapterOps.updateLessonMeta(editorRefs, lessonId, payload)
  const removeLesson = (chapterId: string, lessonId: number) =>
    chapterOps.removeLesson(editorRefs, chapterId, lessonId)
  const reorderLessons = (chapterId: string, reordered: EditableLesson[]) =>
    chapterOps.reorderLessons(editorRefs, chapterId, reordered)

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
