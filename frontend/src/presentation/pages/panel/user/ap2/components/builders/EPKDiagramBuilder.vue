<template>
  <div class="epk-builder">
    <!-- Toolbar -->
    <div class="epk-toolbar">
      <div class="epk-toolbar-group">
        <button class="epk-btn" @click="addNode('event')" :disabled="submitted">
          <span class="epk-shape-prev epk-shape-hex"></span> Ereignis
        </button>
        <button class="epk-btn" @click="addNode('function')" :disabled="submitted">
          <span class="epk-shape-prev epk-shape-rect"></span> Funktion
        </button>
        <button class="epk-btn" @click="addNode('xor')" :disabled="submitted">
          <span class="epk-shape-prev epk-shape-circle">&#10005;</span> XOR
        </button>
        <button class="epk-btn" @click="addNode('and')" :disabled="submitted">
          <span class="epk-shape-prev epk-shape-circle">&#8743;</span> AND
        </button>
        <button class="epk-btn" @click="addNode('or')" :disabled="submitted">
          <span class="epk-shape-prev epk-shape-circle">&#8744;</span> OR
        </button>
      </div>
      <div class="epk-toolbar-group">
        <button
          class="epk-btn"
          @click="toggleConnect"
          :disabled="submitted || nodes.length < 2"
          :class="{ 'epk-btn-active': isConnecting }"
        >
          &#8595; Verbinden
        </button>
        <button class="epk-btn epk-btn-danger" @click="clearAll" :disabled="submitted">
          &#128465; Leeren
        </button>
      </div>
    </div>

    <!-- SVG Canvas -->
    <div class="epk-canvas-wrap">
      <svg
        class="epk-canvas"
        :viewBox="`0 0 ${canvasW} ${canvasH}`"
        ref="svgEl"
        @mousemove="onMove"
        @mouseup="onUp"
        @mousedown.self="deselect"
      >
        <defs>
          <pattern id="epk-grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.025)" stroke-width="0.5" />
          </pattern>
          <marker id="epk-arrow" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <path d="M0,0 L8,3 L0,6 Z" fill="#546e7a" />
          </marker>
          <marker id="epk-arrow-sel" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <path d="M0,0 L8,3 L0,6 Z" fill="#1a73e8" />
          </marker>
        </defs>
        <rect width="100%" height="100%" fill="url(#epk-grid)" />

        <!-- Kanten -->
        <g v-for="edge in edges" :key="edge.id">
          <line
            :x1="nodeCenter(edge.from).x"
            :y1="nodeCenter(edge.from).y"
            :x2="nodeCenter(edge.to).x"
            :y2="nodeCenter(edge.to).y"
            class="epk-edge"
            :class="{ 'epk-edge-sel': selectedEdgeId === edge.id }"
            :marker-end="selectedEdgeId === edge.id ? 'url(#epk-arrow-sel)' : 'url(#epk-arrow)'"
            @click.stop="selectEdge(edge.id)"
          />
        </g>

        <!-- Verbindungs-Preview -->
        <line
          v-if="isConnecting && connectFrom && mouse"
          :x1="nodeCenter(connectFrom).x"
          :y1="nodeCenter(connectFrom).y"
          :x2="mouse.x"
          :y2="mouse.y"
          class="epk-connect-preview"
        />

        <!-- Nodes -->
        <g
          v-for="node in nodes"
          :key="node.id"
          :transform="`translate(${node._x}, ${node._y})`"
          class="epk-node-group"
          :class="{
            'epk-node-selected': selectedNodeId === node.id,
            'epk-node-connect-target': isConnecting && connectFrom && connectFrom !== node.id
          }"
          @mousedown.stop="onNodeDown(node, $event)"
          @click.stop="onNodeClick(node)"
        >
          <!-- Ereignis: Hexagon -->
          <polygon
            v-if="node.type === 'event'"
            :points="hexPoints(140, 44)"
            class="epk-shape epk-event"
            :class="{ 'epk-shape-sel': selectedNodeId === node.id }"
          />
          <!-- Funktion: Abgerundetes Rechteck -->
          <rect
            v-else-if="node.type === 'function'"
            x="0" y="0" width="140" height="44" rx="6"
            class="epk-shape epk-function"
            :class="{ 'epk-shape-sel': selectedNodeId === node.id }"
          />
          <!-- Konnektoren: Kreis -->
          <circle
            v-else
            cx="70" cy="22" r="20"
            class="epk-shape epk-connector"
            :class="{
              'epk-shape-sel': selectedNodeId === node.id,
              'epk-connector-xor': node.type === 'xor',
              'epk-connector-and': node.type === 'and',
              'epk-connector-or': node.type === 'or',
            }"
          />
          <!-- Label -->
          <text
            x="70" :y="node.type === 'xor' || node.type === 'and' || node.type === 'or' ? 27 : 27"
            text-anchor="middle"
            class="epk-label"
            :class="{ 'epk-label-connector': isConnectorType(node.type) }"
          >
            {{ isConnectorType(node.type) ? getConnectorSymbol(node.type) : truncate(node.label, 18) }}
          </text>
        </g>
      </svg>
    </div>

    <!-- Eigenschafts-Panel -->
    <div v-if="selectedNodeId && !submitted" class="epk-props">
      <div class="epk-props-header">
        <span>{{ getNodeTypeLabel(selectedNode?.type || 'event') }} bearbeiten</span>
        <button class="epk-btn-sm epk-btn-danger" @click="deleteNode(selectedNodeId)">Löschen</button>
      </div>
      <div v-if="!isConnectorType(selectedNode?.type || '')" class="epk-prop-row">
        <label class="epk-prop-label">Bezeichnung:</label>
        <input
          :value="selectedNode?.label"
          @input="updateNodeLabel(($event.target as HTMLInputElement).value)"
          class="epk-prop-input"
          :placeholder="selectedNode?.type === 'event' ? 'z.B. Bestellung eingegangen' : 'z.B. Bestellung prüfen'"
        />
      </div>
    </div>

    <!-- Edge Panel -->
    <div v-if="selectedEdgeId && !submitted" class="epk-props">
      <div class="epk-props-header">
        <span>Kante</span>
        <button class="epk-btn-sm epk-btn-danger" @click="deleteEdge(selectedEdgeId)">Löschen</button>
      </div>
      <div class="epk-prop-info">
        {{ getNodeLabel(selectedEdge?.from || '') }} &#8594; {{ getNodeLabel(selectedEdge?.to || '') }}
      </div>
    </div>

    <!-- Ergebnis -->
    <div v-if="submitted && result" class="epk-result">
      <div class="epk-result-score" :class="resultClass">
        {{ result.pct }}% — {{ result.feedback }}
      </div>
      <div v-if="result.details" class="epk-result-details">
        <div v-if="result.details.nodeScore !== undefined" class="epk-result-row">
          <span>Knoten:</span> <span class="epk-result-val">{{ result.details.nodeScore }}%</span>
        </div>
        <div v-if="result.details.edgeScore !== undefined" class="epk-result-row">
          <span>Verbindungen:</span> <span class="epk-result-val">{{ result.details.edgeScore }}%</span>
        </div>
        <div v-if="result.details.structureScore !== undefined" class="epk-result-row">
          <span>Struktur:</span> <span class="epk-result-val">{{ result.details.structureScore }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { EPKNode, EPKEdge, EPKDiagramData, EPKNodeType, DiagramGradingResult } from '../../types'

interface PositionedNode extends EPKNode {
  _x: number
  _y: number
}

const props = defineProps<{
  template?: EPKDiagramData
  solution?: EPKDiagramData
  submitted: boolean
  instructions?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', data: EPKDiagramData): void
  (e: 'graded', result: DiagramGradingResult): void
}>()

const canvasW = 900
const canvasH = 700

const nodes = ref<PositionedNode[]>([])
const edges = ref<EPKEdge[]>([])
const selectedNodeId = ref<string | null>(null)
const selectedEdgeId = ref<string | null>(null)
const isConnecting = ref(false)
const connectFrom = ref<string | null>(null)
const mouse = ref<{ x: number; y: number } | null>(null)
const dragNode = ref<string | null>(null)
const dragOffX = ref(0)
const dragOffY = ref(0)
const svgEl = ref<SVGSVGElement | null>(null)
const result = ref<DiagramGradingResult | null>(null)
let nextId = 1

const selectedNode = computed(() => nodes.value.find(n => n.id === selectedNodeId.value))
const selectedEdge = computed(() => edges.value.find(e => e.id === selectedEdgeId.value))
const resultClass = computed(() => {
  if (!result.value) return ''
  if (result.value.pct >= 80) return 'epk-result-great'
  if (result.value.pct >= 50) return 'epk-result-ok'
  return 'epk-result-bad'
})

function hexPoints(w: number, h: number): string {
  const cx = w / 2, cy = h / 2
  const dx = w / 2, dy = h / 2
  const notch = w * 0.15
  return `${notch},${cy} ${0},${0} ${w},${0} ${w - notch},${cy} ${w},${h} ${0},${h}`
}

function isConnectorType(type: string): boolean {
  return type === 'xor' || type === 'and' || type === 'or'
}

function getConnectorSymbol(type: string): string {
  if (type === 'xor') return '×'
  if (type === 'and') return '∧'
  if (type === 'or') return '∨'
  return '?'
}

function getNodeTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    event: 'Ereignis', function: 'Funktion', xor: 'XOR-Konnektor', and: 'AND-Konnektor', or: 'OR-Konnektor'
  }
  return labels[type] || type
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max - 1) + '…' : s
}

