<template>
  <div class="admin-courses-page">
    <!-- Page Header - Compact -->
    <div class="mb-3 flex justify-between items-center">
      <div>
        <h1 class="text-lg font-bold text-[var(--color-text-primary)]">{{ $t('admin.courses.title') }}</h1>
        <p class="text-xs text-[var(--color-text-secondary)]">{{ $t('admin.courses.subtitle') }}</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="openCourseCreateWindow"
          class="px-3 py-1.5 text-sm bg-[var(--color-primary)] text-white rounded hover:bg-[var(--color-primary-dark)] transition-colors font-medium"
        >
          + {{ $t('admin.courses.create') }}
        </button>
        <button
          @click="openWindowManager"
          class="px-3 py-1.5 text-sm bg-[var(--color-surface)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded hover:bg-[var(--color-background)] transition-colors"
        >
          {{ $t('admin.courses.windows') }}
        </button>
      </div>
    </div>

    <!-- Filters - Compact -->
    <div class="bg-[var(--color-surface)] rounded shadow-sm p-3 mb-3 border border-[var(--color-border)]">
      <div class="grid grid-cols-1 md:grid-cols-6 gap-2 items-end">
        <!-- Search -->
        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ $t('common.search') }}
          </label>
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('admin.courses.searchPlaceholder')"
            class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-1 focus:ring-[var(--color-primary)] focus:border-transparent"
            @input="debouncedSearch"
          />
        </div>

        <!-- Category Filter -->
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ $t('courses.category') }}
          </label>
          <select
            v-model="categoryFilter"
            class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-1 focus:ring-[var(--color-primary)] focus:border-transparent"
            @change="loadCourses"
          >
            <option :value="undefined">{{ $t('admin.courses.allCategories') }}</option>
            <option
              v-for="cat in flatCategories"
              :key="cat.category_id"
              :value="cat.category_id"
            >
              {{ '—'.repeat(cat.level - 1) }} {{ cat.name }}
            </option>
          </select>
        </div>

        <!-- Status Filter -->
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ $t('common.status') }}
          </label>
          <select
            v-model="statusFilter"
            class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-1 focus:ring-[var(--color-primary)] focus:border-transparent"
            @change="loadCourses"
          >
            <option value="all">{{ $t('admin.courses.allStatus') }}</option>
            <option value="draft">{{ $t('admin.courses.draft') }}</option>
            <option value="published">{{ $t('admin.courses.statusPublished') }}</option>
            <option value="archived">{{ $t('admin.courses.archived') }}</option>
          </select>
        </div>

        <!-- Level Filter -->
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            Level
          </label>
          <select
            v-model="levelFilter"
            class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-1 focus:ring-[var(--color-primary)] focus:border-transparent"
            @change="loadCourses"
          >
            <option value="">{{ $t('courses.level_all') }}</option>
            <option value="beginner">{{ $t('courses.level_beginner') }}</option>
            <option value="intermediate">{{ $t('courses.level_intermediate') }}</option>
            <option value="advanced">{{ $t('courses.level_advanced') }}</option>
          </select>
        </div>

        <!-- Reset Filters Button -->
        <div>
          <button
            @click="resetFilters"
            class="w-full px-2 py-1.5 text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] border border-[var(--color-border)] rounded hover:bg-[var(--color-background)]"
          >
            {{ $t('common.reset') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Courses Table -->
    <div class="bg-[var(--color-surface)] rounded shadow-sm border border-[var(--color-border)]">
      <div v-if="adminStore.isLoading" class="p-4 text-center">
        <p class="text-xs text-[var(--color-text-secondary)]">{{ $t('admin.courses.loading') }}</p>
      </div>

      <div v-else-if="adminStore.error" class="p-4 text-center">
        <p class="text-xs text-red-600">{{ adminStore.error }}</p>
      </div>

      <div v-else-if="adminStore.courses.length === 0" class="p-4 text-center">
        <p class="text-xs text-[var(--color-text-secondary)]">{{ $t('admin.courses.noCourses') }}</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-[var(--color-background)] border-b border-[var(--color-border)]">
            <tr>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                {{ $t('admin.courses.columnTitle') }}
              </th>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                {{ $t('admin.courses.creator') }}
              </th>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                {{ $t('common.status') }}
              </th>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                Level
              </th>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                {{ $t('admin.courses.chapters') }}
              </th>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                {{ $t('admin.courses.enrollments') }}
              </th>
              <th class="px-3 py-2 text-right text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                {{ $t('common.actions') }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-[var(--color-surface)] divide-y divide-[var(--color-border)]">
            <tr
              v-for="course in adminStore.courses"
              :key="course.course_id"
              class="hover:bg-[var(--color-background)]"
            >
              <!-- Title -->
              <td class="px-3 py-2">
                <div class="text-xs font-medium text-[var(--color-text-primary)] truncate max-w-[200px]" :title="course.title">
                  {{ course.title }}
                </div>
                <div v-if="course.category_name || course.category" class="text-[10px] text-[var(--color-text-secondary)] truncate">
                  {{ course.category_name || course.category }}
                </div>
              </td>

              <!-- Creator -->
              <td class="px-3 py-2">
                <div class="text-xs text-[var(--color-text-primary)] truncate max-w-[100px]">
                  {{ course.creator_name || $t('admin.courses.unknown') }}
                </div>
              </td>

              <!-- Status -->
              <td class="px-3 py-2">
                <span
                  :class="getStatusBadgeClass(course.status)"
                  class="px-1.5 py-0.5 inline-flex text-[10px] leading-4 font-semibold rounded-full"
                >
                  {{ getStatusLabel(course.status) }}
                </span>
              </td>

              <!-- Level -->
              <td class="px-3 py-2 text-xs text-[var(--color-text-primary)]">
                {{ getLevelLabel(course.level) }}
              </td>

              <!-- Modules -->
              <td class="px-3 py-2 text-xs text-[var(--color-text-primary)]">
                {{ course.module_count }}
              </td>

              <!-- Enrollments -->
              <td class="px-3 py-2 text-xs text-[var(--color-text-primary)]">
                {{ course.enrollment_count }}
              </td>

              <!-- Actions -->
              <td class="px-3 py-2 whitespace-nowrap text-right text-xs font-medium">
                <div class="flex justify-end gap-1">
                  <!-- Details Button -->
                  <button
                    @click="viewCourseDetail(course.course_id)"
                    class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] px-2 py-1 text-xs border border-[var(--color-primary)] rounded hover:bg-[var(--color-primary)] hover:text-white transition-colors"
                  >
                    {{ $t('common.details') }}
                  </button>

                  <!-- Publish Button (only for drafts) -->
                  <button
                    v-if="course.status === 'draft'"
                    @click="publishCourse(course.course_id)"
                    class="text-green-600 hover:text-green-800 px-2 py-1 text-xs border border-green-600 rounded hover:bg-green-600 hover:text-white transition-colors"
                  >
                    {{ $t('admin.courses.publish') }}
                  </button>

                  <!-- Unpublish Button (only for published) -->
                  <button
                    v-if="course.status === 'published'"
                    @click="unpublishCourse(course.course_id)"
                    class="text-yellow-600 hover:text-yellow-800 px-2 py-1 text-xs border border-yellow-600 rounded hover:bg-yellow-600 hover:text-white transition-colors"
                  >
                    {{ $t('admin.courses.unpublish') }}
                  </button>

                  <!-- Archive Button (only for draft/published) -->
                  <button
                    v-if="course.status !== 'archived'"
                    @click="archiveCourse(course.course_id)"
                    class="text-yellow-600 hover:text-yellow-800 px-2 py-1 text-xs border border-yellow-600 rounded hover:bg-yellow-600 hover:text-white transition-colors"
                  >
                    {{ $t('admin.courses.archive') }}
                  </button>

                  <!-- Restore Button (only for archived) -->
                  <button
                    v-if="course.status === 'archived'"
                    @click="unarchiveCourse(course.course_id)"
                    class="text-blue-600 hover:text-blue-800 px-2 py-1 text-xs border border-blue-600 rounded hover:bg-blue-600 hover:text-white transition-colors"
                  >
                    {{ $t('admin.courses.restore') }}
                  </button>

                  <!-- Permanent Delete Button (always visible) -->
                  <button
                    @click="permanentDeleteCourse(course.course_id, course.title)"
                    class="text-red-700 hover:text-white px-2 py-1 text-xs border border-red-700 rounded hover:bg-red-700 transition-colors"
                    :title="$t('admin.courses.deleteWarning')"
                  >
                    {{ $t('common.delete') }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination - Compact -->
      <div v-if="adminStore.courses.length > 0" class="px-3 py-2 border-t border-[var(--color-border)]">
        <div class="flex items-center justify-between">
          <div class="text-xs text-[var(--color-text-secondary)]">
            {{ (currentPage - 1) * perPage + 1 }}-{{ Math.min(currentPage * perPage, adminStore.coursesTotal) }} von {{ adminStore.coursesTotal }}
          </div>
          <div class="flex gap-1 items-center">
            <button
              @click="changePage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-2 py-1 text-xs border border-[var(--color-border)] rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--color-background)]"
            >
              &lt;
            </button>
            <span class="px-2 py-1 text-xs text-[var(--color-text-primary)]">
              {{ currentPage }}/{{ Math.ceil(adminStore.coursesTotal / perPage) }}
            </span>
            <button
              @click="changePage(currentPage + 1)"
              :disabled="currentPage >= Math.ceil(adminStore.coursesTotal / perPage)"
              class="px-2 py-1 text-xs border border-[var(--color-border)] rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--color-background)]"
            >
              &gt;
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAdminStore } from '@/store/admin.store'
import { useWindowStore } from '@/store/window.store'
import type { Category } from '@/api/admin.api'

const { t } = useI18n()
const router = useRouter()
const adminStore = useAdminStore()
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
  const flatten = (nodes: any[], parentLevel: number = 0) => {
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
        flatten(node.children, node.level)
      }
    }
  }
  flatten(adminStore.categoryTree)
  return result
})

