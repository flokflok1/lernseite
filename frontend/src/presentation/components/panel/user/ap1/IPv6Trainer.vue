<template>
  <div class="iv6">
    <!-- Mode Toggle -->
    <div class="iv6-modes">
      <button :class="['iv6-mode-btn', mode === 'type' ? 'iv6-mode-active' : '']" @click="mode = 'type'; newRound()">
        🔍 Adresstyp erkennen
      </button>
      <button :class="['iv6-mode-btn', mode === 'shorten' ? 'iv6-mode-active' : '']" @click="mode = 'shorten'; newRound()">
        ✂️ Adresse kürzen
      </button>
    </div>


    <!-- Difficulty -->
    <div class="iv6-diff-row">
      <button class="iv6-diff-btn" :class="difficulty==='easy'?'iv6-diff-on iv6-diff-easy':''" @click="setDifficulty('easy')">🟢 Leicht</button>
      <button class="iv6-diff-btn" :class="difficulty==='medium'?'iv6-diff-on iv6-diff-medium':''" @click="setDifficulty('medium')">🟡 Mittel</button>
      <button class="iv6-diff-btn" :class="difficulty==='hard'?'iv6-diff-on iv6-diff-hard':''" @click="setDifficulty('hard')">🔴 Schwer</button>
    </div>

    <!-- Score -->
    <div class="iv6-score-row">
      <span class="iv6-score">✅ {{ correct }} richtig</span>
      <span class="iv6-score iv6-score-wrong">❌ {{ wrong }} falsch</span>
      <span class="iv6-streak" v-if="streak > 1">🔥 {{ streak }} Streak</span>
    </div>

    <!-- Question Card -->
    <div class="iv6-card">
      <!-- TYPE MODE -->
      <template v-if="mode === 'type'">
        <div class="iv6-question">Welcher IPv6-Adresstyp ist das?</div>
        <div class="iv6-addr">{{ current.addr }}</div>
        <input
          v-model="typeInput"
          class="iv6-input"
          placeholder="Adresstyp eingeben..."
          :disabled="answered"
          @keydown.enter="checkType"
        />
        <div class="iv6-hint-row">
          <button v-if="!answered" class="iv6-check-btn" @click="checkType">Prüfen</button>
          <button v-if="!answered" class="iv6-hint-btn" @click="showHint = !showHint">{{ showHint ? '🙈 Ausblenden' : '💡 Tipp' }}</button>
        </div>
        <div v-if="showHint && !answered" class="iv6-hint-box">
          <span v-for="t in types" :key="t.id" class="iv6-hint-tag">{{ t.label }}</span>
        </div>
        <div v-if="answered" class="iv6-feedback" :class="lastCorrect ? 'iv6-fb-ok' : 'iv6-fb-err'">
          <div v-if="lastCorrect">✓ Richtig! — {{ typeLabel(current.type) }}</div>
          <div v-else>
            ✗ Falsch — richtig: <strong>{{ typeLabel(current.type) }}</strong>
            <span class="iv6-fb-hint">{{ current.hint }}</span>
          </div>
        </div>
      </template>

      <!-- SHORTEN MODE -->
      <template v-if="mode === 'shorten'">
        <div class="iv6-question">Kürze diese IPv6-Adresse:</div>
        <div class="iv6-addr">{{ current.full }}</div>
        <div class="iv6-rules">
          <span>Regel 1: führende Nullen weglassen</span>
          <span>Regel 2: längste Nullgruppe → <code>::</code> (nur einmal!)</span>
        </div>
        <input
          v-model="userInput"
          class="iv6-input"
          placeholder="Gekürzte Adresse eingeben..."
          :disabled="answered"
          @keydown.enter="checkShorten"
        />
        <button v-if="!answered" class="iv6-check-btn" @click="checkShorten">Prüfen</button>
        <div v-if="answered" class="iv6-feedback" :class="lastCorrect ? 'iv6-fb-ok' : 'iv6-fb-err'">
          <div v-if="lastCorrect">✓ Richtig!</div>
          <div v-else>
            ✗ Nicht ganz — richtige Antwort: <strong>{{ current.short }}</strong>
            <div class="iv6-steps" v-if="current.steps">
              <div v-for="(s, i) in current.steps" :key="i" class="iv6-step">{{ s }}</div>
            </div>
          </div>
        </div>
      </template>

      <!-- Next Button -->
      <button v-if="answered" class="iv6-next-btn" @click="newRound">Nächste →</button>
    </div>

    <!-- Lumi Tutor -->
    <div class="iv6-tutor-wrap">
      <button class="iv6-tutor-toggle" @click="showTutor = !showTutor">
        🤖 {{ showTutor ? 'Lumi ausblenden ▲' : 'Lumi fragen ▼' }}
      </button>
      <div v-if="showTutor" class="iv6-tutor-panel">
        <div ref="tutorContainer" class="iv6-tutor-msgs">
          <div v-if="tutorMessages.length === 0" class="iv6-tutor-empty">
            Hi Pascal! Ich bin Lumi 🤖<br>Frag mich zu IPv6 — oder klick auf "Zur Aufgabe" für einen gezielten Tipp!
          </div>
          <div v-for="(m, i) in tutorMessages" :key="i" class="iv6-tutor-msg" :class="m.role === 'user' ? 'iv6-tm-user' : 'iv6-tm-bot'">{{ m.content }}</div>
          <div v-if="tutorLoading" class="iv6-tutor-msg iv6-tm-bot iv6-tm-loading">Lumi denkt nach…</div>
        </div>
        <div class="iv6-tutor-input-row">
          <button class="iv6-tutor-ctx-btn" @click="askAboutCurrent" :disabled="tutorLoading || !current.addr && !current.full">❓ Zur Aufgabe</button>
          <input v-model="tutorInput" class="iv6-tutor-input" placeholder="Frag Lumi..." @keydown.enter="askTutor()" :disabled="tutorLoading" />
          <button class="iv6-tutor-send" @click="askTutor()" :disabled="tutorLoading || !tutorInput.trim()">→</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { tutorChat } from '@/infrastructure/api/clients/public/learning/tutor/tutor.api'