function nodeCenter(id: string): { x: number; y: number } {
  const n = nodes.value.find(nd => nd.id === id)
  if (!n) return { x: 0, y: 0 }
  if (isConnectorType(n.type)) return { x: n._x + 70, y: n._y + 22 }
  return { x: n._x + 70, y: n._y + 22 }
}

function getNodeLabel(id: string): string {
  const n = nodes.value.find(nd => nd.id === id)
  if (!n) return '?'
  return isConnectorType(n.type) ? getConnectorSymbol(n.type) : n.label
}

function svgPoint(e: MouseEvent): { x: number; y: number } {
  if (!svgEl.value) return { x: 0, y: 0 }
  const pt = svgEl.value.createSVGPoint()
  pt.x = e.clientX; pt.y = e.clientY
  const ctm = svgEl.value.getScreenCTM()?.inverse()
  if (ctm) { const t = pt.matrixTransform(ctm); return { x: t.x, y: t.y } }
  return { x: 0, y: 0 }
}

// ─── Actions ───
function addNode(type: EPKNodeType) {
  const id = `n${nextId++}`
  const col = nodes.value.length % 3
  const row = Math.floor(nodes.value.length / 3)
  const defaultLabel = type === 'event' ? 'Neues Ereignis' : type === 'function' ? 'Neue Funktion' : type.toUpperCase()
  nodes.value.push({ id, type, label: defaultLabel, _x: 80 + col * 200, _y: 60 + row * 100 })
  selectedNodeId.value = id
  selectedEdgeId.value = null
  emitUpdate()
}

