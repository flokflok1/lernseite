// Method Execution Components (Barrel Export)
// Re-exports from base/learning/methods/method-execution/ (DDD migration)

export { default as MethodCardList } from './MethodCardList.vue'
export { default as TaskStatsPanel } from './TaskStatsPanel.vue'
export { default as TokenBalanceDisplay } from './TokenBalanceDisplay.vue'
export { default as TaskProgressHeader } from './TaskProgressHeader.vue'
export { default as TaskPracticeList } from './TaskPracticeList.vue'
export { default as TaskContentPanel } from './TaskContentPanel.vue'

// Method Execution Composables
export { useMethodExecution, type GeneratedTask, type MethodMetadata } from './composables'
export { useTaskPractice, type TaskWithProgress } from './composables'
