<script setup lang="ts">
import { ref, computed } from 'vue'

interface CalculatorStep {
  keys: string
  result: string
  note: string
}

interface CalculatorHint {
  mode?: string
  setup_note?: string
  steps: CalculatorStep[]
  exam_tip?: string
}

interface Props {
  hint: CalculatorHint | null
}

const props = defineProps<Props>()

const expanded = ref(false)
const completedSteps = ref<Set<number>>(new Set())

const hasHint = computed(() => props.hint && props.hint.steps?.length > 0)

function toggleStep(idx: number) {
  if (completedSteps.value.has(idx)) {
    completedSteps.value.delete(idx)
  } else {
    completedSteps.value.add(idx)
  }
}

function reset() {
  completedSteps.value.clear()
}
</script>

<template>
  <aside v-if="hasHint && hint" class="calc-panel" :class="{ 'calc-expanded': expanded }">
    <button
      type="button"
      class="calc-toggle"
      @click="expanded = !expanded"
      :aria-expanded="expanded"
    >
      <span class="calc-icon">📱</span>
      <span class="calc-title">Casio FX-991DE X — Schritt-für-Schritt</span>
      <span class="calc-chev" :class="{ 'calc-chev-open': expanded }">▾</span>
    </button>

    <div v-if="expanded" class="calc-body">
      <div v-if="hint.mode" class="calc-mode">
        <strong>Modus:</strong> {{ hint.mode }}
      </div>

      <p v-if="hint.setup_note" class="calc-setup">
        <strong>Setup:</strong> {{ hint.setup_note }}
      </p>

      <ol class="calc-steps">
        <li
          v-for="(step, idx) in hint.steps"
          :key="idx"
          class="calc-step"
          :class="{ 'calc-step-done': completedSteps.has(idx) }"
        >
          <button
            type="button"
            class="calc-step-check"
            :aria-label="completedSteps.has(idx) ? 'Schritt rückgängig machen' : 'Schritt als erledigt markieren'"
            @click="toggleStep(idx)"
          >
            <span v-if="completedSteps.has(idx)">✓</span>
            <span v-else>{{ idx + 1 }}</span>
          </button>
          <div class="calc-step-body">
            <div class="calc-step-keys">{{ step.keys }}</div>
            <div class="calc-step-result">
              <span class="calc-step-arrow">→</span>
              <span class="calc-step-value">{{ step.result }}</span>
            </div>
            <div v-if="step.note" class="calc-step-note">{{ step.note }}</div>
          </div>
        </li>
      </ol>

      <div v-if="hint.exam_tip" class="calc-tip">
        <strong>💡 Prüfungstipp:</strong> {{ hint.exam_tip }}
      </div>

      <button
        v-if="completedSteps.size > 0"
        type="button"
        class="calc-reset"
        @click="reset"
      >
        ↺ Schritte zurücksetzen
      </button>
    </div>
  </aside>
</template>

<style scoped>
.calc-panel {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #f8fafc;
  margin: 1rem 0;
  overflow: hidden;
}

.calc-expanded {
  border-color: #6366f1;
  box-shadow: 0 1px 6px rgba(99, 102, 241, 0.15);
}

.calc-toggle {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.9rem;
  background: transparent;
  border: 0;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  text-align: left;
}

.calc-toggle:hover {
  background: #eef2ff;
}

.calc-icon {
  font-size: 1.2rem;
}

.calc-title {
  flex: 1;
}

.calc-chev {
  font-size: 0.9rem;
  color: #64748b;
  transition: transform 0.15s;
}

.calc-chev-open {
  transform: rotate(180deg);
}

.calc-body {
  padding: 0.3rem 0.9rem 0.9rem;
  border-top: 1px solid #e2e8f0;
  background: #fff;
}

.calc-mode {
  font-size: 0.82rem;
  color: #4338ca;
  padding: 0.4rem 0.6rem;
  background: #eef2ff;
  border-radius: 4px;
  margin: 0.4rem 0;
}

.calc-setup {
  margin: 0.4rem 0 0.6rem;
  font-size: 0.82rem;
  color: #475569;
  line-height: 1.4;
  padding: 0.3rem 0;
}

.calc-steps {
  list-style: none;
  padding: 0;
  margin: 0.4rem 0;
}

.calc-step {
  display: flex;
  gap: 0.6rem;
  padding: 0.5rem 0.4rem;
  border-left: 3px solid #e2e8f0;
  margin: 0.25rem 0;
  border-radius: 0 4px 4px 0;
  transition: background 0.15s;
}

.calc-step:hover {
  background: #f8fafc;
}

.calc-step-done {
  border-left-color: #16a34a;
  background: #f0fdf4;
  opacity: 0.75;
}

.calc-step-done .calc-step-keys {
  text-decoration: line-through;
}

.calc-step-check {
  width: 24px;
  height: 24px;
  min-width: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1.5px solid #cbd5e1;
  background: #fff;
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}

.calc-step-check:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.calc-step-done .calc-step-check {
  background: #16a34a;
  border-color: #16a34a;
  color: #fff;
}

.calc-step-body {
  flex: 1;
  min-width: 0;
}

.calc-step-keys {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 0.86rem;
  font-weight: 600;
  color: #0f172a;
  background: #f1f5f9;
  padding: 3px 6px;
  border-radius: 3px;
  display: inline-block;
  word-break: break-all;
}

.calc-step-result {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 3px;
  font-size: 0.85rem;
}

.calc-step-arrow {
  color: #94a3b8;
}

.calc-step-value {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-weight: 700;
  color: #7c3aed;
  background: #faf5ff;
  padding: 2px 6px;
  border-radius: 3px;
}

.calc-step-note {
  font-size: 0.78rem;
  color: #475569;
  margin-top: 3px;
  line-height: 1.35;
}

.calc-tip {
  margin: 0.8rem 0 0.3rem;
  padding: 0.6rem 0.7rem;
  background: #fefce8;
  border-left: 3px solid #eab308;
  border-radius: 3px;
  font-size: 0.82rem;
  color: #713f12;
  line-height: 1.4;
}

.calc-reset {
  display: block;
  margin: 0.5rem 0 0;
  padding: 0.3rem 0.6rem;
  background: transparent;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 0.78rem;
  color: #64748b;
  cursor: pointer;
}

.calc-reset:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
}
</style>
