<template>
  <div class="renderer">
    <div v-if="renderedContent" class="content-block" v-html="renderedContent" />
    <ul v-if="keyPoints.length" class="key-points">
      <li v-for="(point, i) in keyPoints" :key="i" class="key-point">
        <span class="kp-bullet">{{ i + 1 }}</span>
        <span>{{ point }}</span>
      </li>
    </ul>
    <div v-if="solution" class="understood-section">
      <label class="understood-label">
        <input v-model="understood" type="checkbox" class="understood-check" />
        <span>{{ t('lesson.methodExecution.renderer.deepExplanation.understood') }}</span>
      </label>
      <Transition name="fade">
        <div v-if="understood && solution.summary" class="summary-box">
          <h4 class="summary-title">{{ t('lesson.methodExecution.renderer.deepExplanation.summary') }}</h4>
          <p>{{ solution.summary }}</p>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from './markdown'
import type { DeepExplanationData, DeepExplanationSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: (DeepExplanationData & { content_html?: string; raw_text?: string }) | null; solution: DeepExplanationSolution | null }>()
const understood = ref(false)

const renderedContent = computed(() => renderMarkdown(props.data?.content || props.data?.content_html || props.data?.raw_text || ''))
const keyPoints = computed(() => props.data?.keyPoints || [])
</script>

<style scoped>
.content-block {
  line-height: 1.75;
  margin-bottom: 1.5rem;
  font-size: 0.9375rem;
  color: var(--color-text-primary);
}

.content-block :deep(code) {
  background: rgba(99, 102, 241, 0.1);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
  color: var(--color-accent-light);
}

.key-points {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.key-point {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(99, 102, 241, 0.04);
  border: 1px solid rgba(99, 102, 241, 0.08);
  border-radius: 0.625rem;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--color-text-primary);
}

.kp-bullet {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6875rem;
  font-weight: 700;
}

.understood-section {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 1rem;
}

.understood-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.understood-check {
  width: 1.125rem;
  height: 1.125rem;
  accent-color: var(--color-success);
}

.summary-box {
  margin-top: 1rem;
  padding: 1rem 1.125rem;
  background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 0.625rem;
}

.summary-title {
  margin: 0 0 0.5rem;
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--color-success);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.summary-box p {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.65;
  color: var(--color-text-primary);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
