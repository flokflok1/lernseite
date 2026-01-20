<!--
  LSX Desktop Taskbar

  Displays all open panels as taskbar items.
  Allows restoring minimized panels and switching between features.

  Phase: B24-06 - Admin Desktop OS
-->

<template>
  <div class="lsx-taskbar">
    <div class="lsx-taskbar-items">
      <button
        v-for="panel in panels"
        :key="panel.id"
        class="lsx-taskbar-item"
        :class="{
          'lsx-taskbar-item--active': panel.id === activePanelId,
          'lsx-taskbar-item--minimized': panel.minimized
        }"
        @click="handleTaskbarItemClick(panel.id)"
        :title="panel.title"
      >
        <span v-if="panel.icon" class="lsx-taskbar-item-icon">{{ panel.icon }}</span>
        <span class="lsx-taskbar-item-title">{{ truncateTitle(panel.title) }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePanelStore } from '@/store/modules/desktop'
import type { LsxPanel as _LsxPanel } from '@/store/modules/desktop'

const panelStore = usePanelStore()

const panels = computed(() => panelStore.panels)
const activePanelId = computed(() => panelStore.activePanelId)

/**
 * Handle taskbar item click
 */
function handleTaskbarItemClick(panelId: string): void {
  const panel = panelStore.getPanelById(panelId)
  if (!panel) return

  if (panel.minimized) {
    // Restore minimized panel
    panelStore.restorePanel(panelId)
  } else if (panelStore.activePanelId === panelId) {
    // Minimize if clicking active panel
    panelStore.minimizePanel(panelId)
  } else {
    // Focus panel
    panelStore.focusPanel(panelId)
  }
}

/**
 * Truncate long titles
 * Handles undefined/null titles gracefully
 */
function truncateTitle(title: string | undefined | null): string {
  if (!title) return ''
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
