<template>
  <div class="admin-course-list-content p-4">
    <!-- Header with Create Button -->
    <div class="mb-3 flex justify-between items-center">
      <div>
        <h3 class="text-base font-bold text-[var(--color-text-primary)]">{{ $t('panel.courses.title') }}</h3>
        <p class="text-xs text-[var(--color-text-secondary)]">{{ $t('panel.courses.description') }}</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="openCourseCreatePanel"
          class="px-3 py-1.5 text-sm bg-[var(--color-primary)] text-white rounded hover:bg-[var(--color-primary-dark)] transition-colors font-medium"
        >
          + {{ $t('panel.courses.create') }}
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-[var(--color-surface-secondary)] rounded p-3 mb-3 border border-[var(--color-border)]">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-2 items-end">
        <!-- Search -->
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            {{ $t('common.search') }}
          </label>
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('panel.courses.searchPlaceholder')"
            class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-1 focus:ring-[var(--color-primary)]"
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
            class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)]"
            @change="loadCourses"
          >
            <option :value="undefined">{{ $t('panel.courses.allCategories') }}</option>
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
            class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)]"
            @change="loadCourses"
          >
            <option value="all">{{ $t('panel.courses.allStatus') }}</option>
            <option value="draft">{{ $t('panel.courses.draft') }}</option>
            <option value="published">{{ $t('panel.courses.statusPublished') }}</option>
            <option value="archived">{{ $t('panel.courses.archived') }}</option>
          </select>
        </div>

        <!-- Level Filter -->
        <div>
          <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            Level
          </label>
          <select
            v-model="levelFilter"
            class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)]"
            @change="loadCourses"
          >
            <option value="">{{ $t('courses.level_all') }}</option>
            <option value="beginner">{{ $t('courses.level_beginner') }}</option>
            <option value="intermediate">{{ $t('courses.level_intermediate') }}</option>
            <option value="advanced">{{ $t('courses.level_advanced') }}</option>
          </select>
        </div>

        <!-- Reset Button -->
        <div>
          <button
            @click="resetFilters"
            class="w-full px-2 py-1.5 text-xs text-[var(--color-text-secondary)] border border-[var(--color-border)] rounded hover:bg-[var(--color-background)]"
          >
            {{ $t('common.reset') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Courses Table -->
    <div class="bg-[var(--color-surface)] rounded border border-[var(--color-border)]">
      <div v-if="panelStore.isLoading" class="p-4 text-center">
        <p class="text-xs text-[var(--color-text-secondary)]">{{ $t('panel.courses.loading') }}</p>
      </div>

      <div v-else-if="panelStore.error" class="p-4 text-center">
        <p class="text-xs text-red-600">{{ panelStore.error }}</p>
      </div>

      <div v-else-if="panelStore.courses.length === 0" class="p-4 text-center">
        <p class="text-xs text-[var(--color-text-secondary)]">{{ $t('panel.courses.noCourses') }}</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-[var(--color-background)] border-b border-[var(--color-border)]">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">
                {{ $t('panel.courses.columnTitle') }}
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">
                {{ $t('panel.courses.creator') }}
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">
                {{ $t('common.status') }}
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">
                Level
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">
                {{ $t('panel.courses.chapters') }}
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase">
                {{ $t('panel.courses.enrollments') }}
              </th>
              <th class="px-3 py-2 text-right text-xs font-medium text-[var(--color-text-secondary)] uppercase">
                {{ $t('common.actions') }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--color-border)]">
            <tr
              v-for="course in panelStore.courses"
              :key="course.course_id"
              class="hover:bg-[var(--color-background)]"
            >
              <td class="px-3 py-2">
                <div class="text-xs font-medium truncate max-w-[150px]" :title="course.title">
                  {{ course.title }}
                </div>
                <div v-if="course.category_name" class="text-[10px] text-[var(--color-text-secondary)] truncate">
                  {{ course.category_name }}
                </div>
              </td>

              <td class="px-3 py-2">
                <div class="text-xs truncate max-w-[100px]">
                  {{ course.creator_name || $t('panel.courses.unknown') }}
                </div>
              </td>

              <td class="px-3 py-2">
                <span
                  :class="getStatusBadgeClass(course.status)"
                  class="px-1.5 py-0.5 inline-flex text-[10px] font-semibold rounded-full"
                >
                  {{ getStatusLabel(course.status) }}
                </span>
              </td>

              <td class="px-3 py-2 text-xs">
                {{ getLevelLabel(course.level) }}
              </td>

              <td class="px-3 py-2 text-xs">
                {{ course.module_count || 0 }}
              </td>

              <td class="px-3 py-2 text-xs">
                {{ course.enrollment_count || 0 }}
              </td>

              <td class="px-3 py-2 text-right">
                <div class="flex justify-end gap-1">
                  <button
                    @click="viewCourseDetail(course.course_id)"
                    class="text-[var(--color-primary)] hover:text-white px-2 py-1 text-xs border border-[var(--color-primary)] rounded hover:bg-[var(--color-primary)]"
                  >
                    {{ $t('common.edit') }}
                  </button>

                  <button
                    v-if="course.status === 'draft'"
                    @click="publishCourse(course.course_id)"
                    class="text-green-600 hover:text-white px-2 py-1 text-xs border border-green-600 rounded hover:bg-green-600"
                  >
                    {{ $t('panel.courses.publish') }}
                  </button>

                  <button
                    v-if="course.status === 'published'"
                    @click="unpublishCourse(course.course_id)"
                    class="text-yellow-600 hover:text-white px-2 py-1 text-xs border border-yellow-600 rounded hover:bg-yellow-600"
                  >
                    {{ $t('panel.courses.unpublish') }}
                  </button>

                  <button
                    @click="archiveCourse(course.course_id)"
                    v-if="course.status !== 'archived'"
                    class="text-yellow-600 hover:text-white px-2 py-1 text-xs border border-yellow-600 rounded hover:bg-yellow-600"
                  >
                    {{ $t('panel.courses.archive') }}
                  </button>

                  <button
                    v-if="course.status === 'archived'"
                    @click="unarchiveCourse(course.course_id)"
                    class="text-blue-600 hover:text-white px-2 py-1 text-xs border border-blue-600 rounded hover:bg-blue-600"
                  >
                    {{ $t('panel.courses.restore') }}
                  </button>

                  <button
                    @click="permanentDeleteCourse(course.course_id, course.title)"
                    class="text-red-700 hover:text-white px-2 py-1 text-xs border border-red-700 rounded hover:bg-red-700"
                  >
                    {{ $t('common.delete') }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="panelStore.courses.length > 0" class="px-3 py-2 border-t border-[var(--color-border)] flex justify-between items-center">
        <div class="text-xs text-[var(--color-text-secondary)]">
          {{ (currentPage - 1) * perPage + 1 }}-{{ Math.min(currentPage * perPage, panelStore.coursesTotal) }} von {{ panelStore.coursesTotal }}
        </div>
        <div class="flex gap-1">
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-2 py-1 text-xs border border-[var(--color-border)] rounded disabled:opacity-50"
          >
            &lt;
          </button>
          <span class="px-2 py-1 text-xs">{{ currentPage }}/{{ Math.ceil(panelStore.coursesTotal / perPage) }}</span>
          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage >= Math.ceil(panelStore.coursesTotal / perPage)"
            class="px-2 py-1 text-xs border border-[var(--color-border)] rounded disabled:opacity-50"
          >
            &gt;
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/admin'
import { usePanelStore } from '@/application/stores/modules/desktop'
import type { Category } from '@/application/services/api/admin'

const { t } = useI18n()
const router = useRouter()
const panelStore = usePanelStore()
const windowStore = usePanelStore()

// Filters
const searchQuery = ref('')
const statusFilter = ref<'all' | 'draft' | 'published' | 'archived'>('all')
const levelFilter = ref('')
const categoryFilter = ref<number | undefined>(undefined)

// Pagination
const currentPage = ref(1)
const perPage = ref(20)

let searchTimeout: ReturnType<typeof setTimeout> | null = null

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
  flatten(panelStore.categoryTree)
  return result
})

