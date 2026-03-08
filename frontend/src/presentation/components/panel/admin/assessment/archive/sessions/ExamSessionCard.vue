<!--
  ExamSessionCard - A single exam session (e.g. "Sommer 2024")
  Shows ready/total count, tags, and expandable list of exam parts.
-->

<template>
  <div
    class="bg-[var(--color-surface)] rounded-xl border transition-all duration-200 hover:shadow-md"
    :class="session.ready_count === session.exam_count && session.exam_count > 0
      ? 'border-l-4 border-l-[var(--color-success-text,#16a34a)] border-t-[var(--color-border)] border-r-[var(--color-border)] border-b-[var(--color-border)]'
      : 'border-l-4 border-l-[var(--color-warning-text,#d97706)] border-t-[var(--color-border)] border-r-[var(--color-border)] border-b-[var(--color-border)]'"
  >
    <button
      class="w-full px-4 py-3.5 flex items-center justify-between text-left"
      @click="toggleExpanded"
    >
      <div class="flex items-center gap-4">
        <!-- Season + Year -->
        <div class="flex items-baseline gap-1.5">
          <span class="text-base font-bold text-[var(--color-text-primary)]">
            {{ seasonLabel }}
          </span>
          <span class="text-lg font-bold text-[var(--color-primary)]">
            {{ session.year }}
          </span>
        </div>

        <!-- Status Badge -->
        <span
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold"
          :class="session.ready_count === session.exam_count && session.exam_count > 0
            ? 'bg-[var(--color-success-bg,#dcfce7)] text-[var(--color-success-text,#15803d)]'
            : 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]'"
        >
          <!-- Status dot -->
          <span
            class="w-1.5 h-1.5 rounded-full"
            :class="session.ready_count === session.exam_count && session.exam_count > 0
              ? 'bg-[var(--color-success-text,#15803d)]'
              : 'bg-[var(--color-warning-text,#92400e)]'"
          ></span>
          {{ t('panel.examArchive.session.examCount', {
            ready: session.ready_count,
            total: session.exam_count
          }) }}
        </span>

        <!-- Question Count Pill -->
        <span
          v-if="session.total_questions > 0"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
          </svg>
          {{ t('panel.examArchive.session.totalQuestions', { count: session.total_questions }) }}
        </span>
      </div>

      <div class="flex items-center gap-2.5">
        <!-- Tags -->
        <span
          v-for="tag in session.tags"
          :key="tag"
          class="px-2.5 py-1 rounded-full text-xs font-medium bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary-text,#6d28d9)] border border-[var(--color-primary-text,#6d28d9)]/15"
        >
          {{ tag }}
        </span>
        <!-- Chevron -->
        <div class="w-7 h-7 rounded-md flex items-center justify-center bg-[var(--color-surface-secondary)] transition-colors">
          <svg
            class="w-4 h-4 text-[var(--color-text-secondary)] transition-transform duration-200"
            :class="{ 'rotate-180': expanded }"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    </button>

    <!-- Expanded: individual exam parts -->
    <div v-if="expanded" class="border-t border-[var(--color-border)] px-4 py-3.5 space-y-2">
      <div v-if="loading" class="flex justify-center py-4">
        <div class="animate-spin rounded-full h-6 w-6 border-2 border-[var(--color-border)] border-t-[var(--color-primary)]" />
      </div>
      <template v-else>
        <div
          v-for="exam in exams"
          :key="exam.exam_id"
          class="flex items-center justify-between px-4 py-3 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] transition-colors hover:border-[var(--color-primary)]/30"
        >
          <div class="flex items-center gap-3">
            <!-- Status dot indicator -->
            <span
              class="w-2.5 h-2.5 rounded-full flex-shrink-0"
              :class="{
                'bg-[var(--color-success-text,#16a34a)]': exam.analysis_status === 'ready',
                'bg-[var(--color-warning-text,#d97706)]': exam.analysis_status === 'pending',
                'bg-[var(--color-info-text,#2563eb)]': exam.analysis_status === 'analyzing',
                'bg-[var(--color-error-text,#dc2626)]': exam.analysis_status === 'failed',
              }"
            ></span>
            <span class="text-sm font-medium text-[var(--color-text-primary)]">
              {{ exam.part || exam.title }}
            </span>
            <span
              class="inline-flex px-2 py-0.5 rounded-md text-xs font-medium"
              :class="statusClass(exam.analysis_status)"
            >
              {{ t(`panel.examArchive.status.${exam.analysis_status}`) }}
            </span>
          </div>
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
            </svg>
            {{ t('panel.examArchive.questions', { count: exam.question_count }) }}
          </span>
        </div>
        <p
          v-if="exams.length === 0"
          class="text-sm text-[var(--color-text-secondary)] text-center py-4"
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
