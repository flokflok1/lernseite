<!--
  AI Studio Tabs Bar

  Horizontal tab navigation for the 9 AI Studio tabs + chat toggle.
  Extracted from AiStudioMain to keep each file under 500 LOC.
-->

<template>
  <div class="tabs-bar">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      @click="$emit('select-tab', tab.id)"
      class="tab-button"
      :class="{ active: activeTab === tab.id }"
    >
      <span class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-label">{{ tab.label }}</span>
      <span v-if="tab.badge" class="tab-badge" :class="tab.badgeColor || 'primary'">
        {{ tab.badge }}
      </span>
      <div v-if="activeTab === tab.id" class="tab-indicator"></div>
    </button>

    <div class="tabs-spacer"></div>

    <!-- Chat Toggle -->
    <button
      @click="$emit('toggle-chat')"
      class="tab-button"
      :class="{ active: chatExpanded }"
    >
      <span class="tab-icon">💬</span>
      <span class="tab-label">{{ $t('aiEditorPro.chat') }}</span>
      <svg
        class="chat-chevron"
        :class="{ open: chatExpanded }"
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
/**
 * AiStudioTabsBar - Tab navigation for AI Studio
 */
import type { TabConfig } from './views'

interface Props {
  tabs: TabConfig[]
  activeTab: string
  chatExpanded: boolean
}

defineProps<Props>()

defineEmits<{
  'select-tab': [tabId: string]
  'toggle-chat': []
}>()
</script>

<style scoped>
.tabs-bar {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  position: relative;
  transition: all 0.15s;
}

.tab-button:hover {
  color: var(--color-text-primary);
  background: var(--color-surface);
}

.tab-button.active {
  color: var(--color-primary);
  background: var(--color-bg);
}

.tab-icon {
  font-size: 1.125rem;
}

.tab-badge {
  padding: 0.125rem 0.375rem;
  border-radius: 9999px;
  font-size: 0.625rem;
  font-weight: 700;
}

.tab-badge.primary {
  background: var(--color-primary);
  color: white;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-primary);
}

.tabs-spacer {
  flex: 1;
}

.chat-chevron {
  width: 1rem;
  height: 1rem;
  transition: transform 0.15s;
}

.chat-chevron.open {
  transform: rotate(180deg);
}
</style>
