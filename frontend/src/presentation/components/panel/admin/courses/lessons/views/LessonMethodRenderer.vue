<!--
  Lesson Method Renderer

  Renders a preview of a learning method's config data.
  Handles LM12 (Math Steps), LM22 (Quiz), LM13 (Flashcards),
  and a generic fallback for all other method types.
-->

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Props {
  methodType: number | string
  config: Record<string, unknown>
}

const props = defineProps<Props>()

const numericType = computed((): number => {
  return typeof props.methodType === 'string'
    ? parseInt(props.methodType, 10)
    : props.methodType
})

const resolvedConfig = computed(() => {
  let cfg = props.config || {}
  if (cfg.raw_content && typeof cfg.raw_content === 'string') {
    try {
      cfg = { ...cfg, ...JSON.parse(cfg.raw_content as string) }
    } catch { /* ignore parse errors */ }
  }
  return cfg as Record<string, unknown>
})

const mathSteps = computed(() => {
  if (numericType.value !== 12) return []
  const cfg = resolvedConfig.value
  return (cfg.steps || cfg.exercises || []) as Array<Record<string, unknown>>
})

const quizQuestions = computed(() => {
  if (numericType.value !== 22) return []
  const cfg = resolvedConfig.value
  return Array.isArray(cfg) ? cfg : ((cfg.questions || []) as Array<Record<string, unknown>>)
})

const flashcards = computed(() => {
  if (numericType.value !== 13) return []
  const cfg = resolvedConfig.value
  return Array.isArray(cfg) ? cfg : ((cfg.cards || []) as Array<Record<string, unknown>>)
})

const isSpecialType = computed(() => [12, 13, 22].includes(numericType.value))

const defaultData = computed(() => {
  if (isSpecialType.value) return null
  const cfg = resolvedConfig.value
  const dataKeys = Array.isArray(cfg) ? ['items'] : Object.keys(cfg)
  const itemCount = Array.isArray(cfg)
    ? cfg.length
    : ((cfg.steps as unknown[])?.length
      || (cfg.questions as unknown[])?.length
      || (cfg.cards as unknown[])?.length
      || (cfg.items as unknown[])?.length
      || 0)
  return {
    dataKeys,
    itemCount,
    json: JSON.stringify(cfg, null, 2).substring(0, 1000)
  }
})

function truncate(text: string | undefined, maxLen: number): string {
  if (!text) return ''
  return text.length > maxLen ? text.substring(0, maxLen) + '...' : text
}
</script>

