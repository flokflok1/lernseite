<template>
  <div class="method-execution-panel">
    <!-- 1. Progress Header -->
    <TaskProgressHeader
      :completed="completedCount"
      :total="totalCount"
      :percentage="progressPercentage"
    />

    <!-- 2. Task Practice List (PRIMARY) -->
    <TaskPracticeList
      :tasks="tasks"
      :active-task-id="activeTaskId"
      :get-icon="getMethodIcon"
      :get-name="getMethodName"
      @open="handleOpenTask"
    />

    <!-- 3. AI Smart-Mix (SECONDARY, bottom) -->
    <div class="ai-section">
      <button
        @click="handleAiGenerate"
        :disabled="isGenerating || !smartMixPreview"
        class="ai-generate-btn"
      >
        <span v-if="isGenerating" class="spinner-sm" />
        <span v-else-if="smartMixPreview">{{ $t('lesson.methodExecution.aiGenerate') }}: {{ smartMixPreview }}</span>
        <span v-else>{{ $t('lesson.methodExecution.allCompleted') }}</span>
      </button>
      <p class="ai-hint">{{ $t('lesson.methodExecution.aiGenerateHint') }}</p>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isGenerating" class="loading-overlay">
      <div class="loading-box">
        <div class="loading-spinner" />
        <p class="loading-title">{{ $t('lesson.methodExecution.generating') }}</p>
        <p class="loading-hint">{{ $t('lesson.methodExecution.generatingHint') }}</p>
      </div>
    </div>

    <!-- Error Bar -->
    <Transition name="slide-up">
      <div v-if="errorMessage" class="error-bar">
        <span>{{ errorMessage }}</span>
        <button @click="errorMessage = null" class="error-close">&times;</button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
/**
 * MethodExecutionPanel (Redesigned)
 * ==================================
 * Shows editor-created tasks as a practice list (primary).
 * AI generation is a small secondary feature at the bottom.
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePlayerStore } from '@/application/stores/modules/content/player.store'
import {
  TaskProgressHeader,
  TaskPracticeList,
  useTaskPractice,
  useMethodExecution,
} from '@/presentation/components/public/learning/methods/method-execution'

// ============================================================================
// Props
// ============================================================================

interface Props {
  lessonId: string | number
  methods: any[]
}

const props = defineProps<Props>()
const { t } = useI18n()
const playerStore = usePlayerStore()

// ============================================================================
// Composables
// ============================================================================

const {
  tasks,
  completedCount,
  totalCount,
  progressPercentage,
  getMethodIcon,
  getMethodName,
  pickSmartMixMethodType,
  refreshProgress,
} = useTaskPractice(String(props.lessonId))

const {
  isExecuting: isGenerating,
  generateTask,
} = useMethodExecution(String(props.lessonId))

// ============================================================================
// State
// ============================================================================

const activeTaskId = ref<string | number | null>(null)
const errorMessage = ref<string | null>(null)

const smartMixPreview = computed(() => {
  const type = pickSmartMixMethodType()
  if (type === null) return null
  return getMethodName(type)
})

// ============================================================================
// Handlers
// ============================================================================

function handleOpenTask(methodId: string | number): void {
  activeTaskId.value = methodId

  // Find the method in the store and start a runner session
  const method = playerStore.availableMethods.find(
    (m: any) => String(m.method_id) === String(methodId)
  )
  if (method) {
    playerStore.executeLearningMethod({
      lesson_id: String(props.lessonId),
      method_id: method.method_id,
    }).then(() => {
      refreshProgress()
    }).catch((err: any) => {
      errorMessage.value = err?.message || t('lesson.methodExecution.generating')
      setTimeout(() => { errorMessage.value = null }, 5000)
    })
  }
}

async function handleAiGenerate(): Promise<void> {
  const methodType = pickSmartMixMethodType()
  if (methodType === null) return

  // Find a method instance of this type to use for generation
  const method = playerStore.availableMethods.find(
    (m: any) => m.method_type === methodType
  )
  if (!method) return

  errorMessage.value = null
  try {
    await generateTask(method as any)
    await refreshProgress()
  } catch (err: any) {
    errorMessage.value = err?.message || t('lesson.methodPanel.errors.generating')
    setTimeout(() => { errorMessage.value = null }, 5000)
  }
}
</script>

<style scoped>
/* Panel Layout */
.method-execution-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* AI Section */
.ai-section {
  padding: 0.625rem 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  flex-shrink: 0;
}

.ai-generate-btn {
  width: 100%;
  padding: 0.4375rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #64748b;
  background-color: transparent;
  border: 1px dashed rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
}

.ai-generate-btn:hover:not(:disabled) {
  border-color: rgba(99, 102, 241, 0.3);
  color: #a5b4fc;
  background: rgba(99, 102, 241, 0.04);
}

.ai-generate-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.ai-hint {
  font-size: 0.625rem;
  color: #475569;
  margin: 0.25rem 0 0;
  text-align: center;
}

/* Spinner */
.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid var(--color-border, #e5e7eb);
  border-top-color: var(--color-primary, #3b82f6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
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
  to { transform: rotate(360deg); }
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
