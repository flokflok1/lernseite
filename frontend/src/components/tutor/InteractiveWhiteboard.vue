<!--
  InteractiveWhiteboard - Animiertes Whiteboard für Tutor-Erklärungen

  Features:
  - Canvas-basiertes Zeichensystem
  - Animiertes Schreiben (Handschrift-Effekt)
  - Text mit verschiedenen Größen und Farben
  - Hervorhebungen und Unterstreichungen
  - Pfeile und Linien
  - Schrittweises Aufbauen
  - Löschfunktion

  Usage:
  <InteractiveWhiteboard
    ref="whiteboard"
    :width="800"
    :height="500"
    @action-complete="onActionComplete"
  />

  // In script:
  whiteboard.value.executeAction({ type: 'write', content: 'Hallo', position: {x: 50, y: 50}, duration: 1000 })
-->

<template>
  <div class="whiteboard-container" :class="{ 'transparent-mode': backgroundColor === 'transparent' }" :style="{ width: `${width}px`, height: `${height}px` }">
    <!-- Whiteboard Frame -->
    <div class="whiteboard-frame" :class="{ 'no-frame': backgroundColor === 'transparent' }">
      <!-- Whiteboard Header (hidden when no title or transparent) -->
      <div v-if="title && backgroundColor !== 'transparent'" class="whiteboard-header">
        <div class="header-dots">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
        </div>
        <span class="header-title">{{ title }}</span>
      </div>

      <!-- Canvas Area -->
      <div class="whiteboard-canvas-wrapper">
        <canvas
          ref="canvasRef"
          :width="canvasWidth"
          :height="canvasHeight"
          class="whiteboard-canvas"
          :class="{ 'transparent-canvas': backgroundColor === 'transparent' }"
        ></canvas>

        <!-- Cursor/Pen indicator (chalk style for transparent mode) -->
        <div
          v-if="isDrawing"
          class="pen-cursor"
          :class="{ 'chalk-cursor': backgroundColor === 'transparent' }"
          :style="{ left: `${cursorPosition.x}px`, top: `${cursorPosition.y}px` }"
        >
          {{ backgroundColor === 'transparent' ? '✎' : '✏️' }}
        </div>
      </div>

      <!-- Controls -->
      <div v-if="showControls" class="whiteboard-controls">
        <button @click="clearBoard" class="control-btn" title="Löschen">
          🗑️
        </button>
        <button @click="undoLast" class="control-btn" title="Rückgängig" :disabled="actionHistory.length === 0">
          ↩️
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'

// ============================================================================
// Types
// ============================================================================
export interface SchemaRow {
  name: string
  operator: string
  value: string
  highlight?: boolean
}

export interface WhiteboardAction {
  type: 'write' | 'draw' | 'highlight' | 'arrow' | 'underline' | 'box' | 'clear' | 'schema'
  content?: string
  position: { x: number, y: number }
  endPosition?: { x: number, y: number }
  duration: number
  color?: string
  fontSize?: number
  fontWeight?: 'normal' | 'bold'
  lineWidth?: number
  schema?: SchemaRow[]  // For schema type: array of rows to display
}

interface ActionHistoryEntry {
  action: WhiteboardAction
  imageData: ImageData
}

// ============================================================================
// Props & Emits
// ============================================================================
const props = withDefaults(defineProps<{
  width?: number
  height?: number
  title?: string
  showControls?: boolean
  backgroundColor?: string
  textColor?: string
}>(), {
  width: 800,
  height: 500,
  title: 'Whiteboard',
  showControls: true,
  backgroundColor: '#ffffff',
  textColor: '#1e293b'
})

const emit = defineEmits<{
  (e: 'action-complete', action: WhiteboardAction): void
  (e: 'action-start', action: WhiteboardAction): void
  (e: 'cleared'): void
}>()

