<!--
  CalculatorHistoryPanel - History display for OnScreenCalculator

  Shows past calculations and allows reusing results.
-->

<template>
  <div v-if="history.length > 0" class="history-panel">
    <div class="history-header">
      <span>{{ $t('calculator.history') }}</span>
      <button @click="$emit('clear')" class="history-clear">
        {{ $t('calculator.clearHistory') }}
      </button>
    </div>
    <div class="history-list">
      <div
        v-for="(entry, idx) in history.slice(0, 5)"
        :key="idx"
        class="history-entry"
        @click="$emit('use-entry', entry)"
      >
        <span class="entry-formula">{{ entry.formula }}</span>
        <span class="entry-result">= {{ formatNumber(entry.result) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { HistoryEntry } from './composables/useCalculator'

interface Props {
  history: HistoryEntry[]
  formatNumber: (num: number) => string
}

defineProps<Props>()

defineEmits<{
  (e: 'clear'): void
  (e: 'use-entry', entry: HistoryEntry): void
}>()
</script>

<style scoped>
.history-panel {
  margin-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 0.75rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.history-clear {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 0.6875rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.history-clear:hover {
  background: rgba(239, 68, 68, 0.1);
}

.history-list {
  max-height: 100px;
  overflow-y: auto;
}

.history-entry {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0.5rem;
  margin-bottom: 0.25rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.75rem;
  transition: background 0.15s;
}

.history-entry:hover {
  background: rgba(99, 102, 241, 0.15);
}

.entry-formula {
  color: #94a3b8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 120px;
}

.entry-result {
  color: #6366f1;
  font-weight: 500;
}
</style>
