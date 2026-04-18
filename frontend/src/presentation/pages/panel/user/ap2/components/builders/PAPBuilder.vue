<script setup lang="ts">
import { ref, computed } from 'vue'

type NodeType = 'terminator' | 'process' | 'decision' | 'io' | 'connector'

interface PAPNode {
  id: string
  type: NodeType
  label: string
  x: number
  y: number
}

interface PAPEdge {
  id: string
  from: string
  to: string
  label?: string
}

interface Props {
  submitted?: boolean
  width?: number
  height?: number
  initialNodes?: PAPNode[]
  initialEdges?: PAPEdge[]
}

const props = withDefaults(defineProps<Props>(), {
  submitted: false,
  width: 900,
  height: 700,
  initialNodes: () => [],
  initialEdges: () => [],
})

const emit = defineEmits<{
  change: [payload: { nodes: PAPNode[]; edges: PAPEdge[] }]
}>()

const nodes = ref<PAPNode[]>([...props.initialNodes])
const edges = ref<PAPEdge[]>([...props.initialEdges])
const selectedNodeId = ref<string | null>(null)
const edgeStartId = ref<string | null>(null)

const svgEl = ref<SVGSVGElement | null>(null)
const draggingId = ref<string | null>(null)
const dragOffset = ref<{ x: number; y: number }>({ x: 0, y: 0 })

let idCounter = 1
function nextId(prefix: string) {
  return `${prefix}-${idCounter++}-${Date.now()}`
}

const NODE_SIZES: Record<NodeType, { w: number; h: number }> = {
  terminator: { w: 140, h: 50 },
  process:    { w: 150, h: 60 },
  decision:   { w: 170, h: 90 },
  io:         { w: 160, h: 60 },
  connector:  { w: 40, h: 40 },
}

const NODE_LABELS: Record<NodeType, string> = {
  terminator: 'Start / Ende',
  process: 'Operation',
  decision: 'Verzweigung',
  io: 'Ein-/Ausgabe',
  connector: 'Verbinder',
}

function addNode(type: NodeType) {
  if (props.submitted) return
  const label = type === 'terminator' ? 'Start' : window.prompt(`${NODE_LABELS[type]}-Text:`) || NODE_LABELS[type]
  const offset = nodes.value.length * 30
  nodes.value.push({
    id: nextId(type),
    type,
    label,
    x: 100 + (offset % 300),
    y: 80 + offset,
  })
  emitChange()
}

function deleteNode(id: string) {
  if (props.submitted) return
  nodes.value = nodes.value.filter(n => n.id !== id)
  edges.value = edges.value.filter(e => e.from !== id && e.to !== id)
  selectedNodeId.value = null
  emitChange()
}

function editLabel(id: string) {
  if (props.submitted) return
  const node = nodes.value.find(n => n.id === id)
  if (!node) return
  const next = window.prompt('Neue Beschriftung:', node.label)
  if (next !== null) {
    node.label = next
    emitChange()
  }
}

function startEdge(id: string) {
  if (props.submitted) return
  if (edgeStartId.value === id) {
    edgeStartId.value = null
    return
  }
  if (edgeStartId.value) {
    const from = edgeStartId.value
    const to = id
    if (from !== to) {
      const fromNode = nodes.value.find(n => n.id === from)
      const label = fromNode?.type === 'decision'
        ? window.prompt('Kantenbeschriftung (z.B. "ja" / "nein"):') || ''
        : ''
      edges.value.push({ id: nextId('edge'), from, to, label })
      emitChange()
    }
    edgeStartId.value = null
  } else {
    edgeStartId.value = id
  }
}

function svgPoint(evt: PointerEvent): { x: number; y: number } {
  if (!svgEl.value) return { x: 0, y: 0 }
  const rect = svgEl.value.getBoundingClientRect()
  return {
    x: (evt.clientX - rect.left) * (props.width / rect.width),
    y: (evt.clientY - rect.top) * (props.height / rect.height),
  }
}

function onNodeDown(evt: PointerEvent, id: string) {
  if (props.submitted) return
  evt.stopPropagation()
  selectedNodeId.value = id
  const node = nodes.value.find(n => n.id === id)
  if (!node) return
  const p = svgPoint(evt)
  draggingId.value = id
  dragOffset.value = { x: p.x - node.x, y: p.y - node.y }
}

function onSvgMove(evt: PointerEvent) {
  if (!draggingId.value) return
  const node = nodes.value.find(n => n.id === draggingId.value)
  if (!node) return
  const p = svgPoint(evt)
  node.x = Math.max(0, Math.min(props.width, p.x - dragOffset.value.x))
  node.y = Math.max(0, Math.min(props.height, p.y - dragOffset.value.y))
}

