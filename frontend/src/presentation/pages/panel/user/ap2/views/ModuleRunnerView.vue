<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import {
  startModule,
  submitModuleAnswer,
  listModules,
  type ModuleCard,
  type ModuleItem,
  type ModuleSubmitResponse,
} from '@/infrastructure/api/clients/panel/user/exams/ap2-modules.api'

interface Props { slug: string }
const props = defineProps<Props>()
const router = useRouter()
const route = useRoute()

// State
const module = ref<ModuleCard | null>(null)
const theory = ref<string>('')
const item = ref<ModuleItem | null>(null)
const phase = ref<'theory' | 'task' | 'feedback' | 'mastered' | 'cooldown'>('theory')
const answer = ref('')
const submitting = ref(false)
const lastResponse = ref<ModuleSubmitResponse | null>(null)
const elapsedSec = ref(0)
const error = ref<string | null>(null)

let timerHandle: number | null = null

const theoryHtml = computed(() => {
  if (!theory.value) return ''
  return DOMPurify.sanitize(marked.parse(theory.value, { async: false }) as string)
})

const streakDisplay = computed(() => {
  if (!module.value?.progress) return '0/3'
  return `${module.value.progress.streak_count}/3`
})

const timerLabel = computed(() => {
  const min = Math.floor(elapsedSec.value / 60)
  const sec = elapsedSec.value % 60
  return `${min}:${sec.toString().padStart(2, '0')}`
})

const timerClass = computed(() => {
  if (!item.value) return ''
  const expected = item.value.estimated_time_sec || 120
  if (elapsedSec.value > expected * 2) return 'timer-over'
  if (elapsedSec.value > expected) return 'timer-warn'
  return ''
})

async function loadModule() {
  try {
    // Slug → Module über die Liste auflösen
    const all = await listModules()
    const m = all.find(x => x.slug === props.slug)
    if (!m) {
      error.value = `Modul "${props.slug}" nicht gefunden.`
      return
    }
    if (m.progress?.status === 'locked') {
      error.value = 'Modul ist gesperrt — schließe erst die Voraussetzungen ab.'
      module.value = m
      return
    }
    if (m.progress?.cooldown_until && new Date(m.progress.cooldown_until) > new Date()) {
      phase.value = 'cooldown'
      module.value = m
      return
    }

    const res = await startModule(m.module_id)
    module.value = res.module
    theory.value = res.theory_markdown || ''
    item.value = res.first_item
    phase.value = theory.value ? 'theory' : 'task'
    if (phase.value === 'task') startTimer()
  } catch (e: any) {
    error.value = e?.response?.data?.error || 'Konnte Modul nicht starten.'
  }
}

function startTimer() {
  elapsedSec.value = 0
  if (timerHandle) window.clearInterval(timerHandle)
  timerHandle = window.setInterval(() => { elapsedSec.value++ }, 1000)
}

function stopTimer() {
  if (timerHandle) {
    window.clearInterval(timerHandle)
    timerHandle = null
  }
}

function startTask() {
  phase.value = 'task'
  startTimer()
}

async function submit() {
  if (!module.value || !item.value || !answer.value.trim()) return
  submitting.value = true
  stopTimer()
  error.value = null
  try {
    const res = await submitModuleAnswer(
      module.value.module_id,
      item.value.item_id,
      answer.value,
    )
    lastResponse.value = res
    if (module.value) {
      module.value.progress = res.progress
    }
    if (res.progress.status === 'mastered' || res.progress.status === 'pending_recall') {
      phase.value = 'mastered'
    } else {
      phase.value = 'feedback'
    }
  } catch (e: any) {
    error.value = e?.response?.data?.error || 'Bewertung fehlgeschlagen.'
  } finally {
    submitting.value = false
  }
}

function nextTask() {
  if (!lastResponse.value) return
  if (lastResponse.value.next_item) {
    item.value = lastResponse.value.next_item
    answer.value = ''
    lastResponse.value = null
    phase.value = 'task'
    startTimer()
  } else {
    // Pool erschöpft oder gar kein next-Item — zurück zur Liste
    router.push('/ap2-training/modules')
  }
}

function backToList() {
  router.push('/ap2-training/modules')
}

function onKey(e: KeyboardEvent) {
  // Ctrl+Enter = submit
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && phase.value === 'task') {
    e.preventDefault()
    submit()
  }
  // Enter im feedback = nächste Aufgabe
  if (e.key === 'Enter' && phase.value === 'feedback' && !e.shiftKey) {
    if (e.target && (e.target as HTMLElement).tagName === 'TEXTAREA') return
    e.preventDefault()
    nextTask()
  }
}

onMounted(() => {
  loadModule()
  window.addEventListener('keydown', onKey)
})

onBeforeUnmount(() => {
  stopTimer()
  window.removeEventListener('keydown', onKey)
})

watch(() => props.slug, () => {
  stopTimer()
  module.value = null
  theory.value = ''
  item.value = null
  phase.value = 'theory'
  answer.value = ''
  lastResponse.value = null
  error.value = null
  loadModule()
})
</script>

