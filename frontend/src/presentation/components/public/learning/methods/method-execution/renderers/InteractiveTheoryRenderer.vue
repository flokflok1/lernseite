<template>
  <div class="renderer">
    <div v-if="renderedConcept" class="concept" v-html="renderedConcept" />
    <div v-for="(ex, i) in examples" :key="i" class="example-card">
      <pre class="example-code">{{ ex.code }}</pre>
      <p class="example-explanation">{{ ex.explanation }}</p>
    </div>
    <div v-if="question" class="question-section">
      <h4 class="q-label">{{ t('lesson.methodExecution.renderer.interactiveTheory.questionLabel') }}</h4>
      <p class="q-text">{{ question }}</p>
      <textarea v-model="answer" class="answer-input" rows="3" :placeholder="t('lesson.methodExecution.renderer.common.yourAnswer') + '...'" />
      <button class="check-btn" :disabled="!answer.trim()" @click="showAnswer = true">{{ t('lesson.methodExecution.renderer.common.check') }}</button>
      <Transition name="fade">
        <div v-if="showAnswer && solution" class="solution-box">
          <h4 class="sol-label">{{ t('lesson.methodExecution.renderer.common.solution') }}</h4>
          <p>{{ solution.answer }}</p>
          <p v-if="solution.explanation" class="sol-explanation">{{ solution.explanation }}</p>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from './markdown'
import type { InteractiveTheoryData, InteractiveTheorySolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: (InteractiveTheoryData & { raw_text?: string }) | null; solution: InteractiveTheorySolution | null }>()
const answer = ref('')
const showAnswer = ref(false)
const renderedConcept = computed(() => renderMarkdown(props.data?.concept || props.data?.raw_text || ''))
const examples = computed(() => props.data?.examples || [])
const question = computed(() => props.data?.interactiveQuestion || '')
</script>

<style scoped>
.concept {
  font-size: 0.9375rem;
  line-height: 1.75;
  margin-bottom: 1.25rem;
  color: var(--color-text-primary);
}

.example-card {
  padding: 1.125rem;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.75rem;
  margin-bottom: 0.75rem;
  transition: border-color 0.2s;
}

.example-card:hover {
  border-color: rgba(99, 102, 241, 0.15);
}

.example-code {
  margin: 0 0 0.625rem;
  padding: 0.875rem;
  background: var(--color-code-bg);
  color: var(--color-code-text);
  border-radius: 0.5rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem;
  line-height: 1.7;
  white-space: pre-wrap;
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.example-explanation {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.question-section {
  margin-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 1.25rem;
}

.q-label {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-accent-light);
  margin: 0 0 0.375rem;
}

.q-text {
  font-size: 0.9375rem;
  font-weight: 500;
  margin: 0 0 0.75rem;
  color: var(--color-text-primary);
}

.answer-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  resize: vertical;
  background: rgba(255, 255, 255, 0.025);
  color: var(--color-text-primary);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.answer-input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.check-btn {
  margin-top: 0.75rem;
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

.solution-box {
  margin-top: 1rem;
  padding: 1rem 1.125rem;
  background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 0.625rem;
}

.sol-label {
  margin: 0 0 0.375rem;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-success);
}

.solution-box p {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.65;
  color: var(--color-text-primary);
}

.sol-explanation {
  margin: 0.5rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  font-style: italic;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