const loadCourses = async () => {
  await panelStore.loadCourses({
    page: currentPage.value,
    per_page: perPage.value,
    search: searchQuery.value || undefined,
    status: statusFilter.value === 'all' ? undefined : statusFilter.value,
    level: levelFilter.value || undefined,
    category_id: categoryFilter.value || undefined
  })
}

const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadCourses()
  }, 500)
}

const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = 'all'
  levelFilter.value = ''
  categoryFilter.value = undefined
  currentPage.value = 1
  loadCourses()
}

const changePage = (page: number) => {
  currentPage.value = page
  loadCourses()
}

const viewCourseDetail = (courseId: string) => {
  if (!courseId) return
  windowStore.openPanel({
    type: 'admin-course-editor',
    title: t('panel.courses.editCourse'),
    icon: '📝'
  })
  // TODO: Pass course ID to window content
}

const publishCourse = async (courseId: string) => {
  if (!confirm(t('panel.courses.confirmPublish'))) return
  try {
    await panelStore.publishCourse(courseId)
    loadCourses()
  } catch (error) {
    console.error('Failed to publish:', error)
  }
}

const unpublishCourse = async (courseId: string) => {
  if (!confirm(t('panel.courses.confirmUnpublish'))) return
  try {
    await panelStore.unpublishCourse(courseId)
    loadCourses()
  } catch (error) {
    console.error('Failed to unpublish:', error)
  }
}

