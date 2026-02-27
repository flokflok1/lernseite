<template>
  <div class="renderer">
    <p v-if="taskText" class="task-text">{{ taskText }}</p>

    <!-- Topic to Explain -->
    <div class="topic-card">
      <h4 class="section-label">{{ t('lesson.methodExecution.renderer.oralExplanation.topic') }}</h4>
      <p class="topic-text">{{ topicText }}</p>
      <div v-if="keyPoints.length" class="key-points">
        <span class="kp-label">{{ t('lesson.methodExecution.renderer.oralExplanation.keyPoints') }}:</span>
        <ul class="kp-list">
          <li v-for="(kp, i) in keyPoints" :key="i" class="kp-item">{{ kp }}</li>
        </ul>
      </div>
    </div>

    <!-- Recording Section (text fallback) -->
    <div class="record-section">
      <h4 class="section-label">{{ t('lesson.methodExecution.renderer.oralExplanation.yourExplanation') }}</h4>

      <!-- Audio indicator (visual only - actual recording requires browser API) -->
      <div class="audio-hint">
        <span class="mic-icon">🎤</span>
        <span class="audio-text">{{ t('lesson.methodExecution.renderer.oralExplanation.audioHint') }}</span>
      </div>

      <!-- Text fallback -->
      <textarea
        v-model="userExplanation"
        class="explanation-input"
        rows="6"
        :placeholder="t('lesson.methodExecution.renderer.oralExplanation.placeholder')"
        :disabled="submitted"
      />

      <!-- Word count -->
      <div class="word-info">
        <span class="word-count">{{ wordCount }} {{ t('lesson.methodExecution.renderer.oralExplanation.words') }}</span>
        <span v-if="minWords" class="word-min" :class="{ 'word-min--met': wordCount >= minWords }">
          {{ t('lesson.methodExecution.renderer.oralExplanation.minWords', { count: minWords }) }}
        </span>
      </div>
    </div>

    <!-- Submit -->
    <button v-if="!submitted" class="submit-btn" :disabled="!userExplanation.trim() || (minWords && wordCount < minWords)" @click="submitted = true">
      {{ t('lesson.methodExecution.renderer.oralExplanation.submit') }}
    </button>

    <!-- Self-Assessment (after submit) -->
    <Transition name="fade">
      <div v-if="submitted" class="self-assess">
        <h4 class="section-label">{{ t('lesson.methodExecution.renderer.oralExplanation.selfAssess') }}</h4>
        <div class="assess-checklist">
          <label v-for="(criterion, i) in assessCriteria" :key="i" class="assess-item">
            <input v-model="assessChecks[i]" type="checkbox" class="assess-check" />
            <span>{{ criterion }}</span>
          </label>
        </div>
        <div class="assess-score">
          {{ assessChecks.filter(Boolean).length }}/{{ assessCriteria.length }}
          {{ t('lesson.methodExecution.renderer.oralExplanation.criteriaMetLabel') }}
        </div>
      </div>
    </Transition>

    <!-- Reset -->
    <button v-if="submitted" class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>

    <!-- Solution -->
    <button v-if="solution" class="solution-btn" @click="showSolution = !showSolution">
      {{ showSolution ? t('lesson.methodExecution.renderer.common.hideSolution') : t('lesson.methodExecution.renderer.common.sampleSolution') }}
    </button>
    <Transition name="fade">
      <div v-if="showSolution && solution" class="solution-box">
        <p v-if="solution.explanation" class="sol-text">{{ solution.explanation }}</p>
        <p v-if="solution.modelAnswer" class="sol-model">{{ solution.modelAnswer }}</p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { OralExplanationData, OralExplanationSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: OralExplanationData | null; solution: OralExplanationSolution | null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const showSolution = ref(false)
const submitted = ref(false)
const userExplanation = ref('')

watch(() => props.data, () => reset(), { deep: true })

// Emit on submit — self-assessed, 1/1 for completion
watch(submitted, (val) => {
  if (val) emit('complete', 1, 1)
})

const taskText = computed(() => props.data?.task || props.data?.description || '')
const topicText = computed(() => props.data?.topic || props.data?.question || '')
const keyPoints = computed(() => props.data?.keyPoints || [])
const minWords = computed(() => props.data?.minWords || 0)
const assessCriteria = computed(() =>
  props.data?.criteria || [
    t('lesson.methodExecution.renderer.oralExplanation.criteria.complete'),
    t('lesson.methodExecution.renderer.oralExplanation.criteria.clear'),
    t('lesson.methodExecution.renderer.oralExplanation.criteria.examples'),
  ]
)
const assessChecks = ref<boolean[]>(assessCriteria.value.map(() => false))

const wordCount = computed(() => {
  const trimmed = userExplanation.value.trim()
  return trimmed ? trimmed.split(/\s+/).length : 0
})

function reset() {
  submitted.value = false
  userExplanation.value = ''
  assessChecks.value = assessCriteria.value.map(() => false)
  showSolution.value = false
}
</script>

<style scoped>
.task-text { font-size: 0.9375rem; line-height: 1.75; margin-bottom: 1.25rem; color: var(--color-text-primary); }

.section-label {
  font-size: 0.6875rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--color-accent-light); margin: 0 0 0.5rem;
}

