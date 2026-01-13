<template>
  <div class="explanation-list-panel">
    <!-- List Header -->
    <div class="list-header">
      <h3>{{ $t('lesson.tutorPlayer.explanations') }}</h3>
      <button @click="$emit('new-explanation')" class="new-btn" :title="$t('lesson.tutorPlayer.createNew')">
        {{ $t('common.new') }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="list-loading">
      <div class="small-spinner"></div>
      <span>{{ $t('common.loading') }}</span>
    </div>

    <!-- Empty List -->
    <div v-else-if="explanations.length === 0" class="list-empty">
      <p>{{ $t('lesson.tutorPlayer.noExplanations') }}</p>
      <button @click="$emit('new-explanation')" class="create-first-btn">
        {{ $t('lesson.tutorPlayer.createFirst') }}
      </button>
    </div>

    <!-- List Items -->
    <div v-else class="list-items">
      <div
        v-for="expl in explanations"
        :key="expl.explanationId"
        class="list-item"
        :class="{ active: selectedId === expl.explanationId }"
        @click="$emit('select', expl.explanationId)"
      >
        <div class="item-main">
          <span class="item-title">{{ expl.title }}</span>
          <span class="item-meta">
            {{ expl.style }} | {{ formatDate(expl.createdAt) }}
          </span>
        </div>
        <div class="item-actions">
          <button @click.stop="$emit('edit', expl)" class="item-btn" :title="$t('common.rename')">
            {{ $t('common.edit')[0] }}
          </button>
          <button @click.stop="$emit('delete', expl)" class="item-btn delete" :title="$t('common.delete')">
            {{ $t('common.delete')[0] }}
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Title Form -->
    <div v-if="editingExplanation" class="edit-form">
      <input
        v-model="editTitleLocal"
        type="text"
        class="edit-input"
        :placeholder="$t('lesson.tutorPlayer.newTitle')"
        @keyup.enter="$emit('save-title', editTitleLocal)"
        @keyup.esc="$emit('cancel-edit')"
      />
      <div class="edit-buttons">
        <button @click="$emit('save-title', editTitleLocal)" class="save-btn">
          {{ $t('common.save') }}
        </button>
        <button @click="$emit('cancel-edit')" class="cancel-btn">
          {{ $t('common.cancel') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * TutorExplanationList Component
 * ================================
 * Left panel displaying list of lesson explanations with edit/delete actions
 */
import { ref, watch } from 'vue'
import type { ExplanationListItem } from './composables/useTutorPlayer'

interface Props {
  explanations: ExplanationListItem[]
  selectedId: string | null
  isLoading: boolean
  editingExplanation: ExplanationListItem | null
  editTitle: string
}

const props = defineProps<Props>()

defineEmits<{
  'new-explanation': []
  'select': [explanationId: string]
  'edit': [explanation: ExplanationListItem]
  'delete': [explanation: ExplanationListItem]
  'save-title': [title: string]
  'cancel-edit': []
}>()

// Local state for edit title
const editTitleLocal = ref(props.editTitle)

// Watch for external changes to editTitle
watch(() => props.editTitle, (newVal) => {
  editTitleLocal.value = newVal
})

// ============================================================================
// Methods
// ============================================================================

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
/* Explanation List Panel */
.explanation-list-panel {
  width: 280px;
  min-width: 280px;
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* List Header */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border, #334155);
}

.list-header h3 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
}

.new-btn {
  padding: 0.375rem 0.75rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.new-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

/* Loading State */
.list-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--color-text-tertiary, #64748b);
}

.small-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border, #334155);
  border-top-color: var(--color-primary, #6366f1);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty List */
.list-empty {
  padding: 2rem 1rem;
  text-align: center;
}

.list-empty p {
  color: var(--color-text-tertiary, #64748b);
  margin: 0 0 1rem;
  font-size: 0.875rem;
}

.create-first-btn {
  padding: 0.5rem 1rem;
  background: var(--color-surface-secondary, #0f172a);
  border: 1px dashed var(--color-border, #334155);
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.create-first-btn:hover {
  border-color: var(--color-primary, #6366f1);
  color: var(--color-primary, #6366f1);
}

/* List Items */
.list-items {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  margin-bottom: 0.25rem;
  transition: all 0.2s;
}

.list-item:hover {
  background: var(--color-surface-secondary, #0f172a);
}

.list-item.active {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.item-main {
  flex: 1;
  min-width: 0;
}

.item-title {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary, #f1f5f9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary, #64748b);
  margin-top: 0.25rem;
}

.item-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.list-item:hover .item-actions {
  opacity: 1;
}

.item-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 0.25rem;
  background: var(--color-surface, #1e293b);
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.625rem;
  cursor: pointer;
  transition: all 0.2s;
}

.item-btn:hover {
  background: var(--color-surface-secondary, #0f172a);
}

.item-btn.delete:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* Edit Form */
.edit-form {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border, #334155);
}

.edit-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.375rem;
  background: var(--color-surface-secondary, #0f172a);
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.8125rem;
  margin-bottom: 0.5rem;
}

.edit-input:focus {
  outline: none;
  border-color: var(--color-primary, #6366f1);
}

.edit-buttons {
  display: flex;
  gap: 0.5rem;
}

.save-btn,
.cancel-btn {
  flex: 1;
  padding: 0.375rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn {
  background: #10b981;
  color: white;
}

.save-btn:hover {
  background: #059669;
}

.cancel-btn {
  background: var(--color-surface, #1e293b);
  color: var(--color-text-secondary, #94a3b8);
  border: 1px solid var(--color-border, #334155);
}

.cancel-btn:hover {
  background: var(--color-surface-secondary, #0f172a);
}
</style>