const emit = defineEmits(['score'])

const mode = ref<'type' | 'shorten'>('type')
const correct = ref(0)
const wrong = ref(0)
const streak = ref(0)
const answered = ref(false)
const lastCorrect = ref(false)
const selected = ref('')
const userInput = ref('')
const typeInput = ref('')
const showHint = ref(false)
const difficulty = ref<'easy'|'medium'|'hard'>('medium')
const showTutor = ref(false)
const tutorMessages = ref<{role: string, content: string}[]>([])
const tutorInput = ref('')
const tutorLoading = ref(false)
const tutorContainer = ref<HTMLDivElement | null>(null)

const LUMI_PROMPT = `Du bist Lumi, ein Sokrates-Tutor für IPv6 (Pascal, FISI AP1 BW). WICHTIG: Gib NIEMALS direkt die Antwort! Stelle eine gezielte Frage, die Pascal selbst zum Schluss führt. Max 2-3 Sätze. Deutsch.`

async function askTutor(msg?: string) {
  const question = (msg || tutorInput.value).trim()
  if (!question || tutorLoading.value) return
  tutorMessages.value.push({ role: 'user', content: question })
  tutorInput.value = ''
  tutorLoading.value = true
  await nextTick()
  if (tutorContainer.value) tutorContainer.value.scrollTop = tutorContainer.value.scrollHeight
  try {
    const history = tutorMessages.value.slice(0, -1).map(m => ({
      role: (m.role === 'tutor' ? 'assistant' : 'user') as 'assistant' | 'user',
      content: m.content
    }))
    const res = await tutorChat({ message: question, systemPrompt: LUMI_PROMPT, history })
    tutorMessages.value.push({ role: 'tutor', content: res.message })
  } catch {
    tutorMessages.value.push({ role: 'tutor', content: '⚠️ Fehler — bitte nochmal versuchen.' })
  } finally {
    tutorLoading.value = false
    await nextTick()
    if (tutorContainer.value) tutorContainer.value.scrollTop = tutorContainer.value.scrollHeight
  }
}

function askAboutCurrent() {
  if (!current.value) return
  const q = mode.value === 'type'
    ? `Welcher IPv6-Adresstyp ist "${current.value.addr}". Gib mir NICHT die Antwort — stell mir eine Frage die mich selbst drauf bringt!`
    : `Wie kürze ich "${current.value.full}" — ich weiß noch nicht wie. Was ist mein erster Schritt? Stell mir eine Frage, sag mir nicht die Lösung!`
  showTutor.value = true
  askTutor(q)
}