// ============================================================================
// State
// ============================================================================
const canvasRef = ref<HTMLCanvasElement | null>(null)
const isDrawing = ref(false)
const cursorPosition = ref({ x: 0, y: 0 })
const actionHistory = ref<ActionHistoryEntry[]>([])
const currentActionQueue = ref<WhiteboardAction[]>([])
const isProcessingQueue = ref(false)

// ============================================================================
// Computed
// ============================================================================
const canvasWidth = computed(() => props.width - 40) // Account for padding
const canvasHeight = computed(() => props.height - 80) // Account for header and padding

// ============================================================================
// Canvas Context
// ============================================================================
function getContext(): CanvasRenderingContext2D | null {
  return canvasRef.value?.getContext('2d') ?? null
}

// ============================================================================
// Action Execution
// ============================================================================
async function executeAction(action: WhiteboardAction): Promise<void> {
  const ctx = getContext()
  if (!ctx) return

  emit('action-start', action)
  isDrawing.value = true

  // Save state before action
  const imageData = ctx.getImageData(0, 0, canvasWidth.value, canvasHeight.value)
  actionHistory.value.push({ action, imageData })

  switch (action.type) {
    case 'write':
      await animateText(ctx, action)
      break
    case 'draw':
      await animateLine(ctx, action)
      break
    case 'highlight':
      await animateHighlight(ctx, action)
      break
    case 'arrow':
      await animateArrow(ctx, action)
      break
    case 'underline':
      await animateUnderline(ctx, action)
      break
    case 'box':
      await animateBox(ctx, action)
      break
    case 'schema':
      await animateSchema(ctx, action)
      break
    case 'clear':
      await animateClear(ctx, action)
      break
  }

  isDrawing.value = false
  emit('action-complete', action)
}

// Queue multiple actions
async function executeActions(actions: WhiteboardAction[]): Promise<void> {
  for (const action of actions) {
    await executeAction(action)
  }
}

// ============================================================================
// Position Helpers - Convert percent (0-100) to pixel coordinates
// ============================================================================
function toPixelX(percentX: number): number {
  // If value is > 100, assume it's already in pixels (legacy support)
  if (percentX > 100) return percentX
  return (percentX / 100) * canvasWidth.value
}

function toPixelY(percentY: number): number {
  // If value is > 100, assume it's already in pixels (legacy support)
  if (percentY > 100) return percentY
  return (percentY / 100) * canvasHeight.value
}

function toPixelPos(pos: { x: number, y: number }): { x: number, y: number } {
  return { x: toPixelX(pos.x), y: toPixelY(pos.y) }
}

// ============================================================================
// Animation Functions
// ============================================================================
async function animateText(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
  if (!action.content) return

  const fontSize = action.fontSize || 24
  const fontWeight = action.fontWeight || 'normal'
  const color = action.color || props.textColor

  // Convert position from percent to pixels
  const pos = toPixelPos(action.position)

  ctx.font = `${fontWeight} ${fontSize}px 'Segoe UI', Arial, sans-serif`
  ctx.fillStyle = color
  ctx.textBaseline = 'top'

  const text = action.content
  const charDelay = action.duration / text.length
  let currentText = ''

  for (let i = 0; i < text.length; i++) {
    currentText += text[i]

    // Update cursor position
    const metrics = ctx.measureText(currentText)
    cursorPosition.value = {
      x: pos.x + metrics.width,
      y: pos.y
    }

    // Clear previous text and redraw
    const prevMetrics = ctx.measureText(currentText.slice(0, -1))
    ctx.fillText(text[i], pos.x + prevMetrics.width, pos.y)

    await delay(charDelay)
  }
}

