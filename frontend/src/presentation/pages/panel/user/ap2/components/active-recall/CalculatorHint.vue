<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CalculatorHint } from '@/infrastructure/api/clients/panel/user/exams/ap2-modules.api'

interface Props {
  hint: CalculatorHint | null | undefined
}
const props = defineProps<Props>()

const expanded = ref(false)

const hasContent = computed(() => {
  const h = props.hint
  if (!h) return false
  return !!(h.steps?.length || h.formula || h.example || h.summary || h.mode)
})

function toggle() { expanded.value = !expanded.value }
</script>

<template>
  <div v-if="hasContent" class="calc">
    <button
      type="button"
      class="calc-toggle"
      :class="{ 'calc-toggle--open': expanded }"
      @click="toggle"
    >
      <span class="calc-head-label">
        {{ $t('ap2Trainer.calculator.heading') }}
        <span v-if="hint?.model" class="calc-model">— {{ hint.model }}</span>
      </span>
      <span class="calc-arrow">{{ expanded ? '▾' : '▸' }}</span>
    </button>

    <div v-if="expanded" class="calc-body">
      <p v-if="hint?.summary" class="calc-summary">{{ hint.summary }}</p>

      <div v-if="hint?.mode" class="calc-row">
        <span class="calc-row-k">{{ $t('ap2Trainer.calculator.mode') }}:</span>
        <code class="calc-code">{{ hint.mode }}</code>
      </div>

      <div v-if="hint?.formula" class="calc-row">
        <span class="calc-row-k">{{ $t('ap2Trainer.calculator.formula') }}:</span>
        <code class="calc-code">{{ hint.formula }}</code>
      </div>

      <div v-if="hint?.example" class="calc-row">
        <span class="calc-row-k">{{ $t('ap2Trainer.calculator.example') }}:</span>
        <code class="calc-code">{{ hint.example }}</code>
      </div>

      <div v-if="hint?.steps?.length" class="calc-steps">
        <div class="calc-row-k calc-steps-title">
          {{ $t('ap2Trainer.calculator.steps') }}:
        </div>
        <ol class="calc-step-list">
          <li v-for="(step, i) in hint.steps" :key="i" class="calc-step">
            <div class="calc-step-label">{{ step.label }}</div>
            <div v-if="step.keys" class="calc-step-keys">
              <span class="calc-k-label">
                {{ $t('ap2Trainer.calculator.keys') }}:
              </span>
              <code class="calc-code">{{ step.keys }}</code>
            </div>
            <div v-if="step.display" class="calc-step-display">
              <span class="calc-k-label">
                {{ $t('ap2Trainer.calculator.display') }}:
              </span>
              <code class="calc-code calc-display">{{ step.display }}</code>
            </div>
            <div v-if="step.note" class="calc-step-note">{{ step.note }}</div>
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calc {
  border: 1px solid var(--color-border, #334155);
  border-left: 3px solid #8b5cf6;
  border-radius: 6px;
  margin-bottom: 0.8rem;
  background: rgba(139,92,246,0.05);
}

.calc-toggle {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.8rem;
  background: transparent;
  border: 0;
  color: #c4b5fd;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.88rem;
}
.calc-toggle:hover { background: rgba(139,92,246,0.08); }
.calc-toggle--open { border-bottom: 1px dashed #475569; }

.calc-head-label { display: flex; align-items: baseline; gap: 0.4rem; flex-wrap: wrap; }
.calc-model { color: #94a3b8; font-size: 0.75rem; font-weight: 400; }
.calc-arrow { color: #94a3b8; font-size: 0.9rem; }

.calc-body {
  padding: 0.8rem 1rem;
  color: #e2e8f0;
  font-size: 0.87rem;
  line-height: 1.5;
}

.calc-summary { margin: 0 0 0.7rem 0; color: #cbd5e1; }

.calc-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
  align-items: baseline;
  flex-wrap: wrap;
}
.calc-row-k { color: #94a3b8; font-size: 0.78rem; min-width: 70px; }
.calc-code {
  background: #0f172a;
  border: 1px solid #334155;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Fira Code', ui-monospace, monospace;
  color: #fbbf24;
  font-size: 0.83em;
}

.calc-steps { margin-top: 0.6rem; }
.calc-steps-title { margin-bottom: 0.3rem; }

.calc-step-list {
  counter-reset: step;
  list-style: none;
  padding: 0;
  margin: 0;
}
.calc-step {
  counter-increment: step;
  padding: 0.5rem 0.7rem 0.5rem 2rem;
  margin-bottom: 0.4rem;
  background: rgba(0,0,0,0.2);
  border-radius: 4px;
  position: relative;
}
.calc-step::before {
  content: counter(step);
  position: absolute;
  left: 0.5rem;
  top: 0.5rem;
  background: #8b5cf6;
  color: #fff;
  width: 1.2rem;
  height: 1.2rem;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
}

.calc-step-label { color: #f1f5f9; font-weight: 500; margin-bottom: 0.3rem; }
.calc-step-keys, .calc-step-display {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 0.2rem;
  align-items: baseline;
  flex-wrap: wrap;
}
.calc-k-label {
  color: #94a3b8;
  font-size: 0.72rem;
  min-width: 58px;
}
.calc-display { background: #042f2e; color: #86efac; border-color: #164e63; }
.calc-step-note {
  color: #94a3b8;
  font-size: 0.78rem;
  font-style: italic;
  margin-top: 0.2rem;
}
</style>
