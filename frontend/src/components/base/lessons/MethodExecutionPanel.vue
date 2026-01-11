<template>
  <div class="method-execution-panel">
    <!-- Token Balance -->
    <TokenBalanceDisplay
      :balance="tokenBalance"
      :color-class="tokenColorClass"
      :percentage="tokenPercentage"
    />

    <!-- Task Stats -->
    <TaskStatsPanel
      :count-generated="countGenerated"
      :count-solved="countSolved"
      :show-calculator="false"
      @show-all="openAllTasksModal"
      @delete-all="confirmDeleteAll"
    />

    <!-- Method Cards -->
    <MethodCardList
      :methods="methods"
      :is-executing="isExecuting"
      :executing-method-id="executingMethodId"
      :get-icon="getMethodIcon"
      :get-name="getMethodName"
      :can-execute="canExecute"
      @generate="handleGenerateTask"
    />

    <!-- Recent Tasks Preview -->
    <div v-if="recentTasks.length > 0" class="recent-section">
      <h4 class="recent-title">{{ $t('lesson.methodExecution.recentTasks') }}</h4>
      <div class="recent-list">
        <button
          v-for="(task, index) in recentTasks"
          :key="index"
          @click="handleOpenRecentTask(index)"
          class="recent-item"
        >
          <div class="recent-num">{{ generatedTasks.length - index }}</div>
          <span class="recent-text">{{ getTaskPreview(task) }}</span>
          <span class="recent-status">
            {{ task.completed ? '✓' : '○' }}
          </span>
        </button>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isExecuting" class="loading-overlay">
      <div class="loading-box">
        <div class="loading-spinner"></div>
        <p class="loading-title">{{ $t('lesson.methodExecution.generating') }}</p>
        <p class="loading-hint">{{ $t('lesson.methodExecution.generatingHint') }}</p>
      </div>
    </div>

    <!-- Error Bar -->
    <Transition name="slide-up">
      <div v-if="errorMessage" class="error-bar">
        <span>{{ errorMessage }}</span>
        <button @click="errorMessage = null" class="error-close">×</button>
      </div>
    </Transition>

    <!-- Math Task Modal -->
    <MathTaskModal
      v-if="showTaskModal && selectedTaskIndex !== null && generatedTasks[selectedTaskIndex]"
      :task="generatedTasks[selectedTaskIndex].data"
      @close="closeTaskModal"
      @complete="handleTaskComplete"
    />

    <!-- All Tasks Modal -->
    <TaskManagerModal
      :show="showAllTasksModal"
      :tasks="filteredTasks"
      :selected-tasks="selectedTasks"
      :sort-by="sortBy"
      :filter-by="filterBy"
      :format-time="formatTimeAgo"
      @close="closeAllTasksModal"
      @sort="setSortBy"
      @filter="setFilterBy"
      @toggle-select="toggleTaskSelection"
      @toggle-all="toggleAllTasks"
      @delete-selected="confirmDeleteSelected"
      @delete-task="confirmDeleteTask"
      @open-task="openTaskModal"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * MethodExecutionPanel (Orchestrator)
 * ====================================
 * Coordinates method execution, task management, and token balance
 * Refactored from 1601 LOC to ~250 LOC (-84%)
 */
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LearningMethod } from '@/types/learning-methods'
import MathTaskModal from './MathTaskModal.vue'

import {
  TokenBalanceDisplay,
  TaskStatsPanel,
  MethodCardList,
  TaskManagerModal,
  useMethodExecution,
  type GeneratedTask
} from '@/components/base/lessons/method-execution'

const { t } = useI18n()

// ============================================================================
// Props
// ============================================================================

interface Props {
  lessonId: string | number
  methods: LearningMethod[]
}

const props = defineProps<Props>()

// ============================================================================
// Composable
// ============================================================================

