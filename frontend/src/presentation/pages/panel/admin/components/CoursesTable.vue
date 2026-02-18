<template>
  <div class="bg-[var(--color-surface)] rounded shadow-sm border border-[var(--color-border)]">
    <!-- Loading -->
    <div v-if="isLoading" class="p-4 text-center">
      <p class="text-xs text-[var(--color-text-secondary)]">{{ $t('panel.courses.loading') }}</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="p-4 text-center">
      <p class="text-xs text-red-600">{{ error }}</p>
    </div>

    <!-- Empty -->
    <div v-else-if="courses.length === 0" class="p-4 text-center">
      <p class="text-xs text-[var(--color-text-secondary)]">{{ $t('panel.courses.noCourses') }}</p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-[var(--color-background)] border-b border-[var(--color-border)]">
          <tr>
            <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              {{ $t('panel.courses.columnTitle') }}
            </th>
            <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              {{ $t('panel.courses.creator') }}
            </th>
            <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              {{ $t('common.status') }}
            </th>
            <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              Level
            </th>
            <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              {{ $t('panel.courses.chapters') }}
            </th>
            <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              {{ $t('panel.courses.enrollments') }}
            </th>
            <th class="px-3 py-2 text-right text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              {{ $t('common.actions') }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-[var(--color-surface)] divide-y divide-[var(--color-border)]">
          <tr
            v-for="course in courses"
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
                {{ course.creator_name || $t('panel.courses.unknown') }}
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
                <button
                  @click="$emit('viewDetail', course.course_id)"
                  class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] px-2 py-1 text-xs border border-[var(--color-primary)] rounded hover:bg-[var(--color-primary)] hover:text-white transition-colors"
                >
                  {{ $t('common.details') }}
                </button>

                <button
                  v-if="course.status === 'draft'"
                  @click="$emit('publish', course.course_id)"
                  class="text-green-600 hover:text-green-800 px-2 py-1 text-xs border border-green-600 rounded hover:bg-green-600 hover:text-white transition-colors"
                >
                  {{ $t('panel.courses.publish') }}
                </button>

                <button
                  v-if="course.status === 'published'"
                  @click="$emit('unpublish', course.course_id)"
                  class="text-yellow-600 hover:text-yellow-800 px-2 py-1 text-xs border border-yellow-600 rounded hover:bg-yellow-600 hover:text-white transition-colors"
                >
                  {{ $t('panel.courses.unpublish') }}
                </button>

                <button
                  v-if="course.status !== 'archived'"
                  @click="$emit('archive', course.course_id)"
                  class="text-yellow-600 hover:text-yellow-800 px-2 py-1 text-xs border border-yellow-600 rounded hover:bg-yellow-600 hover:text-white transition-colors"
                >
                  {{ $t('panel.courses.archive') }}
                </button>

                <button
                  v-if="course.status === 'archived'"
                  @click="$emit('unarchive', course.course_id)"
                  class="text-blue-600 hover:text-blue-800 px-2 py-1 text-xs border border-blue-600 rounded hover:bg-blue-600 hover:text-white transition-colors"
                >
                  {{ $t('panel.courses.restore') }}
                </button>

                <button
                  @click="$emit('permanentDelete', course.course_id, course.title)"
                  class="text-red-700 hover:text-white px-2 py-1 text-xs border border-red-700 rounded hover:bg-red-700 transition-colors"
                  :title="$t('panel.courses.deleteWarning')"
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
    <div v-if="courses.length > 0" class="px-3 py-2 border-t border-[var(--color-border)]">
      <div class="flex items-center justify-between">
        <div class="text-xs text-[var(--color-text-secondary)]">
          {{ (currentPage - 1) * perPage + 1 }}-{{ Math.min(currentPage * perPage, coursesTotal) }} von {{ coursesTotal }}
        </div>
        <div class="flex gap-1 items-center">
          <button
            @click="$emit('changePage', currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-2 py-1 text-xs border border-[var(--color-border)] rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--color-background)]"
          >
            &lt;
          </button>
          <span class="px-2 py-1 text-xs text-[var(--color-text-primary)]">
            {{ currentPage }}/{{ totalPages }}
          </span>
          <button
            @click="$emit('changePage', currentPage + 1)"
            :disabled="currentPage >= totalPages"
            class="px-2 py-1 text-xs border border-[var(--color-border)] rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--color-background)]"
          >
            &gt;
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  courses: any[]
  coursesTotal: number
  currentPage: number
  perPage: number
  totalPages: number
  isLoading: boolean
  error: string | null
  getStatusBadgeClass: (status: string) => string
  getStatusLabel: (status: string) => string
  getLevelLabel: (level?: string) => string
}

defineProps<Props>()

defineEmits<{
  viewDetail: [courseId: string]
  publish: [courseId: string]
  unpublish: [courseId: string]
  archive: [courseId: string]
  unarchive: [courseId: string]
  permanentDelete: [courseId: string, courseTitle: string]
  changePage: [page: number]
}>()
</script>
