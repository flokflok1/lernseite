import { ref, computed } from 'vue'
import type { DraftStructure, DraftChapter, SelectedContext } from '../../types'
import {
  getChaptersForEdit,
  getLessonsForEdit,
} from '@/infrastructure/api/clients/panel/editor/courses/courses.api'

export function useStructureView() {
  const draftStructure = ref<DraftStructure | null>(null)
  const selectedContext = ref<SelectedContext | null>(null)
  const expandedNodes = ref<Set<string>>(new Set())
  const isFinalizing = ref(false)
  const error = ref<string | null>(null)

  const hasStructure = computed(
    () => draftStructure.value !== null && draftStructure.value.chapters.length > 0,
  )

  const chapterCount = computed(() => draftStructure.value?.chapters.length ?? 0)

  const lessonCount = computed(
    () => draftStructure.value?.chapters.reduce((sum, ch) => sum + ch.lessons.length, 0) ?? 0,
  )

  const contextLabel = computed(() => {
    if (!selectedContext.value) return null
    const prefix = selectedContext.value.type === 'chapter' ? 'Ch' : 'L'
    return `${prefix}: ${selectedContext.value.title}`
  })

  function setContext(type: 'chapter' | 'lesson', id: string, title: string): void {
    selectedContext.value = { type, id, title }
  }

  function clearContext(): void {
    selectedContext.value = null
  }

  function toggleNode(nodeId: string): void {
    if (expandedNodes.value.has(nodeId)) {
      expandedNodes.value.delete(nodeId)
    } else {
      expandedNodes.value.add(nodeId)
    }
    expandedNodes.value = new Set(expandedNodes.value)
  }

  function expandAll(): void {
    if (!draftStructure.value) return
    const ids = new Set<string>()
    for (const ch of draftStructure.value.chapters) {
      ids.add(ch.id)
    }
    expandedNodes.value = ids
  }

  function updateFromResponse(structure: Record<string, unknown>): void {
    if (!structure) return

    const chapters = (structure.chapters as Record<string, unknown>[]) || []

    draftStructure.value = {
      courseId: (structure.course_id as string) || draftStructure.value?.courseId || '',
      courseTitle: (structure.course_title as string) || draftStructure.value?.courseTitle || '',
      chapters: chapters.map((ch: Record<string, unknown>, ci: number) => ({
        id: (ch.id as string) || (ch.chapter_id as string) || `ch-${ci}`,
        title: (ch.title as string) || `Chapter ${ci + 1}`,
        order: (ch.order as number) ?? ci,
        lessons: ((ch.lessons as Record<string, unknown>[]) || []).map(
          (ls: Record<string, unknown>, li: number) => ({
            id: (ls.id as string) || (ls.lesson_id as string) || `ls-${ci}-${li}`,
            title: (ls.title as string) || `Lesson ${li + 1}`,
            order: (ls.order as number) ?? li,
            contentIndicators: (
              (ls.content_indicators as Record<string, unknown>[]) ||
              (ls.methods as Record<string, unknown>[]) ||
              []
            ).map((ind: Record<string, unknown>) => ({
              type: (ind.type as string) || 'method',
              label: (ind.label as string) || (ind.name as string) || (ind.type as string),
              count: ind.count as number | undefined,
              status: (ind.status as string) || 'empty',
            })),
          }),
        ),
      })),
    }

    expandAll()
  }

  async function loadCourseStructure(courseId: string, courseTitle = ''): Promise<void> {
    error.value = null
    try {
      const chapters = await getChaptersForEdit(courseId)
      const draftChapters: DraftChapter[] = []

      for (const ch of chapters) {
        let lessons
        try {
          lessons = await getLessonsForEdit(ch.chapter_id)
        } catch (e: unknown) {
          console.warn('[StructureView] Failed to load lessons for chapter', ch.chapter_id, e)
          lessons = []
        }
        draftChapters.push({
          id: ch.chapter_id,
          title: ch.title,
          order: ch.order_index,
          lessons: lessons.map((ls) => ({
            id: String(ls.lesson_id),
            title: ls.title,
            order: ls.order_index,
            contentIndicators: [],
          })),
        })
      }

      draftStructure.value = {
        courseId,
        courseTitle,
        chapters: draftChapters,
      }

      expandAll()
    } catch (e: unknown) {
      console.warn('[StructureView] Failed to load course structure:', e)
      draftStructure.value = null
    }
  }

  function clearStructure(): void {
    draftStructure.value = null
    selectedContext.value = null
    expandedNodes.value = new Set()
    error.value = null
  }

  return {
    draftStructure,
    selectedContext,
    expandedNodes,
    isFinalizing,
    error,
    hasStructure,
    chapterCount,
    lessonCount,
    contextLabel,
    setContext,
    clearContext,
    toggleNode,
    expandAll,
    updateFromResponse,
    loadCourseStructure,
    clearStructure,
  }
}