<template>
  <div class="runner">
    <header class="runner-head">
      <button class="runner-back" @click="backToList">← Zurück zur Liste</button>
      <div v-if="module" class="runner-title-block">
        <h2>{{ module.name_de }}</h2>
        <div class="runner-meta">
          <span class="runner-streak">Streak: <strong>{{ streakDisplay }}</strong></span>
          <span v-if="phase === 'task'" class="runner-timer" :class="timerClass">⏱ {{ timerLabel }}</span>
        </div>
      </div>
    </header>

    <div v-if="error" class="runner-error">⚠️ {{ error }}</div>

    <div v-if="phase === 'cooldown' && module?.progress" class="runner-cooldown">
      <h3>🛑 Cooldown aktiv</h3>
      <p>
        Du hast 3× hintereinander unter 80% gehabt. Mach 30 Minuten Pause —
        Kopf frei kriegen ist Teil des Lernens.
      </p>
      <p class="runner-cooldown-time">
        Bereit ab: <strong>{{ new Date(module.progress.cooldown_until!).toLocaleTimeString('de-DE') }}</strong>
      </p>
    </div>

    <!-- THEORY -->
    <section v-else-if="phase === 'theory' && theory" class="runner-theory">
      <h3>📖 Lehrblock — kurz lesen, dann legst du los</h3>
      <article class="theory-content" v-html="theoryHtml" />
      <div class="runner-actions">
        <button class="btn btn-primary" @click="startTask">
          ▶ Verstanden — erste Aufgabe
        </button>
      </div>
    </section>

    <!-- TASK -->
    <section v-else-if="phase === 'task' && item" class="runner-task">
      <div class="task-prompt">
        <pre class="task-text">{{ item.prompt }}</pre>
      </div>
      <textarea
        v-model="answer"
        class="task-textarea"
        rows="10"
        placeholder="Deine Antwort — kein Druck, schreib was du weißt. Strg+Enter zum Abschicken."
        :disabled="submitting"
      />
      <div class="runner-actions">
        <span class="task-hint">
          Tipp: Strg+Enter zum Abschicken. Ziel-Zeit ca.
          {{ Math.round((item.estimated_time_sec || 120) / 60) }} min.
        </span>
        <button
          class="btn btn-primary"
          :disabled="submitting || answer.trim().length < 4"
          @click="submit"
        >
          {{ submitting ? 'Bewerte…' : 'Antwort abschicken' }}
        </button>
      </div>
    </section>

    <!-- FEEDBACK -->
    <section v-else-if="phase === 'feedback' && lastResponse" class="runner-feedback">
      <header class="feedback-head" :class="lastResponse.passed ? 'feedback-pass' : 'feedback-fail'">
        <span class="feedback-pct">{{ lastResponse.pct }}%</span>
        <span class="feedback-state">
          {{ lastResponse.passed ? '✅ Bestanden — Streak +1' : '❌ Nicht bestanden — Streak zurück auf 0' }}
        </span>
      </header>

      <p class="feedback-summary" v-if="lastResponse.feedback.summary">
        {{ lastResponse.feedback.summary }}
      </p>

      <div v-if="lastResponse.feedback.correct_aspects.length" class="feedback-block feedback-correct">
        <strong>✓ Richtig erkannt:</strong>
        <ul><li v-for="(a, i) in lastResponse.feedback.correct_aspects" :key="i">{{ a }}</li></ul>
      </div>

      <div v-if="lastResponse.feedback.partial_aspects.length" class="feedback-block feedback-partial">
        <strong>~ Teilweise:</strong>
        <ul><li v-for="(a, i) in lastResponse.feedback.partial_aspects" :key="i">{{ a }}</li></ul>
      </div>

      <div v-if="lastResponse.feedback.missing_aspects.length" class="feedback-block feedback-missing">
        <strong>✗ Hat gefehlt:</strong>
        <ul><li v-for="(a, i) in lastResponse.feedback.missing_aspects" :key="i">{{ a }}</li></ul>
      </div>

      <div v-if="lastResponse.feedback.incorrect_aspects.length" class="feedback-block feedback-wrong">
        <strong>✗ Falsch:</strong>
        <ul><li v-for="(a, i) in lastResponse.feedback.incorrect_aspects" :key="i">{{ a }}</li></ul>
      </div>

      <div v-if="lastResponse.feedback.suggestions.length" class="feedback-block feedback-tips">
        <strong>💡 Tipps:</strong>
        <ul><li v-for="(a, i) in lastResponse.feedback.suggestions" :key="i">{{ a }}</li></ul>
      </div>

      <div class="runner-actions">
        <button class="btn btn-primary" @click="nextTask">
          {{ lastResponse.next_item ? '▶ Nächste Aufgabe (Enter)' : '↩ Zur Übersicht' }}
        </button>
      </div>
    </section>

    <!-- MASTERED / PENDING_RECALL -->
    <section v-else-if="phase === 'mastered' && lastResponse" class="runner-mastered">
      <h3 v-if="module?.progress?.status === 'pending_recall'">🟡 3-Streak geschafft!</h3>
      <h3 v-else>🎉 Modul mastered!</h3>

      <p v-if="module?.progress?.status === 'pending_recall'">
        Du hast 3× hintereinander ≥80% — sehr gut. In 4 Stunden kommt der
        <strong>Same-Day-Recall</strong> — eine kurze Aufgabe (1 min).
        Bestehst du auch den, ist das Modul endgültig mastered und das nächste
        wird freigeschaltet.
      </p>
      <p v-else>
        Der Same-Day-Recall ist auch bestanden — das Modul sitzt fest.
        Das nächste Modul ist freigeschaltet. Spot-Checks kommen in 2/4/7/12/18 Tagen.
      </p>

      <div class="runner-actions">
        <button class="btn btn-primary" @click="backToList">
          ↩ Zur Modul-Übersicht
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.runner {
  max-width: 880px;
  margin: 0 auto;
  padding: 1rem;
}

