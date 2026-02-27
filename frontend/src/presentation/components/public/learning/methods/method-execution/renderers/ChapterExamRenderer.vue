<template>
  <div class="renderer">
    <!-- Exam Header -->
    <div class="exam-header">
      <div class="exam-badge">🎓 {{ t('lesson.methodExecution.renderer.chapterExam.badge') }}</div>
      <p v-if="taskText" class="task-text">{{ taskText }}</p>
      <div class="exam-meta">
        <span v-if="totalPoints" class="meta-item">{{ totalPoints }} {{ t('lesson.methodExecution.renderer.chapterExam.totalPoints') }}</span>
        <span class="meta-item">{{ questions.length }} {{ t('lesson.methodExecution.renderer.chapterExam.questionsCount') }}</span>
        <span v-if="passingPercent" class="meta-item">{{ passingPercent }}% {{ t('lesson.methodExecution.renderer.chapterExam.passingScore') }}</span>
      </div>
    </div>

    <!-- Questions -->
    <div class="questions">
      <div v-for="(q, i) in questions" :key="i" class="question-card">
        <div class="q-top">
          <span class="q-number">{{ i + 1 }}</span>
          <span class="q-text">{{ q.question || q.text }}</span>
          <span v-if="q.points" class="q-points">{{ q.points }}P</span>
        </div>

        <!-- MC options -->
        <div v-if="q.options?.length" class="q-options">
          <button
            v-for="(opt, j) in q.options" :key="j"
            class="opt-btn"
            :class="{
              'opt--selected': selectedAnswers[i] === j,
              'opt--correct': checked && j === getCorrectIdx(q),
              'opt--wrong': checked && selectedAnswers[i] === j && j !== getCorrectIdx(q)
            }"
            :disabled="checked"
            @click="selectedAnswers[i] = j"
          >
            <span class="opt-letter">{{ String.fromCharCode(65 + j) }}</span>
            {{ typeof opt === 'string' ? opt : opt.text }}
          </button>
        </div>

        <!-- Free text -->
        <textarea
          v-else
          v-model="textAnswers[i]"
          class="q-textarea"
          rows="3"
          :placeholder="t('lesson.methodExecution.renderer.chapterExam.answerPlaceholder')"
          :disabled="checked"
        />

        <!-- Feedback -->
        <Transition name="fade">
          <div v-if="checked && q.answer" class="q-feedback">
            <span class="fb-label">{{ t('lesson.methodExecution.renderer.chapterExam.correctAnswer') }}:</span>
            <span class="fb-answer">{{ q.answer }}</span>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Submit / Score -->
    <div class="exam-actions">
      <button v-if="!checked" class="submit-btn" :disabled="!canSubmit" @click="checked = true">
        {{ t('lesson.methodExecution.renderer.chapterExam.submitExam') }}
      </button>
      <button v-if="checked" class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>

    <Transition name="fade">
      <div v-if="checked" class="result-card" :class="passed ? 'result--pass' : 'result--fail'">
        <div class="result-icon">{{ passed ? '🎉' : '📚' }}</div>
        <div class="result-info">
          <p class="result-title">{{ passed ? t('lesson.methodExecution.renderer.chapterExam.passed') : t('lesson.methodExecution.renderer.chapterExam.failed') }}</p>
          <p class="result-score">{{ earnedPoints }}/{{ totalPoints || questions.length }} {{ t('lesson.methodExecution.renderer.chapterExam.totalPoints') }}</p>
        </div>
      </div>
    </Transition>

    <!-- Solution -->
    <button v-if="solution" class="solution-btn" @click="showSolution = !showSolution">
      {{ showSolution ? t('lesson.methodExecution.renderer.common.hideSolution') : t('lesson.methodExecution.renderer.common.sampleSolution') }}
    </button>
    <Transition name="fade">
      <div v-if="showSolution && solution" class="solution-box">
        <p v-if="solution.explanation" class="sol-text">{{ solution.explanation }}</p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChapterExamData, ChapterExamSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: ChapterExamData | null; solution: ChapterExamSolution | null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const showSolution = ref(false)
const checked = ref(false)

watch(() => props.data, () => reset(), { deep: true })

watch(checked, (val) => {
  if (val) emit('complete', earnedPoints.value, totalPoints.value || questions.value.length)
})

const taskText = computed(() => props.data?.task || props.data?.description || '')
const questions = computed(() => props.data?.questions || [])
const totalPoints = computed(() => {
  const pts = questions.value.reduce((sum: number, q: any) => sum + (q.points || 1), 0)
  return pts
})
const passingPercent = computed(() => props.data?.passingPercent || 60)

const selectedAnswers = ref<Record<number, number>>({})
const textAnswers = ref<string[]>(questions.value.map(() => ''))

function getCorrectIdx(q: any): number {
  if (!q.options) return -1
  return q.options.findIndex((o: any) => o.correct === true)
}

const canSubmit = computed(() =>
  questions.value.every((_: any, i: number) => {
    const q = questions.value[i]
    if (q.options?.length) return selectedAnswers.value[i] !== undefined
    return textAnswers.value[i]?.trim()
  })
)