async function animateLine(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
  if (!action.endPosition) return

  const color = action.color || props.textColor
  const lineWidth = action.lineWidth || 2

  ctx.strokeStyle = color
  ctx.lineWidth = lineWidth
  ctx.lineCap = 'round'

  // Convert positions from percent to pixels
  const startPos = toPixelPos(action.position)
  const endPos = toPixelPos(action.endPosition)

  const startX = startPos.x
  const startY = startPos.y
  const endX = endPos.x
  const endY = endPos.y

  const steps = 30
  const stepDelay = action.duration / steps

  for (let i = 0; i <= steps; i++) {
    const progress = i / steps
    const currentX = startX + (endX - startX) * progress
    const currentY = startY + (endY - startY) * progress

    cursorPosition.value = { x: currentX, y: currentY }

    if (i === 0) {
      ctx.beginPath()
      ctx.moveTo(startX, startY)
    }

    ctx.lineTo(currentX, currentY)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(currentX, currentY)

    await delay(stepDelay)
  }
}

async function animateHighlight(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
  if (!action.content) return

  const fontSize = action.fontSize || 24
  const color = action.color || '#fbbf24'

  // Convert position from percent to pixels
  const pos = toPixelPos(action.position)

  // Measure text to get highlight bounds
  ctx.font = `${fontSize}px 'Segoe UI', Arial, sans-serif`
  const metrics = ctx.measureText(action.content)

  const padding = 6
  const boxWidth = metrics.width + padding * 2
  const boxHeight = fontSize + padding * 2

  // Animate highlight background
  ctx.fillStyle = color + '40' // 25% opacity
  const steps = 10
  const stepDelay = action.duration / steps

  for (let i = 0; i <= steps; i++) {
    const progress = i / steps
    ctx.fillRect(
      pos.x - padding,
      pos.y - padding,
      boxWidth * progress,
      boxHeight
    )
    await delay(stepDelay)
  }

  // Draw text on top
  ctx.fillStyle = action.color || props.textColor
  ctx.fillText(action.content, pos.x, pos.y)
}

async function animateArrow(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
  if (!action.endPosition) return

  // Draw line first
  await animateLine(ctx, action)

  // Convert positions for arrowhead calculation
  const endPos = toPixelPos(action.endPosition)
  const startPos = toPixelPos(action.position)

  // Draw arrowhead
  const color = action.color || props.textColor
  const lineWidth = action.lineWidth || 2

  const angle = Math.atan2(
    endPos.y - startPos.y,
    endPos.x - startPos.x
  )

  const arrowLength = 15
  const arrowAngle = Math.PI / 6

  ctx.strokeStyle = color
  ctx.fillStyle = color
  ctx.lineWidth = lineWidth

  ctx.beginPath()
  ctx.moveTo(endPos.x, endPos.y)
  ctx.lineTo(
    endPos.x - arrowLength * Math.cos(angle - arrowAngle),
    endPos.y - arrowLength * Math.sin(angle - arrowAngle)
  )
  ctx.lineTo(
    endPos.x - arrowLength * Math.cos(angle + arrowAngle),
    endPos.y - arrowLength * Math.sin(angle + arrowAngle)
  )
  ctx.closePath()
  ctx.fill()
}

async function animateUnderline(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
  if (!action.content) return

  // Convert position to pixels first
  const pos = toPixelPos(action.position)

  const fontSize = action.fontSize || 24
  ctx.font = `${fontSize}px 'Segoe UI', Arial, sans-serif`
  const metrics = ctx.measureText(action.content)

  // Draw underline directly without calling animateLine (avoids double conversion)
  const color = action.color || props.textColor
  const lineWidth = action.lineWidth || 3
  const startX = pos.x
  const startY = pos.y + fontSize + 4
  const endX = pos.x + metrics.width
  const endY = startY

  ctx.strokeStyle = color
  ctx.lineWidth = lineWidth
  ctx.lineCap = 'round'

  const steps = 20
  const stepDelay = action.duration / steps

  for (let i = 0; i <= steps; i++) {
    const progress = i / steps
    const currentX = startX + (endX - startX) * progress

    cursorPosition.value = { x: currentX, y: startY }

    if (i === 0) {
      ctx.beginPath()
      ctx.moveTo(startX, startY)
    }

    ctx.lineTo(currentX, endY)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(currentX, endY)

    await delay(stepDelay)
  }
}

