<template>
  <div class="renderer">
    <div v-if="scenario" class="scenario-text" v-html="renderMarkdown(scenario)" />
    <div v-if="requirements.length" class="requirements">
      <h4 class="section-label">{{ t('lesson.methodExecution.renderer.scenario.requirements') }}</h4>
      <ul class="req-list">
        <li v-for="(r, i) in requirements" :key="i" class="req-item">
          <input v-model="checked[i]" type="checkbox" class="req-check" />
          <span :class="{ 'req-done': checked[i] }">{{ r }}</span>
        </li>
      </ul>
    </div>
    <div v-if="hints.length" class="hints">
      <button class="hints-toggle" @click="showHints = !showHints">
        {{ showHints ? t('lesson.methodExecution.renderer.scenario.hideHints') : t('lesson.methodExecution.renderer.scenario.showHints') }} {{ t('lesson.methodExecution.renderer.scenario.hintsCount', { count: hints.length }) }}
      </button>
      <Transition name="fade">
        <ul v-if="showHints" class="hint-list">
          <li v-for="(h, i) in hints" :key="i">{{ h }}</li>
        </ul>
      </Transition>
    </div>
    <div class="code-section">
      <h4 class="section-label">{{ t('lesson.methodExecution.renderer.scenario.yourSolution') }}</h4>
      <textarea v-model="userCode" class="code-input" rows="10" :placeholder="t('lesson.methodExecution.renderer.scenario.codePlaceholder')" />
    </div>
    <button class="solution-btn" @click="showSolution = !showSolution">
      {{ showSolution ? t('lesson.methodExecution.renderer.common.hideSolution') : t('lesson.methodExecution.renderer.common.showSolution') }}
    </button>
    <Transition name="fade">
      <div v-if="showSolution && solution?.code" class="solution-box">
        <h4 class="sol-label">{{ t('lesson.methodExecution.renderer.common.sampleSolution') }}</h4>
        <pre class="sol-code">{{ solution.code }}</pre>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from './markdown'
import type { ScenarioData, ScenarioSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: ScenarioData | null; solution: ScenarioSolution | null }>()
const showHints = ref(false)
const showSolution = ref(false)
const userCode = ref('')
const checked = ref<boolean[]>([])
const scenario = computed(() => props.data?.scenario || '')
const requirements = computed(() => props.data?.requirements || [])
const hints = computed(() => props.data?.hints || [])

// Sync checked array when requirements change
watch(requirements, (r) => {
  checked.value = r.map(() => false)
}, { immediate: true })

watch(() => props.data, () => {
  showHints.value = false
  showSolution.value = false
  userCode.value = ''
}, { deep: true })
</script>

<style scoped>
.scenario-text {
  font-size: 0.9375rem;
  line-height: 1.75;
  margin-bottom: 1.25rem;
  padding: 1.125rem;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.75rem;
  color: var(--color-text-primary);
}

.section-label {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-accent-light);
  margin: 0 0 0.5rem;
}

.req-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.req-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.5rem;
  color: var(--color-text-primary);
  transition: border-color 0.15s;
}

.req-item:has(.req-check:checked) {
  border-color: rgba(16, 185, 129, 0.2);
  background: rgba(16, 185, 129, 0.04);
}

.req-check {
  width: 1.125rem;
  height: 1.125rem;
  accent-color: var(--color-success);
  flex-shrink: 0;
}

.req-done {
  text-decoration: line-through;
  opacity: 0.5;
  color: var(--color-text-tertiary);
}

.hints-toggle {
  padding: 0.375rem 0.875rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.04);
  color: var(--color-text-secondary);
  cursor: pointer;
  margin-bottom: 0.75rem;
  transition: all 0.15s;
}

.hints-toggle:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--color-text-primary);
}

.hint-list {
  padding-left: 1.25rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin: 0 0 1.25rem;
  line-height: 1.6;
}

.hint-list li {
  margin-bottom: 0.375rem;
}

.code-input {
  width: 100%;
  padding: 0.875rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem;
  line-height: 1.7;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.625rem;
  background: var(--color-code-bg);
  color: var(--color-code-text);
  resize: vertical;
  margin-bottom: 1rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.code-input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.solution-btn {
  padding: 0.5rem 1.25rem;
  background: rgba(16, 185, 129, 0.06);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.solution-btn:hover {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
}

.solution-box {
  margin-top: 1rem;
  padding: 1rem 1.125rem;
  background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 0.625rem;
}

.sol-label {
  margin: 0 0 0.5rem;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-success);
}

.sol-code {
  margin: 0;
  padding: 0.875rem;
  background: var(--color-code-bg);
  color: var(--color-code-text);
  border-radius: 0.5rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem;
  line-height: 1.7;
  white-space: pre-wrap;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