const earnedPoints = computed(() =>
  questions.value.reduce((sum: number, q: any, i: number) => {
    const pts = q.points || 1
    if (q.options?.length) {
      return sum + (selectedAnswers.value[i] === getCorrectIdx(q) ? pts : 0)
    }
    if (q.answer) {
      const correct = textAnswers.value[i]?.trim().toLowerCase() === String(q.answer).trim().toLowerCase()
      return sum + (correct ? pts : 0)
    }
    // Free-text without expected answer: no auto-scoring (0 points)
    return sum
  }, 0)
)

const passed = computed(() => (earnedPoints.value / (totalPoints.value || 1)) * 100 >= passingPercent.value)

function reset() {
  checked.value = false
  selectedAnswers.value = {}
  textAnswers.value = questions.value.map(() => '')
  showSolution.value = false
}
</script>

<style scoped>
.exam-header { margin-bottom: 1.5rem; }
.exam-badge {
  display: inline-block; padding: 0.25rem 0.75rem; font-size: 0.6875rem;
  font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(234, 179, 8, 0.12));
  border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 999px;
  color: var(--color-warning); margin-bottom: 0.75rem;
}
.task-text { font-size: 0.9375rem; line-height: 1.75; margin: 0 0 0.75rem; color: var(--color-text-primary); }
.exam-meta { display: flex; gap: 1rem; flex-wrap: wrap; }
.meta-item { font-size: 0.75rem; color: var(--color-text-tertiary); }

.questions { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1.25rem; }

.question-card {
  padding: 1rem; background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.625rem;
}

.q-top { display: flex; align-items: flex-start; gap: 0.625rem; margin-bottom: 0.625rem; }
.q-number {
  width: 1.375rem; height: 1.375rem; background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 0.625rem; font-weight: 700; flex-shrink: 0;
}
.q-text { flex: 1; font-size: 0.875rem; color: var(--color-text-primary); line-height: 1.5; }
.q-points { font-size: 0.6875rem; font-weight: 600; color: var(--color-warning); white-space: nowrap; }

.q-options { display: flex; flex-direction: column; gap: 0.375rem; }

.opt-btn {
  display: flex; align-items: center; gap: 0.625rem; text-align: left;
  padding: 0.5rem 0.75rem; background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.5rem;
  cursor: pointer; transition: all 0.15s; color: var(--color-text-primary); font-size: 0.8125rem;
}
.opt-btn:hover:not(:disabled) { border-color: rgba(99, 102, 241, 0.25); }
.opt--selected { border-color: rgba(99, 102, 241, 0.35); background: rgba(99, 102, 241, 0.06); }
.opt--correct { border-color: rgba(16, 185, 129, 0.4) !important; background: rgba(16, 185, 129, 0.08) !important; }
.opt--wrong { border-color: rgba(239, 68, 68, 0.4) !important; background: rgba(239, 68, 68, 0.06) !important; }
.opt-btn:disabled { cursor: default; }

.opt-letter {
  width: 1.25rem; height: 1.25rem; display: flex; align-items: center; justify-content: center;
  background: rgba(99, 102, 241, 0.1); color: var(--color-accent-light); border-radius: 0.25rem;
  font-size: 0.6875rem; font-weight: 700; flex-shrink: 0;
}

.q-textarea {
  width: 100%; padding: 0.625rem; border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem; font-size: 0.8125rem; resize: vertical;
  background: rgba(255, 255, 255, 0.025); color: var(--color-text-primary);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.q-textarea:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }
.q-textarea:disabled { opacity: 0.6; }

.q-feedback {
  margin-top: 0.5rem; padding: 0.375rem 0.625rem;
  background: rgba(16, 185, 129, 0.04); border-left: 2px solid rgba(16, 185, 129, 0.3);
  border-radius: 0.25rem; font-size: 0.8125rem;
}
.fb-label { color: var(--color-text-tertiary); }
.fb-answer { color: var(--color-success); font-weight: 500; margin-left: 0.25rem; }

.exam-actions { display: flex; gap: 0.75rem; margin-bottom: 1rem; }

.submit-btn {
  padding: 0.625rem 2rem; background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; border: none; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 600;
  cursor: pointer; box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25); transition: all 0.15s;
}
.submit-btn:hover:not(:disabled) { box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35); transform: translateY(-1px); }
.submit-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.reset-btn {
  padding: 0.5rem 1.25rem; background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 0.5rem;
  font-size: 0.8125rem; color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s;
}
.reset-btn:hover { background: rgba(255, 255, 255, 0.08); }

.result-card {
  display: flex; align-items: center; gap: 1rem;
  padding: 1.25rem; border-radius: 0.75rem; margin-bottom: 1rem;
}
.result--pass { background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.2); }
.result--fail { background: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.2); }
.result-icon { font-size: 1.75rem; }
.result-title { margin: 0; font-size: 1rem; font-weight: 700; color: var(--color-text-primary); }
.result-score { margin: 0.125rem 0 0; font-size: 0.8125rem; color: var(--color-text-secondary); }

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
.sol-text { margin: 0; font-size: 0.8125rem; color: var(--color-text-secondary); font-style: italic; line-height: 1.6; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
