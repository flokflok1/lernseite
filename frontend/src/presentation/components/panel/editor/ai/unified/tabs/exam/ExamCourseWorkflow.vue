<!--
  ExamCourseWorkflow — Course preview + generation within the AI Editor exam tab.
  Compact version of ExamCourseGenerator, integrated into the unified editor.
-->
<template>
  <div class="space-y-4">
    <!-- Section Header -->
    <div>
      <h3 class="text-sm font-semibold text-[var(--color-text-primary)]">
        {{ t('aiEditor.exam.courseSection') }}
      </h3>
      <p class="text-xs text-[var(--color-text-secondary)] mt-0.5">
        {{ t('aiEditor.exam.courseDescription') }}
      </p>
    </div>

    <!-- Actions -->
    <div class="flex items-center gap-2">
      <button
        @click="$emit('preview')"
        :disabled="previewing"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white rounded-md transition-colors disabled:opacity-50"
        style="background-color: var(--color-primary, #7c3aed);"
      >
        {{ previewing ? '...' : t('panel.examCourseGenerator.preview') }}
      </button>
      <button
        v-if="plan"
        @click="$emit('generate')"
        :disabled="generating"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white rounded-md transition-colors disabled:opacity-50"
        style="background-color: var(--color-success-text, #16a34a);"
      >
        {{ generating ? t('panel.examCourseGenerator.generating') : t('aiEditor.exam.generateCourse') }}
      </button>
    </div>

    <!-- Plan Preview -->
    <div v-if="plan" class="space-y-2">
      <div class="flex items-center gap-3 text-xs text-[var(--color-text-secondary)]">
        <span>{{ plan.total_questions }} {{ t('panel.examCourseGenerator.questions') }}</span>
        <span>{{ plan.chapters.length }} {{ t('panel.examCourseGenerator.chapters') }}</span>
        <span>{{ Math.round(plan.total_points) }} {{ t('panel.examCourseGenerator.points') }}</span>
      </div>

      <div class="space-y-1.5 max-h-64 overflow-y-auto">
        <div
          v-for="(ch, idx) in plan.chapters"
          :key="ch.topic"
          class="flex items-center justify-between rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2"
        >
          <div class="flex items-center gap-2 min-w-0">
            <span class="text-[10px] font-mono text-[var(--color-text-tertiary)] w-5 text-right flex-shrink-0">
              {{ idx + 1 }}
            </span>
            <span class="text-xs font-medium text-[var(--color-text-primary)] truncate">
              {{ ch.parent_label?.de || ch.topic }}
            </span>
          </div>
          <div class="flex items-center gap-2 text-[10px] text-[var(--color-text-tertiary)] flex-shrink-0">
            <span>{{ ch.question_count }}q</span>
            <span>{{ Math.round(ch.point_weight) }}p</span>
            <span
              v-if="ch.is_gap"
              class="px-1 py-0.5 rounded bg-amber-100 text-amber-700 text-[9px] font-medium"
            >
              {{ t('panel.examCourseGenerator.aiOnly') }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Generation Progress -->
    <div
      v-if="progress"
      class="rounded-md border p-3"
      :class="progressBorderClass"
    >
      <div class="flex items-center justify-between mb-1.5">
        <span class="text-xs font-medium text-[var(--color-text-primary)]">
          {{ t('panel.examCourseGenerator.generatingProgress') }}
        </span>
        <span class="text-[10px] text-[var(--color-text-secondary)]">
          {{ progress.completed }}/{{ progress.total }}
        </span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-1.5">
        <div
          class="h-1.5 rounded-full transition-all duration-500"
          :class="progressBarClass"
          :style="{ width: progressPercent + '%' }"
        />
      </div>
      <p v-if="progress.status === 'ready'" class="mt-1.5 text-green-600 text-[10px]">
        {{ t('panel.examCourseGenerator.generationComplete') }}
      </p>
    </div>

    <!-- Result -->
    <div
      v-if="result && !generating"
      class="rounded-md border p-3"
      style="background: var(--color-success-bg, #dcfce7); border-color: var(--color-success-text, #15803d);"
    >
      <p class="text-xs font-medium" style="color: var(--color-success-text, #15803d);">
        {{ t('panel.examCourseGenerator.success') }}
      </p>
      <p class="text-[10px] mt-1" style="color: var(--color-success-text, #15803d);">
        {{ result.chapters_count }} {{ t('panel.examCourseGenerator.chapters') }},
        {{ result.lm_count }} {{ t('panel.examCourseGenerator.lmCount') }}
      </p>
      <a
        :href="`/panel/courses/${result.course_id}`"
        class="inline-block mt-1.5 text-[10px] underline text-[var(--color-primary)]"
      >
        {{ t('panel.examCourseGenerator.openInEditor') }}
      </a>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="rounded-md px-3 py-2 text-xs border"
      style="background: var(--color-error-bg, #fee2e2); border-color: var(--color-error-text, #dc2626); color: var(--color-error-text, #dc2626);"
    >
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CoursePlan, GenerateResult, GenerationProgress } from '@/infrastructure/api/clients/panel/admin/exams/course-generator.api'

const { t } = useI18n()

const props = defineProps<{
  plan: CoursePlan | null
  result: GenerateResult | null
  progress: GenerationProgress | null
  progressPercent: number
  previewing: boolean
  generating: boolean
  error: string | null
}>()

defineEmits<{
  preview: []
  generate: []
}>()

const progressBorderClass = computed(() => {
  const s = props.progress?.status
  if (s === 'ready') return 'bg-green-50 border-green-200'
  if (s === 'failed') return 'bg-red-50 border-red-200'
  return 'bg-blue-50 border-blue-200'
})

const progressBarClass = computed(() => {
  const s = props.progress?.status
  if (s === 'ready') return 'bg-green-600'
  if (s === 'failed') return 'bg-red-600'
  return 'bg-blue-600'
})
</script>
