<template>
  <div class="renderer">
    <div v-if="taskText" class="task-text" v-html="renderMarkdown(taskText)" />

    <!-- Step Progress -->
    <div class="step-progress">
      <div v-for="(s, i) in steps" :key="i" class="step-dot" :class="{ 'dot--done': i < currentStep, 'dot--active': i === currentStep, 'dot--locked': i > currentStep }" />
    </div>

    <!-- Current Step -->
    <div v-if="steps.length" class="step-card">
      <div class="step-header">
        <span class="step-badge">{{ t('lesson.methodExecution.renderer.multiStepExam.stepOf', { current: currentStep + 1, total: steps.length }) }}</span>
        <span v-if="currentStepData.points" class="step-points">{{ currentStepData.points }} {{ t('lesson.methodExecution.renderer.multiStepExam.points') }}</span>
      </div>
      <h4 class="step-title">{{ currentStepData.title || t('lesson.methodExecution.renderer.multiStepExam.stepLabel', { n: currentStep + 1 }) }}</h4>
      <div v-if="currentStepData.description" class="step-desc" v-html="renderMarkdown(currentStepData.description)" />

      <!-- Step Input -->
      <textarea
        v-model="answers[currentStep]"
        class="step-input"
        :rows="currentStepData.inputRows || 4"
        :placeholder="t('lesson.methodExecution.renderer.multiStepExam.answerPlaceholder')"
        :disabled="checked"
      />

      <!-- Feedback after check -->
      <Transition name="fade">
        <div v-if="checked && currentStepData.expectedAnswer" class="step-feedback" :class="isCurrentCorrect ? 'feedback--correct' : 'feedback--wrong'">
          <span class="feedback-icon">{{ isCurrentCorrect ? '✓' : '✗' }}</span>
          <div>
            <p class="feedback-label">{{ t('lesson.methodExecution.renderer.multiStepExam.expectedAnswer') }}:</p>
            <p class="feedback-text">{{ currentStepData.expectedAnswer }}</p>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Navigation -->
    <div class="step-nav">
      <button v-if="currentStep > 0" class="nav-btn nav-btn--back" @click="currentStep--">
        &larr; {{ t('lesson.methodExecution.renderer.stepByStep.back') }}
      </button>
      <div class="nav-spacer" />
      <button v-if="!checked && currentStep < steps.length - 1" class="nav-btn nav-btn--next" :disabled="!answers[currentStep]?.trim()" @click="currentStep++">
        {{ t('lesson.methodExecution.renderer.stepByStep.next') }} &rarr;
      </button>
      <button v-if="!checked && currentStep === steps.length - 1" class="nav-btn nav-btn--submit" :disabled="answers.some(a => !a.trim())" @click="checked = true">
        {{ t('lesson.methodExecution.renderer.multiStepExam.submit') }}
      </button>
      <button v-if="checked" class="nav-btn nav-btn--reset" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>

    <!-- Score -->
    <Transition name="fade">
      <div v-if="checked" class="score-box">
        <span class="score-value">{{ correctCount }}/{{ steps.length }}</span>
        <span class="score-label">{{ t('lesson.methodExecution.renderer.multiStepExam.stepsCorrect') }}</span>
      </div>
    </Transition>

    <!-- Solution -->
    <button v-if="solution" class="solution-btn" @click="showSolution = !showSolution">
      {{ showSolution ? t('lesson.methodExecution.renderer.common.hideSolution') : t('lesson.methodExecution.renderer.common.sampleSolution') }}
    </button>
    <Transition name="fade">
      <div v-if="showSolution && solution" class="solution-box">
        <div v-if="solution.steps" class="sol-steps">
          <div v-for="(ss, i) in solution.steps" :key="i" class="sol-step">
            <span class="sol-step-num">{{ i + 1 }}</span>
            <p class="sol-step-text">{{ ss }}</p>
          </div>
        </div>
        <p v-if="solution.explanation" class="sol-explanation">{{ solution.explanation }}</p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from './markdown'