const types = [
  { id: 'linklocal', tag: 'fe80…', label: 'Link-Local' },
  { id: 'multicast', tag: 'ff…',   label: 'Multicast' },
  { id: 'global',    tag: '2/3…',  label: 'Global Unicast' },
  { id: 'loopback',  tag: '::1',   label: 'Loopback' },
]

const typePool = [
  { addr: 'fe80::1', type: 'linklocal', diff: 'easy', hint: 'fe80 am Anfang = immer Link-Local' },
  { addr: 'ff02::1', type: 'multicast', diff: 'easy', hint: 'ff02::1 = alle Knoten im Segment' },
  { addr: '::1', type: 'loopback', diff: 'easy', hint: '::1 = Loopback, wie 127.0.0.1 bei IPv4' },
  { addr: '2001:db8::1', type: 'global', diff: 'easy', hint: '2001 = Global Unicast (öffentlich routebar)' },
  { addr: 'fe80::a1b2:3c4d', type: 'linklocal', diff: 'medium', hint: 'Jedes Gerät bekommt automatisch eine fe80-Adresse' },
  { addr: 'ff02::2', type: 'multicast', diff: 'medium', hint: 'ff02::2 = alle Router im Segment' },
  { addr: 'ff00::1', type: 'multicast', diff: 'medium', hint: 'ff am Anfang = immer Multicast' },
  { addr: '2a02:8071:2::1', type: 'global', diff: 'medium', hint: '2a02 startet mit 2 = Global Unicast' },
  { addr: 'fe80::1ff:fe23:4567:890a', type: 'linklocal', diff: 'hard', hint: 'Lange Adresse — fe80 am Anfang verrät: Link-Local' },
  { addr: '3ffe::1', type: 'global', diff: 'hard', hint: '3ffe startet mit 3 = Global Unicast' },
  { addr: 'ff0e::1', type: 'multicast', diff: 'hard', hint: 'ff0e = globales Multicast (ff = immer Multicast!)' },
  { addr: '2600::1', type: 'global', diff: 'hard', hint: '26xx startet mit 2 = Global Unicast' },
]

const shortenPool = [
  { diff: 'easy', full: '2001:0db8:0000:0000:0000:0000:0000:0001', short: '2001:db8::1', steps: ['0db8 → db8', '0000:0000:0000:0000:0000 → ::', '0001 → 1'] },
  { diff: 'easy', full: 'fe80:0000:0000:0000:0000:0000:0000:0001', short: 'fe80::1', steps: ['0000:0000:0000:0000:0000:0000 → ::', '0001 → 1'] },
  { diff: 'easy', full: 'ff02:0000:0000:0000:0000:0000:0000:0001', short: 'ff02::1', steps: ['0000:0000:0000:0000:0000:0000 → ::', '0001 → 1'] },
  { diff: 'easy', full: '0000:0000:0000:0000:0000:0000:0000:0001', short: '::1', steps: ['Alle 7 Nullblöcke → ::', '0001 → 1 → Loopback!'] },
  { diff: 'medium', full: '2001:0db8:0000:0042:0000:0000:0000:0001', short: '2001:db8:0:42::1', steps: ['0db8 → db8', '0000 → 0 (allein, kein ::)', '0042 → 42', '0000:0000:0000 → ::', '0001 → 1'] },
  { diff: 'medium', full: '2001:0db8:0001:0000:0000:0000:0000:0001', short: '2001:db8:1::1', steps: ['0db8 → db8', '0001 → 1', '0000:0000:0000:0000 → ::', '0001 → 1'] },
  { diff: 'medium', full: '2001:0db8:0000:0000:0000:0ff0:0042:0001', short: '2001:db8::ff0:42:1', steps: ['0db8 → db8', '0000:0000:0000 → ::', '0ff0 → ff0', '0042 → 42', '0001 → 1'] },
  { diff: 'hard', full: 'fe80:0000:0000:0000:0a12:0000:0000:0001', short: 'fe80::a12:0:0:1', steps: ['0000:0000:0000 → :: (erste, längste Gruppe!)', '0a12 → a12', '0000:0000 bleibt 0:0 (:: schon benutzt!)', '0001 → 1'] },
  { diff: 'hard', full: '2001:0db8:0000:0001:0000:0000:0001:0001', short: '2001:db8:0:1::1:1', steps: ['0db8 → db8', '0000 → 0', '0001 → 1', '0000:0000 → ::', '0001 → 1', '0001 → 1'] },
  { diff: 'hard', full: '2001:0db8:0001:0002:0003:0000:0000:0004', short: '2001:db8:1:2:3::4', steps: ['0db8 → db8', '0001→1', '0002→2', '0003→3', '0000:0000 → ::', '0004 → 4'] },
]