/**
 * Load courses with current filters
 */
const loadCourses = async () => {
  await adminStore.loadCourses({
    page: currentPage.value,
    per_page: perPage.value,
    search: searchQuery.value || undefined,
    status: statusFilter.value === 'all' ? undefined : statusFilter.value,
    level: levelFilter.value || undefined,
    category_id: categoryFilter.value || undefined
  })
}

/**
 * Debounced search handler
 */
const debouncedSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1 // Reset to first page on new search
    loadCourses()
  }, 500)
}

/**
 * Reset all filters
 */
const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = 'all'
  levelFilter.value = ''
  categoryFilter.value = undefined
  currentPage.value = 1
  loadCourses()
}

/**
 * Change page
 */
const changePage = (page: number) => {
  currentPage.value = page
  loadCourses()
}

/**
 * Navigate to course detail page
 */
const viewCourseDetail = (courseId: string) => {
  // Ensure courseId is valid before navigation
  if (!courseId || typeof courseId !== 'string') {
    console.error('Invalid course ID:', courseId)
    return
  }
  router.push({ name: 'admin-course-detail', params: { id: courseId } })
}

/**
 * Publish a course
 */
const publishCourse = async (courseId: string) => {
  if (!confirm(t('admin.courses.confirmPublish'))) {
    return
  }

  try {
    await adminStore.publishCourse(courseId)
    loadCourses() // Reload to update status
  } catch (error) {
    console.error('Failed to publish course:', error)
  }
}

