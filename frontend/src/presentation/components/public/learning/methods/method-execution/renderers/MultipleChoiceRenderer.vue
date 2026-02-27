<template>
  <div class="renderer">
    <div v-for="(q, qi) in questions" :key="qi" class="question-block">
      <div class="q-header">
        <span class="q-number">{{ t('lesson.methodExecution.renderer.multipleChoice.questionOf', { current: qi + 1, total: questions.length }) }}</span>
      </div>
      <div class="q-text" v-html="renderMarkdown(q.question || '')" />
      <div class="options">
        <label
          v-for="(opt, oi) in q.options"
          :key="oi"
          class="option"
          :class="{
            'option--selected': selections[qi]?.has(oi),
            'option--correct': checked && isOptionCorrect(qi, oi),
            'option--wrong': checked && selections[qi]?.has(oi) && !isOptionCorrect(qi, oi)
          }"
        >
          <input
            type="checkbox"
            :checked="selections[qi]?.has(oi)"
            :disabled="checked"
            class="option-check"
            @change="toggleOption(qi, oi)"
          />
          <span class="option-text">{{ opt }}</span>
        </label>
      </div>
    </div>
    <div class="actions">
      <button v-if="!checked" class="check-btn" :disabled="!hasAnySelection" @click="checked = true">{{ t('lesson.methodExecution.renderer.common.check') }}</button>
      <button v-else class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>
    <div v-if="checked" class="score">{{ t('lesson.methodExecution.renderer.multipleChoice.correctCount', { correct: correctCount, total: questions.length }) }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from './markdown'
import type { MultipleChoiceData } from './types'

const { t } = useI18n()
const props = defineProps<{ data: MultipleChoiceData | null; solution: null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const checked = ref(false)
const questions = computed(() => props.data?.questions || [])
const selections = ref<Map<number, Set<number>>>(new Map())

// Initialize selections
questions.value.forEach((_: any, i: number) => {
  selections.value.set(i, new Set())
})

watch(() => props.data, () => reset(), { deep: true })

watch(checked, (val) => {
  if (val) emit('complete', correctCount.value, questions.value.length)
})

const hasAnySelection = computed(() => {
  for (const [, set] of selections.value) {
    if (set.size > 0) return true
  }
  return false
})

const correctCount = computed(() => {
  let count = 0
  questions.value.forEach((q: any, qi: number) => {
    const correctIndices = new Set(q.correctAnswers || [])
    const selected = selections.value.get(qi) || new Set()
    if (selected.size === correctIndices.size && [...selected].every(i => correctIndices.has(i))) {
      count++
    }
  })
  return count
})

function isOptionCorrect(qi: number, oi: number): boolean {
  const q = questions.value[qi]
  return (q.correctAnswers || []).includes(oi)
}

function toggleOption(qi: number, oi: number) {
  const set = selections.value.get(qi) || new Set()
  if (set.has(oi)) set.delete(oi)
  else set.add(oi)
  selections.value.set(qi, new Set(set))
  selections.value = new Map(selections.value)
}

function reset() {
  checked.value = false
  questions.value.forEach((_: any, i: number) => {
    selections.value.set(i, new Set())
  })
  selections.value = new Map(selections.value)
}
</script>

<style scoped>
.question-block {
  margin-bottom: 1.75rem;
  padding-bottom: 1.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.question-block:last-of-type {
  border-bottom: none;
  margin-bottom: 1rem;
}

.q-header {
  margin-bottom: 0.5rem;
}

.q-number {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.q-text {
  font-size: 0.9375rem;
  font-weight: 500;
  margin: 0 0 0.875rem;
  line-height: 1.5;
}

:root.dark .q-text {
  color: var(--color-text-primary);
}

.options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.625rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  background: rgba(255, 255, 255, 0.02);
}

.option:hover:not(.option--correct):not(.option--wrong) {
  border-color: rgba(99, 102, 241, 0.3);
  background: rgba(99, 102, 241, 0.06);
}

.option--selected {
  border-color: rgba(99, 102, 241, 0.4);
  background: rgba(99, 102, 241, 0.08);
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.1);
}

.option--correct {
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.08);
}

.option--wrong {
  border-color: rgba(239, 68, 68, 0.4);
  background: rgba(239, 68, 68, 0.06);
}

.option-check {
  width: 1rem;
  height: 1rem;
  accent-color: var(--color-accent);
  flex-shrink: 0;
}

.option-text {
  flex: 1;
}

:root.dark .option-text {
  color: var(--color-text-primary);
}

.actions {
  display: flex;
  gap: 0.625rem;
  margin-bottom: 0.75rem;
}

.check-btn {
  padding: 0.5rem 1.5rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  transition: all 0.15s;
}

.check-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
  transform: translateY(-1px);
}

.check-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.reset-btn {
  padding: 0.5rem 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  background: rgba(255, 255, 255, 0.04);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.reset-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.12);
}

.score {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-accent-light);
}
</style>
