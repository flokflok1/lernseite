<!--
  QuestionHistory - Timeline of changes for a specific question.
-->

<template>
  <div>
    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-6">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-[var(--color-primary)]"></div>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="entries.length === 0"
      class="text-center py-6 text-sm text-[var(--color-text-tertiary)]"
    >
      {{ t('panel.examArchive.questionEditor.historyEmpty') }}
    </div>

    <!-- Timeline -->
    <div v-else class="space-y-3">
      <div
        v-for="entry in entries"
        :key="entry.id"
        class="relative pl-6 border-l-2 border-[var(--color-border)] pb-3 last:pb-0"
      >
        <!-- Timeline dot -->
        <div
          class="absolute -left-[5px] top-1 w-2 h-2 rounded-full"
          style="background-color: var(--color-primary, #7c3aed);"
        ></div>

        <!-- Entry header -->
        <div class="flex items-center gap-2 mb-1">
          <span class="text-sm font-medium text-[var(--color-text-primary)]">
            {{ entry.changed_by_name }}
          </span>
          <span class="text-xs text-[var(--color-text-tertiary)]">
            {{ formatDate(entry.changed_at) }}
          </span>
        </div>

        <!-- Field changed -->
        <div class="text-xs text-[var(--color-text-secondary)] mb-1">
          {{ t('panel.examArchive.questionEditor.changedField', { field: fieldLabel(entry.field) }) }}
        </div>

        <!-- Old / New values -->
        <div class="flex gap-2 text-xs">
          <span
            class="px-2 py-0.5 rounded line-through opacity-60"
            style="background-color: var(--color-error-bg, #fee2e2); color: var(--color-error-text, #dc2626);"
          >
            {{ truncateValue(entry.old_value) }}
          </span>
          <span class="text-[var(--color-text-tertiary)]">&rarr;</span>
          <span
            class="px-2 py-0.5 rounded"
            style="background-color: var(--color-success-bg, #dcfce7); color: var(--color-success-text, #15803d);"
          >
            {{ truncateValue(entry.new_value) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { QuestionHistoryEntry } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import { archiveQuestionHistory } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  questionId: string
}

const props = defineProps<Props>()

const { t } = useI18n()

const loading = ref(true)
const entries = ref<QuestionHistoryEntry[]>([])

onMounted(async () => {
  try {
    entries.value = await archiveQuestionHistory(props.questionId)
  } catch (err) {
    console.error('Failed to load question history:', err)
  } finally {
    loading.value = false
  }
})

function fieldLabel(field: string): string {
  const key = `panel.examArchive.questionEditor.fields.${field}`
  const translated = t(key)
  return translated !== key ? translated : field
}

function formatDate(iso: string): string {
  const date = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 60) return `${diffMin}m`
  const diffH = Math.floor(diffMin / 60)
  if (diffH < 24) return `${diffH}h`
  return date.toLocaleDateString()
}

function truncateValue(val: any): string {
  const s = typeof val === 'string' ? val : JSON.stringify(val) ?? ''
  return s.length > 60 ? s.slice(0, 57) + '...' : s
}
</script>
