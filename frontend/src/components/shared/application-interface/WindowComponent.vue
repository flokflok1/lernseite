<!--
  LSX Desktop Window Component

  Individual draggable, minimizable window instance.
  Provides window chrome (header, buttons) and content slot.

  Phase: B24-06 - Admin Desktop OS
-->

<template>
  <div
    ref="windowRef"
    class="lsx-desktop-window"
    :class="{
      'lsx-desktop-window--active': isActive,
      'lsx-desktop-window--dragging': isDragging,
      'lsx-desktop-window--maximized': window.maximized
    }"
    :style="windowStyle"
    @mousedown="handleWindowClick"
  >
    <!-- Window Header (Draggable, Double-click to maximize) -->
    <div
      ref="headerRef"
      class="lsx-window-header"
      @mousedown="handleDragStart"
      @dblclick="handleMaximize"
    >
      <!-- Icon & Title -->
      <div class="lsx-window-title">
        <span v-if="window.icon" class="lsx-window-icon">{{ window.icon }}</span>
        <span class="lsx-window-title-text">{{ window.title }}</span>
      </div>

      <!-- Window Controls -->
      <div class="lsx-window-controls">
        <button
          class="lsx-window-control lsx-window-control--minimize"
          @click.stop="handleMinimize"
          title="Minimieren"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M2 6h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
        <button
          class="lsx-window-control lsx-window-control--maximize"
          @click.stop="handleMaximize"
          :title="window.maximized ? 'Wiederherstellen' : 'Maximieren'"
        >
          <svg v-if="!window.maximized" width="12" height="12" viewBox="0 0 12 12" fill="none">
            <!-- Maximize icon: single square -->
            <rect x="2" y="2" width="8" height="8" stroke="currentColor" stroke-width="1.5" fill="none" rx="1"/>
          </svg>
          <svg v-else width="12" height="12" viewBox="0 0 12 12" fill="none">
            <!-- Restore icon: two cascaded squares (Windows-style) -->
            <path d="M4 2h6v6M2 4h6v6H2z" stroke="currentColor" stroke-width="1.5" fill="none"/>
          </svg>
        </button>
        <button
          class="lsx-window-control lsx-window-control--close"
          @click.stop="handleClose"
          title="Schließen"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Window Content -->
    <div class="lsx-window-content">
      <slot />
    </div>

    <!-- Resize Handles -->
    <div class="lsx-resize-handle lsx-resize-handle--n" @mousedown="handleResizeStart($event, 'n')"></div>
    <div class="lsx-resize-handle lsx-resize-handle--e" @mousedown="handleResizeStart($event, 'e')"></div>
    <div class="lsx-resize-handle lsx-resize-handle--s" @mousedown="handleResizeStart($event, 's')"></div>
    <div class="lsx-resize-handle lsx-resize-handle--w" @mousedown="handleResizeStart($event, 'w')"></div>
    <div class="lsx-resize-handle lsx-resize-handle--ne" @mousedown="handleResizeStart($event, 'ne')"></div>
    <div class="lsx-resize-handle lsx-resize-handle--se" @mousedown="handleResizeStart($event, 'se')"></div>
    <div class="lsx-resize-handle lsx-resize-handle--sw" @mousedown="handleResizeStart($event, 'sw')"></div>
    <div class="lsx-resize-handle lsx-resize-handle--nw" @mousedown="handleResizeStart($event, 'nw')"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { LsxWindow } from '@/store/window.store'

interface Props {
  window: LsxWindow
  isActive: boolean
}

interface Emits {
  (e: 'close', id: string): void
  (e: 'minimize', id: string): void
  (e: 'maximize', id: string): void
  (e: 'focus', id: string): void
  (e: 'drag', id: string, position: { x: number; y: number }): void
  (e: 'resize', id: string, size: { width: number; height: number }): void
}

type ResizeDirection = 'n' | 'e' | 's' | 'w' | 'ne' | 'se' | 'sw' | 'nw'

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const windowRef = ref<HTMLElement | null>(null)
const headerRef = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const isResizing = ref(false)

/**
 * Computed window style - handles both normal and maximized states
 */
