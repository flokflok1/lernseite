/**
 * useMethodExecution Composable
 * ==============================
 * Business logic for method execution panel:
 * - Token balance management
 * - Task generation & completion
 * - Task CRUD (delete, filter, sort, select)
 * - Method metadata (icons, names)
 * - Time formatting
 */
import { ref, computed, readonly } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePlayerStore } from '@/application/stores/player.store'
import type { LearningMethod } from '@/types/learning-methods'

// ============================================================================
// Types
// ============================================================================

export interface GeneratedTask {
  data: any
  methodName: string
  methodType: number
  tokensUsed: number
  completed: boolean
  createdAt: Date
}

export interface MethodMetadata {
  icon: string
  name: string
  description: string
}

// ============================================================================
// Composable
// ============================================================================

export function useMethodExecution(lessonId: string) {
  const { t } = useI18n()
  const playerStore = usePlayerStore()

  // ==========================================================================
  // State
  // ==========================================================================

  // Token & Balance
  const tokenBalance = ref(5000) // Initial balance

  // Tasks
  const generatedTasks = ref<GeneratedTask[]>([])
  const selectedTaskIndex = ref<number | null>(null)
  const selectedTasks = ref<Set<number>>(new Set())

  // UI State
  const isExecuting = ref(false)
  const errorMessage = ref<string | null>(null)
  const showAllTasksModal = ref(false)
  const showTaskModal = ref(false)

  // Modal Filters/Sorting
  const sortBy = ref<'newest' | 'oldest' | 'method'>('newest')
  const filterBy = ref<'all' | 'completed' | 'pending'>('all')

  // ==========================================================================
  // Computed - Stats
  // ==========================================================================

  const countGenerated = computed(() => generatedTasks.value.length)
  const countSolved = computed(() => generatedTasks.value.filter(t => t.completed).length)
  const countPending = computed(() => countGenerated.value - countSolved.value)

  const tokenColorClass = computed(() => {
    if (tokenBalance.value < 500) return 'color-red'
    if (tokenBalance.value < 2000) return 'color-yellow'
    return 'color-green'
  })

  const tokenPercentage = computed(() => {
    const max = 10000 // Max tokens
    return Math.min(100, (tokenBalance.value / max) * 100)
  })

  // ==========================================================================
  // Computed - Filtered/Sorted Tasks
  // ==========================================================================

  const filteredTasks = computed(() => {
    let tasks = [...generatedTasks.value]

    // Filter
    if (filterBy.value === 'completed') {
      tasks = tasks.filter(t => t.completed)
    } else if (filterBy.value === 'pending') {
      tasks = tasks.filter(t => !t.completed)
    }

    // Sort
    if (sortBy.value === 'newest') {
      tasks.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
    } else if (sortBy.value === 'oldest') {
      tasks.sort((a, b) => a.createdAt.getTime() - b.createdAt.getTime())
    } else if (sortBy.value === 'method') {
      tasks.sort((a, b) => a.methodName.localeCompare(b.methodName))
    }

    return tasks
  })

  const recentTasks = computed(() => {
    return generatedTasks.value
      .slice()
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, 3)
  })

  const hasSelectedTasks = computed(() => selectedTasks.value.size > 0)
  const allTasksSelected = computed(() =>
    filteredTasks.value.length > 0 && selectedTasks.value.size === filteredTasks.value.length
  )

  // ==========================================================================
  // Method Metadata
  // ==========================================================================

  const methodIcons: Record<number, string> = {
    0: '📖', 1: '📝', 2: '🔄', 3: '📊', 4: '💭',
    5: '🔢', 6: '🎯', 7: '🎲', 8: '✍️',
    9: '📋', 10: '❓', 11: '✓'
  }

  function getMethodIcon(methodType: number): string {
    return methodIcons[methodType] || '📄'
  }

  function getMethodName(methodType: number): string {
    // Use i18n keys instead of hardcoded strings
    const key = `lesson.methodExecution.methods.lm${String(methodType).padStart(2, '0')}`
    return t(key)
  }

  function getMethodMetadata(method: LearningMethod): MethodMetadata {
    return {
      icon: getMethodIcon(method.method_type),
      name: getMethodName(method.method_type),
      description: method.description || ''
    }
  }

  // ==========================================================================
  // Methods - Task Generation
  // ==========================================================================

  function canExecute(method: LearningMethod): boolean {
    const tokensRequired = method.estimated_tokens || 100
    return tokenBalance.value >= tokensRequired && !isExecuting.value
  }

  async function generateTask(method: LearningMethod): Promise<void> {
    if (!canExecute(method) || isExecuting.value) {
      return
    }

    isExecuting.value = true
    errorMessage.value = null

    try {
      const response = await playerStore.executeLearningMethod({
        lesson_id: lessonId,
        method_id: method.method_id
      })

      if (playerStore.methodResult) {
        const parsed = parseResult(playerStore.methodResult)
        const tokensUsed = response?.tokens_used || method.estimated_tokens || 100

        generatedTasks.value.push({
          data: parsed,
          methodName: getMethodName(method.method_type),
          methodType: method.method_type,
          tokensUsed: tokensUsed,
          completed: false,
          createdAt: new Date()
        })

        // Deduct tokens
        tokenBalance.value = Math.max(0, tokenBalance.value - tokensUsed)
      }
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : t('errors.unknownError')

      // Auto-hide error after 5 seconds
      setTimeout(() => {
        errorMessage.value = null
      }, 5000)
    } finally {
      isExecuting.value = false
    }
  }

  function parseResult(result: any): any {
    if (typeof result === 'string') {
      try {
        return JSON.parse(result)
      } catch {
        return result
      }
    }
    return result
  }

  // ==========================================================================
  // Methods - Task Management
  // ==========================================================================

  function openTaskModal(index: number): void {
    selectedTaskIndex.value = index
    showTaskModal.value = true
  }

  function closeTaskModal(): void {
    showTaskModal.value = false
    selectedTaskIndex.value = null
  }

  function handleTaskComplete(index: number): void {
    if (index >= 0 && index < generatedTasks.value.length) {
      generatedTasks.value[index].completed = true
    }
    closeTaskModal()
  }

  function toggleTaskSelection(index: number): void {
    if (selectedTasks.value.has(index)) {
      selectedTasks.value.delete(index)
    } else {
      selectedTasks.value.add(index)
    }
  }

  function toggleAllTasks(): void {
    if (allTasksSelected.value) {
      selectedTasks.value.clear()
    } else {
      filteredTasks.value.forEach((_, index) => {
        selectedTasks.value.add(index)
      })
    }
  }

  function deleteTask(index: number): void {
    generatedTasks.value.splice(index, 1)
    selectedTasks.value.delete(index)
  }

  function deleteSelectedTasks(): void {
    const indices = Array.from(selectedTasks.value).sort((a, b) => b - a)
    indices.forEach(index => {
      generatedTasks.value.splice(index, 1)
    })
    selectedTasks.value.clear()
  }

  function deleteAllTasks(): void {
    generatedTasks.value = []
    selectedTasks.value.clear()
  }

  // ==========================================================================
  // Methods - Formatting
  // ==========================================================================

  function formatRelativeTime(date: Date): string {
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHour = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHour / 24)

    if (diffSec < 60) {
      return t('lesson.methodExecution.time.justNow')
    } else if (diffMin < 60) {
      return t('lesson.methodExecution.time.minutesAgo', { count: diffMin })
    } else if (diffHour < 24) {
      return t('lesson.methodExecution.time.hoursAgo', { count: diffHour })
    } else {
      return t('lesson.methodExecution.time.daysAgo', { count: diffDay })
    }
  }

  function formatTimeAgo(date: Date): string {
    return formatRelativeTime(date)
  }

  // ==========================================================================
  // Methods - Modal
  // ==========================================================================

  function openAllTasksModal(): void {
    showAllTasksModal.value = true
  }

  function closeAllTasksModal(): void {
    showAllTasksModal.value = false
    selectedTasks.value.clear()
  }

  function setSortBy(sort: 'newest' | 'oldest' | 'method'): void {
    sortBy.value = sort
  }

  function setFilterBy(filter: 'all' | 'completed' | 'pending'): void {
    filterBy.value = filter
  }

  // ==========================================================================
  // Return
  // ==========================================================================

  return {
    // State - Token & Balance
    tokenBalance: readonly(tokenBalance),
    tokenColorClass,
    tokenPercentage,

    // State - Tasks
    generatedTasks: readonly(generatedTasks),
    selectedTaskIndex: readonly(selectedTaskIndex),
    selectedTasks: readonly(selectedTasks),

    // State - UI
    isExecuting: readonly(isExecuting),
    errorMessage: readonly(errorMessage),
    showAllTasksModal: readonly(showAllTasksModal),
    showTaskModal: readonly(showTaskModal),

    // State - Modal Filters
    sortBy: readonly(sortBy),
    filterBy: readonly(filterBy),

    // Computed - Stats
    countGenerated,
    countSolved,
    countPending,

    // Computed - Tasks
    filteredTasks,
    recentTasks,
    hasSelectedTasks,
    allTasksSelected,

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
    formatRelativeTime,
    formatTimeAgo,

    // Methods - Modal
    openAllTasksModal,
    closeAllTasksModal,
    setSortBy,
    setFilterBy
  }
}
