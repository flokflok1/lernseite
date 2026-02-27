<template>
  <div class="task-practice-list">
    <!-- Empty State -->
    <div v-if="tasks.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <p class="empty-title">{{ $t('lesson.methodExecution.emptyTasks') }}</p>
      <p class="empty-hint">{{ $t('lesson.methodExecution.emptyTasksHint') }}</p>
    </div>

    <!-- Task List -->
    <div v-else class="task-list">
      <button
        v-for="task in tasks"
        :key="String(task.method_id)"
        class="task-item"
        :class="{
          'task-item--active': String(task.method_id) === String(activeTaskId),
          'task-item--completed': task.completed
        }"
        @click="$emit('open', task.method_id)"
      >
        <span class="task-icon">{{ getIcon(task.method_type) }}</span>
        <div class="task-content">
          <span class="task-title">{{ task.title }}</span>
          <span class="task-method-name">{{ getName(task.method_type) }}</span>
        </div>
        <div class="task-meta">
          <span v-if="task.difficulty" class="task-difficulty" :class="`diff-${task.difficulty}`">
            {{ difficultyDots(task.difficulty) }}
          </span>
          <span v-if="task.completed" class="task-check" :title="$t('lesson.methodExecution.taskCompleted')">
            &#10003;
          </span>
          <span v-else-if="task.attempts > 0" class="task-attempts">
            {{ task.attempts }}x
          </span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TaskWithProgress } from './composables/useTaskPractice'

interface Props {
  tasks: TaskWithProgress[]
  activeTaskId?: string | number | null
  getIcon: (methodType: number) => string
  getName: (methodType: number) => string
}

defineProps<Props>()

defineEmits<{
  open: [methodId: string | number]
}>()

function difficultyDots(level: number): string {
  return '●'.repeat(level) + '○'.repeat(3 - level)
}
</script>

<style scoped>
.task-practice-list {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.08) transparent;
}

.task-practice-list::-webkit-scrollbar {
  width: 4px;
}

.task-practice-list::-webkit-scrollbar-track {
  background: transparent;
}

.task-practice-list::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 1rem;
  text-align: center;
}

.empty-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
  opacity: 0.4;
}

.empty-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.25rem;
}

.empty-hint {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
  max-width: 220px;
}

/* Task List */
.task-list {
  display: flex;
  flex-direction: column;
  padding: 0.25rem 0;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  margin: 0 0.375rem;
  border-radius: 0.5rem;
  background: transparent;
  border: 1px solid transparent;
  text-align: left;
  transition: all 0.15s ease;
  cursor: pointer;
  width: calc(100% - 0.75rem);
}

.task-item:hover {
  background-color: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.06);
}

.task-item--active {
  background-color: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.25);
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.1);
}

.task-item--active .task-title {
  color: #a5b4fc;
}

.task-item--active .task-icon {
  transform: scale(1.1);
}

.task-item--completed {
  opacity: 0.55;
}

.task-item--completed:hover {
  opacity: 0.75;
}

/* Icon */
.task-icon {
  font-size: 1rem;
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  background: rgba(255, 255, 255, 0.04);
  transition: transform 0.15s ease;
}

/* Content */
.task-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.task-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary, #111827);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.15s;
}

:root.dark .task-title {
  color: #e2e8f0;
}

.task-method-name {
  font-size: 0.6875rem;
  color: var(--color-text-secondary, #6b7280);
}

:root.dark .task-method-name {
  color: #64748b;
}

/* Meta (right side) */
.task-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.task-difficulty {
  font-size: 0.5rem;
  letter-spacing: 1px;
  color: var(--color-text-secondary, #6b7280);
}

.task-difficulty.diff-1 {
  color: #10b981;
}

.task-difficulty.diff-2 {
  color: #f59e0b;
}

.task-difficulty.diff-3 {
  color: #ef4444;
}

.task-check {
  color: #10b981;
  font-size: 0.75rem;
  font-weight: 700;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 185, 129, 0.12);
  border-radius: 50%;
}

.task-attempts {
  font-size: 0.6875rem;
  color: var(--color-text-secondary, #6b7280);
  font-variant-numeric: tabular-nums;
}
</style>
