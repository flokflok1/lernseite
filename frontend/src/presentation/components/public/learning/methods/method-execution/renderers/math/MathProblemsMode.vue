<template>
  <div>
    <div v-for="(group, gi) in scenarioGroups" :key="gi" class="scenario-group">
      <!-- Scenario context block (shown once per group) -->
      <div v-if="group.scenario_title || group.scenario_text" class="scenario-block">
        <h3 v-if="group.scenario_title" class="scenario-title">{{ group.scenario_title }}</h3>
        <p v-if="group.scenario_text" class="scenario-text">{{ group.scenario_text }}</p>
      </div>

      <!-- Problems within this scenario -->
      <div v-for="p in group.problems" :key="p.globalIndex" class="problem-card">
        <div class="problem-header">
          <span class="problem-number">{{ p.globalIndex + 1 }}</span>
          <h4 class="problem-title">{{ t('lesson.methodExecution.renderer.mathInteractive.problemLabel', { n: p.globalIndex + 1 }) }}</h4>
          <span v-if="p.points" class="points-badge">{{ p.points }} P.</span>
        </div>
        <p class="problem-text">{{ p.question }}</p>
        <div v-if="p.formula" class="formula-display">{{ p.formula }}</div>
        <div class="answer-row">
          <input
            v-model="answers[p.globalIndex]"
            type="text"
            class="answer-input"
            :placeholder="t('lesson.methodExecution.renderer.mathInteractive.yourAnswer')"
            :disabled="checked"
            :class="{ 'input--correct': checked && isCorrect(p.globalIndex), 'input--wrong': checked && !isCorrect(p.globalIndex) }"
          />
          <span v-if="checked" class="answer-status">{{ isCorrect(p.globalIndex) ? '✓' : '✗' }}</span>
        </div>
        <Transition name="fade">
          <div v-if="checked && !isCorrect(p.globalIndex) && p.answer" class="correct-answer">
            {{ t('lesson.methodExecution.renderer.mathInteractive.correctAnswer') }}: <strong>{{ p.answer }}</strong>
          </div>
        </Transition>
        <p v-if="checked && p.hint" class="problem-explanation">{{ p.hint }}</p>
      </div>
    </div>

    <div class="actions">
      <button v-if="!checked" class="check-btn" :disabled="answers.some(a => !a.trim())" @click="checked = true">
        {{ t('lesson.methodExecution.renderer.mathInteractive.checkSolution') }}
      </button>
      <button v-else class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>
    <div v-if="checked" class="score">
      {{ t('lesson.methodExecution.renderer.mathInteractive.score', { correct: correctCount, total: problems.length }) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MathInteractiveData, MathProblem } from '../types'

const { t } = useI18n()
const props = defineProps<{ data: MathInteractiveData | null }>()
const checked = ref(false)
const problems = computed(() => props.data?.problems || [])
const answers = ref<string[]>(problems.value.map(() => ''))

interface IndexedProblem extends MathProblem {
  globalIndex: number
}

interface ScenarioGroup {
  scenario_title: string
  scenario_text: string
  problems: IndexedProblem[]
}

/** Group ALL problems by scenario — merges non-consecutive duplicates via Map. */
const scenarioGroups = computed<ScenarioGroup[]>(() => {
  const map = new Map<string, ScenarioGroup>()
  const order: string[] = []

  problems.value.forEach((p, i) => {
    const key = p.scenario_title || ''
    if (!map.has(key)) {
      map.set(key, {
        scenario_title: p.scenario_title || '',
        scenario_text: p.scenario_text || '',
        problems: [],
      })
      order.push(key)
    }
    map.get(key)!.problems.push({ ...p, globalIndex: i })
  })
  return order.map(k => map.get(k)!)
})

function isCorrect(i: number): boolean {
  return answers.value[i]?.trim().toLowerCase() === String(problems.value[i]?.answer || '').trim().toLowerCase()
}

const correctCount = computed(() => problems.value.filter((_: any, i: number) => isCorrect(i)).length)

function reset() {
  checked.value = false
  answers.value = problems.value.map(() => '')
}
</script>

<style scoped>
/* ── Scenario context ── */
.scenario-group { margin-bottom: 1.5rem; }
.scenario-group:last-child { margin-bottom: 0; }

.scenario-block {
  padding: 1rem 1.25rem;
  background: rgba(99, 102, 241, 0.04);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: 0.75rem;
  margin-bottom: 0.75rem;
}

:root.dark .scenario-block {
  background: rgba(99, 102, 241, 0.06);
  border-color: rgba(99, 102, 241, 0.15);
}

.scenario-title {
  margin: 0 0 0.5rem;
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.scenario-text {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.7;
  color: var(--color-text-secondary);
}

/* ── Problem cards ── */
.problem-card {
  padding: 1.125rem;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.75rem;
  margin-bottom: 0.75rem;
  transition: border-color 0.2s;
}
.problem-card:hover { border-color: rgba(99, 102, 241, 0.12); }

.problem-header { display: flex; align-items: center; gap: 0.625rem; margin-bottom: 0.625rem; }

.problem-number {
  width: 1.625rem; height: 1.625rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.6875rem; flex-shrink: 0;
}

.problem-title { margin: 0; font-size: 0.8125rem; font-weight: 600; color: var(--color-text-primary); flex: 1; }

.points-badge {
  font-size: 0.625rem; font-weight: 600; padding: 0.125rem 0.5rem;
  border-radius: 1rem; background: rgba(99, 102, 241, 0.1);
  color: var(--color-accent-light, #818cf8);
}

.problem-text { margin: 0 0 0.75rem; font-size: 0.9375rem; line-height: 1.65; color: var(--color-text-primary); }

.formula-display {
  padding: 0.875rem 1rem; background: var(--color-code-bg);
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.625rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 1rem; color: var(--color-accent-light); text-align: center; margin-bottom: 0.75rem;
}

.answer-row { display: flex; align-items: center; gap: 0.625rem; margin-top: 0.5rem; }

.answer-input {
  flex: 1; padding: 0.5rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 0.5rem;
  font-size: 0.875rem; background: rgba(255, 255, 255, 0.025);
  color: var(--color-text-primary); transition: border-color 0.15s, box-shadow 0.15s;
}
.answer-input:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }
.answer-input:disabled { opacity: 0.6; }
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

.problem-explanation {
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
