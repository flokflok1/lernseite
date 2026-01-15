<!--
  TutorTab - ADHS-freundliche Lernerklärungen

  Main container that delegates to:
  - ChapterTheoryView: For chapter theory generation
  - LessonExplanationView: For step-by-step lesson explanations
-->

<template>
  <div class="tutor-tab">
    <!-- No Content Selected -->
    <div v-if="!chapter && !lesson" class="empty-state">
      <div class="empty-icon">👨‍🏫</div>
      <h3>{{ $t('windows.aiEditorTutor.selectContent') }}</h3>
      <p v-html="$t('windows.aiEditorTutor.selectContentHint')"></p>
    </div>

    <!-- Chapter View: Theory Generation -->
    <ChapterTheoryView
      v-else-if="chapter && !lesson"
      :course="course"
      :chapter="chapter"
      @generated="onTheoryGenerated"
      @deleted="onTheoryDeleted"
    />

    <!-- Lesson View: Step-by-Step Explanation -->
    <LessonExplanationView
      v-else-if="lesson"
      :course="course"
      :lesson="lesson"
      @generated="onExplanationGenerated"
      @deleted="onExplanationDeleted"
    />
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import { ChapterTheoryView } from '@/components/studio/system-features/tutor/admin/chapter-theory'
import { LessonExplanationView } from '@/components/studio/system-features/tutor/admin/lesson-explanation'

// ============================================================================
// Props
// ============================================================================

interface Course {
  course_id: string
  title: string
}

interface Chapter {
  chapter_id: string
  title: string
}

interface Lesson {
  lesson_id: string
  title: string
}

const props = defineProps<{
  course: Course | null
  chapter: Chapter | null
  lesson: Lesson | null
}>()

// ============================================================================
// Emits
// ============================================================================

const emit = defineEmits<{
  (e: 'content-generated', type: 'theory' | 'explanation', id: string): void
  (e: 'content-deleted', type: 'theory' | 'explanation', id: string): void
}>()

// ============================================================================
// Event Handlers
// ============================================================================

function onTheoryGenerated(theoryId: string) {
  emit('content-generated', 'theory', theoryId)
}

function onTheoryDeleted(theoryId: string) {
  emit('content-deleted', 'theory', theoryId)
}

function onExplanationGenerated(explanationId: string) {
  emit('content-generated', 'explanation', explanationId)
}

function onExplanationDeleted(explanationId: string) {
  emit('content-deleted', 'explanation', explanationId)
}
</script>

<style scoped>
.tutor-tab {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
  color: var(--color-text-primary);
}

.empty-state p {
  margin: 0;
  max-width: 400px;
  line-height: 1.6;
}

.empty-state strong {
  color: var(--color-primary);
}
</style>
