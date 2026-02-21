/**
 * ActivityPreviewPanel.vue
 *
 * Read-only learner-simulation preview for all 12 LM types.
 * Shows activity data as a student would see it.
 */
<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LessonActivity } from '../composables'

const props = defineProps<{
  activity: LessonActivity
  data: Record<string, unknown>
}>()

const { t } = useI18n()
const p = (key: string) => t(`panel.manualEditor.activityEditor.${key}`)
const empty = computed(() => t('panel.manualEditor.activityEditor.preview.emptyField'))

const lm = computed(() => props.activity.method_type)
const d = computed(() => props.data)

// Safe array access helper
const asArray = (val: unknown): Record<string, unknown>[] =>
  Array.isArray(val) ? val : []

const asString = (val: unknown): string =>
  typeof val === 'string' ? val : ''

const asStringArray = (val: unknown): string[] =>
  Array.isArray(val) ? val.filter(v => typeof v === 'string') : []
</script>

<template>
  <div class="preview-panel">
    <h3 class="preview-title">{{ activity.title }}</h3>
    <p v-if="activity.instructions" class="preview-instructions">{{ activity.instructions }}</p>

    <!-- LM00: Deep Explanation -->
    <template v-if="lm === 0">
      <div v-if="asString(d.content)" class="preview-text" v-text="asString(d.content)" />
      <div v-if="asStringArray(d.key_concepts).length" class="preview-tags">
        <span v-for="(tag, i) in asStringArray(d.key_concepts)" :key="i" class="preview-tag">{{ tag }}</span>
      </div>
      <div v-if="asString(d.summary)" class="preview-section">
        <strong>{{ p('lm00.summary') }}</strong>
        <p>{{ asString(d.summary) }}</p>
      </div>
    </template>

    <!-- LM01: Step by Step -->
    <template v-else-if="lm === 1">
      <ol class="preview-steps">
        <li v-for="(step, i) in asArray(d.steps)" :key="i" class="preview-step">
          <strong>{{ asString(step.title) || `${p('lm01.stepTitle')} ${i + 1}` }}</strong>
          <p>{{ asString(step.content) }}</p>
          <p v-if="asString(step.hint)" class="preview-hint">{{ asString(step.hint) }}</p>
        </li>
      </ol>
    </template>

    <!-- LM02: Interactive Theory -->
    <template v-else-if="lm === 2">
      <div v-for="(sec, i) in asArray(d.sections)" :key="i" class="preview-theory-section">
        <h4>{{ asString(sec.title) || `${p('lm02.sectionTitle')} ${i + 1}` }}</h4>
        <p>{{ asString(sec.content) }}</p>
        <details v-if="asString(sec.question)" class="preview-qa">
          <summary>{{ asString(sec.question) }}</summary>
          <p>{{ asString(sec.answer) || empty }}</p>
        </details>
      </div>
    </template>

    <!-- LM03: Diagram Visualization -->
    <template v-else-if="lm === 3">
      <p v-if="asString(d.description)">{{ asString(d.description) }}</p>
      <pre v-if="asString(d.diagram_code)" class="preview-code">{{ asString(d.diagram_code) }}</pre>
      <div v-if="asArray(d.elements).length" class="preview-elements">
        <div v-for="(el, i) in asArray(d.elements)" :key="i" class="preview-element">
          <strong>{{ asString(el.label) }}</strong>
          <span v-if="asString(el.description)"> — {{ asString(el.description) }}</span>
        </div>
      </div>
    </template>

    <!-- LM04: Example Scenario -->
    <template v-else-if="lm === 4">
      <div v-for="(sc, i) in asArray(d.scenarios)" :key="i" class="preview-scenario">
        <h4>{{ asString(sc.title) || `${p('lm04.scenarioTitle')} ${i + 1}` }}</h4>
        <div class="preview-scenario-body">
          <div class="preview-scenario-part">
            <strong>{{ p('lm04.scenarioSituation') }}</strong>
            <p>{{ asString(sc.situation) || empty }}</p>
          </div>
          <div class="preview-scenario-part">
            <strong>{{ p('lm04.scenarioSolution') }}</strong>
            <p>{{ asString(sc.solution) || empty }}</p>
          </div>
          <p v-if="asString(sc.takeaway)" class="preview-hint">{{ asString(sc.takeaway) }}</p>
        </div>
      </div>
    </template>

    <!-- LM05: Math Interactive -->
    <template v-else-if="lm === 5">
      <div v-for="(prob, i) in asArray(d.problems)" :key="i" class="preview-problem">
        <p class="preview-problem-text">{{ asString(prob.text) }}</p>
        <pre v-if="asString(prob.formula)" class="preview-formula">{{ asString(prob.formula) }}</pre>
        <details class="preview-qa">
          <summary>{{ p('lm05.problemSolution') }}</summary>
          <p>{{ asString(prob.solution) }}</p>
        </details>
      </div>
    </template>

    <!-- LM06: Flashcards -->
    <template v-else-if="lm === 6">
      <div v-for="(card, i) in asArray(d.cards)" :key="i" class="preview-flashcard">
        <div class="flashcard-front">{{ asString(card.front) }}</div>
        <details class="preview-qa">
          <summary>{{ p('lm06.cardBack') }}</summary>
          <p>{{ asString(card.back) }}</p>
          <p v-if="asString(card.hint)" class="preview-hint">{{ asString(card.hint) }}</p>
        </details>
      </div>
    </template>

    <!-- LM07: Drag and Drop -->
    <template v-else-if="lm === 7">
      <div v-for="(group, i) in asArray(d.groups)" :key="i" class="preview-group">
        <h4>{{ asString(group.label) || `${p('lm07.groupLabel')} ${i + 1}` }}</h4>
        <ul>
          <li v-for="(item, j) in asStringArray(group.correct_items)" :key="j">{{ item }}</li>
        </ul>
      </div>
    </template>

    <!-- LM08: Cloze Test -->
    <template v-else-if="lm === 8">
      <p class="preview-cloze" v-if="asString(d.text)">
        {{ asString(d.text).replace(/\{\{\d+\}\}/g, '[___]') }}
      </p>
      <div v-if="asArray(d.blanks).length" class="preview-blanks">
        <div v-for="(blank, i) in asArray(d.blanks)" :key="i" class="preview-blank">
          <span class="preview-blank-num">{{ i + 1 }}.</span>
          <strong>{{ asString(blank.answer) }}</strong>
          <span v-if="asStringArray(blank.alternatives).length" class="preview-alts">
            ({{ asStringArray(blank.alternatives).join(', ') }})
          </span>
        </div>
      </div>
    </template>

    <!-- LM09: Free Text Long Answer -->
    <template v-else-if="lm === 9">
      <div class="preview-question">
        <strong>{{ p('lm09.question') }}:</strong>
        <p>{{ asString(d.question) }}</p>
      </div>
      <div v-if="asString(d.rubric)" class="preview-section">
        <strong>{{ p('lm09.rubric') }}</strong>
        <p>{{ asString(d.rubric) }}</p>
      </div>
      <details v-if="asString(d.sample_answer)" class="preview-qa">
        <summary>{{ p('lm09.sampleAnswer') }}</summary>
        <p>{{ asString(d.sample_answer) }}</p>
      </details>
    </template>

    <!-- LM10: IHK Style Tasks -->
    <template v-else-if="lm === 10">
      <p v-if="asString(d.context)" class="preview-context">{{ asString(d.context) }}</p>
      <div class="preview-question">
        <strong>{{ asString(d.question_text) }}</strong>
      </div>
      <div v-if="asArray(d.criteria).length" class="preview-criteria">
        <div v-for="(c, i) in asArray(d.criteria)" :key="i" class="preview-criterion">
          <span>{{ asString(c.text) }}</span>
          <span v-if="c.points" class="preview-points">{{ c.points }} P.</span>
        </div>
      </div>
    </template>

    <!-- LM11: Multi Step Practical -->
    <template v-else-if="lm === 11">
      <ol class="preview-steps">
        <li v-for="(step, i) in asArray(d.steps)" :key="i" class="preview-step">
          <strong>{{ asString(step.title) || `${p('lm11.stepTitle')} ${i + 1}` }}</strong>
          <p>{{ asString(step.description) }}</p>
          <p v-if="asString(step.rubric)" class="preview-hint">{{ asString(step.rubric) }}</p>
          <span v-if="step.points" class="preview-points">{{ step.points }} P.</span>
        </li>
      </ol>
    </template>

    <!-- Fallback -->
    <div v-else class="preview-empty">
      {{ t('panel.manualEditor.activityEditor.unsupported') }}
    </div>

    <!-- No data state -->
    <div v-if="!d || Object.keys(d).length === 0" class="preview-empty">
      {{ t('panel.manualEditor.activityEditor.preview.noData') }}
    </div>
  </div>
