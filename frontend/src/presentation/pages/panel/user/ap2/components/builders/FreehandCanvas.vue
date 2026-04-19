<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  submitted?: boolean
  width?: number
  height?: number
  initialPaths?: Path[]
}

interface Path {
  d: string
  color: string
  width: number
}

const props = withDefaults(defineProps<Props>(), {
  submitted: false,
  width: 1000,
  height: 650,
  initialPaths: () => [],
})

const emit = defineEmits<{
  change: [paths: Path[]]
}>()

type Tool = 'pen' | 'eraser' | 'line' | 'rect' | 'arrow' | 'text'

const tool = ref<Tool>('pen')
const color = ref('#000000')
const strokeWidth = ref(2)

const paths = ref<Path[]>([...props.initialPaths])
const currentPath = ref<string>('')
const startPoint = ref<{ x: number; y: number } | null>(null)
const isDrawing = ref(false)

const texts = ref<Array<{ x: number; y: number; text: string }>>([])

const svgEl = ref<SVGSVGElement | null>(null)

const colors = ['#000000', '#dc2626', '#2563eb', '#16a34a', '#f59e0b', '#7c3aed']

function svgPoint(evt: PointerEvent): { x: number; y: number } {
  if (!svgEl.value) return { x: 0, y: 0 }
  const rect = svgEl.value.getBoundingClientRect()
  const scaleX = props.width / rect.width
  const scaleY = props.height / rect.height
  return {
    x: (evt.clientX - rect.left) * scaleX,
    y: (evt.clientY - rect.top) * scaleY,
  }
}

function onPointerDown(evt: PointerEvent) {
  if (props.submitted) return
  const p = svgPoint(evt)
  isDrawing.value = true
  startPoint.value = p
  if (tool.value === 'pen' || tool.value === 'eraser') {
    currentPath.value = `M ${p.x} ${p.y}`
  } else if (tool.value === 'text') {
    const text = window.prompt('Text:')
    if (text) {
      texts.value.push({ x: p.x, y: p.y, text })
      emitChange()
    }
    isDrawing.value = false
  }
}

function onPointerMove(evt: PointerEvent) {
  if (!isDrawing.value || props.submitted) return
  const p = svgPoint(evt)
  if (tool.value === 'pen' || tool.value === 'eraser') {
    currentPath.value += ` L ${p.x} ${p.y}`
  } else if (tool.value === 'line' && startPoint.value) {
    currentPath.value = `M ${startPoint.value.x} ${startPoint.value.y} L ${p.x} ${p.y}`
  } else if (tool.value === 'arrow' && startPoint.value) {
    currentPath.value = `M ${startPoint.value.x} ${startPoint.value.y} L ${p.x} ${p.y}`
  } else if (tool.value === 'rect' && startPoint.value) {
    const x0 = Math.min(startPoint.value.x, p.x)
    const y0 = Math.min(startPoint.value.y, p.y)
    const w = Math.abs(p.x - startPoint.value.x)
    const h = Math.abs(p.y - startPoint.value.y)
    currentPath.value = `M ${x0} ${y0} L ${x0 + w} ${y0} L ${x0 + w} ${y0 + h} L ${x0} ${y0 + h} Z`
  }
}

function onPointerUp() {
  if (!isDrawing.value) return
  isDrawing.value = false
  if (currentPath.value) {
    paths.value.push({
      d: currentPath.value,
      color: tool.value === 'eraser' ? '#ffffff' : color.value,
      width: tool.value === 'eraser' ? strokeWidth.value * 4 : strokeWidth.value,
    })
    emitChange()
  }
  currentPath.value = ''
  startPoint.value = null
}

function undo() {
  if (paths.value.length > 0) {
    paths.value.pop()
    emitChange()
  }
}

function clearCanvas() {
  if (!window.confirm('Wirklich alles löschen?')) return
  paths.value = []
  texts.value = []
  emitChange()
}

function emitChange() {
  emit('change', [...paths.value])
}

const viewBox = computed(() => `0 0 ${props.width} ${props.height}`)
</script>

