<!--
  ExamCard - Displays a single exam with metadata and actions.
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)] hover:border-[var(--color-primary)] transition-colors">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-2">
          <h3 class="font-semibold text-[var(--color-text-primary)]">{{ exam.title }}</h3>
          <span
            v-if="exam.generated_by_ai"
            class="px-2 py-0.5 rounded text-xs"
            style="background-color: var(--color-primary-bg, #ede9fe); color: var(--color-primary-text, #6d28d9);"
          >
            {{ $t('examManager.aiGenerated') }}
          </span>
          <span
            v-if="exam.published"
            class="px-2 py-0.5 rounded text-xs"
            style="background-color: var(--color-success-bg, #dcfce7); color: var(--color-success-text, #15803d);"
          >
            {{ $t('examManager.published') }}
          </span>
          <span
            v-else
            class="px-2 py-0.5 rounded text-xs"
            style="background-color: var(--color-warning-bg, #fef3c7); color: var(--color-warning-text, #92400e);"
          >
            {{ $t('examManager.draft') }}
          </span>
        </div>

        <p v-if="exam.description" class="text-sm text-[var(--color-text-secondary)] mb-3">
          {{ exam.description }}
        </p>

        <div class="flex flex-wrap gap-4 text-xs text-[var(--color-text-secondary)]">
          <div class="flex items-center gap-1">
            <span>{{ $t('examManager.questions', { count: exam.question_count }) }}</span>
          </div>
          <div class="flex items-center gap-1">
            <span>{{ $t('examManager.duration', { minutes: exam.duration_minutes }) }}</span>
          </div>
          <div class="flex items-center gap-1">
            <span>{{ $t('examManager.passingScore', { score: exam.passing_score }) }}</span>
          </div>
          <div class="flex items-center gap-1">
            <span>{{ $t('examManager.points', { count: exam.total_points }) }}</span>
          </div>
        </div>
      </div>

      <div class="flex gap-1 ml-4">
        <button
          @click="$emit('delete', exam)"
          class="px-2 py-1 text-xs rounded transition-colors"
          style="color: var(--color-error, #dc2626);"
          :title="$t('examManager.delete')"
        >
          {{ $t('examManager.deleteIcon') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Exam } from '@/application/services/api/panel-admin'

interface Props {
  exam: Exam
}

defineProps<Props>()

defineEmits<{
  delete: [exam: Exam]
}>()
</script>