const filteredTypePool = computed(() => typePool.filter((x:any) => x.diff === difficulty.value))
const filteredShortenPool = computed(() => shortenPool.filter((x:any) => x.diff === difficulty.value))
const current = ref<any>({})
const usedTypeIdx = ref<number[]>([])
const usedShortenIdx = ref<number[]>([])

function pickUnused(pool: any[], used: number[]) {
  const avail = pool.map((_, i) => i).filter(i => !used.includes(i))
  if (avail.length === 0) { used.splice(0); return Math.floor(Math.random() * pool.length) }
  return avail[Math.floor(Math.random() * avail.length)]
}

function newRound() {
  answered.value = false
  selected.value = ''
  userInput.value = ''
  typeInput.value = ''
  showHint.value = false
  lastCorrect.value = false
  if (mode.value === 'type') {
    const pool = filteredTypePool.value
    const idx = pickUnused(pool, usedTypeIdx.value)
    usedTypeIdx.value.push(idx)
    current.value = pool[idx]
  } else {
    const pool = filteredShortenPool.value
    const idx = pickUnused(pool, usedShortenIdx.value)
    usedShortenIdx.value.push(idx)
    current.value = pool[idx]
  }
}

function typeLabel(id: string) {
  return types.find(t => t.id === id)?.label || id
}

function checkType() {
  if (!typeInput.value.trim()) return
  answered.value = true
  const input = typeInput.value.trim().toLowerCase().replace(/[-\s]+/g, '')
  const answers: Record<string, string[]> = {
    linklocal: ['linklocal', 'link-local', 'linklokal', 'link-lokal', 'local', 'lokal'],
    multicast: ['multicast'],
    global: ['global', 'globalunicast', 'global unicast', 'unicast'],
    loopback: ['loopback', 'loop'],
  }
  lastCorrect.value = (answers[current.value.type] || []).some(a => a.replace(/[-\s]+/g,'') === input)
  if (lastCorrect.value) { correct.value++; streak.value++; emit('score', 2) }
  else { wrong.value++; streak.value = 0; emit('score', 0) }
}

function normalize(s: string) {
  return s.trim().toLowerCase().replace(/\s+/g, '')
}

function checkShorten() {
  if (!userInput.value.trim()) return
  answered.value = true
  lastCorrect.value = normalize(userInput.value) === normalize(current.value.short)
  if (lastCorrect.value) { correct.value++; streak.value++; emit('score', 3) }
  else { wrong.value++; streak.value = 0; emit('score', 0) }
}


function setDifficulty(d: 'easy'|'medium'|'hard') {
  difficulty.value = d
  usedTypeIdx.value = []
  usedShortenIdx.value = []
  newRound()
}
newRound()
</script>

<style scoped>
.iv6 { display: flex; flex-direction: column; gap: 14px; }

