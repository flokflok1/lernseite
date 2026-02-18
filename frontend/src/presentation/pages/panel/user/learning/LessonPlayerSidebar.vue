<!--
  LessonPlayerSidebar - Chapter navigation sidebar for lesson player

  Displays the list of lessons in the current chapter with active state highlighting.
-->

<template>
  <div class="sidebar-left">
    <div class="sidebar-content">
      <h3 class="sidebar-title">{{ $t('lesson.contents') }}</h3>

      <div v-if="lessons" class="lesson-list">
        <div
          v-for="(lesson, index) in lessons"
          :key="lesson.lesson_id"
          class="lesson-item"
          :class="{
            'lesson-item--active': lesson.lesson_id === activeLessonId,
            'lesson-item--inactive': lesson.lesson_id !== activeLessonId
          }"
          @click="$emit('navigate', lesson.lesson_id)"
        >
          <div class="lesson-item-content">
            <span class="lesson-number">{{ index + 1 }}</span>
            <div class="lesson-info">
              <p class="lesson-name">{{ lesson.title }}</p>
              <div class="lesson-meta">
                <span class="lesson-type-badge">
                  {{ lessonTypeLabel(lesson.lesson_type) }}
                </span>
                <span v-if="lesson.duration_minutes" class="lesson-duration">
                  {{ lesson.duration_minutes }} {{ $t('courses.minutes_short') }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface Lesson {
  lesson_id: number
  title: string
  lesson_type: string
  duration_minutes?: number
}

interface Props {
  lessons: Lesson[] | undefined
  activeLessonId: number | undefined
}

defineProps<Props>()

defineEmits<{
  (e: 'navigate', lessonId: number): void
}>()

const { t } = useI18n()

function lessonTypeLabel(type: string): string {
  const typeMap: Record<string, string> = {
    text: t('lesson.type_text'),
    video: t('lesson.type_video'),
    quiz: t('lesson.type_quiz'),
    ai: t('lesson.type_ai'),
    interactive: t('lesson.type_interactive'),
    mixed: t('lesson.type_mixed')
  }
  return typeMap[type] || type
}
</script>

<style scoped>
.sidebar-left {
  width: 16rem;
  background-color: var(--color-surface, #ffffff);
  border-right: 1px solid var(--color-border, #e5e7eb);
  overflow-y: auto;
}

.sidebar-content {
  padding: 1rem;
}

.sidebar-title {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 1rem;
  font-size: 1rem;
}

.lesson-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.lesson-item {
  cursor: pointer;
  border-radius: 0.5rem;
  padding: 0.75rem;
  transition: all 0.2s;
}

.lesson-item--active {
  background-color: var(--color-primary, #3b82f6);
  color: white;
}

.lesson-item--active .lesson-number,
.lesson-item--active .lesson-name,
.lesson-item--active .lesson-duration {
  color: white;
}

.lesson-item--active .lesson-type-badge {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.lesson-item--inactive:hover {
  background-color: var(--color-surface-secondary, #f9fafb);
}

.lesson-item-content {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.lesson-number {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #9ca3af);
  font-weight: 500;
  min-width: 1rem;
}

.lesson-info {
  flex: 1;
}

.lesson-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

.lesson-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.lesson-type-badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background-color: var(--color-surface-secondary, #f9fafb);
  color: var(--color-text-secondary, #6b7280);
  border-radius: 0.25rem;
}

.lesson-duration {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}
</style>
