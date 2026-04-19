<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import {
  startModule,
  submitModuleAnswer,
  listModules,
  getPreferences,
  getModuleDetail,
  type ModuleCard,
  type ModuleItem,
  type ModuleSubmitResponse,
  type ItemSkillState,
  type UserPreferences,
} from '@/infrastructure/api/clients/panel/user/exams/ap2-modules.api'
import ModuleFeedbackPanel from '../components/active-recall/ModuleFeedbackPanel.vue'
import StuetzradControls from '../components/active-recall/StuetzradControls.vue'
import CalculatorHint from '../components/active-recall/CalculatorHint.vue'

interface Props { slug: string }
const props = defineProps<Props>()
const router = useRouter()

const module = ref<ModuleCard | null>(null)
const theory = ref<string>('')
const item = ref<ModuleItem | null>(null)
const itemSkill = ref<ItemSkillState | null>(null)
const prefs = ref<UserPreferences | null>(null)
const stuetzradOn = ref(false)

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
    const [all, prefsRes] = await Promise.all([listModules(), getPreferences()])
    prefs.value = prefsRes.preferences
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
    applyStuetzradDefault()
    await refreshItemSkill()
    phase.value = theory.value ? 'theory' : 'task'
    if (phase.value === 'task') startTimer()
  } catch (e: any) {
    error.value = e?.response?.data?.error || 'Konnte Modul nicht starten.'
  }
}

function applyStuetzradDefault() {
  if (!prefs.value) return
  const d = prefs.value.stuetzrad_default
  if (d === 'off') stuetzradOn.value = false
  else if (d === 'first_two_on') {
    stuetzradOn.value = (itemSkill.value?.total_attempts ?? 0) < 2
  } else {
    stuetzradOn.value = false
  }
}

async function refreshItemSkill() {
  if (!module.value || !item.value) return
  try {
    const detail = await getModuleDetail(module.value.module_id)
    const found = detail.items.find(i => i.item_id === item.value!.item_id)
    itemSkill.value = found?.skill ?? null
    applyStuetzradDefault()
  } catch {
    itemSkill.value = null
  }
}

function startTimer() {
  elapsedSec.value = 0
  if (timerHandle) window.clearInterval(timerHandle)
  timerHandle = window.setInterval(() => { elapsedSec.value++ }, 1000)
}

function stopTimer() {
  if (timerHandle) { window.clearInterval(timerHandle); timerHandle = null }
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
      stuetzradOn.value,
    )
    lastResponse.value = res
    if (module.value) module.value.progress = res.progress
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

async function nextTask() {
  if (!lastResponse.value) return
  if (lastResponse.value.next_item) {
    item.value = lastResponse.value.next_item
    answer.value = ''
    lastResponse.value = null
    await refreshItemSkill()
    phase.value = 'task'
    startTimer()
  } else {
    router.push('/ap2-training/modules')
  }
}

function backToList() { router.push('/ap2-training/modules') }

