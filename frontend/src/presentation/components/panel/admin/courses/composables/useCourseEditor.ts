/**
 * useCourseEditor composable
 *
 * Encapsulates all course editing business logic: loading, saving,
 * publishing, archiving, deleting courses and chapters.
 */
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import {
  adminGetCourseDetail,
  adminUpdateCourse,
  adminGetCourseChapters,
  adminPublishCourse,
  adminUnpublishCourse,
  adminArchiveCourse,
  adminDeleteCourse,
  adminDeleteChapter,
  type AdminCourseDetail,
  type AdminChapter
} from '@/application/services/api/panel-admin'
import { getCategoryTree, type Category, type CategoryTreeNode } from '@/application/services/api/panel-editor'

export interface CourseForm {
  title: string
  description: string
  category_id: number | null
  level: string
  language: string
  price: number
  is_public: boolean
  tags: string[]
}

export type { AdminCourseDetail, AdminChapter, Category, CategoryTreeNode }

export function useCourseEditor(windowRef: () => LsxWindow, onClose: () => void) {
  const { t } = useI18n()
  const windowStore = useWindowStore()

  // State
  const course = ref<AdminCourseDetail | null>(null)
  const chapters = ref<AdminChapter[]>([])
  const categories = ref<CategoryTreeNode[]>([])
  const loading = ref(true)
  const loadingChapters = ref(false)
  const loadingCategories = ref(false)
  const error = ref<string | null>(null)
  const saving = ref(false)
  const activeTab = ref<'metadata' | 'chapters' | 'actions'>('metadata')

  const form = ref<CourseForm>({
    title: '',
    description: '',
    category_id: null,
    level: 'beginner',
    language: 'de',
    price: 0,
    is_public: true,
    tags: []
  })

  const tagsInput = ref('')

  // Computed
  const courseId = computed(() => windowRef().payload?.courseId as string)

  const tabs = computed(() => [
    { id: 'metadata', label: t('courseEditor.tabs.metadata'), icon: '📝' },
    { id: 'chapters', label: t('courseEditor.tabs.chapters'), icon: '📚' },
    { id: 'actions', label: t('courseEditor.tabs.actions'), icon: '⚡' }
  ])

  const flatCategories = computed(() => {
    const result: Array<Category & { indent: string }> = []

    function flatten(cats: CategoryTreeNode[], level: number): void {
      for (const cat of cats) {
        result.push({
          ...cat,
          indent: '\u2014'.repeat(level) + (level > 0 ? ' ' : '')
        })
        if (cat.children && cat.children.length > 0) {
          flatten(cat.children, level + 1)
        }
      }
    }

    flatten(categories.value, 0)
    return result
  })

  // Methods
  async function loadCategories(): Promise<void> {
    loadingCategories.value = true
    try {
      const tree = await getCategoryTree(false)
      categories.value = tree.categories || []
    } catch (err) {
      console.error('Failed to load categories:', err)
      categories.value = []
    } finally {
      loadingCategories.value = false
    }
  }

  function populateForm(): void {
    if (!course.value) return

    form.value = {
      title: course.value.title,
      description: course.value.description || '',
      category_id: course.value.category_id || null,
      level: course.value.level || 'beginner',
      language: course.value.language || 'de',
      price: course.value.price || 0,
      is_public: course.value.is_public,
      tags: course.value.tags || []
    }

    tagsInput.value = (course.value.tags || []).join(', ')
  }

  async function loadCourse(): Promise<void> {
    if (!courseId.value) {
      error.value = t('courseEditor.errors.noCourseId')
      loading.value = false
      return
    }

    loading.value = true
    error.value = null

    try {
      loadCategories()
      course.value = await adminGetCourseDetail(courseId.value)
      populateForm()
    } catch (err: any) {
      console.error('Error loading course:', err)
      error.value = err.response?.data?.message || t('courseEditor.errors.loadError')
    } finally {
      loading.value = false
    }
  }

  async function loadChapters(): Promise<void> {
    if (!courseId.value) return

    loadingChapters.value = true
    try {
      chapters.value = await adminGetCourseChapters(courseId.value)
    } catch (err: any) {
      console.error('Error loading chapters:', err)
    } finally {
      loadingChapters.value = false
    }
  }

  function resetForm(): void {
    populateForm()
  }

  async function saveCourse(): Promise<void> {
    if (!courseId.value || !form.value.title.trim()) return

    saving.value = true
    try {
      const tags = tagsInput.value
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)

      const updateData = {
        title: form.value.title,
        description: form.value.description || undefined,
        category_id: form.value.category_id,
        level: form.value.level,
        language: form.value.language,
        price: form.value.price,
        is_public: form.value.is_public,
        tags: tags.length > 0 ? tags : undefined
      }

      course.value = await adminUpdateCourse(courseId.value, updateData)
      populateForm()

      windowStore.updateWindowPayload(windowRef().id, {
        course: course.value
      })

      alert(t('courseEditor.alerts.changesSaved'))
    } catch (err: any) {
      console.error('Error saving course:', err)
      alert(t('courseEditor.errors.saveError') + ': ' + (err.response?.data?.message || err.message))
    } finally {
      saving.value = false
    }
  }

  async function publishCourse(): Promise<void> {
    if (!courseId.value || !confirm(t('courseEditor.alerts.publishConfirm'))) return

    try {
      await adminPublishCourse(courseId.value)
      await loadCourse()
      alert(t('courseEditor.alerts.coursePublished'))
    } catch (err: any) {
      console.error('Error publishing course:', err)
      alert(t('courseEditor.errors.publishError') + ': ' + (err.response?.data?.message || err.message))
    }
  }

  async function unpublishCourse(): Promise<void> {
    if (!courseId.value || !confirm(t('courseEditor.alerts.unpublishConfirm'))) return

    try {
      await adminUnpublishCourse(courseId.value)
      await loadCourse()
      alert(t('courseEditor.alerts.courseUnpublished'))
    } catch (err: any) {
      console.error('Error unpublishing course:', err)
      alert(t('courseEditor.errors.unpublishError') + ': ' + (err.response?.data?.message || err.message))
    }
  }

  async function archiveCourse(): Promise<void> {
    if (!courseId.value || !confirm(t('courseEditor.alerts.archiveConfirm'))) return

    try {
      await adminArchiveCourse(courseId.value)
      await loadCourse()
      alert(t('courseEditor.alerts.courseArchived'))
    } catch (err: any) {
      console.error('Error archiving course:', err)
      alert(t('courseEditor.errors.archiveError') + ': ' + (err.response?.data?.message || err.message))
    }
  }

  async function deleteCourse(): Promise<void> {
    if (!courseId.value) return

    const confirmed = confirm(t('courseEditor.alerts.deleteConfirm'))
    if (!confirmed) return

    try {
      await adminDeleteCourse(courseId.value, t('courseEditor.alerts.deleteReason'))
      alert(t('courseEditor.alerts.courseDeleted'))
      onClose()
    } catch (err: any) {
      console.error('Error deleting course:', err)
      alert(t('courseEditor.errors.deleteError') + ': ' + (err.response?.data?.message || err.message))
    }
  }

  function openChapterEditor(chapter: AdminChapter | null): void {
    windowStore.openWindow({
      type: 'admin-kapitel-editor',
      title: chapter
        ? t('courseEditor.chapters.editTitle', { title: chapter.title })
        : t('courseEditor.chapters.newTitle'),
      icon: '📚',
      payload: {
        courseId: courseId.value,
        courseTitle: course.value?.title,
        chapterId: chapter?.chapter_id,
        chapter: chapter
      }
    })
  }

  async function deleteChapter(chapterId: string): Promise<void> {
    if (!confirm(t('courseEditor.alerts.chapterDeleteConfirm'))) return

    try {
      await adminDeleteChapter(chapterId, t('courseEditor.alerts.chapterDeleteReason'))
      await loadChapters()
      alert(t('courseEditor.alerts.chapterDeleted'))
    } catch (err: any) {
      console.error('Error deleting chapter:', err)
      alert(t('courseEditor.errors.chapterDeleteError') + ': ' + (err.response?.data?.message || err.message))
    }
  }

  // Watch for tab changes
  watch(activeTab, (newTab) => {
    if (newTab === 'chapters' && chapters.value.length === 0) {
      loadChapters()
    }
  })

  return {
    // State
    course,
    chapters,
    loading,
    loadingChapters,
    loadingCategories,
    error,
    saving,
    activeTab,
    form,
    tagsInput,

    // Computed
    courseId,
    tabs,
    flatCategories,

    // Methods
    loadCourse,
    loadChapters,
    resetForm,
    saveCourse,
    publishCourse,
    unpublishCourse,
    archiveCourse,
    deleteCourse,
    openChapterEditor,
    deleteChapter
  }
}
