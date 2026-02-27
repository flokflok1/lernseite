<template>
  <div class="task-content-panel">
    <!-- Back Button -->
    <button class="back-btn" @click="$emit('close')">
      <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      {{ $t('lesson.methodExecution.backToLesson') }}
    </button>

    <!-- Task Header -->
    <div class="task-header">
      <span class="task-type-badge">{{ methodTypeName }}</span>
      <h2 class="task-title">{{ execution.title }}</h2>
    </div>

    <!-- Instructions -->
    <div v-if="execution.instructions" class="task-section">
      <h3 class="section-title">{{ $t('lesson.methodExecution.instructions') }}</h3>
      <div class="section-content" v-html="sanitizedInstructions" />
    </div>

    <!-- Dynamic Renderer -->
    <div v-if="hasContent" class="task-section">
      <component
        :is="rendererComponent"
        :data="execution.data"
        :solution="execution.solution"
        @complete="(score: number, maxScore: number) => $emit('complete', score, maxScore)"
      />
    </div>

    <!-- Empty State -->
    <div v-if="!execution.instructions && !hasContent" class="empty-state">
      <p class="empty-text">{{ $t('lesson.methodExecution.noContent') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
import {
  DeepExplanationRenderer,
  StepByStepRenderer,
  InteractiveTheoryRenderer,
  DiagramRenderer,
  ScenarioRenderer,
  MathInteractiveRenderer,
  FlashcardsRenderer,
  DragDropRenderer,
  ClozeRenderer,
  FreeTextRenderer,
  MultipleChoiceRenderer,
  TrueFalseRenderer,
  WhiteboardRenderer,
  HandsOnLabRenderer,
  MultiStepExamRenderer,
  TimeLimitRenderer,
  ComprehensionCheckRenderer,
  OralExplanationRenderer,
  ChapterExamRenderer,
} from './renderers'

interface Props {
  execution: {
    title: string
    instructions?: string
    data?: any
    solution?: any
    method_type?: number
    difficulty?: string
  }
}

const props = defineProps<Props>()
defineEmits<{ close: []; complete: [score: number, maxScore: number] }>()
const { t } = useI18n()

// Maps method_type codes (from DB) to renderer components
// Core types: 0-11, Extension types: 100+
const RENDERER_MAP: Record<number, Component> = {
  // Core content methods (0-11, from learning_method_types)
  0: DeepExplanationRenderer,
  1: StepByStepRenderer,
  2: InteractiveTheoryRenderer,
  3: DiagramRenderer,
  4: ScenarioRenderer,
  5: MathInteractiveRenderer,
  6: FlashcardsRenderer,
  7: DragDropRenderer,
  8: ClozeRenderer,
  9: FreeTextRenderer,
  10: MultipleChoiceRenderer,
  11: MultiStepExamRenderer,
  // Extension methods (100+)
  100: WhiteboardRenderer,
  101: HandsOnLabRenderer,
  102: TimeLimitRenderer,
  103: TrueFalseRenderer,
  104: ComprehensionCheckRenderer,
  105: OralExplanationRenderer,
  106: ChapterExamRenderer,
}

const rendererComponent = computed(() =>
  RENDERER_MAP[props.execution.method_type ?? -1] || DeepExplanationRenderer
)

// Maps method_type codes to i18n keys for display names
const METHOD_TYPE_KEYS: Record<number, string> = {
  0: 'lm00', 1: 'lm01', 2: 'lm02', 3: 'lm03', 4: 'lm04', 5: 'lm05',
  6: 'lm06', 7: 'lm07', 8: 'lm08', 9: 'lm09', 10: 'lm10', 11: 'lm11',
  100: 'lm100', 101: 'lm101', 102: 'lm102', 103: 'lm103',
  104: 'lm104', 105: 'lm105', 106: 'lm106',
}

const methodTypeName = computed(() => {
  const key = METHOD_TYPE_KEYS[props.execution.method_type ?? -1]
  return key ? t(`lesson.methodExecution.methods.${key}`) : t('lesson.methodExecution.taskContent')
})

const hasContent = computed(() => {
  const d = props.execution.data
  if (!d) return false
  if (typeof d === 'object') return Object.keys(d).length > 0
  return true
})

const sanitizedInstructions = computed(() =>
  DOMPurify.sanitize(props.execution.instructions || '', {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'h3', 'h4', 'code', 'pre'],
    ALLOWED_ATTR: ['href', 'title']
  })
)
</script>

<style scoped>
.task-content-panel {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.25rem 2rem 3rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 1.25rem;
  margin-left: -0.375rem;
}

.back-btn:hover {
  color: var(--color-primary, #6366f1);
  background: rgba(99, 102, 241, 0.06);
}

:root.dark .back-btn:hover {
  background: rgba(99, 102, 241, 0.1);
}

.back-icon {
  width: 14px;
  height: 14px;
}

.task-header {
  margin-bottom: 1.75rem;
}

.task-type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #a5b4fc;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(139, 92, 246, 0.12));
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: 999px;
  margin-bottom: 0.625rem;
}

.task-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  margin: 0;
  line-height: 1.35;
}

:root.dark .task-title {
  color: #f1f5f9;
}

.task-section {
  margin-bottom: 1.75rem;
}

.section-title {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-secondary, #6b7280);
  margin: 0 0 0.5rem;
}

:root.dark .section-title {
  color: #64748b;
}

.section-content {
  padding: 0.875rem 1.125rem;
  background-color: var(--color-surface-secondary, #f9fafb);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.625rem;
  font-size: 0.875rem;
  line-height: 1.65;
  color: var(--color-text-primary, #111827);
}

:root.dark .section-content {
  background-color: rgba(255, 255, 255, 0.025);
  border-color: rgba(255, 255, 255, 0.06);
  color: #cbd5e1;
}

.empty-state {
  padding: 3rem 2rem;
  text-align: center;
}

.empty-text {
  color: var(--color-text-secondary, #6b7280);
  font-size: 0.9375rem;
}
</style>
