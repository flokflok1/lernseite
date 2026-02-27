<template>
  <div>
    <p v-if="taskText" class="task-text">{{ taskText }}</p>
    <div v-if="formula" class="formula-display">{{ formula }}</div>
    <div class="steps-list">
      <div
        v-for="(s, i) in steps" :key="i"
        class="step-card"
        :class="{ 'step--locked': i > currentStep && !checked, 'step--active': i === currentStep && !checked }"
      >
        <div class="step-header">
          <span class="step-number">{{ i + 1 }}</span>
          <span class="step-label">{{ s.label || t('lesson.methodExecution.renderer.mathInteractive.stepLabel', { n: i + 1 }) }}</span>
        </div>
        <p v-if="s.instruction" class="step-instruction">{{ s.instruction }}</p>
        <input
          v-model="answers[i]"
          type="text"
          class="answer-input"
          :placeholder="t('lesson.methodExecution.renderer.mathInteractive.stepInstruction')"
          :disabled="checked || i > currentStep"
          :class="{ 'input--correct': checked && isCorrect(i), 'input--wrong': checked && !isCorrect(i) }"
          @keyup.enter="i === currentStep && answers[i].trim() && advance()"
        />
        <Transition name="fade">
          <div v-if="checked && !isCorrect(i)" class="correct-answer">
            {{ t('lesson.methodExecution.renderer.mathInteractive.correctAnswer') }}: <strong>{{ s.solution }}</strong>
          </div>
        </Transition>
      </div>
    </div>
    <div class="actions">
      <button v-if="!checked && currentStep < steps.length - 1" class="advance-btn" :disabled="!answers[currentStep]?.trim()" @click="advance">
        {{ t('lesson.methodExecution.renderer.stepByStep.next') }} &rarr;
      </button>
      <button v-if="!checked && currentStep === steps.length - 1" class="check-btn" :disabled="answers.some(a => !a.trim())" @click="checked = true">
        {{ t('lesson.methodExecution.renderer.mathInteractive.checkSolution') }}
      </button>
      <button v-if="checked" class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>
    <div v-if="checked" class="score">
      {{ t('lesson.methodExecution.renderer.mathInteractive.score', { correct: correctCount, total: steps.length }) }}
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
const currentStep = ref(0)
const steps = computed(() => props.data?.steps || [])
const taskText = computed(() => props.data?.task || '')
const formula = computed(() => props.data?.formula || '')
const answers = ref<string[]>(steps.value.map(() => ''))

function isCorrect(i: number): boolean {
  return answers.value[i]?.trim().toLowerCase() === String(steps.value[i]?.solution || '').trim().toLowerCase()
}

const correctCount = computed(() => steps.value.filter((_: any, i: number) => isCorrect(i)).length)

function advance() {
  if (currentStep.value < steps.value.length - 1) currentStep.value++
}

function reset() {
  checked.value = false
  currentStep.value = 0
  answers.value = steps.value.map(() => '')
}
</script>

<style scoped>
.task-text { font-size: 0.9375rem; line-height: 1.75; margin-bottom: 1.25rem; color: var(--color-text-primary); }

.formula-display {
  padding: 1rem 1.25rem; background: var(--color-code-bg);
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.625rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 1.125rem; color: var(--color-accent-light); text-align: center; margin-bottom: 1rem;
}

.steps-list { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0.5rem; }

.step-card {
  padding: 0.875rem 1rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.625rem;
  transition: all 0.25s ease;
}

.step--active {
  border-color: rgba(99, 102, 241, 0.25);
  background: rgba(99, 102, 241, 0.04);
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.08);
}

.step--locked { opacity: 0.4; pointer-events: none; }

.step-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.375rem; }

.step-number {
  width: 1.375rem; height: 1.375rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.625rem;
}

.step--locked .step-number { background: rgba(255, 255, 255, 0.08); color: var(--color-text-tertiary); }

.step-label { font-size: 0.8125rem; font-weight: 600; color: var(--color-text-primary); }

.step-instruction { margin: 0 0 0.5rem; font-size: 0.8125rem; color: var(--color-text-secondary); }

.answer-input {
  width: 100%; padding: 0.5rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 0.5rem;
  font-size: 0.875rem; background: rgba(255, 255, 255, 0.025);
  color: var(--color-text-primary); transition: border-color 0.15s, box-shadow 0.15s;
}
.answer-input:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }
.answer-input:disabled { opacity: 0.6; }
.input--correct { border-color: rgba(16, 185, 129, 0.4) !important; background: rgba(16, 185, 129, 0.08); color: var(--color-success); }
.input--wrong { border-color: rgba(239, 68, 68, 0.4) !important; background: rgba(239, 68, 68, 0.08); color: var(--color-error); }

.correct-answer {
  margin-top: 0.375rem; font-size: 0.8125rem; color: var(--color-text-secondary);
  padding: 0.375rem 0.625rem; background: rgba(16, 185, 129, 0.04);
  border-radius: 0.375rem; border-left: 2px solid rgba(16, 185, 129, 0.3);
}
.correct-answer strong { color: var(--color-success); }

.actions { display: flex; gap: 0.75rem; margin-top: 1.25rem; margin-bottom: 0.75rem; }

.advance-btn {
  padding: 0.5rem 1.25rem; background: rgba(99, 102, 241, 0.1);
  color: var(--color-accent-light); border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 0.5rem; font-size: 0.8125rem; font-weight: 500;
  cursor: pointer; transition: all 0.15s;
}
.advance-btn:hover:not(:disabled) { background: rgba(99, 102, 241, 0.15); border-color: rgba(99, 102, 241, 0.3); }
.advance-btn:disabled { opacity: 0.35; cursor: not-allowed; }

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
