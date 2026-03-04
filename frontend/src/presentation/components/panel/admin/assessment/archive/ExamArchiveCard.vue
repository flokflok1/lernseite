<!--
  ExamArchiveCard - Displays a single archive exam with status and expandable questions.
-->

<template>
  <div
    class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] hover:border-[var(--color-primary)] transition-colors"
  >
    <!-- Header -->
    <div class="p-4">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-2">
            <h3 class="font-semibold text-[var(--color-text-primary)]">
              {{ exam.title }}
            </h3>
            <!-- Status Badge -->
            <span
              class="px-2 py-0.5 rounded text-xs font-medium"
              :style="statusStyle"
            >
              {{ t(`panel.examArchive.status.${exam.analysis_status}`) }}
            </span>
          </div>

          <div class="flex flex-wrap gap-4 text-xs text-[var(--color-text-secondary)]">
            <span>{{ t('panel.examArchive.semester') }}: {{ exam.season }} {{ exam.year }}</span>
            <span>{{ t('panel.examArchive.part') }}: {{ exam.part }}</span>
            <span v-if="exam.analysis_status === 'ready'">
              {{ t('panel.examArchive.questions', { count: exam.question_count }) }}
            </span>
            <span v-else>
              {{ t('panel.examArchive.noQuestions') }}
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2 ml-4">
          <button
            v-if="exam.analysis_status === 'pending'"
            @click="$emit('analyze', exam.exam_id)"
            class="px-3 py-1.5 text-white rounded text-xs transition-colors"
            style="background-color: var(--color-primary, #7c3aed);"
          >
            {{ t('panel.examArchive.analyze') }}
          </button>
          <button
            v-if="exam.analysis_status === 'ready' && exam.question_count > 0"
            @click="toggleQuestions"
            class="px-3 py-1.5 border border-[var(--color-border)] rounded text-xs text-[var(--color-text-primary)] transition-colors hover:bg-[var(--color-surface-secondary)]"
          >
            {{ expanded ? t('panel.examArchive.hideQuestions') : t('panel.examArchive.showQuestions') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Questions List (expandable) -->
    <div
      v-if="expanded && questions.length > 0"
      class="border-t border-[var(--color-border)] p-4"
    >
      <div
        v-if="loadingQuestions"
        class="flex items-center justify-center py-4"
      >
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-[var(--color-primary)]"></div>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="question in questions"
          :key="question.question_id"
          class="p-3 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)]"
        >
          <div class="flex items-start justify-between mb-1">
            <span class="text-sm font-medium text-[var(--color-text-primary)]">
              {{ question.question_number }}
            </span>
            <span class="text-xs text-[var(--color-text-secondary)]">
              {{ t('panel.examArchive.points', { count: question.points }) }}
            </span>
          </div>
          <p class="text-sm text-[var(--color-text-secondary)] mb-2">
            {{ question.question_text }}
          </p>
          <div v-if="question.topics.length > 0" class="flex flex-wrap gap-1">
            <span class="text-xs text-[var(--color-text-secondary)]">
              {{ t('panel.examArchive.topics') }}:
            </span>
            <span
              v-for="topic in question.topics"
              :key="topic"
              class="px-1.5 py-0.5 rounded text-xs"
              style="background-color: var(--color-primary-bg, #ede9fe); color: var(--color-primary-text, #6d28d9);"
            >
              {{ topic }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ArchiveExam, ArchiveQuestion } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import { archiveGetQuestions } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  exam: ArchiveExam
}

const props = defineProps<Props>()

defineEmits<{
  analyze: [examId: string]
}>()

const { t } = useI18n()

const expanded = ref(false)
const questions = ref<ArchiveQuestion[]>([])
const loadingQuestions = ref(false)

const statusStyle = computed(() => {
  const styles: Record<string, { bg: string; color: string }> = {
    pending: { bg: 'var(--color-warning-bg, #fef3c7)', color: 'var(--color-warning-text, #92400e)' },
    analyzing: { bg: 'var(--color-info-bg, #eff6ff)', color: 'var(--color-info-text, #1e40af)' },
    ready: { bg: 'var(--color-success-bg, #dcfce7)', color: 'var(--color-success-text, #15803d)' },
    failed: { bg: 'var(--color-error-bg, #fee2e2)', color: 'var(--color-error-text, #dc2626)' }
  }
  const s = styles[props.exam.analysis_status] || styles.pending
  return { backgroundColor: s.bg, color: s.color }
})

const toggleQuestions = async () => {
  if (expanded.value) {
    expanded.value = false
    return
  }

  if (questions.value.length === 0) {
    loadingQuestions.value = true
    try {
      questions.value = await archiveGetQuestions(props.exam.exam_id)
    } catch (err) {
      console.error('Failed to load questions:', err)
    } finally {
      loadingQuestions.value = false
    }
  }

  expanded.value = true
}
</script>
