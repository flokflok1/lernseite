<template>
  <div class="renderer">
    <p v-if="taskText" class="task-text">{{ taskText }}</p>

    <!-- Timer Display -->
    <div class="timer-bar" :class="{ 'timer--warning': timePercent < 25, 'timer--danger': timePercent < 10 }">
      <div class="timer-fill" :style="{ width: `${timePercent}%` }" />
      <span class="timer-label">{{ formattedTime }}</span>
    </div>

    <!-- Questions -->
    <div class="questions-list">
      <div v-for="(q, i) in questions" :key="i" class="question-card" :class="{ 'q--answered': answers[i]?.trim() }">
        <div class="q-header">
          <span class="q-number">{{ i + 1 }}</span>
          <span class="q-text">{{ q.question || q.text }}</span>
        </div>
        <input
          v-model="answers[i]"
          type="text"
          class="q-input"
          :placeholder="t('lesson.methodExecution.renderer.timeLimit.answerPlaceholder')"
          :disabled="finished"
          @keyup.enter="i < questions.length - 1 ? focusNext(i) : undefined"
        />
        <Transition name="fade">
          <div v-if="finished && q.answer" class="q-feedback" :class="isCorrect(i) ? 'fb--correct' : 'fb--wrong'">
            <span class="fb-icon">{{ isCorrect(i) ? '✓' : '✗' }}</span>
            <span class="fb-text">{{ q.answer }}</span>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Controls -->
    <div class="controls">
      <button v-if="!started && !finished" class="start-btn" @click="startTimer">
        {{ t('lesson.methodExecution.renderer.timeLimit.start') }}
      </button>
      <button v-if="started && !finished" class="submit-btn" :disabled="answers.every(a => !a.trim())" @click="finish">
        {{ t('lesson.methodExecution.renderer.timeLimit.submitEarly') }}
      </button>
      <button v-if="finished" class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>

    <!-- Score -->
    <Transition name="fade">
      <div v-if="finished" class="score-box">
        <span class="score-value">{{ correctCount }}/{{ questions.length }}</span>
        <span class="score-label">{{ t('lesson.methodExecution.renderer.common.correct') }}</span>
        <span v-if="!timeUp" class="time-bonus">{{ t('lesson.methodExecution.renderer.timeLimit.timeRemaining') }}: {{ formattedTime }}</span>
        <span v-else class="time-up">{{ t('lesson.methodExecution.renderer.timeLimit.timeUp') }}</span>
      </div>
    </Transition>

    <!-- Solution -->
    <button v-if="solution" class="solution-btn" @click="showSolution = !showSolution">
      {{ showSolution ? t('lesson.methodExecution.renderer.common.hideSolution') : t('lesson.methodExecution.renderer.common.sampleSolution') }}
    </button>
    <Transition name="fade">
      <div v-if="showSolution && solution" class="solution-box">
        <p v-if="solution.explanation" class="sol-explanation">{{ solution.explanation }}</p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TimeLimitData, TimeLimitSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: TimeLimitData | null; solution: TimeLimitSolution | null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const showSolution = ref(false)

const taskText = computed(() => props.data?.task || props.data?.description || '')
const questions = computed(() => props.data?.questions || [])
const timeLimitSec = computed(() => (props.data?.timeLimitMinutes || 5) * 60)

const answers = ref<string[]>(questions.value.map(() => ''))
const started = ref(false)
const finished = ref(false)
const timeUp = ref(false)
const remaining = ref(timeLimitSec.value)
let timer: ReturnType<typeof setInterval> | null = null

watch(() => props.data, () => reset(), { deep: true })

const timePercent = computed(() => (remaining.value / timeLimitSec.value) * 100)
const formattedTime = computed(() => {
  const m = Math.floor(remaining.value / 60)
  const s = remaining.value % 60
  return `${m}:${String(s).padStart(2, '0')}`
})

function startTimer() {
  started.value = true
  timer = setInterval(() => {
    remaining.value--
    if (remaining.value <= 0) {
      timeUp.value = true
      finish()
    }
  }, 1000)
}

function finish() {
  finished.value = true
  if (timer) { clearInterval(timer); timer = null }
  emit('complete', correctCount.value, questions.value.length)
}

function isCorrect(i: number): boolean {
  const expected = questions.value[i]?.answer
  if (!expected) return true
  return answers.value[i]?.trim().toLowerCase() === String(expected).trim().toLowerCase()
}