import type { MultiStepExamData, MultiStepExamSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: MultiStepExamData | null; solution: MultiStepExamSolution | null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const showSolution = ref(false)
const checked = ref(false)
const currentStep = ref(0)

const taskText = computed(() => props.data?.task || props.data?.description || '')
const steps = computed(() => props.data?.steps || [])
const answers = ref<string[]>(steps.value.map(() => ''))

watch(() => props.data, () => reset(), { deep: true })

watch(checked, (val) => {
  if (val) emit('complete', correctCount.value, steps.value.length)
})

const currentStepData = computed(() => steps.value[currentStep.value] || {})
const isCurrentCorrect = computed(() => {
  const expected = currentStepData.value.expectedAnswer
  if (!expected) return true
  return answers.value[currentStep.value]?.trim().toLowerCase() === String(expected).trim().toLowerCase()
})

const correctCount = computed(() =>
  steps.value.filter((_: any, i: number) => {
    const expected = steps.value[i]?.expectedAnswer
    if (!expected) return true
    return answers.value[i]?.trim().toLowerCase() === String(expected).trim().toLowerCase()
  }).length
)

function reset() {
  checked.value = false
  currentStep.value = 0
  answers.value = steps.value.map(() => '')
}
</script>

<style scoped>
.task-text { font-size: 0.9375rem; line-height: 1.75; margin-bottom: 1.25rem; color: var(--color-text-primary); }

.step-progress {
  display: flex; align-items: center; gap: 0.375rem;
  margin-bottom: 1.25rem; justify-content: center;
}

.step-dot {
  width: 0.5rem; height: 0.5rem; border-radius: 50%;
  background: rgba(255, 255, 255, 0.1); transition: all 0.3s;
}
.dot--done { background: var(--color-success); }
.dot--active { background: var(--color-accent-light); width: 0.75rem; height: 0.75rem; box-shadow: 0 0 8px rgba(165, 180, 252, 0.4); }
.dot--locked { background: rgba(255, 255, 255, 0.06); }

.step-card {
  padding: 1.25rem; background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.75rem;
  margin-bottom: 1rem;
}

.step-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.625rem; }
.step-badge {
  font-size: 0.6875rem; font-weight: 600; color: var(--color-accent-light);
  text-transform: uppercase; letter-spacing: 0.06em;
}
.step-points { font-size: 0.75rem; color: var(--color-warning); font-weight: 600; }

.step-title { font-size: 1rem; font-weight: 600; color: var(--color-text-primary); margin: 0 0 0.375rem; }
.step-desc { font-size: 0.8125rem; color: var(--color-text-secondary); margin: 0 0 0.75rem; line-height: 1.6; }

.step-input {
  width: 100%; padding: 0.75rem; border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem; font-size: 0.875rem; resize: vertical;
  background: rgba(255, 255, 255, 0.025); color: var(--color-text-primary);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.step-input:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }
.step-input:disabled { opacity: 0.6; }

.step-feedback {
  display: flex; align-items: flex-start; gap: 0.625rem;
  margin-top: 0.75rem; padding: 0.75rem; border-radius: 0.5rem;
}
.feedback--correct { background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.2); }
.feedback--wrong { background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); }
.feedback-icon { font-weight: 700; font-size: 1rem; }
.feedback--correct .feedback-icon { color: var(--color-success); }
.feedback--wrong .feedback-icon { color: var(--color-error); }
.feedback-label { margin: 0; font-size: 0.75rem; color: var(--color-text-tertiary); }
.feedback-text { margin: 0.125rem 0 0; font-size: 0.8125rem; color: var(--color-text-primary); }

.step-nav { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.nav-spacer { flex: 1; }

.nav-btn {
  padding: 0.5rem 1.25rem; border-radius: 0.5rem;
  font-size: 0.8125rem; font-weight: 500; cursor: pointer; transition: all 0.15s;
}
.nav-btn--back { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); color: var(--color-text-secondary); }
.nav-btn--back:hover { background: rgba(255, 255, 255, 0.08); }
.nav-btn--next { background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); color: var(--color-accent-light); }
.nav-btn--next:hover:not(:disabled) { background: rgba(99, 102, 241, 0.15); }
.nav-btn--submit {
  background: linear-gradient(135deg, #6366f1, #4f46e5); border: none; color: #fff; font-weight: 600;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}
.nav-btn--submit:hover:not(:disabled) { box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35); transform: translateY(-1px); }
.nav-btn--reset { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); color: var(--color-text-secondary); }
.nav-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.score-box {
  display: flex; align-items: baseline; gap: 0.5rem;
  padding: 0.875rem 1rem; background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 0.625rem;
  margin-bottom: 1rem;
}
.score-value { font-size: 1.375rem; font-weight: 700; color: var(--color-accent-light); }
.score-label { font-size: 0.8125rem; color: var(--color-text-secondary); }

.solution-btn {
  padding: 0.5rem 1.25rem; background: rgba(16, 185, 129, 0.06); color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 0.5rem;
  font-size: 0.8125rem; font-weight: 500; cursor: pointer; transition: all 0.15s;
}
.solution-btn:hover { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); }

.solution-box {
  margin-top: 1rem; padding: 1rem 1.125rem; background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.15); border-radius: 0.625rem;
}
.sol-steps { display: flex; flex-direction: column; gap: 0.5rem; }
.sol-step { display: flex; align-items: flex-start; gap: 0.625rem; }
.sol-step-num {
  width: 1.25rem; height: 1.25rem; background: rgba(16, 185, 129, 0.15); color: var(--color-success);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 0.625rem; font-weight: 700; flex-shrink: 0;
}
.sol-step-text { margin: 0; font-size: 0.8125rem; color: var(--color-text-primary); line-height: 1.6; }
.sol-explanation { margin: 0.75rem 0 0; font-size: 0.8125rem; color: var(--color-text-secondary); font-style: italic; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
