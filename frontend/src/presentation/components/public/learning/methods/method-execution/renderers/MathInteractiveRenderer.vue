<template>
  <div class="renderer">
    <!-- Auto-detect math mode and delegate to sub-component -->
    <MathProblemsMode v-if="mathMode === 'problems'" :data="data" />
    <MathEquationsMode v-else-if="mathMode === 'equations'" :data="data" />
    <MathStepsMode v-else-if="mathMode === 'steps'" :data="data" />
    <MathCodeMode v-else :data="data" :solution-visible="showSolution" @toggle-solution="showSolution = !showSolution" />

    <!-- Shared: Bonus task -->
    <div v-if="bonusTask" class="bonus">
      <strong>{{ t('lesson.methodExecution.renderer.common.bonus') }}:</strong> {{ bonusTask }}
    </div>

    <!-- Shared: Solution reveal (code mode) -->
    <Transition name="fade">
      <div v-if="showSolution && solution" class="solution-box">
        <pre v-if="solution.code" class="sol-code">{{ solution.code }}</pre>
        <p v-if="solution.explanation" class="sol-explanation">{{ solution.explanation }}</p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MathInteractiveData, MathInteractiveSolution } from './types'
import MathProblemsMode from './math/MathProblemsMode.vue'
import MathEquationsMode from './math/MathEquationsMode.vue'
import MathStepsMode from './math/MathStepsMode.vue'
import MathCodeMode from './math/MathCodeMode.vue'

const { t } = useI18n()
const props = defineProps<{ data: MathInteractiveData | null; solution: MathInteractiveSolution | null }>()
const showSolution = ref(false)

type MathMode = 'problems' | 'equations' | 'steps' | 'testCases'

const mathMode = computed<MathMode>(() => {
  if (props.data?.problems?.length) return 'problems'
  if (props.data?.equations?.length) return 'equations'
  if (props.data?.steps?.length) return 'steps'
  return 'testCases'
})

const bonusTask = computed(() => props.data?.bonusTask || '')
</script>

<style scoped>
.bonus {
  padding: 0.875rem 1rem;
  background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(245, 158, 11, 0.15);
  border-radius: 0.625rem;
  font-size: 0.875rem;
  margin-top: 1rem;
  color: var(--color-warning);
  line-height: 1.6;
}

.bonus strong { color: var(--color-warning); }

.solution-box {
  padding: 1rem 1.125rem;
  background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 0.625rem;
  margin-top: 0.75rem;
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

.sol-explanation {
  margin: 0.75rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  font-style: italic;
  line-height: 1.6;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
