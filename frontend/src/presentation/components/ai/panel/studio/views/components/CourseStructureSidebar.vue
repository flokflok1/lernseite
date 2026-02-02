<!--
  CourseStructureSidebar - Chapter tree with search and expansion
-->

<template>
  <div class="course-structure-sidebar">
    <!-- Search -->
    <div class="sidebar-search">
      <div class="search-wrapper">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('panel.aiStudio.search')"
          class="search-input"
        />
        <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>

    <!-- Chapter Tree -->
    <div class="chapter-tree">
      <!-- No Course Selected -->
      <div v-if="!course" class="empty-state">
        <p>{{ $t('panel.aiStudio.selectCourseToView') }}</p>
      </div>

      <!-- Loading -->
      <div v-else-if="isLoading" class="loading-state">
        <div class="spinner"></div>
      </div>

      <!-- Chapters -->
      <template v-else>
        <div v-for="chapter in filteredChapters" :key="chapter.chapter_id" class="chapter-block">
          <!-- Chapter Header -->
          <button
            @click="handleToggleChapter(chapter.chapter_id)"
            class="chapter-header"
            :class="{ active: selectedChapterId === chapter.chapter_id }"
          >
            <svg
              class="chapter-chevron"
              :class="{ expanded: isExpanded(chapter.chapter_id) }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span class="chapter-number">{{ chapter.order_index + 1 }}.</span>
            <span class="chapter-title">{{ chapter.title }}</span>
            <span class="lesson-count">{{ chapter.lessons?.length || 0 }}</span>
          </button>

          <!-- Lessons -->
          <div v-if="isExpanded(chapter.chapter_id)" class="lessons-list">
            <button
              v-for="lesson in chapter.lessons"
              :key="lesson.lesson_id"
              @click="handleSelectLesson(lesson.lesson_id, chapter.chapter_id)"
              class="lesson-item"
              :class="{ active: selectedLessonId === lesson.lesson_id }"
            >
              <span class="lesson-number">{{ lesson.order_index + 1 }}.</span>
              <span class="lesson-title">{{ lesson.title }}</span>
              <span
                v-if="lesson.lm_type"
                class="lm-badge"
                :class="{ active: selectedLessonId === lesson.lesson_id }"
              >
                {{ lesson.lm_type }}
              </span>
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- Quick Actions -->
    <div class="sidebar-actions">
      <button
        @click="$emit('create-chapter')"
        class="action-btn"
        :disabled="!course"
      >
        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        {{ $t('panel.aiStudio.newChapter') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * CourseStructureSidebar - Chapter tree navigation
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Course, Chapter } from '../composables/useAiStudioState'

const { t } = useI18n()

// =============================================================================
// Props
// =============================================================================

interface Props {
  course: Course | null
  chapters: Chapter[]
  selectedChapterId: string | null
  selectedLessonId: string | null
  expandedChapters: Set<string>
  isLoading?: boolean
}

const props = defineProps<Props>()

// =============================================================================
// Emits
// =============================================================================

const emit = defineEmits<{
  (e: 'select-chapter', chapterId: string): void
  (e: 'select-lesson', lessonId: string, chapterId: string): void
  (e: 'toggle-chapter', chapterId: string): void
  (e: 'create-chapter'): void
}>()

// =============================================================================
// State
// =============================================================================

const searchQuery = ref('')

// =============================================================================
// Computed
// =============================================================================

const filteredChapters = computed(() => {
  if (!searchQuery.value) return props.chapters

  const query = searchQuery.value.toLowerCase()

  return props.chapters.filter(chapter => {
    // Match chapter title
    if (chapter.title.toLowerCase().includes(query)) return true

    // Match any lesson title
    if (chapter.lessons?.some(lesson =>
      lesson.title.toLowerCase().includes(query)
    )) return true

    return false
  })
})

// =============================================================================
// Methods
// =============================================================================

function isExpanded(chapterId: string): boolean {
  return props.expandedChapters.has(chapterId)
}

function handleToggleChapter(chapterId: string): void {
  emit('toggle-chapter', chapterId)
  emit('select-chapter', chapterId)
}

function handleSelectLesson(lessonId: string, chapterId: string): void {
  emit('select-lesson', lessonId, chapterId)
}
</script>

<style scoped>
.course-structure-sidebar {
  display: flex;
  flex-direction: column;
  width: 16rem;
  flex-shrink: 0;
  border-right: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
  min-height: 0;
}

/* Search */
.sidebar-search {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.search-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.search-icon {
  position: absolute;
  left: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--color-text-tertiary);
}

/* Chapter Tree */
.chapter-tree {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.empty-state {
  padding: 1rem;
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
}

.loading-state {
  padding: 1rem;
  display: flex;
  justify-content: center;
}

.spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Chapter Block */
.chapter-block {
  margin-bottom: 0.25rem;
}

.chapter-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: none;
  border: none;
  border-radius: 0.5rem;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}

.chapter-header:hover {
  background: var(--color-surface);
}

.chapter-header.active {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.chapter-chevron {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  transition: transform 0.15s;
}

.chapter-chevron.expanded {
  transform: rotate(90deg);
}

.chapter-number {
  font-size: 0.75rem;
  font-family: monospace;
  color: var(--color-text-tertiary);
}

.chapter-title {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lesson-count {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

/* Lessons List */
.lessons-list {
  margin-left: 1rem;
  margin-top: 0.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.lesson-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: none;
  border: none;
  border-radius: 0.5rem;
  text-align: left;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.lesson-item:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.lesson-item.active {
  background: var(--color-primary);
  color: white;
}

.lesson-number {
  font-size: 0.75rem;
  font-family: monospace;
  opacity: 0.6;
}

.lesson-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lm-badge {
  padding: 0.125rem 0.375rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 500;
}

.lm-badge.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

/* Sidebar Actions */
.sidebar-actions {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.action-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.action-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  width: 1rem;
  height: 1rem;
}
</style>
