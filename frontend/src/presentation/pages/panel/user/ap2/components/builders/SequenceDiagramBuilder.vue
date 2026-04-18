<template>
  <div class="sq-builder">
    <!-- Toolbar -->
    <div class="sq-toolbar">
      <div class="sq-toolbar-group">
        <button class="sq-btn" @click="addActor('object')" :disabled="submitted">
          <span class="sq-icon">&#9634;</span> Objekt
        </button>
        <button class="sq-btn" @click="addActor('actor')" :disabled="submitted">
          <span class="sq-icon">&#9786;</span> Akteur
        </button>
        <button class="sq-btn" @click="addActor('system')" :disabled="submitted">
          <span class="sq-icon">&#9881;</span> System
        </button>
      </div>
      <div class="sq-toolbar-group">
        <button
          class="sq-btn"
          @click="addMessage"
          :disabled="submitted || actors.length < 2"
        >
          &#8594; Nachricht
        </button>
        <button class="sq-btn sq-btn-danger" @click="clearAll" :disabled="submitted">
          &#128465; Leeren
        </button>
      </div>
    </div>

    <!-- SVG Canvas -->
    <div class="sq-canvas-wrap">
      <svg
        class="sq-canvas"
        :viewBox="`0 0 ${cW} ${cH}`"
        ref="svgEl"
      >
        <defs>
          <pattern id="sq-grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.02)" stroke-width="0.5" />
          </pattern>
          <marker id="sq-arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <path d="M0,0 L8,3 L0,6 Z" fill="#546e7a" />
          </marker>
          <marker id="sq-arr-sel" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <path d="M0,0 L8,3 L0,6 Z" fill="#1a73e8" />
          </marker>
          <marker id="sq-arr-ret" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <path d="M0,0 L8,3 L0,6" fill="none" stroke="#546e7a" stroke-width="1" />
          </marker>
        </defs>
        <rect width="100%" height="100%" fill="url(#sq-grid)" />

        <!-- Actor Headers -->
        <g v-for="(actor, ai) in actors" :key="actor.id">
          <!-- Header-Box -->
          <rect
            :x="actorX(ai) - 50" y="10" width="100" height="40" rx="5"
            class="sq-actor-box"
            :class="{
              'sq-actor-sel': selectedActorId === actor.id,
              'sq-actor-type-actor': actor.type === 'actor',
              'sq-actor-type-system': actor.type === 'system',
            }"
            @click.stop="selectActor(actor.id)"
          />
          <!-- Strichmännchen für Akteur -->
          <g v-if="actor.type === 'actor'" :transform="`translate(${actorX(ai) - 50}, 12)`">
            <circle cx="10" cy="6" r="5" class="sq-stickman" />
            <line x1="10" y1="11" x2="10" y2="24" class="sq-stickman" />
            <line x1="2" y1="16" x2="18" y2="16" class="sq-stickman" />
            <line x1="10" y1="24" x2="3" y2="34" class="sq-stickman" />
            <line x1="10" y1="24" x2="17" y2="34" class="sq-stickman" />
          </g>
          <!-- Name -->
          <text
            :x="actor.type === 'actor' ? actorX(ai) + 5 : actorX(ai)"
            y="35"
            :text-anchor="actor.type === 'actor' ? 'start' : 'middle'"
            class="sq-actor-name"
            @click.stop="selectActor(actor.id)"
          >
            {{ actor.name }}
          </text>
          <!-- Lebenslinie -->
          <line
            :x1="actorX(ai)" y1="50"
            :x2="actorX(ai)" :y2="cH - 20"
            class="sq-lifeline"
          />
        </g>

        <!-- Messages -->
        <g v-for="(msg, mi) in sortedMessages" :key="msg.id">
          <line
            :x1="actorX(actorIndex(msg.from))"
            :y1="msgY(mi)"
            :x2="actorX(actorIndex(msg.to))"
            :y2="msgY(mi)"
            class="sq-msg-line"
            :class="{
              'sq-msg-sel': selectedMsgId === msg.id,
              'sq-msg-return': msg.type === 'return',
              'sq-msg-async': msg.type === 'async',
            }"
            :marker-end="selectedMsgId === msg.id ? 'url(#sq-arr-sel)' : msg.type === 'return' ? 'url(#sq-arr-ret)' : 'url(#sq-arr)'"
            @click.stop="selectMsg(msg.id)"
          />
          <!-- Sequenznummer + Label -->
          <text
            :x="(actorX(actorIndex(msg.from)) + actorX(actorIndex(msg.to))) / 2"
            :y="msgY(mi) - 6"
            text-anchor="middle"
            class="sq-msg-label"
            @click.stop="selectMsg(msg.id)"
          >
            {{ msg.sequence }}. {{ msg.label }}
          </text>
        </g>
      </svg>
    </div>

    <!-- Actor Props -->
    <div v-if="selectedActorId && !submitted" class="sq-props">
      <div class="sq-props-header">
        <span>Akteur/Objekt bearbeiten</span>
        <button class="sq-btn-sm sq-btn-danger" @click="deleteActor(selectedActorId)">Löschen</button>
      </div>
      <div class="sq-prop-row">
        <label class="sq-prop-label">Name:</label>
        <input :value="selActor?.name" @input="updateActor('name', ($event.target as HTMLInputElement).value)" class="sq-prop-input" />
      </div>
      <div class="sq-prop-row">
        <label class="sq-prop-label">Typ:</label>
        <select :value="selActor?.type" @change="updateActor('type', ($event.target as HTMLSelectElement).value)" class="sq-prop-select">
          <option value="object">Objekt</option>
          <option value="actor">Akteur</option>
          <option value="system">System</option>
        </select>
      </div>
    </div>

    <!-- Message Props -->
    <div v-if="selectedMsgId && !submitted" class="sq-props">
      <div class="sq-props-header">
        <span>Nachricht bearbeiten</span>
        <button class="sq-btn-sm sq-btn-danger" @click="deleteMsg(selectedMsgId)">Löschen</button>
      </div>
      <div class="sq-prop-row">
        <label class="sq-prop-label">Von:</label>
        <select :value="selMsg?.from" @change="updateMsg('from', ($event.target as HTMLSelectElement).value)" class="sq-prop-select">
          <option v-for="a in actors" :key="a.id" :value="a.id">{{ a.name }}</option>
        </select>
      </div>
      <div class="sq-prop-row">
        <label class="sq-prop-label">An:</label>
        <select :value="selMsg?.to" @change="updateMsg('to', ($event.target as HTMLSelectElement).value)" class="sq-prop-select">
          <option v-for="a in actors" :key="a.id" :value="a.id">{{ a.name }}</option>
        </select>
      </div>
      <div class="sq-prop-row">
        <label class="sq-prop-label">Label:</label>
        <input :value="selMsg?.label" @input="updateMsg('label', ($event.target as HTMLInputElement).value)" class="sq-prop-input" placeholder="z.B. HTTP GET /api" />
      </div>
      <div class="sq-prop-row">
        <label class="sq-prop-label">Typ:</label>
        <select :value="selMsg?.type" @change="updateMsg('type', ($event.target as HTMLSelectElement).value)" class="sq-prop-select">
          <option value="sync">Synchron</option>
          <option value="async">Asynchron</option>
          <option value="return">Rückgabe</option>
          <option value="create">Erzeugung</option>
          <option value="destroy">Zerstörung</option>
        </select>
      </div>
      <div class="sq-prop-row">
        <label class="sq-prop-label">Reihenfolge:</label>
        <input type="number" :value="selMsg?.sequence" @input="updateMsg('sequence', parseInt(($event.target as HTMLInputElement).value) || 0)" class="sq-prop-input sq-prop-input-num" min="1" />
      </div>
    </div>

    <!-- Result -->
    <div v-if="submitted && result" class="sq-result">
      <div class="sq-result-score" :class="rClass">{{ result.pct }}% — {{ result.feedback }}</div>
      <div v-if="result.details" class="sq-result-details">
        <div v-if="result.details.nodeScore !== undefined" class="sq-result-row">
          <span>Akteure/Objekte:</span> <span class="sq-result-val">{{ result.details.nodeScore }}%</span>
        </div>
        <div v-if="result.details.edgeScore !== undefined" class="sq-result-row">
          <span>Nachrichten:</span> <span class="sq-result-val">{{ result.details.edgeScore }}%</span>
        </div>
        <div v-if="result.details.sequenceScore !== undefined" class="sq-result-row">
          <span>Reihenfolge:</span> <span class="sq-result-val">{{ result.details.sequenceScore }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { SequenceActor, SequenceMessage, SequenceDiagramData, SequenceMessageType, DiagramGradingResult } from '../../types'

const props = defineProps<{
  template?: SequenceDiagramData
  solution?: SequenceDiagramData
  submitted: boolean
  instructions?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', data: SequenceDiagramData): void
  (e: 'graded', result: DiagramGradingResult): void
}>()

const cW = 900, cH = 600
const actors = ref<SequenceActor[]>([])
const messages = ref<SequenceMessage[]>([])
const selectedActorId = ref<string | null>(null)
const selectedMsgId = ref<string | null>(null)
const svgEl = ref<SVGSVGElement | null>(null)
const result = ref<DiagramGradingResult | null>(null)
let nid = 1

const selActor = computed(() => actors.value.find(a => a.id === selectedActorId.value))
const selMsg = computed(() => messages.value.find(m => m.id === selectedMsgId.value))
const sortedMessages = computed(() => [...messages.value].sort((a, b) => a.sequence - b.sequence))
const rClass = computed(() => {
  if (!result.value) return ''
  return result.value.pct >= 80 ? 'sq-result-great' : result.value.pct >= 50 ? 'sq-result-ok' : 'sq-result-bad'
})

function actorX(idx: number): number {
  const spacing = Math.min(200, (cW - 100) / Math.max(actors.value.length, 1))
  return 80 + idx * spacing
}

function actorIndex(id: string): number {
  return actors.value.findIndex(a => a.id === id)
}

function msgY(sortedIdx: number): number {
  return 90 + sortedIdx * 50
}

function addActor(type: SequenceActor['type']) {
  const id = `a${nid++}`
  actors.value.push({ id, name: type === 'actor' ? 'Benutzer' : type === 'system' ? 'System' : 'Objekt', type })
  selectedActorId.value = id; selectedMsgId.value = null; emitData()
}

function deleteActor(id: string) {
  actors.value = actors.value.filter(a => a.id !== id)
  messages.value = messages.value.filter(m => m.from !== id && m.to !== id)
  selectedActorId.value = null; emitData()
}

function updateActor(field: string, val: string) {
  const a = actors.value.find(ac => ac.id === selectedActorId.value)
  if (a) { (a as any)[field] = val; emitData() }
}

function selectActor(id: string) { selectedActorId.value = id; selectedMsgId.value = null }

function addMessage() {
  if (actors.value.length < 2) return
  const id = `m${nid++}`
  const seq = messages.value.length + 1
  messages.value.push({
    id, from: actors.value[0].id, to: actors.value[1].id,
    label: 'Neue Nachricht', type: 'sync', sequence: seq,
  })
  selectedMsgId.value = id; selectedActorId.value = null; emitData()
}

function deleteMsg(id: string) {
  messages.value = messages.value.filter(m => m.id !== id)
  // Sequenzen neu nummerieren
  const sorted = [...messages.value].sort((a, b) => a.sequence - b.sequence)
  sorted.forEach((m, i) => { m.sequence = i + 1 })
  selectedMsgId.value = null; emitData()
}

function updateMsg(field: string, val: any) {
  const m = messages.value.find(msg => msg.id === selectedMsgId.value)
  if (m) { (m as any)[field] = val; emitData() }
}

function selectMsg(id: string) { selectedMsgId.value = id; selectedActorId.value = null }

function clearAll() {
  actors.value = []; messages.value = []
  selectedActorId.value = null; selectedMsgId.value = null
  nid = 1; emitData()
}

function emitData() {
  emit('update:modelValue', {
    actors: actors.value.map(a => ({ ...a })),
    messages: messages.value.map(m => ({ ...m })),
  })
}

// Grading
function grade(): DiagramGradingResult {
  if (!props.solution) return { pct: 0, feedback: 'Keine Musterlösung', details: {} }
  const sol = props.solution as SequenceDiagramData

  // Actor score
  let matchedActors = 0
  for (const sa of sol.actors) {
    const found = actors.value.find(a => a.name.toLowerCase() === sa.name.toLowerCase())
    if (found) matchedActors++
  }
  const nodeScore = sol.actors.length > 0 ? Math.round((matchedActors / sol.actors.length) * 100) : 100

  // Message score (from→to pair + label contains)
  let matchedMsgs = 0
  for (const sm of sol.messages) {
    const sfName = sol.actors.find(a => a.id === sm.from)?.name.toLowerCase() || ''
    const stName = sol.actors.find(a => a.id === sm.to)?.name.toLowerCase() || ''
    const found = messages.value.find(m => {
      const uf = actors.value.find(a => a.id === m.from)?.name.toLowerCase() || ''
      const ut = actors.value.find(a => a.id === m.to)?.name.toLowerCase() || ''
      return uf === sfName && ut === stName && m.label.toLowerCase().includes(sm.label.toLowerCase().slice(0, 5))
    })
    if (found) matchedMsgs++
  }
  const edgeScore = sol.messages.length > 0 ? Math.round((matchedMsgs / sol.messages.length) * 100) : 100

  // Sequence order score
  let orderCorrect = 0
  const solSorted = [...sol.messages].sort((a, b) => a.sequence - b.sequence)
  const userSorted = [...messages.value].sort((a, b) => a.sequence - b.sequence)
  for (let i = 0; i < solSorted.length; i++) {
    const sm = solSorted[i]
    const sfName = sol.actors.find(a => a.id === sm.from)?.name.toLowerCase() || ''
    const stName = sol.actors.find(a => a.id === sm.to)?.name.toLowerCase() || ''
    if (userSorted[i]) {
      const uf = actors.value.find(a => a.id === userSorted[i].from)?.name.toLowerCase() || ''
      const ut = actors.value.find(a => a.id === userSorted[i].to)?.name.toLowerCase() || ''
      if (uf === sfName && ut === stName) orderCorrect++
    }
  }
  const sequenceScore = solSorted.length > 0 ? Math.round((orderCorrect / solSorted.length) * 100) : 100

  const pct = Math.round(nodeScore * 0.2 + edgeScore * 0.5 + sequenceScore * 0.3)
  let feedback = pct >= 90 ? 'Perfekt!' : pct >= 70 ? 'Gut, leichte Abweichungen.' : pct >= 50 ? 'Grundidee da, Details fehlen.' : 'Noch deutlich zu verbessern.'
  return { pct, feedback, details: { nodeScore, edgeScore, sequenceScore } }
}

onMounted(() => {
  if (props.template) {
    actors.value = props.template.actors.map(a => ({ ...a }))
    messages.value = props.template.messages.map(m => ({ ...m }))
    nid = actors.value.length + messages.value.length + 1
  }
})

watch(() => props.submitted, (s) => { if (s) { const r = grade(); result.value = r; emit('graded', r) } })
</script>

<style scoped>
.sq-builder { width: 100%; margin: 12px 0; }
.sq-toolbar {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  background: rgba(0,0,0,0.2); border-radius: 8px 8px 0 0;
  border: 1px solid rgba(255,255,255,0.06); border-bottom: none; flex-wrap: wrap;
}
.sq-toolbar-group { display: flex; gap: 6px; }
.sq-btn {
  padding: 5px 10px; background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 5px;
  color: #b0bec5; font-size: 0.8rem; cursor: pointer; transition: all 0.15s;
  display: flex; align-items: center; gap: 5px;
}
.sq-btn:hover:not(:disabled) { background: rgba(26,115,232,0.12); color: #e3f2fd; }
.sq-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.sq-btn-danger { color: #ef5350; }
.sq-btn-sm { padding: 3px 8px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: #90a4ae; font-size: 0.75rem; cursor: pointer; }
.sq-icon { font-size: 0.9rem; }

.sq-canvas-wrap { border: 1px solid rgba(255,255,255,0.06); border-radius: 0 0 8px 8px; overflow: hidden; background: rgba(0,0,0,0.25); }
.sq-canvas { width: 100%; height: 500px; display: block; }

.sq-actor-box { fill: rgba(38,50,56,0.85); stroke: #546e7a; stroke-width: 1.5; cursor: pointer; }
.sq-actor-sel { stroke: #1a73e8; stroke-width: 2; }
.sq-actor-type-actor { stroke: #66bb6a; }
.sq-actor-type-system { stroke: #ff9800; }
.sq-actor-name { fill: #e0e0e0; font-size: 11px; font-weight: 600; cursor: pointer; }
.sq-stickman { stroke: #66bb6a; stroke-width: 1.5; fill: none; }
.sq-stickman:first-child { fill: rgba(102,187,106,0.2); }
.sq-lifeline { stroke: #37474f; stroke-width: 1; stroke-dasharray: 4 3; }

.sq-msg-line { stroke: #546e7a; stroke-width: 1.5; cursor: pointer; }
.sq-msg-line:hover { stroke: #90a4ae; }
.sq-msg-sel { stroke: #1a73e8; stroke-width: 2; }
.sq-msg-return { stroke-dasharray: 6 3; }
.sq-msg-async { stroke-dasharray: 3 3; }
.sq-msg-label { fill: #b0bec5; font-size: 10px; cursor: pointer; }

.sq-props { margin-top: 10px; padding: 12px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; }
.sq-props-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 0.85rem; font-weight: 600; color: #e3f2fd; }
.sq-prop-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.sq-prop-label { font-size: 0.8rem; color: #90a4ae; min-width: 85px; }
.sq-prop-input { flex: 1; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; padding: 5px 8px; color: #e0e0e0; font-size: 0.82rem; outline: none; }
.sq-prop-input:focus { border-color: #1a73e8; }
.sq-prop-input-num { max-width: 70px; }
.sq-prop-select { flex: 1; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; padding: 5px 8px; color: #e0e0e0; font-size: 0.82rem; outline: none; }

.sq-result { margin-top: 12px; padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); }
.sq-result-score { font-size: 0.9rem; font-weight: 600; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; }
.sq-result-great { background: rgba(34,197,94,0.12); color: #22c55e; }
.sq-result-ok { background: rgba(245,158,11,0.12); color: #f59e0b; }
.sq-result-bad { background: rgba(239,68,68,0.12); color: #ef4444; }
.sq-result-details { display: flex; flex-direction: column; gap: 4px; }
.sq-result-row { display: flex; justify-content: space-between; font-size: 0.82rem; color: #90a4ae; padding: 4px 8px; }
.sq-result-val { font-weight: 600; color: #e0e0e0; font-family: 'JetBrains Mono', monospace; }
</style>