const correctCount = computed(() => questions.value.filter((_: any, i: number) => isCorrect(i)).length)

function focusNext(i: number) {
  const inputs = document.querySelectorAll('.q-input')
  if (inputs[i + 1]) (inputs[i + 1] as HTMLInputElement).focus()
}

function reset() {
  finished.value = false; started.value = false; timeUp.value = false
  remaining.value = timeLimitSec.value
  answers.value = questions.value.map(() => '')
  showSolution.value = false
}

onBeforeUnmount(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.task-text { font-size: 0.9375rem; line-height: 1.75; margin-bottom: 1.25rem; color: var(--color-text-primary); }

.timer-bar {
  position: relative; height: 2rem; background: rgba(255, 255, 255, 0.04);
  border-radius: 0.5rem; overflow: hidden; margin-bottom: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.timer-fill {
  height: 100%; background: linear-gradient(90deg, #6366f1, #818cf8);
  border-radius: 0.5rem; transition: width 1s linear;
}
.timer--warning .timer-fill { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.timer--danger .timer-fill { background: linear-gradient(90deg, #ef4444, #f87171); }
.timer-label {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: 0.8125rem; font-weight: 700; color: var(--color-text-primary);
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
}

.questions-list { display: flex; flex-direction: column; gap: 0.625rem; margin-bottom: 1rem; }

.question-card {
  padding: 0.875rem 1rem; background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.625rem;
  transition: border-color 0.2s;
}
.q--answered { border-color: rgba(99, 102, 241, 0.15); }

.q-header { display: flex; align-items: flex-start; gap: 0.625rem; margin-bottom: 0.5rem; }
.q-number {
  width: 1.375rem; height: 1.375rem; background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 0.625rem; font-weight: 700; flex-shrink: 0;
}
.q-text { font-size: 0.875rem; color: var(--color-text-primary); line-height: 1.5; }

.q-input {
  width: 100%; padding: 0.5rem 0.75rem; border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem; font-size: 0.875rem; background: rgba(255, 255, 255, 0.025);
  color: var(--color-text-primary); transition: border-color 0.15s, box-shadow 0.15s;
}
.q-input:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }
.q-input:disabled { opacity: 0.6; }

.q-feedback {
  display: flex; align-items: center; gap: 0.5rem;
  margin-top: 0.5rem; padding: 0.375rem 0.625rem; border-radius: 0.375rem;
  font-size: 0.8125rem;
}
.fb--correct { background: rgba(16, 185, 129, 0.06); color: var(--color-success); }
.fb--wrong { background: rgba(239, 68, 68, 0.05); color: var(--color-error); }
.fb-icon { font-weight: 700; }
.fb-text { color: var(--color-text-primary); }

.controls { display: flex; gap: 0.75rem; margin-bottom: 1rem; }

.start-btn {
  padding: 0.625rem 2rem; background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; border: none; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 600;
  cursor: pointer; box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25); transition: all 0.15s;
}
.start-btn:hover { box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35); transform: translateY(-1px); }

.submit-btn {
  padding: 0.5rem 1.5rem; background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff; border: none; border-radius: 0.5rem; font-size: 0.8125rem; font-weight: 600;
  cursor: pointer; transition: all 0.15s;
}
.submit-btn:hover:not(:disabled) { transform: translateY(-1px); }
.submit-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.reset-btn {
  padding: 0.5rem 1.25rem; background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 0.5rem;
  font-size: 0.8125rem; color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s;
}
.reset-btn:hover { background: rgba(255, 255, 255, 0.08); }

.score-box {
  display: flex; align-items: baseline; gap: 0.5rem; flex-wrap: wrap;
  padding: 0.875rem 1rem; background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 0.625rem;
  margin-bottom: 1rem;
}
.score-value { font-size: 1.375rem; font-weight: 700; color: var(--color-accent-light); }
.score-label { font-size: 0.8125rem; color: var(--color-text-secondary); }
.time-bonus { margin-left: auto; font-size: 0.75rem; color: var(--color-success); font-weight: 500; }
.time-up { margin-left: auto; font-size: 0.75rem; color: var(--color-error); font-weight: 500; }

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
.sol-explanation { margin: 0; font-size: 0.8125rem; color: var(--color-text-secondary); font-style: italic; line-height: 1.6; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