function onSvgUp() {
  if (draggingId.value) {
    draggingId.value = null
    emitChange()
  }
}

function clearAll() {
  if (props.submitted) return
  if (!window.confirm('Wirklich alles löschen?')) return
  nodes.value = []
  edges.value = []
  emitChange()
}

function emitChange() {
  emit('change', { nodes: [...nodes.value], edges: [...edges.value] })
}

const viewBox = computed(() => `0 0 ${props.width} ${props.height}`)

function nodeSize(type: NodeType) {
  return NODE_SIZES[type]
}

function edgePath(edge: PAPEdge): string {
  const from = nodes.value.find(n => n.id === edge.from)
  const to = nodes.value.find(n => n.id === edge.to)
  if (!from || !to) return ''
  const sz1 = nodeSize(from.type)
  const sz2 = nodeSize(to.type)
  const x1 = from.x + sz1.w / 2
  const y1 = from.y + sz1.h
  const x2 = to.x + sz2.w / 2
  const y2 = to.y
  const midY = (y1 + y2) / 2
  return `M ${x1} ${y1} L ${x1} ${midY} L ${x2} ${midY} L ${x2} ${y2}`
}

function edgeMidpoint(edge: PAPEdge) {
  const from = nodes.value.find(n => n.id === edge.from)
  const to = nodes.value.find(n => n.id === edge.to)
  if (!from || !to) return { x: 0, y: 0 }
  const sz1 = nodeSize(from.type)
  return { x: from.x + sz1.w / 2 + 8, y: (from.y + sz1.h + to.y) / 2 }
}
</script>

