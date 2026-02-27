<template>
  <div class="renderer">
    <!-- Single Quick-Check Question -->
    <div class="check-card">
      <div class="check-icon-wrap">
        <span class="check-icon">✅</span>
      </div>
      <h4 class="check-title">{{ t('lesson.methodExecution.renderer.comprehensionCheck.title') }}</h4>
      <p class="check-question">{{ questionText }}</p>

      <!-- Options (if provided) -->
      <div v-if="options.length" class="options-list">
        <button
          v-for="(opt, i) in options" :key="i"
          class="option-btn"
          :class="{
            'opt--selected': selectedOption === i,
            'opt--correct': checked && i === correctIndex,
            'opt--wrong': checked && selectedOption === i && i !== correctIndex
          }"
          :disabled="checked"
          @click="selectedOption = i"
        >
          <span class="opt-letter">{{ String.fromCharCode(65 + i) }}</span>
          <span class="opt-text">{{ opt.text || opt }}</span>
        </button>
      </div>

      <!-- Free text fallback -->
      <textarea
        v-if="!options.length"
        v-model="freeAnswer"
        class="free-input"
        rows="3"
        :placeholder="t('lesson.methodExecution.renderer.comprehensionCheck.placeholder')"
        :disabled="checked"
      />

      <!-- Check Button -->
      <button
        v-if="!checked"
        class="check-btn"
        :disabled="options.length ? selectedOption === null : !freeAnswer.trim()"
        @click="checked = true"
      >
        {{ t('lesson.methodExecution.renderer.common.check') }}
      </button>

      <!-- Feedback -->
      <Transition name="fade">
        <div v-if="checked" class="feedback" :class="isCorrect ? 'feedback--correct' : 'feedback--wrong'">
          <span class="feedback-emoji">{{ isCorrect ? '🎉' : '💡' }}</span>
          <div>
            <p class="feedback-title">{{ isCorrect ? t('lesson.methodExecution.renderer.comprehensionCheck.correct') : t('lesson.methodExecution.renderer.comprehensionCheck.incorrect') }}</p>
            <p v-if="explanation" class="feedback-text">{{ explanation }}</p>
          </div>
        </div>
      </Transition>

      <!-- Reset -->
      <button v-if="checked" class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ComprehensionCheckData, ComprehensionCheckSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: ComprehensionCheckData | null; solution: ComprehensionCheckSolution | null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const checked = ref(false)
const selectedOption = ref<number | null>(null)
const freeAnswer = ref('')

const questionText = computed(() => props.data?.question || props.data?.task || '')
const options = computed(() => props.data?.options || [])
const correctIndex = computed(() => {
  if (!options.value.length) return -1
  const idx = options.value.findIndex((o: any) => o.correct === true)
  return idx === -1 ? 0 : idx
})
const explanation = computed(() => props.data?.explanation || props.solution?.explanation || '')

const isCorrect = computed(() => {
  if (options.value.length) return selectedOption.value === correctIndex.value
  const expected = props.data?.answer || props.solution?.answer
  if (!expected) return true
  return freeAnswer.value.trim().toLowerCase() === String(expected).trim().toLowerCase()
})

watch(() => props.data, () => reset(), { deep: true })

watch(checked, (val) => {
  if (val) emit('complete', isCorrect.value ? 1 : 0, 1)
})

function reset() {
  checked.value = false
  selectedOption.value = null
  freeAnswer.value = ''
}
</script>

<style scoped>
.check-card {
  padding: 1.5rem; background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.75rem;
  text-align: center;
}

.check-icon-wrap { margin-bottom: 0.75rem; }
.check-icon { font-size: 1.5rem; }

.check-title {
  font-size: 0.6875rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--color-accent-light); margin: 0 0 0.75rem;
}

.check-question {
  font-size: 1.0625rem; color: var(--color-text-primary); line-height: 1.6;
  margin: 0 0 1.25rem; text-align: left;
}

.options-list { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1rem; }

.option-btn {
  display: flex; align-items: center; gap: 0.75rem; text-align: left;
  padding: 0.75rem 1rem; background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 0.625rem;
  cursor: pointer; transition: all 0.15s; color: var(--color-text-primary); font-size: 0.875rem;
}
.option-btn:hover:not(:disabled) { border-color: rgba(99, 102, 241, 0.3); background: rgba(99, 102, 241, 0.04); }
.opt--selected { border-color: rgba(99, 102, 241, 0.4); background: rgba(99, 102, 241, 0.08); }
.opt--correct { border-color: rgba(16, 185, 129, 0.4) !important; background: rgba(16, 185, 129, 0.08) !important; }
.opt--wrong { border-color: rgba(239, 68, 68, 0.4) !important; background: rgba(239, 68, 68, 0.06) !important; }
.option-btn:disabled { cursor: default; }

.opt-letter {
  width: 1.5rem; height: 1.5rem; display: flex; align-items: center; justify-content: center;
  background: rgba(99, 102, 241, 0.1); color: var(--color-accent-light); border-radius: 0.375rem;
  font-size: 0.75rem; font-weight: 700; flex-shrink: 0;
}
.opt--correct .opt-letter { background: rgba(16, 185, 129, 0.2); color: var(--color-success); }
.opt--wrong .opt-letter { background: rgba(239, 68, 68, 0.2); color: var(--color-error); }

.free-input {
  width: 100%; padding: 0.75rem; border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem; font-size: 0.875rem; resize: vertical;
  background: rgba(255, 255, 255, 0.025); color: var(--color-text-primary);
  margin-bottom: 1rem; text-align: left;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.free-input:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }
.free-input:disabled { opacity: 0.6; }

.check-btn {
  padding: 0.5rem 2rem; background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; border: none; border-radius: 0.5rem; font-size: 0.8125rem; font-weight: 600;
  cursor: pointer; box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25); transition: all 0.15s;
}
.check-btn:hover:not(:disabled) { box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35); transform: translateY(-1px); }
.check-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.feedback {
  display: flex; align-items: flex-start; gap: 0.75rem; text-align: left;
  margin-top: 1rem; padding: 1rem; border-radius: 0.625rem;
}
.feedback--correct { background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.2); }
.feedback--wrong { background: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.2); }
.feedback-emoji { font-size: 1.25rem; }
.feedback-title { margin: 0; font-size: 0.875rem; font-weight: 600; color: var(--color-text-primary); }
.feedback-text { margin: 0.25rem 0 0; font-size: 0.8125rem; color: var(--color-text-secondary); line-height: 1.6; }

.reset-btn {
  margin-top: 0.75rem; padding: 0.5rem 1.25rem;
  background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem; font-size: 0.8125rem; color: var(--color-text-secondary);
  cursor: pointer; transition: all 0.15s;
}
.reset-btn:hover { background: rgba(255, 255, 255, 0.08); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
