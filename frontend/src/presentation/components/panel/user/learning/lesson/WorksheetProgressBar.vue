<!--
  WorksheetProgressBar — Clickable lesson progress dots.
  Shows each lesson as a dot: completed (green), current (blue pulse), available (gray).
-->
<template>
  <nav class="progress-bar" :aria-label="$t('lesson.contents')">
    <button
      v-for="(lesson, idx) in lessons"
      :key="lesson.lesson_id"
      class="progress-step"
      :class="stepClass(lesson)"
      :title="lesson.title"
      :aria-label="`${idx + 1}. ${lesson.title}`"
      :aria-current="lesson.lesson_id === activeLessonId ? 'step' : undefined"
      @click="$emit('navigate', lesson.lesson_id)"
    >
      <span class="step-dot" />
      <span class="step-number">{{ idx + 1 }}</span>
    </button>

    <!-- Connecting lines between dots -->
    <div class="progress-track">
      <div
        class="progress-fill"
        :style="{ width: fillWidth }"
      />
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Lesson {
  lesson_id: number
  title: string
  completed?: boolean
}

interface Props {
  lessons: Lesson[]
  activeLessonId: number | undefined
  completedLessonIds?: number[]
}

const props = withDefaults(defineProps<Props>(), {
  completedLessonIds: () => [],
})

defineEmits<{
  navigate: [lessonId: number]
}>()

function isCompleted(lesson: Lesson): boolean {
  return lesson.completed === true || props.completedLessonIds.includes(lesson.lesson_id)
}

function stepClass(lesson: Lesson): string {
  if (lesson.lesson_id === props.activeLessonId) return 'step--current'
  if (isCompleted(lesson)) return 'step--completed'
  return 'step--pending'
}

const fillWidth = computed(() => {
  if (!props.lessons.length) return '0%'
  const activeIdx = props.lessons.findIndex(l => l.lesson_id === props.activeLessonId)
  if (activeIdx <= 0) return '0%'
  return `${(activeIdx / (props.lessons.length - 1)) * 100}%`
})
</script>

<style scoped>
.progress-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 0.75rem 1rem;
  position: relative;
}

/* Track line behind dots */
.progress-track {
  position: absolute;
  left: 2rem;
  right: 2rem;
  top: 50%;
  height: 2px;
  background: var(--color-border, #e5e7eb);
  border-radius: 1px;
  z-index: 0;
  pointer-events: none;
}

:root.dark .progress-track {
  background: #374151;
}

.progress-fill {
  height: 100%;
  background: #10b981;
  border-radius: 1px;
  transition: width 0.4s ease;
}

/* Step button */
.progress-step {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  transition: transform 0.15s;
}

.progress-step:hover {
  transform: scale(1.15);
}

.step-dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.step-number {
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--color-text-secondary, #9ca3af);
  transition: color 0.2s;
}

/* States */
.step--completed .step-dot {
  background: #10b981;
  border-color: #10b981;
}

.step--completed .step-number {
  color: #10b981;
}

.step--current .step-dot {
  background: #3b82f6;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
  animation: pulse 2s ease-in-out infinite;
}

.step--current .step-number {
  color: #3b82f6;
  font-weight: 700;
}

.step--pending .step-dot {
  background: var(--color-surface, #fff);
  border-color: var(--color-border, #d1d5db);
}

:root.dark .step--pending .step-dot {
  background: #1f2937;
  border-color: #4b5563;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2); }
  50%      { box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.1); }
}

/* Print: hide interactive elements */
@media print {
  .progress-bar { display: none; }
}
</style>
