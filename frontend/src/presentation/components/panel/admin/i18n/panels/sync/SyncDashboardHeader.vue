<script setup lang="ts">
/**
 * SyncDashboardHeader
 *
 * Header section of the I18n Sync Dashboard containing:
 * - Title and subtitle
 * - Mode selector (MANUAL / AUTO)
 * - Language selector (de, en, pl)
 */

import type { SyncMode } from '../types/sync.types'

interface Props {
  selectedMode: SyncMode
  selectedLanguages: string[]
  availableLanguages: string[]
}

interface Emits {
  (e: 'mode-change', mode: SyncMode): void
  (e: 'toggle-language', lang: string): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<template>
  <div class="dashboard-header">
    <div class="header-content">
      <div class="header-title">
        <h1>{{ $t('panel.i18n.title') }}</h1>
        <p class="subtitle">{{ $t('panel.i18n.subtitle') }}</p>
      </div>

      <!-- Mode Selector -->
      <div class="mode-selector">
        <button
          class="mode-button"
          :class="{ active: selectedMode === 'MANUAL' }"
          @click="$emit('mode-change', 'MANUAL' as SyncMode)"
        >
          <span class="mode-icon">&#127919;</span>
          <span class="mode-label">{{ $t('panel.i18n.mode_manual') }}</span>
          <span class="mode-desc">{{ $t('panel.i18n.mode_manual_desc') }}</span>
        </button>

        <button
          class="mode-button"
          :class="{ active: selectedMode === 'AUTO' }"
          @click="$emit('mode-change', 'AUTO' as SyncMode)"
        >
          <span class="mode-icon">&#9881;&#65039;</span>
          <span class="mode-label">{{ $t('panel.i18n.mode_auto') }}</span>
          <span class="mode-desc">{{ $t('panel.i18n.mode_auto_desc') }}</span>
        </button>
      </div>
    </div>

    <!-- Language Selection -->
    <div class="language-selector">
      <label class="label">{{ $t('panel.i18n.languages') }}</label>
      <div class="language-options">
        <button
          v-for="lang in availableLanguages"
          :key="lang"
          class="language-button"
          :class="{ active: selectedLanguages.includes(lang) }"
          @click="$emit('toggle-language', lang)"
        >
          {{ lang.toUpperCase() }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-title h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

.header-title .subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: #6b7280;
}

.mode-selector {
  display: flex;
  gap: 12px;
}

.mode-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.mode-button:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.mode-button.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.mode-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.mode-label {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.mode-desc {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.language-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.label {
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.language-options {
  display: flex;
  gap: 8px;
}

.language-button {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-weight: 500;
  font-size: 12px;
  transition: all 0.3s;
}

.language-button:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.language-button.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}
</style>
