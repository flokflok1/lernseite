<template>
  <div class="renderer">
    <div class="code-block">
      <div v-for="(line, li) in codeLines" :key="li" class="code-line">
        <span class="line-num">{{ li + 1 }}</span>
        <span class="line-content">
          <template v-for="(part, pi) in parseLine(line, li)" :key="pi">
            <input
              v-if="part.isBlank"
              v-model="answers[part.blankIndex!]"
              class="blank-input"
              :class="{ 'blank--correct': checked && isCorrect(part.blankIndex!), 'blank--wrong': checked && !isCorrect(part.blankIndex!) }"
              :placeholder="getHint(part.blankIndex!)"
              :disabled="checked"
              :size="Math.max(8, (getHint(part.blankIndex!) || '').length)"
            />
            <span v-else>{{ part.text }}</span>
          </template>
        </span>
      </div>
    </div>
    <div class="actions">
      <button v-if="!checked" class="check-btn" :disabled="answers.some(a => !a.trim())" @click="checked = true">{{ t('lesson.methodExecution.renderer.common.check') }}</button>
      <button v-else class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>
    <div v-if="checked" class="score">{{ t('lesson.methodExecution.renderer.cloze.correctCount', { correct: correctCount, total: blanks.length }) }}</div>
    <Transition name="fade">
      <div v-if="checked" class="solution-box">
        <h4 class="sol-label">{{ t('lesson.methodExecution.renderer.common.solution') }}</h4>
        <pre class="sol-code">{{ solution?.completedCode || '' }}</pre>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ClozeData, ClozeSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: ClozeData | null; solution: ClozeSolution | null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const checked = ref(false)
const blanks = computed(() => props.data?.blanks || [])
const answers = ref<string[]>(blanks.value.map(() => ''))
const codeLines = computed(() => (props.data?.codeTemplate || '').split('\n'))

watch(() => props.data, () => reset(), { deep: true })

const correctCount = computed(() =>
  blanks.value.filter((b: any, i: number) => answers.value[i]?.trim().toLowerCase() === b.answer?.toLowerCase()).length
)

interface Part { text?: string; isBlank?: boolean; blankIndex?: number }

function parseLine(line: string, lineIndex: number): Part[] {
  const parts: Part[] = []
  const segments = line.split('___')
  segments.forEach((seg, i) => {
    if (seg) parts.push({ text: seg })
    if (i < segments.length - 1) {
      const idx = countBlanksUpTo(codeLines.value, lineIndex, i)
      parts.push({ isBlank: true, blankIndex: idx })
    }
  })
  return parts
}

function countBlanksUpTo(lines: string[], targetLineIndex: number, blankInLine: number): number {
  let count = 0
  for (let li = 0; li < lines.length; li++) {
    const n = (lines[li].match(/___/g) || []).length
    if (li === targetLineIndex) return count + blankInLine
    count += n
  }
  return count
}

watch(checked, (val) => {
  if (val) emit('complete', correctCount.value, blanks.value.length)
})

function getHint(idx: number): string { return blanks.value[idx]?.hint || '' }
function isCorrect(idx: number): boolean {
  return answers.value[idx]?.trim().toLowerCase() === blanks.value[idx]?.answer?.toLowerCase()
}
function reset() { checked.value = false; answers.value = blanks.value.map(() => '') }
</script>

<style scoped>
.code-block {
  background: var(--color-code-bg);
  border-radius: 0.75rem;
  padding: 1rem 0;
  margin-bottom: 1.25rem;
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.code-line {
  display: flex;
  align-items: center;
  padding: 0.125rem 1rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem;
  line-height: 1.8;
  color: var(--color-code-text);
}

.line-num {
  width: 2rem;
  text-align: right;
  color: var(--color-text-tertiary);
  margin-right: 1rem;
  flex-shrink: 0;
  font-size: 0.75rem;
  user-select: none;
}

.blank-input {
  background: rgba(99, 102, 241, 0.12);
  border: 1px dashed rgba(99, 102, 241, 0.45);
  border-radius: 0.25rem;
  padding: 0.125rem 0.5rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem;
  color: var(--color-accent-light);
  outline: none;
  transition: all 0.15s;
}

.blank-input:focus {
  border-color: var(--color-accent);
  background: rgba(99, 102, 241, 0.2);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.12);
}

.blank--correct {
  border-color: var(--color-success);
  border-style: solid;
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-success);
}

.blank--wrong {
  border-color: var(--color-error);
  border-style: solid;
  background: rgba(239, 68, 68, 0.15);
  color: var(--color-error);
}

.actions {
  display: flex;
  gap: 0.625rem;
  margin-bottom: 0.75rem;
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

.check-btn:disabled {
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

.score {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-accent-light);
  margin-bottom: 0.75rem;
}

.solution-box {
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
  padding: 0.75rem;
  background: var(--color-code-bg);
  color: var(--color-code-text);
  border-radius: 0.5rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace;
  font-size: 0.8125rem;
  white-space: pre-wrap;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
