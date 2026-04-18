<template>
  <div class="sd-builder">
    <!-- Toolbar -->
    <div class="sd-toolbar">
      <div class="sd-toolbar-group">
        <button class="sd-btn" @click="addState(false)" :disabled="submitted">
          <span class="sd-shape-prev sd-shape-state"></span> Zustand
        </button>
        <button class="sd-btn" @click="addState(true, false)" :disabled="submitted || hasInitial">
          <span class="sd-shape-prev sd-shape-initial"></span> Startzustand
        </button>
        <button class="sd-btn" @click="addState(false, true)" :disabled="submitted || hasFinal">
          <span class="sd-shape-prev sd-shape-final"></span> Endzustand
        </button>
      </div>
      <div class="sd-toolbar-group">
        <button
          class="sd-btn"
          @click="toggleConnect"
          :disabled="submitted || states.length < 2"
          :class="{ 'sd-btn-active': isConnecting }"
        >
          &#8594; Transition
        </button>
        <button class="sd-btn sd-btn-danger" @click="clearAll" :disabled="submitted">&#128465; Leeren</button>
      </div>
    </div>

    <!-- Canvas -->
    <div class="sd-canvas-wrap">
      <svg
        class="sd-canvas"
        :viewBox="`0 0 ${cW} ${cH}`"
        ref="svgEl"
        @mousemove="onMove"
        @mouseup="onUp"
        @mousedown.self="deselect"
      >
        <defs>
          <pattern id="sd-grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.025)" stroke-width="0.5" />
          </pattern>
          <marker id="sd-arrow" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <path d="M0,0 L8,3 L0,6 Z" fill="#546e7a" />
          </marker>
          <marker id="sd-arrow-sel" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <path d="M0,0 L8,3 L0,6 Z" fill="#1a73e8" />
          </marker>
        </defs>
        <rect width="100%" height="100%" fill="url(#sd-grid)" />

        <!-- Transitions -->
        <g v-for="tr in transitions" :key="tr.id">
          <path
            :d="getTransitionPath(tr)"
            class="sd-trans-line"
            :class="{ 'sd-trans-sel': selectedTransId === tr.id }"
            :marker-end="selectedTransId === tr.id ? 'url(#sd-arrow-sel)' : 'url(#sd-arrow)'"
            @click.stop="selectTrans(tr.id)"
          />
          <!-- Label auf der Kante -->
          <text
            :x="getTransMid(tr).x"
            :y="getTransMid(tr).y - 8"
            text-anchor="middle"
            class="sd-trans-label"
            @click.stop="selectTrans(tr.id)"
          >
            {{ formatTransLabel(tr) }}
          </text>
        </g>

        <!-- Preview -->
        <line
          v-if="isConnecting && connectFrom && mouse"
          :x1="stateCenter(connectFrom).x" :y1="stateCenter(connectFrom).y"
          :x2="mouse.x" :y2="mouse.y"
          class="sd-connect-preview"
        />

        <!-- States -->
        <g
          v-for="st in states"
          :key="st.id"
          :transform="`translate(${st._x}, ${st._y})`"
          class="sd-state-group"
          :class="{
            'sd-state-selected': selectedStateId === st.id,
            'sd-state-connect': isConnecting && connectFrom && connectFrom !== st.id
          }"
          @mousedown.stop="onStateDown(st, $event)"
          @click.stop="onStateClick(st)"
        >
          <!-- Startzustand: Gefüllter Kreis -->
          <circle v-if="st.isInitial" cx="60" cy="24" r="10" class="sd-initial-dot" />
          <!-- Endzustand: Bullseye -->
          <g v-else-if="st.isFinal">
            <circle cx="60" cy="24" r="14" class="sd-final-outer" />
            <circle cx="60" cy="24" r="9" class="sd-final-inner" />
          </g>
          <!-- Normaler Zustand -->
          <rect
            v-if="!st.isInitial && !st.isFinal"
            width="120" height="48" rx="12"
            class="sd-state-rect"
            :class="{ 'sd-state-rect-sel': selectedStateId === st.id }"
          />
          <!-- Name -->
          <text
            x="60" :y="st.isInitial || st.isFinal ? 28 : 28"
            text-anchor="middle"
            class="sd-state-name"
            :class="{ 'sd-special-label': st.isInitial || st.isFinal }"
          >
            {{ st.isInitial ? '●' : st.isFinal ? '◉' : st.name }}
          </text>
          <!-- Name unter Special-Nodes -->
          <text
            v-if="st.isInitial || st.isFinal"
            x="60" y="52"
            text-anchor="middle"
            class="sd-state-sub"
          >
            {{ st.name }}
          </text>
        </g>
      </svg>
    </div>

    <!-- State Props -->
    <div v-if="selectedStateId && !submitted && selectedState && !selectedState.isInitial && !selectedState.isFinal" class="sd-props">
      <div class="sd-props-header">
        <span>Zustand bearbeiten</span>
        <button class="sd-btn-sm sd-btn-danger" @click="deleteState(selectedStateId)">Löschen</button>
      </div>
      <div class="sd-prop-row">
        <label class="sd-prop-label">Name:</label>
        <input :value="selectedState.name" @input="updateStateName(($event.target as HTMLInputElement).value)" class="sd-prop-input" placeholder="Zustandsname" />
      </div>
    </div>

    <!-- Transition Props -->
    <div v-if="selectedTransId && !submitted && selectedTrans" class="sd-props">
      <div class="sd-props-header">
        <span>Transition bearbeiten</span>
        <button class="sd-btn-sm sd-btn-danger" @click="deleteTrans(selectedTransId)">Löschen</button>
      </div>
      <div class="sd-prop-row">
        <label class="sd-prop-label">Auslöser:</label>
        <input :value="selectedTrans.trigger" @input="updateTrans('trigger', ($event.target as HTMLInputElement).value)" class="sd-prop-input" placeholder="z.B. Paket empfangen" />
      </div>
      <div class="sd-prop-row">
        <label class="sd-prop-label">Bedingung:</label>
        <input :value="selectedTrans.guard || ''" @input="updateTrans('guard', ($event.target as HTMLInputElement).value)" class="sd-prop-input" placeholder="[optional, z.B. CRC OK]" />
      </div>
      <div class="sd-prop-row">
        <label class="sd-prop-label">Aktion:</label>
        <input :value="selectedTrans.action || ''" @input="updateTrans('action', ($event.target as HTMLInputElement).value)" class="sd-prop-input" placeholder="/ optional, z.B. ACK senden" />
      </div>
    </div>

    <!-- Ergebnis -->
    <div v-if="submitted && result" class="sd-result">
      <div class="sd-result-score" :class="rClass">{{ result.pct }}% — {{ result.feedback }}</div>
      <div v-if="result.details" class="sd-result-details">
        <div v-if="result.details.nodeScore !== undefined" class="sd-result-row">
          <span>Zustände:</span> <span class="sd-result-val">{{ result.details.nodeScore }}%</span>
        </div>
        <div v-if="result.details.edgeScore !== undefined" class="sd-result-row">
          <span>Transitionen:</span> <span class="sd-result-val">{{ result.details.edgeScore }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { StateNode, StateTransition, StateDiagramData, DiagramGradingResult } from '../../types'

interface PosState extends StateNode { _x: number; _y: number }

const props = defineProps<{
  template?: StateDiagramData
  solution?: StateDiagramData
  submitted: boolean
  instructions?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', data: StateDiagramData): void
  (e: 'graded', result: DiagramGradingResult): void
}>()

const cW = 900, cH = 600
const states = ref<PosState[]>([])
const transitions = ref<StateTransition[]>([])
const selectedStateId = ref<string | null>(null)
const selectedTransId = ref<string | null>(null)
const isConnecting = ref(false)
const connectFrom = ref<string | null>(null)
const mouse = ref<{ x: number; y: number } | null>(null)
const dragState = ref<string | null>(null)
const dragOff = ref({ x: 0, y: 0 })
const svgEl = ref<SVGSVGElement | null>(null)
const result = ref<DiagramGradingResult | null>(null)
let nid = 1

const selectedState = computed(() => states.value.find(s => s.id === selectedStateId.value))
const selectedTrans = computed(() => transitions.value.find(t => t.id === selectedTransId.value))
const hasInitial = computed(() => states.value.some(s => s.isInitial))
const hasFinal = computed(() => states.value.some(s => s.isFinal))
const rClass = computed(() => {
  if (!result.value) return ''
  return result.value.pct >= 80 ? 'sd-result-great' : result.value.pct >= 50 ? 'sd-result-ok' : 'sd-result-bad'
})

function stateCenter(id: string): { x: number; y: number } {
  const s = states.value.find(st => st.id === id)
  if (!s) return { x: 0, y: 0 }
  return { x: s._x + 60, y: s._y + 24 }
}

function svgPt(e: MouseEvent): { x: number; y: number } {
  if (!svgEl.value) return { x: 0, y: 0 }
  const pt = svgEl.value.createSVGPoint()
  pt.x = e.clientX; pt.y = e.clientY
  const ctm = svgEl.value.getScreenCTM()?.inverse()
  if (ctm) { const t = pt.matrixTransform(ctm); return { x: t.x, y: t.y } }
  return { x: 0, y: 0 }
}

function formatTransLabel(tr: StateTransition): string {
  let lbl = tr.trigger || ''
  if (tr.guard) lbl += ` [${tr.guard}]`
  if (tr.action) lbl += ` / ${tr.action}`
  return lbl || '?'
}

function getTransitionPath(tr: StateTransition): string {
  const f = stateCenter(tr.from)
  const t = stateCenter(tr.to)
  if (tr.from === tr.to) {
    // Selbst-Transition (Loop)
    return `M ${f.x} ${f.y - 24} C ${f.x - 40} ${f.y - 80}, ${f.x + 40} ${f.y - 80}, ${f.x} ${f.y - 24}`
  }
  // Leichte Kurve für parallele Kanten
  const dx = t.x - f.x, dy = t.y - f.y
  const len = Math.sqrt(dx * dx + dy * dy) || 1
  const offset = 15
  const mx = (f.x + t.x) / 2 + (-dy / len) * offset
  const my = (f.y + t.y) / 2 + (dx / len) * offset
  return `M ${f.x} ${f.y} Q ${mx} ${my} ${t.x} ${t.y}`
}

function getTransMid(tr: StateTransition): { x: number; y: number } {
  const f = stateCenter(tr.from), t = stateCenter(tr.to)
  if (tr.from === tr.to) return { x: f.x, y: f.y - 65 }
  const dx = t.x - f.x, dy = t.y - f.y, len = Math.sqrt(dx * dx + dy * dy) || 1
  return { x: (f.x + t.x) / 2 + (-dy / len) * 15, y: (f.y + t.y) / 2 + (dx / len) * 15 }
}

function addState(initial = false, final = false) {
  const id = `s${nid++}`
  const col = states.value.length % 4
  const row = Math.floor(states.value.length / 4)
  states.value.push({
    id, name: initial ? 'Start' : final ? 'Ende' : 'Neuer Zustand',
    isInitial: initial, isFinal: final,
    _x: 80 + col * 200, _y: 60 + row * 140,
  })
  selectedStateId.value = id; selectedTransId.value = null; emitData()
}

function deleteState(id: string) {
  states.value = states.value.filter(s => s.id !== id)
  transitions.value = transitions.value.filter(t => t.from !== id && t.to !== id)
  selectedStateId.value = null; emitData()
}

function updateStateName(name: string) {
  const s = states.value.find(st => st.id === selectedStateId.value)
  if (s) { s.name = name; emitData() }
}

function toggleConnect() { isConnecting.value = !isConnecting.value; connectFrom.value = null; mouse.value = null }
function selectTrans(id: string) { if (!isConnecting.value) { selectedTransId.value = id; selectedStateId.value = null } }
function deleteTrans(id: string) { transitions.value = transitions.value.filter(t => t.id !== id); selectedTransId.value = null; emitData() }
function updateTrans(field: string, val: string) {
  const t = transitions.value.find(tr => tr.id === selectedTransId.value)
  if (t) { (t as any)[field] = val; emitData() }
}
function clearAll() { states.value = []; transitions.value = []; selectedStateId.value = null; selectedTransId.value = null; nid = 1; emitData() }
function deselect() { if (!isConnecting.value) { selectedStateId.value = null; selectedTransId.value = null } }

function onStateClick(st: PosState) {
  if (isConnecting.value) {
    if (!connectFrom.value) { connectFrom.value = st.id }
    else {
      const id = `t${nid++}`
      transitions.value.push({ id, from: connectFrom.value, to: st.id, trigger: '' })
      connectFrom.value = null; mouse.value = null; isConnecting.value = false
      selectedTransId.value = id; emitData()
    }
    return
  }
  selectedStateId.value = st.id; selectedTransId.value = null
}

function onStateDown(st: PosState, e: MouseEvent) {
  if (props.submitted || isConnecting.value) return
  dragState.value = st.id; const pt = svgPt(e)
  dragOff.value = { x: pt.x - st._x, y: pt.y - st._y }
}

function onMove(e: MouseEvent) {
  const pt = svgPt(e)
  if (isConnecting.value && connectFrom.value) mouse.value = pt
  if (dragState.value) {
    const s = states.value.find(st => st.id === dragState.value)
    if (s) { s._x = Math.max(0, pt.x - dragOff.value.x); s._y = Math.max(0, pt.y - dragOff.value.y) }
  }
}

function onUp() { dragState.value = null }

function emitData() {
  emit('update:modelValue', {
    states: states.value.map(s => ({ id: s.id, name: s.name, isInitial: s.isInitial, isFinal: s.isFinal })),
    transitions: transitions.value.map(t => ({ ...t })),
  })
}

// Grading
function grade(): DiagramGradingResult {
  if (!props.solution) return { pct: 0, feedback: 'Keine Musterlösung', details: {} }
  const sol = props.solution as StateDiagramData

  let matchedStates = 0
  for (const ss of sol.states) {
    const found = states.value.find(s => s.name.toLowerCase() === ss.name.toLowerCase() || (ss.isInitial && s.isInitial) || (ss.isFinal && s.isFinal))
    if (found) matchedStates++
  }
  const nodeScore = sol.states.length > 0 ? Math.round((matchedStates / sol.states.length) * 100) : 100

  let matchedTrans = 0
  for (const st of sol.transitions) {
    const sfName = sol.states.find(s => s.id === st.from)?.name.toLowerCase() || ''
    const stName = sol.states.find(s => s.id === st.to)?.name.toLowerCase() || ''
    const found = transitions.value.find(t => {
      const uf = states.value.find(s => s.id === t.from)?.name.toLowerCase() || ''
      const ut = states.value.find(s => s.id === t.to)?.name.toLowerCase() || ''
      return uf === sfName && ut === stName && t.trigger.toLowerCase().includes(st.trigger.toLowerCase().slice(0, 4))
    })
    if (found) matchedTrans++
  }
  const edgeScore = sol.transitions.length > 0 ? Math.round((matchedTrans / sol.transitions.length) * 100) : 100

  const pct = Math.round(nodeScore * 0.45 + edgeScore * 0.55)
  let feedback = pct >= 90 ? 'Ausgezeichnet!' : pct >= 70 ? 'Gut, einige Details fehlen.' : pct >= 50 ? 'Grundstruktur da, aber Lücken.' : 'Noch viel Arbeit nötig.'
  return { pct, feedback, details: { nodeScore, edgeScore } }
}

onMounted(() => {
  if (props.template) {
    states.value = props.template.states.map((s, i) => ({ ...s, _x: 80 + (i % 4) * 200, _y: 60 + Math.floor(i / 4) * 140 }))
    transitions.value = props.template.transitions.map(t => ({ ...t }))
    nid = props.template.states.length + props.template.transitions.length + 1
  }
})

watch(() => props.submitted, (s) => { if (s) { const r = grade(); result.value = r; emit('graded', r) } })
</script>

<style scoped>
.sd-builder { width: 100%; margin: 12px 0; }
.sd-toolbar {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  background: rgba(0,0,0,0.2); border-radius: 8px 8px 0 0;
  border: 1px solid rgba(255,255,255,0.06); border-bottom: none; flex-wrap: wrap;
}
.sd-toolbar-group { display: flex; gap: 6px; }
.sd-btn {
  padding: 5px 10px; background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 5px;
  color: #b0bec5; font-size: 0.8rem; cursor: pointer; transition: all 0.15s;
  display: flex; align-items: center; gap: 5px;
}
.sd-btn:hover:not(:disabled) { background: rgba(26,115,232,0.12); color: #e3f2fd; }
.sd-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.sd-btn-active { background: rgba(26,115,232,0.2) !important; border-color: #1a73e8 !important; color: #e3f2fd !important; }
.sd-btn-danger { color: #ef5350; }
.sd-btn-sm { padding: 3px 8px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: #90a4ae; font-size: 0.75rem; cursor: pointer; }
.sd-shape-prev { display: inline-block; width: 14px; height: 14px; border: 1.5px solid; }
.sd-shape-state { border-color: #42a5f5; border-radius: 4px; background: rgba(66,165,245,0.15); }
.sd-shape-initial { border-color: #66bb6a; border-radius: 50%; background: #66bb6a; }
.sd-shape-final { border-color: #ef5350; border-radius: 50%; background: rgba(239,83,80,0.3); }

.sd-canvas-wrap { border: 1px solid rgba(255,255,255,0.06); border-radius: 0 0 8px 8px; overflow: hidden; background: rgba(0,0,0,0.25); }
.sd-canvas { width: 100%; height: 500px; display: block; }

.sd-state-group { cursor: grab; }
.sd-state-group:active { cursor: grabbing; }
.sd-state-rect { fill: rgba(66,165,245,0.1); stroke: #42a5f5; stroke-width: 1.5; transition: stroke 0.15s; }
.sd-state-rect-sel { stroke: #1a73e8; stroke-width: 2.5; }
.sd-state-connect .sd-state-rect { stroke: #66bb6a; stroke-dasharray: 4 2; }
.sd-state-name { fill: #e0e0e0; font-size: 12px; font-weight: 600; pointer-events: none; }
.sd-special-label { font-size: 16px; }
.sd-state-sub { fill: #78909c; font-size: 10px; pointer-events: none; }
.sd-initial-dot { fill: #66bb6a; stroke: none; }
.sd-final-outer { fill: none; stroke: #ef5350; stroke-width: 2; }
.sd-final-inner { fill: #ef5350; stroke: none; }

.sd-trans-line { stroke: #546e7a; stroke-width: 1.5; fill: none; cursor: pointer; }
.sd-trans-line:hover { stroke: #90a4ae; }
.sd-trans-sel { stroke: #1a73e8; stroke-width: 2; }
.sd-trans-label { fill: #b0bec5; font-size: 10px; cursor: pointer; }
.sd-connect-preview { stroke: #1a73e8; stroke-width: 1.5; stroke-dasharray: 6 3; pointer-events: none; }

.sd-props { margin-top: 10px; padding: 12px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; }
.sd-props-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 0.85rem; font-weight: 600; color: #e3f2fd; }
.sd-prop-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.sd-prop-label { font-size: 0.8rem; color: #90a4ae; min-width: 80px; }
.sd-prop-input { flex: 1; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; padding: 5px 8px; color: #e0e0e0; font-size: 0.82rem; outline: none; }
.sd-prop-input:focus { border-color: #1a73e8; }

.sd-result { margin-top: 12px; padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); }
.sd-result-score { font-size: 0.9rem; font-weight: 600; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; }
.sd-result-great { background: rgba(34,197,94,0.12); color: #22c55e; }
.sd-result-ok { background: rgba(245,158,11,0.12); color: #f59e0b; }
.sd-result-bad { background: rgba(239,68,68,0.12); color: #ef4444; }
.sd-result-details { display: flex; flex-direction: column; gap: 4px; }
.sd-result-row { display: flex; justify-content: space-between; font-size: 0.82rem; color: #90a4ae; padding: 4px 8px; }
.sd-result-val { font-weight: 600; color: #e0e0e0; font-family: 'JetBrains Mono', monospace; }
</style>
