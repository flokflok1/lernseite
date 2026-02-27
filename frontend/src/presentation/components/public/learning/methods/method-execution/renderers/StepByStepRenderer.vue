<template>
  <div class="renderer">
    <div class="step-counter">{{ t('lesson.methodExecution.renderer.stepByStep.stepOf', { current: current + 1, total: steps.length }) }}</div>
    <div class="step-progress">
      <div class="step-bar" :style="{ width: `${steps.length ? ((current + 1) / steps.length) * 100 : 0}%` }" />
    </div>
    <div v-if="currentStep" class="step-card">
      <div class="step-number">{{ currentStep.step || current + 1 }}</div>
      <h3 class="step-title">{{ currentStep.title }}</h3>
      <div class="step-content" v-html="renderMarkdown(currentStep.content || '')" />
    </div>
    <div class="step-nav">
      <button :disabled="current === 0" class="step-btn" @click="current--">&larr; {{ t('lesson.methodExecution.renderer.stepByStep.back') }}</button>
      <div class="step-dots">
        <span v-for="(_, i) in steps" :key="i" class="dot" :class="{ 'dot--active': i === current, 'dot--done': i < current }" @click="current = i" />
      </div>
      <button v-if="current < steps.length - 1" class="step-btn step-btn--primary" @click="current++">{{ t('lesson.methodExecution.renderer.stepByStep.next') }} &rarr;</button>
      <button v-else class="step-btn step-btn--success" @click="done = true">{{ t('lesson.methodExecution.renderer.stepByStep.done') }} ✓</button>
    </div>
    <Transition name="fade">
      <div v-if="done && solution" class="done-box">
        <p v-if="solution.expectedOutput"><strong>{{ t('lesson.methodExecution.renderer.stepByStep.expectedOutput') }}:</strong> {{ solution.expectedOutput }}</p>
        <ul v-if="solution.commonErrors">
          <li v-for="(e, i) in solution.commonErrors" :key="i">{{ e }}</li>
        </ul>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { renderMarkdown } from './markdown'
import type { StepByStepData, StepByStepSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: StepByStepData | null; solution: StepByStepSolution | null }>()
const current = ref(0)
const done = ref(false)
const steps = computed(() => props.data?.steps || [])
const currentStep = computed(() => steps.value[current.value])

watch(() => props.data, () => {
  current.value = 0
  done.value = false
}, { deep: true })
</script>

<style scoped>
.step-counter {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.5rem;
}

.step-progress {
  height: 3px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  margin-bottom: 1.25rem;
  overflow: hidden;
}

.step-bar {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #818cf8);
  border-radius: 2px;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-card {
  padding: 1.25rem 1.375rem;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.75rem;
  margin-bottom: 1.25rem;
}

.step-number {
  width: 1.75rem;
  height: 1.75rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.75rem;
  margin-bottom: 0.75rem;
}

.step-title {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.step-content {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.65;
  color: var(--color-text-secondary);
}

.step-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.step-dots {
  display: flex;
  gap: 0.375rem;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.dot:hover { background: rgba(255, 255, 255, 0.2); }
.dot--active { background: var(--color-accent); transform: scale(1.3); box-shadow: 0 0 6px rgba(99, 102, 241, 0.4); }
.dot--done { background: var(--color-success); }

.step-btn {
  padding: 0.4375rem 1rem;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.04);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.step-btn:hover:not(:disabled) { background: rgba(255, 255, 255, 0.08); }
.step-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.step-btn--primary {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}

.step-btn--primary:hover { box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35); transform: translateY(-1px); }

.step-btn--success {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
}

.step-btn--success:hover { box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); transform: translateY(-1px); }

.done-box {
  margin-top: 1.25rem;
  padding: 1rem 1.125rem;
  background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 0.625rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.done-box ul { margin: 0.5rem 0 0; padding-left: 1.25rem; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
