<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import type { ModuleSubmitResponse } from '@/infrastructure/api/clients/panel/user/exams/ap2-modules.api'

interface Props {
  response: ModuleSubmitResponse
}
const props = defineProps<Props>()

const emit = defineEmits<{
  next: []
}>()

const showModelAnswer = computed(
  () => !!props.response.model_answer
    && (props.response.stuetzrad_used || !props.response.passed),
)

const modelAnswerHtml = computed(() => {
  if (!props.response.model_answer) return ''
  const html = marked.parse(props.response.model_answer, { async: false }) as string
  return DOMPurify.sanitize(html)
})

const kopfSerieLabel = computed(() => {
  const s = props.response.skill
  return `${s.kopf_serie_count} / ${s.effective_target}`
})

const streakBadgeClass = computed(() => {
  if (props.response.stuetzrad_used) return 'badge-neutral'
  return props.response.passed ? 'badge-pass' : 'badge-fail'
})
</script>

<template>
  <section class="feedback-panel">
    <header class="feedback-head" :class="streakBadgeClass">
      <span class="feedback-pct">{{ response.pct }}%</span>
      <span class="feedback-state">
        <template v-if="response.stuetzrad_used">
          🪄 Stützrad AN — kein Streak-Einfluss
        </template>
        <template v-else-if="response.passed">
          ✅ Bestanden — Kopf-Serie: <strong>{{ kopfSerieLabel }}</strong>
        </template>
        <template v-else>
          ❌ Nicht bestanden — Kopf-Serie zurück auf 0
          ({{ response.skill.fail_count }}× Fehler)
        </template>
      </span>
    </header>

    <p v-if="response.feedback.summary" class="feedback-summary">
      {{ response.feedback.summary }}
    </p>

    <div v-if="response.skill.should_suggest_stuetzrad && !response.stuetzrad_used"
         class="suggest-box suggest-stuetzrad">
      💡 <strong>Probier's mit Stützrad:</strong>
      Du hast {{ response.skill.fail_count }}× hintereinander unter 80% —
      aktiviere das Stützrad und lies die Musterlösung, dann wiederholst du
      es ohne Stützrad bis es sitzt.
    </div>

    <div v-if="response.skill.should_suggest_pause" class="suggest-box suggest-pause">
      🛑 <strong>Pausier lieber:</strong>
      {{ response.skill.fail_count }}× Fehler — dein Kopf ist durch.
      Mach 10 min Pause, snooze das Item oder wechsle das Modul.
    </div>

    <div v-if="response.feedback.correct_aspects.length"
         class="feedback-block feedback-correct">
      <strong>✓ Richtig erkannt:</strong>
      <ul><li v-for="(a, i) in response.feedback.correct_aspects" :key="i">{{ a }}</li></ul>
    </div>

    <div v-if="response.feedback.partial_aspects.length"
         class="feedback-block feedback-partial">
      <strong>~ Teilweise:</strong>
      <ul><li v-for="(a, i) in response.feedback.partial_aspects" :key="i">{{ a }}</li></ul>
    </div>

    <div v-if="response.feedback.missing_aspects.length"
         class="feedback-block feedback-missing">
      <strong>✗ Hat gefehlt:</strong>
      <ul><li v-for="(a, i) in response.feedback.missing_aspects" :key="i">{{ a }}</li></ul>
    </div>

    <div v-if="response.feedback.incorrect_aspects.length"
         class="feedback-block feedback-wrong">
      <strong>✗ Falsch:</strong>
      <ul><li v-for="(a, i) in response.feedback.incorrect_aspects" :key="i">{{ a }}</li></ul>
    </div>

    <div v-if="response.feedback.suggestions.length"
         class="feedback-block feedback-tips">
      <strong>💡 Tipps:</strong>
      <ul><li v-for="(a, i) in response.feedback.suggestions" :key="i">{{ a }}</li></ul>
    </div>

    <div v-if="showModelAnswer" class="feedback-block model-answer-block">
      <strong>📘 Musterlösung:</strong>
      <div class="model-answer-body" v-html="modelAnswerHtml" />
    </div>

    <div class="feedback-actions">
      <button class="btn btn-primary" @click="emit('next')">
        {{ response.next_item ? '▶ Nächste Aufgabe (Enter)' : '↩ Zur Übersicht' }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.feedback-panel {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1.4rem;
}

.feedback-head {
  display: flex;
  align-items: baseline;
  gap: 0.8rem;
  padding: 0.8rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}
.badge-pass { background: rgba(22,163,74,0.15); border-left: 3px solid #16a34a; }
.badge-fail { background: rgba(220,38,38,0.15); border-left: 3px solid #dc2626; }
.badge-neutral { background: rgba(59,130,246,0.12); border-left: 3px solid #3b82f6; }

.feedback-pct { font-size: 1.6rem; font-weight: 700; color: #f1f5f9; }
.feedback-state { color: #cbd5e1; }
.feedback-state strong { color: #fbbf24; }

.feedback-summary {
  margin: 0.5rem 0 1rem 0;
  color: #f1f5f9;
  font-size: 0.95rem;
  line-height: 1.5;
}

.suggest-box {
  padding: 0.7rem 1rem;
  border-radius: 6px;
  margin-bottom: 0.8rem;
  font-size: 0.88rem;
  color: #e2e8f0;
  line-height: 1.5;
}
.suggest-stuetzrad { background: rgba(59,130,246,0.12); border-left: 3px solid #3b82f6; }
.suggest-pause { background: rgba(245,158,11,0.12); border-left: 3px solid #f59e0b; }
.suggest-box strong { color: #fbbf24; }

.feedback-block {
  margin: 0.6rem 0;
  padding: 0.6rem 0.8rem;
  border-radius: 4px;
  font-size: 0.88rem;
}
.feedback-block ul { margin: 0.3rem 0 0 1.2rem; padding: 0; }
.feedback-block li { margin-bottom: 0.2rem; line-height: 1.4; }
.feedback-correct { background: rgba(22,163,74,0.08); border-left: 3px solid #16a34a; color: #cbd5e1; }
.feedback-correct strong { color: #86efac; }
.feedback-partial { background: rgba(245,158,11,0.08); border-left: 3px solid #f59e0b; color: #cbd5e1; }
.feedback-partial strong { color: #fbbf24; }
.feedback-missing { background: rgba(220,38,38,0.08); border-left: 3px solid #dc2626; color: #cbd5e1; }
.feedback-missing strong { color: #fca5a5; }
.feedback-wrong { background: rgba(220,38,38,0.08); border-left: 3px solid #dc2626; color: #cbd5e1; }
.feedback-wrong strong { color: #fca5a5; }
.feedback-tips { background: rgba(59,130,246,0.08); border-left: 3px solid #3b82f6; color: #cbd5e1; }
.feedback-tips strong { color: #93c5fd; }

.model-answer-block {
  background: rgba(139,92,246,0.08);
  border-left: 3px solid #8b5cf6;
  color: #e2e8f0;
}
.model-answer-block strong { color: #c4b5fd; }
.model-answer-body {
  margin-top: 0.5rem;
  line-height: 1.55;
  font-size: 0.9rem;
}
.model-answer-body :deep(code) {
  background: #0f172a;
  border: 1px solid #334155;
  padding: 1px 5px;
  border-radius: 3px;
  font-family: monospace;
  color: #fbbf24;
  font-size: 0.88em;
}
.model-answer-body :deep(pre) {
  background: #0f172a;
  border: 1px solid #334155;
  padding: 0.8rem;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.85em;
}

.feedback-actions { margin-top: 1rem; }

.btn {
  padding: 0.55rem 1rem;
  border: 0;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-primary { background: #2563eb; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #1e40af; }
</style>
