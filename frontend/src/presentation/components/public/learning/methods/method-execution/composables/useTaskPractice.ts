/**
 * useTaskPractice Composable
 * ==========================
 * Primary sidebar logic for task practice list.
 * Merges available methods with user progress data.
 * Replaces useMethodExecution as the primary sidebar composable.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePlayerStore } from '@/application/stores/modules/content/player.store'

// ============================================================================
// Types
// ============================================================================

export interface TaskWithProgress {
  method_id: string | number
  title: string
  method_type: number
  difficulty: number | null
  order_index: number
  tier: string
  completed: boolean
  score: number | null
  attempts: number
}

// ============================================================================
// Method Metadata
// ============================================================================

const METHOD_ICONS: Record<number, string> = {
  0: '📖', 1: '📝', 2: '🔄', 3: '📊', 4: '💭',
  5: '🔢', 6: '🎯', 7: '🎲', 8: '✍️',
  9: '📋', 10: '❓', 11: '✓'
}

const DIFFICULTY_LABELS: Record<number, string> = {
  1: 'easy',
  2: 'medium',
  3: 'hard',
}

// ============================================================================
// Composable
// ============================================================================

export function useTaskPractice(lessonId: string) {
  const { t } = useI18n()
  const playerStore = usePlayerStore()

  // ========================================================================
  // Computed — Tasks merged with progress
  // ========================================================================

  const tasks = computed<TaskWithProgress[]>(() => {
    const methods = playerStore.availableMethods as any[]
    const progress = playerStore.methodsProgress

    return methods
      .map((m) => {
        const methodId = String(m.method_id)
        const p = progress[methodId]
        return {
          method_id: m.method_id,
          title: m.title || getMethodName(m.method_type),
          method_type: m.method_type ?? 0,
          difficulty: m.difficulty ?? null,
          order_index: m.order_index ?? 0,
          tier: m.tier ?? 'basis',
          completed: p?.completed ?? false,
          score: p?.score ?? null,
          attempts: p?.attempts ?? 0,
        }
      })
      .sort((a, b) => a.order_index - b.order_index)
  })

  const completedCount = computed(() => playerStore.completedMethodsCount)
  const totalCount = computed(() => playerStore.totalMethodsCount)

  const progressPercentage = computed(() => {
    if (totalCount.value === 0) return 0
    return Math.round((completedCount.value / totalCount.value) * 100)
  })

  // ========================================================================
  // Helpers
  // ========================================================================

  function getMethodIcon(methodType: number): string {
    return METHOD_ICONS[methodType] || '📄'
  }

  function getMethodName(methodType: number): string {
    const key = `lesson.methodExecution.methods.lm${String(methodType).padStart(2, '0')}`
    return t(key)
  }

  function getDifficultyLabel(difficulty: number | null): string | null {
    if (difficulty == null) return null
    const key = DIFFICULTY_LABELS[difficulty]
    return key ? t(`lesson.methodExecution.difficulty.${key}`) : null
  }

  // ========================================================================
  // Actions
  // ========================================================================

  async function refreshProgress(): Promise<void> {
    await playerStore.refreshMethodsProgress(lessonId)
  }

  /**
   * Pick a random uncompleted method type for AI Smart-Mix generation.
   * Returns null if all tasks are completed.
   */
  function pickSmartMixMethodType(): number | null {
    const uncompleted = tasks.value.filter((t) => !t.completed)
    if (uncompleted.length === 0) return null

    // Collect unique method types from uncompleted tasks
    const types = [...new Set(uncompleted.map((t) => t.method_type))]
    return types[Math.floor(Math.random() * types.length)]
  }

  // ========================================================================
  // Return
  // ========================================================================

  return {
    tasks,
    completedCount,
    totalCount,
    progressPercentage,

    getMethodIcon,
    getMethodName,
    getDifficultyLabel,

    refreshProgress,
    pickSmartMixMethodType,
  }
}
