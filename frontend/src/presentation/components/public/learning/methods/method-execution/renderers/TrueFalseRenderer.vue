<template>
  <div class="renderer">
    <div v-for="(stmt, i) in statements" :key="i" class="statement-card" :class="{ 'stmt--correct': checked && isCorrect(i), 'stmt--wrong': checked && answers[i] !== null && !isCorrect(i) }">
      <div class="stmt-header">
        <span class="stmt-number">{{ t('lesson.methodExecution.renderer.trueFalse.statementOf', { current: i + 1, total: statements.length }) }}</span>
      </div>
      <p class="stmt-text">{{ stmt.statement }}</p>
      <div class="stmt-buttons">
        <button
          class="tf-btn tf-btn--true"
          :class="{ 'tf-btn--active': answers[i] === true }"
          :disabled="checked"
          @click="answers[i] = true; answers = [...answers]"
        >{{ t('lesson.methodExecution.renderer.trueFalse.true') }}</button>
        <button
          class="tf-btn tf-btn--false"
          :class="{ 'tf-btn--active': answers[i] === false }"
          :disabled="checked"
          @click="answers[i] = false; answers = [...answers]"
        >{{ t('lesson.methodExecution.renderer.trueFalse.false') }}</button>
      </div>
      <Transition name="fade">
        <p v-if="checked && stmt.explanation" class="stmt-explanation">
          <strong>{{ t('lesson.methodExecution.renderer.trueFalse.explanation') }}:</strong> {{ stmt.explanation }}
        </p>
      </Transition>
    </div>
    <div class="actions">
      <button v-if="!checked" class="check-btn" :disabled="answers.some(a => a === null)" @click="checked = true">{{ t('lesson.methodExecution.renderer.common.check') }}</button>
      <button v-else class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>
    <div v-if="checked" class="score">{{ t('lesson.methodExecution.renderer.trueFalse.correctCount', { correct: correctCount, total: statements.length }) }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TrueFalseData } from './types'

const { t } = useI18n()
const props = defineProps<{ data: TrueFalseData | null; solution: null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const checked = ref(false)
const statements = computed(() => props.data?.statements || [])
const answers = ref<(boolean | null)[]>(statements.value.map(() => null))

watch(() => props.data, () => reset(), { deep: true })

const correctCount = computed(() =>
  statements.value.filter((s: any, i: number) => answers.value[i] === s.isTrue).length
)

watch(checked, (val) => {
  if (val) emit('complete', correctCount.value, statements.value.length)
})

function isCorrect(i: number): boolean {
  return answers.value[i] === statements.value[i]?.isTrue
}

function reset() {
  checked.value = false
  answers.value = statements.value.map(() => null)
}
</script>

<style scoped>
.statement-card {
  padding: 1rem 1.125rem;
  margin-bottom: 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.625rem;
  transition: all 0.25s ease;
}

.stmt--correct {
  border-color: rgba(16, 185, 129, 0.35);
  background: rgba(16, 185, 129, 0.06);
}

.stmt--wrong {
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.05);
}

.stmt-header {
  margin-bottom: 0.375rem;
}

.stmt-number {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.stmt-text {
  font-size: 0.9375rem;
  line-height: 1.55;
  margin: 0 0 0.75rem;
}

:root.dark .stmt-text {
  color: var(--color-text-primary);
}

.stmt-buttons {
  display: flex;
  gap: 0.5rem;
}

.tf-btn {
  padding: 0.4375rem 1.125rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: var(--color-text-primary);
  transition: all 0.2s ease;
}

.tf-btn:hover:not(:disabled):not(.tf-btn--active) {
  border-color: rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.06);
}

.tf-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.tf-btn--true.tf-btn--active {
  background: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.4);
  color: var(--color-success);
  font-weight: 600;
}

.tf-btn--false.tf-btn--active {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.35);
  color: var(--color-error);
  font-weight: 600;
}

.stmt-explanation {
  margin: 0.75rem 0 0;
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  font-style: italic;
  line-height: 1.55;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 0.375rem;
  border-left: 2px solid rgba(99, 102, 241, 0.3);
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
}

.score {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-accent-light);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
