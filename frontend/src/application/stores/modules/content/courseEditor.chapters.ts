/**
 * Course Editor - Chapter Operations
 *
 * Extracted from courseEditor.store.ts to keep the orchestrator under 500 LOC.
 * Provides chapter and lesson CRUD actions that mutate shared refs.
 */

import type { Ref } from 'vue'
import type {
  EditableCourse,
  EditableChapter,
  EditableLesson,
  ChapterPayload,
  UpdateChapterPayload,
  LessonPayload,
  UpdateLessonPayload,
} from '@/application/services/api/panel-editor'
import * as coursesApi from '@/application/services/api/panel-editor'

interface EditorRefs {
  currentCourse: Ref<EditableCourse | null>
  chapters: Ref<EditableChapter[]>
  lessonsByChapterId: Ref<Record<string, EditableLesson[]>>
  selectedChapterId: Ref<string | null>
  selectedLessonId: Ref<number | null>
  saving: Ref<boolean>
  dirty: Ref<boolean>
  error: Ref<string | null>
}

/**
 * Extract error message from caught error
 */
function extractErrorMessage(err: unknown, fallback: string): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const response = (err as { response?: { data?: { message?: string } } }).response
    if (response?.data?.message) return response.data.message
  }
  if (err instanceof Error) return err.message
  return fallback
}

/**
 * Add a new chapter to the current course
 */
export async function addChapter(
  refs: EditorRefs,
  title: string
): Promise<EditableChapter> {
  if (!refs.currentCourse.value) {
    throw new Error('No course loaded')
  }

  refs.saving.value = true
  refs.error.value = null

  try {
    const payload: ChapterPayload = {
      course_id: refs.currentCourse.value.course_id,
      title,
      order_index: refs.chapters.value.length + 1,
    }

    const newChapter = await coursesApi.createChapter(payload)
    refs.chapters.value.push(newChapter)
    refs.lessonsByChapterId.value[newChapter.chapter_id] = []
    refs.dirty.value = false

    return newChapter
  } catch (err: unknown) {
    refs.error.value = extractErrorMessage(err, 'Failed to add chapter')
    throw err
  } finally {
    refs.saving.value = false
  }
}

/**
 * Update chapter metadata (title, description, etc.)
 */
export async function updateChapterMeta(
  refs: EditorRefs,
  chapterId: string,
  payload: UpdateChapterPayload
): Promise<void> {
  refs.saving.value = true
  refs.error.value = null

  try {
    const updatedChapter = await coursesApi.updateChapter(chapterId, payload)

    const index = refs.chapters.value.findIndex((c) => c.chapter_id === chapterId)
    if (index !== -1) {
      refs.chapters.value[index] = updatedChapter
    }

    refs.dirty.value = false
  } catch (err: unknown) {
    refs.error.value = extractErrorMessage(err, 'Failed to update chapter')
    throw err
  } finally {
    refs.saving.value = false
  }
}

/**
 * Remove chapter and all its lessons
 */
export async function removeChapter(
  refs: EditorRefs,
  chapterId: string
): Promise<void> {
  refs.saving.value = true
  refs.error.value = null

  try {
    await coursesApi.deleteChapter(chapterId)

    refs.chapters.value = refs.chapters.value.filter((c) => c.chapter_id !== chapterId)
    delete refs.lessonsByChapterId.value[chapterId]

    if (refs.selectedChapterId.value === chapterId) {
      refs.selectedChapterId.value = null
      refs.selectedLessonId.value = null
    }

    refs.dirty.value = false
  } catch (err: unknown) {
    refs.error.value = extractErrorMessage(err, 'Failed to remove chapter')
    throw err
  } finally {
    refs.saving.value = false
  }
}

/**
 * Reorder chapters within a course
 */