.iv6-modes { display: flex; gap: 8px; }
.iv6-mode-btn {
  flex: 1; padding: 10px; border-radius: 10px; border: 1px solid var(--color-border);
  background: var(--color-surface); color: var(--color-text-secondary);
  cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.15s;
}
.iv6-mode-btn:hover { border-color: #6366f1; color: #a5b4fc; }
.iv6-mode-active { border-color: #6366f1 !important; background: rgba(99,102,241,0.2) !important; color: #a5b4fc !important; }

.iv6-ref {
  background: rgba(14,165,233,0.06); border: 1px solid rgba(14,165,233,0.2);
  border-radius: 10px; padding: 12px 14px;
}
.iv6-ref-title { font-size: 11px; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.iv6-ref-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.iv6-ref-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--color-text-secondary); }
.iv6-ref-tag { font-family: monospace; font-weight: 700; font-size: 12px; padding: 2px 7px; border-radius: 5px; white-space: nowrap; }
.iv6-ll .iv6-ref-tag { background: rgba(251,191,36,0.15); color: #fbbf24; }
.iv6-mc .iv6-ref-tag { background: rgba(239,68,68,0.15); color: #f87171; }
.iv6-gu .iv6-ref-tag { background: rgba(74,222,128,0.15); color: #4ade80; }
.iv6-lo .iv6-ref-tag { background: rgba(167,139,250,0.15); color: #a78bfa; }

.iv6-score-row { display: flex; gap: 12px; align-items: center; font-size: 13px; }
.iv6-score { color: #4ade80; font-weight: 700; }
.iv6-score-wrong { color: #f87171; }
.iv6-streak { color: #fb923c; font-weight: 700; }

.iv6-card {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 14px; padding: 22px; display: flex; flex-direction: column; gap: 16px;
}

.iv6-question { font-size: 14px; color: var(--color-text-secondary); font-weight: 600; }

.iv6-addr {
  font-family: monospace; font-size: 20px; font-weight: 700; color: #38bdf8;
  background: rgba(14,165,233,0.08); border: 1px solid rgba(14,165,233,0.2);
  border-radius: 8px; padding: 14px 16px; word-break: break-all; letter-spacing: 1px;
}

.iv6-choices { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.iv6-choice {
  display: flex; align-items: center; gap: 10px; padding: 12px 14px;
  border-radius: 10px; border: 1px solid var(--color-border);
  background: var(--color-surface); cursor: pointer; transition: all 0.15s;
  font-size: 13px; text-align: left;
}
.iv6-choice:hover:not(:disabled) { border-color: #6366f1; background: rgba(99,102,241,0.1); }
.iv6-choice:disabled { cursor: default; }
.iv6-choice-tag { font-family: monospace; font-weight: 700; font-size: 13px; color: #38bdf8; }
.iv6-choice-label { font-weight: 600; color: var(--color-text-primary); }
.iv6-correct { border-color: #22c55e !important; background: rgba(34,197,94,0.15) !important; }
.iv6-wrong { border-color: #ef4444 !important; background: rgba(239,68,68,0.15) !important; }
.iv6-dim { opacity: 0.4; }

.iv6-rules { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--color-text-secondary); }
.iv6-rules code { background: rgba(255,255,255,0.08); padding: 1px 5px; border-radius: 4px; color: #fbbf24; font-family: monospace; }

.iv6-input {
  width: 100%; padding: 12px 14px; border-radius: 8px;
  border: 1px solid var(--color-border); background: var(--color-bg);
  color: var(--color-text-primary); font-family: monospace; font-size: 16px;
  outline: none; transition: border-color 0.15s;
}
.iv6-input:focus { border-color: #6366f1; }
.iv6-input:disabled { opacity: 0.6; }

.iv6-check-btn {
  align-self: flex-start; padding: 10px 22px; border-radius: 8px;
  background: #4f46e5; color: white; border: none; cursor: pointer;
  font-size: 14px; font-weight: 600; transition: background 0.15s;
}
.iv6-check-btn:hover { background: #6366f1; }

.iv6-feedback {
  border-radius: 8px; padding: 12px 14px; font-size: 13px; font-weight: 600; line-height: 1.6;
}
.iv6-fb-ok { background: rgba(34,197,94,0.12); border: 1px solid #22c55e; color: #4ade80; }
.iv6-fb-err { background: rgba(239,68,68,0.12); border: 1px solid #ef4444; color: #fca5a5; }
.iv6-fb-hint { display: block; font-weight: 400; font-size: 12px; color: var(--color-text-secondary); margin-top: 4px; }
.iv6-fb-err strong { color: #4ade80; font-family: monospace; }

.iv6-steps { margin-top: 8px; display: flex; flex-direction: column; gap: 3px; }
.iv6-step { font-size: 12px; font-weight: 400; color: var(--color-text-secondary); font-family: monospace; }
.iv6-step::before { content: '→ '; color: #38bdf8; }

.iv6-next-btn {
  align-self: flex-end; padding: 10px 24px; border-radius: 8px;
  background: #4f46e5; color: white; border: none; cursor: pointer;
  font-size: 14px; font-weight: 600; transition: background 0.15s;
}
.iv6-next-btn:hover { background: #6366f1; }

.iv6-hint-row { display: flex; gap: 8px; align-items: center; }
.iv6-hint-btn {
  padding: 10px 16px; border-radius: 8px;
  background: rgba(99,102,241,0.15); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.4);
  cursor: pointer; font-size: 13px; font-weight: 600; transition: background 0.15s;
}
.iv6-hint-btn:hover { background: rgba(99,102,241,0.28); }
.iv6-hint-box { display: flex; gap: 8px; flex-wrap: wrap; }
.iv6-hint-tag {
  padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  color: var(--color-text-secondary);
}

.iv6-tutor-wrap { display: flex; flex-direction: column; gap: 0; }
.iv6-tutor-toggle {
  align-self: flex-start; padding: 8px 18px; border-radius: 20px;
  background: rgba(99,102,241,0.15); color: #a5b4fc;
  border: 1px solid rgba(99,102,241,0.4); cursor: pointer;
  font-size: 13px; font-weight: 600; transition: background 0.15s;
}
.iv6-tutor-toggle:hover { background: rgba(99,102,241,0.28); }
.iv6-tutor-panel {
  margin-top: 8px; border: 1px solid var(--color-border);
  border-radius: 14px; overflow: hidden;
  background: var(--color-surface);
}
.iv6-tutor-msgs {
  height: 240px; overflow-y: auto; padding: 14px; display: flex;
  flex-direction: column; gap: 10px;
}
.iv6-tutor-empty { font-size: 13px; color: var(--color-text-secondary); line-height: 1.6; text-align: center; margin: auto; }
.iv6-tutor-msg { max-width: 88%; padding: 10px 14px; border-radius: 14px; font-size: 13px; line-height: 1.6; white-space: pre-wrap; }
.iv6-tm-user { align-self: flex-end; background: #4f46e5; color: white; border-bottom-right-radius: 4px; }
.iv6-tm-bot { align-self: flex-start; background: rgba(255,255,255,0.07); color: var(--color-text-primary); border-bottom-left-radius: 4px; border: 1px solid var(--color-border); }
.iv6-tm-loading { opacity: 0.6; font-style: italic; }
.iv6-tutor-input-row { display: flex; gap: 6px; padding: 10px 12px; border-top: 1px solid var(--color-border); }
.iv6-tutor-ctx-btn {
  padding: 8px 12px; border-radius: 8px; font-size: 12px; font-weight: 600;
  background: rgba(251,191,36,0.12); color: #fbbf24;
  border: 1px solid rgba(251,191,36,0.3); cursor: pointer; white-space: nowrap;
  transition: background 0.15s;
}
.iv6-tutor-ctx-btn:hover:not(:disabled) { background: rgba(251,191,36,0.22); }
.iv6-tutor-ctx-btn:disabled { opacity: 0.4; cursor: default; }
.iv6-tutor-input {
  flex: 1; padding: 8px 12px; border-radius: 8px; font-size: 13px;
  border: 1px solid var(--color-border); background: var(--color-bg);
  color: var(--color-text-primary); outline: none;
}
.iv6-tutor-input:focus { border-color: #6366f1; }
.iv6-tutor-send {
  padding: 8px 14px; border-radius: 8px; background: #4f46e5; color: white;
  border: none; cursor: pointer; font-size: 15px; font-weight: 700;
  transition: background 0.15s;
}
.iv6-tutor-send:hover:not(:disabled) { background: #6366f1; }
.iv6-tutor-send:disabled { opacity: 0.4; cursor: default; }

.iv6-diff-row { display: flex; gap: 8px; }
.iv6-diff-btn { flex: 1; padding: 8px; border-radius: 10px; border: 1px solid var(--color-border); background: var(--color-surface); color: var(--color-text-secondary); cursor: pointer; font-size: 12px; font-weight: 600; transition: all 0.15s; }
.iv6-diff-btn:hover { opacity: 0.85; }
.iv6-diff-on { font-weight: 700; }
.iv6-diff-easy { border-color: #4ade80 !important; background: rgba(74,222,128,0.15) !important; color: #4ade80 !important; }
.iv6-diff-medium { border-color: #fbbf24 !important; background: rgba(251,191,36,0.15) !important; color: #fbbf24 !important; }
.iv6-diff-hard { border-color: #f87171 !important; background: rgba(248,113,113,0.15) !important; color: #f87171 !important; }
</style>