async function animateSchema(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
  if (!action.schema || action.schema.length === 0) return

  const startX = (action.position?.x || 10) * canvasWidth.value / 100
  const startY = (action.position?.y || 10) * canvasHeight.value / 100
  const fontSize = action.fontSize || 18
  const lineHeight = fontSize * 1.5
  const color = action.color || props.textColor
  const highlightColor = '#fbbf24'

  ctx.font = `${fontSize}px 'Segoe UI', Arial, sans-serif`
  ctx.textBaseline = 'top'

  const delayPerRow = action.duration / action.schema.length

  for (let i = 0; i < action.schema.length; i++) {
    const row = action.schema[i]
    const y = startY + i * lineHeight

    // Highlight background if marked
    if (row.highlight) {
      ctx.fillStyle = highlightColor + '40' // 25% opacity
      const nameWidth = ctx.measureText(row.name).width
      const opWidth = ctx.measureText(` ${row.operator} `).width
      const valueWidth = ctx.measureText(row.value).width
      const totalWidth = nameWidth + opWidth + valueWidth + 20
      ctx.fillRect(startX - 5, y - 3, totalWidth, lineHeight)
    }

    // Draw name
    ctx.fillStyle = row.highlight ? highlightColor : color
    ctx.fillText(row.name, startX, y)
    const nameWidth = ctx.measureText(row.name).width

    // Draw operator (centered)
    ctx.fillStyle = '#94a3b8' // Gray for operator
    ctx.fillText(` ${row.operator} `, startX + nameWidth, y)
    const opWidth = ctx.measureText(` ${row.operator} `).width

    // Draw value
    ctx.fillStyle = row.highlight ? highlightColor : color
    ctx.font = `bold ${fontSize}px 'Segoe UI', Arial, sans-serif`
    ctx.fillText(row.value, startX + nameWidth + opWidth, y)
    ctx.font = `${fontSize}px 'Segoe UI', Arial, sans-serif`

    // Update cursor position
    cursorPosition.value = {
      x: startX + nameWidth + opWidth + ctx.measureText(row.value).width,
      y: y
    }

    await delay(delayPerRow)
  }
}

async function animateBox(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
  if (!action.endPosition) return

  const color = action.color || props.textColor
  const lineWidth = action.lineWidth || 2

  ctx.strokeStyle = color
  ctx.lineWidth = lineWidth

  // Convert positions from percent to pixels
  const startPos = toPixelPos(action.position)
  const endPos = toPixelPos(action.endPosition)

  const x = startPos.x
  const y = startPos.y
  const w = endPos.x - x
  const h = endPos.y - y

  const steps = 40
  const stepDelay = action.duration / steps
  const perimeter = 2 * (w + h)

  ctx.beginPath()

  for (let i = 0; i <= steps; i++) {
    const progress = i / steps
    const distance = perimeter * progress

    let px, py

    if (distance <= w) {
      // Top edge
      px = x + distance
      py = y
    } else if (distance <= w + h) {
      // Right edge
      px = x + w
      py = y + (distance - w)
    } else if (distance <= 2 * w + h) {
      // Bottom edge
      px = x + w - (distance - w - h)
      py = y + h
    } else {
      // Left edge
      px = x
      py = y + h - (distance - 2 * w - h)
    }

    cursorPosition.value = { x: px, y: py }

    if (i === 0) {
      ctx.moveTo(px, py)
    } else {
      ctx.lineTo(px, py)
      ctx.stroke()
      ctx.beginPath()
      ctx.moveTo(px, py)
    }

    await delay(stepDelay)
  }

  // Close the box
  ctx.lineTo(x, y)
  ctx.stroke()
}

