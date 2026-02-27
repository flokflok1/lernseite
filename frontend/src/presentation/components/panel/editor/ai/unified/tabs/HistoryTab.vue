<script setup lang="ts">
/**
 * HistoryTab — Generation history with filtering
 */
import { onMounted, onActivated, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import type { useGenerationHistory } from '../composables'

interface Props {
  courseId: string
}

const props = defineProps<Props>()
const { t } = useI18n()

const history = inject<ReturnType<typeof useGenerationHistory>>('generationHistory')
if (!history) {
  throw new Error('[HistoryTab] Missing required inject: generationHistory. Must be used inside UnifiedAIEditor.')
}

function refreshHistory() {
  if (props.courseId) {
    history.loadHistory(props.courseId)
  }
}

onMounted(refreshHistory)
onActivated(refreshHistory)

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString()
}
</script>

<template>
  <div class="history-tab">
    <!-- Header -->
    <div class="history-header">
      <h3 class="history-title">{{ t('aiEditor.history.title') }}</h3>
      <span class="history-tokens">
        {{ history.totalTokens.value.toLocaleString() }} {{ t('aiEditor.history.totalTokens') }}
      </span>
    </div>

    <!-- Filter -->
    <div v-if="history.uniqueSkills.value.length > 1" class="history-filters">
      <button
        class="filter-btn"
        :class="{ active: !history.filterSkill.value }"
        @click="history.setFilter(null)"
      >
        {{ t('aiEditor.history.all') }}
      </button>
      <button
        v-for="skill in history.uniqueSkills.value"
        :key="skill"
        class="filter-btn"
        :class="{ active: history.filterSkill.value === skill }"
        @click="history.setFilter(skill)"
      >
        {{ skill }}
      </button>
    </div>

    <!-- Entries -->
    <div class="history-body">
      <div v-if="history.isLoading.value" class="loading-state">
        {{ t('common.loading') }}
      </div>
      <div v-else-if="history.filteredEntries.value.length === 0" class="empty-state">
        {{ t('aiEditor.history.empty') }}
      </div>
      <div v-else class="entry-list">
        <div
          v-for="entry in history.filteredEntries.value"
          :key="entry.generation_id"
          class="entry-row"
        >
          <div class="entry-top">
            <span class="entry-skill">{{ entry.skill_code }}</span>
            <span class="entry-status" :class="'status-' + entry.status">
              {{ entry.status }}
            </span>
          </div>
          <div class="entry-meta">
            <span>{{ entry.model_name }}</span>
            <span>{{ (entry.tokens_input + entry.tokens_output).toLocaleString() }} tokens</span>
            <span>{{ formatDate(entry.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.history-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.history-tokens {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.history-filters {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.filter-btn {
  padding: 0.25rem 0.625rem;
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  background: var(--color-surface-secondary, var(--color-surface));
  color: var(--color-text-secondary);
}

.filter-btn.active {
  background: var(--color-primary);
  color: white;
}

.history-body {
  flex: 1;
  overflow-y: auto;
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 8rem;
  font-size: 0.8125rem;
  color: var(--color-text-tertiary);
}

.entry-list {
  display: flex;
  flex-direction: column;
}

.entry-row {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  transition: background 0.1s;
}

.entry-row:hover {
  background: var(--color-surface-secondary, var(--color-surface));
}

.entry-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.entry-skill {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.entry-status {
  font-size: 0.5625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-completed {
  background: var(--color-success-subtle, #1a3b2a);
  color: var(--color-success, #48bb78);
}

.status-failed {
  background: var(--color-danger-subtle, #3b1a1a);
  color: var(--color-danger, #fc8181);
}

.status-running {
  background: var(--color-info-subtle, #1a2a3b);
  color: var(--color-info, #63b3ed);
}

.entry-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}
</style>
