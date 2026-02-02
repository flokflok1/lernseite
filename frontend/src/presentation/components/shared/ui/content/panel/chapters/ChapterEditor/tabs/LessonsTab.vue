<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AdminLesson, DragState } from '../types'

interface Props {
  lessons: AdminLesson[]
  dragState: DragState
  isLoading: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'add-lesson': []
  'edit-lesson': [lesson: AdminLesson]
  'delete-lesson': [lessonId: string]
  'drag-start': [index: number]
  'drag-over': [index: number]
  'drop': [targetIndex: number]
  'drag-end': []
}>()

const { t } = useI18n()

// Computed
const isEmpty = computed(() => props.lessons.length === 0)

const lessonTypeIcons: Record<string, string> = {
  text: '📄',
  video: '🎥',
  quiz: '❓',
  interactive: '🎮',
  exercise: '💪',
  ai: '🤖',
  exam: '📝'
}

// Methods
const handleAddLesson = () => {
  emit('add-lesson')
}

const handleEditLesson = (lesson: AdminLesson) => {
  emit('edit-lesson', lesson)
}

const handleDeleteLesson = (lessonId: string) => {
  if (confirm(t('features.chapterEditor.lessons.deleteConfirm'))) {
    emit('delete-lesson', lessonId)
  }
}

const handleDragStart = (index: number) => {
  emit('drag-start', index)
}

const handleDragOver = (index: number, event: DragEvent) => {
  event.preventDefault()
  emit('drag-over', index)
}

const handleDrop = (targetIndex: number, event: DragEvent) => {
  event.preventDefault()
  emit('drop', targetIndex)
}

const handleDragEnd = () => {
  emit('drag-end')
}

const getLessonTypeLabel = (type: string): string => {
  const icon = lessonTypeIcons[type] || '📋'
  const label = t(`features.chapterEditor.lessonTypes.${type}`) || type
  return `${icon} ${label}`
}

const isDraggedOver = (index: number): boolean => {
  return props.dragState.targetIndex === index
}

const isDragging = (index: number): boolean => {
  return props.dragState.draggedIndex === index
}
</script>

<template>
  <div class="lessons-tab">
    <div class="lessons-header">
      <h3>{{ $t('features.chapterEditor.tabs.lessons') }}</h3>
      <button class="btn btn-primary btn-sm" @click="handleAddLesson">
        <span class="icon">➕</span>
        {{ $t('features.chapterEditor.buttons.addLesson') }}
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <span class="loader">⏳</span>
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="isEmpty" class="empty-state">
      <p>{{ $t('features.chapterEditor.empty.lessons') }}</p>
    </div>

    <div v-else class="lessons-list">
      <div
        v-for="(lesson, index) in lessons"
        :key="lesson.lesson_id"
        class="lesson-item"
        :class="{
          'is-dragging': isDragging(index),
          'is-drag-over': isDraggedOver(index)
        }"
        draggable="true"
        @dragstart="handleDragStart(index)"
        @dragover.prevent="handleDragOver(index, $event)"
        @drop="handleDrop(index, $event)"
        @dragend="handleDragEnd"
      >
        <div class="lesson-drag-handle">☰</div>

        <div class="lesson-number">{{ index + 1 }}</div>

        <div class="lesson-content">
          <h4 class="lesson-title">{{ lesson.title }}</h4>
          <p class="lesson-type">{{ getLessonTypeLabel(lesson.method_type) }}</p>
        </div>

        <div class="lesson-meta">
          <span v-if="lesson.published" class="badge badge-success">
            {{ $t('features.chapterEditor.status.published') }}
          </span>
          <span v-else class="badge badge-draft">
            {{ $t('features.chapterEditor.status.draft') }}
          </span>
        </div>

        <div class="lesson-actions">
          <button
            class="btn btn-secondary btn-sm"
            :title="$t('features.chapterEditor.buttons.editLesson')"
            @click="handleEditLesson(lesson)"
          >
            <span class="icon">✏️</span>
          </button>

          <button
            class="btn btn-danger btn-sm"
            :title="$t('features.chapterEditor.buttons.deleteLesson')"
            @click="handleDeleteLesson(lesson.lesson_id)"
          >
            <span class="icon">🗑️</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lessons-tab {
  padding: 1rem;
}

.lessons-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.lessons-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: var(--color-text-primary);
}

.lessons-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.lesson-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  background-color: white;
  cursor: grab;
  transition: all 0.2s;
}

.lesson-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  background-color: var(--color-bg-secondary);
}

.lesson-item.is-dragging {
  opacity: 0.5;
  background-color: var(--color-bg-secondary);
  cursor: grabbing;
}

.lesson-item.is-drag-over {
  border: 2px dashed var(--color-primary);
  background-color: var(--color-primary-light);
}

.lesson-drag-handle {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  cursor: grab;
  user-select: none;
  flex-shrink: 0;
}

.lesson-drag-handle:active {
  cursor: grabbing;
}

.lesson-number {
  min-width: 2rem;
  text-align: center;
  font-weight: 600;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.lesson-content {
  flex: 1;
  min-width: 0;
}

.lesson-title {
  margin: 0 0 0.25rem 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text-primary);
  word-break: break-word;
}

.lesson-type {
  margin: 0;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.lesson-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex-shrink: 0;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge-success {
  background-color: var(--color-success-bg);
  color: var(--color-success-text);
}

.badge-draft {
  background-color: var(--color-warning-bg);
  color: var(--color-warning-text);
}

.lesson-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn {
  padding: 0.35rem 0.5rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.btn-secondary {
  background-color: var(--color-primary);
  color: white;
}

.btn-secondary:hover {
  background-color: var(--color-primary-dark);
}

.btn-danger {
  background-color: var(--color-error);
  color: white;
}

.btn-danger:hover {
  background-color: var(--color-error-dark);
}

.btn-sm {
  padding: 0.35rem 0.5rem;
  font-size: 0.8rem;
}

.icon {
  font-size: 0.95rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

.empty-state p {
  margin: 0;
  font-size: 0.95rem;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.loader {
  font-size: 1.25rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