/**
 * Unpublish a course
 */
const unpublishCourse = async (courseId: string) => {
  if (!confirm(t('admin.courses.confirmUnpublish'))) {
    return
  }

  try {
    await adminStore.unpublishCourse(courseId)
    loadCourses() // Reload to update status
  } catch (error) {
    console.error('Failed to unpublish course:', error)
  }
}

/**
 * Archive a course
 */
const archiveCourse = async (courseId: string) => {
  if (!confirm(t('admin.courses.confirmArchive'))) {
    return
  }

  try {
    await adminStore.archiveCourse(courseId)
    loadCourses() // Reload to update status
  } catch (error) {
    console.error('Failed to archive course:', error)
  }
}

/**
 * Unarchive (restore) a course
 */
const unarchiveCourse = async (courseId: string) => {
  if (!confirm(t('admin.courses.confirmRestore'))) {
    return
  }

  try {
    await adminStore.unarchiveCourse(courseId)
    loadCourses() // Reload to update status
  } catch (error) {
    console.error('Failed to unarchive course:', error)
  }
}

/**
 * Permanently delete a course (hard delete)
 */
const permanentDeleteCourse = async (courseId: string, courseTitle: string) => {
  const confirmMessage = t('admin.courses.confirmDeleteWarning', { title: courseTitle })

  if (!confirm(confirmMessage)) {
    return
  }

  // Double confirmation for safety
  const doubleConfirm = prompt(t('admin.courses.confirmDeletePrompt', { title: courseTitle }))
  if (doubleConfirm !== 'LÖSCHEN') {
    return
  }

  try {
    await adminStore.permanentDeleteCourse(courseId, `Permanent gelöscht durch Admin`)
    loadCourses() // Reload to update list
  } catch (error) {
    console.error('Failed to permanently delete course:', error)
  }
}

/**
 * Get CSS classes for status badge
 */
const getStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'draft':
      return 'bg-gray-100 text-gray-800'
    case 'published':
      return 'bg-green-100 text-green-800'
    case 'archived':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get translated label for status
 */
const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'draft':
      return t('admin.courses.draft')
    case 'published':
      return t('admin.courses.statusPublished')
    case 'archived':
      return t('admin.courses.archived')
    default:
      return status
  }
}

/**
 * Get translated label for level
 */
const getLevelLabel = (level?: string): string => {
  if (!level) return t('admin.courses.notSpecified')

  switch (level) {
    case 'beginner':
      return t('courses.level_beginner')
    case 'intermediate':
      return t('courses.level_intermediate')
    case 'advanced':
      return t('courses.level_advanced')
    default:
      return level
  }
}

/**
 * Open course create window
 */
function openCourseCreateWindow(): void {
  windowStore.openWindow({
    type: 'admin-course-create',
    title: t('admin.courses.createNewCourse'),
    icon: '📚'
  })
}

/**
 * Open window manager
 */
function openWindowManager(): void {
  windowStore.openWindow({
    type: 'admin-window-manager',
    title: t('admin.courses.windowManager'),
    icon: '🗂',
    size: { width: 400, height: 500 }
  })
}

// Load courses and categories on mount
onMounted(async () => {
  // Load courses and categories, but handle errors gracefully
  await Promise.allSettled([
    loadCourses().catch(err => {
      console.error('Failed to load courses:', err)
      // UI will show empty state
    }),
    adminStore.loadCategoryTree().catch(err => {
      console.warn('Failed to load categories (database not initialized?):', err)
      // UI will work without categories
    })
  ])
})
</script>

<style scoped>
.admin-courses-page {
  padding: 1rem;
}
</style>
