<template>
  <div class="renderer">
    <div v-if="question" class="question-text" v-html="renderMarkdown(question)" />
    <div class="answer-section">
      <textarea
        v-model="userAnswer"
        class="answer-input"
        rows="8"
        :placeholder="t('lesson.methodExecution.renderer.freeText.placeholder')"
        :disabled="submitted"
      />
      <div class="answer-meta">
        <span class="word-count">{{ t('lesson.methodExecution.renderer.freeText.wordCount', { count: wordCount }) }}</span>
      </div>
    </div>
    <div class="actions">
      <button v-if="!submitted" class="submit-btn" :disabled="wordCount < 3" @click="handleSubmit">
        {{ t('lesson.methodExecution.renderer.freeText.submit') }}
      </button>
      <button v-else class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
      <button class="solution-btn" @click="showSolution = !showSolution">
        {{ showSolution ? t('lesson.methodExecution.renderer.common.hideSolution') : t('lesson.methodExecution.renderer.common.showSolution') }}
      </button>
    </div>
    <Transition name="fade">
      <div v-if="showSolution && solution" class="solution-box">
        <div v-if="solution.modelAnswer" class="sol-section">
          <h4 class="sol-label">{{ t('lesson.methodExecution.renderer.freeText.modelAnswer') }}</h4>
          <p class="sol-text">{{ solution.modelAnswer }}</p>
        </div>
        <div v-if="solution.keyPoints?.length" class="sol-section">
          <h4 class="sol-label">{{ t('lesson.methodExecution.renderer.freeText.keyPoints') }}</h4>
          <ul class="key-points-list">
            <li v-for="(kp, i) in solution.keyPoints" :key="i">{{ kp }}</li>
          </ul>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from './markdown'
import type { FreeTextData, FreeTextSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: FreeTextData | null; solution: FreeTextSolution | null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const userAnswer = ref('')
const submitted = ref(false)
const showSolution = ref(false)
const question = computed(() => props.data?.question || '')
const wordCount = computed(() => userAnswer.value.trim() ? userAnswer.value.trim().split(/\s+/).length : 0)

function reset() {
  submitted.value = false
  userAnswer.value = ''
}

function handleSubmit() {
  submitted.value = true
  // FreeText is self-assessed, emit full score on submission
  emit('complete', 1, 1)
}
</script>

<style scoped>
.question-text {
  font-size: 0.9375rem;
  line-height: 1.65;
  margin-bottom: 1.25rem;
  font-weight: 500;
}

:root.dark .question-text {
  color: var(--color-text-primary);
}

.answer-input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.625rem;
  font-size: 0.875rem;
  line-height: 1.65;
  resize: vertical;
  background: rgba(255, 255, 255, 0.025);
  color: var(--color-text-primary);
  transition: border-color 0.2s;
  font-family: inherit;
}

.answer-input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
}

:root.dark .answer-input {
  color: var(--color-text-primary);
}

.answer-input:disabled {
  opacity: 0.6;
}

.answer-meta {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.375rem;
  margin-bottom: 1rem;
}

.word-count {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  font-variant-numeric: tabular-nums;
}

.actions {
  display: flex;
  gap: 0.625rem;
  margin-bottom: 1rem;
}

.submit-btn {
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

.submit-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
  transform: translateY(-1px);
}

.submit-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.reset-btn {
  padding: 0.5rem 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  background: rgba(255, 255, 255, 0.04);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.reset-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

.solution-btn {
  padding: 0.5rem 1.25rem;
  background: rgba(16, 185, 129, 0.08);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
}

.solution-btn:hover {
  background: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.3);
}

.solution-box {
  padding: 1rem 1.125rem;
  background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 0.625rem;
}

.sol-section {
  margin-bottom: 1rem;
}

.sol-section:last-child {
  margin-bottom: 0;
}

.sol-label {
  margin: 0 0 0.5rem;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-success);
}

.sol-text {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.65;
  color: var(--color-text-primary);
}

.key-points-list {
  margin: 0;
  padding-left: 1.25rem;
  font-size: 0.875rem;
  line-height: 1.65;
  color: var(--color-text-primary);
}

.key-points-list li {
  margin-bottom: 0.25rem;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
