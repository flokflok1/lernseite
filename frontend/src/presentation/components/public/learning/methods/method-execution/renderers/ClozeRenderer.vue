<template>
  <div class="renderer">
    <!-- Sentence mode (exam-style cloze) -->
    <div v-if="!isCodeMode" class="sentence-block">
      <div v-for="(line, li) in codeLines" :key="li" class="sentence-line">
        <span class="sentence-num">{{ li + 1 }}.</span>
        <span class="sentence-content">
          <template v-for="(part, pi) in parseLine(line, li)" :key="pi">
            <input
              v-if="part.isBlank"
              v-model="answers[part.blankIndex!]"
              class="blank-input blank-input--sentence"
              :class="{ 'blank--correct': checked && isCorrect(part.blankIndex!), 'blank--wrong': checked && !isCorrect(part.blankIndex!) }"
              :placeholder="getHint(part.blankIndex!)"
              :disabled="checked"
              :size="Math.max(12, (getHint(part.blankIndex!) || '').length + 4)"
            />
            <span v-else>{{ part.text }}</span>
          </template>
        </span>
      </div>
    </div>

    <!-- Code mode (original code-cloze) -->
    <div v-else class="code-block">
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
    <div v-if="checked" class="score">{{ t('lesson.methodExecution.renderer.cloze.correctCount', { correct: correctCount, total: normalizedBlanks.length }) }}</div>
    <Transition name="fade">
      <div v-if="checked" class="solution-box">
        <h4 class="sol-label">{{ t('lesson.methodExecution.renderer.common.solution') }}</h4>
        <div v-if="!isCodeMode" class="sol-sentences">
          <div v-for="(blank, i) in normalizedBlanks" :key="i" class="sol-sentence">
            <strong>{{ i + 1 }}.</strong> {{ blank.answers.join(' / ') }}
          </div>
        </div>
        <pre v-else class="sol-code">{{ solution?.completedCode || '' }}</pre>
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

interface NormalizedBlank {
  hint: string
  answers: string[] // multiple accepted answers
}

// Detect mode: sentences = exam-style text, blanks+codeTemplate = code-style
const isCodeMode = computed(() => {
  const d = props.data as any
  if (!d) return true
  return !d.sentences || (d.codeTemplate && d.blanks)
})

// Normalize both formats into a unified internal representation
const normalizedBlanks = computed<NormalizedBlank[]>(() => {
  const d = props.data as any
  if (!d) return []

  // Exam sentences format
  if (d.sentences && !d.codeTemplate) {
    const result: NormalizedBlank[] = []
    for (const s of d.sentences) {
      if (!s.text?.trim()) continue
      const blankCount = (s.text.match(/\{\{blank\}\}/g) || []).length
      const answers = (s.answers || []).filter((a: string) => a?.trim())
      for (let i = 0; i < Math.max(blankCount, 1); i++) {
        result.push({ hint: '', answers: answers.length ? answers : [''] })
      }
    }
    return result
  }

  // Standard blanks format
  return (d.blanks || []).map((b: any) => ({
    hint: b.hint || '',
    answers: [b.answer || ''],
  }))
})

const codeLines = computed(() => {
  const d = props.data as any
  if (!d) return []

  // Exam sentences: build template from sentences
  if (d.sentences && !d.codeTemplate) {
    return d.sentences
      .filter((s: any) => s.text?.trim())
      .map((s: any) => s.text.replace(/\{\{blank\}\}/g, '___'))
  }

  return (d.codeTemplate || '').split('\n')
})

const answers = ref<string[]>(normalizedBlanks.value.map(() => ''))

watch(() => props.data, () => reset(), { deep: true })

const correctCount = computed(() =>
  normalizedBlanks.value.filter((b, i) => {
    const userAnswer = answers.value[i]?.trim().toLowerCase()
    if (!userAnswer) return false
    return b.answers.some(a => a.toLowerCase() === userAnswer)
  }).length
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
  if (val) emit('complete', correctCount.value, normalizedBlanks.value.length)
})

function getHint(idx: number): string { return normalizedBlanks.value[idx]?.hint || '' }
function isCorrect(idx: number): boolean {
  const userAnswer = answers.value[idx]?.trim().toLowerCase()
  if (!userAnswer) return false
  return normalizedBlanks.value[idx]?.answers.some(a => a.toLowerCase() === userAnswer) || false
}
function reset() { checked.value = false; answers.value = normalizedBlanks.value.map(() => '') }
</script>

<style scoped>
/* Sentence mode (exam-style) */
.sentence-block {
  background: var(--color-surface-secondary, #f9fafb);
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin-bottom: 1.25rem;
  border: 1px solid var(--color-border, #e5e7eb);
}

:root.dark .sentence-block {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.06);
}

.sentence-line {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  padding: 0.625rem 0;
  font-size: 0.9375rem;
  line-height: 1.75;
  color: var(--color-text-primary, #111827);
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

:root.dark .sentence-line {
  color: #e2e8f0;
  border-bottom-color: rgba(255, 255, 255, 0.04);
}

.sentence-line:last-child {
  border-bottom: none;
}

.sentence-num {
  font-weight: 700;
  color: var(--color-primary, #6366f1);
  flex-shrink: 0;
  min-width: 1.5rem;
}

.sentence-content {
  flex: 1;
}

.blank-input--sentence {
  font-family: inherit;
  font-size: 0.9375rem;
  padding: 0.25rem 0.75rem;
  min-width: 120px;
}

/* Code mode (original) */
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

/* Shared blank input styles */
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

.sol-sentences {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.sol-sentence {
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
  padding: 0.25rem 0;
}

:root.dark .sol-sentence {
  color: #cbd5e1;
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
