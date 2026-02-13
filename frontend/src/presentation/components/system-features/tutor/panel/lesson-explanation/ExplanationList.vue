<!--
  ExplanationList - List of lesson explanations with create form
-->

<template>
  <div class="explanation-list">
    <div class="panel-header">
      <span class="panel-icon">📝</span>
      <span class="panel-title">{{ $t('lessonExplanationView.explanations') }}</span>
      <button
        @click="$emit('refresh')"
        class="refresh-btn"
        :title="$t('lessonExplanationView.refresh')"
      >
        🔄
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="list-loading">
      <div class="spinner"></div>
      <span>{{ $t('lessonExplanationView.loading') }}</span>
    </div>

    <!-- Explanation List -->
    <div v-else class="content-list">
      <div v-if="explanations.length === 0" class="list-empty">
        <span class="empty-icon-small">📝</span>
        <p>{{ $t('lessonExplanationView.noExplanations') }}</p>
      </div>

      <div
        v-for="expl in explanations"
        :key="expl.explanationId"
        class="list-item"
        :class="{ active: selectedId === expl.explanationId }"
        @click="$emit('select', expl.explanationId)"
      >
        <div class="item-icon">📖</div>
        <div class="item-info">
          <span class="item-name">{{ expl.title }}</span>
          <span class="item-meta">
            {{ $t('lessonExplanationView.stepsCount', { count: expl.stepCount }) }} •
            {{ formatDate(expl.createdAt) }}
          </span>
        </div>
        <div class="item-actions">
          <button
            @click.stop="handleDelete(expl.explanationId)"
            class="item-btn danger"
            :title="$t('lessonExplanationView.delete')"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- Create New Button -->
    <div class="list-actions">
      <button @click="$emit('create')" class="create-btn">
        {{ $t('lessonExplanationView.createNew') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ExplanationList - Displays list of lesson explanations
 */
import { useI18n } from 'vue-i18n'
import type { LessonExplanation } from '@/application/composables/useTheoryManagement'

const { t } = useI18n()

// Props
interface Props {
  explanations: LessonExplanation[]
  isLoading: boolean
  selectedId: string | null
}

defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'select', id: string): void
  (e: 'delete', id: string): void
  (e: 'create'): void
  (e: 'refresh'): void
}>()

// Methods
function handleDelete(id: string): void {
  if (confirm(t('lessonExplanationView.confirmDelete'))) {
    emit('delete', id)
  }
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit'
    })
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.explanation-list {
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon {
  font-size: 1rem;
}

.panel-title {
  font-weight: 600;
  font-size: 0.875rem;
  flex: 1;
}

.refresh-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.6;
}

.refresh-btn:hover {
  opacity: 1;
}

/* List */
.list-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.content-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  color: var(--color-text-tertiary);
}

.empty-icon-small {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.list-empty p {
  margin: 0;
  font-size: 0.875rem;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 0.25rem;
}

.list-item:hover {
  background: var(--color-surface-secondary);
}

.list-item.active {
  background: var(--color-primary);
  color: white;
}

.list-item.active .item-meta {
  color: rgba(255, 255, 255, 0.8);
}

.item-icon {
  font-size: 1.25rem;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-meta {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.item-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
}

.list-item:hover .item-actions,
.list-item.active .item-actions {
  opacity: 1;
}

.item-btn {
  padding: 0.25rem 0.375rem;
  background: none;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.15s;
}

.item-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.item-btn.danger:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* Actions */
.list-actions {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.create-btn {
  width: 100%;
  padding: 0.625rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.create-btn:hover {
  background: var(--color-primary-dark);
}
</style>
