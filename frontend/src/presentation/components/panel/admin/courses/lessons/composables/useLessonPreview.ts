/**
 * Composable for lesson preview data loading and method metadata.
 *
 * Shared between LessonPreview, LessonPreviewWindow, and LessonPreviewPanel
 * to eliminate duplicated logic across three nearly identical components.
 */
import { ref, computed, type Ref, type ComputedRef } from 'vue'
import http from '@/infrastructure/api/http'

// --- Types ---

export interface LessonPreviewPayload {
  lesson?: {
    lesson_id?: string
    id?: string
    title?: string
    description?: string
    content?: { theory?: string }
    duration_minutes?: number
    lesson_type?: string
    methods?: Array<{
      id?: string
      type: number | string
      title?: string
      description?: string
      config?: Record<string, unknown>
      data?: Record<string, unknown>
    }>
  }
  lessonId?: string
  position?: string | number
  chapter?: { title?: string }
}

export interface LessonMethod {
  method_id: string
  method_type: number | string
  method_name?: string
  description?: string
  config: Record<string, unknown>
}

export interface LessonData {
  title?: string
  description?: string
  content?: { theory?: string }
  duration_minutes?: number
  lesson_type?: string
  chapter_id?: string
  chapter_title?: string
  created_at?: string
}

export interface UseLessonPreviewReturn {
  loading: Ref<boolean>
  error: Ref<string | null>
  lessonData: Ref<LessonData | null>
  methods: Ref<LessonMethod[]>
  activeTab: Ref<string>
  expandedMethod: Ref<string | null>
  lessonId: ComputedRef<string | undefined>
  lessonPosition: ComputedRef<string | number>
  chapterTitle: ComputedRef<string>
  loadLessonData: () => Promise<void>
  toggleMethod: (methodId: string) => void
}

// --- Composable ---

export function useLessonPreview(
  payload: ComputedRef<LessonPreviewPayload | undefined>
): UseLessonPreviewReturn {
  const loading = ref(true)
  const error = ref<string | null>(null)
  const lessonData = ref<LessonData | null>(null)
  const methods = ref<LessonMethod[]>([])
  const activeTab = ref('exercises')
  const expandedMethod = ref<string | null>(null)

  const lessonId = computed(() => {
    const p = payload.value
    return p?.lesson?.lesson_id || p?.lesson?.id || p?.lessonId
  })

  const lessonPosition = computed(() => payload.value?.position || '1')

  const chapterTitle = computed(
    () => payload.value?.chapter?.title || lessonData.value?.chapter_title || ''
  )

  async function loadLessonData(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      if (lessonId.value && !lessonId.value.startsWith('draft-')) {
        const lessonResponse = await http.get(`/lessons/${lessonId.value}`)
        if (lessonResponse.data.success) {
          lessonData.value = lessonResponse.data.lesson
        }

        const methodsResponse = await http.get(`/lessons/${lessonId.value}/methods`)
        if (methodsResponse.data.success) {
          methods.value = methodsResponse.data.methods || []
        }
      } else {
        const lessonPayload = payload.value?.lesson
        if (lessonPayload) {
          lessonData.value = {
            title: lessonPayload.title,
            description: lessonPayload.description,
            content: lessonPayload.content,
            duration_minutes: lessonPayload.duration_minutes,
            lesson_type: lessonPayload.lesson_type || 'text'
          }
          methods.value = lessonPayload.methods?.map((m) => ({
            method_id: m.id || `draft-${Math.random()}`,
            method_type: m.type,
            method_name: m.title,
            description: m.description,
            config: (m.config || m.data || {}) as Record<string, unknown>
          })) || []
        }
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: string } } }
      console.error('Failed to load lesson:', err)
      error.value = axiosErr.response?.data?.error || 'Lektion konnte nicht geladen werden'
    } finally {
      loading.value = false
    }
  }

  function toggleMethod(methodId: string): void {
    expandedMethod.value = expandedMethod.value === methodId ? null : methodId
  }

  return {
    loading,
    error,
    lessonData,
    methods,
    activeTab,
    expandedMethod,
    lessonId,
    lessonPosition,
    chapterTitle,
    loadLessonData,
    toggleMethod
  }
}

// --- Method Metadata ---

export const METHOD_ICONS: Record<number, string> = {
  0: '📖', 1: '📝', 2: '🔄', 3: '📊', 4: '💭', 6: '🎯',
  8: '✏️', 9: '💻', 10: '🌐', 11: '🔧', 12: '🔢', 13: '🃏',
  14: '🎯', 15: '📝', 16: '🔍', 17: '🛠️', 18: '✍️', 19: '📋',
  20: '📑', 21: '⏱️', 22: '❓', 23: '✅', 24: '🎤', 25: '🏆',
  26: '👥', 27: '🤝', 28: '📊', 29: '📓', 30: '📁', 31: '🎓', 32: '🔄'
}

export function parseMethodType(type: number | string | undefined): number {
  if (type === undefined || type === null) return NaN
  return typeof type === 'string' ? parseInt(type, 10) : type
}

export function getMethodIcon(type: number | string | undefined): string {
  const numType = parseMethodType(type)
  return isNaN(numType) ? '📚' : (METHOD_ICONS[numType] || '📚')
}

export function cleanMethodTitle(
  title: string | undefined,
  methodType: number | string | undefined
): string {
  if (!title) return 'Aufgabe'
  const numType = parseMethodType(methodType)
  if (!isNaN(numType)) {
    const prefix = `LM${String(numType).padStart(2, '0')}:`
    if (title.startsWith(prefix)) {
      return title.substring(prefix.length).trim()
    }
  }
  return title
}

export function formatTheoryContent(content: string): string {
  if (!content) return ''
  return content
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

export function formatDate(dateStr: string, locale = 'de-DE'): string {
  return new Date(dateStr).toLocaleDateString(locale, {
    day: '2-digit', month: '2-digit', year: 'numeric'
  })
}

/**
 * Returns localized method name using the i18n t() function.
 * Falls back to "Lernmethode {id}" if key is not found.
 */
export function getMethodName(
  type: number | string | undefined,
  t: (key: string, params?: Record<string, unknown>) => string,
  keyPrefix = 'panel.lessons.preview'
): string {
  const numType = parseMethodType(type)
  if (isNaN(numType)) return t(`${keyPrefix}.methodDefault`)
  const key = `${keyPrefix}.methodNames.lm${numType}`
  const name = t(key)
  return name === key ? t(`${keyPrefix}.methodWithId`, { id: numType }) : name
}

export interface PreviewTab {
  id: string
  label: string
  icon: string
  count?: number
}

/**
 * Builds the standard tab configuration for lesson preview.
 */
export function buildPreviewTabs(
  methodCount: number,
  t: (key: string) => string,
  keyPrefix = 'panel.lessons.preview'
): PreviewTab[] {
  return [
    { id: 'exercises', label: t(`${keyPrefix}.exercises`), icon: '📝', count: methodCount },
    { id: 'theory', label: t(`${keyPrefix}.theory`), icon: '📖' },
    { id: 'info', label: t(`${keyPrefix}.info`), icon: 'ℹ️' }
  ]
}
