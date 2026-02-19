/**
 * useCourseEditor composable
 *
 * Shared business logic for course editing used by both
 * CourseEditorWindow and CourseEditorPanel components.
 */

import { ref, computed, watch, onMounted } from 'vue'
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
} from '@/infrastructure/api/clients/panel/admin'
import { getCategoryTree, type Category, type CategoryTreeNode } from '@/infrastructure/api/clients/panel/editor'

interface CourseForm {
  title: string
  description: string
  category_id: number | null
  level: string
  language: string
  price: number
  is_public: boolean
  tags: string[]
}

interface UseCourseEditorOptions {
  courseId: () => string | undefined
  onClose: () => void
  onCourseUpdated?: (course: AdminCourseDetail) => void
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function useCourseEditor(options: UseCourseEditorOptions) {
  const { courseId, onClose, onCourseUpdated } = options

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

  const tabs = computed(() => [
    { id: 'metadata', label: 'Metadaten', icon: '' },
    { id: 'chapters', label: 'Kapitel', icon: '' },
    { id: 'actions', label: 'Aktionen', icon: '' }
  ])

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

  async function loadCourse(): Promise<void> {
    const id = courseId()
    if (!id) {
      error.value = 'Keine Kurs-ID angegeben'
      loading.value = false
      return
    }

    loading.value = true
    error.value = null

    try {
      loadCategories()
      course.value = await adminGetCourseDetail(id)
      populateForm()
    } catch (err: any) {
      console.error('Error loading course:', err)
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kursdaten'
    } finally {
      loading.value = false
    }
  }

  async function loadChapters(): Promise<void> {
    const id = courseId()
    if (!id) return

    loadingChapters.value = true
    try {
      chapters.value = await adminGetCourseChapters(id)
    } catch (err: any) {
      console.error('Error loading chapters:', err)
    } finally {
      loadingChapters.value = false
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

  function resetForm(): void {
    populateForm()
  }

  async function saveCourse(): Promise<void> {
    const id = courseId()
    if (!id || !form.value.title.trim()) return

    saving.value = true
    try {
      const tags = tagsInput.value
        .split(',')
        .map((t: string) => t.trim())
        .filter((t: string) => t.length > 0)

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

      course.value = await adminUpdateCourse(id, updateData)
      populateForm()
      onCourseUpdated?.(course.value)
    } catch (err: any) {
      console.error('Error saving course:', err)
      error.value = err.response?.data?.message || 'Fehler beim Speichern'
    } finally {
      saving.value = false
    }
  }

  async function publishCourse(): Promise<void> {
    const id = courseId()
    if (!id || !confirm('Moechten Sie diesen Kurs wirklich veroeffentlichen?')) return

    try {
      await adminPublishCourse(id)
      await loadCourse()
    } catch (err: any) {
      console.error('Error publishing course:', err)
      error.value = err.response?.data?.message || 'Fehler beim Veroeffentlichen'
    }
  }

  async function unpublishCourse(): Promise<void> {
    const id = courseId()
    if (!id || !confirm('Moechten Sie die Veroeffentlichung wirklich zurueckziehen?')) return

    try {
      await adminUnpublishCourse(id)
      await loadCourse()
    } catch (err: any) {
      console.error('Error unpublishing course:', err)
      error.value = err.response?.data?.message || 'Fehler'
    }
  }

  async function archiveCourse(): Promise<void> {
    const id = courseId()
    if (!id || !confirm('Moechten Sie diesen Kurs wirklich archivieren?')) return

    try {
      await adminArchiveCourse(id)
      await loadCourse()
    } catch (err: any) {
      console.error('Error archiving course:', err)
      error.value = err.response?.data?.message || 'Fehler'
    }
  }

  async function deleteCourse(): Promise<void> {
    const id = courseId()
    if (!id) return

    const confirmed = confirm(
      'WARNUNG: Moechten Sie diesen Kurs wirklich PERMANENT loeschen?\n\nDiese Aktion kann nicht rueckgaengig gemacht werden!'
    )
    if (!confirmed) return

    try {
      await adminDeleteCourse(id, 'Manuell durch Admin geloescht')
      onClose()
    } catch (err: any) {
      console.error('Error deleting course:', err)
      error.value = err.response?.data?.message || 'Fehler beim Loeschen'
    }
  }

  async function deleteChapter(chapterId: string): Promise<void> {
    if (!confirm('Moechten Sie dieses Kapitel wirklich loeschen?')) return

    try {
      await adminDeleteChapter(chapterId, 'Geloescht durch Admin')
      await loadChapters()
    } catch (err: any) {
      console.error('Error deleting chapter:', err)
      error.value = err.response?.data?.message || 'Fehler'
    }
  }

  // Watch for tab changes to lazy-load chapters
  watch(activeTab, (newTab) => {
    if (newTab === 'chapters' && chapters.value.length === 0) {
      loadChapters()
    }
  })

  onMounted(() => {
    loadCourse()
  })

  return {
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
    flatCategories,
    tabs,
    loadCourse,
    loadChapters,
    saveCourse,
    resetForm,
    publishCourse,
    unpublishCourse,
    archiveCourse,
    deleteCourse,
    deleteChapter
  }
}
