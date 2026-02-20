<!--
  ExplanationListPanel - List of lesson explanations

  Left panel displaying available explanations with search, filtering,
  deletion, and creation capabilities.
-->

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LessonExplanation } from '../types/explanation.types'

const { t } = useI18n()

interface Props {
  explanations: LessonExplanation[]
  isLoading: boolean
  selectedId: string | null
}

interface Emits {
  (e: 'select', id: string): void
  (e: 'delete', id: string): void
  (e: 'refresh'): void
  (e: 'create'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Local state
const searchQuery = ref('')
const confirmDeleteId = ref<string | null>(null)

// Computed
const filteredExplanations = computed(() => {
  if (!searchQuery.value) return props.explanations

  const query = searchQuery.value.toLowerCase()
  return props.explanations.filter(exp =>
    exp.title.toLowerCase().includes(query)
  )
})

// Methods
const handleSelect = (explanationId: string) => {
  emit('select', explanationId)
}

const handleDelete = (explanationId: string) => {
  if (confirmDeleteId.value === explanationId) {
    // Confirm delete
    confirmDeleteId.value = null
    emit('delete', explanationId)
  } else {
    // First click - show confirm
    confirmDeleteId.value = explanationId
  }
}

const cancelDelete = () => {
  confirmDeleteId.value = null
}

const handleCreate = () => {
  emit('create')
}

const handleRefresh = () => {
  emit('refresh')
}
</script>

<template>
  <div class="explanation-list-panel">
    <!-- Header -->
    <div class="panel-header">
      <h3>{{ $t('course-editor.explanation.list.title') }}</h3>
      <button class="refresh-btn" @click="handleRefresh" :disabled="isLoading" title="Refresh">
        ↻
      </button>
    </div>

    <!-- Search -->
    <div class="search-bar">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="$t('course-editor.explanation.list.search')"
        class="search-input"
      />
    </div>

    <!-- List -->
    <div class="explanations-list">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>{{ $t('common.loading') }}</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredExplanations.length === 0" class="empty-state">
        <p>{{ $t('course-editor.explanation.list.empty') }}</p>
      </div>

      <!-- Explanation Items -->
      <div v-else class="items">
        <div
          v-for="explanation in filteredExplanations"
          :key="explanation.explanationId"
          :class="['item', { active: selectedId === explanation.explanationId }]"
          @click="handleSelect(explanation.explanationId)"
        >
          <div class="item-header">
            <div class="item-title">{{ explanation.title }}</div>
            <button
              :class="['delete-btn', { confirm: confirmDeleteId === explanation.explanationId }]"
              @click.stop="handleDelete(explanation.explanationId)"
            >
              {{ confirmDeleteId === explanation.explanationId ? '✓' : '✕' }}
            </button>
          </div>

          <div class="item-meta">
            <span class="style-badge">{{ explanation.style }}</span>
            <span class="step-count">{{ explanation.steps.length }} {{ $t('course-editor.explanation.list.steps') }}</span>
          </div>

          <!-- Delete Confirm -->
          <div v-if="confirmDeleteId === explanation.explanationId" class="delete-confirm">
            <button class="confirm-btn" @click.stop="handleDelete(explanation.explanationId)">
              {{ $t('common.confirm') }}
            </button>
            <button class="cancel-btn" @click.stop="cancelDelete">
              {{ $t('common.cancel') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Button -->
    <div class="panel-footer">
      <button class="create-btn" @click="handleCreate">
        + {{ $t('course-editor.explanation.list.create') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.explanation-list-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-right: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
  overflow: hidden;
}

/* Header */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem;
  border-bottom: 1px solid var(--color-border);
}

.panel-header h3 {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.refresh-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  color: var(--color-text-secondary);
  transition: color 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  color: var(--color-text-primary);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Search */
.search-bar {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 0.875rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* List */
.explanations-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 0.75rem;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
  text-align: center;
  padding: 1rem;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Items */
.items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  cursor: pointer;
  transition: all 0.2s;
}

.item:hover {
  border-color: var(--color-primary);
  background: var(--color-surface-hover);
}

.item.active {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.item-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  gap: 0.5rem;
}

.item-title {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  word-break: break-word;
}

.delete-btn {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  padding: 0;
  border: 1px solid var(--color-error-light);
  border-radius: 3px;
  background: var(--color-surface);
  color: var(--color-error);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover {
  border-color: var(--color-error);
  background: var(--color-error-light);
}

.delete-btn.confirm {
  border-color: var(--color-error);
  background: var(--color-error);
  color: white;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.style-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 500;
}

.step-count {
  display: inline-block;
}

/* Delete Confirm */
.delete-confirm {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
}

.confirm-btn,
.cancel-btn {
  flex: 1;
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  background: var(--color-surface);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn {
  border-color: var(--color-error);
  color: var(--color-error);
}

.confirm-btn:hover {
  background: var(--color-error-light);
}

.cancel-btn {
  color: var(--color-text-secondary);
}

.cancel-btn:hover {
  background: var(--color-surface-hover);
}

/* Footer */
.panel-footer {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.create-btn {
  width: 100%;
  padding: 0.625rem;
  border: 1px dashed var(--color-primary);
  border-radius: 4px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.create-btn:hover {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: white;
}
</style>