function deleteNode(id: string) {
  nodes.value = nodes.value.filter(n => n.id !== id)
  edges.value = edges.value.filter(e => e.from !== id && e.to !== id)
  selectedNodeId.value = null
  emitUpdate()
}

function updateNodeLabel(label: string) {
  const n = nodes.value.find(nd => nd.id === selectedNodeId.value)
  if (n) { n.label = label; emitUpdate() }
}

function toggleConnect() {
  isConnecting.value = !isConnecting.value
  connectFrom.value = null
  mouse.value = null
}

function selectEdge(id: string) {
  if (isConnecting.value) return
  selectedEdgeId.value = id
  selectedNodeId.value = null
}

function deleteEdge(id: string) {
  edges.value = edges.value.filter(e => e.id !== id)
  selectedEdgeId.value = null
  emitUpdate()
}

function clearAll() {
  nodes.value = []; edges.value = []
  selectedNodeId.value = null; selectedEdgeId.value = null
  nextId = 1; emitUpdate()
}

function deselect() {
  if (!isConnecting.value) {
    selectedNodeId.value = null
    selectedEdgeId.value = null
  }
}

// ─── Node Interaction ───
function onNodeClick(node: PositionedNode) {
  if (isConnecting.value) {
    if (!connectFrom.value) {
      connectFrom.value = node.id
    } else if (connectFrom.value !== node.id) {
      const id = `e${nextId++}`
      edges.value.push({ id, from: connectFrom.value, to: node.id })
      connectFrom.value = null
      mouse.value = null
      isConnecting.value = false
      selectedEdgeId.value = id
      emitUpdate()
    }
    return
  }
  selectedNodeId.value = node.id
  selectedEdgeId.value = null
}

function onNodeDown(node: PositionedNode, e: MouseEvent) {
  if (props.submitted || isConnecting.value) return
  dragNode.value = node.id
  const pt = svgPoint(e)
  dragOffX.value = pt.x - node._x
  dragOffY.value = pt.y - node._y
}

