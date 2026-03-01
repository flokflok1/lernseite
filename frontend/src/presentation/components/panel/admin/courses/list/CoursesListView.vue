<template>
  <div class="panel-courses-page">
    <!-- Page Header - Compact -->
    <div class="mb-3 flex justify-between items-center">
      <div>
        <h1 class="text-lg font-bold text-[var(--color-text-primary)]">{{ $t('panel.courses.title') }}</h1>
        <p class="text-xs text-[var(--color-text-secondary)]">{{ $t('panel.courses.subtitle') }}</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="openCourseCreateWindow"
          class="px-3 py-1.5 text-sm bg-[var(--color-primary)] text-white rounded hover:bg-[var(--color-primary-dark)] transition-colors font-medium"
        >
          + {{ $t('panel.courses.create') }}
        </button>
        <button
          @click="openWindowManager"
          class="px-3 py-1.5 text-sm bg-[var(--color-surface)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded hover:bg-[var(--color-background)] transition-colors"
        >
          {{ $t('panel.courses.panels') }}
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
            :placeholder="$t('panel.courses.searchPlaceholder')"
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
            <option :value="undefined">{{ $t('panel.courses.allCategories') }}</option>
            <option
              v-for="cat in flatCategories"
              :key="cat.category_id"
              :value="cat.category_id"
            >
              {{ '\u2014'.repeat(cat.level - 1) }} {{ cat.name }}
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
        <table class="w-full">
          <thead class="bg-[var(--color-background)] border-b border-[var(--color-border)]">
            <tr>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">{{ $t('panel.courses.columnTitle') }}</th>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">{{ $t('panel.courses.creator') }}</th>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">{{ $t('common.status') }}</th>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">Level</th>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">{{ $t('panel.courses.chapters') }}</th>
              <th class="px-3 py-2 text-left text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">{{ $t('panel.courses.enrollments') }}</th>
              <th class="px-3 py-2 text-right text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody class="bg-[var(--color-surface)] divide-y divide-[var(--color-border)]">
            <tr v-for="course in panelStore.courses" :key="course.course_id" class="hover:bg-[var(--color-background)]">
              <td class="px-3 py-2">
                <div class="text-xs font-medium text-[var(--color-text-primary)] truncate max-w-[200px]" :title="course.title">{{ course.title }}</div>
                <div v-if="course.category_name || course.category" class="text-[10px] text-[var(--color-text-secondary)] truncate">{{ course.category_name || course.category }}</div>
              </td>
              <td class="px-3 py-2">
                <div class="text-xs text-[var(--color-text-primary)] truncate max-w-[100px]">{{ course.creator_name || $t('panel.courses.unknown') }}</div>
              </td>
              <td class="px-3 py-2">
                <span :class="getStatusBadgeClass(course.status)" class="px-1.5 py-0.5 inline-flex text-[10px] leading-4 font-semibold rounded-full">{{ getStatusLabel(course.status) }}</span>
              </td>
              <td class="px-3 py-2 text-xs text-[var(--color-text-primary)]">{{ getLevelLabel(course.level) }}</td>
              <td class="px-3 py-2 text-xs text-[var(--color-text-primary)]">{{ course.module_count }}</td>
              <td class="px-3 py-2 text-xs text-[var(--color-text-primary)]">{{ course.enrollment_count }}</td>
              <td class="px-3 py-2 whitespace-nowrap text-right text-xs font-medium">
                <div class="flex justify-end gap-1">
                  <button @click="viewCourseDetail(course.course_id)" class="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] px-2 py-1 text-xs border border-[var(--color-primary)] rounded hover:bg-[var(--color-primary)] hover:text-white transition-colors">{{ $t('common.details') }}</button>
                  <button v-if="course.status === 'draft'" @click="publishCourse(course.course_id)" class="text-green-600 hover:text-green-800 px-2 py-1 text-xs border border-green-600 rounded hover:bg-green-600 hover:text-white transition-colors">{{ $t('panel.courses.publish') }}</button>
                  <button v-if="course.status === 'published'" @click="unpublishCourse(course.course_id)" class="text-yellow-600 hover:text-yellow-800 px-2 py-1 text-xs border border-yellow-600 rounded hover:bg-yellow-600 hover:text-white transition-colors">{{ $t('panel.courses.unpublish') }}</button>
                  <button v-if="course.status !== 'archived'" @click="archiveCourse(course.course_id)" class="text-yellow-600 hover:text-yellow-800 px-2 py-1 text-xs border border-yellow-600 rounded hover:bg-yellow-600 hover:text-white transition-colors">{{ $t('panel.courses.archive') }}</button>
                  <button v-if="course.status === 'archived'" @click="unarchiveCourse(course.course_id)" class="text-blue-600 hover:text-blue-800 px-2 py-1 text-xs border border-blue-600 rounded hover:bg-blue-600 hover:text-white transition-colors">{{ $t('panel.courses.restore') }}</button>
                  <button @click="permanentDeleteCourse(course.course_id, course.title)" class="text-red-700 hover:text-white px-2 py-1 text-xs border border-red-700 rounded hover:bg-red-700 transition-colors" :title="$t('panel.courses.deleteWarning')">{{ $t('common.delete') }}</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination - Compact -->
      <div v-if="panelStore.courses.length > 0" class="px-3 py-2 border-t border-[var(--color-border)]">
        <div class="flex items-center justify-between">
          <div class="text-xs text-[var(--color-text-secondary)]">
            {{ (currentPage - 1) * perPage + 1 }}-{{ Math.min(currentPage * perPage, panelStore.coursesTotal) }} von {{ panelStore.coursesTotal }}
          </div>
          <div class="flex gap-1 items-center">
            <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="px-2 py-1 text-xs border border-[var(--color-border)] rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--color-background)]">&lt;</button>
            <span class="px-2 py-1 text-xs text-[var(--color-text-primary)]">{{ currentPage }}/{{ totalPages }}</span>
            <button @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages" class="px-2 py-1 text-xs border border-[var(--color-border)] rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--color-background)]">&gt;</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { usePanelCourses } from '@/presentation/components/panel/admin/courses/composables/usePanelCourses'

const {
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
} = usePanelCourses()
</script>

<style scoped>
.panel-courses-page {
  padding: 1rem;
}
</style>