.topic-card {
  padding: 1rem 1.125rem; background: rgba(99, 102, 241, 0.04);
  border: 1px solid rgba(99, 102, 241, 0.12); border-radius: 0.625rem;
  margin-bottom: 1.25rem;
}
.topic-text { font-size: 1rem; color: var(--color-text-primary); margin: 0 0 0.75rem; line-height: 1.6; }

.kp-label { font-size: 0.75rem; color: var(--color-text-tertiary); }
.kp-list { margin: 0.25rem 0 0; padding-left: 1.25rem; }
.kp-item { font-size: 0.8125rem; color: var(--color-text-secondary); line-height: 1.6; }

.record-section { margin-bottom: 1rem; }

.audio-hint {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.5rem 0.75rem; background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(245, 158, 11, 0.12); border-radius: 0.5rem;
  margin-bottom: 0.75rem;
}
.mic-icon { font-size: 1rem; }
.audio-text { font-size: 0.75rem; color: var(--color-warning); }

.explanation-input {
  width: 100%; padding: 0.875rem; border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.625rem; font-size: 0.875rem; resize: vertical;
  background: rgba(255, 255, 255, 0.025); color: var(--color-text-primary); line-height: 1.65;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.explanation-input:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }
.explanation-input:disabled { opacity: 0.6; }

.word-info { display: flex; align-items: center; justify-content: space-between; margin-top: 0.375rem; }
.word-count { font-size: 0.75rem; color: var(--color-text-tertiary); }
.word-min { font-size: 0.75rem; color: var(--color-error); }
.word-min--met { color: var(--color-success); }

.submit-btn {
  padding: 0.5rem 2rem; background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; border: none; border-radius: 0.5rem; font-size: 0.8125rem; font-weight: 600;
  cursor: pointer; box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25); transition: all 0.15s;
  margin-bottom: 1rem;
}
.submit-btn:hover:not(:disabled) { box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35); transform: translateY(-1px); }
.submit-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.self-assess {
  padding: 1rem 1.125rem; background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.625rem;
  margin-bottom: 1rem;
}
.assess-checklist { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0.75rem; }
.assess-item {
  display: flex; align-items: center; gap: 0.625rem;
  font-size: 0.875rem; color: var(--color-text-primary); cursor: pointer;
}
.assess-check { width: 1.125rem; height: 1.125rem; accent-color: var(--color-success); flex-shrink: 0; }
.assess-score { font-size: 0.8125rem; font-weight: 600; color: var(--color-accent-light); }

.reset-btn {
  padding: 0.5rem 1.25rem; background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 0.5rem;
  font-size: 0.8125rem; color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s;
  margin-bottom: 1rem;
}
.reset-btn:hover { background: rgba(255, 255, 255, 0.08); }

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
.sol-text { margin: 0 0 0.5rem; font-size: 0.8125rem; color: var(--color-text-secondary); font-style: italic; line-height: 1.6; }
.sol-model { margin: 0; font-size: 0.875rem; color: var(--color-text-primary); line-height: 1.65; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
