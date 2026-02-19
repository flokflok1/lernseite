<!--
  InteractiveWhiteboard - Animiertes Whiteboard fuer Tutor-Erklaerungen

  Features:
  - Canvas-basiertes Zeichensystem
  - Animiertes Schreiben (Handschrift-Effekt)
  - Text mit verschiedenen Groessen und Farben
  - Hervorhebungen und Unterstreichungen
  - Pfeile und Linien
  - Schrittweises Aufbauen
  - Loeschfunktion

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
  <div
    class="whiteboard-container"
    :class="{ 'transparent-mode': backgroundColor === 'transparent' }"
    :style="{ width: `${width}px`, height: `${height}px` }"
  >
    <div class="whiteboard-frame" :class="{ 'no-frame': backgroundColor === 'transparent' }">
      <div v-if="title && backgroundColor !== 'transparent'" class="whiteboard-header">
        <div class="header-dots">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
        </div>
        <span class="header-title">{{ title }}</span>
      </div>

      <div class="whiteboard-canvas-wrapper">
        <canvas
          ref="canvasRef"
          :width="canvasWidth"
          :height="canvasHeight"
          class="whiteboard-canvas"
          :class="{ 'transparent-canvas': backgroundColor === 'transparent' }"
        ></canvas>

        <div
          v-if="isDrawing"
          class="pen-cursor"
          :class="{ 'chalk-cursor': backgroundColor === 'transparent' }"
          :style="{ left: `${cursorPosition.x}px`, top: `${cursorPosition.y}px` }"
        >
          {{ backgroundColor === 'transparent' ? '\u270E' : '\u270F\uFE0F' }}
        </div>
      </div>

      <div v-if="showControls" class="whiteboard-controls">
        <button @click="clearBoard" class="control-btn" :title="t('whiteboard.delete')">
          \uD83D\uDDD1\uFE0F
        </button>
        <button
          @click="undoLast"
          class="control-btn"
          :title="t('whiteboard.undo')"
          :disabled="actionHistory.length === 0"
        >
          \u21A9\uFE0F
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWhiteboardCanvas } from './composables/useWhiteboardCanvas.ts'

export type { SchemaRow, WhiteboardAction } from './types/whiteboard.types.ts'

const { t } = useI18n()

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
  (e: 'action-complete', action: import('./whiteboard.types.ts').WhiteboardAction): void
  (e: 'action-start', action: import('./whiteboard.types.ts').WhiteboardAction): void
  (e: 'cleared'): void
}>()

// ============================================================================
// Canvas Setup
// ============================================================================
const canvasRef = ref<HTMLCanvasElement | null>(null)
const canvasWidth = computed(() => props.width - 40)
const canvasHeight = computed(() => props.height - 80)

const {
  isDrawing,
  cursorPosition,
  actionHistory,
  executeAction,
  executeActions,
  clearBoard,
  undoLast,
  initCanvas,
} = useWhiteboardCanvas({
  canvasRef,
  canvasWidth,
  canvasHeight,
  backgroundColor: () => props.backgroundColor,
  textColor: () => props.textColor,
  onActionStart: (action) => emit('action-start', action),
  onActionComplete: (action) => emit('action-complete', action),
  onCleared: () => emit('cleared'),
})

// ============================================================================
// Lifecycle
// ============================================================================
onMounted(async () => {
  await nextTick()
  initCanvas()
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

:root.dark .whiteboard-canvas {
  background: #f8fafc;
}
</style>
