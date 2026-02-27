<template>
  <div class="renderer">
    <pre v-if="diagram" class="diagram-box">{{ diagram }}</pre>
    <div v-if="description" class="description" v-html="renderMarkdown(description)" />
    <div v-if="questions.length" class="questions-section">
      <h4 class="section-label">{{ t('lesson.methodExecution.renderer.diagram.comprehensionQuestions') }}</h4>
      <div v-for="(q, i) in questions" :key="i" class="question-item">
        <p class="q-text"><strong>{{ i + 1 }}.</strong> {{ q }}</p>
        <textarea v-model="answers[i]" class="q-input" rows="2" :placeholder="t('lesson.methodExecution.renderer.common.yourAnswer') + '...'" />
      </div>
      <button class="check-btn" :disabled="answers.every(a => !a.trim())" @click="showSolution = true">{{ t('lesson.methodExecution.renderer.diagram.checkAnswers') }}</button>
      <Transition name="fade">
        <div v-if="showSolution && solutionAnswers.length" class="solutions">
          <div v-for="(a, i) in solutionAnswers" :key="i" class="sol-item">
            <strong>{{ i + 1 }}.</strong> {{ a }}
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from './markdown'
import type { DiagramData, DiagramSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: DiagramData | null; solution: DiagramSolution | null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const showSolution = ref(false)
const diagram = computed(() => props.data?.diagram || '')
const description = computed(() => props.data?.description || '')
const questions = computed(() => props.data?.questions || [])
const answers = ref<string[]>(Array(12).fill(''))
const solutionAnswers = computed(() => props.solution?.answers || [])

watch(() => props.data, () => {
  showSolution.value = false
  answers.value = Array(12).fill('')
}, { deep: true })

// Emit when solution is revealed (self-check renderer)
watch(showSolution, (val) => {
  if (val) emit('complete', 1, 1)
})
</script>

<style scoped>
.diagram-box {
  padding: 1.25rem;
  background: var(--color-code-bg);
  color: #a5f3fc;
  border-radius: 0.75rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem;
  line-height: 1.7;
  white-space: pre;
  overflow-x: auto;
  margin-bottom: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.description {
  font-size: 0.9375rem;
  line-height: 1.7;
  margin-bottom: 1.25rem;
  color: var(--color-text-primary);
}

.section-label {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-accent-light);
  margin: 0 0 0.75rem;
}

.question-item {
  margin-bottom: 1rem;
}

.q-text {
  margin: 0 0 0.375rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.q-text strong {
  color: var(--color-accent-light);
}

.q-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  resize: vertical;
  background: rgba(255, 255, 255, 0.025);
  color: var(--color-text-primary);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.q-input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
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

.check-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.solutions {
  margin-top: 1rem;
  padding: 1rem 1.125rem;
  background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 0.625rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sol-item {
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--color-text-primary);
}

.sol-item strong {
  color: var(--color-success);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
