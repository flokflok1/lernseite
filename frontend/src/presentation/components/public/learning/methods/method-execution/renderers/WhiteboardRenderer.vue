<template>
  <div class="renderer">
    <p v-if="taskText" class="task-text">{{ taskText }}</p>

    <!-- Drawing Canvas Area -->
    <div class="canvas-area">
      <div class="canvas-toolbar">
        <button v-for="tool in tools" :key="tool.id" class="tool-btn" :class="{ 'tool-btn--active': activeTool === tool.id }" @click="activeTool = tool.id">
          {{ tool.icon }}
        </button>
        <div class="toolbar-spacer" />
        <button class="tool-btn tool-btn--clear" @click="clearCanvas">{{ t('lesson.methodExecution.renderer.whiteboard.clear') }}</button>
      </div>
      <canvas ref="canvasRef" class="drawing-canvas" @mousedown="startDraw" @mousemove="draw" @mouseup="stopDraw" @mouseleave="stopDraw" />
      <p class="canvas-hint">{{ t('lesson.methodExecution.renderer.whiteboard.drawHint') }}</p>
    </div>

    <!-- Requirements Checklist -->
    <div v-if="requirements.length" class="requirements">
      <h4 class="section-label">{{ t('lesson.methodExecution.renderer.whiteboard.requirements') }}</h4>
      <ul class="req-list">
        <li v-for="(r, i) in requirements" :key="i" class="req-item">
          <input v-model="checked[i]" type="checkbox" class="req-check" />
          <span :class="{ 'req-done': checked[i] }">{{ r }}</span>
        </li>
      </ul>
    </div>

    <!-- Explanation Input -->
    <div v-if="showExplanation" class="explanation-section">
      <h4 class="section-label">{{ t('lesson.methodExecution.renderer.whiteboard.explain') }}</h4>
      <textarea v-model="explanation" class="explanation-input" rows="4" :placeholder="t('lesson.methodExecution.renderer.whiteboard.explainPlaceholder')" />
    </div>

    <!-- Solution -->
    <button v-if="solution" class="solution-btn" @click="showSolution = !showSolution">
      {{ showSolution ? t('lesson.methodExecution.renderer.common.hideSolution') : t('lesson.methodExecution.renderer.common.showSolution') }}
    </button>
    <Transition name="fade">
      <div v-if="showSolution && solution" class="solution-box">
        <h4 class="sol-label">{{ t('lesson.methodExecution.renderer.common.sampleSolution') }}</h4>
        <p v-if="solution.description" class="sol-text">{{ solution.description }}</p>
        <pre v-if="solution.diagram" class="sol-diagram">{{ solution.diagram }}</pre>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import type { WhiteboardData, WhiteboardSolution } from './types'

const { t } = useI18n()
const props = defineProps<{ data: WhiteboardData | null; solution: WhiteboardSolution | null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const canvasRef = ref<HTMLCanvasElement | null>(null)
const isDrawing = ref(false)
const activeTool = ref('pen')
const explanation = ref('')
const showSolution = ref(false)
const checked = ref<boolean[]>([])

// Shape drawing state
let startX = 0
let startY = 0
let canvasSnapshot: ImageData | null = null

const taskText = computed(() => props.data?.task || props.data?.description || '')
const requirements = computed(() => props.data?.requirements || [])
const showExplanation = computed(() => props.data?.requireExplanation !== false)

// Sync checked array when requirements change
watch(requirements, (r) => {
  checked.value = r.map(() => false)
}, { immediate: true })

watch(() => props.data, () => {
  showSolution.value = false
  explanation.value = ''
  clearCanvas()
}, { deep: true })

const tools = [
  { id: 'pen', icon: '✏️' },
  { id: 'line', icon: '📏' },
  { id: 'rect', icon: '⬜' },
  { id: 'eraser', icon: '🧹' },
]

onMounted(async () => {
  await nextTick()
  const canvas = canvasRef.value
  if (!canvas) return
  canvas.width = canvas.offsetWidth
  canvas.height = 300
  const ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.fillStyle = '#0f172a'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }
})

