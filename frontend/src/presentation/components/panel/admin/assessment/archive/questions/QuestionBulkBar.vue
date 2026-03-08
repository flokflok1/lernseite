<!--
  QuestionBulkBar - Sticky bottom bar for bulk actions on selected questions.
  Shows selected count with options to change topics, delete, or clear selection.
-->

<template>
  <div
    class="sticky bottom-0 z-10 flex items-center justify-between gap-3 px-4 py-3 border-t border-[var(--color-border)] bg-[var(--color-surface)] shadow-lg"
  >
    <span class="text-sm font-medium text-[var(--color-text-primary)]">
      {{ t('panel.examArchive.questionEditor.bulkSelected', { count: selectedCount }) }}
    </span>

    <div class="flex items-center gap-2">
      <button
        @click="emit('bulk-topics')"
        class="px-3 py-1.5 text-sm rounded border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg)] transition-colors"
      >
        {{ t('panel.examArchive.questionEditor.bulkUpdateTopics') }}
      </button>
      <button
        @click="handleBulkDelete"
        class="px-3 py-1.5 text-sm rounded border border-red-300 text-red-600 hover:bg-red-50 transition-colors"
      >
        {{ t('panel.examArchive.questionEditor.bulkDelete') }}
      </button>
      <button
        @click="emit('clear-selection')"
        class="px-3 py-1.5 text-sm text-[var(--color-text-secondary)] underline hover:text-[var(--color-text-primary)] transition-colors"
      >
        {{ t('panel.examArchive.questionEditor.cancel') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Props {
  selectedCount: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'bulk-delete': []
  'bulk-topics': []
  'clear-selection': []
}>()

function handleBulkDelete() {
  const msg = t('panel.examArchive.questionEditor.bulkDeleteConfirm', { count: props.selectedCount })
  if (window.confirm(msg)) {
    emit('bulk-delete')
  }
}
</script>
