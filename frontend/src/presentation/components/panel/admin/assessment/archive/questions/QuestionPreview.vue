<!--
  QuestionPreview - Read-only render of a question as a learner would see it.
-->

<template>
  <div class="space-y-4">
    <!-- Scenario box -->
    <div
      v-if="question.scenario_title"
      class="rounded-lg p-4"
      style="background-color: var(--color-info-bg, #eff6ff); border: 1px solid var(--color-info-border, #bfdbfe);"
    >
      <h4 class="font-semibold text-sm mb-1 text-[var(--color-info-text, #1e40af)]">
        {{ t('panel.examArchive.questionEditor.scenario') }}: {{ question.scenario_title }}
      </h4>
      <p
        v-if="(question as any).scenario_text"
        class="text-sm text-[var(--color-info-text, #1e40af)] opacity-90"
      >
        {{ (question as any).scenario_text }}
      </p>
    </div>

    <!-- Question text -->
    <div class="text-sm text-[var(--color-text-primary)] leading-relaxed">
      {{ question.question_text }}
    </div>

    <!-- Points badge -->
    <div class="flex items-center gap-2">
      <span
        class="px-2 py-0.5 rounded text-xs font-medium"
        style="background-color: var(--color-primary-bg, #ede9fe); color: var(--color-primary-text, #6d28d9);"
      >
        {{ question.points }} {{ t('panel.examArchive.questionEditor.fields.points') }}
      </span>
      <span
        v-if="question.question_type"
        class="px-2 py-0.5 rounded text-xs font-medium bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)]"
      >
        {{ t(`panel.examArchive.questionEditor.types.${question.question_type}`, question.question_type) }}
      </span>
    </div>

    <!-- Answer area (disabled, type-dependent) -->
    <div class="mt-3">
      <!-- MCQ options -->
      <div v-if="question.question_type === 'mcq' && options.length > 0" class="space-y-2">
        <label
          v-for="(option, idx) in options"
          :key="idx"
          class="flex items-center gap-2 p-2 rounded border border-[var(--color-border)] bg-[var(--color-surface)] cursor-not-allowed opacity-70"
        >
          <input type="radio" disabled class="accent-[var(--color-primary)]" />
          <span class="text-sm text-[var(--color-text-primary)]">{{ option }}</span>
        </label>
      </div>

      <!-- Calculation input -->
      <div v-else-if="question.question_type === 'calculation'">
        <input
          type="text"
          disabled
          :placeholder="t('panel.examArchive.questionEditor.fields.solution')"
          class="w-full px-3 py-2 text-sm rounded border border-[var(--color-border)] bg-[var(--color-surface-secondary)] text-[var(--color-text-tertiary)] cursor-not-allowed"
        />
      </div>

      <!-- Default: textarea -->
      <div v-else>
        <textarea
          disabled
          rows="3"
          :placeholder="t('panel.examArchive.questionEditor.fields.solution')"
          class="w-full px-3 py-2 text-sm rounded border border-[var(--color-border)] bg-[var(--color-surface-secondary)] text-[var(--color-text-tertiary)] resize-none cursor-not-allowed"
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ArchiveQuestion } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  question: ArchiveQuestion
}

const props = defineProps<Props>()

const { t } = useI18n()

const options = computed<string[]>(() => {
  const data = (props.question as any).data
  if (data && Array.isArray(data.options)) {
    return data.options
  }
  return []
})
</script>