<template>
  <div class="fh-canvas">
    <div class="fh-toolbar">
      <div class="fh-tool-group">
        <button
          v-for="t in (['pen','line','arrow','rect','text','eraser'] as Tool[])"
          :key="t"
          class="fh-btn"
          :class="{ 'fh-btn-active': tool === t }"
          :disabled="submitted"
          @click="tool = t"
        >
          <span v-if="t === 'pen'">✎ Stift</span>
          <span v-else-if="t === 'line'">— Linie</span>
          <span v-else-if="t === 'arrow'">→ Pfeil</span>
          <span v-else-if="t === 'rect'">▭ Rechteck</span>
          <span v-else-if="t === 'text'">T Text</span>
          <span v-else-if="t === 'eraser'">⌫ Radierer</span>
        </button>
      </div>

      <div class="fh-tool-group">
        <button
          v-for="c in colors"
          :key="c"
          class="fh-color"
          :class="{ 'fh-color-active': color === c }"
          :style="{ background: c }"
          :disabled="submitted"
          @click="color = c"
        />
      </div>

      <div class="fh-tool-group">
        <label class="fh-width">
          Dicke: {{ strokeWidth }}
          <input type="range" min="1" max="8" v-model.number="strokeWidth" :disabled="submitted" />
        </label>
      </div>

      <div class="fh-tool-group">
        <button class="fh-btn" :disabled="submitted || paths.length === 0" @click="undo">↶ Rückgängig</button>
        <button class="fh-btn fh-btn-danger" :disabled="submitted" @click="clearCanvas">🗑 Leeren</button>
      </div>
    </div>

    <div class="fh-canvas-wrap">
      <svg
        ref="svgEl"
        class="fh-svg"
        :viewBox="viewBox"
        :class="{ 'fh-submitted': submitted }"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerUp"
        @pointerleave="onPointerUp"
      >
        <defs>
          <pattern id="fh-grid" width="25" height="25" patternUnits="userSpaceOnUse">
            <path d="M 25 0 L 0 0 0 25" fill="none" stroke="#e5e7eb" stroke-width="0.5" />
          </pattern>
          <marker id="fh-arrow" markerWidth="10" markerHeight="8" refX="10" refY="4" orient="auto">
            <path d="M0,0 L10,4 L0,8 Z" fill="currentColor" />
          </marker>
        </defs>

        <rect :width="width" :height="height" fill="url(#fh-grid)" />

        <g>
          <path
            v-for="(p, i) in paths"
            :key="i"
            :d="p.d"
            :stroke="p.color"
            :stroke-width="p.width"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <path
            v-if="currentPath"
            :d="currentPath"
            :stroke="tool === 'eraser' ? '#ffffff' : color"
            :stroke-width="tool === 'eraser' ? strokeWidth * 4 : strokeWidth"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
            :marker-end="tool === 'arrow' ? 'url(#fh-arrow)' : undefined"
          />
          <text
            v-for="(t, i) in texts"
            :key="`t${i}`"
            :x="t.x"
            :y="t.y"
            :fill="color"
            font-size="16"
            font-family="system-ui, sans-serif"
          >
            {{ t.text }}
          </text>
        </g>
      </svg>
    </div>

    <p class="fh-hint">
      Freihand-Zeichnung als Backup für alle Diagramm-Typen. Stift für grobe Skizzen,
      Linie/Pfeil/Rechteck für geometrische Formen, Text für Beschriftungen.
    </p>
  </div>
</template>

<style scoped>
.fh-canvas {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}

.fh-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  padding: 0.5rem;
  background: #fff;
  border-radius: 6px;
}

.fh-tool-group {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.fh-btn {
  padding: 0.4rem 0.7rem;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.15s;
}

.fh-btn:hover:not(:disabled) {
  background: #f3f4f6;
}

.fh-btn-active {
  background: #3b82f6;
  color: #fff;
  border-color: #3b82f6;
}

.fh-btn-danger:hover:not(:disabled) {
  background: #fee2e2;
  border-color: #dc2626;
  color: #dc2626;
}

.fh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.fh-color {
  width: 24px;
  height: 24px;
  border: 2px solid #d1d5db;
  border-radius: 50%;
  cursor: pointer;
}

.fh-color-active {
  border-color: #1f2937;
  transform: scale(1.15);
}

.fh-width {
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.fh-width input { width: 80px; }

.fh-canvas-wrap {
  position: relative;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  overflow: hidden;
}

.fh-svg {
  width: 100%;
  height: auto;
  display: block;
  touch-action: none;
  cursor: crosshair;
}

.fh-submitted { cursor: not-allowed; }

.fh-hint {
  margin: 0;
  font-size: 0.8rem;
  color: #6b7280;
  font-style: italic;
}
</style>
