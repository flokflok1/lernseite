/**
 * useCourseDetail Composable
 * ==========================
 * Manages course data, chapters, files, and actions for admin course detail view
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  adminGetCourseDetail,
  adminGetCourseChapters,
  adminDeleteChapter,
  adminPublishCourse,
  adminUnpublishCourse,
  adminArchiveCourse,
  adminListCourseFiles,
  adminUploadCourseFile,
  adminDeleteCourseFile,
  type AdminCourseDetail,
  type AdminChapter,
  type CourseFile,
  type CourseFileCategorySummary
} from '@/infrastructure/api/admin.api'

export interface Chapter {
  chapter_id?: string
  title: string
  description?: string
  duration_minutes?: number
  order_index?: number
  lessons?: any[]
}

export function useCourseDetail(courseId: string) {
  const { t, locale } = useI18n()

  // ============================================================================
  // State
  // ============================================================================

  const course = ref<AdminCourseDetail | null>(null)
  const loading = ref(true)
  const error = ref<string | null>(null)

  // Chapters
  const chapters = ref<Chapter[]>([])
  const chaptersLoading = ref(false)
  const expandedChapters = ref<number[]>([])

  // Files
  const courseFiles = ref<CourseFile[]>([])
  const filesLoading = ref(false)
  const filesError = ref<string | null>(null)
  const filesCategorySummary = ref<CourseFileCategorySummary[]>([])
  const isUploading = ref(false)

  // ============================================================================
  // Computed
  // ============================================================================

  const lessonCount = computed(() => {
    return chapters.value.reduce((sum, chap) => sum + (chap.lessons?.length || 0), 0)
  })

  const fileCount = computed(() => courseFiles.value.length)

  const revenueDisplay = computed(() => {
    const revenue = (course.value as any)?.revenue || 0
    if (revenue === 0) return '–'
    return `${revenue.toFixed(0)}€`
  })

  const ratingDisplay = computed(() => {
    const rating = (course.value as any)?.average_rating || 0
    if (rating === 0) return '–'
    return rating.toFixed(1)
  })

  const completionRateDisplay = computed(() => {
    const rate = (course.value as any)?.completion_rate || 0
    if (rate === 0) return '–'
    return `${Math.round(rate)}%`
  })

  const statusBadgeStyle = computed(() => {
    if (!course.value) return ''

    const statusStyles = {
      draft: 'background-color: var(--color-status-draft-bg, #f3f4f6); color: var(--color-status-draft-text, #374151);',
      published: 'background-color: var(--color-status-published-bg, #dcfce7); color: var(--color-status-published-text, #15803d);',
      archived: 'background-color: var(--color-status-archived-bg, #ffedd5); color: var(--color-status-archived-text, #c2410c);'
    }

    return statusStyles[course.value.status as keyof typeof statusStyles] || statusStyles.draft
  })

  const statusText = computed(() => {
    if (!course.value) return ''
    const statusMap = {
      draft: t('admin.courseDetail.status.draft'),
      published: t('admin.courseDetail.status.published'),
      archived: t('admin.courseDetail.status.archived')
    }
    return statusMap[course.value.status as keyof typeof statusMap] || course.value.status
  })

  const languageLabel = computed(() => {
    if (!course.value) return ''
    const languageMap: Record<string, string> = {
      de: 'Deutsch',
      en: 'English',
      pl: 'Polski'
    }
    return languageMap[course.value.language || 'de'] || course.value.language
  })

  const levelLabel = computed(() => {
    if (!course.value) return ''
    const levelMap: Record<string, string> = {
      beginner: t('courses.level_beginner'),
      intermediate: t('courses.level_intermediate'),
      advanced: t('courses.level_advanced')
    }
    return levelMap[course.value.difficulty_level] || course.value.difficulty_level
  })

  const showAdBadge = computed(() => {
    if (!course.value) return false
    return course.value.ad_enabled
  })

  const showPremiumBadge = computed(() => {
    if (!course.value) return false
    return Number(course.value.price || 0) > 0
  })

  const showFreeBadge = computed(() => {
    if (!course.value) return false
    return Number(course.value.price || 0) === 0 && !course.value.ad_enabled
  })

  // ============================================================================
  // Course Loading
  // ============================================================================

  async function loadCourse() {
    loading.value = true
    error.value = null

    try {
      if (!courseId || courseId === 'undefined' || courseId === 'null') {
        throw new Error(`${t('admin.courseDetail.invalidCourseId')}: ${courseId}`)
      }

      course.value = await adminGetCourseDetail(courseId)
    } catch (err: any) {
      console.error('Error loading course:', err)
      error.value = err.response?.data?.message || err.message || t('admin.courseDetail.loadErrorDetails')
    } finally {
      loading.value = false
    }
  }

  async function loadCourseChapters(): Promise<void> {
    if (!course.value) return

    chaptersLoading.value = true

    try {
      const apiChapters = await adminGetCourseChapters(course.value.course_id)
      chapters.value = apiChapters.map(c => ({
        chapter_id: String(c.chapter_id),
        title: c.title,
        description: c.description || undefined,
        duration_minutes: c.duration_minutes,
        order_index: c.order_index,
        lessons: []
      }))
    } catch (err: any) {
      console.error('Error loading chapters:', err)
    } finally {
      chaptersLoading.value = false
    }
  }

  // ============================================================================
  // Chapter Actions
  // ============================================================================

  function toggleChapter(index: number): void {
    const idx = expandedChapters.value.indexOf(index)
    if (idx === -1) {
      expandedChapters.value.push(index)
    } else {
      expandedChapters.value.splice(idx, 1)
    }
  }

  async function deleteChapter(chapterToDelete: Chapter): Promise<void> {
    if (!course.value || !chapterToDelete.chapter_id) return

    if (!confirm(t('admin.courseDetail.confirmDeleteChapter', { title: chapterToDelete.title }))) {
      return
    }

    try {
      await adminDeleteChapter(course.value.course_id, chapterToDelete.chapter_id)
      await loadCourseChapters()
    } catch (err: any) {
      console.error('Error deleting chapter:', err)
      alert(err.response?.data?.message || t('admin.courseDetail.deleteChapterError'))
    }
  }

  // ============================================================================
  // Course Actions
  // ============================================================================

  async function publishCourse(): Promise<void> {
    if (!course.value) return

    try {
      await adminPublishCourse(course.value.course_id)
      await loadCourse()
    } catch (err: any) {
      console.error('Error publishing course:', err)
      alert(err.response?.data?.message || t('admin.courseDetail.publishError'))
    }
  }

  async function unpublishCourse(): Promise<void> {
    if (!course.value) return

    try {
      await adminUnpublishCourse(course.value.course_id)
      await loadCourse()
    } catch (err: any) {
      console.error('Error unpublishing course:', err)
      alert(err.response?.data?.message || t('admin.courseDetail.unpublishError'))
    }
  }

  async function archiveCourse(): Promise<void> {
    if (!course.value) return

    if (!confirm(t('admin.courseDetail.confirmArchive'))) {
      return
    }

    try {
      await adminArchiveCourse(course.value.course_id)
      await loadCourse()
    } catch (err: any) {
      console.error('Error archiving course:', err)
      alert(err.response?.data?.message || t('admin.courseDetail.archiveError'))
    }
  }

  // ============================================================================
  // File Management
  // ============================================================================

  async function loadCourseFiles(): Promise<void> {
    if (!course.value) return

    filesLoading.value = true
    filesError.value = null

    try {
      const response = await adminListCourseFiles(course.value.course_id)
      courseFiles.value = response.files
      filesCategorySummary.value = response.summary
    } catch (err: any) {
      console.error('Error loading files:', err)
      filesError.value = err.response?.data?.message || t('admin.courseDetail.filesLoadError')
    } finally {
      filesLoading.value = false
    }
  }

  async function uploadFile(file: File, category: string): Promise<void> {
    if (!course.value) return

    isUploading.value = true

    try {
      await adminUploadCourseFile(course.value.course_id, file, category)
      await loadCourseFiles()
    } catch (err: any) {
      console.error('Error uploading file:', err)
      alert(err.response?.data?.message || t('admin.courseDetail.uploadError'))
    } finally {
      isUploading.value = false
    }
  }

  async function deleteFile(file: CourseFile): Promise<void> {
    if (!course.value) return

    if (!confirm(t('admin.courseDetail.confirmDeleteFile', { name: file.original_filename }))) {
      return
    }

    try {
      await adminDeleteCourseFile(course.value.course_id, file.file_id)
      await loadCourseFiles()
    } catch (err: any) {
      console.error('Error deleting file:', err)
      alert(err.response?.data?.message || t('admin.courseDetail.deleteFileError'))
    }
  }

  // ============================================================================
  // Utilities
  // ============================================================================

  function formatDate(dateString: string): string {
    const date = new Date(dateString)
    return date.toLocaleDateString(locale.value, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  function formatDateShort(dateString: string): string {
    const date = new Date(dateString)
    return date.toLocaleDateString(locale.value, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  // ============================================================================
  // Initialize
  // ============================================================================

  async function initialize() {
    await loadCourse()
    if (course.value) {
      await Promise.all([
        loadCourseChapters(),
        loadCourseFiles()
      ])
    }
  }

  return {
    // State
    course,
    loading,
    error,
    chapters,
    chaptersLoading,
    expandedChapters,
    courseFiles,
    filesLoading,
    filesError,
    filesCategorySummary,
    isUploading,
    // Computed
    lessonCount,
    fileCount,
    revenueDisplay,
    ratingDisplay,
    completionRateDisplay,
    statusBadgeStyle,
    statusText,
    languageLabel,
    levelLabel,
    showAdBadge,
    showPremiumBadge,
    showFreeBadge,
    // Methods
    loadCourse,
    loadCourseChapters,
    toggleChapter,
    deleteChapter,
    publishCourse,
    unpublishCourse,
    archiveCourse,
    loadCourseFiles,
    uploadFile,
    deleteFile,
    formatDate,
    formatDateShort,
    initialize
  }
}