</template>

<style scoped>
.preview-panel {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  height: 100%;
}

.preview-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-primary);
}

.preview-instructions {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
  padding: 8px 12px;
  background: color-mix(in srgb, var(--color-accent) 5%, transparent);
  border-radius: 6px;
  border-left: 3px solid var(--color-accent);
}

.preview-text {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.preview-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--color-accent) 12%, transparent);
  color: var(--color-accent);
}

.preview-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-section strong {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-text-secondary);
}

.preview-section p {
  margin: 0;
  font-size: 14px;
}

.preview-steps {
  margin: 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.preview-step {
  font-size: 14px;
}

.preview-step strong {
  display: block;
  margin-bottom: 2px;
}

.preview-step p {
  margin: 0;
}

.preview-hint {
  font-size: 12px;
  color: var(--color-text-tertiary);
  font-style: italic;
  margin: 4px 0 0;
}

.preview-theory-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

.preview-theory-section h4 {
  margin: 0;
  font-size: 14px;
}

.preview-theory-section p {
  margin: 0;
  font-size: 13px;
}

.preview-qa {
  margin-top: 6px;
  cursor: pointer;
}

.preview-qa summary {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-accent);
}

.preview-qa p {
  margin: 4px 0 0;
  font-size: 13px;
}

.preview-code {
  padding: 12px;
  background: var(--color-surface-alt, #1e1e1e);
  color: var(--color-text-primary);
  border-radius: 6px;
  font-size: 12px;
  overflow-x: auto;
  margin: 0;
}

.preview-elements {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-element {
  font-size: 13px;
  padding: 4px 8px;
  background: color-mix(in srgb, var(--color-accent) 4%, transparent);
  border-radius: 4px;
}

.preview-scenario {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 12px;
}

.preview-scenario h4 {
  margin: 0 0 8px;
  font-size: 14px;
}

.preview-scenario-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-scenario-part strong {
  font-size: 11px;
  text-transform: uppercase;
  color: var(--color-text-secondary);
}

.preview-scenario-part p {
  margin: 2px 0 0;
  font-size: 13px;
}

.preview-problem {
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

.preview-problem-text {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

.preview-formula {
  font-size: 14px;
  padding: 8px 12px;
  background: color-mix(in srgb, var(--color-warning) 8%, transparent);
  border-radius: 4px;
  margin: 6px 0;
  font-family: 'Courier New', monospace;
}

.preview-flashcard {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
}

.flashcard-front {
  padding: 16px;
  font-size: 15px;
  font-weight: 500;
  text-align: center;
  background: color-mix(in srgb, var(--color-accent) 6%, transparent);
}

.preview-flashcard .preview-qa {
  padding: 12px;
  margin: 0;
}

.preview-group {
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

.preview-group h4 {
  margin: 0 0 6px;
  font-size: 13px;
  color: var(--color-accent);
}

.preview-group ul {
  margin: 0;
  padding-left: 18px;
}

.preview-group li {
  font-size: 13px;
}

.preview-cloze {
  font-size: 15px;
  line-height: 1.8;
  margin: 0;
}

.preview-blanks {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
}

.preview-blank {
  font-size: 13px;
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.preview-blank-num {
  color: var(--color-text-tertiary);
  min-width: 18px;
}

.preview-alts {
  color: var(--color-text-tertiary);
  font-size: 12px;
}

.preview-question strong {
  font-size: 12px;
  text-transform: uppercase;
  color: var(--color-text-secondary);
}

.preview-question p {
  margin: 4px 0 0;
  font-size: 14px;
}

.preview-context {
  font-size: 13px;
  padding: 10px;
  background: color-mix(in srgb, var(--color-info) 8%, transparent);
  border-radius: 6px;
  margin: 0;
}

.preview-criteria {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-criterion {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  padding: 4px 8px;
  background: color-mix(in srgb, var(--color-surface-alt, var(--color-surface)) 50%, transparent);
  border-radius: 4px;
}

.preview-points {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-accent);
}

.preview-empty {
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 13px;
  padding: 24px 0;
}
</style>
