/**
 * useFilePreview Composable
 *
 * Shared business logic for file, chapter, and lesson preview components.
 * Handles file loading (PDF, image, text), chapter lesson listing,
 * and lesson content display.
 *
 * Used by: FilePreview.vue, FilePreviewPanel.vue, FilePreviewWindow.vue
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface FilePayload {
  id: string
  name: string
  type: string
  size: number
}

export interface ChapterPayload {
  chapter_id: string
  title: string
  description?: string
}

export interface LessonPayload {
  lesson_id: string
  title: string
  description?: string
  content?: any
  duration_minutes?: number
}

export type PreviewType = 'file' | 'chapter' | 'lesson' | 'unknown'

interface FilePreviewPayload {
  file?: FilePayload
  chapter?: ChapterPayload
  lesson?: LessonPayload
}

const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
const TEXT_EXTENSIONS = ['txt', 'md', 'json', 'xml', 'csv', 'log']
const FILE_TYPE_ICONS: Record<string, string> = { pdf: '\uD83D\uDCD5', txt: '\uD83D\uDCDD', jpg: '\uD83D\uDDBC\uFE0F', png: '\uD83D\uDDBC\uFE0F' }

// ---------------------------------------------------------------------------
// Composable
// ---------------------------------------------------------------------------

export function useFilePreview(getPayload: () => FilePreviewPayload | undefined) {
  const { t } = useI18n()

  // Reactive state
  const fileUrl = ref<string | null>(null)
  const textContent = ref<string | null>(null)
  const chapterLessons = ref<LessonPayload[]>([])
  const loading = ref(true)
  const error = ref<string | null>(null)

  // Derived payload data
  const previewType = computed<PreviewType>(() => {
    const payload = getPayload()
    if (payload?.file) return 'file'
    if (payload?.chapter) return 'chapter'
    if (payload?.lesson) return 'lesson'
    return 'unknown'
  })

  const file = computed<FilePayload | null>(() => getPayload()?.file || null)
  const chapter = computed<ChapterPayload | null>(() => getPayload()?.chapter || null)
  const lesson = computed<LessonPayload | null>(() => getPayload()?.lesson || null)

  // File type detection
  const fileExtension = computed(() => file.value?.type?.toLowerCase() || '')
  const isPdf = computed(() => fileExtension.value === 'pdf')
  const isImage = computed(() => IMAGE_EXTENSIONS.includes(fileExtension.value))
  const isText = computed(() => TEXT_EXTENSIONS.includes(fileExtension.value))

  // Header computeds
  const headerIcon = computed(() => {
    if (previewType.value === 'file') {
      return FILE_TYPE_ICONS[fileExtension.value] || '\uD83D\uDCC4'
    }
    if (previewType.value === 'chapter') return '\uD83D\uDCD6'
    if (previewType.value === 'lesson') return '\uD83D\uDCC4'
    return '\uD83D\uDCCB'
  })

  const headerTitle = computed(() => {
    if (previewType.value === 'file') return file.value?.name || t('filePreview.file')
    if (previewType.value === 'chapter') return chapter.value?.title || t('filePreview.chapter')
    if (previewType.value === 'lesson') return lesson.value?.title || t('filePreview.lesson')
    return t('filePreview.preview')
  })

  const headerMeta = computed(() => {
    if (previewType.value === 'file') {
      return `${formatFileSize(file.value?.size)} \u00B7 ${file.value?.type?.toUpperCase()}`
    }
    if (previewType.value === 'chapter') {
      return t('filePreview.lessonsCount', { count: chapterLessons.value.length })
    }
    if (previewType.value === 'lesson') {
      if (lesson.value?.duration_minutes) {
        return `${lesson.value.duration_minutes} ${t('filePreview.min')}`
      }
      return t('filePreview.lesson')
    }
    return ''
  })

  // ---------------------------------------------------------------------------
  // Content loading
  // ---------------------------------------------------------------------------

  async function loadContent(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      if (previewType.value === 'file') {
        await loadFile()
      } else if (previewType.value === 'chapter') {
        await loadChapterLessons()
      } else if (previewType.value === 'lesson') {
        loading.value = false
      } else {
        error.value = t('filePreview.unknownType')
        loading.value = false
      }
    } catch (err: any) {
      error.value = err.message || t('filePreview.loadError')
      loading.value = false
    }
  }

  async function loadFile(): Promise<void> {
    if (!file.value?.id) {
      error.value = t('filePreview.noFileId')
      loading.value = false
      return
    }

    try {
      const serveUrl = `/panel/course-files/${file.value.id}/serve`

      if (isPdf.value) {
        const response = await http.get(serveUrl, { responseType: 'blob' })
        const blob = new Blob([response.data], { type: 'application/pdf' })
        fileUrl.value = URL.createObjectURL(blob)
      } else if (isImage.value) {
        const response = await http.get(serveUrl, { responseType: 'blob' })
        const blob = new Blob([response.data])
        fileUrl.value = URL.createObjectURL(blob)
      } else if (isText.value) {
        const response = await http.get(serveUrl, { responseType: 'text' })
        textContent.value = response.data
      } else {
        const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'
        fileUrl.value = `${baseUrl}/panel/course-files/${file.value.id}/serve`
      }
    } catch (err: any) {
      console.error('File load error:', err)
      error.value = err.response?.data?.error || t('filePreview.fileLoadError')
    } finally {
      loading.value = false
    }
  }

  async function loadChapterLessons(): Promise<void> {
    if (!chapter.value?.chapter_id) {
      error.value = t('filePreview.noChapterId')
      loading.value = false
      return
    }

    try {
      const res = await http.get(`/panel/chapters/${chapter.value.chapter_id}/lessons`)
      if (res.data.success) {
        chapterLessons.value = res.data.data?.lessons || res.data.lessons || []
      }
    } catch {
      error.value = t('filePreview.lessonsLoadError')
    } finally {
      loading.value = false
    }
  }

  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------

  function downloadFile(): void {
    if (fileUrl.value) {
      const a = document.createElement('a')
      a.href = fileUrl.value
      a.download = file.value?.name || 'download'
      a.click()
    }
  }

  function openEditor(): void {
    // TODO: Open editor for chapter/lesson
    console.log('Open editor for', previewType.value)
  }

  // ---------------------------------------------------------------------------
  // Lifecycle
  // ---------------------------------------------------------------------------

  onMounted(() => {
    loadContent()
  })

  onUnmounted(() => {
    if (fileUrl.value?.startsWith('blob:')) {
      URL.revokeObjectURL(fileUrl.value)
    }
  })

  return {
    // State
    fileUrl,
    textContent,
    chapterLessons,
    loading,
    error,

    // Computed
    previewType,
    file,
    chapter,
    lesson,
    isPdf,
    isImage,
    isText,
    headerIcon,
    headerTitle,
    headerMeta,

    // Actions
    downloadFile,
    openEditor,
    loadContent,
  }
}

// ---------------------------------------------------------------------------
// Helpers (exported for potential reuse)
// ---------------------------------------------------------------------------

export function formatFileSize(bytes: number | undefined): string {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