.runner-head {
  margin-bottom: 1.2rem;
}

.runner-back {
  background: transparent;
  color: #94a3b8;
  border: 0;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.3rem 0;
}
.runner-back:hover { color: #cbd5e1; }

.runner-title-block {
  margin-top: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.runner-title-block h2 { margin: 0; color: #f1f5f9; }

.runner-meta {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  font-size: 0.85rem;
  color: #94a3b8;
}

.runner-streak strong { color: #fbbf24; font-size: 1.05rem; }

.runner-timer {
  font-family: monospace;
  background: rgba(255,255,255,0.05);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}
.runner-timer.timer-warn { color: #fbbf24; }
.runner-timer.timer-over { color: #f87171; background: rgba(220,38,38,0.15); }

.runner-error {
  padding: 1rem;
  background: #7f1d1d33;
  border-left: 3px solid #dc2626;
  color: #fecaca;
  border-radius: 4px;
  margin: 1rem 0;
}

.runner-cooldown,
.runner-mastered {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 2rem;
  text-align: center;
}
.runner-cooldown h3,
.runner-mastered h3 { margin-top: 0; color: #f1f5f9; }
.runner-cooldown-time { color: #fbbf24; }

.runner-theory {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1.4rem;
}
.runner-theory h3 { margin-top: 0; color: #f1f5f9; }

.theory-content {
  color: #cbd5e1;
  line-height: 1.6;
  font-size: 0.95rem;
}
.theory-content :deep(h2) { font-size: 1.1rem; color: #f1f5f9; margin-top: 1.5rem; }
.theory-content :deep(h3) { font-size: 1rem; color: #f1f5f9; margin-top: 1.2rem; }
.theory-content :deep(code) {
  background: #0f172a;
  border: 1px solid #334155;
  padding: 1px 5px;
  border-radius: 3px;
  font-family: monospace;
  color: #fbbf24;
  font-size: 0.88em;
}
.theory-content :deep(pre) {
  background: #0f172a;
  border: 1px solid #334155;
  padding: 0.8rem;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.85em;
}
.theory-content :deep(pre code) { background: none; border: 0; padding: 0; }
.theory-content :deep(table) {
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.88rem;
}
.theory-content :deep(th),
.theory-content :deep(td) {
  border: 1px solid #334155;
  padding: 0.4rem 0.7rem;
  text-align: left;
}
.theory-content :deep(th) { background: rgba(255,255,255,0.04); }
.theory-content :deep(strong) { color: #f1f5f9; }

.runner-task {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1.4rem;
}

.task-prompt {
  background: rgba(0,0,0,0.2);
  border-left: 3px solid #3b82f6;
  border-radius: 4px;
  padding: 0.8rem 1rem;
  margin-bottom: 1rem;
}

.task-text {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 0.95rem;
  color: #f1f5f9;
  line-height: 1.5;
}

.task-textarea {
  width: 100%;
  padding: 0.8rem;
  background: #0f172a;
  border: 1px solid #475569;
  border-radius: 6px;
  color: #f1f5f9;
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.5;
  resize: vertical;
}
.task-textarea:focus { outline: none; border-color: #3b82f6; }

.task-hint {
  font-size: 0.78rem;
  color: #94a3b8;
}

.runner-actions {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  justify-content: space-between;
  margin-top: 1rem;
  flex-wrap: wrap;
}

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
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.runner-feedback {
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
.feedback-pass { background: rgba(22,163,74,0.15); border-left: 3px solid #16a34a; }
.feedback-fail { background: rgba(220,38,38,0.15); border-left: 3px solid #dc2626; }

.feedback-pct {
  font-size: 1.6rem;
  font-weight: 700;
  color: #f1f5f9;
}

.feedback-state { color: #cbd5e1; }

.feedback-summary {
  margin: 0.5rem 0 1rem 0;
  color: #f1f5f9;
  font-size: 0.95rem;
  line-height: 1.5;
}

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
</style>