const windowStyle = computed(() => {
  if (props.window.maximized) {
    return {
      left: '0px',
      top: '0px',
      width: '100vw',
      height: 'calc(100vh - 56px)', // Leave room for taskbar
      maxHeight: 'none',
      zIndex: props.window.zIndex,
      borderRadius: '0',
      display: 'flex',
      flexDirection: 'column'
    }
  }
  return {
    left: `${props.window.position.x}px`,
    top: `${props.window.position.y}px`,
    width: props.window.size?.width ? `${props.window.size.width}px` : '800px',
    height: props.window.size?.height ? `${props.window.size.height}px` : 'auto',
    maxHeight: 'calc(100vh - 80px)',
    zIndex: props.window.zIndex
  }
})

// Drag state
const dragState = ref<{
  startX: number
  startY: number
  offsetX: number
  offsetY: number
} | null>(null)

// Resize state
const resizeState = ref<{
  direction: ResizeDirection
  startX: number
  startY: number
  startWidth: number
  startHeight: number
  startPosX: number
  startPosY: number
} | null>(null)

/**
 * Handle window click (focus)
 */
function handleWindowClick(): void {
  emit('focus', props.window.id)
}

/**
 * Handle minimize button
 */
function handleMinimize(): void {
  emit('minimize', props.window.id)
}

/**
 * Handle close button
 */
function handleClose(): void {
  emit('close', props.window.id)
}

/**
 * Handle maximize/restore button
 */
function handleMaximize(): void {
  emit('maximize', props.window.id)
}

/**
 * Start dragging window
 */
function handleDragStart(e: MouseEvent): void {
  // Only drag on left mouse button
  if (e.button !== 0) return

  // Don't allow dragging when maximized
  if (props.window.maximized) return

  // Focus window
  emit('focus', props.window.id)

  // Calculate offset from cursor to window position
  const offsetX = e.clientX - props.window.position.x
  const offsetY = e.clientY - props.window.position.y

  dragState.value = {
    startX: e.clientX,
    startY: e.clientY,
    offsetX,
    offsetY
  }

  isDragging.value = true

  // Add global listeners
  document.addEventListener('mousemove', handleDragMove)
  document.addEventListener('mouseup', handleDragEnd)

  // Prevent text selection
  e.preventDefault()
}

/**
 * Handle drag move
 */
function handleDragMove(e: MouseEvent): void {
  if (!dragState.value) return

  // Calculate new position
  let newX = e.clientX - dragState.value.offsetX
  let newY = e.clientY - dragState.value.offsetY

  // Constrain to viewport
  const minX = 0
  const minY = 0
  const maxX = window.innerWidth - 200 // Keep at least 200px visible
  const maxY = window.innerHeight - 50 // Keep header visible

  newX = Math.max(minX, Math.min(newX, maxX))
  newY = Math.max(minY, Math.min(newY, maxY))

  // Emit drag event
  emit('drag', props.window.id, { x: newX, y: newY })
}

/**
 * End dragging
 */
function handleDragEnd(): void {
  isDragging.value = false
  dragState.value = null

  // Remove global listeners
  document.removeEventListener('mousemove', handleDragMove)
  document.removeEventListener('mouseup', handleDragEnd)
}

/**
 * Start resizing window
 */
function handleResizeStart(e: MouseEvent, direction: ResizeDirection): void {
  if (e.button !== 0) return

  // Don't allow resizing when maximized
  if (props.window.maximized) return

  emit('focus', props.window.id)

  const rect = windowRef.value?.getBoundingClientRect()
  if (!rect) return

  resizeState.value = {
    direction,
    startX: e.clientX,
    startY: e.clientY,
    startWidth: rect.width,
    startHeight: rect.height,
    startPosX: props.window.position.x,
    startPosY: props.window.position.y
  }

  isResizing.value = true

  document.addEventListener('mousemove', handleResizeMove)
  document.addEventListener('mouseup', handleResizeEnd)

  e.preventDefault()
  e.stopPropagation()
}

/**
 * Handle resize move
 */
