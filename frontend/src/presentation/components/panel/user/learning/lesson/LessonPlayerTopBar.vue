<!--
  LessonPlayerTopBar - Navigation bar for the lesson player

  Shows course/chapter info, progress indicator, and completion controls.
-->

<template>
  <div class="top-bar">
    <div class="top-bar-content">
      <div class="top-bar-left">
        <Button
          variant="outline"
          size="sm"
          @click="$emit('back')"
        >
          ← {{ $t('chapter.back_to_course') }}
        </Button>
        <div class="course-info">
          <h2 class="course-title">{{ courseTitle }}</h2>
          <p class="chapter-title">{{ chapterTitle }}</p>
        </div>
      </div>

      <div class="top-bar-right">
        <!-- Progress Indicator -->
        <div v-if="progressPercentage != null" class="progress-text">
          {{ $t('lesson.progress_completed', { progress: Math.round(progressPercentage) }) }}
        </div>
        <div v-else-if="isCompleted" class="progress-text">
          {{ $t('lesson.progress_completed', { progress: 100 }) }}
        </div>

        <!-- Complete Button -->
        <Button
          v-if="!isCompleted"
          variant="primary"
          size="sm"
          @click="$emit('complete')"
        >
          {{ $t('lesson.mark_completed') }}
        </Button>
        <span v-else class="completed-badge">
          {{ $t('lesson.completed') }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from '@/presentation/components/shared/ui/Button.vue'

interface Props {
  courseTitle: string
  chapterTitle: string
  progressPercentage: number | null
  isCompleted: boolean
}

defineProps<Props>()

defineEmits<{
  (e: 'back'): void
  (e: 'complete'): void
}>()
</script>

<style scoped>
.top-bar {
  background-color: var(--color-surface, #ffffff);
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  padding: 1rem 1.5rem;
}

.top-bar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.course-info {
  border-left: 1px solid var(--color-border, #e5e7eb);
  padding-left: 1rem;
}

.course-title {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  font-size: 1rem;
  margin: 0;
}

.chapter-title {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}

.completed-badge {
  font-size: 0.875rem;
  color: #10b981;
  font-weight: 500;
}
</style>
