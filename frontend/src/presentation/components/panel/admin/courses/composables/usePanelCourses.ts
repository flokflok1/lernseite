/**
 * Composable for panel courses page business logic.
 *
 * Manages filters, pagination, CRUD operations, and display helpers
 * for the admin courses list.
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/admin/panel.store'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import type { Category } from '@/infrastructure/api/clients/panel/admin'

export interface CourseFilters {
  searchQuery: string
  statusFilter: 'all' | 'draft' | 'published' | 'archived'
  levelFilter: string
  categoryFilter: number | undefined
}

export function usePanelCourses() {
  const { t } = useI18n()
  const router = useRouter()
  const panelStore = usePanelStore()
  const windowStore = useWindowStore()

  // Filters
  const searchQuery = ref('')
  const statusFilter = ref<'all' | 'draft' | 'published' | 'archived'>('all')
  const levelFilter = ref('')
  const categoryFilter = ref<number | undefined>(undefined)

  // Pagination
  const currentPage = ref(1)
  const perPage = ref(20)

  // Debounce timer
  let searchTimeout: ReturnType<typeof setTimeout> | null = null

  // Flatten category tree for simple dropdown
  const flatCategories = computed((): Category[] => {
    const result: Category[] = []

    function flatten(nodes: any[]): void {
      for (const node of nodes) {
        result.push({
          category_id: node.category_id,
          name: node.name,
          slug: node.slug,
          description: node.description,
          parent_id: node.parent_id,
          level: node.level,
          is_active: node.is_active,
          created_at: node.created_at,
          updated_at: node.updated_at
        })
        if (node.children && node.children.length > 0) {
          flatten(node.children)
        }
      }
    }

    flatten(panelStore.categoryTree)
    return result
  })

  const totalPages = computed((): number =>
    Math.ceil(panelStore.coursesTotal / perPage.value)
  )

  // -------------------------------------------------------------------
  // Data loading
  // -------------------------------------------------------------------

  async function loadCourses(): Promise<void> {
    await panelStore.loadCourses({
      page: currentPage.value,
      per_page: perPage.value,
      search: searchQuery.value || undefined,
      status: statusFilter.value === 'all' ? undefined : statusFilter.value,
      level: levelFilter.value || undefined,
      category_id: categoryFilter.value || undefined
    })
  }

  function debouncedSearch(): void {
    if (searchTimeout) {
      clearTimeout(searchTimeout)
    }
    searchTimeout = setTimeout(() => {
      currentPage.value = 1
      loadCourses()
    }, 500)
  }

  function resetFilters(): void {
    searchQuery.value = ''
    statusFilter.value = 'all'
    levelFilter.value = ''
    categoryFilter.value = undefined
    currentPage.value = 1
    loadCourses()
  }

  function changePage(page: number): void {
    currentPage.value = page
    loadCourses()
  }

  // -------------------------------------------------------------------
  // Navigation
  // -------------------------------------------------------------------

  function viewCourseDetail(courseId: string): void {
    if (!courseId || typeof courseId !== 'string') {
      console.error('Invalid course ID:', courseId)
      return
    }
    router.push({ name: 'panel-course-detail', params: { id: courseId } })
  }

  // -------------------------------------------------------------------
  // CRUD operations
  // -------------------------------------------------------------------

  async function publishCourse(courseId: string): Promise<void> {
    if (!confirm('Möchten Sie diesen Kurs wirklich veröffentlichen?')) return

    try {
      await panelStore.publishCourse(courseId)
      loadCourses()
    } catch (error) {
      console.error('Failed to publish course:', error)
    }
  }

  async function unpublishCourse(courseId: string): Promise<void> {
    if (!confirm('Möchten Sie diesen Kurs wirklich zurückziehen?')) return

    try {
      await panelStore.unpublishCourse(courseId)
      loadCourses()
    } catch (error) {
      console.error('Failed to unpublish course:', error)
    }
  }

  async function archiveCourse(courseId: string): Promise<void> {
    if (!confirm('Möchten Sie diesen Kurs wirklich archivieren?')) return

    try {
      await panelStore.archiveCourse(courseId)
      loadCourses()
    } catch (error) {
      console.error('Failed to archive course:', error)
    }
  }

  async function unarchiveCourse(courseId: string): Promise<void> {
    if (!confirm('Möchten Sie diesen Kurs wirklich wiederherstellen?')) return

    try {
      await panelStore.unarchiveCourse(courseId)
      loadCourses()
    } catch (error) {
      console.error('Failed to unarchive course:', error)
    }
  }

  async function permanentDeleteCourse(courseId: string, courseTitle: string): Promise<void> {
    const confirmMessage =
      `WARNUNG: Der Kurs "${courseTitle}" wird PERMANENT gelöscht!\n\n` +
      `Dies kann NICHT rückgängig gemacht werden.\n` +
      `Alle Kapitel, Lektionen und Einschreibungen werden ebenfalls gelöscht.\n\n` +
      `Sind Sie absolut sicher?`

    if (!confirm(confirmMessage)) return

    const doubleConfirm = prompt(
      `Geben Sie "LÖSCHEN" ein, um den Kurs "${courseTitle}" permanent zu löschen:`
    )
    if (doubleConfirm !== 'LÖSCHEN') {
      alert('Löschvorgang abgebrochen.')
      return
    }

    try {
      await panelStore.permanentDeleteCourse(courseId, 'Permanent gelöscht durch Admin')
      loadCourses()
    } catch (error) {
      console.error('Failed to permanently delete course:', error)
      alert('Fehler beim Löschen des Kurses.')
    }
  }

  // -------------------------------------------------------------------
  // Display helpers
  // -------------------------------------------------------------------

  function getStatusBadgeClass(status: string): string {
    switch (status) {
      case 'draft':     return 'bg-gray-100 text-gray-800'
      case 'published': return 'bg-green-100 text-green-800'
      case 'archived':  return 'bg-red-100 text-red-800'
      default:          return 'bg-gray-100 text-gray-800'
    }
  }

  function getStatusLabel(status: string): string {
    switch (status) {
      case 'draft':     return t('panel.courses.draft')
      case 'published': return t('panel.courses.statusPublished')
      case 'archived':  return t('panel.courses.archived')
      default:          return status
    }
  }

  function getLevelLabel(level?: string): string {
    if (!level) return t('panel.courses.notSpecified')

    switch (level) {
      case 'beginner':     return t('courses.level_beginner')
      case 'intermediate': return t('courses.level_intermediate')
      case 'advanced':     return t('courses.level_advanced')
      default:             return level
    }
  }

  // -------------------------------------------------------------------
  // Window actions
  // -------------------------------------------------------------------

  function openCourseCreateWindow(): void {
    windowStore.openWindow({
      type: 'panel-course-create',
      title: t('panel.courses.createNewCourse'),
      icon: '📚'
    })
  }

  function openWindowManager(): void {
    windowStore.openWindow({
      type: 'panel-window-manager',
      title: t('panel.courses.panelManager'),
      icon: '🗂',
      size: { width: 400, height: 500 }
    })
  }

  // -------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------

  onMounted(async () => {
    await Promise.allSettled([
      loadCourses().catch(err => {
        console.error('Failed to load courses:', err)
      }),
      panelStore.loadCategoryTree().catch(err => {
        console.warn('Failed to load categories (database not initialized?):', err)
      })
    ])
  })

  return {
    // State
    searchQuery,
    statusFilter,
    levelFilter,
    categoryFilter,
    currentPage,
    perPage,
    flatCategories,
    totalPages,
    panelStore,

    // Actions
    loadCourses,
    debouncedSearch,
    resetFilters,
    changePage,
    viewCourseDetail,
    publishCourse,
    unpublishCourse,
    archiveCourse,
    unarchiveCourse,
    permanentDeleteCourse,

    // Display helpers
    getStatusBadgeClass,
    getStatusLabel,
    getLevelLabel,

    // Window actions
    openCourseCreateWindow,
    openWindowManager
  }
}
