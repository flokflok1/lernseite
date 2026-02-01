<template>
  <div class="pagination">
    <button
      :disabled="currentPage === 1"
      @click="$emit('change', currentPage - 1)"
      class="pagination-btn"
    >
      ← {{ $t('common.previous') }}
    </button>

    <span class="pagination-info">
      {{ $t('common.page') }} {{ currentPage }} {{ $t('common.of') }} {{ totalPages }}
    </span>

    <button
      :disabled="currentPage === totalPages"
      @click="$emit('change', currentPage + 1)"
      class="pagination-btn"
    >
      {{ $t('common.next') }} →
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{
  currentPage: number
  totalPages: number
}>()

defineEmits<{
  change: [page: number]
}>()

const { t } = useI18n()
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: center;
  padding: 1rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.pagination-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.pagination-info {
  font-weight: 500;
  color: #6b7280;
}
</style>
