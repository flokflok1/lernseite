/**
 * CourseSelector.vue
 *
 * Course list view shown before the editor when no course is selected.
 * Displays user's courses with search, create, and delete functionality.
 * Dark-mode-ready using CSS variables from the start.
 */

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

const { t } = useI18n()
const store = useCourseEditorStore()

const emit = defineEmits<{
  select: [courseId: number]
  create: []
}>()

const searchQuery = ref('')

onMounted(() => {
  store.listCourses()
})

const filteredCourses = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return store.courseList
  return store.courseList.filter(
    (c: any) =>
      c.title?.toLowerCase().includes(q) ||
      c.description?.toLowerCase().includes(q)
  )
})

const getStatusKey = (course: any): string => {
  if (course.is_published) return 'published'
  return 'draft'
}

const getStatusClass = (course: any): string => {
  if (course.is_published) return 'status-published'
  return 'status-draft'
}

const formatDate = (dateStr: string | undefined): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString(undefined, { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const handleDelete = async (course: any) => {
  const confirmed = confirm(t('panel.manualEditor.courseSelector.confirmDelete', { title: course.title }))
  if (!confirmed) return
  try {
    await store.deleteCourseById(course.course_id)
  } catch {
    // Error is set in store
  }
}
</script>

<template>
  <div class="course-selector">
    <!-- Header -->
    <div class="selector-header">
      <h2 class="selector-title">{{ $t('panel.manualEditor.courseSelector.title') }}</h2>
      <button class="btn-create" @click="emit('create')">
        + {{ $t('panel.manualEditor.courseSelector.createNew') }}
      </button>
    </div>

    <!-- Search -->
    <div class="search-bar">
      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        :placeholder="$t('panel.manualEditor.courseSelector.search')"
      />
    </div>

    <!-- Loading -->
    <div v-if="store.courseListLoading" class="loading-state">
      <p>{{ $t('common.loading') }}...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="store.courseList.length === 0" class="empty-state">
      <p class="empty-title">{{ $t('panel.manualEditor.courseSelector.noCourses') }}</p>
      <p class="empty-hint">{{ $t('panel.manualEditor.courseSelector.noCoursesHint') }}</p>
    </div>

    <!-- No search results -->
    <div v-else-if="filteredCourses.length === 0" class="empty-state">
      <p class="empty-title">{{ $t('panel.manualEditor.courseSelector.noResults') }}</p>
    </div>

    <!-- Course list -->
    <div v-else class="course-list">
      <div
        v-for="course in filteredCourses"
        :key="course.course_id"
        class="course-card"
        @click="emit('select', course.course_id)"
      >
        <div class="card-body">
          <div class="card-top">
            <span class="course-title">{{ course.title }}</span>
            <span class="status-badge" :class="getStatusClass(course)">
              {{ $t(`panel.manualEditor.courseSelector.status.${getStatusKey(course)}`) }}
            </span>
          </div>
          <p v-if="course.description" class="course-desc">{{ course.description }}</p>
          <div class="card-meta">
            <span v-if="course.total_chapters != null" class="meta-item">
              {{ $t('panel.manualEditor.courseSelector.chapters', { count: course.total_chapters }) }}
            </span>
            <span class="meta-item">
              {{ $t('panel.manualEditor.courseSelector.lastEdited') }}: {{ formatDate(course.updated_at || course.created_at) }}
            </span>
          </div>
        </div>
        <button
          class="btn-delete"
          @click.stop="handleDelete(course)"
          :title="$t('media.delete')"
        >
          &times;
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.course-selector {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  overflow: hidden;
  background: var(--color-bg);
}

.selector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.selector-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.btn-create {
  padding: 8px 16px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: filter 0.15s;
}

.btn-create:hover {
  filter: brightness(0.9);
}

.search-bar {
  margin-bottom: 16px;
  flex-shrink: 0;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 14px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}

.loading-state,
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 4px;
}

.empty-hint {
  font-size: 13px;
  margin: 0;
}

.course-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.course-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface);
  cursor: pointer;
  transition: all 0.15s;
}

.course-card:hover {
  border-color: var(--color-accent);
  background: color-mix(in srgb, var(--color-accent) 5%, var(--color-surface));
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.course-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.status-draft {
  background: color-mix(in srgb, var(--color-text-tertiary) 15%, transparent);
  color: var(--color-text-secondary);
}

.status-published {
  background: color-mix(in srgb, var(--color-success) 15%, transparent);
  color: var(--color-success);
}

.course-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0 0 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.btn-delete {
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
  transition: all 0.15s;
}

.btn-delete:hover {
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
  border-color: var(--color-error);
  color: var(--color-error);
}
</style>