function onMove(e: MouseEvent) {
  const pt = svgPoint(e)
  if (isConnecting.value && connectFrom.value) mouse.value = pt
  if (dragNode.value) {
    const n = nodes.value.find(nd => nd.id === dragNode.value)
    if (n) {
      n._x = Math.max(0, Math.min(canvasW - 140, pt.x - dragOffX.value))
      n._y = Math.max(0, Math.min(canvasH - 50, pt.y - dragOffY.value))
    }
  }
}

function onUp() { dragNode.value = null }

function emitUpdate() {
  emit('update:modelValue', {
    nodes: nodes.value.map(n => ({ id: n.id, type: n.type, label: n.label })),
    edges: edges.value.map(e => ({ ...e })),
  })
}

// ─── Grading ───
function gradeEPK(): DiagramGradingResult {
  if (!props.solution) return { pct: 0, feedback: 'Keine Musterlösung', details: {} }
  const sol = props.solution as EPKDiagramData

  // Knoten-Score: Typ + Label Matching
  let matchedNodes = 0
  for (const sn of sol.nodes) {
    const match = nodes.value.find(n =>
      n.type === sn.type && n.label.toLowerCase().includes(sn.label.toLowerCase().slice(0, 5))
    )
    if (match) matchedNodes++
  }
  const nodeScore = sol.nodes.length > 0 ? Math.round((matchedNodes / sol.nodes.length) * 100) : 100

  // Kanten-Score: From/To Typ-Paar
  let matchedEdges = 0
  for (const se of sol.edges) {
    const sf = sol.nodes.find(n => n.id === se.from)
    const st = sol.nodes.find(n => n.id === se.to)
    if (!sf || !st) continue
    const found = edges.value.some(ue => {
      const uf = nodes.value.find(n => n.id === ue.from)
      const ut = nodes.value.find(n => n.id === ue.to)
      if (!uf || !ut) return false
      return uf.type === sf.type && ut.type === st.type &&
        uf.label.toLowerCase().includes(sf.label.toLowerCase().slice(0, 5)) &&
        ut.label.toLowerCase().includes(st.label.toLowerCase().slice(0, 5))
    })
    if (found) matchedEdges++
  }
  const edgeScore = sol.edges.length > 0 ? Math.round((matchedEdges / sol.edges.length) * 100) : 100

  // Struktur: Ereignis→Funktion→Ereignis Abfolge prüfen
  let structureScore = 100
  for (const edge of edges.value) {
    const from = nodes.value.find(n => n.id === edge.from)
    const to = nodes.value.find(n => n.id === edge.to)
    if (!from || !to) continue
    // Regel: Zwei gleiche Nicht-Konnektor-Typen dürfen nicht direkt verbunden sein
    if (from.type === to.type && !isConnectorType(from.type)) {
      structureScore -= 10
    }
  }
  structureScore = Math.max(0, structureScore)

  const pct = Math.round(nodeScore * 0.35 + edgeScore * 0.4 + structureScore * 0.25)
  let feedback = ''
  if (pct >= 90) feedback = 'Hervorragend! Die EPK ist korrekt aufgebaut.'
  else if (pct >= 70) feedback = 'Gut, aber einige Elemente oder Verbindungen fehlen.'
  else if (pct >= 50) feedback = 'Grundstruktur erkennbar, aber deutliche Lücken.'
  else feedback = 'Die EPK muss noch deutlich überarbeitet werden.'

  return { pct, feedback, details: { nodeScore, edgeScore, structureScore } }
}

// ─── Lifecycle ───
onMounted(() => {
  if (props.template) {
    nodes.value = props.template.nodes.map((n, i) => ({
      ...n, _x: 80 + (i % 2) * 280, _y: 50 + Math.floor(i / 2) * 100,
    }))
    edges.value = props.template.edges.map(e => ({ ...e }))
    nextId = props.template.nodes.length + props.template.edges.length + 1
  }
})

watch(() => props.submitted, (s) => {
  if (s) { const r = gradeEPK(); result.value = r; emit('graded', r) }
})
</script>

<style scoped>
.epk-builder { width: 100%; margin: 12px 0; }

