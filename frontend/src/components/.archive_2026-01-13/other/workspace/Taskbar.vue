<!--
  LSX Desktop Taskbar

  Displays all open windows as taskbar items.
  Allows restoring minimized windows and switching between windows.

  Phase: B24-06 - Admin Desktop OS
-->

<template>
  <div class="lsx-taskbar">
    <div class="lsx-taskbar-items">
      <button
        v-for="window in windows"
        :key="window.id"
        class="lsx-taskbar-item"
        :class="{
          'lsx-taskbar-item--active': window.id === activeWindowId,
          'lsx-taskbar-item--minimized': window.minimized
        }"
        @click="handleTaskbarItemClick(window.id)"
        :title="window.title"
      >
        <span v-if="window.icon" class="lsx-taskbar-item-icon">{{ window.icon }}</span>
        <span class="lsx-taskbar-item-title">{{ truncateTitle(window.title) }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWindowStore } from '@/store/modules/desktop'
import type { LsxWindow as _LsxWindow } from '@/store/modules/desktop'

const windowStore = useWindowStore()

const windows = computed(() => windowStore.windows)
const activeWindowId = computed(() => windowStore.activeWindowId)

/**
 * Handle taskbar item click
 */
function handleTaskbarItemClick(windowId: string): void {
  const window = windowStore.getWindowById(windowId)
  if (!window) return

  if (window.minimized) {
    // Restore minimized window
    windowStore.restoreWindow(windowId)
  } else if (windowStore.activeWindowId === windowId) {
    // Minimize if clicking active window
    windowStore.minimizeWindow(windowId)
  } else {
    // Focus window
    windowStore.focusWindow(windowId)
  }
}

/**
 * Truncate long titles
 */
function truncateTitle(title: string): string {
  const maxLength = 20
  if (title.length <= maxLength) return title
  return title.substring(0, maxLength - 3) + '...'
}
</script>

<style scoped>
.lsx-taskbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 48px;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  padding: 6px 16px;
  display: flex;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(12px);
}

.lsx-taskbar-items {
  display: flex;
  gap: 8px;
  align-items: center;
  overflow-x: auto;
  flex: 1;
}

/* Hide scrollbar */
.lsx-taskbar-items::-webkit-scrollbar {
  display: none;
}

.lsx-taskbar-items {
  scrollbar-width: none;
}

.lsx-taskbar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: var(--color-background);
  color: var(--color-text-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  min-width: 120px;
  max-width: 200px;
}

.lsx-taskbar-item:hover {
  background: var(--color-primary);
  color: white;
  transform: translateY(-2px);
}

.lsx-taskbar-item--active {
  background: var(--color-primary);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.lsx-taskbar-item--minimized {
  opacity: 0.6;
}

.lsx-taskbar-item--minimized:hover {
  opacity: 1;
}

.lsx-taskbar-item-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.lsx-taskbar-item-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