export async function reorderChapters(
  refs: EditorRefs,
  reorderedChapters: EditableChapter[]
): Promise<void> {
  if (!refs.currentCourse.value) {
    throw new Error('No course loaded')
  }

  refs.saving.value = true
  refs.error.value = null

  try {
    const items = reorderedChapters.map((chap, index) => ({
      id: chap.chapter_id,
      order_index: index + 1,
    }))

    await coursesApi.reorderChapters(refs.currentCourse.value.course_id, { items })

    refs.chapters.value = reorderedChapters.map((chap, index) => ({
      ...chap,
      order_index: index + 1,
    }))

    refs.dirty.value = false
  } catch (err: unknown) {
    refs.error.value = extractErrorMessage(err, 'Failed to reorder chapters')
    throw err
  } finally {
    refs.saving.value = false
  }
}

/**
 * Add a new lesson to a chapter
 */
export async function addLesson(
  refs: EditorRefs,
  chapterId: string,
  title: string
): Promise<EditableLesson> {
  refs.saving.value = true
  refs.error.value = null

  try {
    const currentLessons = refs.lessonsByChapterId.value[chapterId] || []

    const payload: LessonPayload = {
      chapter_id: chapterId,
      title,
      lesson_type: 'text',
      order_index: currentLessons.length + 1,
    }

    const newLesson = await coursesApi.createLesson(payload)

    if (!refs.lessonsByChapterId.value[chapterId]) {
      refs.lessonsByChapterId.value[chapterId] = []
    }
    refs.lessonsByChapterId.value[chapterId].push(newLesson)

    refs.dirty.value = false

    return newLesson
  } catch (err: unknown) {
    refs.error.value = extractErrorMessage(err, 'Failed to add lesson')
    throw err
  } finally {
    refs.saving.value = false
  }
}

/**
 * Update lesson metadata
 */
export async function updateLessonMeta(
  refs: EditorRefs,
  lessonId: number,
  payload: UpdateLessonPayload
): Promise<void> {
  refs.saving.value = true
  refs.error.value = null

  try {
    const updatedLesson = await coursesApi.updateLesson(lessonId, payload)

    const chapterId = updatedLesson.chapter_id
    const chapterLessons = refs.lessonsByChapterId.value[chapterId] || []
    const index = chapterLessons.findIndex((l) => l.lesson_id === lessonId)
    if (index !== -1) {
      chapterLessons[index] = updatedLesson
    }

    refs.dirty.value = false
  } catch (err: unknown) {
    refs.error.value = extractErrorMessage(err, 'Failed to update lesson')
    throw err
  } finally {
    refs.saving.value = false
  }
}

/**
 * Remove a lesson from a chapter
 */
export async function removeLesson(
  refs: EditorRefs,
  chapterId: string,
  lessonId: number
): Promise<void> {
  refs.saving.value = true
  refs.error.value = null

  try {
    await coursesApi.deleteLesson(lessonId)

    const chapterLessons = refs.lessonsByChapterId.value[chapterId] || []
    refs.lessonsByChapterId.value[chapterId] = chapterLessons.filter(
      (l) => l.lesson_id !== lessonId
    )

    if (refs.selectedLessonId.value === lessonId) {
      refs.selectedLessonId.value = null
    }

    refs.dirty.value = false
  } catch (err: unknown) {
    refs.error.value = extractErrorMessage(err, 'Failed to remove lesson')
    throw err
  } finally {
    refs.saving.value = false
  }
}

/**
 * Reorder lessons within a chapter
 */
export async function reorderLessons(
  refs: EditorRefs,
  chapterId: string,
  reorderedLessons: EditableLesson[]
): Promise<void> {
  refs.saving.value = true
  refs.error.value = null

  try {
    const items = reorderedLessons.map((lesson, index) => ({
      id: lesson.lesson_id,
      order_index: index + 1,
    }))

    await coursesApi.reorderLessons(chapterId, { items })

    refs.lessonsByChapterId.value[chapterId] = reorderedLessons.map((lesson, index) => ({
      ...lesson,
      order_index: index + 1,
    }))

    refs.dirty.value = false
  } catch (err: unknown) {
    refs.error.value = extractErrorMessage(err, 'Failed to reorder lessons')
    throw err
  } finally {
    refs.saving.value = false
  }
}
