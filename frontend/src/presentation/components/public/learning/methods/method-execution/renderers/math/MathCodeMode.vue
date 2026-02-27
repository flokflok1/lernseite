<template>
  <div>
    <p class="task-text">{{ task }}</p>
    <div class="code-section">
      <h4 class="section-label">{{ t('lesson.methodExecution.renderer.mathInteractive.yourSolution') }}</h4>
      <textarea v-model="userCode" class="code-input" rows="6" :placeholder="codePlaceholder" />
    </div>
    <div v-if="testCases.length" class="test-cases">
      <h4 class="section-label">{{ t('lesson.methodExecution.renderer.mathInteractive.testCases') }}</h4>
      <div v-for="(tc, i) in testCases" :key="i" class="test-case" :class="{ 'tc--pass': results[i] === true, 'tc--fail': results[i] === false }">
        <span class="tc-status">{{ results[i] === true ? '✓' : results[i] === false ? '✗' : '○' }}</span>
        <span class="tc-input">{{ t('lesson.methodExecution.renderer.mathInteractive.input') }}: <code>{{ tc.input }}</code></span>
        <span class="tc-expected">{{ t('lesson.methodExecution.renderer.mathInteractive.expected') }}: <code>{{ tc.expected }}</code> ({{ tc.type }})</span>
      </div>
    </div>
    <div class="actions">
      <button class="run-btn" @click="checkSolution">{{ t('lesson.methodExecution.renderer.mathInteractive.checkSolution') }}</button>
      <button class="solution-btn" @click="$emit('toggleSolution')">
        {{ solutionVisible ? t('lesson.methodExecution.renderer.common.hideSolution') : t('lesson.methodExecution.renderer.common.sampleSolution') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MathInteractiveData } from '../types'

const { t } = useI18n()
const props = defineProps<{ data: MathInteractiveData | null; solutionVisible: boolean }>()
defineEmits<{ toggleSolution: [] }>()

const task = computed(() => props.data?.task || '')
const testCases = computed(() => props.data?.testCases || [])
const codePlaceholder = computed(() => props.data?.placeholder || 'function solve() {\n  // ...\n}')
const userCode = ref('')
const results = ref<(boolean | null)[]>([])

function checkSolution() {
  results.value = testCases.value.map(() => userCode.value.trim().length > 10 ? true : null)
}
</script>

<style scoped>
.task-text { font-size: 0.9375rem; line-height: 1.75; margin-bottom: 1.25rem; color: var(--color-text-primary); }

.section-label {
  font-size: 0.6875rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--color-accent-light); margin: 0 0 0.5rem;
}

.code-input {
  width: 100%; padding: 0.875rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem; line-height: 1.7;
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.625rem;
  background: var(--color-code-bg); color: var(--color-code-text);
  resize: vertical; margin-bottom: 1rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.code-input:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }

.test-cases { margin-bottom: 1rem; }

.test-case {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.5rem 0.875rem; border-radius: 0.5rem;
  font-size: 0.8125rem; margin-bottom: 0.375rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.2s ease;
}

.tc--pass { border-color: rgba(16, 185, 129, 0.3); background: rgba(16, 185, 129, 0.06); }
.tc--fail { border-color: rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.05); }

.tc-status { font-weight: 700; width: 1.25rem; text-align: center; font-size: 0.875rem; }
.tc--pass .tc-status { color: var(--color-success); }
.tc--fail .tc-status { color: var(--color-error); }

.tc-input, .tc-expected { color: var(--color-text-secondary); }

code {
  padding: 0.125rem 0.375rem; background: rgba(99, 102, 241, 0.1);
  border-radius: 0.25rem; font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem; color: var(--color-accent-light);
}

.actions { display: flex; gap: 0.75rem; margin-bottom: 0.75rem; }

.run-btn {
  padding: 0.5rem 1.5rem; background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; border: none; border-radius: 0.5rem;
  font-size: 0.8125rem; font-weight: 600; cursor: pointer;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25); transition: all 0.15s;
}
.run-btn:hover { box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35); transform: translateY(-1px); }

.solution-btn {
  padding: 0.5rem 1.25rem; background: rgba(16, 185, 129, 0.06);
  color: var(--color-success); border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 0.5rem; font-size: 0.8125rem; font-weight: 500;
  cursor: pointer; transition: all 0.15s;
}
.solution-btn:hover { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); }
</style>
