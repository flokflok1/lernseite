<!--
  TutorSubNavigation - Horizontal chapter/lesson navigation for Tutor tab

  Displays chapters as horizontal tabs and allows chapter/lesson selection.
  Only shown when in the KI-Tutor tab to maximize content space.
-->

<template>
  <div class="tutor-sub-navigation">
    <!-- Chapters Container (horizontal scroll) -->
    <div class="chapters-container">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner-small"></div>
      </div>

      <!-- No Course Message -->
      <div v-else-if="!selectedChapterId && chapters.length === 0" class="empty-message">
        {{ $t('admin.aiEditor.selectCourseToView') }}
      </div>

      <!-- Chapters List -->
      <template v-else>
        <button
          v-for="chapter in chapters"
          :key="chapter.chapter_id"
          @click="selectChapter(chapter.chapter_id)"
          class="chapter-tab"
          :class="{ active: chapter.chapter_id === selectedChapterId }"
        >
          <span class="chapter-label">
            {{ chapter.order_index + 1 }}. {{ chapter.title }}
          </span>
          <span class="lesson-count">{{ chapter.lessons?.length || 0 }}</span>
        </button>

        <!-- Add Chapter Button -->
        <button
          @click="$emit('create-chapter')"
          class="add-chapter-btn"
          :title="$t('admin.aiEditor.newChapter')"
        >
          <svg class="plus-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>{{ $t('admin.aiEditor.newChapter') }}</span>
        </button>
      </template>
    </div>

    <!-- Lessons Sub-Tabs (shown for selected chapter) -->
    <div v-if="selectedChapter && selectedChapter.lessons && selectedChapter.lessons.length > 0" class="lessons-container">
      <button
        v-for="lesson in selectedChapter.lessons"
        :key="lesson.lesson_id"
        @click="selectLesson(lesson.lesson_id)"
        class="lesson-tab"
        :class="{ active: lesson.lesson_id === selectedLessonId }"
      >
        <span class="lesson-label">{{ lesson.order_index + 1 }}. {{ lesson.title }}</span>
        <span v-if="lesson.lm_type" class="lm-badge">{{ lesson.lm_type }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * TutorSubNavigation - Horizontal chapter and lesson navigation for KI-Tutor tab
 *
 * Displays chapters as horizontal tabs with lesson sub-tabs.
 * Optimizes screen space by replacing the sidebar when in Tutor mode.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Chapter, Lesson } from '../composables/useAiStudioState'

const { t } = useI18n()

// =============================================================================
// Props
// =============================================================================

interface Props {
  chapters: Chapter[]
  selectedChapterId: string | null
  selectedLessonId: string | null
  isLoading: boolean
}

const props = defineProps<Props>()

// =============================================================================
// Emits
// =============================================================================

const emit = defineEmits<{
  (e: 'select-chapter', chapterId: string): void
  (e: 'select-lesson', lessonId: string): void
  (e: 'create-chapter'): void
}>()

// =============================================================================
// Computed
// =============================================================================

const selectedChapter = computed(() => {
  return props.chapters.find(c => c.chapter_id === props.selectedChapterId)
})

// =============================================================================
// Methods
// =============================================================================

function selectChapter(chapterId: string): void {
  emit('select-chapter', chapterId)
}

function selectLesson(lessonId: string): void {
  emit('select-lesson', lessonId)
}
</script>

<style scoped>
.tutor-sub-navigation {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  max-height: auto;
  overflow: hidden;
}

/* Chapters Container */
.chapters-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  overflow-x: auto;
  overflow-y: hidden;
  border-bottom: 1px solid var(--color-border);
  scroll-behavior: smooth;
}

.chapters-container::-webkit-scrollbar {
  height: 4px;
}

.chapters-container::-webkit-scrollbar-track {
  background: transparent;
}

.chapters-container::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 2px;
}

.chapters-container::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}

/* Loading State */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  min-width: 200px;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty Message */
.empty-message {
  padding: 0.75rem 1rem;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  white-space: nowrap;
}

/* Chapter Tab */
.chapter-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.chapter-tab:hover {
  background: var(--color-surface-tertiary);
  border-color: var(--color-text-secondary);
}

.chapter-tab.active {
  background: linear-gradient(135deg, #7c3aed, #9f1239);
  color: white;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.3);
}

.chapter-label {
  font-weight: 600;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lesson-count {
  font-size: 0.75rem;
  opacity: 0.7;
  font-weight: 600;
  background: var(--color-surface);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.chapter-tab.active .lesson-count {
  background: rgba(255, 255, 255, 0.2);
}

/* Add Chapter Button */
.add-chapter-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: 1px dashed var(--color-primary);
  border-radius: 0.5rem;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.add-chapter-btn:hover {
  background: var(--color-primary-faded);
  border-color: var(--color-primary);
}

.plus-icon {
  width: 1rem;
  height: 1rem;
}

/* Lessons Container */
.lessons-container {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  overflow-x: auto;
  overflow-y: hidden;
  background: var(--color-surface-secondary);
  scroll-behavior: smooth;
}

.lessons-container::-webkit-scrollbar {
  height: 4px;
}

.lessons-container::-webkit-scrollbar-track {
  background: transparent;
}

.lessons-container::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 2px;
}

/* Lesson Tab */
.lesson-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.lesson-tab:hover {
  background: var(--color-surface-secondary);
  border-color: var(--color-text-secondary);
}

.lesson-tab.active {
  background: var(--color-secondary);
  color: white;
  border-color: var(--color-secondary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.lesson-label {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lm-badge {
  font-size: 0.625rem;
  background: var(--color-primary);
  color: white;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-weight: 700;
}

.lesson-tab.active .lm-badge {
  background: rgba(255, 255, 255, 0.3);
}
</style>