<template>
  <div class="pap-builder">
    <div class="pap-toolbar">
      <div class="pap-tool-group">
        <span class="pap-tool-label">DIN 66001:</span>
        <button class="pap-btn" :disabled="submitted" @click="addNode('terminator')">
          ⬭ Start/Ende
        </button>
        <button class="pap-btn" :disabled="submitted" @click="addNode('process')">
          ▭ Operation
        </button>
        <button class="pap-btn" :disabled="submitted" @click="addNode('decision')">
          ◇ Verzweigung
        </button>
        <button class="pap-btn" :disabled="submitted" @click="addNode('io')">
          ▱ E/A
        </button>
        <button class="pap-btn" :disabled="submitted" @click="addNode('connector')">
          ◯ Verbinder
        </button>
      </div>

      <div class="pap-tool-group">
        <button class="pap-btn pap-btn-danger" :disabled="submitted" @click="clearAll">
          🗑 Alles löschen
        </button>
      </div>
    </div>

    <p class="pap-hint">
      <strong>Bedienung:</strong> Form hinzufügen → ziehen. Klick auf Form: Beschriftung ändern. "Kante"-Button
      zweimal klicken (Start + Ziel), um Pfeil zu zeichnen. Bei ◇ Verzweigung wirst du nach „ja/nein"-Label gefragt.
    </p>

    <div class="pap-canvas-wrap">
      <svg
        ref="svgEl"
        class="pap-svg"
        :viewBox="viewBox"
        @pointermove="onSvgMove"
        @pointerup="onSvgUp"
        @pointerleave="onSvgUp"
      >
        <defs>
          <pattern id="pap-grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" stroke-width="0.5" />
          </pattern>
          <marker id="pap-arr" markerWidth="10" markerHeight="8" refX="10" refY="4" orient="auto">
            <path d="M0,0 L10,4 L0,8 Z" fill="#374151" />
          </marker>
        </defs>

        <rect :width="width" :height="height" fill="url(#pap-grid)" />

        <!-- Edges -->
        <g>
          <g v-for="edge in edges" :key="edge.id">
            <path
              :d="edgePath(edge)"
              stroke="#374151"
              stroke-width="2"
              fill="none"
              marker-end="url(#pap-arr)"
            />
            <text
              v-if="edge.label"
              :x="edgeMidpoint(edge).x"
              :y="edgeMidpoint(edge).y"
              font-size="13"
              fill="#1f2937"
              font-family="system-ui"
              font-weight="600"
            >
              {{ edge.label }}
            </text>
          </g>
        </g>

        <!-- Nodes -->
        <g
          v-for="node in nodes"
          :key="node.id"
          :class="{
            'pap-node-selected': selectedNodeId === node.id,
            'pap-node-edge-start': edgeStartId === node.id,
          }"
          @pointerdown="onNodeDown($event, node.id)"
        >
          <!-- Terminator: rounded rect -->
          <rect
            v-if="node.type === 'terminator'"
            :x="node.x" :y="node.y"
            :width="NODE_SIZES.terminator.w" :height="NODE_SIZES.terminator.h"
            :rx="NODE_SIZES.terminator.h / 2"
            fill="#fef3c7" stroke="#f59e0b" stroke-width="2"
          />
          <!-- Process: rect -->
          <rect
            v-else-if="node.type === 'process'"
            :x="node.x" :y="node.y"
            :width="NODE_SIZES.process.w" :height="NODE_SIZES.process.h"
            fill="#dbeafe" stroke="#2563eb" stroke-width="2"
          />
          <!-- Decision: rhombus -->
          <polygon
            v-else-if="node.type === 'decision'"
            :points="`${node.x + NODE_SIZES.decision.w / 2},${node.y}
                     ${node.x + NODE_SIZES.decision.w},${node.y + NODE_SIZES.decision.h / 2}
                     ${node.x + NODE_SIZES.decision.w / 2},${node.y + NODE_SIZES.decision.h}
                     ${node.x},${node.y + NODE_SIZES.decision.h / 2}`"
            fill="#fef9c3" stroke="#ca8a04" stroke-width="2"
          />
          <!-- I/O: parallelogram -->
          <polygon
            v-else-if="node.type === 'io'"
            :points="`${node.x + 15},${node.y}
                     ${node.x + NODE_SIZES.io.w},${node.y}
                     ${node.x + NODE_SIZES.io.w - 15},${node.y + NODE_SIZES.io.h}
                     ${node.x},${node.y + NODE_SIZES.io.h}`"
            fill="#ede9fe" stroke="#7c3aed" stroke-width="2"
          />
          <!-- Connector: circle -->
          <circle
            v-else-if="node.type === 'connector'"
            :cx="node.x + NODE_SIZES.connector.w / 2"
            :cy="node.y + NODE_SIZES.connector.h / 2"
            :r="NODE_SIZES.connector.w / 2"
            fill="#f3f4f6" stroke="#6b7280" stroke-width="2"
          />

          <text
            :x="node.x + NODE_SIZES[node.type].w / 2"
            :y="node.y + NODE_SIZES[node.type].h / 2 + 4"
            text-anchor="middle"
            font-size="13"
            font-family="system-ui, sans-serif"
            font-weight="500"
            fill="#111827"
            style="pointer-events: none;"
          >
            {{ node.label }}
          </text>
        </g>
      </svg>
    </div>

    <div v-if="selectedNodeId && !submitted" class="pap-actions">
      <button class="pap-btn" @click="editLabel(selectedNodeId)">✎ Beschriften</button>
      <button class="pap-btn" @click="startEdge(selectedNodeId)">
        {{ edgeStartId === selectedNodeId ? '✕ Kante abbrechen' : '→ Kante von hier' }}
      </button>
      <button class="pap-btn pap-btn-danger" @click="deleteNode(selectedNodeId)">🗑 Löschen</button>
    </div>
  </div>
</template>

<style scoped>
.pap-builder {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}

.pap-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: space-between;
  padding: 0.5rem;
  background: #fff;
  border-radius: 6px;
}

.pap-tool-group {
  display: flex;
  gap: 0.3rem;
  align-items: center;
  flex-wrap: wrap;
}

.pap-tool-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
  margin-right: 0.3rem;
}

.pap-btn {
  padding: 0.4rem 0.7rem;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
}

.pap-btn:hover:not(:disabled) {
  background: #f3f4f6;
}

.pap-btn-danger:hover:not(:disabled) {
  background: #fee2e2;
  border-color: #dc2626;
  color: #dc2626;
}

.pap-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pap-hint {
  margin: 0;
  font-size: 0.8rem;
  color: #6b7280;
  padding: 0.4rem 0.6rem;
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  border-radius: 3px;
}

.pap-canvas-wrap {
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  overflow: hidden;
}

.pap-svg {
  width: 100%;
  height: auto;
  display: block;
  touch-action: none;
}

.pap-node-selected rect,
.pap-node-selected polygon,
.pap-node-selected circle {
  stroke-width: 3 !important;
  filter: drop-shadow(0 0 4px rgba(59, 130, 246, 0.6));
}

.pap-node-edge-start rect,
.pap-node-edge-start polygon,
.pap-node-edge-start circle {
  stroke: #dc2626 !important;
  stroke-dasharray: 4, 2;
}

.pap-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #fff;
  border-radius: 6px;
}
</style>
