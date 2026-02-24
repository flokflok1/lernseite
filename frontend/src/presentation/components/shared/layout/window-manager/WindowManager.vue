<!--
  LSX Desktop Layer

  Main desktop rendering layer that manages all floating windows.
  Renders window components based on window type and manages taskbar.

  Phase: B24-06 - Admin Desktop OS
-->

<template>
  <div class="lsx-desktop-layer">
    <!-- Main Content (router-view slot) -->
    <div class="lsx-desktop-content">
      <slot />
    </div>

    <!-- Floating Windows -->
    <FloatingWindow
      v-for="window in visibleWindows"
      :key="window.id"
      :window="window"
      :isActive="window.id === activeWindowId"
      @close="handleClose"
      @minimize="handleMinimize"
      @maximize="handleMaximize"
      @focus="handleFocus"
      @drag="handleDrag"
      @resize="handleResize"
      @popout="handlePopout"
    >
      <!-- Dynamic Window Content based on type -->
      <component
        :is="resolveWindowComponent(window.type)"
        :window="window"
        @close="handleClose(window.id)"
      />
    </FloatingWindow>

    <!-- Taskbar (fixed position) -->
    <Taskbar />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import { useWindowSync } from '@/application/composables/useWindowSync'
import { resolveWindowComponent } from './windowResolver'
import FloatingWindow from './FloatingWindow.vue'
import Taskbar from './Taskbar.vue'

const windowStore = useWindowStore()
const { onSync } = useWindowSync()

const visibleWindows = computed(() => windowStore.visibleWindows)
const activeWindowId = computed(() => windowStore.activeWindowId)

// Listen for pop-in requests from pop-out windows
onSync('action:popin', (msg) => {
  if (msg.payload) {
    windowStore.popinWindow(
      msg.payload.windowType as string,
      msg.payload.payload as Record<string, unknown>
    )
  }
})

function handleClose(windowId: string): void {
  windowStore.closeWindow(windowId)
}

function handleMinimize(windowId: string): void {
  windowStore.minimizeWindow(windowId)
}

function handleMaximize(windowId: string): void {
  windowStore.toggleMaximize(windowId)
}

function handleFocus(windowId: string): void {
  windowStore.focusWindow(windowId)
}

function handleDrag(windowId: string, position: { x: number; y: number }): void {
  windowStore.updateWindowPosition(windowId, position)
}

function handleResize(windowId: string, size: { width: number; height: number }): void {
  windowStore.updateWindowSize(windowId, size)
}

function handlePopout(windowId: string): void {
  windowStore.popoutWindow(windowId)
}
</script>

<style scoped>
.lsx-desktop-layer {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.lsx-desktop-content {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  padding-bottom: 56px; /* Space for fixed taskbar (48px + 8px gap) */
  box-sizing: border-box;
}
</style>