function handleResizeMove(e: MouseEvent): void {
  if (!resizeState.value) return

  const { direction, startX, startY, startWidth, startHeight, startPosX, startPosY } = resizeState.value
  const deltaX = e.clientX - startX
  const deltaY = e.clientY - startY

  let newWidth = startWidth
  let newHeight = startHeight
  let newX = startPosX
  let newY = startPosY

  // Handle horizontal resizing
  if (direction.includes('e')) {
    newWidth = startWidth + deltaX
  }
  if (direction.includes('w')) {
    newWidth = startWidth - deltaX
    newX = startPosX + deltaX
  }

  // Handle vertical resizing
  if (direction.includes('s')) {
    newHeight = startHeight + deltaY
  }
  if (direction.includes('n')) {
    newHeight = startHeight - deltaY
    newY = startPosY + deltaY
  }

  // Apply minimum size
  const minWidth = 400
  const minHeight = 300

  if (newWidth < minWidth) {
    if (direction.includes('w')) {
      newX = startPosX + startWidth - minWidth
    }
    newWidth = minWidth
  }

  if (newHeight < minHeight) {
    if (direction.includes('n')) {
      newY = startPosY + startHeight - minHeight
    }
    newHeight = minHeight
  }

  // Update position if needed (for n/w/nw/ne/sw resizing)
  if (direction.includes('n') || direction.includes('w')) {
    emit('drag', props.window.id, { x: newX, y: newY })
  }

  // Emit resize event
  emit('resize', props.window.id, { width: newWidth, height: newHeight })
}

/**
 * End resizing
 */
function handleResizeEnd(): void {
  isResizing.value = false
  resizeState.value = null

  document.removeEventListener('mousemove', handleResizeMove)
  document.removeEventListener('mouseup', handleResizeEnd)
}
</script>

<style scoped>
.lsx-desktop-window {
  position: fixed;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  transition: box-shadow 0.2s ease;
  min-width: 400px;
  min-height: 300px;
}

.lsx-desktop-window--active {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.18);
}

.lsx-desktop-window--dragging {
  cursor: move;
  user-select: none;
}

.lsx-desktop-window--maximized {
  border-radius: 0 !important;
  box-shadow: none;
  position: fixed;
}

.lsx-desktop-window--maximized .lsx-window-header {
  cursor: default;
  flex-shrink: 0;
}

.lsx-desktop-window--maximized .lsx-window-content {
  position: absolute;
  top: 57px; /* Header height */
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.lsx-desktop-window--maximized .lsx-resize-handle {
  display: none;
}

/* Window Header */
.lsx-window-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  cursor: move;
  user-select: none;
}

.lsx-window-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.lsx-window-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.lsx-window-title-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Window Controls */
.lsx-window-controls {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.lsx-window-control {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.lsx-window-control:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.lsx-window-control--close:hover {
  background: #ef4444;
  color: white;
}

.lsx-window-control--minimize:hover {
  background: var(--color-primary);
  color: white;
}

.lsx-window-control--maximize:hover {
  background: #10b981;
  color: white;
}

/* Window Content */
.lsx-window-content {
  flex: 1;
  min-height: 0; /* Critical for nested flex scrolling */
  min-width: 0; /* Critical for horizontal flex */
  max-width: 100%;
  overflow: hidden;
  background: var(--color-surface);
}

/* Ensure content inside doesn't force window width */
.lsx-window-content :deep(> *) {
  max-width: 100%;
  box-sizing: border-box;
}

/* Scrollbar Styling */
.lsx-window-content::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.lsx-window-content::-webkit-scrollbar-track {
  background: transparent;
}

.lsx-window-content::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}

.lsx-window-content::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}

/* Resize Handles */
.lsx-resize-handle {
  position: absolute;
  z-index: 10;
}

/* Edge handles - 8px wide/tall inside the window border */
.lsx-resize-handle--n {
  top: 0;
  left: 16px;
  right: 16px;
  height: 8px;
  cursor: n-resize;
}

.lsx-resize-handle--e {
  top: 16px;
  right: 0;
  bottom: 16px;
  width: 8px;
  cursor: e-resize;
}

.lsx-resize-handle--s {
  bottom: 0;
  left: 16px;
  right: 16px;
  height: 8px;
  cursor: s-resize;
}

.lsx-resize-handle--w {
  top: 16px;
  left: 0;
  bottom: 16px;
  width: 8px;
  cursor: w-resize;
}

/* Corner handles - 16x16px at corners */
.lsx-resize-handle--ne {
  top: 0;
  right: 0;
  width: 16px;
  height: 16px;
  cursor: ne-resize;
}

.lsx-resize-handle--se {
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  cursor: se-resize;
}

.lsx-resize-handle--sw {
  bottom: 0;
  left: 0;
  width: 16px;
  height: 16px;
  cursor: sw-resize;
}

.lsx-resize-handle--nw {
  top: 0;
  left: 0;
  width: 16px;
  height: 16px;
  cursor: nw-resize;
}
</style>
