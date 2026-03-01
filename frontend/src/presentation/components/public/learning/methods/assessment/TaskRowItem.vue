<!--
  TaskRowItem.vue

  Renders a single task row within the TaskManagerModal.
  Displays checkbox, task preview, status badge, and delete button.

  Extracted from TaskManagerModal.vue for G01 compliance (<500 LOC).
-->

<template>
  <div
    class="task-row-enhanced"
    :class="{
      'task-row--done': task.completed,
      'task-row--selected': selected
    }"
  >
    <!-- Checkbox -->
    <label class="task-checkbox" @click.stop>
      <input
        type="checkbox"
        :checked="selected"
        @change="$emit('toggle-select')"
      />
      <span class="checkmark"></span>
    </label>

    <!-- Task Content -->
    <div class="task-content" @click="$emit('open')">
      <div class="task-num">{{ index + 1 }}</div>
      <div class="task-details">
        <p class="task-question">
          {{ taskPreview }}
        </p>
        <div class="task-meta">
          <span class="meta-method">{{ task.methodName }}</span>
          <span>{{ formatTime(task.createdAt) }}</span>
          <span>{{ task.tokensUsed }} {{ $t('lesson.methodExecution.tokens') }}</span>
        </div>
      </div>
    </div>

    <!-- Status Badge -->
    <div class="task-status">
      <span v-if="task.completed" class="task-badge">
        &#x2713; {{ $t('lesson.methodExecution.modal.completed') }}
      </span>
      <span v-else class="task-badge">
        {{ $t('lesson.methodExecution.modal.pending') }}
      </span>
    </div>

    <!-- Delete Button -->
    <button
      @click.stop="$emit('delete')"
      class="task-delete"
      :title="$t('common.delete')"
    >
      &#x1F5D1;&#xFE0F;
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { GeneratedTask } from '../../public/learning/methods/method-execution/composables/useMethodExecution.ts'

interface Props {
  task: GeneratedTask
  index: number
  selected: boolean
  formatTime: (date: Date) => string
}

const props = defineProps<Props>()

defineEmits<{
  'toggle-select': []
  'open': []
  'delete': []
}>()

const taskPreview = computed((): string => {
  if (props.task.data && typeof props.task.data === 'object') {
    if (props.task.data.question) return props.task.data.question
    if (props.task.data.title) return props.task.data.title
    if (props.task.data.text) return props.task.data.text
  }
  return props.task.methodName
})
</script>

<style scoped>
.task-row-enhanced {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  background-color: var(--color-surface, #ffffff);
  transition: all 0.2s;
}

.task-row-enhanced:hover {
  border-color: var(--color-primary, #3b82f6);
}

.task-row-enhanced.task-row--done {
  background-color: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.3);
}

.task-row-enhanced.task-row--selected {
  border-color: var(--color-primary, #3b82f6);
  background-color: rgba(59, 130, 246, 0.05);
}

/* Checkbox */
.task-checkbox {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.task-checkbox input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border, #e5e7eb);
  border-radius: 4px;
  background-color: var(--color-surface, #ffffff);
  transition: all 0.2s;
}

.task-checkbox input:checked ~ .checkmark {
  background-color: var(--color-primary, #3b82f6);
  border-color: var(--color-primary, #3b82f6);
}

.task-checkbox input:checked ~ .checkmark::after {
  content: '\2713';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

/* Task Content */
.task-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  min-width: 0;
}

.task-num {
  width: 28px;
  height: 28px;
  background-color: var(--color-primary, #3b82f6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.task-details {
  flex: 1;
  min-width: 0;
}

.task-question {
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.task-meta span {
  font-size: 0.7rem;
  color: var(--color-text-secondary, #6b7280);
}

.meta-method {
  background-color: var(--color-surface-secondary, #f9fafb);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

/* Task Status */
.task-status {
  flex-shrink: 0;
}

.task-badge {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

/* Task Delete */
.task-delete {
  padding: 0.375rem;
  border-radius: 0.375rem;
  background: transparent;
  color: var(--color-text-secondary, #6b7280);
  transition: all 0.2s;
  flex-shrink: 0;
}

.task-delete:hover:not(:disabled) {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.task-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
