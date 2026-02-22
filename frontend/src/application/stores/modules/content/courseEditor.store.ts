/**
 * Course Editor Store — course editing state, chapters, lessons, dirty/save.
 * Chapter/lesson CRUD: courseEditor.chapters.ts
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  EditableCourse,
  EditableChapter,
  EditableLesson,
  CreateCoursePayload,
  UpdateCoursePayload,
  UpdateChapterPayload,
  UpdateLessonPayload,
  CourseListItem,
  CategoryTreeResponse,
} from '@/infrastructure/api/clients/panel/editor'
import * as coursesApi from '@/infrastructure/api/clients/panel/editor'
import { toCourseDomain, toChapterDomain, fromChapterDomain, fromLessonDomain } from './adapters'
import * as chapterOps from './courseEditor.chapters'
import { i18n } from '@/infrastructure/plugins/i18n'

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
  const courseList = ref<CourseListItem[]>([])
  const courseListLoading = ref(false)
  const pendingContent = ref<{ lessonId: number; html: string } | null>(null)

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

  /** Translate using the global i18n instance (safe outside Vue components) */
  const t = (key: string): string => {
    const composer = i18n.global
    return typeof composer.t === 'function' ? composer.t(key) : key
  }

  /** Extract error message from API error, with i18n fallback key */
  const extractErrorMessage = (err: unknown, fallbackKey: string): string => {
    if (err instanceof Error) {
      const axiosErr = err as Error & { response?: { data?: { message?: string } } }
      return axiosErr.response?.data?.message || t(fallbackKey)
    }
    return t(fallbackKey)
  }

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
      const lessonResults = await Promise.all(
        chapters.value.map(c => coursesApi.getLessonsForEdit(c.chapter_id))
      )
      chapters.value.forEach((chapter, i) => {
        lessonsByChapterId.value[chapter.chapter_id] = lessonResults[i]
      })

      dirty.value = false
    } catch (err: unknown) {
      error.value = extractErrorMessage(err, 'panel.manualEditor.errors.loadFailed')
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
        title: initialData?.title || t('panel.manualEditor.courseSelector.defaultTitle'),
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
    } catch (err: unknown) {
      error.value = extractErrorMessage(err, 'panel.manualEditor.errors.createFailed')
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
      throw new Error(t('panel.manualEditor.errors.loadFailed'))
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
        throw new Error(t('panel.manualEditor.errors.updateFailed'))
      }

      currentCourse.value = await coursesApi.updateCourse(
        currentCourse.value.course_id,
        partialMeta
      )
      dirty.value = false
    } catch (err: unknown) {
      error.value = extractErrorMessage(err, 'panel.manualEditor.errors.updateFailed')
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * Update lesson content immediately via API (used for non-TipTap content updates)
   */
  const updateLessonContent = async (lessonId: number, content: string): Promise<void> => {
    return chapterOps.updateLessonMeta(editorRefs, lessonId, { content })
  }

  /**
   * Buffer TipTap content locally without hitting the API.
   * Updates the in-memory lesson data (for preview) and marks dirty.
   * Content is flushed to API by saveAllChanges() after debounce.
   */
  const setLocalContent = (lessonId: number, html: string): void => {
    pendingContent.value = { lessonId, html }

    // Update in-memory lesson data so Preview tab reflects changes immediately
    for (const lessons of Object.values(lessonsByChapterId.value)) {
      const lesson = lessons.find(l => l.lesson_id === lessonId)
      if (lesson) {
        lesson.content = html
        break
      }
    }
    dirty.value = true
  }

  /**
   * Flush pending content to API and clear dirty flag.
   * On failure: restores pendingContent so the next save attempt retries.
   */
  const saveAllChanges = async (): Promise<void> => {
    if (saving.value) return  // Guard: prevent concurrent saves
    const pending = pendingContent.value
    if (!pending) { dirty.value = false; return }
    pendingContent.value = null
    try {
      await updateLessonContent(pending.lessonId, pending.html)
      // Only clear dirty if no new content was buffered during the async save
      if (!pendingContent.value) {
        dirty.value = false
      }
    } catch (err) {
      // Restore only if no newer content has been buffered
      if (!pendingContent.value) {
        pendingContent.value = pending
      }
      dirty.value = true
      throw err
    }
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
      throw new Error(t('panel.manualEditor.errors.loadFailed'))
    }

    saving.value = true
    error.value = null

    try {
      const courseDomain = toCourseDomain(currentCourse.value, chapters.value, lessonsByChapterId.value)

      if (!courseDomain.canPublish()) {
        throw new Error(t('panel.manualEditor.errors.publishFailed'))
      }

      await coursesApi.updateCourseStatus(currentCourse.value.course_id, 'publish')
      currentCourse.value = await coursesApi.getCourseForEdit(currentCourse.value.course_id)
      dirty.value = false
    } catch (err: unknown) {
      error.value = extractErrorMessage(err, 'panel.manualEditor.errors.publishFailed')
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
      throw new Error(t('panel.manualEditor.errors.loadFailed'))
    }

    saving.value = true
    error.value = null

    try {
      await coursesApi.updateCourseStatus(currentCourse.value.course_id, 'unpublish')
      currentCourse.value = await coursesApi.getCourseForEdit(currentCourse.value.course_id)
      dirty.value = false
    } catch (err: unknown) {
      error.value = extractErrorMessage(err, 'panel.manualEditor.errors.unpublishFailed')
      throw err
    } finally {
      saving.value = false
    }
  }

  /**
   * List courses owned by current user
   * @param status - Filter: 'active' (default), 'archived', 'trash', 'all'
   */
  const listCourses = async (status?: string): Promise<void> => {
    courseListLoading.value = true
    error.value = null
    try {
      courseList.value = await coursesApi.listEditorCourses(status)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err, 'panel.manualEditor.errors.listFailed')
    } finally {
      courseListLoading.value = false
    }
  }

  /** Run a course-list action: API call → remove from local list → surface errors */
  const courseListAction = async (
    action: () => Promise<unknown>,
    courseId: number,
    fallbackMsg: string
  ): Promise<void> => {
    try {
      await action()
      courseList.value = courseList.value.filter(c => c.course_id !== courseId)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err, fallbackMsg)
    }
  }

  const trashCourse = (courseId: number) =>
    courseListAction(() => coursesApi.deleteCourse(courseId), courseId, 'panel.manualEditor.errors.genericError')
  const restoreFromTrash = (courseId: number) =>
    courseListAction(() => coursesApi.updateCourseStatus(courseId, 'restore'), courseId, 'panel.manualEditor.errors.genericError')
  const archiveCourse = (courseId: number) =>
    courseListAction(() => coursesApi.updateCourseStatus(courseId, 'archive'), courseId, 'panel.manualEditor.errors.genericError')
  const unarchiveCourse = (courseId: number) =>
    courseListAction(() => coursesApi.updateCourseStatus(courseId, 'unarchive'), courseId, 'panel.manualEditor.errors.genericError')
  const permanentDelete = (courseId: number) =>
    courseListAction(() => coursesApi.updateCourseStatus(courseId, 'purge'), courseId, 'panel.manualEditor.errors.genericError')

  // Delegated chapter/lesson actions (bound to shared refs)
  const addChapter = (title: string) => chapterOps.addChapter(editorRefs, title)
  const updateChapterMeta = (chapterId: string, payload: UpdateChapterPayload) =>
    chapterOps.updateChapterMeta(editorRefs, chapterId, payload)
  const removeChapter = (chapterId: string) => chapterOps.removeChapter(editorRefs, chapterId)
  const reorderChapters = (reordered: EditableChapter[]) =>
    chapterOps.reorderChapters(editorRefs, reordered)
  const addLesson = (chapterId: string, title: string) =>
    chapterOps.addLesson(editorRefs, chapterId, title)
  const updateLessonMeta = (lessonId: number, payload: UpdateLessonPayload) =>
    chapterOps.updateLessonMeta(editorRefs, lessonId, payload)
  const removeLesson = (chapterId: string, lessonId: number) =>
    chapterOps.removeLesson(editorRefs, chapterId, lessonId)
  const reorderLessons = (chapterId: string, reordered: EditableLesson[]) =>
    chapterOps.reorderLessons(editorRefs, chapterId, reordered)

  // Categories
  const categoryTree = ref<CategoryTreeResponse | null>(null)
  const loadingCategories = ref(false)

  const loadCategories = async () => {
    loadingCategories.value = true
    try {
      const result = await coursesApi.getCategoryTree()
      categoryTree.value = result
    } catch (err: unknown) {
      error.value = extractErrorMessage(err, 'panel.manualEditor.errors.loadFailed')
      categoryTree.value = null
    } finally {
      loadingCategories.value = false
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
    courseList,
    courseListLoading,

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
    setLocalContent,
    saveAllChanges,
    discardChanges,
    markDirty,
    selectChapter,
    selectLesson,
    clearEditor,
    publishCourse,
    unpublishCourse,
    listCourses,
    trashCourse,
    restoreFromTrash,
    archiveCourse,
    unarchiveCourse,
    permanentDelete,
    categoryTree,
    loadingCategories,
    loadCategories,
  }
})