const {
  // State - Token & Balance
  tokenBalance,
  tokenColorClass,
  tokenPercentage,

  // State - Tasks
  generatedTasks,
  selectedTaskIndex,
  selectedTasks,

  // State - UI
  isExecuting,
  errorMessage,
  showAllTasksModal,
  showTaskModal,

  // State - Modal Filters
  sortBy,
  filterBy,

  // Computed - Stats
  countGenerated,
  countSolved,

  // Computed - Tasks
  filteredTasks,
  recentTasks,

  // Methods - Metadata
  getMethodIcon,
  getMethodName,
  getMethodMetadata,

  // Methods - Task Generation
  canExecute,
  generateTask,

  // Methods - Task Management
  openTaskModal,
  closeTaskModal,
  handleTaskComplete,
  toggleTaskSelection,
  toggleAllTasks,
  deleteTask,
  deleteSelectedTasks,
  deleteAllTasks,

  // Methods - Formatting
  formatTimeAgo,

  // Methods - Modal
  openAllTasksModal,
  closeAllTasksModal,
  setSortBy,
  setFilterBy
} = useMethodExecution(String(props.lessonId))

// ============================================================================
// State (UI-specific)
// ============================================================================

const executingMethodId = ref<string | null>(null)

// ============================================================================
// Event Handlers
// ============================================================================

async function handleGenerateTask(method: LearningMethod): Promise<void> {
  executingMethodId.value = method.method_id
  try {
    await generateTask(method)
  } finally {
    executingMethodId.value = null
  }
}

function handleOpenRecentTask(recentIndex: number): void {
  // Map recent index (0-2) to actual task index (reverse order)
  const actualIndex = generatedTasks.value.length - 1 - recentIndex
  openTaskModal(actualIndex)
}

function getTaskPreview(task: GeneratedTask): string {
  if (task.data && typeof task.data === 'object') {
    if (task.data.question) return task.data.question
    if (task.data.title) return task.data.title
    if (task.data.text) return task.data.text
  }
  return task.methodName
}

function confirmDeleteAll(): void {
  if (confirm(t('lesson.methodExecution.confirmDeleteAll'))) {
    deleteAllTasks()
  }
}

function confirmDeleteSelected(): void {
  if (confirm(t('lesson.methodExecution.confirmDeleteSelected', { count: selectedTasks.value.size }))) {
    deleteSelectedTasks()
  }
}

function confirmDeleteTask(index: number): void {
  if (confirm(t('lesson.methodExecution.confirmDeleteTask'))) {
    deleteTask(index)
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  // Initialize token balance or load from API if needed
  // tokenBalance is managed by the composable
})
</script>

<style scoped>
/* Method Execution Panel */
.method-execution-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background-color: var(--color-background, #f9fafb);
}

/* Recent Section */
.recent-section {
  padding: 1rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface-secondary, #f9fafb);
}

.recent-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  margin: 0 0 0.5rem;
  text-transform: uppercase;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  font-size: 0.75rem;
  text-align: left;
  transition: all 0.2s;
}

.recent-item:hover {
  border-color: var(--color-primary, #3b82f6);
}

.recent-num {
  width: 22px;
  height: 22px;
  background-color: var(--color-primary, #3b82f6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.7rem;
  flex-shrink: 0;
}

.recent-text {
  flex: 1;
  color: var(--color-text-primary, #111827);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-status {
  flex-shrink: 0;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

:root.dark .loading-overlay {
  background-color: rgba(17, 24, 39, 0.95);
}

.loading-box {
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border, #e5e7eb);
  border-top-color: var(--color-primary, #3b82f6);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-title {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.25rem;
}

.loading-hint {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

/* Error Bar */
.error-bar {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  right: 1rem;
  padding: 0.75rem 1rem;
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: #ef4444;
  z-index: 20;
}

.error-close {
  padding: 0.25rem;
  color: #ef4444;
  opacity: 0.7;
  font-size: 1rem;
}

.error-close:hover {
  opacity: 1;
}

/* Transitions */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
