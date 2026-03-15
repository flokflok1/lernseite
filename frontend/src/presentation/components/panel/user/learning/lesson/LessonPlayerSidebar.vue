<!--
  LessonPlayerSidebar - Chapter navigation sidebar for lesson player

  Displays the list of lessons in the current chapter with progress dots
  and active state highlighting via left border accent.
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
            'lesson-item--completed': isCompleted(lesson),
            'lesson-item--inactive': lesson.lesson_id !== activeLessonId && !isCompleted(lesson)
          }"
          @click="$emit('navigate', lesson.lesson_id)"
        >
          <!-- Progress dot -->
          <div class="lesson-dot" :class="dotClass(lesson)"></div>

          <div class="lesson-info">
            <p class="lesson-name">{{ lesson.title }}</p>
            <div class="lesson-meta">
              <span class="lesson-type-badge">
                {{ lessonTypeLabel(lesson.lesson_type, lesson.title) }}
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
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface Lesson {
  lesson_id: number
  title: string
  lesson_type: string
  duration_minutes?: number
  completed?: boolean
}

interface Props {
  lessons: Lesson[] | undefined
  activeLessonId: number | undefined
  completedLessonIds?: number[]
}

const props = withDefaults(defineProps<Props>(), {
  completedLessonIds: () => []
})

defineEmits<{
  (e: 'navigate', lessonId: number): void
}>()

const { t } = useI18n()

function isCompleted(lesson: Lesson): boolean {
  return lesson.completed === true || props.completedLessonIds.includes(lesson.lesson_id)
}

function dotClass(lesson: Lesson): string {
  if (lesson.lesson_id === props.activeLessonId) return 'dot--current'
  if (isCompleted(lesson)) return 'dot--completed'
  return 'dot--pending'
}

// Category detection via shared composable (single source of truth)
import { detectCategory } from '@/application/composables/panel/user/learning/usePageCategory'

function lessonTypeLabel(type: string, title?: string): string {
  if (type === 'text' && title) {
    const detected = detectCategory(title)
    if (detected) {
      const labelKey = {
        theory: 'lessonTimeline.categoryTheory',
        practice: 'lessonTimeline.categoryPractice',
        assessment: 'lessonTimeline.categoryAssessment',
      }[detected.category]
      return `${detected.icon} ${t(labelKey)}`
    }
  }
  const typeMap: Record<string, string> = {
    text: t('lesson.type_text'),
    video: t('lesson.type_video'),
    quiz: t('lesson.type_quiz'),
    ai: t('lesson.type_ai'),
    interactive: t('lesson.type_interactive'),
    mixed: t('lesson.type_mixed'),
  }
  return typeMap[type] || type
}
</script>

<style scoped>
.sidebar-left {
  width: 14rem;
  background-color: var(--color-surface, #ffffff);
  border-right: 1px solid var(--color-border, #e5e7eb);
  overflow-y: auto;
}

:root.dark .sidebar-left {
  background-color: #111827;
}

.sidebar-content {
  padding: 0.625rem;
}

.sidebar-title {
  font-weight: 700;
  color: var(--color-text-secondary, #6b7280);
  margin: 0 0 0.5rem;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.lesson-list {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.lesson-item {
  cursor: pointer;
  border-radius: 0.375rem;
  padding: 0.375rem 0.5rem;
  transition: all 0.2s;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  border-left: 3px solid transparent;
}

.lesson-item--active {
  border-left-color: var(--color-primary, #3b82f6);
  background-color: rgba(59, 130, 246, 0.08);
}

:root.dark .lesson-item--active {
  background-color: rgba(59, 130, 246, 0.15);
}

.lesson-item--completed {
  opacity: 0.75;
}

.lesson-item--inactive:hover {
  background-color: var(--color-surface-secondary, #f9fafb);
}

:root.dark .lesson-item--inactive:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

/* Progress dots */
.lesson-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 0.3125rem;
  transition: all 0.2s;
}

.dot--current {
  background-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.dot--completed {
  background-color: #10b981;
}

.dot--pending {
  background-color: var(--color-border, #d1d5db);
}

:root.dark .dot--pending {
  background-color: #4b5563;
}

.lesson-info {
  flex: 1;
  min-width: 0;
}

.lesson-name {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-primary, #111827);
  margin: 0;
  line-height: 1.3;
}

.lesson-item--active .lesson-name {
  color: var(--color-primary, #3b82f6);
  font-weight: 600;
}

.lesson-meta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-top: 0.125rem;
}

.lesson-type-badge {
  font-size: 0.5625rem;
  padding: 0.0625rem 0.3125rem;
  background-color: var(--color-surface-secondary, #f3f4f6);
  color: var(--color-text-secondary, #6b7280);
  border-radius: 0.1875rem;
}

:root.dark .lesson-type-badge {
  background-color: rgba(255, 255, 255, 0.08);
}

.lesson-duration {
  font-size: 0.625rem;
  color: var(--color-text-secondary, #9ca3af);
}
</style>