function onKey(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && phase.value === 'task') {
    e.preventDefault(); submit()
  }
  if (e.key === 'Enter' && phase.value === 'feedback' && !e.shiftKey) {
    if (e.target && (e.target as HTMLElement).tagName === 'TEXTAREA') return
    e.preventDefault(); nextTask()
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
  module.value = null; theory.value = ''; item.value = null
  itemSkill.value = null; stuetzradOn.value = false
  phase.value = 'theory'; answer.value = ''; lastResponse.value = null
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
          <span v-if="phase === 'task'" class="runner-timer" :class="timerClass">
            ⏱ {{ timerLabel }}
          </span>
        </div>
      </div>
    </header>

    <div v-if="error" class="runner-error">⚠️ {{ error }}</div>

    <div v-if="phase === 'cooldown' && module?.progress" class="runner-cooldown">
      <h3>🛑 Cooldown aktiv</h3>
      <p>Du hast 3× hintereinander unter 80%. Mach 30 Minuten Pause.</p>
      <p class="runner-cooldown-time">
        Bereit ab:
        <strong>{{ new Date(module.progress.cooldown_until!).toLocaleTimeString('de-DE') }}</strong>
      </p>
    </div>

    <section v-else-if="phase === 'theory' && theory" class="runner-theory">
      <h3>📖 Lehrblock — kurz lesen, dann legst du los</h3>
      <article class="theory-content" v-html="theoryHtml" />
      <div class="runner-actions">
        <button class="btn btn-primary" @click="startTask">
          ▶ Verstanden — erste Aufgabe
        </button>
      </div>
    </section>

    <section v-else-if="phase === 'task' && item" class="runner-task">
      <StuetzradControls
        v-model="stuetzradOn"
        :skill="itemSkill"
        :prefs="prefs"
        :disabled="submitting"
      />
      <div class="task-prompt">
        <pre class="task-text">{{ item.prompt }}</pre>
      </div>
      <CalculatorHint :hint="item.calculator_hint" />
      <textarea
        v-model="answer"
        class="task-textarea"
        rows="10"
        :placeholder="stuetzradOn
          ? 'Stützrad ist AN — schreib was du weißt (auch wenig ok). Du siehst danach die Musterlösung.'
          : 'Deine Antwort — Strg+Enter zum Abschicken.'"
        :disabled="submitting"
      />
      <div class="runner-actions">
        <span class="task-hint">
          Tipp: Strg+Enter zum Abschicken. Ziel-Zeit ca.
          {{ Math.round((item.estimated_time_sec || 120) / 60) }} min.
        </span>
        <button
          class="btn btn-primary"
          :disabled="submitting || answer.trim().length < 2"
          @click="submit"
        >
          {{ submitting ? 'Bewerte…' : (stuetzradOn ? '🪄 Abschicken + Lösung' : 'Antwort abschicken') }}
        </button>
      </div>
    </section>

    <ModuleFeedbackPanel
      v-else-if="phase === 'feedback' && lastResponse"
      :response="lastResponse"
      @next="nextTask"
    />

    <section v-else-if="phase === 'mastered' && lastResponse" class="runner-mastered">
      <h3 v-if="module?.progress?.status === 'pending_recall'">🟡 Streak geschafft!</h3>
      <h3 v-else>🎉 Modul mastered!</h3>
      <p v-if="module?.progress?.status === 'pending_recall'">
        Same-Day-Recall kommt in 4 Stunden. Bestehst du ihn, ist das Modul endgültig durch.
      </p>
      <p v-else>Spot-Checks folgen in 2/4/7/12/18 Tagen.</p>
      <div class="runner-actions">
        <button class="btn btn-primary" @click="backToList">↩ Zur Modul-Übersicht</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.runner { max-width: 880px; margin: 0 auto; padding: 1rem; }

.runner-head { margin-bottom: 1.2rem; }
.runner-back {
  background: transparent; color: #94a3b8; border: 0;
  font-size: 0.85rem; cursor: pointer; padding: 0.3rem 0;
}
.runner-back:hover { color: #cbd5e1; }

.runner-title-block {
  margin-top: 0.5rem; display: flex;
  justify-content: space-between; align-items: flex-start;
}
.runner-title-block h2 { margin: 0; color: #f1f5f9; }
.runner-meta { display: flex; gap: 0.8rem; align-items: center; font-size: 0.85rem; color: #94a3b8; }

.runner-timer {
  font-family: monospace;
  background: rgba(255,255,255,0.05);
  padding: 0.2rem 0.5rem; border-radius: 4px;
}
.runner-timer.timer-warn { color: #fbbf24; }
.runner-timer.timer-over { color: #f87171; background: rgba(220,38,38,0.15); }

.runner-error {
  padding: 1rem; background: #7f1d1d33;
  border-left: 3px solid #dc2626; color: #fecaca;
  border-radius: 4px; margin: 1rem 0;
}

.runner-cooldown, .runner-mastered {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px; padding: 2rem; text-align: center;
}
.runner-cooldown h3, .runner-mastered h3 { margin-top: 0; color: #f1f5f9; }
.runner-cooldown-time { color: #fbbf24; }

.runner-theory, .runner-task {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px; padding: 1.4rem;
}
.runner-theory h3 { margin-top: 0; color: #f1f5f9; }
.theory-content { color: #cbd5e1; line-height: 1.6; font-size: 0.95rem; }
.theory-content :deep(h2) { font-size: 1.1rem; color: #f1f5f9; margin-top: 1.5rem; }
.theory-content :deep(h3) { font-size: 1rem; color: #f1f5f9; margin-top: 1.2rem; }
.theory-content :deep(code) {
  background: #0f172a; border: 1px solid #334155;
  padding: 1px 5px; border-radius: 3px; font-family: monospace;
  color: #fbbf24; font-size: 0.88em;
}
.theory-content :deep(pre) {
  background: #0f172a; border: 1px solid #334155;
  padding: 0.8rem; border-radius: 6px; overflow-x: auto; font-size: 0.85em;
}
.theory-content :deep(pre code) { background: none; border: 0; padding: 0; }
.theory-content :deep(table) { border-collapse: collapse; margin: 1rem 0; font-size: 0.88rem; }
.theory-content :deep(th), .theory-content :deep(td) {
  border: 1px solid #334155; padding: 0.4rem 0.7rem; text-align: left;
}
.theory-content :deep(th) { background: rgba(255,255,255,0.04); }
.theory-content :deep(strong) { color: #f1f5f9; }

.task-prompt {
  background: rgba(0,0,0,0.2);
  border-left: 3px solid #3b82f6;
  border-radius: 4px; padding: 0.8rem 1rem; margin-bottom: 1rem;
}
.task-text {
  margin: 0; white-space: pre-wrap; font-family: inherit;
  font-size: 0.95rem; color: #f1f5f9; line-height: 1.5;
}
.task-textarea {
  width: 100%; padding: 0.8rem;
  background: #0f172a; border: 1px solid #475569;
  border-radius: 6px; color: #f1f5f9;
  font-family: inherit; font-size: 0.95rem; line-height: 1.5;
  resize: vertical;
}
.task-textarea:focus { outline: none; border-color: #3b82f6; }
.task-hint { font-size: 0.78rem; color: #94a3b8; }

.runner-actions {
  display: flex; gap: 0.6rem; align-items: center;
  justify-content: space-between; margin-top: 1rem; flex-wrap: wrap;
}
.btn {
  padding: 0.55rem 1rem; border: 0; border-radius: 6px;
  font-weight: 600; font-size: 0.9rem; cursor: pointer;
  transition: background 0.15s;
}
.btn-primary { background: #2563eb; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #1e40af; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
