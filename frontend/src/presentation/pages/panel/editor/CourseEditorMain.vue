/**
 * CourseEditorMain.vue
 *
 * Course editor launcher page within the admin panel.
 * Provides buttons to open Manual Editor and AI Editor as floating windows.
 * Windows are rendered by DesktopLayer (already present in PanelLayout).
 */

<template>
  <div class="course-editor-launcher">
    <div class="launcher-content">
      <div class="launcher-icon">&#9997;&#65039;</div>
      <h2 class="launcher-title">{{ $t('panel.editor.launcher.title') }}</h2>
      <p class="launcher-description">{{ $t('panel.editor.launcher.description') }}</p>
      <p class="launcher-hint">{{ $t('panel.editor.launcher.hint') }}</p>

      <div class="launcher-buttons">
        <button class="launcher-btn" @click="openManualEditor">
          <span class="launcher-btn-icon">&#9998;&#65039;</span>
          <span>{{ t('panel.editor.manual.title') }}</span>
        </button>

        <button class="launcher-btn" @click="openAIEditor">
          <span class="launcher-btn-icon">&#129302;</span>
          <span>{{ t('panel.editor.ai.title') }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'

const { t } = useI18n()
const windowStore = useWindowStore()

function openManualEditor(): void {
  const existing = windowStore.getPanelsByType('editor-manual')
  if (existing.length > 0) {
    windowStore.focusWindow(existing[0].id)
    return
  }
  windowStore.openWindow({
    type: 'editor-manual',
    title: t('panel.editor.manual.title'),
    icon: '\u270E\uFE0F',
    size: { width: 1000, height: 700 },
  })
}

function openAIEditor(): void {
  const existing = windowStore.getPanelsByType('editor-ai-editor')
  if (existing.length > 0) {
    windowStore.focusWindow(existing[0].id)
    return
  }
  windowStore.openWindow({
    type: 'editor-ai-editor',
    title: t('panel.editor.ai.title'),
    icon: '\uD83E\uDD16',
    size: { width: 1000, height: 700 },
  })
}
</script>

<style scoped>
.course-editor-launcher {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
}

.launcher-content {
  text-align: center;
  color: var(--color-text-tertiary);
}

.launcher-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.launcher-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 0.5rem;
}

.launcher-description {
  font-size: 1rem;
  margin: 0 0 0.5rem;
}

.launcher-hint {
  font-size: 0.85rem;
  font-style: italic;
  color: var(--color-text-tertiary);
  margin: 0 0 2rem;
}

.launcher-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.launcher-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-text-primary, #374151);
  background: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  cursor: pointer;
  transition: background-color 0.15s, border-color 0.15s;
}

.launcher-btn:hover {
  background: var(--color-surface-secondary, #f3f4f6);
  border-color: var(--color-border-hover, #d1d5db);
}

.launcher-btn-icon {
  font-size: 1.25rem;
}
</style>
