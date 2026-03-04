<!--
  ExamSessionCard - A single exam session (e.g. "Sommer 2024")
  Shows ready/total count, tags, and expandable list of exam parts.
-->

<template>
  <div
    class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] hover:border-[var(--color-primary)] transition-colors"
  >
    <button
      class="w-full p-3 flex items-center justify-between text-left"
      @click="toggleExpanded"
    >
      <div class="flex items-center gap-3">
        <span class="text-sm font-medium text-[var(--color-text-primary)]">
          {{ seasonLabel }} {{ session.year }}
        </span>
        <span
          class="px-2 py-0.5 rounded text-xs font-medium"
          :class="session.ready_count === session.exam_count && session.exam_count > 0
            ? 'bg-[var(--color-success-bg,#dcfce7)] text-[var(--color-success-text,#15803d)]'
            : 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]'"
        >
          {{ t('panel.examArchive.session.examCount', {
            ready: session.ready_count,
            total: session.exam_count
          }) }}
        </span>
        <span
          v-if="session.total_questions > 0"
          class="text-xs text-[var(--color-text-secondary)]"
        >
          {{ t('panel.examArchive.session.totalQuestions', { count: session.total_questions }) }}
        </span>
      </div>

      <div class="flex items-center gap-2">
        <!-- Tags -->
        <span
          v-for="tag in session.tags"
          :key="tag"
          class="px-1.5 py-0.5 rounded text-xs bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary-text,#6d28d9)]"
        >
          {{ tag }}
        </span>
        <svg
          class="w-4 h-4 text-[var(--color-text-secondary)] transition-transform"
          :class="{ 'rotate-180': expanded }"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </button>

    <!-- Expanded: individual exam parts -->
    <div v-if="expanded" class="border-t border-[var(--color-border)] p-3 space-y-2">
      <div v-if="loading" class="flex justify-center py-3">
        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-[var(--color-primary)]" />
      </div>
      <template v-else>
        <div
          v-for="exam in exams"
          :key="exam.exam_id"
          class="flex items-center justify-between p-2 rounded bg-[var(--color-bg)] border border-[var(--color-border)]"
        >
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium text-[var(--color-text-primary)]">
              {{ exam.part || exam.title }}
            </span>
            <span
              class="px-1.5 py-0.5 rounded text-xs font-medium"
              :class="statusClass(exam.analysis_status)"
            >
              {{ t(`panel.examArchive.status.${exam.analysis_status}`) }}
            </span>
          </div>
          <span class="text-xs text-[var(--color-text-secondary)]">
            {{ t('panel.examArchive.questions', { count: exam.question_count }) }}
          </span>
        </div>
        <p
          v-if="exams.length === 0"
          class="text-sm text-[var(--color-text-secondary)] text-center py-2"
        >
          {{ t('panel.examArchive.noExams') }}
        </p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ExamSession, ArchiveExam } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import { archiveSessionExams } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  session: ExamSession
}

const props = defineProps<Props>()
const { t } = useI18n()

const expanded = ref(false)
const loading = ref(false)
const exams = ref<ArchiveExam[]>([])

const seasonLabel = computed(() =>
  t(`panel.examArchive.session.season.${props.session.season}`)
)

const statusClass = (status: string) => {
  const map: Record<string, string> = {
    ready: 'bg-[var(--color-success-bg,#dcfce7)] text-[var(--color-success-text,#15803d)]',
    pending: 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]',
    analyzing: 'bg-[var(--color-info-bg,#eff6ff)] text-[var(--color-info-text,#1e40af)]',
    failed: 'bg-[var(--color-error-bg,#fee2e2)] text-[var(--color-error-text,#dc2626)]',
  }
  return map[status] || map.pending
}

const toggleExpanded = async () => {
  if (expanded.value) {
    expanded.value = false
    return
  }
  if (exams.value.length === 0) {
    loading.value = true
    try {
      exams.value = await archiveSessionExams(props.session.session_id)
    } catch (err) {
      console.error('Failed to load session exams:', err)
    } finally {
      loading.value = false
    }
  }
  expanded.value = true
}
</script>
