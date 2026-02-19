<!--
  LSX Desktop Window Component

  Individual draggable, minimizable window instance.
  Provides window chrome (header, buttons) and content slot.

  Drag/resize logic extracted to composables/useWindowInteraction.ts

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
          :title="$t('common.minimize')"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M2 6h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
        <button
          class="lsx-window-control lsx-window-control--maximize"
          @click.stop="handleMaximize"
          :title="window.maximized ? $t('common.restore') : $t('common.maximize')"
        >
          <svg v-if="!window.maximized" width="12" height="12" viewBox="0 0 12 12" fill="none">
            <rect x="2" y="2" width="8" height="8" stroke="currentColor" stroke-width="1.5" fill="none" rx="1"/>
          </svg>
          <svg v-else width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M4 2h6v6M2 4h6v6H2z" stroke="currentColor" stroke-width="1.5" fill="none"/>
          </svg>
        </button>
        <button
          class="lsx-window-control lsx-window-control--close"
          @click.stop="handleClose"
          :title="$t('common.close')"
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
import { ref, computed, toRef } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import { useWindowInteraction } from './composables/useWindowInteraction'

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

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const windowRef = ref<HTMLElement | null>(null)
const headerRef = ref<HTMLElement | null>(null)

/**
 * Computed window style - handles both normal and maximized states
 */
const windowStyle = computed(() => {
  if (props.window.maximized) {
    return {
      left: '0px',
      top: '0px',
      width: '100vw',
      height: 'calc(100vh - 56px)',
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

// Drag & Resize via composable
const { isDragging, handleDragStart, handleResizeStart } = useWindowInteraction({
  windowRef,
  windowId: computed(() => props.window.id) as any,
  windowPosition: computed(() => props.window.position) as any,
  isMaximized: computed(() => props.window.maximized) as any,
  onFocus: (id: string) => emit('focus', id),
  onDrag: (id: string, pos) => emit('drag', id, pos),
  onResize: (id: string, size) => emit('resize', id, size)
})

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
  top: 57px;
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
  min-height: 0;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  background: var(--color-surface);
}

.lsx-window-content :deep(> *) {
  max-width: 100%;
  box-sizing: border-box;
}

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

.lsx-resize-handle--n {
  top: 0; left: 16px; right: 16px; height: 8px;
  cursor: n-resize;
}

.lsx-resize-handle--e {
  top: 16px; right: 0; bottom: 16px; width: 8px;
  cursor: e-resize;
}

.lsx-resize-handle--s {
  bottom: 0; left: 16px; right: 16px; height: 8px;
  cursor: s-resize;
}

.lsx-resize-handle--w {
  top: 16px; left: 0; bottom: 16px; width: 8px;
  cursor: w-resize;
}

.lsx-resize-handle--ne {
  top: 0; right: 0; width: 16px; height: 16px;
  cursor: ne-resize;
}

.lsx-resize-handle--se {
  bottom: 0; right: 0; width: 16px; height: 16px;
  cursor: se-resize;
}

.lsx-resize-handle--sw {
  bottom: 0; left: 0; width: 16px; height: 16px;
  cursor: sw-resize;
}

.lsx-resize-handle--nw {
  top: 0; left: 0; width: 16px; height: 16px;
  cursor: nw-resize;
}
</style>