async function animateClear(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
  const steps = 20
  const stepDelay = action.duration / steps
  const isTransparent = props.backgroundColor === 'transparent'

  for (let i = 0; i <= steps; i++) {
    const progress = i / steps
    if (isTransparent) {
      // For transparent mode, just fade out existing content
      ctx.globalAlpha = 1 - progress
    } else {
      ctx.fillStyle = props.backgroundColor
      ctx.globalAlpha = progress
      ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
    }
    await delay(stepDelay)
  }

  ctx.globalAlpha = 1
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)

  // Only fill with color if not transparent
  if (!isTransparent) {
    ctx.fillStyle = props.backgroundColor
    ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  }

  actionHistory.value = []
  emit('cleared')
}

// ============================================================================
// Control Functions
// ============================================================================
function clearBoard() {
  const ctx = getContext()
  if (!ctx) return

  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)

  // Only fill with color if not transparent
  if (props.backgroundColor !== 'transparent') {
    ctx.fillStyle = props.backgroundColor
    ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  }

  actionHistory.value = []
  emit('cleared')
}

function undoLast() {
  if (actionHistory.value.length === 0) return

  const ctx = getContext()
  if (!ctx) return

  actionHistory.value.pop()

  if (actionHistory.value.length === 0) {
    clearBoard()
  } else {
    const lastEntry = actionHistory.value[actionHistory.value.length - 1]
    ctx.putImageData(lastEntry.imageData, 0, 0)
  }
}

// ============================================================================
// Utility
// ============================================================================
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// ============================================================================
// Lifecycle
// ============================================================================
onMounted(async () => {
  await nextTick()
  const ctx = getContext()
  if (ctx) {
    // Only fill if not transparent mode
    if (props.backgroundColor !== 'transparent') {
      ctx.fillStyle = props.backgroundColor
      ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
    }
  }
})

// ============================================================================
// Expose
// ============================================================================
defineExpose({
  executeAction,
  executeActions,
  clearBoard,
  undoLast,
  isDrawing
})
</script>

<style scoped>
.whiteboard-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.whiteboard-frame {
  background: linear-gradient(145deg, #374151 0%, #1f2937 100%);
  border-radius: 1rem;
  padding: 0.5rem;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.whiteboard-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-dots {
  display: flex;
  gap: 0.375rem;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.red { background: #ef4444; }
.dot.yellow { background: #fbbf24; }
.dot.green { background: #22c55e; }

.header-title {
  color: #94a3b8;
  font-size: 0.8125rem;
  font-weight: 500;
}

.whiteboard-canvas-wrapper {
  flex: 1;
  position: relative;
  margin: 0.5rem;
  border-radius: 0.5rem;
  overflow: hidden;
}

.whiteboard-canvas {
  background: #ffffff;
  border-radius: 0.5rem;
  width: 100%;
  height: 100%;
}

.whiteboard-canvas.transparent-canvas {
  background: transparent;
}

/* Transparent mode - no frame styling */
.whiteboard-frame.no-frame {
  background: transparent;
  box-shadow: none;
  padding: 0;
}

.whiteboard-frame.no-frame .whiteboard-canvas-wrapper {
  margin: 0;
}

.pen-cursor.chalk-cursor {
  color: #f5f5dc;
  text-shadow: 0 0 5px rgba(245, 245, 220, 0.5);
}

.pen-cursor {
  position: absolute;
  font-size: 1.25rem;
  pointer-events: none;
  transform: translate(-50%, -100%) rotate(-30deg);
  transition: left 0.05s linear, top 0.05s linear;
  filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.3));
}

.whiteboard-controls {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 0.375rem 0.5rem;
}

.control-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 0.375rem;
  padding: 0.375rem 0.625rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Dark mode whiteboard (inverse - light board) */
:root.dark .whiteboard-canvas {
  background: #f8fafc;
}
</style>