<template>
  <!-- LM12 - Math Steps -->
  <div v-if="numericType === 12" class="method-preview">
    <template v-if="mathSteps.length > 0">
      <h4>{{ $t('panel.lessons.preview.stepCount', { count: mathSteps.length }) }}</h4>
      <div class="exercises-preview">
        <div
          v-for="(step, i) in mathSteps.slice(0, 3)"
          :key="i"
          class="exercise-item"
        >
          <span class="exercise-label">
            {{ $t('panel.lessons.preview.stepLabel', { n: (step.id as number) || i + 1 }) }}
          </span>
          <span class="exercise-text">
            {{ truncate(
              (step.prompt as string) || (step.question as string) || (step.text as string) || t('panel.lessons.preview.task'),
              150
            ) }}
          </span>
        </div>
      </div>
      <p v-if="mathSteps.length > 3" class="more-hint">
        {{ $t('panel.lessons.preview.moreSteps', { count: mathSteps.length - 3 }) }}
      </p>
    </template>
    <p v-else class="no-content">{{ $t('panel.lessons.preview.noStepsConfigured') }}</p>
  </div>

  <!-- LM22 - Quiz -->
  <div v-else-if="numericType === 22" class="method-preview">
    <template v-if="quizQuestions.length > 0">
      <h4>{{ $t('panel.lessons.preview.questionCount', { count: quizQuestions.length }) }}</h4>
      <div class="questions-preview">
        <div
          v-for="(q, i) in quizQuestions.slice(0, 3)"
          :key="i"
          class="question-item"
        >
          <span class="question-label">
            {{ $t('panel.lessons.preview.questionLabel', { n: i + 1 }) }}
          </span>
          <span class="question-text">
            {{ (q as Record<string, unknown>).question || (q as Record<string, unknown>).text }}
          </span>
          <div v-if="(q as Record<string, unknown>).options" class="answers">
            <div
              v-for="(opt, idx) in ((q as Record<string, unknown>).options as string[])"
              :key="idx"
              class="answer"
              :class="{ correct: (q as Record<string, unknown>).correct_index === idx }"
            >
              {{ opt }}
            </div>
          </div>
          <div v-else-if="(q as Record<string, unknown>).answers" class="answers">
            <div
              v-for="(a, idx) in ((q as Record<string, unknown>).answers as Array<Record<string, unknown>>)"
              :key="idx"
              class="answer"
              :class="{ correct: a.correct }"
            >
              {{ a.text || a }}
            </div>
          </div>
        </div>
      </div>
      <p v-if="quizQuestions.length > 3" class="more-hint">
        {{ $t('panel.lessons.preview.moreQuestions', { count: quizQuestions.length - 3 }) }}
      </p>
    </template>
    <p v-else class="no-content">{{ $t('panel.lessons.preview.noQuestionsConfigured') }}</p>
  </div>

  <!-- LM13 - Flashcards -->
  <div v-else-if="numericType === 13" class="method-preview">
    <template v-if="flashcards.length > 0">
      <h4>{{ $t('panel.lessons.preview.cardCount', { count: flashcards.length }) }}</h4>
      <div class="cards-preview">
        <div
          v-for="(card, i) in flashcards.slice(0, 3)"
          :key="i"
          class="card-item"
        >
          <div class="card-front">
            {{ $t('panel.lessons.preview.cardFront') }}
            {{ truncate(
              (card as Record<string, unknown>).front as string
                || (card as Record<string, unknown>).question as string
                || t('panel.lessons.preview.cardN', { n: i + 1 }),
              80
            ) }}
          </div>
          <div class="card-back">
            {{ $t('panel.lessons.preview.cardBack') }}
            {{ truncate(
              (card as Record<string, unknown>).back as string
                || (card as Record<string, unknown>).answer as string
                || '',
              100
            ) }}
          </div>
        </div>
      </div>
      <p v-if="flashcards.length > 3" class="more-hint">
        {{ $t('panel.lessons.preview.moreCards', { count: flashcards.length - 3 }) }}
      </p>
    </template>
    <p v-else class="no-content">{{ $t('panel.lessons.preview.noCardsConfigured') }}</p>
  </div>

  <!-- Default Renderer -->
  <div v-else-if="defaultData" class="method-preview">
    <template v-if="defaultData.itemCount > 0">
      <h4>{{ $t('panel.lessons.preview.elementCount', { count: defaultData.itemCount }) }}</h4>
      <p class="data-hint">{{ $t('panel.lessons.preview.dataFields', { fields: defaultData.dataKeys.join(', ') }) }}</p>
      <details class="config-details">
        <summary>{{ $t('panel.lessons.preview.showJsonData') }}</summary>
        <pre class="config-json">{{ defaultData.json }}</pre>
      </details>
    </template>
    <template v-else-if="defaultData.dataKeys.length > 0">
      <h4>{{ $t('panel.lessons.preview.configuration') }}</h4>
      <p class="data-hint">{{ $t('panel.lessons.preview.fields', { fields: defaultData.dataKeys.join(', ') }) }}</p>
      <details class="config-details">
        <summary>{{ $t('panel.lessons.preview.showJsonData') }}</summary>
        <pre class="config-json">{{ defaultData.json }}</pre>
      </details>
    </template>
    <p v-else class="no-content">{{ $t('panel.lessons.preview.noConfiguration') }}</p>
  </div>
</template>

<style scoped>
.method-preview { font-size: 0.8125rem; }
.method-preview h4 {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
}
.exercises-preview,
.questions-preview,
.cards-preview {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.exercise-item,
.question-item,
.card-item {
  padding: 0.75rem;
  background: var(--color-surface);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}
.exercise-label,
.question-label {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-bottom: 0.25rem;
}
.exercise-text,
.question-text {
  display: block;
  color: var(--color-text-primary);
}
.answers {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.answer {
  padding: 0.375rem 0.5rem;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  font-size: 0.75rem;
}
.answer.correct {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}
.card-front,
.card-back {
  padding: 0.25rem 0;
  font-size: 0.75rem;
}
.card-front {
  color: var(--color-text-primary);
  font-weight: 500;
}
.card-back { color: var(--color-text-secondary); }
.more-hint {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  text-align: center;
  margin-top: 0.5rem;
}
.no-content {
  color: var(--color-text-tertiary);
  font-style: italic;
}
.config-json {
  padding: 0.75rem;
  background: var(--color-surface);
  border-radius: 0.5rem;
  font-size: 0.6875rem;
  font-family: monospace;
  overflow-x: auto;
  max-height: 200px;
  color: var(--color-text-secondary);
}
.data-hint {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin: 0.25rem 0;
}
.config-details { margin-top: 0.5rem; }
.config-details summary {
  font-size: 0.75rem;
  color: var(--color-primary);
  cursor: pointer;
  user-select: none;
}
.config-details summary:hover { text-decoration: underline; }
</style>
