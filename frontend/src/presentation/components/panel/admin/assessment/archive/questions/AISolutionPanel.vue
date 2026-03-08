<!--
  AISolutionPanel - Generates and displays an AI-suggested solution for a question.
-->

<template>
  <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 space-y-4">
    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center gap-3 py-6">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]"></div>
      <span class="text-sm text-[var(--color-text-secondary)]">
        {{ t('panel.examArchive.questionEditor.aiSolutionLoading') }}
      </span>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-sm text-[var(--color-error-text, #dc2626)]">
      {{ error }}
    </div>

    <!-- Result -->
    <template v-else-if="result">
      <div
        class="rounded p-3 text-sm whitespace-pre-wrap leading-relaxed text-[var(--color-text-primary)]"
        style="background-color: var(--color-info-bg, #eff6ff);"
      >
        {{ result.suggested_solution }}
      </div>

      <div class="text-xs text-[var(--color-text-tertiary)]">
        {{ t('panel.examArchive.questionEditor.tokensUsed', { count: result.tokens_used }) }}
      </div>

      <div class="flex gap-2 justify-end">
        <button
          type="button"
          class="px-3 py-1.5 text-sm rounded border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors"
          @click="emit('close')"
        >
          {{ t('panel.examArchive.questionEditor.close') }}
        </button>
        <button
          type="button"
          class="px-3 py-1.5 text-sm rounded text-white transition-colors"
          style="background-color: var(--color-primary, #7c3aed);"
          @click="emit('apply', result.suggested_solution)"
        >
          {{ t('panel.examArchive.questionEditor.aiSolutionApply') }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AISolutionResult } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import { archiveAISolution } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  questionId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  apply: [solution: string]
  close: []
}>()

const { t } = useI18n()

const loading = ref(true)
const error = ref('')
const result = ref<AISolutionResult | null>(null)

onMounted(async () => {
  try {
    result.value = await archiveAISolution(props.questionId)
  } catch (err: any) {
    error.value = err?.message || 'Failed to generate AI solution'
  } finally {
    loading.value = false
  }
})
</script>