function getPos(e: MouseEvent) {
  const rect = canvasRef.value!.getBoundingClientRect()
  return { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

function startDraw(e: MouseEvent) {
  isDrawing.value = true
  const ctx = canvasRef.value?.getContext('2d')
  if (!ctx) return
  const pos = getPos(e)
  startX = pos.x
  startY = pos.y

  if (activeTool.value === 'pen' || activeTool.value === 'eraser') {
    ctx.beginPath()
    ctx.moveTo(pos.x, pos.y)
  } else {
    // Save canvas state for shape preview
    canvasSnapshot = ctx.getImageData(0, 0, canvasRef.value!.width, canvasRef.value!.height)
  }
}

function draw(e: MouseEvent) {
  if (!isDrawing.value) return
  const ctx = canvasRef.value?.getContext('2d')
  if (!ctx) return
  const pos = getPos(e)

  if (activeTool.value === 'pen' || activeTool.value === 'eraser') {
    ctx.strokeStyle = activeTool.value === 'eraser' ? '#0f172a' : '#a5b4fc'
    ctx.lineWidth = activeTool.value === 'eraser' ? 20 : 2
    ctx.lineCap = 'round'
    ctx.lineTo(pos.x, pos.y)
    ctx.stroke()
  } else {
    // Restore snapshot then draw preview shape
    if (canvasSnapshot) ctx.putImageData(canvasSnapshot, 0, 0)
    ctx.strokeStyle = '#a5b4fc'
    ctx.lineWidth = 2
    ctx.lineCap = 'round'

    if (activeTool.value === 'line') {
      ctx.beginPath()
      ctx.moveTo(startX, startY)
      ctx.lineTo(pos.x, pos.y)
      ctx.stroke()
    } else if (activeTool.value === 'rect') {
      ctx.strokeRect(startX, startY, pos.x - startX, pos.y - startY)
    }
  }
}

function stopDraw() {
  isDrawing.value = false
  canvasSnapshot = null
}

function clearCanvas() {
  const ctx = canvasRef.value?.getContext('2d')
  if (!ctx || !canvasRef.value) return
  ctx.fillStyle = '#0f172a'
  ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
}

// Emit completion when all requirements are checked
const completedReqs = computed(() => checked.value.filter(Boolean).length)
watch(completedReqs, (count) => {
  if (count === requirements.value.length && count > 0) {
    emit('complete', count, requirements.value.length)
  }
})
</script>

<style scoped>
.task-text { font-size: 0.9375rem; line-height: 1.75; margin-bottom: 1.25rem; color: var(--color-text-primary); }

.canvas-area { margin-bottom: 1.25rem; }

.canvas-toolbar {
  display: flex; align-items: center; gap: 0.375rem;
  padding: 0.5rem 0.75rem; background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-bottom: none; border-radius: 0.625rem 0.625rem 0 0;
}

.tool-btn {
  padding: 0.375rem 0.625rem; font-size: 0.875rem;
  background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.375rem; cursor: pointer; transition: all 0.15s;
}
.tool-btn:hover { background: rgba(255, 255, 255, 0.08); }
.tool-btn--active { background: rgba(99, 102, 241, 0.15); border-color: rgba(99, 102, 241, 0.3); }
.tool-btn--clear { font-size: 0.75rem; color: var(--color-error); }
.toolbar-spacer { flex: 1; }

.drawing-canvas {
  width: 100%; display: block;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0 0 0.625rem 0.625rem;
  cursor: crosshair;
}

.canvas-hint { font-size: 0.6875rem; color: var(--color-text-tertiary); margin-top: 0.375rem; text-align: center; }

.section-label {
  font-size: 0.6875rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--color-accent-light); margin: 0 0 0.5rem;
}

.req-list { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1.25rem; }
.req-item {
  display: flex; align-items: center; gap: 0.625rem; font-size: 0.875rem;
  padding: 0.5rem 0.75rem; background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 0.5rem; color: var(--color-text-primary);
}
.req-check { width: 1.125rem; height: 1.125rem; accent-color: var(--color-success); flex-shrink: 0; }
.req-done { text-decoration: line-through; opacity: 0.5; color: var(--color-text-tertiary); }

.explanation-input {
  width: 100%; padding: 0.75rem; border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem; font-size: 0.875rem; resize: vertical;
  background: rgba(255, 255, 255, 0.025); color: var(--color-text-primary); transition: border-color 0.15s, box-shadow 0.15s;
}
.explanation-input:focus { outline: none; border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }

.solution-btn {
  padding: 0.5rem 1.25rem; background: rgba(16, 185, 129, 0.06); color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 0.5rem;
  font-size: 0.8125rem; font-weight: 500; cursor: pointer; transition: all 0.15s;
}
.solution-btn:hover { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); }

.solution-box {
  margin-top: 1rem; padding: 1rem 1.125rem; background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.15); border-radius: 0.625rem;
}
.sol-label { margin: 0 0 0.5rem; font-size: 0.6875rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--color-success); }
.sol-text { margin: 0 0 0.75rem; font-size: 0.875rem; line-height: 1.65; color: var(--color-text-primary); }
.sol-diagram {
  margin: 0; padding: 0.875rem; background: var(--color-code-bg); color: #a5f3fc; border-radius: 0.5rem;
  font-family: 'Fira Code', 'JetBrains Mono', monospace; font-size: 0.8125rem; white-space: pre; overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