const archiveCourse = async (courseId: string) => {
  if (!confirm(t('panel.courses.confirmArchive'))) return
  try {
    await panelStore.archiveCourse(courseId)
    loadCourses()
  } catch (error) {
    console.error('Failed to archive:', error)
  }
}

const unarchiveCourse = async (courseId: string) => {
  if (!confirm(t('panel.courses.confirmRestore'))) return
  try {
    await panelStore.unarchiveCourse(courseId)
    loadCourses()
  } catch (error) {
    console.error('Failed to restore:', error)
  }
}

const permanentDeleteCourse = async (courseId: string, courseTitle: string) => {
  if (!confirm(`Delete "${courseTitle}"?`)) return
  const doubleConfirm = prompt(`Type "LÖSCHEN" to confirm deletion of "${courseTitle}"`)
  if (doubleConfirm !== 'LÖSCHEN') return
  try {
    await panelStore.permanentDeleteCourse(courseId, 'Deleted by admin')
    loadCourses()
  } catch (error) {
    console.error('Failed to delete:', error)
  }
}

const getStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'draft': return 'bg-gray-100 text-gray-800'
    case 'published': return 'bg-green-100 text-green-800'
    case 'archived': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'draft': return t('panel.courses.draft')
    case 'published': return t('panel.courses.statusPublished')
    case 'archived': return t('panel.courses.archived')
    default: return status
  }
}

const getLevelLabel = (level?: string): string => {
  if (!level) return t('panel.courses.notSpecified')
  switch (level) {
    case 'beginner': return t('courses.level_beginner')
    case 'intermediate': return t('courses.level_intermediate')
    case 'advanced': return t('courses.level_advanced')
    default: return level
  }
}

function openCourseCreatePanel(): void {
  windowStore.openPanel({
    type: 'admin-course-create',
    title: t('panel.courses.createNewCourse'),
    icon: '📚'
  })
}

onMounted(async () => {
  await Promise.allSettled([
    loadCourses().catch(err => console.error('Failed to load courses:', err)),
    panelStore.loadCategoryTree().catch(err => console.warn('Failed to load categories:', err))
  ])
})
</script>

<style scoped>
.admin-course-list-content {
  height: 100%;
  overflow-y: auto;
}
</style>
