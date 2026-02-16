<script setup lang="ts">
/**
 * ComparisonPagination Component
 *
 * Displays pagination controls for comparison items list.
 * Shows current page and total pages with previous/next navigation.
 */

import { useI18n } from 'vue-i18n'

interface Props {
  currentPage: number
  totalPages: number
}

interface Emits {
  (e: 'page-change', page: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()

function handlePreviousPage(): void {
  if (props.currentPage > 0) {
    emit('page-change', props.currentPage - 1)
  }
}

function handleNextPage(): void {
  if (props.currentPage < props.totalPages - 1) {
    emit('page-change', props.currentPage + 1)
  }
}

const isPreviousDisabled = props.currentPage === 0
const isNextDisabled = props.currentPage >= props.totalPages - 1
</script>

<template>
  <div v-if="totalPages > 1" class="pagination">
    <button
      class="pagination-button"
      :disabled="isPreviousDisabled"
      @click="handlePreviousPage"
    >
      {{ $t('common.previous') }}
    </button>

    <span class="pagination-info">
      {{ currentPage + 1 }} / {{ totalPages }}
    </span>

    <button
      class="pagination-button"
      :disabled="isNextDisabled"
      @click="handleNextPage"
    >
      {{ $t('common.next') }}
    </button>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border, #e0e0e0);
  background-color: var(--color-surface, #f5f5f5);
}

.pagination-button {
  padding: 8px 16px;
  background-color: white;
  border: 1px solid var(--color-border, #e0e0e0);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary, #333);
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-button:hover:not(:disabled) {
  border-color: var(--color-primary, #2196f3);
  background-color: var(--color-primary-light, #e3f2fd);
  color: var(--color-primary, #2196f3);
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--color-surface, #f5f5f5);
}

.pagination-info {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary, #666);
  min-width: 60px;
  text-align: center;
}
</style>
