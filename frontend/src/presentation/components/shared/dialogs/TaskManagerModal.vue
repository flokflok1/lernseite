<template>
  <Teleport to="body">
    <div v-if="show" class="overlay" @click.self="$emit('close')">
      <div class="all-modal all-modal--large">
        <!-- Header -->
        <div class="all-modal-header">
          <h3>{{ $t('lesson.methodExecution.modal.title') }}</h3>
          <button @click="$emit('close')" class="modal-close">&times;</button>
        </div>

        <!-- Toolbar -->
        <div class="modal-toolbar">
          <div class="toolbar-left">
            <!-- Sort Buttons -->
            <button
              @click="$emit('sort', 'newest')"
              class="toolbar-btn"
              :class="{ 'toolbar-btn--active': sortBy === 'newest' }"
            >
              {{ $t('lesson.methodExecution.modal.sortNewest') }}
            </button>
            <button
              @click="$emit('sort', 'oldest')"
              class="toolbar-btn"
              :class="{ 'toolbar-btn--active': sortBy === 'oldest' }"
            >
              {{ $t('lesson.methodExecution.modal.sortOldest') }}
            </button>
            <button
              @click="$emit('sort', 'method')"
              class="toolbar-btn"
              :class="{ 'toolbar-btn--active': sortBy === 'method' }"
            >
              {{ $t('lesson.methodExecution.modal.sortMethod') }}
            </button>
          </div>

          <div class="toolbar-right">
            <!-- Filter Buttons -->
            <button
              @click="$emit('filter', 'all')"
              class="toolbar-btn"
              :class="{ 'toolbar-btn--active': filterBy === 'all' }"
            >
              {{ $t('lesson.methodExecution.modal.filterAll') }}
            </button>
            <button
              @click="$emit('filter', 'completed')"
              class="toolbar-btn"
              :class="{ 'toolbar-btn--active': filterBy === 'completed' }"
            >
              {{ $t('lesson.methodExecution.modal.filterCompleted') }}
            </button>
            <button
              @click="$emit('filter', 'pending')"
              class="toolbar-btn"
              :class="{ 'toolbar-btn--active': filterBy === 'pending' }"
            >
              {{ $t('lesson.methodExecution.modal.filterPending') }}
            </button>
          </div>
        </div>

        <!-- Selection Toolbar (when tasks selected) -->
        <div v-if="hasSelected" class="modal-toolbar">
          <div class="toolbar-left">
            <span class="selection-info">
              {{ $t('lesson.methodExecution.modal.selectedCount', { count: selectedCount }) }}
            </span>
          </div>
          <div class="toolbar-right">
            <button @click="$emit('toggle-all')" class="toolbar-btn">
              {{ allSelected ? $t('common.deselectAll') : $t('common.selectAll') }}
            </button>
            <button @click="$emit('delete-selected')" class="toolbar-btn toolbar-btn--danger">
              {{ $t('lesson.methodExecution.modal.deleteSelected') }}
            </button>
          </div>
        </div>

        <!-- Body -->
        <div class="all-modal-body">
          <div v-if="tasks.length === 0" class="empty-tasks">
            <span class="empty-icon">📝</span>
            <p>{{ $t('lesson.methodExecution.modal.noTasks') }}</p>
            <p class="empty-hint">{{ $t('lesson.methodExecution.modal.noTasksHint') }}</p>
          </div>

          <div v-else>
            <TaskRowItem
              v-for="(task, index) in tasks"
              :key="index"
              :task="task"
              :index="index"
              :selected="isSelected(index)"
              :format-time="formatTime"
              @toggle-select="$emit('toggle-select', index)"
              @open="$emit('open-task', index)"
              @delete="$emit('delete-task', index)"
            />
          </div>
        </div>

        <!-- Footer -->
        <div class="all-modal-footer">
          <div class="footer-stats">
            <span>{{ $t('lesson.methodExecution.modal.totalTasks', { count: tasks.length }) }}</span>
            <span>{{ $t('lesson.methodExecution.modal.completedTasks', { count: completedCount }) }}</span>
          </div>
          <button @click="$emit('close')" class="close-btn">
            {{ $t('common.close') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
/**
 * TaskManagerModal Component
 * ===========================
 * Enhanced modal for managing all generated tasks
 * Features: Sort, Filter, Selection, Bulk Delete
 */
import { computed } from 'vue'
import type { GeneratedTask } from '../../public/learning/methods/method-execution/composables/useMethodExecution.ts'
import TaskRowItem from './TaskRowItem.vue'

interface Props {
  show: boolean
  tasks: GeneratedTask[]
  selectedTasks: Set<number>
  sortBy: 'newest' | 'oldest' | 'method'
  filterBy: 'all' | 'completed' | 'pending'
  formatTime: (date: Date) => string
}

const props = defineProps<Props>()

defineEmits<{
  'close': []
  'sort': [sort: 'newest' | 'oldest' | 'method']
  'filter': [filter: 'all' | 'completed' | 'pending']
  'toggle-select': [index: number]
  'toggle-all': []
  'delete-selected': []
  'delete-task': [index: number]
  'open-task': [index: number]
}>()

// ============================================================================
// Computed
// ============================================================================

const hasSelected = computed(() => props.selectedTasks.size > 0)
const selectedCount = computed(() => props.selectedTasks.size)
const allSelected = computed(() => props.tasks.length > 0 && props.selectedTasks.size === props.tasks.length)
const completedCount = computed(() => props.tasks.filter(t => t.completed).length)

// ============================================================================
// Methods
// ============================================================================

function isSelected(index: number): boolean {
  return props.selectedTasks.has(index)
}
</script>

<style scoped>
/* Overlay */
.overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

/* Modal */
.all-modal {
  background-color: var(--color-surface, #ffffff);
  border-radius: 1rem;
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.all-modal--large {
  max-width: 700px;
  max-height: 85vh;
}

/* Header */
.all-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.all-modal-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #6b7280);
  font-size: 1.25rem;
  transition: all 0.2s;
}

.modal-close:hover {
  background-color: var(--color-surface-secondary, #f9fafb);
}

/* Toolbar */
.modal-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface-secondary, #f9fafb);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.toolbar-btn {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  border-radius: 0.375rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text-primary, #111827);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.toolbar-btn:hover {
  border-color: var(--color-primary, #3b82f6);
}

.toolbar-btn--active {
  background-color: var(--color-primary, #3b82f6);
  color: white;
  border-color: var(--color-primary, #3b82f6);
}

.toolbar-btn--danger {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
}

.toolbar-btn--danger:hover {
  background-color: #ef4444;
  color: white;
}

.selection-info {
  font-size: 0.75rem;
  color: var(--color-primary, #3b82f6);
  font-weight: 500;
}

/* Body */
.all-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

/* Empty State */
.empty-tasks {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary, #6b7280);
}

.empty-tasks .empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.75rem;
}

.empty-tasks p {
  margin: 0;
}

.empty-hint {
  font-size: 0.875rem;
  margin-top: 0.25rem !important;
}

/* Footer */
.all-modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}

.close-btn {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  background-color: var(--color-surface-secondary, #f9fafb);
  color: var(--color-text-primary, #111827);
  border: 1px solid var(--color-border, #e5e7eb);
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: var(--color-surface, #ffffff);
}
</style>
