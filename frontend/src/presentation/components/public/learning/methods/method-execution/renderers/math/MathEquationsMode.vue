<template>
  <div>
    <div v-for="(eq, i) in equations" :key="i" class="equation-card">
      <div class="equation-header">
        <span class="eq-number">{{ i + 1 }}</span>
        <span class="eq-label">{{ t('lesson.methodExecution.renderer.mathInteractive.equationLabel', { n: i + 1 }) }}</span>
      </div>
      <div class="equation-display">{{ eq.equation }}</div>
      <p v-if="eq.variable" class="solve-for">{{ t('lesson.methodExecution.renderer.mathInteractive.solveFor', { variable: eq.variable }) }}</p>
      <div class="answer-row">
        <span class="eq-variable">{{ eq.variable || 'x' }} =</span>
        <input
          v-model="answers[i]"
          type="text"
          class="answer-input answer-input--eq"
          :placeholder="t('lesson.methodExecution.renderer.mathInteractive.result')"
          :disabled="checked"
          :class="{ 'input--correct': checked && isCorrect(i), 'input--wrong': checked && !isCorrect(i) }"
        />
        <span v-if="checked" class="answer-status">{{ isCorrect(i) ? '✓' : '✗' }}</span>
      </div>
      <Transition name="fade">
        <div v-if="checked && !isCorrect(i)" class="correct-answer">
          {{ t('lesson.methodExecution.renderer.mathInteractive.correctAnswer') }}: <strong>{{ eq.solution }}</strong>
        </div>
      </Transition>
      <p v-if="checked && eq.hint" class="explanation">{{ eq.hint }}</p>
    </div>
    <div class="actions">
      <button v-if="!checked" class="check-btn" :disabled="answers.some(a => !a.trim())" @click="checked = true">
        {{ t('lesson.methodExecution.renderer.mathInteractive.checkSolution') }}
      </button>
      <button v-else class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>
    <div v-if="checked" class="score">
      {{ t('lesson.methodExecution.renderer.mathInteractive.score', { correct: correctCount, total: equations.length }) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MathInteractiveData } from '../types'

const { t } = useI18n()
const props = defineProps<{ data: MathInteractiveData | null }>()
const checked = ref(false)
const equations = computed(() => props.data?.equations || [])
const answers = ref<string[]>(equations.value.map(() => ''))

function isCorrect(i: number): boolean {
  return answers.value[i]?.trim().toLowerCase() === String(equations.value[i]?.solution || '').trim().toLowerCase()
}

const correctCount = computed(() => equations.value.filter((_: any, i: number) => isCorrect(i)).length)

function reset() {
  checked.value = false
  answers.value = equations.value.map(() => '')
}
</script>

<style scoped>
.equation-card {
  padding: 1rem 1.125rem;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.75rem;
  margin-bottom: 0.75rem;
}

.equation-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }

.eq-number {
  width: 1.375rem; height: 1.375rem;
  background: rgba(99, 102, 241, 0.15); color: var(--color-accent-light);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.625rem;
}

.eq-label { font-size: 0.75rem; font-weight: 600; color: var(--color-text-secondary); }

.equation-display {
  padding: 0.75rem 1rem; background: var(--color-code-bg);
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.5rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 1.0625rem; color: var(--color-code-text); text-align: center; margin-bottom: 0.625rem;
}

.solve-for { margin: 0 0 0.375rem; font-size: 0.8125rem; color: var(--color-text-tertiary); font-style: italic; }

.answer-row { display: flex; align-items: center; gap: 0.625rem; margin-top: 0.5rem; }

.eq-variable {
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.9375rem; font-weight: 600; color: var(--color-accent-light); flex-shrink: 0;
}

.answer-input {
  flex: 1; padding: 0.5rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 0.5rem;
  font-size: 0.875rem; background: rgba(255, 255, 255, 0.025);
  color: var(--color-text-primary); transition: border-color 0.15s, box-shadow 0.15s;
}
.answer-input:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }
.answer-input:disabled { opacity: 0.6; }
.answer-input--eq { max-width: 160px; font-family: 'Fira Code', 'JetBrains Mono', monospace; text-align: center; }
.input--correct { border-color: rgba(16, 185, 129, 0.4) !important; background: rgba(16, 185, 129, 0.08); color: var(--color-success); }
.input--wrong { border-color: rgba(239, 68, 68, 0.4) !important; background: rgba(239, 68, 68, 0.08); color: var(--color-error); }

.answer-status { font-weight: 700; font-size: 1rem; width: 1.5rem; text-align: center; }
.input--correct ~ .answer-status { color: var(--color-success); }
.input--wrong ~ .answer-status { color: var(--color-error); }

.correct-answer {
  margin-top: 0.375rem; font-size: 0.8125rem; color: var(--color-text-secondary);
  padding: 0.375rem 0.625rem; background: rgba(16, 185, 129, 0.04);
  border-radius: 0.375rem; border-left: 2px solid rgba(16, 185, 129, 0.3);
}
.correct-answer strong { color: var(--color-success); }

.explanation {
  margin: 0.5rem 0 0; font-size: 0.8125rem; color: var(--color-text-secondary);
  font-style: italic; padding-left: 0.75rem;
  border-left: 2px solid rgba(99, 102, 241, 0.2);
}

.actions { display: flex; gap: 0.75rem; margin-top: 1.25rem; margin-bottom: 0.75rem; }

.check-btn {
  padding: 0.5rem 1.5rem; background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; border: none; border-radius: 0.5rem;
  font-size: 0.8125rem; font-weight: 600; cursor: pointer;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25); transition: all 0.15s;
}
.check-btn:hover:not(:disabled) { box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35); transform: translateY(-1px); }
.check-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.reset-btn {
  padding: 0.5rem 1.25rem; border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem; font-size: 0.8125rem;
  background: rgba(255, 255, 255, 0.04); color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s;
}
.reset-btn:hover { background: rgba(255, 255, 255, 0.08); }

.score { font-size: 1rem; font-weight: 700; color: var(--color-accent-light); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
