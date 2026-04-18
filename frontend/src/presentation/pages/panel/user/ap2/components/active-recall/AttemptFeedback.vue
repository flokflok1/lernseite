<template>
  <div class="ap2-fb" :class="scoreClass">
    <header class="ap2-fb-header">
      <span class="ap2-fb-title">{{ t('ap2Trainer.study.feedback.title') }}</span>
      <span class="ap2-fb-score">
        <span class="ap2-fb-score-val">{{ response.pct }}%</span>
        <span class="ap2-fb-score-pts">
          {{ t('ap2Trainer.study.feedback.earned') }}: {{ response.points_earned }} / {{ response.points_total }}
        </span>
      </span>
    </header>

    <p v-if="response.feedback?.summary" class="ap2-fb-summary">
      {{ response.feedback.summary }}
    </p>

    <div v-if="hasLists" class="ap2-fb-lists">
      <div v-if="response.feedback?.correct_aspects?.length" class="ap2-fb-list ap2-fb-correct">
        <h4>✓ {{ t('ap2Trainer.study.feedback.correct') }}</h4>
        <ul><li v-for="(a, i) in response.feedback.correct_aspects" :key="i">{{ a }}</li></ul>
      </div>
      <div v-if="response.feedback?.missing_aspects?.length" class="ap2-fb-list ap2-fb-missing">
        <h4>! {{ t('ap2Trainer.study.feedback.missing') }}</h4>
        <ul><li v-for="(a, i) in response.feedback.missing_aspects" :key="i">{{ a }}</li></ul>
      </div>
      <div v-if="response.feedback?.partial_aspects?.length" class="ap2-fb-list ap2-fb-partial">
        <h4>~ {{ t('ap2Trainer.study.feedback.partial') }}</h4>
        <ul><li v-for="(a, i) in response.feedback.partial_aspects" :key="i">{{ a }}</li></ul>
      </div>
      <div v-if="response.feedback?.incorrect_aspects?.length" class="ap2-fb-list ap2-fb-wrong">
        <h4>✗ {{ t('ap2Trainer.study.feedback.incorrect') }}</h4>
        <ul><li v-for="(a, i) in response.feedback.incorrect_aspects" :key="i">{{ a }}</li></ul>
      </div>
    </div>

    <details v-if="response.model_answer" class="ap2-fb-model">
      <summary>{{ t('ap2Trainer.study.feedback.modelAnswer') }}</summary>
      <pre>{{ response.model_answer }}</pre>
    </details>

    <p v-if="response.feedback?.suggestions?.length" class="ap2-fb-suggestions">
      💡 {{ t('ap2Trainer.study.feedback.suggestions') }}: {{ response.feedback.suggestions.join(' · ') }}
    </p>

    <p class="ap2-fb-mastery">
      {{ t('ap2Trainer.study.feedback.masteryAfter', { n: Math.round(response.mastery_score) }) }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Ap2SubmitResponse } from '@/infrastructure/api/clients/panel/user/exams'

interface Props { response: Ap2SubmitResponse }
const props = defineProps<Props>()
const { t } = useI18n()

const hasLists = computed(() => {
  const fb = props.response.feedback
  return Boolean(fb && (
    fb.correct_aspects?.length || fb.missing_aspects?.length ||
    fb.partial_aspects?.length || fb.incorrect_aspects?.length
  ))
})

const scoreClass = computed(() => {
  const p = props.response.pct
  if (p >= 80) return 'ap2-fb-great'
  if (p >= 50) return 'ap2-fb-ok'
  return 'ap2-fb-weak'
})
</script>

<style scoped>
.ap2-fb {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
}
.ap2-fb-great { border-left: 4px solid #22c55e; }
.ap2-fb-ok    { border-left: 4px solid #f59e0b; }
.ap2-fb-weak  { border-left: 4px solid #ef4444; }

.ap2-fb-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.ap2-fb-title { font-size: 14px; font-weight: 700; color: #cbd5e1; }
.ap2-fb-score { text-align: right; }
.ap2-fb-score-val { font-size: 22px; font-weight: 800; }
.ap2-fb-great .ap2-fb-score-val { color: #4ade80; }
.ap2-fb-ok .ap2-fb-score-val    { color: #fbbf24; }
.ap2-fb-weak .ap2-fb-score-val  { color: #f87171; }
.ap2-fb-score-pts { display: block; font-size: 11px; color: #94a3b8; }

.ap2-fb-summary { color: #e2e8f0; font-size: 13px; margin: 8px 0 12px; }

.ap2-fb-lists {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px;
  margin: 8px 0;
}
.ap2-fb-list { padding: 10px; border-radius: 8px; font-size: 12px; }
.ap2-fb-list h4 { margin: 0 0 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.ap2-fb-list ul { margin: 0; padding-left: 16px; color: #cbd5e1; }
.ap2-fb-correct { background: rgba(34, 197, 94, 0.08); }
.ap2-fb-correct h4 { color: #4ade80; }
.ap2-fb-missing { background: rgba(245, 158, 11, 0.08); }
.ap2-fb-missing h4 { color: #fbbf24; }
.ap2-fb-partial { background: rgba(99, 102, 241, 0.08); }
.ap2-fb-partial h4 { color: #a5b4fc; }
.ap2-fb-wrong { background: rgba(239, 68, 68, 0.08); }
.ap2-fb-wrong h4 { color: #f87171; }

.ap2-fb-model { margin: 10px 0; }
.ap2-fb-model summary { cursor: pointer; font-size: 12px; font-weight: 600; color: #818cf8; }
.ap2-fb-model pre { font-size: 12px; color: #cbd5e1; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 6px; white-space: pre-wrap; word-wrap: break-word; }

.ap2-fb-suggestions { font-size: 12px; color: #94a3b8; margin: 8px 0; }
.ap2-fb-mastery { font-size: 12px; color: #a5b4fc; font-weight: 600; margin: 8px 0 0; }
</style>