.epk-toolbar {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  background: rgba(0,0,0,0.2); border-radius: 8px 8px 0 0;
  border: 1px solid rgba(255,255,255,0.06); border-bottom: none; flex-wrap: wrap;
}
.epk-toolbar-group { display: flex; gap: 6px; }
.epk-btn {
  padding: 5px 10px; background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 5px;
  color: #b0bec5; font-size: 0.8rem; cursor: pointer;
  transition: all 0.15s; display: flex; align-items: center; gap: 5px;
}
.epk-btn:hover:not(:disabled) { background: rgba(26,115,232,0.12); color: #e3f2fd; }
.epk-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.epk-btn-active { background: rgba(26,115,232,0.2) !important; border-color: #1a73e8 !important; color: #e3f2fd !important; }
.epk-btn-danger { color: #ef5350; }
.epk-btn-sm {
  padding: 3px 8px; background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 4px;
  color: #90a4ae; font-size: 0.75rem; cursor: pointer;
}

/* Mini Shape Previews */
.epk-shape-prev {
  display: inline-block; width: 14px; height: 10px; border: 1px solid #78909c;
}
.epk-shape-hex { clip-path: polygon(15% 50%, 0 0, 100% 0, 85% 50%, 100% 100%, 0 100%); background: rgba(255,152,0,0.3); }
.epk-shape-rect { border-radius: 2px; background: rgba(76,175,80,0.3); }
.epk-shape-circle { border-radius: 50%; width: 14px; height: 14px; background: rgba(156,39,176,0.3); font-size: 8px; display: inline-flex; align-items: center; justify-content: center; color: #ce93d8; }

.epk-canvas-wrap {
  border: 1px solid rgba(255,255,255,0.06); border-radius: 0 0 8px 8px;
  overflow: hidden; background: rgba(0,0,0,0.25);
}
.epk-canvas { width: 100%; height: 550px; display: block; }

/* Shapes */
.epk-shape { transition: stroke 0.15s; }
.epk-event { fill: rgba(255,152,0,0.12); stroke: #ff9800; stroke-width: 1.5; }
.epk-function { fill: rgba(76,175,80,0.12); stroke: #4caf50; stroke-width: 1.5; }
.epk-connector { stroke-width: 1.5; }
.epk-connector-xor { fill: rgba(156,39,176,0.12); stroke: #9c27b0; }
.epk-connector-and { fill: rgba(33,150,243,0.12); stroke: #2196f3; }
.epk-connector-or { fill: rgba(0,150,136,0.12); stroke: #009688; }
.epk-shape-sel { stroke-width: 2.5 !important; filter: drop-shadow(0 0 4px rgba(26,115,232,0.4)); }
.epk-node-group { cursor: grab; }
.epk-node-group:active { cursor: grabbing; }
.epk-node-connect-target .epk-shape { stroke: #66bb6a !important; stroke-dasharray: 4 2; }
.epk-label { fill: #e0e0e0; font-size: 11px; font-weight: 500; pointer-events: none; }
.epk-label-connector { font-size: 14px; font-weight: 700; }

.epk-edge { stroke: #546e7a; stroke-width: 1.5; cursor: pointer; }
.epk-edge:hover { stroke: #90a4ae; }
.epk-edge-sel { stroke: #1a73e8; stroke-width: 2; }
.epk-connect-preview { stroke: #1a73e8; stroke-width: 1.5; stroke-dasharray: 6 3; pointer-events: none; }

/* Props Panel */
.epk-props {
  margin-top: 10px; padding: 12px; background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;
}
.epk-props-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 10px; font-size: 0.85rem; font-weight: 600; color: #e3f2fd;
}
.epk-prop-row { display: flex; align-items: center; gap: 8px; }
.epk-prop-label { font-size: 0.8rem; color: #90a4ae; min-width: 90px; }
.epk-prop-input {
  flex: 1; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 4px; padding: 5px 8px; color: #e0e0e0; font-size: 0.82rem; outline: none;
}
.epk-prop-input:focus { border-color: #1a73e8; }
.epk-prop-info { font-size: 0.78rem; color: #78909c; margin-top: 4px; }

/* Result */
.epk-result { margin-top: 12px; padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); }
.epk-result-score { font-size: 0.9rem; font-weight: 600; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; }
.epk-result-great { background: rgba(34,197,94,0.12); color: #22c55e; }
.epk-result-ok { background: rgba(245,158,11,0.12); color: #f59e0b; }
.epk-result-bad { background: rgba(239,68,68,0.12); color: #ef4444; }
.epk-result-details { display: flex; flex-direction: column; gap: 4px; }
.epk-result-row { display: flex; justify-content: space-between; font-size: 0.82rem; color: #90a4ae; padding: 4px 8px; }
.epk-result-val { font-weight: 600; color: #e0e0e0; font-family: 'JetBrains Mono', monospace; }
</style>
